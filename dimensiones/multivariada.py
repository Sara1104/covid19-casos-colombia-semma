"""Dimensión relacional y multivariada — Integrante 4 (Jennifer Andrea Espitia Porra).

Pregunta: ¿Qué diferencias o relaciones evidentes pueden identificarse al
analizar conjuntamente tres o más variables?
"""
import pandas as pd
import plotly.graph_objects as go
from flask import Blueprint, render_template, request

from datos import cargar_datos, ETIQUETAS_EDAD
from graficas import a_html, PALETA

bp = Blueprint("multivariada", __name__)

PREGUNTA = ("¿Qué diferencias o relaciones evidentes pueden identificarse al "
            "analizar conjuntamente tres o más variables?")

VARIABLES = [
    ("grupo_edad", "Edad agrupada en rangos de 10 años.", "Categórica (ordinal)"),
    ("edad_anios", "Edad en años; se usa para separar menores de 60 y personas de 60 o más.", "Numérica"),
    ("sexo", "Sexo de la persona (Femenino / Masculino).", "Categórica"),
    ("recuperado", "Desenlace del caso: recuperado, fallecido, activo o sin dato.", "Categórica"),
    ("tipo_contagio", "Origen del contagio: comunitario, relacionado o importado.", "Categórica"),
    ("anio", "Año de notificación del caso.", "Temporal"),
]


def preparar(df):
    """Agrega las columnas que usa esta dimensión."""
    df = df.copy()
    df["fallecido"] = df["recuperado"] == "Fallecido"
    df["mayor_60"] = df["edad_anios"] >= 60
    return df


def letalidad(serie):
    """Porcentaje de fallecidos dentro de un grupo."""
    return float(serie.mean() * 100) if len(serie) else 0.0


def combinaciones(df):
    """Cuenta los casos de cada combinación de 4 variables."""
    combos = (df.groupby(["grupo_edad", "sexo", "tipo_contagio", "recuperado"], observed=True)
                .size().sort_values(ascending=False).reset_index(name="casos"))
    combos["pct"] = combos["casos"] / len(df) * 100
    return combos


def indicadores(df):
    let_mayor = letalidad(df.loc[df["mayor_60"], "fallecido"])
    let_menor = letalidad(df.loc[~df["mayor_60"], "fallecido"])
    top = combinaciones(df).iloc[0]
    return {
        "casos": len(df),
        "fallecidos": int(df["fallecido"].sum()),
        "let_general": letalidad(df["fallecido"]),
        "let_mayor": let_mayor,
        "let_menor": let_menor,
        "razon": let_mayor / let_menor if let_menor > 0 else None,
        "combo_pct": float(top["pct"]),
        "combo_texto": f"{top['grupo_edad']} años · {top['sexo']} · {top['tipo_contagio']} · {top['recuperado']}",
    }


def grafica_calor(df):
    """Mapa de calor: letalidad según sexo y grupo de edad (3 variables)."""
    grupos = df.groupby(["sexo", "grupo_edad"], observed=False)["fallecido"]
    tasa = grupos.mean().mul(100).unstack("grupo_edad").reindex(columns=ETIQUETAS_EDAD)
    casos = grupos.size().unstack("grupo_edad").reindex(columns=ETIQUETAS_EDAD).fillna(0)
    fig = go.Figure(go.Heatmap(
        z=tasa.values,
        x=[str(c) for c in tasa.columns],
        y=list(tasa.index),
        customdata=casos.values,
        text=tasa.map(lambda v: "" if pd.isna(v) else f"{v:.1f}%").values,
        texttemplate="%{text}",
        colorscale=[[0, "#f1f5f9"], [1, PALETA[1]]],
        colorbar=dict(title="Letalidad %"),
        xgap=2, ygap=2,
        hovertemplate="<b>%{y} · %{x} años</b><br>Letalidad: %{z:.2f}%<br>Casos: %{customdata:,}<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Grupo de edad", yaxis_title=None)
    return a_html(fig)


def grafica_anio(df):
    """Barras agrupadas: letalidad por año, menores de 60 frente a 60 o más."""
    grupos = df.groupby(["anio", "mayor_60"])["fallecido"]
    tasa = grupos.mean().mul(100).unstack("mayor_60")
    casos = grupos.size().unstack("mayor_60")
    anios = [str(int(a)) for a in tasa.index]
    fig = go.Figure()
    for clave, nombre, color in [(False, "Menores de 60", PALETA[0]),
                                 (True, "60 años o más", PALETA[1])]:
        if clave in tasa.columns:
            fig.add_trace(go.Bar(
                x=anios, y=tasa[clave], name=nombre, marker_color=color,
                customdata=casos[clave],
                text=[f"{v:.1f}%" if pd.notna(v) else "" for v in tasa[clave]],
                textposition="outside",
                hovertemplate="<b>%{x} · " + nombre + "</b><br>Letalidad: %{y:.2f}%<br>Casos: %{customdata:,}<extra></extra>",
            ))
    fig.update_layout(barmode="group", xaxis_title="Año de notificación", yaxis_title="Letalidad (%)")
    return a_html(fig)


def grafica_combinaciones(df):
    """Top 10 de combinaciones de edad, sexo, tipo de contagio y desenlace."""
    top = combinaciones(df).head(10).iloc[::-1]
    etiquetas = (top["grupo_edad"].astype(str) + " · " + top["sexo"] + " · "
                 + top["tipo_contagio"] + " · " + top["recuperado"])
    fig = go.Figure(go.Bar(
        x=top["casos"], y=etiquetas, orientation="h", marker_color=PALETA[0],
        text=[f"{p:.1f}%" for p in top["pct"]], textposition="outside",
        hovertemplate="<b>%{y}</b><br>Casos: %{x:,}<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Casos", yaxis_title=None, showlegend=False)
    return a_html(fig)


def filtrar(df, anio, contagio):
    """Aplica los dos filtros interactivos."""
    if anio != "todos":
        df = df[df["anio"] == int(anio)]
    if contagio != "todos":
        df = df[df["tipo_contagio"] == contagio]
    return df


@bp.route("/dimension/multivariada")
def tablero():
    completo = preparar(cargar_datos())
    anios_validos = [str(int(a)) for a in sorted(completo["anio"].dropna().unique())]
    contagios_validos = sorted(completo["tipo_contagio"].dropna().unique())

    anio = request.args.get("anio", "todos")
    contagio = request.args.get("contagio", "todos")
    if anio not in ("todos", *anios_validos):
        anio = "todos"
    if contagio not in ("todos", *contagios_validos):
        contagio = "todos"

    df = filtrar(completo, anio, contagio)
    hay_datos = len(df) > 0
    contexto = dict(
        pregunta=PREGUNTA, variables=VARIABLES,
        anios=anios_validos, contagios=contagios_validos,
        filtros=dict(anio=anio, contagio=contagio), hay_datos=hay_datos,
    )
    if hay_datos:
        contexto.update(
            g_calor=grafica_calor(df),
            g_anio=grafica_anio(df),
            g_combos=grafica_combinaciones(df),
            **indicadores(df),
        )
    return render_template("multivariada.html", **contexto)