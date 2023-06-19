from distutils.log import debug
from multiprocessing.sharedctypes import Value
from select import select
from tkinter import LAST
from tkinter.ttk import Style
from turtle import clear
from typing import Container
import pandas as pd
import geopandas as gpd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import numpy as np
import csv
import json
import wikipedia


propriedade_name = 'Sitio Gira Saol'

# ================================================================ Datasets ======================================================================
df_rdo = pd.read_csv('rdo.CSV', sep=';', encoding='latin-1')
df_regenerantes = pd.read_csv('Regenerantes.csv', sep=';', encoding='latin-1')
df_propriedade = pd.unique(df_rdo['Propriedade'])
df_unico =pd.unique(df_regenerantes['Regenerante'])
df_coordenadas = pd.read_csv('Geoloc_clear.CSV', sep=';', encoding='latin-1')

df_cov_acumulado = df_rdo.groupby(['Propriedade', 'Data RDO'])['Coveamento'].sum().groupby(level=0).cumsum().reset_index()
df_plant_acumulado = df_rdo.groupby(['Propriedade', 'Data RDO'])['Plantio'].sum().groupby(level=0).cumsum().reset_index()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
# =========================================== Criação mapa  ===================================================
px.set_mapbox_access_token("pk.eyJ1IjoiYW5kcmV2YWxidXNhIiwiYSI6ImNsYWxzbDJoczA2c2Izb3BkbDBiejNrOW8ifQ.IDwWHY7_6fH_1IZJslqrsQ")
fig_map = px.scatter_mapbox(df_coordenadas, lat='Latitude', lon='Longitude', zoom=9, size='Plantio', color='Coveamento')

fig_map.update_layout(
    plot_bgcolor='#242424',
    paper_bgcolor='#242424',
    autosize=True,
    margin=go.layout.Margin(l=10, r=0, t=25, b=15),
    showlegend=False,
    mapbox_style='carto-darkmatter',
)

# =========================================== Criação gráfico  ===================================================
trace1 = go.Scatter(x=df_rdo['Data RDO'], y=df_cov_acumulado['Coveamento'], mode='lines' , name='Coveamento')
trace2 = go.Scatter(x=df_rdo['Data RDO'], y=df_plant_acumulado['Plantio'], mode='lines', name='Plantio')
data_graph = [trace1, trace2]

fig_graph = dict(data = data_graph)
layout = dict(
    xaxis=dict(
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False
    ),
    paper_bgcolor='#242424',
    plot_bgcolor='#242424',
    autosize=True,
    margin=go.layout.Margin(l=10, r=10, t=10, b=10)
)

#=================================================================== Layout ========================================================================
app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(id='logo', src='https://i.postimg.cc/zf6tMmvm/logo.png',
                        width="50", height="50"),
                html.H6(' Reflorestamento da Bacia do Rio Doce'),
            ], style={'margin-left':'0px'}),
            html.Div([
                dcc.Dropdown(df_propriedade, 'Bela Vista',  id='cx_proprietario', clearable=False)
            ],  style={'margin-top': '20px', 'margin-bottom': '10px', 'width': '100%'}),
            html.Div([
                dbc.RadioItems(
                    id='show_btn', 
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": " Mapa ", "value": 1, 'width': '100px'},
                        {"label": "Grafico", "value": 2, 'width': '100px'},
                    ],
                    style={'margin-bottom': '10px', 'margin-left': '60px' }),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(f'Localidade: '), 
                            html.Span(id='cartao_localidade'),
                            html.Div(f'Proprietário: '), 
                            html.Span(id='cartao_proprietario'),
                            html.Div(f'Codigo: '),
                            html.Span(id='cartao_cod'),
                            html.Div(f'Inicio: '), 
                            html.Span(id='cartao_inicio'),
                            html.Div(f'Fim: '), 
                            html.Span(id='cartao_fim')

                        ])
                    ], color='light', outline=True, style={}),
                    dcc.Loading(id='loading2', type='default',
                        children=[
                            dbc.Card([
                                dbc.CardImg(top=True, id='imagem_especie'),
                                dbc.CardBody([
                                    html.H6(id='nome_especie'),
                                    html.P(id='text_especie'),
                                ]),
                                dbc.Button('Go Wiki', color='primary'),
                            ], style={})
                    ]),
                ], md=12),
            ]),
        ], md=3, style={'background-color': '#242424', 'padding': '12px', 'height': '100vh'}),
        dbc.Col([
            dbc.Row([
                 dcc.Loading(id='loading1', type='default',
                        children=[
                            dcc.Graph(id='choropleth-map', figure=fig_map,
                                      style={'border-radius': '12px', 'height': '70vh'})
                ]),
            ]),
            dbc.Row([
                dcc.Loading(id='loading3', type='default',
                         children=[
                             dcc.Graph(id='line-graph', figure=fig_graph,
                                style={'border-radius': '7px', 'height': '30vh'})
                ]),
            ]),
        ], md=9, style={'height': '100%'})
    ]), fluid=True)



#=========================================================== callbacks ===========================================================

