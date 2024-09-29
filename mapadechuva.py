import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

# Lista de cidades do estado de São Paulo com coordenadas
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
    'Mauá': (-23.6671, -46.4613),
    'Bauru': (-22.3034, -49.0500),
    'Piracicaba': (-23.7272, -47.6500),
    'São Carlos': (-22.0058, -47.8973),
    'Jundiaí': (-23.1856, -46.8978),
    'Taubaté': (-22.9783, -45.5589),
    'Indaiatuba': (-23.0862, -47.2022),
    'Franca': (-20.5356, -47.5297),
    'Botucatu': (-23.1860, -47.5259),
    'Itu': (-23.2629, -47.3003),
    'Bragança Paulista': (-22.9532, -46.5386),
    'Barueri': (-23.5011, -46.8756),
    'Atibaia': (-23.1165, -46.5510),
    'Santo Antônio do Jardim': (-22.0686, -46.5407),
    'Marília': (-22.2160, -50.4411),
    'Limeira': (-22.5584, -47.4895),
    'Mogi das Cruzes': (-23.5225, -45.0889),
    'São Vicente': (-23.9657, -46.3843),
    'Jacareí': (-23.7471, -45.8848),
    'Cotia': (-23.6346, -47.0863),
    'Poá': (-23.5457, -46.3826),
    'Caieiras': (-23.3347, -46.7261),
    'Salesópolis': (-23.3541, -45.8261),
    'Tatuí': (-23.3485, -47.5300),
    'Ubatuba': (-23.4338, -45.0737),
    'Caraguatatuba': (-23.6161, -45.4200),
    'Ilhabela': (-23.7664, -45.3484),
    'Guarulhos': (-23.4626, -46.5383),
    'São Roque': (-23.5308, -47.1033),
    # Adicione mais cidades conforme necessário
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
        previsao['data'].append(datetime.strptime(item, '%Y-%m-%d').date())
        previsao['precipitação'].append(data['daily']['precipitation_sum'][data['daily']['time'].index(item)])
        
    return pd.DataFrame(previsao)

def plotar_previsao(df):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Estilo do gráfico
    bars = ax.bar(df['data'], df['precipitação'], color='skyblue', edgecolor='blue', alpha=0.7)
    
    # Anotações
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 1), ha='center', va='bottom')

    # Títulos e Rótulos
    ax.set_xlabel('Data', fontsize=14)
    ax.set_ylabel('Precipitação (mm)', fontsize=14)
    ax.set_title('Previsão de Precipitação para os Próximos Dias', fontsize=16)
    
    # Melhorando a aparência
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Adicionando ícones (caso tenha imagens locais)
    # Você pode substituir pela imagem de ícone de chuva que preferir
    for index, row in df.iterrows():
        if row['precipitação'] > 0:
            ax.text(row['data'], row['precipitação'], '☔', fontsize=20, ha='center')

    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

# Interface do Streamlit
st.title('Previsão de Chuva para Obras de Engenharia')
cidade = st.text_input('Digite o nome da cidade (ex: São Paulo, Campinas, etc.):')

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
