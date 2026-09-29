"""Dimensión territorial — Integrante 2 (Diego Armando Guzmán Garzón).

Pregunta: ¿Cómo se distribuye la población y sus principales características
entre los territorios disponibles?

El dataset del equipo solo contiene Chía, así que esta dimensión usa un extracto
del MISMO conjunto del INS (gt2j-8ykr) con los 11 municipios de la provincia
Sabana Centro (data/raw/casos_covid_sabana_centro.csv) para comparar Chía con
sus municipios vecinos.
"""
from functools import lru_cache

import pandas as pd
import plotly.graph_objects as go
from flask import Blueprint, render_template, request

from datos import BASE_DIR, ETIQUETAS_EDAD, GRUPOS_EDAD, SEXO
from graficas import a_html

bp = Blueprint("territorial", __name__)

PREGUNTA = ("¿Cómo se distribuye la población y sus principales características "
            "entre los territorios disponibles?")

RUTA = BASE_DIR / "data" / "raw" / "casos_covid_sabana_centro.csv"
URL_EXTRACTO = (
    "https://www.datos.gov.co/resource/gt2j-8ykr.csv?%24where=departamento_nom%3D%27CUNDINAMARCA%27"
    "%20AND%20ciudad_municipio_nom%20in%28%27CHIA%27%2C%27ZIPAQUIRA%27%2C%27CAJICA%27%2C%27TOCANCIPA%27"
    "%2C%27COTA%27%2C%27SOPO%27%2C%27TABIO%27%2C%27COGUA%27%2C%27GACHANCIPA%27%2C%27TENJO%27%2C%27NEMOCON%27"
    "%29&%24limit=200000"
)

MUNICIPIOS = {
    "CHIA": "Chía", "ZIPAQUIRA": "Zipaquirá", "CAJICA": "Cajicá", "TOCANCIPA": "Tocancipá",
    "COTA": "Cota", "SOPO": "Sopó", "TABIO": "Tabio", "COGUA": "Cogua",
    "GACHANCIPA": "Gachancipá", "TENJO": "Tenjo", "NEMOCON": "Nemocón",
}

# Paleta de esta dimensión (validada: contraste, daltonismo y separación)
COLOR_BASE = "#008fa3"      # municipios
COLOR_CHIA = "#d0632a"      # Chía resaltado (población del proyecto)
COLORES_CONTAGIO = {"Comunitaria": "#008fa3", "Relacionado": "#d0632a", "Importado": "#8a5ea8"}
GRIS = "#6b7280"

VARIABLES = [
    ("ciudad_municipio_nom", "Municipio de notificación del caso (11 municipios de Sabana Centro).", "Categórica / territorial"),
    ("fecha_de_notificaci_n", "Fecha de notificación; se usa el año para el filtro.", "Temporal"),
    ("sexo", "Sexo de la persona (Femenino / Masculino).", "Categórica"),
    ("edad + unidad_medida", "Edad convertida a años y agrupada en rangos de 10 años.", "Numérica"),
    ("recuperado", "Desenlace del caso; se usa para contar fallecidos y calcular la letalidad.", "Categórica"),
    ("fuente_tipo_contagio", "Tipo de contagio: comunitario, relacionado (contacto conocido) o importado.", "Categórica"),
]


