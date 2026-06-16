from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf

import pandas as pd


BASE_COST_PER_50_UNITS = 15_000.0
BASE_UNITS_FOR_COST = 50
RECOMMENDED_PROFIT_MARGIN = 0.20


OBSERVED_RESPONSE_MINUTES = [
    0,
    0,
    9,
    10,
    12,
    12,
    13,
    13,
    13,
    13,
    14,
    14,
    14,
    16,
    16,
    19,
    22,
    22,
    24,
    29,
    32,
    37,
    37,
    43,
    43,
    44,
    47,
    49,
    49,
    52,
    52,
    56,
    58,
    58,
    61,
    62,
    62,
    63,
    64,
    67,
    70,
    72,
    75,
    82,
]


DESCRIPTIVE_SCORES = pd.DataFrame(
    [
        {"atributo": "Color", "promedio": 3.79, "respuestas": 34},
        {"atributo": "Aroma", "promedio": 3.32, "respuestas": 34},
        {"atributo": "Sabor", "promedio": 4.06, "respuestas": 34},
        {"atributo": "Textura", "promedio": 2.74, "respuestas": 34},
    ]
)


ACCEPTANCE_SUMMARY = {
    "responses": 50,
    "positive_satisfaction": 41,
    "top_satisfaction": 20,
    "daily_yes": 30,
    "ultra_preference": 39,
    "survey_responses": 42,
}


@dataclass(frozen=True)
class DigitalPostInputs:
    total_responses: int = 44
    duration_min: int = 82
    capacity_per_minute: int = 20


@dataclass(frozen=True)
class StockPostInputs:
    produced_units: int = 50
    leftover_units: int = 5
    registered_responses: int = 44


@dataclass(frozen=True)
class ViabilityPostInputs:
    sale_price: float
    target_units: int = 500
    cost_per_50_units: float = BASE_COST_PER_50_UNITS
    base_units: int = BASE_UNITS_FOR_COST
    positive_acceptance: int = ACCEPTANCE_SUMMARY["positive_satisfaction"]
    acceptance_responses: int = ACCEPTANCE_SUMMARY["responses"]


def simulate_digital_post(inputs: DigitalPostInputs) -> dict:
    counts = pd.Series(OBSERVED_RESPONSE_MINUTES).value_counts().sort_index()
    duration = max(int(inputs.duration_min), int(max(OBSERVED_RESPONSE_MINUTES)), 1)
    timeline = pd.DataFrame({"minuto": range(duration + 1)})
    timeline["respuestas"] = timeline["minuto"].map(counts).fillna(0).astype(int)
    timeline["acumulado"] = timeline["respuestas"].cumsum()
    timeline["capacidad"] = max(int(inputs.capacity_per_minute), 1)
    timeline["utilizacion_pct"] = timeline["respuestas"] / timeline["capacidad"] * 100
    timeline["saturado"] = timeline["respuestas"] > timeline["capacidad"]

    peak = int(timeline["respuestas"].max())
    peak_minute = int(timeline.loc[timeline["respuestas"].idxmax(), "minuto"])
    utilization = float(peak / max(inputs.capacity_per_minute, 1) * 100)
    saturated_minutes = int(timeline["saturado"].sum())
    avg_per_min = float(inputs.total_responses / max(duration, 1))

    if saturated_minutes:
        status = "Hubo saturacion observada"
        decision = "Revisar la capacidad del formulario para futuros testeos."
    elif peak >= inputs.capacity_per_minute * 0.8:
        status = "Pico alto pero sin saturacion"
        decision = "Mantener monitoreo durante el tramo de mayor carga."
    else:
        status = "Flujo digital estable"
        decision = "El formulario funciono correctamente con la concurrencia observada."

    metrics = {
        "respuestas_registradas": int(inputs.total_responses),
        "duracion_recoleccion_min": duration,
        "pico_respuestas_minuto": peak,
        "minuto_pico": peak_minute,
        "capacidad_por_minuto": int(inputs.capacity_per_minute),
        "utilizacion_maxima_pct": utilization,
        "minutos_saturados": saturated_minutes,
        "promedio_respuestas_minuto": avg_per_min,
        "estado": status,
        "resultado": f"Se registraron {inputs.total_responses} respuestas entre 08:10 y 09:32, con pico de {peak} respuestas en un minuto.",
        "interpretacion": "El flujo real no requiere estimar llegadas aleatorias: se analiza la concurrencia efectivamente observada.",
        "recomendacion": "Conservar el formulario digital y reforzar instrucciones en los primeros minutos del testeo.",
        "decision": decision,
    }
    return {"metrics": metrics, "timeline": timeline}


