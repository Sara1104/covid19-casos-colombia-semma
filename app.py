"""Aplicación Flask — Análisis de casos positivos de COVID-19 en Chía.

Ejecutar localmente:  python app.py   (ver README)
"""
from flask import Flask, render_template

from datos import resumen_general
from dimensiones import BLUEPRINTS

app = Flask(__name__)

for bp in BLUEPRINTS:
    app.register_blueprint(bp)

# Menú compartido por todas las páginas (endpoint, texto)
MENU_DIMENSIONES = [
    ("poblacional.tablero", "Dimensión poblacional"),
    ("territorial.tablero", "Dimensión territorial"),
    ("temporal.tablero", "Dimensión temporal"),
    ("multivariada.tablero", "Dimensión relacional y multivariada"),
]

PROYECTO = {
    "titulo": "COVID-19 en Chía",
    "subtitulo": "Minería para descubrimiento de conocimiento evidente",
    "grupo": "Grupo #4",
    "fuente": "Instituto Nacional de Salud (INS) — datos.gov.co",
    "url_datos": "https://www.datos.gov.co/d/gt2j-8ykr",
}


@app.context_processor
def variables_globales():
    return {"menu_dimensiones": MENU_DIMENSIONES, "proyecto": PROYECTO}


@app.route("/")
def inicio():
    return render_template("index.html", resumen=resumen_general())


@app.errorhandler(404)
def no_encontrada(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
