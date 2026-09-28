# Guía de contribución

## Ramas
Cada integrante trabaja solo en su rama:
- `feature/dimension-poblacional` (Integrante 1)
- `feature/dimension-territorial` (Integrante 2)
- `feature/dimension-temporal` (Integrante 3)
- `feature/dimension-multivariada` (Integrante 4)

## Flujo obligatorio
1. Actualizar `main`: `git checkout main` y `git pull origin main`
2. Crear la rama asignada: `git checkout -b feature/dimension-...`
3. Desarrollar el tablero de la dimensión
4. Hacer commits descriptivos (mínimo 3 relacionados con la dimensión)
5. Subir la rama: `git push -u origin feature/dimension-...`
6. Crear un pull request hacia `main`
7. Solicitar revisión de la Integrante 1
8. Aplicar las correcciones pedidas
9. Obtener la aprobación
10. Fusionar el pull request

## Reglas
- No se hacen commits directos a `main`.
- Cada integrante modifica solo los archivos de su dimensión, para evitar conflictos.
- Los mensajes de commit siguen el formato `tipo: descripción` (por ejemplo `feat: agrega indicadores`, `fix: corrige filtro`, `docs: actualiza README`).
- Los pull requests se fusionan con "Create a merge commit", no con squash.
- Las gráficas se generan desde el dataset; no se aceptan imágenes de terceros.
- Antes de pedir revisión, la aplicación debe ejecutarse sin errores en local.

## Dataset
El archivo `data/raw/casos_covid_chia.csv` no se modifica. Los datos limpios van en `data/processed/`.