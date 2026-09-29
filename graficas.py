"""Utilidades compartidas para las gráficas de los tableros.

Usar `estilo(fig)` y `a_html(fig)` en todas las dimensiones para mantener
la misma identidad visual.
"""
import plotly.graph_objects as go

PALETA = ["#0f6e7c", "#e07a3f", "#5b8c5a", "#8a5ea8", "#c9a227",
          "#3f7cc9", "#b5485d", "#6b7280", "#2a9d8f"]
COLOR_PRINCIPAL = PALETA[0]


def estilo(fig: go.Figure, alto: int = 380) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        colorway=PALETA,
        height=alto,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(family="Inter, system-ui, sans-serif", size=13, color="#1f2937"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(font_size=13),
    )
    return fig


def a_html(fig: go.Figure) -> str:
    """Convierte la figura en un fragmento HTML (Plotly.js se carga en base.html)."""
    return estilo(fig).to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"displaylogo": False, "responsive": True},
    )
