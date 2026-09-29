"""Dimensión temporal — Integrante 3.

Editar solo este archivo y templates/temporal.html.
"""
from flask import Blueprint, render_template

bp = Blueprint("temporal", __name__)

PREGUNTA = ("¿Cómo ha cambiado el comportamiento de la población durante "
            "el periodo disponible?")


@bp.route("/dimension/temporal")
def tablero():
    return render_template("temporal.html", pregunta=PREGUNTA)
