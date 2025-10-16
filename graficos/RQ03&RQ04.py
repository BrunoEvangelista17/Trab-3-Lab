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

    # --- Gráfico para a RQ03: Relação entre Descrição e Status do PR ---
    
    # Filtrar os 10% de PRs com as maiores descrições para focar na distribuição principal
    desc_limit_rq03 = df['description_chars'].quantile(0.90)
    df_filtered_rq03 = df[df['description_chars'] <= desc_limit_rq03]
    print(f"\nPara o gráfico da RQ03, focando em PRs com descrição abaixo de {desc_limit_rq03:.0f} caracteres (90º percentil).")

    # 1. Overlapping Density Plots (Ridge Plot)
    plt.figure(figsize=(12, 7))
    sns.kdeplot(data=df_filtered_rq03, x='description_chars', hue='status',
                fill=True, alpha=0.5, common_norm=False, palette=['#2ca02c', '#d62728'])
    plt.title('RQ03: Distribuição do Tamanho da Descrição por Status do PR (Foco em 90% dos Dados)', fontsize=16)
    plt.xlabel('Tamanho da Descrição (Caracteres)', fontsize=12)
    plt.ylabel('Densidade', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq03_ridge_descricao_vs_status.png')
    print("Gráfico 'rq03_ridge_descricao_vs_status.png' salvo.")


    # --- Gráfico para a RQ07: Relação entre Descrição e Número de Revisões ---

    # Filtrar outliers de descrição e revisões para focar na tendência principal (90%)
    desc_limit_rq07 = df['description_chars'].quantile(0.90)
    reviews_limit_rq07 = df['reviews_count'].quantile(0.90)
    df_filtered_rq07 = df[
        (df['description_chars'] <= desc_limit_rq07) &
        (df['reviews_count'] <= reviews_limit_rq07)
    ]
    print(f"Para o gráfico da RQ07, focando nos 90% dos dados com menores valores.")

    # 2. Bar Plot com Dados Binarizados
    # Criar 4 bins (categorias) para o tamanho da descrição
    df_filtered_rq07['description_bin'] = pd.qcut(df_filtered_rq07['description_chars'], q=4, labels=['Muito Curta', 'Curta', 'Média', 'Longa'])
    
    plt.figure(figsize=(10, 7))
    sns.barplot(data=df_filtered_rq07, x='description_bin', y='reviews_count', palette='cividis', ci='sd')
    plt.title('RQ07: Média de Revisões por Tamanho da Descrição do PR (Foco em 90% dos Dados)', fontsize=16)
    plt.xlabel('Categoria de Tamanho da Descrição', fontsize=12)
    plt.ylabel('Média de Revisões (com Desvio Padrão)', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq07_binned_descricao_vs_revisoes.png')
    print("Gráfico 'rq07_binned_descricao_vs_revisoes.png' salvo.")


except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho especificado: {file_path}")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")