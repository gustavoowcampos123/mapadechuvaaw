import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

def obter_coordenadas(cidade):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(cidade)
    if location:
        return location.latitude, location.longitude
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
    ax.bar(df['data'], df['precipitação'], color='blue', alpha=0.6)
    
    ax.set_xlabel('Data')
    ax.set_ylabel('Precipitação (mm)')
    ax.set_title('Previsão de Precipitação para os Próximos Dias')
    ax.grid()

    return fig

# Interface do Streamlit
st.title('Previsão de Chuva para Obras de Engenharia')
cidade = st.text_input('Digite o nome da cidade (ex: São Paulo, Rio de Janeiro, etc.):')

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
