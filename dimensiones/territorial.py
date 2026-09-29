"""Dimensión territorial — Integrante 2.

Editar solo este archivo y templates/territorial.html.
"""
from flask import Blueprint, render_template

bp = Blueprint("territorial", __name__)

PREGUNTA = ("¿Cómo se distribuye la población y sus principales características "
            "entre los territorios disponibles?")


@bp.route("/dimension/territorial")
def tablero():
    return render_template("territorial.html", pregunta=PREGUNTA)
