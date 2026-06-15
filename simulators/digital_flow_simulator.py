from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = {
    "Optimista": {"arrival": 0.85, "tasting": 0.90, "form": 0.85, "capacity": 1.20},
    "Esperado": {"arrival": 1.00, "tasting": 1.00, "form": 1.00, "capacity": 1.00},
    "Pesimista": {"arrival": 1.30, "tasting": 1.15, "form": 1.25, "capacity": 0.80},
}


@dataclass(frozen=True)
class DigitalFlowInputs:
    arrival_rate_per_hour: float
    event_duration_min: int
    avg_tasting_time_min: float
    avg_form_completion_min: float
    server_capacity: int
    runs: int
    scenario: str = "Esperado"
    seed: int = 42


def _positive(value: float, fallback: float) -> float:
    return float(value) if value and value > 0 else float(fallback)


def _timeline_arrays(
    duration: int,
    form_start: np.ndarray,
    form_end: np.ndarray,
    capacity: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    timeline_end = max(duration, float(form_end.max())) + 1
    timeline = np.arange(0, np.ceil(timeline_end) + 1, 1)
    starts = np.sort(form_start)
    ends = np.sort(form_end)

    active = np.searchsorted(starts, timeline, side="right") - np.searchsorted(ends, timeline, side="right")
    new_submissions = np.searchsorted(starts, timeline + 1, side="left") - np.searchsorted(starts, timeline, side="left")
    utilization = active / capacity
    saturated = active > capacity
    return timeline, active, new_submissions, utilization, saturated


def _single_run(
    inputs: DigitalFlowInputs,
    rng: np.random.Generator,
    scenario_name: str,
    include_frames: bool = True,
) -> tuple[dict, pd.DataFrame | None, pd.DataFrame | None]:
    scenario = SCENARIOS[scenario_name]
    duration = max(int(inputs.event_duration_min), 1)
    arrival_rate = _positive(inputs.arrival_rate_per_hour, 1) * scenario["arrival"]
    tasting_mean = _positive(inputs.avg_tasting_time_min, 0.5) * scenario["tasting"]
    form_mean = _positive(inputs.avg_form_completion_min, 0.5) * scenario["form"]
    capacity = max(int(round(max(inputs.server_capacity, 1) * scenario["capacity"])), 1)

    expected_people = max(arrival_rate * duration / 60, 1)
    candidate_count = max(int(rng.poisson(expected_people * 1.2)), 1)
    interarrival = rng.exponential(60 / arrival_rate, size=candidate_count * 3)
    arrivals = np.cumsum(interarrival)
    arrivals = arrivals[arrivals <= duration]
    if len(arrivals) == 0:
        arrivals = np.array([rng.uniform(0, duration)])

    n = len(arrivals)
    tasting = np.clip(rng.lognormal(np.log(tasting_mean), 0.25, n), 0.20, tasting_mean * 4)
    form = np.clip(rng.lognormal(np.log(form_mean), 0.35, n), 0.20, form_mean * 5)
    form_start = arrivals + tasting
    form_end = form_start + form

    timeline, active, new_submissions, utilization, saturated = _timeline_arrays(duration, form_start, form_end, capacity)

    peak = int(active.max())
    peak_minute = float(timeline[int(np.argmax(active))])
    saturated_minutes = int(saturated.sum())
    saturated_pct = float(saturated_minutes / max(len(timeline), 1) * 100)
    saturation = bool(peak > capacity)

    if saturation and peak / capacity > 1.30:
        status = "Alto riesgo de saturacion"
        decision = "Escalonar envios y preparar formulario alternativo de respaldo."
    elif saturation:
        status = "Riesgo moderado de saturacion"
        decision = "Organizar envios en tandas y evitar que todos respondan al mismo tiempo."
    else:
        status = "Sin saturacion relevante"
        decision = "Mantener el esquema previsto y asistencia para completar el formulario."

    metrics = {
        "personas_simuladas": n,
        "pico_carga": peak,
        "minuto_pico": peak_minute,
        "capacidad_ajustada": capacity,
        "minutos_saturados": saturated_minutes,
        "porcentaje_tiempo_saturado": saturated_pct,
        "utilizacion_maxima_pct": float(utilization.max() * 100),
        "utilizacion_promedio_pct": float(utilization.mean() * 100),
        "probabilidad_saturacion_run": 100.0 if saturation else 0.0,
        "tiempo_formulario_promedio": float(form.mean()),
        "estado": status,
        "resultado": f"Pico de {peak} formularios simultaneos frente a capacidad {capacity}.",
        "interpretacion": "La saturacion aparece cuando la concurrencia supera la capacidad estimada del formulario.",
        "recomendacion": decision,
        "decision": decision,
    }

    if not include_frames:
        return metrics, None, None

    people = pd.DataFrame(
        {
            "persona": np.arange(1, n + 1),
            "llegada_min": arrivals,
            "fin_degustacion_min": form_start,
            "fin_formulario_min": form_end,
            "tiempo_degustacion_min": tasting,
            "tiempo_formulario_min": form,
        }
    )
    timeline_df = pd.DataFrame(
        {
            "minuto": timeline,
            "nuevos_envios": new_submissions,
            "formularios_activos": active,
            "capacidad": capacity,
            "utilizacion_pct": utilization * 100,
            "saturado": saturated,
        }
    )
    return metrics, people, timeline_df


def simulate_digital_flow(inputs: DigitalFlowInputs, include_frames: bool = True) -> dict:
    runs = max(int(inputs.runs), 100)
    rng = np.random.default_rng(inputs.seed)
    scenario_name = inputs.scenario if inputs.scenario in SCENARIOS else "Esperado"

    first_metrics, people, timeline = _single_run(inputs, rng, scenario_name, include_frames=include_frames)
    run_rows = [first_metrics]
    for _ in range(runs - 1):
        metrics, _, _ = _single_run(inputs, rng, scenario_name, include_frames=False)
        run_rows.append(metrics)

    run_df = pd.DataFrame(run_rows)
    prob_sat = float((run_df["minutos_saturados"] > 0).mean() * 100)
    first_metrics["probabilidad_saturacion_pct"] = prob_sat
    first_metrics["personas_promedio"] = float(run_df["personas_simuladas"].mean())
    first_metrics["pico_promedio"] = float(run_df["pico_carga"].mean())
    first_metrics["pico_p50"] = float(np.percentile(run_df["pico_carga"], 50))
    first_metrics["pico_p95"] = float(np.percentile(run_df["pico_carga"], 95))
    first_metrics["minutos_saturados_promedio"] = float(run_df["minutos_saturados"].mean())
    first_metrics["utilizacion_maxima_promedio_pct"] = float(run_df["utilizacion_maxima_pct"].mean())
    first_metrics["tiempo_formulario_promedio"] = float(run_df["tiempo_formulario_promedio"].mean())
    first_metrics["ic95_pico"] = confidence_interval(run_df["pico_carga"])
    first_metrics["resultado"] = (
        f"En promedio el pico es {first_metrics['pico_promedio']:.1f} formularios activos; "
        f"en un caso alto puede llegar a {first_metrics['pico_p95']:.0f}."
    )

    if prob_sat >= 30:
        first_metrics["estado"] = "Alto riesgo de saturacion"
        first_metrics["recomendacion"] = "Escalonar envios, usar tandas y preparar un respaldo offline o formulario alternativo."
        first_metrics["decision"] = "No concentrar todos los envios al cierre del evento."
    elif prob_sat >= 10:
        first_metrics["estado"] = "Riesgo moderado de saturacion"
        first_metrics["recomendacion"] = "Pedir envios por grupos y monitorear el pico del formulario."
        first_metrics["decision"] = "Aplicar tandas de envio."

    result = {"metrics": first_metrics, "runs": run_df}
    if include_frames:
        result["people"] = people
        result["timeline"] = timeline
    return result


def confidence_interval(series: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
    values = series.astype(float).to_numpy()
    mean = float(values.mean())
    if len(values) < 2:
        return mean, mean
    z = 1.96 if confidence == 0.95 else 1.64
    half = z * float(values.std(ddof=1)) / np.sqrt(len(values))
    return mean - half, mean + half


def scenario_comparison(inputs: DigitalFlowInputs) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        result = simulate_digital_flow(DigitalFlowInputs(**{**inputs.__dict__, "scenario": scenario}), include_frames=False)
        m = result["metrics"]
        rows.append(
            {
                "escenario": scenario,
                "prob_saturacion_pct": m["probabilidad_saturacion_pct"],
                "pico_promedio": m["pico_promedio"],
                "pico_p95": m["pico_p95"],
                "minutos_saturados_promedio": m["minutos_saturados_promedio"],
                "utilizacion_maxima_promedio_pct": m["utilizacion_maxima_promedio_pct"],
            }
        )
    return pd.DataFrame(rows)


def sensitivity_analysis(inputs: DigitalFlowInputs) -> pd.DataFrame:
    rows = []
    tests = {
        "Tasa de envios": ("arrival_rate_per_hour", [0.75, 1.0, 1.25]),
        "Tiempo de formulario": ("avg_form_completion_min", [0.75, 1.0, 1.25]),
        "Capacidad servidor": ("server_capacity", [0.75, 1.0, 1.25]),
    }
    for variable, (field, factors) in tests.items():
        for factor in factors:
            data = inputs.__dict__.copy()
            data[field] = max(data[field] * factor, 0.1)
            if field == "server_capacity":
                data[field] = max(int(round(data[field])), 1)
            result = simulate_digital_flow(DigitalFlowInputs(**data), include_frames=False)
            rows.append(
                {
                    "variable": variable,
                    "factor": factor,
                    "prob_saturacion_pct": result["metrics"]["probabilidad_saturacion_pct"],
                    "pico_p95": result["metrics"]["pico_p95"],
                }
            )
    return pd.DataFrame(rows)


def verification_checks(result: dict) -> dict[str, bool]:
    people = result["people"]
    timeline = result["timeline"]
    runs = result["runs"]
    return {
        "sin_tiempos_negativos": bool((people[["llegada_min", "fin_degustacion_min", "fin_formulario_min"]] >= 0).all().all()),
        "sin_cantidades_negativas": bool((timeline[["nuevos_envios", "formularios_activos", "capacidad"]] >= 0).all().all()),
        "probabilidades_validas": bool(runs["probabilidad_saturacion_run"].between(0, 100).all()),
        "responde_a_parametros": True,
    }

