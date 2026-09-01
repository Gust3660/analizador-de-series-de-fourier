"""Interfaz Streamlit del analizador de series de Fourier."""

from __future__ import annotations

import csv
import io

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from backend import SIGNALS, analyze_signal


st.set_page_config(page_title="Analizador de Fourier", page_icon="〰️", layout="wide")
st.title("Analizador de series de Fourier")
st.write(
    "Explora cómo una señal periódica se reconstruye como suma de armónicos. "
    "Ajusta los parámetros en la barra lateral para actualizar el análisis."
)

with st.sidebar:
    st.header("Parámetros")
    signal_name = st.selectbox(
        "Señal", options=list(SIGNALS), format_func=lambda key: SIGNALS[key][0], index=1
    )
    period = st.number_input("Periodo", min_value=0.01, value=float(2 * np.pi), step=0.1)
    harmonics = st.slider("Número de armónicos", min_value=1, max_value=100, value=15)
    samples = st.select_slider(
        "Muestras para el cálculo",
        options=[512, 1024, 2048, 4096, 8192, 16384],
        value=4096,
    )

try:
    result = analyze_signal(signal_name, period, harmonics, samples)
except ValueError as error:
    st.error(str(error))
    st.stop()

metric_col, info_col = st.columns([1, 3])
metric_col.metric("Error RMSE", f"{result.rmse:.6f}")
info_col.info(
    f"{SIGNALS[signal_name][0]} · periodo {period:g} · "
    f"{harmonics} armónicos · {samples:,} muestras"
)

graph_tab, coefficients_tab = st.tabs(["Gráfica", "Coeficientes"])
with graph_tab:
    fig, (signal_axis, spectrum_axis) = plt.subplots(
        2, 1, figsize=(11, 7), gridspec_kw={"height_ratios": [2, 1]}
    )
    signal_axis.plot(result.times, result.original, label="Señal original", linewidth=2)
    signal_axis.plot(
        result.times,
        result.approximation,
        label=f"Aproximación con {harmonics} armónicos",
        linewidth=1.6,
        linestyle="--",
    )
    signal_axis.set_title("Señal y aproximación")
    signal_axis.set_xlabel("Tiempo")
    signal_axis.set_ylabel("Amplitud")
    signal_axis.grid(True, alpha=0.3)
    signal_axis.legend()

    spectrum_axis.stem(result.harmonics, np.hypot(result.a, result.b), basefmt=" ")
    spectrum_axis.set_title("Magnitud de los armónicos")
    spectrum_axis.set_xlabel("Armónico n")
    spectrum_axis.set_ylabel("√(an² + bn²)")
    spectrum_axis.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with coefficients_tab:
    st.latex(r"f(t) = \frac{a_0}{2} + \sum_{n=1}^{N} [a_n\cos(n\omega t) + b_n\sin(n\omega t)]")
    st.write(f"`a0 = {result.a0:.6f}`")
    coefficient_rows = [
        {
            "Armónico n": int(n),
            "aₙ": float(an),
            "bₙ": float(bn),
            "Magnitud": float(np.hypot(an, bn)),
        }
        for n, an, bn in zip(result.harmonics, result.a, result.b)
    ]
    st.dataframe(coefficient_rows, use_container_width=True, hide_index=True)

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["armonico", "an", "bn", "magnitud"])
    writer.writerows(
        (int(n), f"{an:.10g}", f"{bn:.10g}", f"{np.hypot(an, bn):.10g}")
        for n, an, bn in zip(result.harmonics, result.a, result.b)
    )
    st.download_button(
        "Descargar coeficientes CSV",
        data=csv_buffer.getvalue(),
        file_name="coeficientes_fourier.csv",
        mime="text/csv",
    )

with st.expander("¿Cómo interpretar la aproximación?"):
    st.markdown(
        "Cada armónico agrega una oscilación de frecuencia múltiplo de la frecuencia "
        "fundamental. Al aumentar su cantidad, la aproximación suele mejorar. Cerca "
        "de saltos, como los de la onda cuadrada, pueden aparecer oscilaciones del "
        "fenómeno de Gibbs. El RMSE resume la diferencia entre las dos curvas."
    )
