import streamlit as st
import pandas as pd
import xlwings as xw
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def criar_dfs_excel():

    nome_excel = 'Campanha_Motoristas_Natal.xlsx'

    st.session_state.df_motoristas = pd.read_excel(nome_excel, sheet_name='BD - Motoristas')

    st.session_state.df_frota = pd.read_excel(nome_excel, sheet_name='BD - Frota | Tipo')

    st.session_state.df_frota['Veiculo'] = st.session_state.df_frota['Veiculo'].astype(str)

    st.session_state.df_historico = pd.read_excel(nome_excel, sheet_name='BD - Historico')

    st.session_state.df_historico = st.session_state.df_historico[st.session_state.df_historico['Veículo']!='Total'].reset_index(drop=True)

    for index in range(len(st.session_state.df_historico)):

        if pd.isna(st.session_state.df_historico.at[index, 'Veículo']):

            st.session_state.df_historico.at[index, 'Veículo']=st.session_state.df_historico.at[index-1, 'Veículo']

    lista_motoristas_historico = st.session_state.df_historico['Colaborador'].unique().tolist()

    for motorista in lista_motoristas_historico:

        if motorista in st.session_state.df_motoristas['Motorista Sofit'].unique().tolist():

            st.session_state.df_historico.loc[st.session_state.df_historico['Colaborador']==motorista, 'Colaborador']=\
                st.session_state.df_motoristas.loc[st.session_state.df_motoristas['Motorista Sofit']==motorista, 'Motorista Análise'].values[0]
            
    st.session_state.df_historico['ano'] = st.session_state.df_historico['Data'].dt.year

    st.session_state.df_historico['mes'] = st.session_state.df_historico['Data'].dt.month

    st.session_state.df_historico['ano_mes'] = st.session_state.df_historico['mes'].astype(str) + '/' + \
            st.session_state.df_historico['ano'].astype(str).str[-2:]
    
    st.session_state.df_historico = st.session_state.df_historico.rename(columns={'Veículo': 'Veiculo'})
    
    st.session_state.df_historico = pd.merge(st.session_state.df_historico, st.session_state.df_frota, on='Veiculo', how='left')

    st.session_state.df_historico['Apenas Data'] = st.session_state.df_historico['Data'].dt.date

st.set_page_config(layout='wide')

st.title('Abastecimentos com Anomalias - Natal')

st.divider()

row0 = st.columns(1)

if 'df_motoristas' not in st.session_state:

    criar_dfs_excel()

with row0[0]:

    atualizar_dfs_excel = st.button('Atualizar Dados')

    percentual_anomalias = st.number_input('Variação Percentual p/ Anomalia', step=1, value=30)

    percentual_anomalias = percentual_anomalias/100

df_filtro_colunas = st.session_state.df_historico[['Data', 'Despesa', 'Veiculo', 'Consumo real', 'Consumo estimado', 'Percentual do Estimado']]

df_filtro_colunas['Percentual do Estimado'] = df_filtro_colunas['Percentual do Estimado']/100

df_filtro_colunas['Perc - 1'] = df_filtro_colunas['Percentual do Estimado']-1

df_filtro_colunas.loc[(df_filtro_colunas['Perc - 1'] > percentual_anomalias) | (df_filtro_colunas['Perc - 1'] < -percentual_anomalias), 'Anomalia']='X'

df_filtro_colunas = df_filtro_colunas[df_filtro_colunas['Anomalia']=='X'].reset_index(drop=True)

df_filtro_colunas = df_filtro_colunas.rename(columns={'Veiculo': 'Veículo', 'Consumo real': 'Média km/l', 'Consumo estimado': 'Meta km/l'})

container_dataframe = st.container()

container_dataframe.dataframe(df_filtro_colunas[['Data', 'Despesa', 'Veículo', 'Média km/l', 'Meta km/l']], hide_index=True, use_container_width=True)

