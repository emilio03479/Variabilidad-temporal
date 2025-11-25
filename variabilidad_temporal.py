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

# Crear columnas de tiempo
df["year"] = df["valid_time"].dt.year
df["month"] = df["valid_time"].dt.month

df["month_name"] = df["valid_time"].dt.month_name()

VAR_MAP = {
    "Temperatura (°C)": "Temperatura_C",
    "Precipitación (mm)": "Precipitacion_mm",
    "Radiación (W/m²)": "Radiacion_Wm2",
}

# ============================
# INTERFAZ
# ============================
app_ui = ui.page_fluid(
    ui.h2("Análisis de la variabilidad temporal y estacional"),
    ui.hr(),

    # Serie temporal anual
    ui.input_select(
        "var",
        "Variable para serie temporal:",
        list(VAR_MAP.keys()),
        selected="Temperatura (°C)",
    ),
    output_widget("plot_basic"),

    ui.hr(),

    # Boxplot mensual (estacionalidad y variabilidad)
    ui.h3("Estacionalidad y variabilidad mensual (boxplot)"),
    ui.input_select(
        "var_box",
        "Variable para boxplot:",
        list(VAR_MAP.keys()),
        selected="Precipitación (mm)",
    ),
    output_widget("plot_box"),
)

# ============================
# SERVER
# ============================
def server(input, output, session):

    # Serie temporal anual
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
            title=f"Evolución anual de {label}",
        )
        return fig

    # Boxplot mensual
    @render_widget
    def plot_box():
        label = input.var_box()
        col = VAR_MAP[label]

        # Cada observación es un mes-año; graficamos distribución por mes
        data = df.copy()

        fig = px.box(
            data,
            x="month",
            y=col,
            category_orders={"month": list(range(1, 13))},
            labels={"month": "Mes", col: label},
            title=f"Distribución mensual de {label} (boxplot)",
        )
        return fig

    
# ============================
# EJECUCIÓN DE LA APP
# ============================

app = App(app_ui, server)
