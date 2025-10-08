import requests
import time
import os
import pandas as pd
from datetime import datetime, timezone
from multiprocessing import Pool, cpu_count
from functools import partial
import glob
import random

# --- CONFIGURAÇÕES ---
GITHUB_TOKEN = os.getenv("TOKEN")
GITHUB_API_URL = 'https://api.github.com/graphql'
OUTPUT_DIR = "resultados_csv"

# --- QUERIES GraphQL ---
GET_TOP_REPOS_QUERY = """
query GetTopRepos($afterCursor: String) {
  search(query: "sort:stars-desc is:public", type: REPOSITORY, first: 100, after: $afterCursor) {
    nodes {
      ... on Repository {
        owner { login }
        name
        pullRequests(states: [MERGED, CLOSED]) { totalCount }
      }
    }
    pageInfo { endCursor, hasNextPage }
  }
}
"""
GET_PULL_REQUESTS_QUERY = """
query GetPullRequests($owner: String!, $name: String!, $afterCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 40, after: $afterCursor, states: [MERGED, CLOSED], orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        state, createdAt, closedAt, mergedAt, additions, deletions, changedFiles, bodyText
        participants(first: 1) { totalCount }
        comments(first: 1) { totalCount }
        reviews(first: 1) { totalCount }
      }
      pageInfo { endCursor, hasNextPage }
    }
  }
}
"""

# --- FUNÇÃO DE API COM EXPONENTIAL BACKOFF ---
def run_graphql_query(query, variables=None):
    """Executa uma query GraphQL com lógica de retentativa 'exponential backoff'."""
    if not GITHUB_TOKEN:
        raise Exception("Token do GitHub não encontrado.")
    headers = {'Authorization': f'bearer {GITHUB_TOKEN}', 'Content-Type': 'application/json'}
    request_body = {'query': query, 'variables': variables or {}}
    
    max_attempts = 7
    for attempt in range(max_attempts):
        try:
            response = requests.post(GITHUB_API_URL, headers=headers, json=request_body, timeout=90)
            
            if response.status_code in [502, 504]:
                print(f"\nServidor retornou {response.status_code}. Nova tentativa em andamento...")
                response.raise_for_status()

            response.raise_for_status()
            json_response = response.json()
            if 'errors' in json_response:
                print(f"\nErro na query GraphQL: {json_response['errors']}")
            return json_response

        except requests.exceptions.RequestException as e:
            if attempt < max_attempts - 1:
                wait_time = (2 ** attempt) + random.random()
                print(f"\nErro de rede ({e}). Tentando novamente em {wait_time:.2f} segundos...")
                time.sleep(wait_time)
            else:
                print(f"\nFalha na query após {max_attempts} tentativas.")
                raise e

# --- FUNÇÕES DE COLETA DE DADOS ---
def get_top_repos(total_to_fetch=200):
    print(f"Iniciando coleta de {total_to_fetch} repositórios mais populares...")
    repo_nodes = []
    after_cursor = None
    num_pages = (total_to_fetch + 99) // 100
    for page in range(num_pages):
        print(f"Buscando página de repositórios {page + 1}/{num_pages}...")
        result = run_graphql_query(GET_TOP_REPOS_QUERY, {"afterCursor": after_cursor})
        search_data = result['data']['search']
        repo_nodes.extend(search_data['nodes'])
        after_cursor = search_data['pageInfo']['endCursor']
        if not search_data['pageInfo']['hasNextPage']: break
        time.sleep(1)
    print(f"\nTotal de {len(repo_nodes)} repositórios encontrados.")
    filtered_repos = [r for r in repo_nodes if r and r.get('pullRequests', {}).get('totalCount', 0) >= 100]
    print(f"{len(filtered_repos)} repositórios atendem ao critério de >= 100 PRs.")
    return filtered_repos

