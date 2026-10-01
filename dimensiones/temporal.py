"""Dimensión temporal — Integrante 3.

Editar solo este archivo y templates/temporal.html.
"""
from flask import Blueprint, render_template
import plotly.express as px
import pandas as pd

from datos import cargar_datos
from graficas import a_html

bp = Blueprint("temporal", __name__)

PREGUNTA = ("¿Cómo ha cambiado el comportamiento de la población durante "
            "el periodo disponible?")


@bp.route("/dimension/temporal")
def tablero():
    df = cargar_datos()

    # --- Indicadores ---
    total_casos = f"{len(df):,}".replace(",", ".")
    
    anio_mas_casos = df['anio'].value_counts().idxmax()
    casos_anio_max = f"{df['anio'].value_counts().max():,}".replace(",", ".")

    mes_max = df['mes'].value_counts().idxmax()
    casos_mes_max = f"{df['mes'].value_counts().max():,}".replace(",", ".")

    indicadores = {
        "total": total_casos,
        "anio_max": f"{anio_mas_casos} ({casos_anio_max} casos)",
        "mes_max": f"{mes_max} ({casos_mes_max} casos)"
    }

    # --- Gráfica 1: Evolución histórica (Línea de tiempo) ---
    df_mes = df.groupby('mes').size().reset_index(name='casos')
    df_mes['mes'] = df_mes['mes'].astype(str)
    
    fig1 = px.line(
        df_mes, x="mes", y="casos", 
        title="Evolución mensual de casos notificados",
        markers=True,
        labels={"mes": "Mes y Año", "casos": "Número de Casos"}
    )
    grafica1 = a_html(fig1)

    # --- Gráfica 2: Comparación anual (Barras) ---
    df_anio = df.dropna(subset=['anio']).groupby('anio').size().reset_index(name='casos')
    df_anio['anio'] = df_anio['anio'].astype(int).astype(str)

    fig2 = px.bar(
        df_anio, x="anio", y="casos",
        title="Total de casos por año",
        labels={"anio": "Año", "casos": "Casos Confirmados"},
        text_auto='.2s'
    )
    grafica2 = a_html(fig2)

    # --- Gráfica 3: Estacionalidad mensual acumulada ---
    df['mes_num'] = df['fecha_notificacion'].dt.month
    df_estacional = df.dropna(subset=['mes_num']).groupby('mes_num').size().reset_index(name='casos')
    
    nombres_meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
                     7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    df_estacional['mes_nombre'] = df_estacional['mes_num'].map(nombres_meses)
    
    fig3 = px.bar(
        df_estacional, x="mes_nombre", y="casos",
        title="Suma histórica de casos agrupados por mes",
        labels={"mes_nombre": "Mes", "casos": "Acumulado Histórico"},
        category_orders={"mes_nombre": list(nombres_meses.values())}
    )
    # Colorear la barra más alta para resaltarla
    fig3.update_traces(marker_color=['#e07a3f' if x == 'Jun' else '#0f6e7c' for x in df_estacional['mes_nombre']])
    grafica3 = a_html(fig3)

    return render_template(
        "temporal.html", 
        pregunta=PREGUNTA,
        indicadores=indicadores,
        grafica1=grafica1,
        grafica2=grafica2,
        grafica3=grafica3
    )
