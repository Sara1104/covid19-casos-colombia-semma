# Análisis de casos positivos de COVID-19 en Chía

**Grupo #4**

Aplicación web desarrollada con Python, Flask y Bootstrap para el análisis
exploratorio de casos positivos de COVID-19 en Chía (Cundinamarca), aplicando
la metodología SEMMA.

## Conjunto de datos
- **Nombre:** Casos positivos de COVID-19 en Colombia
- **Tema:** Salud pública – COVID-19
- **Entidad que publica:** Instituto Nacional de Salud (INS), Bogotá D.C.
- **URL:** https://www.datos.gov.co/d/gt2j-8ykr
- **Población estudiada:** Personas con caso confirmado de COVID-19 en Chía
- **Registros:** 32.055 (dataset original filtrado por municipio: Chía)

## Integrantes
| N.º | Integrante | Responsabilidad | Dimensión |
|---|---|---|---|
| 1 | Sara Vargas Carreño| Administración del repositorio | Poblacional |
| 2 | Diego Armando Guzmán Garzón | Configuración de Flask | Territorial |
| 3 | Diego Nicolás Castellanos Martínez | Publicación de la aplicación | Temporal |
| 4 | Jennifer Andrea Espitia Porra | Informe técnico | Relacional y multivariada |

## Aplicación publicada
(URL; la completa el Integrante 3 cuando publique)

## Cómo ejecutar el proyecto localmente
Requisitos: Python 3.10 o superior y Git.

```bash
# 1. Clonar el repositorio
git clone https://github.com/Sara1104/covid19-casos-colombia-semma.git
cd covid19-casos-colombia-semma

# 2. Crear y activar un entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

Abrir http://127.0.0.1:5000 en el navegador.

### Estructura del proyecto
```
app.py                  Aplicación Flask: registra las dimensiones y la página de inicio
datos.py                Carga y limpieza común del dataset (usar cargar_datos())
graficas.py             Estilo común de las gráficas Plotly (usar a_html(fig))
dimensiones/
  poblacional.py        Integrante 1 — ruta /dimension/poblacional
  territorial.py        Integrante 2 — ruta /dimension/territorial
  temporal.py           Integrante 3 — ruta /dimension/temporal
  multivariada.py       Integrante 4 — ruta /dimension/multivariada
templates/
  base.html             Plantilla base con Bootstrap y menú de navegación
  _componentes.html     Macros: encabezado, indicador, gráfica, conocimiento
  index.html            Página de inicio
  <dimension>.html      Tablero de cada integrante
static/css/estilos.css  Identidad visual del proyecto
data/raw/               Dataset original (no se modifica)
```

### Cómo agregar tu tablero
Cada integrante edita **solo** `dimensiones/<su_dimension>.py` y `templates/<su_dimension>.html`,
así los pull requests no generan conflictos. En el `.py` se filtran los datos, se calculan los
indicadores y se crean las gráficas con Plotly:

```python
import plotly.express as px
from datos import cargar_datos
from graficas import a_html

df = cargar_datos()
fig = px.histogram(df, x="edad_anios", color="sexo")
grafica_html = a_html(fig)   # se envía a la plantilla
```

En la plantilla se usan los componentes compartidos:

```jinja
{% import "_componentes.html" as c %}
{{ c.indicador(valor, "Etiqueta", "bi-people") }}
{{ c.grafica("Título", grafica_html, "Interpretación...") }}
```

## Flujo de trabajo
Ver [CONTRIBUTING.md](CONTRIBUTING.md).