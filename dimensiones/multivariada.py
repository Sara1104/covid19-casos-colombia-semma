"""Dimensión relacional y multivariada — Integrante 4.

Editar solo este archivo y templates/multivariada.html.
"""
from flask import Blueprint, render_template

bp = Blueprint("multivariada", __name__)

PREGUNTA = ("¿Qué diferencias o relaciones evidentes pueden identificarse al "
            "analizar conjuntamente tres o más variables?")


@bp.route("/dimension/multivariada")
def tablero():
    return render_template("multivariada.html", pregunta=PREGUNTA)
