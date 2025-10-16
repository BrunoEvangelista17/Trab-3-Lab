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

    # --- Gráficos para a RQ08: Relação entre Interações e Número de Revisões ---

    # Filtrar outliers para focar na tendência principal (90%)
    participants_limit = df['interaction_participants'].quantile(0.90)
    comments_limit = df['interaction_comments'].quantile(0.90)
    reviews_limit = df['reviews_count'].quantile(0.90)

    df_filtered = df[
        (df['interaction_participants'] <= participants_limit) &
        (df['interaction_comments'] <= comments_limit) &
        (df['reviews_count'] <= reviews_limit)
    ]
    print(f"\nPara os gráficos da RQ08, focando nos 90% dos dados com menores valores.")

    # 1. 2D Histogram (Heatmap): Número de Participantes vs. Número de Revisões
    plt.figure(figsize=(10, 8))
    h1 = plt.hist2d(data=df_filtered, x='interaction_participants', y='reviews_count', bins=10, cmap='inferno')
    plt.colorbar(h1[3], label='Contagem de PRs') # Adiciona a barra de cores
    plt.title('RQ08: Densidade de PRs por Participantes vs. Revisões (Heatmap)', fontsize=16)
    plt.xlabel('Número de Participantes', fontsize=12)
    plt.ylabel('Número de Revisões', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq08_heatmap_participantes_vs_revisoes.png')
    print("Gráfico 'rq08_heatmap_participantes_vs_revisoes.png' salvo.")

    # 2. 2D Histogram (Heatmap): Número de Comentários vs. Número de Revisões
    plt.figure(figsize=(10, 8))
    h2 = plt.hist2d(data=df_filtered, x='interaction_comments', y='reviews_count', bins=15, cmap='inferno')
    plt.colorbar(h2[3], label='Contagem de PRs')
    plt.title('RQ08: Densidade de PRs por Comentários vs. Revisões (Heatmap)', fontsize=16)
    plt.xlabel('Número de Comentários', fontsize=12)
    plt.ylabel('Número de Revisões', fontsize=12)
    plt.tight_layout()
    plt.savefig('rq08_heatmap_comentarios_vs_revisoes.png')
    print("Gráfico 'rq08_heatmap_comentarios_vs_revisoes.png' salvo.")


except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho especificado: {file_path}")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")