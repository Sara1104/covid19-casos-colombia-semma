"""Dimensión poblacional — Integrante 1 (Sara Vargas Carreño).

Pregunta: ¿Cómo está compuesta y distribuida la población analizada según
sus principales características?
"""
import plotly.graph_objects as go
from flask import Blueprint, render_template, request

from datos import cargar_datos, SEXO
from graficas import a_html, PALETA

bp = Blueprint("poblacional", __name__)

PREGUNTA = ("¿Cómo está compuesta y distribuida la población analizada según "
            "sus principales características?")

VARIABLES = [
    ("sexo", "Sexo de la persona (Femenino / Masculino).", "Categórica"),
    ("estado", "Gravedad del caso (leve, grave, fallecido, sin dato).", "Categórica"),
    ("tipo_contagio", "Origen del contagio: comunitario, relacionado o importado.", "Categórica"),
    ("edad_anios", "Edad en años (bebés en meses o días quedan en 0).", "Numérica"),
    ("pertenencia_etnica", "Grupo étnico reportado, según el diccionario del INS.", "Categórica"),
]

COLOR_F = PALETA[1]
COLOR_M = PALETA[0]
COLORES_ESTADO = {"Leve": PALETA[0], "Fallecido": PALETA[1], "Grave": PALETA[3], "Sin dato": PALETA[7]}


def filtrar(df, sexo, contagio):
    if sexo != "todos":
        df = df[df["sexo"] == sexo]
    if contagio != "todos":
        df = df[df["tipo_contagio"] == contagio]
    return df


def grafica_sexo(df):
    conteo = df["sexo"].value_counts()
    total = conteo.sum()
    fig = go.Figure(go.Bar(
        x=conteo.index, y=conteo.values,
        marker_color=[COLOR_F if s == "Femenino" else COLOR_M for s in conteo.index],
        text=[f"{v:,.0f}".replace(",", ".") + f" ({v/total*100:.1f}%)" for v in conteo.values],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Casos: %{y:,}<extra></extra>",
    ))
    fig.update_layout(xaxis_title=None, yaxis_title="Casos", showlegend=False)
    return a_html(fig)


def grafica_estado(df):
    conteo = df["estado"].value_counts()
    conteo = conteo.reindex([c for c in COLORES_ESTADO if c in conteo.index]).dropna()
    fig = go.Figure(go.Pie(
        labels=conteo.index, values=conteo.values,
        marker=dict(colors=[COLORES_ESTADO[c] for c in conteo.index]),
        hovertemplate="<b>%{label}</b><br>Casos: %{value:,}<br>%{percent}<extra></extra>",
    ))
    return a_html(fig)


