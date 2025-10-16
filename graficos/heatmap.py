import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Caminho para o arquivo do dataset
file_path = './dataset_completo.csv'

try:
    df = pd.read_csv(file_path)
    print("Dataset carregado com sucesso!")

    # Selecionar apenas as colunas numéricas
    numerical_df = df.select_dtypes(include=['float64', 'int64'])

    # Calcular a matriz de correlação de Spearman
    corr_matrix = numerical_df.corr(method='spearman')

    # Configurar o plot
    plt.figure(figsize=(12, 10))

    # Gerar o mapa de calor com a escala de -1 a 1
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap='coolwarm',
        fmt=".2f",
        linewidths=.5,
        vmin=-1,  # Define o valor mínimo da escala de cor
        vmax=1    # Define o valor máximo da escala de cor
    )

    # Adicionar títulos e ajustar layout
    plt.title('Mapa de Calor de Correlação de Spearman', fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Salvar a imagem
    plt.savefig('heatmap_correlation_scaled.png')
    print("Mapa de calor salvo como 'heatmap_correlation_scaled.png'")

except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho especificado: {file_path}")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")