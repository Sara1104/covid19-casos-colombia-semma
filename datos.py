"""Carga y limpieza común del conjunto de datos.

Todas las dimensiones usan `cargar_datos()` para trabajar sobre la misma
versión limpia de los datos. El archivo original en data/raw no se modifica.
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RUTA_RAW = BASE_DIR / "data" / "raw" / "casos_covid_chia.csv"

COLUMNAS = {
    "fecha reporte web": "fecha_reporte",
    "ID de caso": "id_caso",
    "Fecha de notificación": "fecha_notificacion",
    "Código DIVIPOLA departamento": "cod_departamento",
    "Nombre departamento": "departamento",
    "Código DIVIPOLA municipio": "cod_municipio",
    "Nombre municipio": "municipio",
    "Edad": "edad",
    "Unidad de medida de edad": "unidad_edad",
    "Sexo": "sexo",
    "Tipo de contagio": "tipo_contagio",
    "Ubicación del caso": "ubicacion",
    "Estado": "estado",
    "Código ISO del país": "cod_pais",
    "Nombre del país": "pais",
    "Recuperado": "recuperado",
    "Fecha de inicio de síntomas": "fecha_sintomas",
    "Fecha de muerte": "fecha_muerte",
    "Fecha de diagnóstico": "fecha_diagnostico",
    "Fecha de recuperación": "fecha_recuperacion",
    "Tipo de recuperación": "tipo_recuperacion",
    "Pertenencia étnica": "pertenencia_etnica",
    "Nombre del grupo étnico": "grupo_etnico",
}

COLUMNAS_FECHA = [
    "fecha_reporte", "fecha_notificacion", "fecha_sintomas",
    "fecha_muerte", "fecha_diagnostico", "fecha_recuperacion",
]

# Códigos del diccionario de datos del INS
PERTENENCIA_ETNICA = {
    "1": "Indígena", "2": "ROM", "3": "Raizal",
    "4": "Palenquero", "5": "Negro", "6": "Otro",
}
SEXO = {"F": "Femenino", "M": "Masculino"}

GRUPOS_EDAD = [0, 10, 20, 30, 40, 50, 60, 70, 80, 200]
ETIQUETAS_EDAD = ["0-9", "10-19", "20-29", "30-39", "40-49",
                  "50-59", "60-69", "70-79", "80+"]


def _texto(serie: pd.Series) -> pd.Series:
    """Unifica mayúsculas/minúsculas ('casa' y 'Casa' -> 'Casa')."""
    return serie.str.strip().str.capitalize()


@lru_cache(maxsize=1)
def cargar_datos() -> pd.DataFrame:
    """Lee el CSV original y devuelve un DataFrame limpio (se lee una sola vez)."""
    df = pd.read_csv(RUTA_RAW, dtype=str).rename(columns=COLUMNAS)

    for col in COLUMNAS_FECHA:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["ubicacion", "estado", "recuperado", "tipo_recuperacion", "tipo_contagio"]:
        df[col] = _texto(df[col])
    df[["ubicacion", "estado", "recuperado"]] = df[["ubicacion", "estado", "recuperado"]].fillna("Sin dato")

    df["sexo"] = df["sexo"].map(SEXO)
    df["pertenencia_etnica"] = df["pertenencia_etnica"].map(PERTENENCIA_ETNICA).fillna("Sin dato")

    # Edad en años: unidad 1 = años, 2 = meses, 3 = días
    edad = pd.to_numeric(df["edad"], errors="coerce")
    unidad = df["unidad_edad"].astype(str)
    df["edad_anios"] = edad.where(unidad == "1", 0).astype(int)
    df["grupo_edad"] = pd.cut(df["edad_anios"], bins=GRUPOS_EDAD, labels=ETIQUETAS_EDAD, right=False)

    df["anio"] = df["fecha_notificacion"].dt.year
    df["mes"] = df["fecha_notificacion"].dt.to_period("M").astype(str)
    return df


def resumen_general() -> dict:
    """Cifras generales para la página de inicio."""
    df = cargar_datos()
    return {
        "registros": len(df),
        "variables": len(COLUMNAS),
        "fecha_min": df["fecha_notificacion"].min().strftime("%d/%m/%Y"),
        "fecha_max": df["fecha_notificacion"].max().strftime("%d/%m/%Y"),
        "fallecidos": int((df["recuperado"] == "Fallecido").sum()),
        "edad_promedio": round(float(df["edad_anios"].mean()), 1),
    }
