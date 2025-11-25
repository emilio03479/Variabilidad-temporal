# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 20:32:35 2025

@author: ezcem
"""

# ============================
# LIBRERIAS
# ============================

import pandas as pd
import plotly.express as px
from shiny import App, ui
from shinywidgets import render_widget, output_widget
import xarray as xr

# ============================
# CARGA DE DATOS
# ============================

DATA_PATH = "ERA5_CR_2000_2025_promedios.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])

df["year"] = df["valid_time"].dt.year
df["month"] = df["valid_time"].dt.month
df["month_name"] = df["valid_time"].dt.month_name()

DATA_NC = "datos.nc"
ds = xr.open_dataset(DATA_NC)
df_nc = ds.to_dataframe().reset_index()

# Mapa entre nombres bonitos y nombres reales
VAR_MAP = {
    "Temperatura (°C)": "Temperatura_C",
    "Precipitación (mm)": "Precipitacion_mm",
    "Radiación (W/m²)": "Radiacion_Wm2",
}

app_ui = ui.page_fluid(
    ui.h2("Análisis de la variabilidad temporal y espacial"),
    ui.hr(),

    ui.input_select(
        "var",
        "Variable a graficar:",
        list(VAR_MAP.keys()),
        selected="Temperatura (°C)"
    ),

    output_widget("plot_basic"),

    ui.hr(),
    ui.h3("Mapa"),

    ui.input_select(
        "var_map",
        "Variable para mapa:",
        {
            "t2m": "Temperatura (°C)",
            "tp": "Precipitación (mm)",
            "ssrd": "Radiación (W/m²)",
        },
        selected="tp"
    ),

    output_widget("plot_map"),
)

def server(input, output, session):

    # ==============================
    # SERIE TEMPORAL (plotly widget)
    # ==============================
    @render_widget
    def plot_basic():
        label = input.var()
        col = VAR_MAP[label]

        data = df.groupby("year")[col].mean().reset_index()

        fig = px.line(
            data,
            x="year",
            y=col,
            markers=True,
            title=f"Evolución anual de {label}"
        )
        return fig

    
# ============================
# EJECUCIÓN DE LA APP
# ============================

app = App(app_ui, server)
