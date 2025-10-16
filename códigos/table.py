import pandas as pd

# Caminho para o arquivo do dataset, conforme solicitado
file_path = './dataset_completo.csv'

try:
    # Carregar o dataset a partir do arquivo CSV
    df = pd.read_csv(file_path)
    print(f"Dataset carregado com sucesso do caminho: {file_path}")

    # Criar a métrica 'Tamanho (Linhas Add+Del)'
    df['size_lines_total'] = df['size_additions'] + df['size_deletions']

    # Definir as colunas que queremos analisar e seus nomes na tabela
    metrics_to_analyze = {
        'size_files': 'Tamanho (Arquivos)',
        'size_lines_total': 'Tamanho (Linhas Add+Del)',
        'analysis_time_hours': 'Tempo de Análise (Horas)',
        'description_chars': 'Descrição (Caracteres)',
        'interaction_participants': 'Interações (Participantes)',
        'interaction_comments': 'Interações (Comentários)'
    }

    # Agrupar por status e calcular a mediana para cada métrica
    median_results = df.groupby('status')[list(metrics_to_analyze.keys())].median()

    # Renomear as colunas para a tabela final
    median_results = median_results.rename(columns=metrics_to_analyze)

    # Exibir os resultados transpostos para facilitar a cópia
    print("\n### Valores medianos para a Tabela ###")
    print(median_results.transpose())

except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado no caminho especificado: {file_path}")
    print("Por favor, certifique-se de que o arquivo 'dataset_completo.csv' está no mesmo diretório que o script.")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")