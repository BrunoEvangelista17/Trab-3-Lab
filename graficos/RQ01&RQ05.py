import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Definir o estilo dos gráficos
sns.set_style("whitegrid")

# Caminho para o arquivo do dataset
file_path = './dataset_completo.csv'

try:
    # Carregar o dataset
    df = pd.read_csv(file_path)
    print(f"Dataset carregado com sucesso de '{file_path}'")

    # Criar uma métrica consolidada para o tamanho total das linhas
    df['size_total_lines'] = df['size_additions'] + df['size_deletions']

    # --- Gráficos para a RQ01 (Focando na distribuição principal) ---

    # Para visualizar melhor, vamos filtrar os 5% maiores PRs
    size_files_limit = df['size_files'].quantile(0.8)
    size_lines_limit = df['size_total_lines'].quantile(0.8)
    
    df_filtered_rq01 = df[
        (df['size_files'] < size_files_limit) &
        (df['size_total_lines'] < size_lines_limit)
    ]
    print(f"\nPara os gráficos da RQ01, estamos focando nos dados abaixo do 95º percentil.")

    # 1. Box plot: Número de Arquivos vs. Status (com zoom)
    plt.figure(figsize=(10, 7))
    sns.boxplot(x='status', y='size_files', data=df_filtered_rq01, palette=['#2ca02c', '#d62728'])
    plt.title('RQ01: Número de Arquivos por Status do PR (Foco em 80% dos Dados)', fontsize=16)
    plt.xlabel('Status Final do PR', fontsize=12)
    plt.ylabel('Número de Arquivos Modificados', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq01_arquivos_vs_status_zoom.png')
    print("Gráfico 'rq01_arquivos_vs_status_zoom.png' salvo.")

    # 2. Box plot: Total de Linhas vs. Status (com zoom)
    plt.figure(figsize=(10, 7))
    sns.boxplot(x='status', y='size_total_lines', data=df_filtered_rq01, palette=['#2ca02c', '#d62728'])
    plt.title('RQ01: Total de Linhas por Status do PR (Foco em 80% dos Dados)', fontsize=16)
    plt.xlabel('Status Final do PR', fontsize=12)
    plt.ylabel('Total de Linhas Modificadas (Add+Del)', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq01_linhas_vs_status_zoom.png')
    print("Gráfico 'rq01_linhas_vs_status_zoom.png' salvo.")


    # --- Gráficos para a RQ05 (Focando na tendência principal) ---
    
    # Vamos usar o mesmo filtro para os gráficos de dispersão
    reviews_limit = df['reviews_count'].quantile(0.95)
    df_filtered_rq05 = df[
        (df['size_files'] < size_files_limit) &
        (df['size_total_lines'] < size_lines_limit) &
        (df['reviews_count'] < reviews_limit)
    ]
    print(f"\nPara os gráficos da RQ05, também focamos no 95º percentil.")


    # 3. Scatter plot: Número de Arquivos vs. Número de Revisões (com zoom)
    plt.figure(figsize=(10, 7))
    sns.regplot(x='size_files', y='reviews_count', data=df_filtered_rq05,
                scatter_kws={'alpha':0.6}, line_kws={'color':'red'})
    plt.title('RQ05: Arquivos vs. Revisões (Foco em 80% dos Dados)', fontsize=16)
    plt.xlabel('Número de Arquivos Modificados', fontsize=12)
    plt.ylabel('Número de Revisões', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq05_arquivos_vs_revisoes_zoom.png')
    print("Gráfico 'rq05_arquivos_vs_revisoes_zoom.png' salvo.")

    # 4. Scatter plot: Total de Linhas vs. Número de Revisões (com zoom)
    plt.figure(figsize=(10, 7))
    sns.regplot(x='size_total_lines', y='reviews_count', data=df_filtered_rq05,
                scatter_kws={'alpha':0.6}, line_kws={'color':'red'})
    plt.title('RQ05: Linhas vs. Revisões (Foco em 80% dos Dados)', fontsize=16)
    plt.xlabel('Total de Linhas Modificadas (Add+Del)', fontsize=12)
    plt.ylabel('Número de Revisões', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq05_linhas_vs_revisoes_zoom.png')
    print("Gráfico 'rq05_linhas_vs_revisoes_zoom.png' salvo.")


except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho especificado: {file_path}")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")