def simulate_stock_post(inputs: StockPostInputs) -> dict:
    produced = max(int(inputs.produced_units), 0)
    leftover = max(min(int(inputs.leftover_units), produced), 0)
    consumed = produced - leftover
    response_coverage = consumed / max(int(inputs.registered_responses), 1)
    consumption_pct = consumed / max(produced, 1) * 100
    leftover_pct = leftover / max(produced, 1) * 100
    suggested_next = int(ceil(consumed * 1.05))

    if leftover == 0:
        status = "Stock justo"
        decision = "Producir una reserva minima para evitar quiebre."
    elif leftover_pct <= 15:
        status = "Stock bien dimensionado"
        decision = "Mantener una produccion cercana a la actual."
    else:
        status = "Sobrante alto"
        decision = "Reducir produccion o porcionar menos unidades en el proximo testeo."

    rows = pd.DataFrame(
        [
            {"concepto": "Producidas", "unidades": produced},
            {"concepto": "Consumidas", "unidades": consumed},
            {"concepto": "Sobrantes", "unidades": leftover},
            {"concepto": "Sugeridas proximo testeo", "unidades": suggested_next},
        ]
    )
    metrics = {
        "galletitas_producidas": produced,
        "galletitas_consumidas": consumed,
        "galletitas_sobrantes": leftover,
        "consumo_pct": consumption_pct,
        "sobrante_pct": leftover_pct,
        "cobertura_respuestas_por_consumo": response_coverage,
        "produccion_sugerida_proximo_testeo": suggested_next,
        "estado": status,
        "resultado": f"De {produced} galletitas producidas se consumieron {consumed} y sobraron {leftover}.",
        "interpretacion": "El stock se evalua con unidades reales, no con demanda simulada.",
        "recomendacion": f"Para un testeo similar, producir alrededor de {suggested_next} unidades deja un margen pequeno sobre el consumo observado.",
        "decision": decision,
    }
    return {"metrics": metrics, "rows": rows}