@app.callback(
    [
        Output('cartao_localidade', 'children'),
        Output('cartao_proprietario', 'children'),
        Output('cartao_inicio', 'children'),
        Output('cartao_fim', 'children'),
        Output('cartao_cod', 'children'),
    ],    
    [
        Input('cx_proprietario', 'value')
    ]  
)
def display_info(propriedade_name):

    cartao_localidade = df_rdo['Localidade'].loc[propriedade_name == df_rdo['Propriedade']].iloc[0]
    cartao_proprietario = df_rdo['Proprietario'].loc[propriedade_name == df_rdo['Propriedade']].iloc[0]
    cartao_inicio = df_rdo['Data RDO'].loc[propriedade_name == df_rdo['Propriedade']].iloc[0]
    cartao_fim = df_rdo['Data RDO'].loc[propriedade_name == df_rdo['Propriedade']].iloc[-1]
    cartao_cod = df_rdo['ID'].loc[propriedade_name == df_rdo['Propriedade']].iloc[0]
    return(cartao_localidade, cartao_proprietario, cartao_inicio, cartao_fim, cartao_cod)

@app.callback(
        Output('line-graph', 'figure'),
    [
        Input('cx_proprietario', 'value')
    ]
)
def plot_graf(propriedade_name):
    df_covline = df_cov_acumulado[df_cov_acumulado['Propriedade'] == propriedade_name]
    df_plantline = df_plant_acumulado[df_plant_acumulado['Propriedade'] == propriedade_name] 

    fig_graph = go.Figure() 
    fig_graph.add_traces([go.Scatter(x=df_plantline['Data RDO'], y=df_covline['Coveamento']),
                      go.Scatter(x=df_plantline['Data RDO'], y=df_plantline['Plantio'])
                    ])

    fig_graph.update_layout(
    xaxis=dict(
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False
    ),
    paper_bgcolor='#242424',
    plot_bgcolor='#242424',
    autosize=True,
    margin=go.layout.Margin(l=10, r=10, t=10, b=10)
    )

    return(fig_graph)

@app.callback(
    [
        Output('nome_especie', 'children'),
        Output('text_especie', 'children'),
    ],
    [
        Input('cx_proprietario', 'value')
    ]
)
def card_especies(propriedade_name):

    cod = df_rdo['ID'].loc[propriedade_name == df_rdo['Propriedade']].iloc[0]
    df_especies = df_regenerantes['Regenerante'].loc[cod == df_regenerantes['Propriedade']]
    wikipedia.set_lang("pt")
    reg_obj = (df_especies.iloc[0])
    reg_sumary = wikipedia.summary(reg_obj)[0:200]

    return(reg_obj, reg_sumary)

@app.callback(
    [
        Output('loading1', 'children'),
        Output('loading3', 'children'),
    ],
    [
        Input('show_btn', 'value')
    ]
)
def plotsize(value):
 
    if value == 1:
        fig_map = px.scatter_mapbox(df_coordenadas, lat='Latitude', lon='Longitude', zoom=9, size='Plantio', color='Coveamento')

        fig_map.update_layout(
            plot_bgcolor='#242424',
            paper_bgcolor='#242424',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=25, b=15),
            showlegend=False,
            mapbox_style='carto-darkmatter',
        )
        plot_graph = dcc.Graph(id='line-graph', figure=fig_graph, style={'height': '30vh'})
        plot_map = dcc.Graph(id='choropleth-map', figure=fig_map, style={'height': '70vh'})

        return(plot_map, plot_graph)
    elif value == 2:
        fig_map = px.scatter_mapbox(df_coordenadas, lat='Latitude', lon='Longitude', zoom=9, size='Plantio', color='Coveamento')

        fig_map.update_layout(
            plot_bgcolor='#242424',
            paper_bgcolor='#242424',
            autosize=True,
            margin=go.layout.Margin(l=10, r=0, t=25, b=15),
            showlegend=False,
            mapbox_style='carto-darkmatter',
        )
        plot_graph = dcc.Graph(id='line-graph', figure=fig_graph, style={'height': '70vh'})
        plot_map = dcc.Graph(id='choropleth-map', figure=fig_map, style={'height': '30vh'})

        return(plot_graph, plot_map)
    
@app.callback(
    [
        Output('choropleth-map', 'figure'),
    ],    
    [
        Input('cx_proprietario', 'value')
    ]  
)
def Interative_map(propriedade_name):

    cod = df_rdo['ID'].loc[propriedade_name == df_rdo['Propriedade']].iloc[0]
    latitude_zoom = df_coordenadas['Latitude'].loc[cod == df_coordenadas['Cod']].iloc[0]
    longitude_zoom = df_coordenadas['Longitude'].loc[cod == df_coordenadas['Cod']].iloc[0]

    fig_map = px.scatter_mapbox(df_coordenadas, 
                                lat='Latitude', lon='Longitude', 
                                zoom=9, 
                                size='Plantio', color='Coveamento')

    fig_map.update_layout(
    mapbox=dict(center = go.layout.mapbox.Center(lat=latitude_zoom, lon=longitude_zoom),
                                                 zoom = 19),
    plot_bgcolor='#242424',
    paper_bgcolor='#242424',
    autosize=True,
    margin=go.layout.Margin(l=10, r=0, t=25, b=15),
    showlegend=False,
    mapbox_style='carto-darkmatter',
    )

    return(fig_map)

if __name__ == '__main__':
     app.run_server(debug=True)