@lru_cache(maxsize=1)
def cargar_sabana_centro() -> pd.DataFrame:
    """Lee el extracto de Sabana Centro y lo deja con las mismas reglas de limpieza del proyecto."""
    cols = ["fecha_de_notificaci_n", "ciudad_municipio_nom", "edad", "unidad_medida",
            "sexo", "fuente_tipo_contagio", "recuperado"]
    df = pd.read_csv(RUTA, dtype=str, usecols=cols)

    df["municipio"] = df["ciudad_municipio_nom"].map(MUNICIPIOS)
    df["anio"] = pd.to_datetime(df["fecha_de_notificaci_n"], errors="coerce").dt.year.astype("Int64")
    df["sexo"] = df["sexo"].map(SEXO)
    edad = pd.to_numeric(df["edad"], errors="coerce")
    df["edad_anios"] = edad.where(df["unidad_medida"] == "1", 0).fillna(0).astype(int)
    df["grupo_edad"] = pd.cut(df["edad_anios"], bins=GRUPOS_EDAD, labels=ETIQUETAS_EDAD, right=False).astype(str)
    df["tipo_contagio"] = df["fuente_tipo_contagio"].str.strip().str.capitalize()
    df["fallecido"] = df["recuperado"].str.strip().str.lower().eq("fallecido")
    return df[["municipio", "anio", "sexo", "edad_anios", "grupo_edad", "tipo_contagio", "fallecido"]]