# --- MUDANÇA AQUI: Adicionado limite na coleta de PRs ---
def get_prs_for_repo(owner, name, max_prs=200):
    """Busca os pull requests de um repositório até atingir o limite max_prs."""
    all_prs = []
    after_cursor = None
    
    # Loop para buscar páginas de PRs
    while True:
        result = run_graphql_query(GET_PULL_REQUESTS_QUERY, {"owner": owner, "name": name, "afterCursor": after_cursor})
        if not result: break
        
        repo_data = result.get('data', {}).get('repository')
        if not repo_data or 'pullRequests' not in repo_data: break
            
        pr_data = repo_data['pullRequests']
        all_prs.extend(pr_data['nodes'])

        # 1. Verifica se o limite foi atingido ou ultrapassado
        if len(all_prs) >= max_prs:
            print(f"  -> Limite de {max_prs} PRs atingido para {owner}/{name}.")
            break # Interrompe o loop de paginação
            
        # Continua a paginação se houver mais páginas e o limite não foi atingido
        if not pr_data['pageInfo']['hasNextPage']:
            break
        after_cursor = pr_data['pageInfo']['endCursor']
        time.sleep(0.5)
        
    # 2. Retorna a lista cortada para garantir que não exceda o limite
    return all_prs[:max_prs]
# --- FIM DA MUDANÇA ---

def process_and_save_repo(repo, output_dir):
    """Processa um único repositório, pulando se o CSV já existir."""
    try:
        owner = repo['owner']['login']
        name = repo['name']
        repo_name_full = f"{owner}/{name}"

        filename = f"{owner}-{name}.csv"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            print(f"JÁ EXISTE: Pulando {repo_name_full}, o arquivo '{filename}' já foi criado.")
            return 0

        print(f"Iniciando: {repo_name_full}")
        
        # A chamada aqui permanece a mesma, pois a função agora tem o limite embutido
        prs = get_prs_for_repo(owner, name)
        
        valid_prs_for_repo = []
        for pr in prs:
            if not pr or pr.get('reviews') is None: continue
            if pr['reviews']['totalCount'] < 1: continue
            
            created_at = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))
            final_date_str = pr['mergedAt'] or pr['closedAt']
            if not final_date_str: continue
            
            duration_hours = (datetime.fromisoformat(final_date_str.replace('Z', '+00:00')) - created_at).total_seconds() / 3600
            if duration_hours <= 1: continue

            valid_prs_for_repo.append({
                'repository': repo_name_full, 'status': pr['state'], 'analysis_time_hours': duration_hours,
                'size_files': pr['changedFiles'], 'size_additions': pr['additions'], 'size_deletions': pr['deletions'],
                'description_chars': len(pr.get('bodyText') or ''), 'interaction_participants': pr['participants']['totalCount'],
                'interaction_comments': pr['comments']['totalCount'], 'reviews_count': pr['reviews']['totalCount']
            })

        if valid_prs_for_repo:
            df = pd.DataFrame(valid_prs_for_repo)
            df.to_csv(filepath, index=False)
            print(f"SALVO: {repo_name_full} -> {len(valid_prs_for_repo)} PRs em '{filepath}'")
            return len(valid_prs_for_repo)
        else:
            pd.DataFrame([]).to_csv(filepath)
            print(f"Finalizado: {repo_name_full} -> Nenhum PR válido. Arquivo vazio criado.")
            return 0
            
    except Exception as e:
        print(f"ERRO ao processar {repo.get('name')}: {e}")
        return 0

def combine_csvs(input_dir, output_file):
    print(f"\nCombinando arquivos CSV do diretório '{input_dir}'...")
    all_files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not all_files:
        print("Nenhum arquivo CSV para combinar.")
        return

    df_list = []
    for file in all_files:
        try:
            # Tenta ler o arquivo
            df = pd.read_csv(file)
            # Adiciona na lista apenas se não estiver vazio
            if not df.empty:
                df_list.append(df)
        except pd.errors.EmptyDataError:
            # Se o arquivo estiver vazio, informa e continua
            print(f"AVISO: Pulando arquivo vazio: {os.path.basename(file)}")
            continue

    if not df_list:
        print("Nenhum dado válido encontrado nos arquivos CSV para combinar.")
        return

    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"Total de {len(combined_df)} registros salvos no arquivo final '{output_file}'")
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    top_repos_list = get_top_repos(total_to_fetch=200)
    if not top_repos_list:
        print("Nenhum repositório encontrado para processar.")
        return
    
    num_processes = 3
    print(f"\nIniciando coleta paralela com {num_processes} processos...")
    worker_func = partial(process_and_save_repo, output_dir=OUTPUT_DIR)
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(worker_func, top_repos_list)
        
    total_prs_saved = sum(results)
    print(f"\nColeta incremental finalizada! Total de {total_prs_saved} PRs salvos em arquivos individuais.")
    
    combine_csvs(input_dir=OUTPUT_DIR, output_file="dataset_completo.csv")

if __name__ == "__main__":
    main()