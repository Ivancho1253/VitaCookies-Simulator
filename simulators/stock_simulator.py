from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = {
    "Optimista": {"people_factor": 0.90, "trial_factor": 0.95, "waste_factor": 0.85},
    "Esperado": {"people_factor": 1.00, "trial_factor": 1.00, "waste_factor": 1.00},
    "Pesimista": {"people_factor": 1.15, "trial_factor": 1.08, "waste_factor": 1.25},
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


def simulate_stock(inputs: StockInputs) -> dict:
    rng = np.random.default_rng(inputs.seed)
    scenario = SCENARIOS.get(inputs.scenario, SCENARIOS["Esperado"])

    runs = max(int(inputs.runs), 100)
    initial_portions = max(int(inputs.initial_portions), 0)
    expected_diners = max(int(inputs.expected_diners), 1)
    trial_probability = float(np.clip(inputs.trial_probability * scenario["trial_factor"], 0, 1))
    waste_mean = float(np.clip(inputs.waste_percentage * scenario["waste_factor"], 0, 0.6))
    safety_margin = float(np.clip(inputs.safety_margin, 0, 0.8))

    diners_mean = expected_diners * scenario["people_factor"]
    diners = rng.normal(diners_mean, max(diners_mean * 0.12, 1), runs)
    diners = np.clip(np.round(diners), 0, None).astype(int)
    demand = rng.binomial(diners, trial_probability)

    waste = rng.normal(waste_mean, max(waste_mean * 0.25, 0.01), runs)
    waste = np.clip(waste, 0, 0.7)
    usable_portions = np.floor(initial_portions * (1 - waste)).astype(int)

    missing = np.maximum(demand - usable_portions, 0)
    surplus = np.maximum(usable_portions - demand, 0)
    wasted_by_process = initial_portions - usable_portions
    shortage_probability = float((missing > 0).mean() * 100)

    recommended_base = np.percentile(demand / np.maximum(1 - waste, 0.05), 90)
    recommended_portions = int(np.ceil(recommended_base * (1 + safety_margin)))

    if shortage_probability <= 5 and surplus.mean() <= initial_portions * 0.35:
        status = "Stock suficiente"
        recommendation = (
            "El stock cubre la demanda con bajo riesgo. Mantener control de entrega para reducir desperdicio."
        )
    elif shortage_probability <= 15:
        status = "Stock ajustado"
        recommendation = (
            f"Preparar cerca de {recommended_portions} porciones o tener una reserva; "
            "el riesgo no es crítico, pero puede aparecer faltante si aumenta la participación."
        )
    else:
        status = "Alto riesgo de quiebre"
        recommendation = (
            f"Aumentar la producción a por lo menos {recommended_portions} porciones "
            "antes del testeo sensorial."
        )

    simulations = pd.DataFrame(
        {
            "comensales": diners,
            "demanda_porciones": demand,
            "desperdicio_pct": waste,
            "porciones_utiles": usable_portions,
            "porciones_faltantes": missing,
            "porciones_sobrantes": surplus,
            "desperdicio_proceso": wasted_by_process,
        }
    )

    metrics = {
        "probabilidad_quiebre_pct": shortage_probability,
        "demanda_promedio": float(demand.mean()),
        "demanda_p90": float(np.percentile(demand, 90)),
        "porciones_faltantes_prom": float(missing.mean()),
        "porciones_sobrantes_prom": float(surplus.mean()),
        "desperdicio_promedio": float(wasted_by_process.mean()),
        "porciones_recomendadas": recommended_portions,
        "estado": status,
        "recomendacion": recommendation,
    }

    return {"metrics": metrics, "simulations": simulations}


def simulate_stock_scenarios(inputs: StockInputs) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        scenario_inputs = StockInputs(**{**inputs.__dict__, "scenario": scenario})
        result = simulate_stock(scenario_inputs)
        metrics = result["metrics"]
        rows.append(
            {
                "escenario": scenario,
                "prob_quiebre_pct": metrics["probabilidad_quiebre_pct"],
                "demanda_promedio": metrics["demanda_promedio"],
                "faltante_promedio": metrics["porciones_faltantes_prom"],
                "sobrante_promedio": metrics["porciones_sobrantes_prom"],
                "recomendadas": metrics["porciones_recomendadas"],
            }
        )
    return pd.DataFrame(rows)