def resumen_por_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla base de la dimensión: una fila por municipio."""
    g = df.groupby("municipio").agg(
        casos=("fallecido", "size"),
        fallecidos=("fallecido", "sum"),
        edad_mediana=("edad_anios", "median"),
        mayores_60=("edad_anios", lambda s: (s >= 60).mean() * 100),
        relacionado=("tipo_contagio", lambda s: (s == "Relacionado").mean() * 100),
    )
    g["participacion"] = g["casos"] / g["casos"].sum() * 100
    g["letalidad"] = g["fallecidos"] / g["casos"] * 100
    return g.sort_values("casos", ascending=False)


def _colores(municipios) -> list:
    return [COLOR_CHIA if m == "Chía" else COLOR_BASE for m in municipios]


def grafica_casos(t: pd.DataFrame) -> str:
    d = t.sort_values("casos")
    fig = go.Figure(go.Bar(
        x=d["casos"], y=d.index, orientation="h", marker_color=_colores(d.index),
        text=[f"{c:,.0f}".replace(",", ".") + f"  ({p:.1f}%)" for c, p in zip(d["casos"], d["participacion"])],
        textposition="outside", cliponaxis=False,
        customdata=d[["participacion"]],
        hovertemplate="<b>%{y}</b><br>Casos: %{x:,}<br>Participación: %{customdata[0]:.1f}%<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Casos confirmados", yaxis_title=None, showlegend=False,
                      xaxis=dict(range=[0, d["casos"].max() * 1.3]))
    return a_html(fig)


def grafica_letalidad(t: pd.DataFrame, promedio: float) -> str:
    d = t.sort_values("letalidad")
    fig = go.Figure(go.Bar(
        x=d["letalidad"], y=d.index, orientation="h", marker_color=_colores(d.index),
        text=[f"{v:.2f}%" for v in d["letalidad"]], textposition="outside", cliponaxis=False,
        customdata=d[["fallecidos", "casos"]],
        hovertemplate="<b>%{y}</b><br>Letalidad: %{x:.2f}%<br>Fallecidos: %{customdata[0]:,} de %{customdata[1]:,} casos<extra></extra>",
    ))
    fig.add_vline(x=promedio, line_dash="dash", line_color=GRIS, line_width=1.5,
                  annotation_text=f"Sabana Centro: {promedio:.2f}%", annotation_position="top",
                  annotation_font_color=GRIS)
    fig.update_layout(xaxis_title="Letalidad (% de casos que fallecieron)", yaxis_title=None,
                      showlegend=False, xaxis=dict(range=[0, max(d["letalidad"].max() * 1.25, 0.5)]))
    return a_html(fig)


def grafica_contagio(df: pd.DataFrame) -> str:
    pct = pd.crosstab(df["municipio"], df["tipo_contagio"], normalize="index") * 100
    pct = pct.reindex(columns=[c for c in COLORES_CONTAGIO if c in pct.columns], fill_value=0)
    if "Relacionado" in pct.columns:
        pct = pct.sort_values("Relacionado")
    fig = go.Figure()
    for tipo in pct.columns:
        fig.add_bar(
            x=pct[tipo], y=pct.index, orientation="h", name=tipo,
            marker=dict(color=COLORES_CONTAGIO[tipo], line=dict(color="#ffffff", width=1.5)),
            text=[f"{v:.0f}%" if v >= 8 else "" for v in pct[tipo]], textposition="inside",
            insidetextfont=dict(color="#ffffff"),
            hovertemplate="<b>%{y}</b><br>" + tipo + ": %{x:.1f}%<extra></extra>",
        )
    fig.update_layout(barmode="stack", xaxis_title="% de casos del municipio", yaxis_title=None,
                      xaxis=dict(range=[0, 100], ticksuffix="%"))
    return a_html(fig)


def filtrar(df: pd.DataFrame, anio: str, sexo: str, edad: str) -> pd.DataFrame:
    if anio != "todos":
        df = df[df["anio"] == int(anio)]
    if sexo != "todos":
        df = df[df["sexo"] == sexo]
    if edad != "todos":
        df = df[df["grupo_edad"] == edad]
    return df


def conocimientos(df: pd.DataFrame) -> list:
    """Tres conocimientos evidentes calculados con TODOS los registros (sin filtros)."""
    t = resumen_por_municipio(df)
    top3 = t.head(3)
    pct_top3 = top3["participacion"].sum()
    prom = df["fallecido"].mean() * 100
    let = t.sort_values("letalidad", ascending=False)
    altos = let.head(3)
    bajo = let.tail(1)
    rel = t.sort_values("relacionado", ascending=False)
    fmt = lambda n: f"{n:,.0f}".replace(",", ".")

    return [
        {
            "pregunta": "¿Los casos se reparten de forma pareja entre los municipios de Sabana Centro?",
            "variables": "Municipio de notificación y cantidad de casos.",
            "procedimiento": "Se contaron los casos por municipio, se calculó la participación porcentual y se ordenaron de mayor a menor.",
            "evidencia": "Gráfica «Casos por municipio», indicador de concentración y tabla resumen.",
            "hallazgo": (f"{', '.join(top3.index)} concentran el {pct_top3:.1f}% de los "
                         f"{fmt(t['casos'].sum())} casos; Chía es el primero con {t.loc['Chía', 'participacion']:.1f}%, "
                         f"mientras {t.index[-1]} apenas aporta el {t['participacion'].iloc[-1]:.1f}%."),
            "interpretacion": "Los casos se concentran en los tres municipios más grandes y urbanos de la provincia; la distribución no es pareja.",
            "utilidad": "Orienta dónde ubicar la mayor capacidad de pruebas, vacunación y atención en futuros brotes.",
            "limitacion": "Son conteos absolutos: sin la población de cada municipio no puede afirmarse que Chía tenga mayor riesgo por habitante.",
        },
        {
            "pregunta": "¿La proporción de casos que terminaron en fallecimiento es igual en todos los municipios?",
            "variables": "Municipio, desenlace del caso (recuperado / fallecido) y edad.",
            "procedimiento": "Se calculó la letalidad (fallecidos ÷ casos × 100) por municipio y se comparó con el promedio de la provincia; se revisó además el % de casos de 60 años o más.",
            "evidencia": "Gráfica «Letalidad por municipio» con línea de referencia provincial y tabla resumen.",
            "hallazgo": (f"La letalidad va de {bajo['letalidad'].iloc[0]:.2f}% en {bajo.index[0]} a "
                         f"{altos['letalidad'].iloc[0]:.2f}% en {altos.index[0]} (promedio {prom:.2f}%). "
                         f"{', '.join(altos.index)} superan el promedio, y Zipaquirá registra más fallecidos "
                         f"({fmt(t.loc['Zipaquirá', 'fallecidos'])}) que Chía ({fmt(t.loc['Chía', 'fallecidos'])}) con menos casos."),
            "interpretacion": (f"Tener más casos no implica más letalidad. En Cogua pesa una población de casos más envejecida "
                               f"({t.loc['Cogua', 'mayores_60']:.1f}% con 60 años o más); en los municipios pequeños también "
                               "puede influir el acceso a atención hospitalaria."),
            "utilidad": "Sirve para priorizar seguimiento a adultos mayores y rutas de atención en los municipios con letalidad alta.",
            "limitacion": "En municipios pequeños pocos fallecidos cambian mucho el porcentaje; no se conocen comorbilidades ni el lugar de atención.",
        },
        {
            "pregunta": "¿Cambia la forma de contagio y el perfil de edad entre municipios?",
            "variables": "Municipio, tipo de contagio y edad.",
            "procedimiento": "Se calculó el porcentaje de cada tipo de contagio y la edad mediana por municipio.",
            "evidencia": "Gráfica «Tipo de contagio por municipio» y tabla resumen.",
            "hallazgo": (f"En {rel.index[0]} el {rel['relacionado'].iloc[0]:.1f}% de los casos fue por contacto conocido "
                         f"(relacionado), frente a {rel['relacionado'].iloc[-1]:.1f}% en {rel.index[-1]}. "
                         f"Tocancipá y Gachancipá tienen la edad mediana más baja "
                         f"({t.loc['Tocancipá', 'edad_mediana']:.0f} y {t.loc['Gachancipá', 'edad_mediana']:.0f} años)."),
            "interpretacion": "En Tocancipá y Sopó el rastreo identificó más cadenas de contagio y la población afectada es más joven, un comportamiento compatible con contagio en entornos laborales.",
            "utilidad": "Sugiere reforzar protocolos y rastreo en lugares de trabajo en esos municipios.",
            "limitacion": "El dataset no indica el lugar del contagio; la relación con el trabajo es una hipótesis, no una conclusión.",
        },
    ]


@bp.route("/dimension/territorial")
def tablero():
    completo = cargar_sabana_centro()
    anios = sorted(int(a) for a in completo["anio"].dropna().unique())

    anio = request.args.get("anio", "todos")
    sexo = request.args.get("sexo", "todos")
    edad = request.args.get("edad", "todos")
    if anio != "todos" and (not anio.isdigit() or int(anio) not in anios):
        anio = "todos"
    if sexo not in ("todos", *SEXO.values()):
        sexo = "todos"
    if edad not in ("todos", *ETIQUETAS_EDAD):
        edad = "todos"

    df = filtrar(completo, anio, sexo, edad)
    hay_datos = len(df) > 0
    contexto = dict(
        pregunta=PREGUNTA, variables=VARIABLES, url_extracto=URL_EXTRACTO,
        anios=anios, sexos=list(SEXO.values()), edades=ETIQUETAS_EDAD,
        filtros=dict(anio=anio, sexo=sexo, edad=edad), hay_datos=hay_datos,
        conocimientos=conocimientos(completo), total_provincia=len(completo),
    )
    if hay_datos:
        t = resumen_por_municipio(df)
        promedio = df["fallecido"].mean() * 100
        mayor_let = t.sort_values("letalidad", ascending=False).iloc[0]
        contexto.update(
            casos=len(df),
            participacion_chia=t.loc["Chía", "participacion"] if "Chía" in t.index else 0,
            top3=t.head(3)["participacion"].sum(),
            top3_nombres=", ".join(t.head(3).index),
            mayor_letalidad=dict(municipio=t.sort_values("letalidad", ascending=False).index[0],
                                 valor=mayor_let["letalidad"]),
            promedio_letalidad=promedio,
            tabla=t.reset_index().to_dict("records"),
            g_casos=grafica_casos(t),
            g_letalidad=grafica_letalidad(t, promedio),
            g_contagio=grafica_contagio(df),
        )
    return render_template("territorial.html", **contexto)