def grafica_edad(df):
    fig = go.Figure(go.Histogram(
        x=df["edad_anios"], nbinsx=20, marker_color=COLOR_M,
        hovertemplate="Edad: %{x}<br>Casos: %{y}<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Edad (años)", yaxis_title="Casos", showlegend=False)
    return a_html(fig)


def conocimientos(df):
    total = len(df)
    fmt = lambda n: f"{n:,.0f}".replace(",", ".")
    sexo_pct = df["sexo"].value_counts(normalize=True) * 100
    estado_pct = df["estado"].value_counts(normalize=True) * 100
    contagio_pct = df["tipo_contagio"].value_counts(normalize=True) * 100

    return [
        {
            "pregunta": "¿Hay más hombres o mujeres entre los casos confirmados?",
            "variables": "Sexo.",
            "procedimiento": "Se contaron los casos por sexo y se calculó el porcentaje de cada uno sobre el total.",
            "evidencia": "Gráfica «Casos por sexo».",
            "hallazgo": (f"De los {fmt(total)} casos, {sexo_pct.get('Femenino', 0):.1f}% corresponden a mujeres "
                         f"y {sexo_pct.get('Masculino', 0):.1f}% a hombres."),
            "interpretacion": "La diferencia entre sexos es moderada; las mujeres son ligeramente mayoría entre los casos confirmados en Chía.",
            "utilidad": "Sirve de línea base para campañas de salud que necesiten dirigirse a la población general sin sesgo de sexo.",
            "limitacion": "El dato refleja quién se hizo la prueba y fue confirmado, no necesariamente quién se expuso más al virus.",
        },
        {
            "pregunta": "¿Qué tan graves fueron los casos confirmados en Chía?",
            "variables": "Estado del caso.",
            "procedimiento": "Se agruparon los casos por estado (leve, grave, fallecido, sin dato) y se calculó su participación porcentual.",
            "evidencia": "Gráfica circular «Casos por estado».",
            "hallazgo": (f"El {estado_pct.get('Leve', 0):.1f}% de los casos fueron leves y el "
                         f"{estado_pct.get('Fallecido', 0):.1f}% terminó en fallecimiento; solo 1 caso quedó registrado como grave."),
            "interpretacion": "La inmensa mayoría de los casos confirmados tuvo evolución leve, coherente con el perfil de edad relativamente joven del municipio.",
            "utilidad": "Respalda decisiones sobre cuánta capacidad de atención de baja y alta complejidad se necesita ante un rebrote similar.",
            "limitacion": "163 registros no tienen estado reportado (0,5%), y la categoría «grave» casi no se usó, lo que sugiere que algunos casos graves pudieron quedar registrados solo como leves o fallecidos.",
        },
        {
            "pregunta": "¿Cómo se originó la mayoría de los contagios?",
            "variables": "Tipo de contagio.",
            "procedimiento": "Se calculó el porcentaje de casos por tipo de contagio (comunitario, relacionado, importado).",
            "evidencia": "Indicador y gráfica de tipo de contagio.",
            "hallazgo": (f"El {contagio_pct.get('Comunitaria', 0):.1f}% de los casos fue de origen comunitario (sin fuente identificada), "
                         f"frente a {contagio_pct.get('Relacionado', 0):.1f}% relacionado y apenas "
                         f"{contagio_pct.get('Importado', 0):.2f}% importado."),
            "interpretacion": "El predominio del contagio comunitario indica que, en buena parte del período, el virus ya circulaba de forma generalizada y no era posible rastrear cada cadena de contagio.",
            "utilidad": "Justifica priorizar medidas de prevención generalizadas sobre el rastreo de contactos en los picos de contagio comunitario.",
            "limitacion": "La clasificación depende de la capacidad de rastreo del momento; más «comunitario» puede reflejar menos rastreo, no solo más circulación del virus.",
        },
    ]


@bp.route("/dimension/poblacional")
def tablero():
    completo = cargar_datos()
    contagios_validos = sorted(completo["tipo_contagio"].dropna().unique())

    sexo = request.args.get("sexo", "todos")
    contagio = request.args.get("contagio", "todos")
    if sexo not in ("todos", *SEXO.values()):
        sexo = "todos"
    if contagio not in ("todos", *contagios_validos):
        contagio = "todos"

    df = filtrar(completo, sexo, contagio)
    hay_datos = len(df) > 0
    contexto = dict(
        pregunta=PREGUNTA, variables=VARIABLES,
        sexos=list(SEXO.values()), contagios=contagios_validos,
        filtros=dict(sexo=sexo, contagio=contagio), hay_datos=hay_datos,
        conocimientos=conocimientos(completo),
    )
    if hay_datos:
        contexto.update(
            casos=len(df),
            pct_mujeres=(df["sexo"] == "Femenino").mean() * 100,
            pct_leve=(df["estado"] == "Leve").mean() * 100,
            edad_mediana=df["edad_anios"].median(),
            g_sexo=grafica_sexo(df),
            g_estado=grafica_estado(df),
            g_edad=grafica_edad(df),
        )
    return render_template("poblacional.html", **contexto)