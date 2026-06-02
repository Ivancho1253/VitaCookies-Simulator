from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = {
    "Optimista": {
        "arrival_factor": 0.85,
        "form_factor": 0.85,
        "server_factor": 1.20,
    },
    "Esperado": {
        "arrival_factor": 1.00,
        "form_factor": 1.00,
        "server_factor": 1.00,
    },
    "Pesimista": {
        "arrival_factor": 1.30,
        "form_factor": 1.25,
        "server_factor": 0.80,
    },
}


@dataclass(frozen=True)
class QueueInputs:
    arrival_rate_per_hour: float
    event_duration_min: int
    server_capacity: int
    avg_form_time_min: float
    scenario: str = "Esperado"
    seed: int = 42


def _positive(value: float, fallback: float) -> float:
    return float(value) if value and value > 0 else float(fallback)


def simulate_queue(inputs: QueueInputs) -> dict:
    """Simulates simultaneous digital form submissions during the event."""
    rng = np.random.default_rng(inputs.seed)
    scenario = SCENARIOS.get(inputs.scenario, SCENARIOS["Esperado"])

    event_duration = max(int(inputs.event_duration_min), 1)
    arrival_rate = _positive(inputs.arrival_rate_per_hour, 1) * scenario["arrival_factor"]
    base_server_capacity = max(int(inputs.server_capacity), 1)
    server_capacity = max(int(round(base_server_capacity * scenario["server_factor"])), 1)
    avg_form_time = _positive(inputs.avg_form_time_min, 0.5) * scenario["form_factor"]

    expected_submissions = max(arrival_rate * event_duration / 60, 1)
    total_submissions = max(int(rng.poisson(expected_submissions)), 1)

    interarrival = rng.exponential(60 / arrival_rate, size=total_submissions * 3)
    submission_start = np.cumsum(interarrival)
    submission_start = submission_start[submission_start <= event_duration]
    if len(submission_start) == 0:
        submission_start = np.array([rng.uniform(0, event_duration)])

    n_submissions = len(submission_start)
    form_times = rng.lognormal(mean=np.log(avg_form_time), sigma=0.35, size=n_submissions)
    form_times = np.clip(form_times, 0.15, avg_form_time * 4)
    submission_end = submission_start + form_times

    timeline_end = max(event_duration, float(submission_end.max())) + 1
    timeline = np.arange(0, np.ceil(timeline_end) + 1, 1)
    active_forms = np.array(
        [np.sum((submission_start <= minute) & (submission_end > minute)) for minute in timeline]
    )
    arrivals_per_minute = np.array(
        [np.sum((submission_start >= minute) & (submission_start < minute + 1)) for minute in timeline]
    )

    saturated = active_forms > server_capacity
    peak_form_load = int(active_forms.max())
    peak_form_minute = float(timeline[int(np.argmax(active_forms))])
    saturated_minutes = int(np.sum(saturated))
    saturation_ratio = float(saturated_minutes / max(len(timeline), 1) * 100)
    load_ratio = float(peak_form_load / server_capacity)

    if peak_form_load <= server_capacity:
        status = "Sin saturacion digital"
        recommendation = (
            "La capacidad estimada alcanza para los envios simultaneos. Mantener el enlace visible "
            "y asistencia breve para quienes tengan problemas al completar el formulario."
        )
    elif load_ratio <= 1.25:
        status = "Riesgo moderado de saturacion"
        recommendation = (
            "Conviene pedir que los comensales envien el formulario en tandas o al finalizar cada bloque "
            "de degustacion, para evitar un pico concentrado."
        )
    else:
        status = "Alto riesgo de saturacion"
        recommendation = (
            "La capacidad digital queda corta para el pico estimado. Se recomienda escalonar los envios, "
            "tener un formulario alternativo de respaldo y evitar que todos carguen al mismo tiempo."
        )

    submissions = pd.DataFrame(
        {
            "persona": np.arange(1, n_submissions + 1),
            "inicio_envio_min": submission_start,
            "fin_envio_min": submission_end,
            "tiempo_carga_formulario_min": form_times,
        }
    )

    timeline_df = pd.DataFrame(
        {
            "minuto": timeline,
            "nuevos_envios": arrivals_per_minute,
            "envios_formulario_activos": active_forms,
            "capacidad_formulario": server_capacity,
            "saturado": saturated,
        }
    )

    metrics = {
        "personas_simuladas": n_submissions,
        "pico_carga_formulario": peak_form_load,
        "pico_carga_min": peak_form_minute,
        "capacidad_formulario_ajustada": server_capacity,
        "minutos_saturados_formulario": saturated_minutes,
        "porcentaje_tiempo_saturado": saturation_ratio,
        "tiempo_carga_promedio_min": float(form_times.mean()),
        "tiempo_carga_maximo_min": float(form_times.max()),
        "estado_general": status,
        "recomendacion": recommendation,
    }

    return {"metrics": metrics, "people": submissions, "timeline": timeline_df}


def simulate_queue_scenarios(inputs: QueueInputs) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        scenario_inputs = QueueInputs(**{**inputs.__dict__, "scenario": scenario})
        result = simulate_queue(scenario_inputs)
        metrics = result["metrics"]
        rows.append(
            {
                "escenario": scenario,
                "personas": metrics["personas_simuladas"],
                "pico_formulario": metrics["pico_carga_formulario"],
                "capacidad": metrics["capacidad_formulario_ajustada"],
                "minutos_saturados": metrics["minutos_saturados_formulario"],
                "tiempo_saturado_pct": metrics["porcentaje_tiempo_saturado"],
            }
        )
    return pd.DataFrame(rows)

