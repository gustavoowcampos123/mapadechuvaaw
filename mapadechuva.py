import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

coordenadas = {
    'São Paulo': (-23.5505, -46.6333),
    'Campinas': (-22.9056, -47.0608),
    'São Bernardo do Campo': (-23.6821, -46.5657),
    'São José dos Campos': (-23.2237, -45.9009),
    'Sorocaba': (-23.5012, -47.4875),
    'Ribeirão Preto': (-21.1730, -47.8103),
    'Santo André': (-23.6637, -46.5383),
    'Osasco': (-23.5329, -46.7918),
    'Diadema': (-23.6854, -46.6203),
    'Bauru': (-22.3034, -49.0500),
    'Piracicaba': (-23.7272, -47.6500),
    'Jundiaí': (-23.1856, -46.8978),
    'Taubaté': (-22.9783, -45.5589),
    'Limeira': (-22.5584, -47.4895),
    'Mauá': (-23.6671, -46.4613),
}

def obter_previsao(cidade):
    lat, lon = coordenadas[cidade]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=America/Sao_Paulo"
    resposta = requests.get(url)
    return resposta.json()

def processar_dados(data):
    previsao = {'data': [], 'precipitação': []}
    for i, item in enumerate(data['daily']['time']):
        previsao['data'].append(datetime.strptime(item, '%Y-%m-%d').date())
        previsao['precipitação'].append(data['daily']['precipitation_sum'][i])
    return pd.DataFrame(previsao)

def plotar_previsao(df, cidade):
    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(df['data'], df['precipitação'], color='lightblue', edgecolor='blue', alpha=0.9)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom')

    ax.set_xlabel('Data', fontsize=16)
    ax.set_ylabel('Precipitação (mm)', fontsize=16)
    ax.set_title(f'Previsão de Precipitação — {cidade}', fontsize=20, pad=20)
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for index, row in df.iterrows():
        if row['precipitação'] > 0:
            ax.text(row['data'], row['precipitação'], '☔', fontsize=20, ha='center')
        else:
            ax.text(row['data'], 0.5, '☀️', fontsize=20, ha='center')

    plt.xticks(rotation=45, fontsize=12)
    plt.tight_layout()
    plt.savefig('previsao_chuva.png', dpi=150)
    print("Gráfico salvo em: previsao_chuva.png")

def main():
    print("=== Previsão de Chuva para Obras de Engenharia ===\n")
    cidades = list(coordenadas.keys())
    for i, c in enumerate(cidades, 1):
        print(f"  {i:2}. {c}")

    print()
    while True:
        try:
            escolha = int(input("Selecione o número da cidade: "))
            if 1 <= escolha <= len(cidades):
                break
            print(f"Digite um número entre 1 e {len(cidades)}.")
        except ValueError:
            print("Entrada inválida.")

    cidade = cidades[escolha - 1]
    print(f"\nBuscando previsão para {cidade}...")

    dados = obter_previsao(cidade)

    if 'daily' not in dados:
        print("Erro: dados indisponíveis.")
        return

    df = processar_dados(dados)

    print(f"\n{'Data':<14} {'Precipitação (mm)':>18}")
    print("-" * 33)
    for _, row in df.iterrows():
        icone = "☔" if row['precipitação'] > 0 else "☀️"
        print(f"{str(row['data']):<14} {row['precipitação']:>14.2f} mm  {icone}")

    plotar_previsao(df, cidade)

if __name__ == '__main__':
    main()
