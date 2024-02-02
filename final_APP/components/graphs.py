# -----------------------------------------------------------------------------
# Table FRAME X: "Segmentos Reen" Y: "Segmento AHA"
# -----------------------------------------------------------------------------
#PARA GRAFICAR
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from trame.widgets import vuetify2 as vuetify

#PARA LEER JSON
import json
import pandas as pd

from components.fromJsonToTable import fetch_data

def plotly_graph_vuetify():
    df = fetch_data('output.json')  # get data from fetch_data function

    fig = px.scatter(df, x="Segmento AHA", y="Segmentos Reen")

    # Convert the Plotly Express figure to a JSON string
    fig_json = fig.to_json()

    with vuetify.VContainer(fluid=True):
        with vuetify.VRow(dense=True):
            vuetify.VSpacer()

            # Convert the JSON string to a format that can be used with the plotly.Figure class
            # figure = go.Figure(data=pio.from_json(fig_json).data)


            vuetify.VSpacer()