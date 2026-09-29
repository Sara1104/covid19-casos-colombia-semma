"""Registro de las cuatro dimensiones (un blueprint por integrante)."""
from .poblacional import bp as bp_poblacional
from .territorial import bp as bp_territorial
from .temporal import bp as bp_temporal
from .multivariada import bp as bp_multivariada

BLUEPRINTS = [bp_poblacional, bp_territorial, bp_temporal, bp_multivariada]
