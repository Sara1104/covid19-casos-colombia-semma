import pandas as pd

df = pd.read_csv("data/raw/casos_covid_chia.csv", low_memory=False)

columnas = ["Nombre departamento", "Nombre municipio", "Sexo", "Estado",
            "Tipo de contagio", "Ubicación del caso", "Unidad de medida de edad",
            "Recuperado", "Tipo de recuperación", "Pertenencia étnica"]

for col in columnas:
    print("\n=== " + col + " ===")
    print(df[col].value_counts(dropna=False))