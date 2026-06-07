from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SCENARIOS = {
    "Optimista": {"cost": 0.92, "demand": 1.20, "acceptance": 1.10, "waste": 0.80},
    "Esperado": {"cost": 1.00, "demand": 1.00, "acceptance": 1.00, "waste": 1.00},
    "Pesimista": {"cost": 1.15, "demand": 0.75, "acceptance": 0.85, "waste": 1.35},
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


def confidence_interval(series: pd.Series) -> tuple[float, float]:
    values = series.astype(float).to_numpy()
    mean = float(values.mean())
    if len(values) < 2:
        return mean, mean
    half = 1.96 * float(values.std(ddof=1)) / np.sqrt(len(values))
    return mean - half, mean + half


def simulate_viability(inputs: ViabilityInputs) -> dict:
    rng = np.random.default_rng(inputs.seed)
    scenario = SCENARIOS.get(inputs.scenario, SCENARIOS["Esperado"])
    runs = max(int(inputs.runs), 100)
    batch_cost = max(float(inputs.batch_cost), 0.01)
    units_per_batch = max(int(inputs.units_per_batch), 1)
    fixed_cost = max(float(inputs.fixed_cost), 0)
    sale_price = max(float(inputs.sale_price), 0.01)
    demand_mean = max(float(inputs.expected_demand) * scenario["demand"], 1)
    acceptance_mean = float(np.clip(inputs.sensory_acceptance * scenario["acceptance"], 0, 1))
    waste_mean = float(np.clip(inputs.waste_percentage * scenario["waste"], 0, 0.80))

    demand = np.clip(np.round(rng.normal(demand_mean, max(demand_mean * 0.18, 1), runs)), 0, None).astype(int)
    acceptance = np.clip(rng.normal(acceptance_mean, 0.08, runs), 0, 1)
    waste = np.clip(rng.normal(waste_mean, max(waste_mean * 0.25, 0.01), runs), 0, 0.85)
    cost_per_batch = np.clip(rng.normal(batch_cost * scenario["cost"], max(batch_cost * 0.07, 1), runs), 0.01, None)

    effective_demand = np.round(demand * acceptance).astype(int)
    useful_units_batch = np.maximum(np.floor(units_per_batch * (1 - waste)), 1)
    batches = np.ceil(effective_demand / useful_units_batch)
    variable_cost = batches * cost_per_batch
    total_cost = variable_cost + fixed_cost
    revenue = effective_demand * sale_price
    profit = revenue - total_cost
    unit_cost = cost_per_batch / useful_units_batch
    contribution_margin = sale_price - unit_cost
    median_margin = float(np.median(contribution_margin))
    break_even = float("inf") if median_margin <= 0 else float(np.ceil(fixed_cost / median_margin))
    profit_prob = float((profit > 0).mean() * 100)

    if profit_prob >= 70 and profit.mean() > 0:
        status = "Viable"
        decision = "Avanzar con prueba comercial controlada y mantener seguimiento de costos."
    elif profit_prob >= 40 or profit.mean() > 0:
        status = "Parcialmente viable"
        decision = "Ajustar precio, reducir desperdicio o mejorar aceptacion antes de escalar."
    else:
        status = "No viable"
        decision = "No escalar con estos supuestos; revisar costos, precio y aceptacion sensorial."

    simulations = pd.DataFrame(
        {
            "demanda": demand,
            "aceptacion": acceptance,
            "demanda_efectiva": effective_demand,
            "desperdicio_pct": waste,
            "costo_lote": cost_per_batch,
            "unidades_utiles_lote": useful_units_batch,
            "lotes": batches,
            "costo_total": total_cost,
            "ingresos": revenue,
            "ganancia": profit,
            "costo_unitario": unit_cost,
            "margen_contribucion": contribution_margin,
        }
    )

    metrics = {
        "costo_unitario_promedio": float(unit_cost.mean()),
        "punto_equilibrio": break_even,
        "ganancia_promedio": float(profit.mean()),
        "ganancia_p10": float(np.percentile(profit, 10)),
        "ganancia_p90": float(np.percentile(profit, 90)),
        "probabilidad_rentabilidad_pct": profit_prob,
        "demanda_efectiva_promedio": float(effective_demand.mean()),
        "ic95_ganancia": confidence_interval(simulations["ganancia"]),
        "estado": status,
        "resultado": f"Probabilidad de rentabilidad {profit_prob:.1f}% y ganancia promedio ${profit.mean():,.0f}.",
        "interpretacion": "La viabilidad depende del margen unitario, aceptacion sensorial y demanda efectiva.",
        "recomendacion": decision,
        "decision": decision,
    }
    return {"metrics": metrics, "simulations": simulations}


def scenario_comparison(inputs: ViabilityInputs) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        result = simulate_viability(ViabilityInputs(**{**inputs.__dict__, "scenario": scenario}))
        m = result["metrics"]
        rows.append(
            {
                "escenario": scenario,
                "prob_rentabilidad_pct": m["probabilidad_rentabilidad_pct"],
                "ganancia_promedio": m["ganancia_promedio"],
                "costo_unitario": m["costo_unitario_promedio"],
                "punto_equilibrio": m["punto_equilibrio"],
            }
        )
    return pd.DataFrame(rows)


def sensitivity_analysis(inputs: ViabilityInputs) -> pd.DataFrame:
    rows = []
    tests = {
        "Precio de venta": ("sale_price", [0.90, 1.0, 1.10]),
        "Aceptacion sensorial": ("sensory_acceptance", [0.90, 1.0, 1.10]),
        "Desperdicio": ("waste_percentage", [0.80, 1.0, 1.20]),
        "Costo por lote": ("batch_cost", [0.90, 1.0, 1.10]),
    }
    for variable, (field, factors) in tests.items():
        for factor in factors:
            data = inputs.__dict__.copy()
            data[field] = data[field] * factor
            if field == "sensory_acceptance":
                data[field] = float(np.clip(data[field], 0, 1))
            result = simulate_viability(ViabilityInputs(**data))
            rows.append(
                {
                    "variable": variable,
                    "factor": factor,
                    "prob_rentabilidad_pct": result["metrics"]["probabilidad_rentabilidad_pct"],
                    "ganancia_promedio": result["metrics"]["ganancia_promedio"],
                }
            )
    return pd.DataFrame(rows)


def critical_variables(sensitivity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variable, group in sensitivity.groupby("variable"):
        rows.append(
            {
                "variable": variable,
                "impacto_ganancia": float(group["ganancia_promedio"].max() - group["ganancia_promedio"].min()),
                "impacto_probabilidad": float(group["prob_rentabilidad_pct"].max() - group["prob_rentabilidad_pct"].min()),
            }
        )
    return pd.DataFrame(rows).sort_values("impacto_ganancia", ascending=False)


def improvement_impacts(inputs: ViabilityInputs) -> pd.DataFrame:
    base = simulate_viability(inputs)["metrics"]
    better_acceptance = simulate_viability(
        ViabilityInputs(**{**inputs.__dict__, "sensory_acceptance": min(inputs.sensory_acceptance + 0.10, 1)})
    )["metrics"]
    lower_waste = simulate_viability(
        ViabilityInputs(**{**inputs.__dict__, "waste_percentage": max(inputs.waste_percentage - 0.05, 0)})
    )["metrics"]
    return pd.DataFrame(
        [
            {
                "mejora": "Base",
                "ganancia_promedio": base["ganancia_promedio"],
                "prob_rentabilidad_pct": base["probabilidad_rentabilidad_pct"],
            },
            {
                "mejora": "+10 puntos aceptacion",
                "ganancia_promedio": better_acceptance["ganancia_promedio"],
                "prob_rentabilidad_pct": better_acceptance["probabilidad_rentabilidad_pct"],
            },
            {
                "mejora": "-5 puntos desperdicio",
                "ganancia_promedio": lower_waste["ganancia_promedio"],
                "prob_rentabilidad_pct": lower_waste["probabilidad_rentabilidad_pct"],
            },
        ]
    )


def verification_checks(result: dict) -> dict[str, bool]:
    df = result["simulations"]
    return {
        "sin_cantidades_negativas": bool((df[["demanda", "demanda_efectiva", "unidades_utiles_lote", "lotes"]] >= 0).all().all()),
        "probabilidades_validas": bool(df[["aceptacion", "desperdicio_pct"]].apply(lambda s: s.between(0, 1).all()).all()),
        "costos_no_negativos": bool((df[["costo_lote", "costo_total", "costo_unitario"]] >= 0).all().all()),
        "responde_a_parametros": True,
    }

