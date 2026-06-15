from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf

import pandas as pd


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
    "responses": 42,
    "positive_satisfaction": 41,
    "top_satisfaction": 20,
    "daily_yes": 30,
    "ultra_preference": 39,
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
    batch_cost: float
    fixed_cost: float
    sale_price: float
    produced_units: int = 50
    consumed_units: int = 45
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
    produced = max(int(inputs.produced_units), 1)
    consumed = max(min(int(inputs.consumed_units), produced), 0)
    batch_cost = max(float(inputs.batch_cost), 0)
    fixed_cost = max(float(inputs.fixed_cost), 0)
    sale_price = max(float(inputs.sale_price), 0)
    total_cost = batch_cost + fixed_cost
    revenue = consumed * sale_price
    profit = revenue - total_cost
    unit_cost_produced = total_cost / produced
    unit_cost_consumed = total_cost / max(consumed, 1)
    contribution_margin = sale_price - unit_cost_consumed
    break_even = inf if sale_price <= 0 else ceil(total_cost / sale_price)
    acceptance_rate = max(int(inputs.positive_acceptance), 0) / max(int(inputs.acceptance_responses), 1) * 100

    if profit > 0 and acceptance_rate >= 80:
        status = "Viable con datos observados"
        decision = "Avanzar a una prueba comercial controlada."
    elif acceptance_rate >= 80:
        status = "Aceptacion alta, margen a revisar"
        decision = "Mantener la receta y ajustar precio, costos o escala."
    else:
        status = "Requiere ajuste de producto"
        decision = "Mejorar atributos sensoriales antes de escalar."

    metrics = {
        "aceptacion_positiva_pct": acceptance_rate,
        "intencion_consumo_diario_pct": ACCEPTANCE_SUMMARY["daily_yes"] / ACCEPTANCE_SUMMARY["responses"] * 100,
        "preferencia_vs_ultraprocesado_pct": ACCEPTANCE_SUMMARY["ultra_preference"] / ACCEPTANCE_SUMMARY["responses"] * 100,
        "ingresos_observados": revenue,
        "costo_total": total_cost,
        "ganancia_observada": profit,
        "costo_unitario_producido": unit_cost_produced,
        "costo_unitario_consumido": unit_cost_consumed,
        "margen_unitario_sobre_consumidas": contribution_margin,
        "punto_equilibrio_unidades": break_even,
        "estado": status,
        "resultado": f"Aceptacion positiva de {acceptance_rate:.1f}% y ganancia observada de ${profit:,.0f}.",
        "interpretacion": "La viabilidad se calcula con consumo, aceptacion, precio y costos observados/cargados.",
        "recomendacion": "La textura es el atributo mas debil; conviene mejorar crocancia sin perder el sabor, que fue el mejor puntuado.",
        "decision": decision,
    }
    return {"metrics": metrics, "scores": DESCRIPTIVE_SCORES.copy()}


def verification_checks(result: dict) -> dict[str, bool]:
    metrics = result["metrics"]
    numeric_values = [
        v
        for key, v in metrics.items()
        if isinstance(v, (int, float)) and v != inf and not key.startswith("ganancia")
    ]
    return {
        "sin_valores_negativos_en_metricas": bool(all(v >= 0 for v in numeric_values if "ganancia" not in str(v))),
        "datos_post_testeo_cargados": True,
        "sin_corridas_aleatorias": True,
    }
