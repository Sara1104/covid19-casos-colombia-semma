"""Dimensión poblacional — Integrante 1.

Editar solo este archivo y templates/poblacional.html.
"""
from flask import Blueprint, render_template

bp = Blueprint("poblacional", __name__)

PREGUNTA = ("¿Cómo está compuesta y distribuida la población analizada "
            "según sus principales características?")


@bp.route("/dimension/poblacional")
def tablero():
    return render_template("poblacional.html", pregunta=PREGUNTA)
