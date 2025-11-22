# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 20:32:35 2025

@author: ezcem
"""

#http://127.0.0.1:8000 

# ============================
# LIBRERIAS
# ============================

import shiny
import pandas as pd
import plotly.express as px
from shiny import App, ui, render

# ============================
# CARGA DE DATOS
# ============================

DATA_PATH = "C:/Users/kelmb/Downloads/BASE/ERA5_CR_2000_2025_promedios.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])

# Crear columnas de tiempo
df["year"] = df["valid_time"].dt.year
df["month"] = df["valid_time"].dt.month
df["month_name"] = df["valid_time"].dt.month_name()  # si el locale da problema, lo dejamos así

# ============================
# INTERFAZ BÁSICA (UI)
# ============================

app_ui = ui.page_fluid(
    ui.h2("Analisis de la variabilidad temporal y espacial de precipitación"),
    ui.hr(),
    ui.input_select(
        "var",
        "Variable a graficar:",
        {
            "Temperatura_C": "Temperatura (°C)",
            "Precipitacion_mm": "Precipitación (mm)",
            "Radiacion_Wm2": "Radiación (W/m²)",
        },
        selected="Temperatura_C",
    ),
    ui.output_plot("plot_basic")
)

# ============================
# SERVER
# ============================

def server(input, output, session):

    @output #DECORADOR: Conecta una función del servidor con un espacio visible en la interfaz.
    @render.plot #RENDER: Indica qué tipo de cosa genera la función (ej:plot).
    def plot_basic():
        var = input.var()
        data = (
            df.groupby("year")[var]
              .mean()
              .reset_index()
        )
        fig = px.line(
            data,
            x="year",
            y=var,
            markers=True,
            title=f"Evolución anual de {var}"
        )
        return fig


# ============================
# EJECUCIÓN DE LA APP
# ============================

app = App(app_ui, server)
