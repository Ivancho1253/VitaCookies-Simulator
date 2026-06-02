from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = {
    "Optimista": {"cost_factor": 0.92, "demand_factor": 1.20, "acceptance_factor": 1.10, "waste_factor": 0.80},
    "Esperado": {"cost_factor": 1.00, "demand_factor": 1.00, "acceptance_factor": 1.00, "waste_factor": 1.00},
    "Pesimista": {"cost_factor": 1.15, "demand_factor": 0.75, "acceptance_factor": 0.85, "waste_factor": 1.35},
}


@dataclass(frozen=True)
class ViabilityInputs:
    batch_cost: float
    units_per_batch: int
    fixed_cost: float
    waste_percentage: float
    sale_price: float
    expected_demand: int
    sensory_acceptance: float
    runs: int
    scenario: str = "Esperado"
    seed: int = 42


def simulate_viability(inputs: ViabilityInputs) -> dict:
    rng = np.random.default_rng(inputs.seed)
    scenario = SCENARIOS.get(inputs.scenario, SCENARIOS["Esperado"])

    runs = max(int(inputs.runs), 100)
    batch_cost = max(float(inputs.batch_cost), 0.01)
    units_per_batch = max(int(inputs.units_per_batch), 1)
    fixed_cost = max(float(inputs.fixed_cost), 0)
    sale_price = max(float(inputs.sale_price), 0.01)
    expected_demand = max(int(inputs.expected_demand), 1)
    acceptance_mean = float(np.clip(inputs.sensory_acceptance * scenario["acceptance_factor"], 0, 1))
    waste_mean = float(np.clip(inputs.waste_percentage * scenario["waste_factor"], 0, 0.7))

    demand = rng.normal(expected_demand * scenario["demand_factor"], max(expected_demand * 0.18, 1), runs)
    demand = np.clip(np.round(demand), 0, None).astype(int)
    acceptance = rng.normal(acceptance_mean, 0.08, runs)
    acceptance = np.clip(acceptance, 0, 1)
    waste = rng.normal(waste_mean, max(waste_mean * 0.25, 0.01), runs)
    waste = np.clip(waste, 0, 0.75)
    batch_costs = rng.normal(batch_cost * scenario["cost_factor"], max(batch_cost * 0.06, 1), runs)
    batch_costs = np.clip(batch_costs, 0.01, None)

    sellable_units_per_batch = np.maximum(np.floor(units_per_batch * (1 - waste)), 1)
    effective_demand = np.round(demand * acceptance).astype(int)
    batches_needed = np.ceil(effective_demand / sellable_units_per_batch)
    variable_cost = batches_needed * batch_costs
    total_cost = variable_cost + fixed_cost
    revenue = effective_demand * sale_price
    profit = revenue - total_cost
    contribution_margin = sale_price - (batch_costs / sellable_units_per_batch)

    avg_unit_cost = float(np.mean(batch_costs / sellable_units_per_batch))
    median_margin = float(np.median(contribution_margin))
    if median_margin <= 0:
        break_even_units = float("inf")
    else:
        break_even_units = float(np.ceil(fixed_cost / median_margin))

    profitable_probability = float((profit > 0).mean() * 100)
    avg_profit = float(profit.mean())

    if profitable_probability >= 70 and avg_profit > 0:
        status = "Viable"
        recommendation = (
            "El producto muestra viabilidad preliminar: la probabilidad de rentabilidad es alta "
            "y el precio cubre el costo unitario esperado."
        )
    elif profitable_probability >= 40 or avg_profit > 0:
        status = "Parcialmente viable"
        recommendation = (
            "La viabilidad depende de controlar costos, desperdicio y aceptación sensorial. "
            "Conviene ajustar receta, lote o precio antes de escalar."
        )
    else:
        status = "No viable"
        recommendation = (
            "No conviene escalar con estos supuestos: el margen es insuficiente o la demanda aceptada "
            "no alcanza el punto de equilibrio."
        )

    simulations = pd.DataFrame(
        {
            "demanda_total": demand,
            "aceptacion_sensorial": acceptance,
            "demanda_efectiva": effective_demand,
            "desperdicio_pct": waste,
            "unidades_vendibles_lote": sellable_units_per_batch,
            "lotes_necesarios": batches_needed,
            "costo_total": total_cost,
            "ingresos": revenue,
            "ganancia": profit,
            "margen_contribucion": contribution_margin,
        }
    )

    metrics = {
        "costo_unitario_prom": avg_unit_cost,
        "precio_venta": sale_price,
        "demanda_efectiva_prom": float(effective_demand.mean()),
        "punto_equilibrio_unidades": break_even_units,
        "ganancia_promedio": avg_profit,
        "ganancia_p10": float(np.percentile(profit, 10)),
        "ganancia_p90": float(np.percentile(profit, 90)),
        "probabilidad_rentabilidad_pct": profitable_probability,
        "estado": status,
        "recomendacion": recommendation,
    }

    return {"metrics": metrics, "simulations": simulations}


def simulate_viability_scenarios(inputs: ViabilityInputs) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        scenario_inputs = ViabilityInputs(**{**inputs.__dict__, "scenario": scenario})
        result = simulate_viability(scenario_inputs)
        metrics = result["metrics"]
        rows.append(
            {
                "escenario": scenario,
                "prob_rentabilidad_pct": metrics["probabilidad_rentabilidad_pct"],
                "ganancia_promedio": metrics["ganancia_promedio"],
                "costo_unitario": metrics["costo_unitario_prom"],
                "demanda_efectiva": metrics["demanda_efectiva_prom"],
                "punto_equilibrio": metrics["punto_equilibrio_unidades"],
            }
        )
    return pd.DataFrame(rows)

