import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

# Lista de 15 cidades do estado de São Paulo com coordenadas
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

def obter_coordenadas(cidade):
    if cidade in coordenadas:
        return coordenadas[cidade]

    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(cidade)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        st.error(f"Erro ao obter coordenadas: {e}")

    return None, None

def obter_previsao(cidade):
    lat, lon = obter_coordenadas(cidade)
    
    if lat is None or lon is None:
        return None
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=America/Sao_Paulo"
    resposta = requests.get(url)
    return resposta.json()

def processar_dados(data):
    previsao = {'data': [], 'precipitação': []}
    
    for item in data['daily']['time']:
        precip = data['daily']['precipitation_sum'][data['daily']['time'].index(item)]
        
        previsao['data'].append(datetime.strptime(item, '%Y-%m-%d').date())
        previsao['precipitação'].append(precip)
        
    return pd.DataFrame(previsao)

def plotar_previsao(df):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Estilo do gráfico
    bars = ax.bar(df['data'], df['precipitação'], color='lightblue', edgecolor='blue', alpha=0.9)

    # Anotações
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center', va='bottom')

    # Títulos e Rótulos
    ax.set_xlabel('Data', fontsize=16)
    ax.set_ylabel('Precipitação (mm)', fontsize=16)
    ax.set_title('Previsão de Precipitação para os Próximos Dias', fontsize=20, pad=20)

    # Ajustar os limites do eixo Y
    ax.set_ylim(0, 100)  # Limite de 0 a 100 mm
    ax.set_yticks(range(0, 101, 10))  # Espaçamento de 10 em 10 mm

    # Melhorando a aparência
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Adicionando ícones
    for index, row in df.iterrows():
        if row['precipitação'] > 0:
            ax.text(row['data'], row['precipitação'], '☔', fontsize=20, ha='center')
        else:
            ax.text(row['data'], 0.5, '☀️', fontsize=20, ha='center')  # Ícone de sol para dias sem chuva

    plt.xticks(rotation=45, fontsize=12)
    plt.tight_layout()

    return fig

# Interface do Streamlit
st.title('Previsão de Chuva para Obras de Engenharia')
cidade = st.selectbox('Selecione o nome da cidade:', list(coordenadas.keys()))

if st.button('Obter Previsão'):
    if cidade:
        dados = obter_previsao(cidade)

        if dados and 'daily' in dados:
            df = processar_dados(dados)
            fig = plotar_previsao(df)

            st.pyplot(fig)
        else:
            st.error('Cidade não encontrada ou dados indisponíveis.')
    else:
        st.warning('Por favor, insira o nome da cidade.')