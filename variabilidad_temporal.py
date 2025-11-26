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
from shinywidgets import output_widget, render_widget


# ============================
# CARGA DE DATOS
# ============================

DATA_PATH = "ERA5_CR_2000_2025_promedios.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])

# Crear columnas de tiempo
df["year"] = df["valid_time"].dt.year
df["month"] = df["valid_time"].dt.month

df["month_name"] = df["valid_time"].dt.month_name()


DATA_NC = "datos.nc"
ds = xr.open_dataset(DATA_NC)


# Convertir a dataframe
df_nc = ds.to_dataframe().reset_index()

VAR_MAP = {
    "Temperatura (°C)": "Temperatura_C",
    "Precipitación (mm)": "Precipitacion_mm",
    "Radiación (W/m²)": "Radiacion_Wm2",
}



# ============================
# INTERFAZ
# ============================
app_ui = ui.page_fluid(

    
    ui.h2("Analisis de la variabilidad temporal y espacial de precipitación"),
    ui.hr(),
    

    ui.h2("Análisis de la variabilidad temporal y estacional"),
    ui.hr(),

    # Serie temporal anual

    ui.input_select(
        "var",
        "Variable para serie temporal:",
        list(VAR_MAP.keys()),
        selected="Temperatura (°C)",
    ),

    ui.output_plot("plot_basic"),
    
    
    ui.hr(),
    ui.h3("Mapas climáticos para Costa Rica"),
    ui.input_select(
        "anio_map",
        "Año:",
        sorted(df_nc["valid_time"].dt.year.unique().astype(str))
    ),
    
    ui.input_select(
        "mes_map",
        "Mes:",
        {
            "1":"Enero", "2": "Febrero", "3": "Marzo", 
            "4": "Abril", "5": "Mayo", "6": "Junio",
            "7": "Julio", "8": "Agosto", "9": "Setiembre",
            "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
            }
    ),
    
    ui.row(
        
        ui.column(
            4,
            ui.card(
                ui.card_header("Radiación (W/m²)"),
                output_widget("map_radiacion")
                )
        ),
        
        ui.column(
            4,
            ui.card(
                ui.card_header("Temperatura (ºC)"),
                output_widget("map_temperatura")
            )
        ),
        
        ui.column(
            4,
            ui.card(
                ui.card_header("Precipitación(mm)"),
               output_widget("map_precipitacion")
            )
        )
    )

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

    
    # =============== FILTRO MES / AÑO ==================
    def filtrar_mes_anio():
        anio = int(input.anio_map())
        mes = int(input.mes_map())

        df_filtro = df_nc[
            (df_nc["valid_time"].dt.year == anio) &
            (df_nc["valid_time"].dt.month == mes)
        ]
        return df_filtro

    # =============== MAPA RADIACION ==================
    @render_widget

    def map_radiacion():
        data = filtrar_mes_anio()

        fig = px.scatter_geo(
            data,
            lat="latitude",
            lon="longitude",
            color="ssrd",
            title=f"Radiación (W/m²) — {input.mes_map()} / {input.anio_map()}",
            color_continuous_scale="turbo"
        )

        fig.update_geos(
            scope="north america",
            center=dict(lat=9.7, lon=-84.0),
            projection_scale=20
        )



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

    # =============== MAPA TEMPERATURA ==================
    @render_widget

    def map_temperatura():
        data = filtrar_mes_anio()

        fig = px.scatter_geo(
            data,
            lat="latitude",
            lon="longitude",
            color="t2m",
            title=f"Temperatura (°C) — {input.mes_map()} / {input.anio_map()}",
            color_continuous_scale="turbo"
        )

        fig.update_geos(
            scope="north america",
            center=dict(lat=9.7, lon=-84.0),
            projection_scale=20
        )

        return fig

    # =============== MAPA PRECIPITACIÓN ==================
    @render_widget

    def map_precipitacion():
        data = filtrar_mes_anio()

        fig = px.scatter_geo(
            data,
            lat="latitude",
            lon="longitude",
            color="tp",
            title=f"Precipitación (mm) — {input.mes_map()} / {input.anio_map()}",
            color_continuous_scale="RdBu_r"
        )

        fig.update_geos(
            scope="north america",
            center=dict(lat=9.7, lon=-84.0),
            projection_scale=20
        )

        return fig


    
# ============================
# EJECUCIÓN DE LA APP
# ============================

app = App(app_ui, server)


if __name__ == "__main__":
    app.run()
