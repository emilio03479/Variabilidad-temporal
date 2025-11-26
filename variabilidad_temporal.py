# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 20:32:35 2025

@author: ezcem
"""

# ============================
# LIBRERIAS
# ============================


import shiny
import pandas as pd
import plotly.express as px
from shiny import App, ui, render
import xarray as xr
from shinywidgets import output_widget, render_widget
from plotly import graph_objects as go



# ============================
# CARGA DE DATOS
# ============================

DATA_PATH = "ERA5_CR_2000_2025_promedios.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["valid_time"])

# ============================
# CREAR COLUMNAS A TIEMPO
# ============================
df["year"] = df["valid_time"].dt.year
df["month"] = df["valid_time"].dt.month
df["month_name"] = df["valid_time"].dt.month_name()


DATA_NC = "datos.nc"
ds = xr.open_dataset(DATA_NC)


# ============================
# CONVERTIR A DATAFRAME
# ============================
df_nc = ds.to_dataframe().reset_index()
# Crear nueva columna en df_nc en °C
df_nc["t2m_C"] = df_nc["t2m"] - 273.15

VAR_MAP = {
    "Temperatura (°C)": "Temperatura_C",
    "Precipitación (mm)": "Precipitacion_mm",
    "Radiación (W/m²)": "Radiacion_Wm2",
}


# ============================
# INTERFAZ
# ============================

app_ui = ui.page_fluid(
    ui.h1("Análisis de la variabilidad climática en Costa Rica (2000–2025)"),
    ui.hr(),
    
    # ============================
    # SERIE TEMPORAL ANUAL
    # ============================
    ui.h2("Serie temporal anual de la temperatura, precipitación o radiación"),
    
    ui.input_select(
        "var",
        "Elegir variable:",
        list(VAR_MAP.keys()),
        selected="Temperatura (°C)",
    ),
    output_widget("plot_basic"),
    

    # ============================
    # MAPA CLIMATICO
    # ============================
    ui.hr(),
    ui.h3("Mapas climáticos mensuales de radiación, temperatura y precipitación en Costa Rica"),
    
    ui.input_select(
        "anio_map",
        "Elegir año:",
        sorted(df_nc["valid_time"].dt.year.unique().astype(str))
    ),
    
    ui.input_select(
        "mes_map",
        "Elegir mes:",
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
                ui.output_ui("map_radiacion")
                )
            ),
        
        ui.column(
            4,
            ui.card(
                ui.card_header("Temperatura (ºC)"),
                ui.output_ui("map_temperatura")
            )
            ),
        
        ui.column(
            4,
            ui.card(
                ui.card_header("Precipitación(mm)"),
                ui.output_ui("map_precipitacion")
            ),
        ),
    ),
    # ============================
    # BOXPLOT MENSUAL
    # ============================
    ui.hr(),
    ui.h3("Variabilidad mensual de la temperatura, precipitación o radiación"),
    
    ui.input_select(
        "var_box",
        "Elegir variable:",
        list(VAR_MAP.keys()),
        selected="Precipitación (mm)",
    ),
    output_widget("plot_box"),

)


# ============================
# SERVER
# ============================

def server(input, output, session):

    # ============================
    # SERIE TEMPORAL ANUAL
    # ============================
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
            title=f"Serie temporal anual de {label} en Costa Rica",
            labels={"year": "Año", col: label},
        )
        return fig
    
    # ============================
    # FILTRO MES/AÑO
    # ============================
    def filtrar_mes_anio():
        anio = int(input.anio_map())
        mes = int(input.mes_map())

        df_filtro = df_nc[
            (df_nc["valid_time"].dt.year == anio) &
            (df_nc["valid_time"].dt.month == mes)
        ]
        return df_filtro


    # =============== MAPA RADIACION ==================
    @output
    @render.ui

    def map_radiacion():
        data = filtrar_mes_anio()
        fig = px.scatter_mapbox(
            data,
            lat="latitude",
            lon="longitude",
            color="ssrd",
            title=f"Radiación (W/m²) — {input.mes_map()} / {input.anio_map()}",
            color_continuous_scale="turbo",
            zoom=5.8,  # ajusta zoom según Costa Rica
            center={"lat": 9.9, "lon": -84.3},
            height=600,
        )

        fig.update_layout(mapbox_style="open-street-map")  # estilo básico
        fig.update_coloraxes(colorbar=dict(title="W/m²", len=0.7, y=0.5))

      
        return ui.HTML(fig.to_html(full_html=False))


    
    # =============== MAPA TEMPERATURA ==================
    @output
    @render.ui

    def map_temperatura():
        data = filtrar_mes_anio()
        fig = px.scatter_mapbox(
            data,
            lat="latitude",
            lon="longitude",
            color="t2m_C",
            title=f"Temperatura (°C) — {input.mes_map()} / {input.anio_map()}",
            color_continuous_scale="turbo",
            zoom=5.8,  # ajusta zoom según Costa Rica
            center={"lat": 9.9, "lon": -84.3},
            height=600,
        )

        fig.update_layout(mapbox_style="open-street-map")  # estilo básico
        fig.update_coloraxes(colorbar=dict(title="°C", len=0.7, y=0.5))
        
        return ui.HTML(fig.to_html(full_html=False))

    # =============== MAPA PRECIPITACIÓN ==================
    @output
    @render.ui

    def map_precipitacion():
        data = filtrar_mes_anio()
        fig = px.scatter_mapbox(
            data,
            lat="latitude",
            lon="longitude",
            color="tp",
            title=f"Precipitación (mm) — {input.mes_map()} / {input.anio_map()}",
            color_continuous_scale="RdBu_r",
            zoom=5.8,  # ajusta zoom según Costa Rica
            center={"lat": 9.9, "lon": -84.3},
            height=600,
        )

        fig.update_layout(mapbox_style="open-street-map")  # estilo básico
        fig.update_coloraxes(colorbar=dict(title="mm", len=0.7, y=0.5))
        
        return ui.HTML(fig.to_html(full_html=False))


    


    # ============================
    # BOXPLOT
    # ============================
    @render_widget
    def plot_box():
        label = input.var_box()
        col = VAR_MAP[label]

        # ============================
        # OBSERVACIÓN = MES/AÑO
        # ============================
        data = df.copy()

        fig = px.box(
            data,
            x="month",
            y=col,
            category_orders={"month": list(range(1, 13))},
            labels={"month": "Mes", col: label},
            title=f"Distribución mensual de {label} en Costa Rica",
        )

        return fig



# ============================
# EJECUCIÓN DE LA APP
# ============================

app = App(app_ui, server)


#if __name__ == "__main__":
    #app.run()