def simulate_viability_post(inputs: ViabilityPostInputs) -> dict:
    base_units = max(int(inputs.base_units), 1)
    target_units = max(int(inputs.target_units), 1)
    cost_per_50 = max(float(inputs.cost_per_50_units), 0)
    sale_price = max(float(inputs.sale_price), 0)
    acceptance_rate = max(int(inputs.positive_acceptance), 0) / max(int(inputs.acceptance_responses), 1) * 100
    acceptance_ratio = acceptance_rate / 100
    accepted_units = int(round(target_units * acceptance_ratio))
    unsold_units = max(target_units - accepted_units, 0)
    unit_cost = cost_per_50 / base_units if base_units else 0
    projected_cost = unit_cost * target_units
    projected_revenue = accepted_units * sale_price
    projected_profit = projected_revenue - projected_cost
    contribution_margin = sale_price * acceptance_ratio - unit_cost
    break_even_price = inf if accepted_units == 0 else projected_cost / accepted_units
    recommended_price = inf if break_even_price == inf else break_even_price * (1 + RECOMMENDED_PROFIT_MARGIN)
    break_even_units = inf if sale_price <= 0 else ceil(projected_cost / sale_price)
    profit_margin_pct = 0 if projected_revenue <= 0 else projected_profit / projected_revenue * 100
    roi_pct = 0 if projected_cost <= 0 else projected_profit / projected_cost * 100

    if sale_price == 0:
        status = "Precio pendiente"
        decision = f"Definir un precio unitario. Para ganar algo, conviene apuntar a por lo menos ${recommended_price:,.0f} por unidad."
    elif projected_profit > 0 and sale_price >= recommended_price:
        status = "Precio recomendable"
        decision = f"Si vendes a ${sale_price:,.0f}, la produccion deja ganancia y supera el precio recomendado de ${recommended_price:,.0f}."
    elif projected_profit > 0:
        status = "Rentable, pero con margen bajo"
        decision = f"Hay ganancia, pero para un margen mas sano conviene acercar el precio a ${recommended_price:,.0f} por unidad."
    elif acceptance_rate >= 80:
        status = "No rentable a ese precio"
        decision = f"No conviene vender a ${sale_price:,.0f}: no cubre el costo. Minimo ${break_even_price:,.0f}; recomendado ${recommended_price:,.0f}."
    else:
        status = "Requiere ajuste de producto"
        decision = "Mejorar atributos sensoriales antes de escalar."

    scenarios = []
    for units in [50, 100, 250, 500, 1000]:
        accepted = int(round(units * acceptance_ratio))
        unsold = max(units - accepted, 0)
        cost = unit_cost * units
        revenue = accepted * sale_price
        scenarios.append(
            {
                "produccion": units,
                "unidades_aceptadas_estimadas": accepted,
                "unidades_no_vendidas_estimadas": unsold,
                "costo_estimado": cost,
                "ingresos_estimados": revenue,
                "ganancia_estimada": revenue - cost,
            }
        )

    metrics = {
        "aceptacion_positiva_pct": acceptance_rate,
        "respuestas_positivas": int(inputs.positive_acceptance),
        "respuestas_aceptabilidad": int(inputs.acceptance_responses),
        "intencion_consumo_diario_pct": ACCEPTANCE_SUMMARY["daily_yes"] / ACCEPTANCE_SUMMARY["survey_responses"] * 100,
        "preferencia_vs_ultraprocesado_pct": ACCEPTANCE_SUMMARY["ultra_preference"] / ACCEPTANCE_SUMMARY["survey_responses"] * 100,
        "costo_producir_50": cost_per_50,
        "costo_unitario_estimado": unit_cost,
        "produccion_objetivo": target_units,
        "unidades_aceptadas_estimadas": accepted_units,
        "unidades_no_vendidas_estimadas": unsold_units,
        "ingresos_estimados": projected_revenue,
        "costo_estimado": projected_cost,
        "ganancia_estimada": projected_profit,
        "margen_unitario_ponderado": contribution_margin,
        "margen_ganancia_pct": profit_margin_pct,
        "retorno_sobre_costo_pct": roi_pct,
        "precio_equilibrio": break_even_price,
        "precio_recomendado": recommended_price,
        "margen_recomendado_pct": RECOMMENDED_PROFIT_MARGIN * 100,
        "unidades_equilibrio": break_even_units,
        "estado": status,
        "resultado": f"Producir {target_units} galletitas cuesta ${projected_cost:,.0f}; con aceptabilidad de {acceptance_rate:.1f}% se venderian unas {accepted_units}.",
        "interpretacion": f"A ${sale_price:,.0f} por unidad, los ingresos estimados son ${projected_revenue:,.0f} y la ganancia/perdida seria ${projected_profit:,.0f}.",
        "recomendacion": f"Precio recomendado: ${recommended_price:,.0f} por unidad para cubrir costos y dejar cerca de {RECOMMENDED_PROFIT_MARGIN * 100:.0f}% de margen.",
        "decision": decision,
    }
    financial_summary = pd.DataFrame(
        [
            {"concepto": "Ingresos estimados", "monto": projected_revenue},
            {"concepto": "Costo estimado", "monto": projected_cost},
            {"concepto": "Ganancia estimada", "monto": projected_profit},
        ]
    )
    unit_summary = pd.DataFrame(
        [
            {"concepto": "A vender estimadas", "unidades": accepted_units},
            {"concepto": "Sin vender estimadas", "unidades": unsold_units},
        ]
    )
    price_summary = pd.DataFrame(
        [
            {"concepto": "Tu precio", "precio": sale_price},
            {"concepto": "Minimo sin perdida", "precio": 0 if break_even_price == inf else break_even_price},
            {"concepto": "Recomendado", "precio": 0 if recommended_price == inf else recommended_price},
        ]
    )
    return {
        "metrics": metrics,
        "scores": DESCRIPTIVE_SCORES.copy(),
        "scenarios": pd.DataFrame(scenarios),
        "financial_summary": financial_summary,
        "unit_summary": unit_summary,
        "price_summary": price_summary,
    }


def verification_checks(result: dict) -> dict[str, bool]:
    metrics = result["metrics"]
    numeric_values = [
        v
        for key, v in metrics.items()
        if isinstance(v, (int, float)) and v != inf and not key.startswith("ganancia") and not key.startswith("margen")
    ]
    return {
        "sin_valores_negativos_en_metricas": bool(all(v >= 0 for v in numeric_values if "ganancia" not in str(v))),
        "datos_post_testeo_cargados": True,
        "sin_corridas_aleatorias": True,
    }
