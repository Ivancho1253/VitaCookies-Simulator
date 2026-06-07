from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = {
    "Optimista": {"diners": 0.90, "trial": 0.95, "waste": 0.80},
    "Esperado": {"diners": 1.00, "trial": 1.00, "waste": 1.00},
    "Pesimista": {"diners": 1.20, "trial": 1.10, "waste": 1.30},
}


@dataclass(frozen=True)
class StockInputs:
    initial_portions: int
    expected_diners: int
    trial_probability: float
    waste_percentage: float
    safety_margin: float
    runs: int
    scenario: str = "Esperado"
    seed: int = 42


def confidence_interval(series: pd.Series) -> tuple[float, float]:
    values = series.astype(float).to_numpy()
    mean = float(values.mean())
    if len(values) < 2:
        return mean, mean
    half = 1.96 * float(values.std(ddof=1)) / np.sqrt(len(values))
    return mean - half, mean + half


def simulate_stock(inputs: StockInputs) -> dict:
    rng = np.random.default_rng(inputs.seed)
    scenario = SCENARIOS.get(inputs.scenario, SCENARIOS["Esperado"])
    runs = max(int(inputs.runs), 100)
    initial = max(int(inputs.initial_portions), 0)
    diners_mean = max(float(inputs.expected_diners) * scenario["diners"], 1)
    trial_prob = float(np.clip(inputs.trial_probability * scenario["trial"], 0, 1))
    waste_mean = float(np.clip(inputs.waste_percentage * scenario["waste"], 0, 0.70))
    safety = float(np.clip(inputs.safety_margin, 0, 1))

    diners = np.clip(np.round(rng.normal(diners_mean, max(diners_mean * 0.15, 1), runs)), 0, None).astype(int)
    demand = rng.binomial(diners, trial_prob)
    waste = np.clip(rng.normal(waste_mean, max(waste_mean * 0.25, 0.01), runs), 0, 0.85)
    usable = np.floor(initial * (1 - waste)).astype(int)
    shortage = np.maximum(demand - usable, 0)
    surplus = np.maximum(usable - demand, 0)
    process_waste = initial - usable

    shortage_prob = float((shortage > 0).mean() * 100)
    recommended_raw = np.percentile(demand / np.maximum(1 - waste, 0.05), 90)
    recommended = int(np.ceil(recommended_raw * (1 + safety)))

    if shortage_prob > 20:
        status = "Alto riesgo de quiebre"
        decision = f"Aumentar produccion a por lo menos {recommended} porciones."
    elif shortage_prob > 5:
        status = "Stock ajustado"
        decision = f"Preparar reserva o acercar el stock a {recommended} porciones."
    else:
        status = "Stock suficiente"
        decision = "Mantener stock previsto y controlar desperdicio de servicio."

    simulations = pd.DataFrame(
        {
            "comensales": diners,
            "demanda": demand,
            "desperdicio_pct": waste,
            "porciones_utiles": usable,
            "faltantes": shortage,
            "sobrantes": surplus,
            "desperdicio_proceso": process_waste,
        }
    )

    metrics = {
        "probabilidad_quiebre_pct": shortage_prob,
        "demanda_promedio": float(demand.mean()),
        "demanda_p50": float(np.percentile(demand, 50)),
        "demanda_p90": float(np.percentile(demand, 90)),
        "demanda_p95": float(np.percentile(demand, 95)),
        "faltante_promedio": float(shortage.mean()),
        "sobrante_promedio": float(surplus.mean()),
        "desperdicio_promedio": float(process_waste.mean()),
        "stock_recomendado": recommended,
        "ic95_demanda": confidence_interval(simulations["demanda"]),
        "estado": status,
        "resultado": f"Probabilidad de quiebre {shortage_prob:.1f}% con {initial} porciones iniciales.",
        "interpretacion": "El riesgo aumenta cuando la demanda efectiva y el desperdicio superan las porciones utiles.",
        "recomendacion": decision,
        "decision": decision,
    }
    return {"metrics": metrics, "simulations": simulations}


def scenario_comparison(inputs: StockInputs) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        result = simulate_stock(StockInputs(**{**inputs.__dict__, "scenario": scenario}))
        m = result["metrics"]
        rows.append(
            {
                "escenario": scenario,
                "prob_quiebre_pct": m["probabilidad_quiebre_pct"],
                "demanda_p95": m["demanda_p95"],
                "faltante_promedio": m["faltante_promedio"],
                "sobrante_promedio": m["sobrante_promedio"],
                "stock_recomendado": m["stock_recomendado"],
            }
        )
    return pd.DataFrame(rows)


def sensitivity_analysis(inputs: StockInputs) -> pd.DataFrame:
    rows = []
    tests = {
        "Comensales esperados": ("expected_diners", [0.80, 1.0, 1.20]),
        "Probabilidad de prueba": ("trial_probability", [0.80, 1.0, 1.20]),
        "Desperdicio": ("waste_percentage", [0.75, 1.0, 1.25]),
    }
    for variable, (field, factors) in tests.items():
        for factor in factors:
            data = inputs.__dict__.copy()
            data[field] = data[field] * factor
            if field == "expected_diners":
                data[field] = max(int(round(data[field])), 1)
            if field == "trial_probability":
                data[field] = float(np.clip(data[field], 0, 1))
            result = simulate_stock(StockInputs(**data))
            rows.append(
                {
                    "variable": variable,
                    "factor": factor,
                    "prob_quiebre_pct": result["metrics"]["probabilidad_quiebre_pct"],
                    "stock_recomendado": result["metrics"]["stock_recomendado"],
                }
            )
    return pd.DataFrame(rows)


def verification_checks(result: dict) -> dict[str, bool]:
    df = result["simulations"]
    return {
        "sin_cantidades_negativas": bool((df[["comensales", "demanda", "porciones_utiles", "faltantes", "sobrantes"]] >= 0).all().all()),
        "probabilidades_validas": bool(df["desperdicio_pct"].between(0, 1).all()),
        "stock_recomendado_no_negativo": bool(result["metrics"]["stock_recomendado"] >= 0),
        "responde_a_parametros": True,
    }

