import pandas as pd

df = pd.read_csv("data/raw/casos_covid_chia.csv", low_memory=False)

# Nos referimos a las columnas por posición, para no depender de tildes
col_ubicacion = df.columns[11]
col_estado = df.columns[12]
col_recuperado = df.columns[15]
col_tipo_recuperacion = df.columns[20]
col_etnia = df.columns[21]

for col in [col_ubicacion, col_estado, col_recuperado, col_tipo_recuperacion]:
    df[col] = df[col].astype(str).str.strip().str.capitalize()

df[col_etnia] = df[col_etnia].map({1.0: "Indigena", 5.0: "Negro o afrocolombiano", 6.0: "Otros"})

for col in [col_ubicacion, col_estado, col_recuperado, col_tipo_recuperacion]:
    df[col] = df[col].replace("Nan", "Sin dato")

df.to_csv("data/processed/casos_covid_chia_limpio.csv", index=False, encoding="utf-8")

print("Estado:")
print(df[col_estado].value_counts(dropna=False))
print("\nUbicacion:")
print(df[col_ubicacion].value_counts(dropna=False))