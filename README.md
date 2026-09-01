# Analizador de series de Fourier

Aplicación web interactiva hecha con Streamlit para explorar cómo señales periódicas se pueden aproximar mediante una serie de Fourier. La interfaz permite elegir la señal y sus parámetros, comparar la forma original con la reconstrucción, consultar los coeficientes y descargarlos como CSV.

## Funciones

- Señales disponibles: seno, cuadrada, triangular y diente de sierra.
- Cálculo numérico de `a0`, `an` y `bn`.
- Gráfica de la señal original, su aproximación y la magnitud de sus armónicos.
- Métrica RMSE para estimar el error de la aproximación.
- Tabla de coeficientes con opción de descarga CSV.
- Controles interactivos para periodo, cantidad de armónicos y muestras.

## Estructura

```text
.
├── backend.py       # Generación de señales y cálculos de Fourier
├── frontend.py      # Interfaz Streamlit
├── requirements.txt
└── README.md
```

El backend contiene los cálculos y no depende de Streamlit. El frontend se encarga de presentar los controles, gráficas y resultados.

## Requisitos

- Python 3.10 o posterior
- Dependencias indicadas en `requirements.txt`

## Instalación y ejecución

Abre una terminal en la carpeta del proyecto y crea un entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En macOS o Linux, activa el entorno con:

```bash
source .venv/bin/activate
```

Inicia la aplicación desde la carpeta raíz del proyecto:

```bash
python -m streamlit run frontend.py
```

Streamlit abrirá la aplicación en el navegador. Detén el servidor con `Ctrl+C` en la terminal.

## Uso

1. Elige una señal en la barra lateral.
2. Ajusta el periodo, el número de armónicos y las muestras para el cálculo.
3. En **Gráfica**, compara la señal original y su reconstrucción y observa el espectro.
4. En **Coeficientes**, consulta `a0`, `an`, `bn` y descarga la tabla como CSV.

La serie usada es:

```text
f(t) = a0/2 + Σ [an cos(n·ω·t) + bn sin(n·ω·t)]
ω = 2π / periodo
```

En señales con discontinuidades pueden aparecer oscilaciones cerca de los saltos, conocidas como fenómeno de Gibbs.
