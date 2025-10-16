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

    # --- Gráfico para a RQ02: Relação entre Tempo e Status do PR ---
    
    # Filtrar os 20% de PRs com maior tempo de análise para focar na distribuição principal
    time_limit_rq02 = df['analysis_time_hours'].quantile(0.80)
    df_filtered_rq02 = df[df['analysis_time_hours'] <= time_limit_rq02]
    print(f"\nPara o gráfico da RQ02, focando em PRs com tempo de análise abaixo de {time_limit_rq02:.2f} horas (80º percentil).")

    # 1. Violin Plot: Tempo de Análise vs. Status
    plt.figure(figsize=(10, 7))
    sns.violinplot(x='status', y='analysis_time_hours', data=df_filtered_rq02, palette=['#2ca02c', '#d62728'])
    plt.title('RQ02: Distribuição do Tempo de Análise por Status do PR (Foco em 80% dos Dados)', fontsize=16)
    plt.xlabel('Status Final do PR', fontsize=12)
    plt.ylabel('Tempo de Análise (Horas)', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq02_violin_tempo_vs_status_80pct.png')
    print("Gráfico 'rq02_violin_tempo_vs_status_80pct.png' salvo.")


    # --- Gráfico para a RQ06: Relação entre Tempo e Número de Revisões ---

    # Filtrar outliers de tempo e revisões para focar na densidade principal (80%)
    time_limit_rq06 = df['analysis_time_hours'].quantile(0.80)
    reviews_limit_rq06 = df['reviews_count'].quantile(0.80)
    df_filtered_rq06 = df[
        (df['analysis_time_hours'] <= time_limit_rq06) &
        (df['reviews_count'] <= reviews_limit_rq06)
    ]
    print(f"Para o gráfico da RQ06, focando nos 80% dos dados com menores valores.")

    # 2. 2D Density Plot (KDE): Tempo de Análise vs. Número de Revisões
    plt.figure(figsize=(12, 8))
    sns.kdeplot(
        data=df_filtered_rq06,
        x='analysis_time_hours',
        y='reviews_count',
        fill=True,      
        thresh=0.05,    
        cmap='mako'     
    )
    plt.title('RQ06: Densidade de PRs por Tempo de Análise vs. Revisões (Foco em 80% dos Dados)', fontsize=16)
    plt.xlabel('Tempo de Análise (Horas)', fontsize=12)
    plt.ylabel('Número de Revisões', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq06_kde_tempo_vs_revisoes_80pct.png')
    print("Gráfico 'rq06_kde_tempo_vs_revisoes_80pct.png' salvo.")


except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho especificado: {file_path}")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")