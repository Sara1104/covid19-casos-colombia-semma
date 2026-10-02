import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath('.'))
from datos import cargar_datos

df = cargar_datos()
print("Total rows:", len(df))
print("fecha_notificacion range:", df['fecha_notificacion'].min(), "to", df['fecha_notificacion'].max())

# Casos por año
print("\nCasos por año:")
print(df['anio'].value_counts().sort_index())

# Casos por mes
print("\nCasos por mes (head 10):")
print(df['mes'].value_counts().sort_index().head(10))

# Agrupar por mes para ver picos
meses = df.groupby('mes').size()
print("\nMes con más casos:", meses.idxmax(), "con", meses.max())
print("Mes con menos casos:", meses.idxmin(), "con", meses.min())

