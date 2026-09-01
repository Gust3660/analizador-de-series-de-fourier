"""Calculos de señales y series de Fourier, independientes de la interfaz."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

SignalFunction = Callable[[np.ndarray, float], np.ndarray]


def sine_signal(t: np.ndarray, period: float) -> np.ndarray:
    return np.sin(2 * np.pi * t / period)


def square_signal(t: np.ndarray, period: float) -> np.ndarray:
    return np.where(np.sin(2 * np.pi * t / period) >= 0, 1.0, -1.0)


def triangle_signal(t: np.ndarray, period: float) -> np.ndarray:
    return (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * t / period))


def sawtooth_signal(t: np.ndarray, period: float) -> np.ndarray:
    phase = t / period
    return 2 * (phase - np.floor(phase + 0.5))


SIGNALS: dict[str, tuple[str, SignalFunction]] = {
    "seno": ("Onda senoidal", sine_signal),
    "cuadrada": ("Onda cuadrada", square_signal),
    "triangular": ("Onda triangular", triangle_signal),
    "diente": ("Onda de diente de sierra", sawtooth_signal),
}


@dataclass(frozen=True)
class FourierAnalysis:
    """Resultados numericos necesarios para presentar un analisis."""

    a0: float
    a: np.ndarray
    b: np.ndarray
    harmonics: np.ndarray
    times: np.ndarray
    original: np.ndarray
    approximation: np.ndarray
    rmse: float


def _coefficients(values: np.ndarray, harmonics: int) -> tuple[float, np.ndarray, np.ndarray]:
    sample_count = values.size
    # La regla del punto medio reduce el sesgo en discontinuidades.
    angles = 2 * np.pi * (np.arange(sample_count) + 0.5) / sample_count
    a0 = 2 * float(np.mean(values))
    a = np.empty(harmonics, dtype=float)
    b = np.empty(harmonics, dtype=float)
    for n in range(1, harmonics + 1):
        a[n - 1] = (2 / sample_count) * np.dot(values, np.cos(n * angles))
        b[n - 1] = (2 / sample_count) * np.dot(values, np.sin(n * angles))
    return a0, a, b


def _reconstruct(
    times: np.ndarray, period: float, a0: float, a: np.ndarray, b: np.ndarray
) -> np.ndarray:
    result = np.full_like(times, a0 / 2, dtype=float)
    for n, (an, bn) in enumerate(zip(a, b), start=1):
        angle = 2 * np.pi * n * times / period
        result += an * np.cos(angle) + bn * np.sin(angle)
    return result


def analyze_signal(
    signal_name: str,
    period: float = 2 * np.pi,
    harmonics: int = 15,
    samples: int = 4096,
    plot_points: int = 2000,
) -> FourierAnalysis:
    """Calcula coeficientes, reconstruccion y error para una señal periodica."""
    if signal_name not in SIGNALS:
        raise ValueError(f"Señal desconocida: {signal_name}")
    if not np.isfinite(period) or period <= 0:
        raise ValueError("El periodo debe ser un numero positivo.")
    if harmonics < 1:
        raise ValueError("El numero de armonicos debe ser al menos 1.")
    if samples < 16 or harmonics >= samples // 2:
        raise ValueError("Las muestras deben ser >= 16 y armonicos < muestras / 2.")
    if plot_points < 2:
        raise ValueError("Se necesitan al menos dos puntos para dibujar la señal.")

    _, signal_fn = SIGNALS[signal_name]
    sample_times = (np.arange(samples) + 0.5) * period / samples
    sample_values = signal_fn(sample_times, period)
    a0, a, b = _coefficients(sample_values, harmonics)
    times = np.linspace(0, period, plot_points, endpoint=False)
    original = signal_fn(times, period)
    approximation = _reconstruct(times, period, a0, a, b)
    rmse = float(np.sqrt(np.mean((original - approximation) ** 2)))
    return FourierAnalysis(
        a0=a0,
        a=a,
        b=b,
        harmonics=np.arange(1, harmonics + 1),
        times=times,
        original=original,
        approximation=approximation,
        rmse=rmse,
    )
