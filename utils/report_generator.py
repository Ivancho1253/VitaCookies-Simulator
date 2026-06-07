from __future__ import annotations

from datetime import datetime
from io import BytesIO
from math import isinf
from typing import Any


MODEL_CARDS = {
    "digital": {
        "title": "Simulador 1 - Formulario digital",
        "system": "Personas que prueban VitaCookies y luego responden un formulario.",
        "objective": "Ver si el formulario puede trabarse cuando muchas personas responden juntas.",
        "entities": "Personas, formulario digital y capacidad simultanea.",
        "state": "Formularios activos, uso del sistema y minutos de saturacion.",
        "events": "Llegada del comensal, fin de degustacion, inicio de carga, fin/envio del formulario.",
        "parameters": "Tasa de llegada, duracion, tiempo de degustacion, tiempo de formulario, capacidad concurrente.",
        "inputs": "Escenario, tasa de llegada, duracion, tiempos promedio, capacidad y Numero de simulaciones.",
        "outputs": "Riesgo de saturacion, pico esperado, pico prudente, uso del sistema y decision sugerida.",
        "assumptions": "Cada persona tiene celular propio; la limitacion relevante es la concurrencia del formulario.",
        "restrictions": "No modela fallas reales de red ni decisiones individuales complejas.",
        "scope": "Apoya decisiones operativas antes y despues del testeo sensorial.",
    },
    "stock": {
        "title": "Simulador 2 - Porciones para el testeo",
        "system": "Porciones disponibles para las personas que asisten al testeo.",
        "objective": "Estimar si las porciones alcanzan y cuanta reserva conviene preparar.",
        "entities": "Comensales, porciones, desperdicio, demanda.",
        "state": "Porciones utiles, demanda, faltantes, sobrantes.",
        "events": "Asistencia al evento, decision de probar, consumo, perdida/desperdicio.",
        "parameters": "Porciones iniciales, comensales esperados, probabilidad de prueba, desperdicio, margen.",
        "inputs": "Porciones iniciales, comensales, probabilidad de consumo, desperdicio, reserva extra y Numero de simulaciones.",
        "outputs": "Riesgo de faltante, demanda alta, faltantes, sobrantes y porciones sugeridas.",
        "assumptions": "La demanda y desperdicio varian aleatoriamente alrededor de los supuestos cargados.",
        "restrictions": "No modela preferencias individuales ni reposicion durante el evento.",
        "scope": "Apoya la decision de cantidad a producir para evitar faltantes y desperdicio excesivo.",
    },
    "viability": {
        "title": "Simulador 3 - Viabilidad del producto",
        "system": "Produccion y posible venta de VitaCookies.",
        "objective": "Probar si el precio, los costos y la aceptacion alcanzan para que el producto sea rentable.",
        "entities": "Lotes, unidades, demanda, consumidores, costos, ingresos.",
        "state": "Unidades vendibles, demanda efectiva, costos, ingresos y ganancia.",
        "events": "Produccion de lote, desperdicio, venta, recuperacion de costos.",
        "parameters": "Costo por lote, unidades, precio, demanda, aceptacion, desperdicio y costos fijos.",
        "inputs": "Costos, precio, demanda esperada, aceptacion sensorial, desperdicio y Numero de simulaciones.",
        "outputs": "Costo unitario, punto de equilibrio, ganancia, chance de rentabilidad y decision.",
        "assumptions": "La aceptacion sensorial impacta sobre la demanda efectiva.",
        "restrictions": "No reemplaza un estudio de mercado ni costos industriales reales.",
        "scope": "Apoya una decision preliminar sobre escalar o ajustar el producto.",
    },
}

METRIC_LABELS = {
    "probabilidad_saturacion_pct": "Riesgo de saturacion (%)",
    "pico_promedio": "Pico esperado",
    "pico_p95": "Pico prudente",
    "minutos_saturados_promedio": "Minutos saturados promedio",
    "utilizacion_maxima_promedio_pct": "Uso maximo promedio (%)",
    "probabilidad_quiebre_pct": "Riesgo de faltante (%)",
    "demanda_p95": "Demanda alta",
    "faltante_promedio": "Faltante promedio",
    "sobrante_promedio": "Sobrante promedio",
    "stock_recomendado": "Porciones sugeridas",
    "probabilidad_rentabilidad_pct": "Chance de rentabilidad (%)",
    "ganancia_promedio": "Ganancia promedio",
    "ganancia_p10": "Ganancia baja",
    "costo_unitario_promedio": "Costo unitario promedio",
    "punto_equilibrio": "Punto de equilibrio",
}


def _fmt(value: Any) -> str:
    if value is None:
        return "No ejecutado"
    if isinstance(value, tuple):
        return f"{value[0]:,.2f} a {value[1]:,.2f}"
    if isinstance(value, float) and isinf(value):
        return "No alcanzable"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def _metric_label(key: str) -> str:
    return METRIC_LABELS.get(key, key.replace("_", " ").capitalize())


def _model_section(key: str, result: dict | None) -> str:
    card = MODEL_CARDS[key]
    lines = [
        f"## {card['title']}",
        "",
        "### Como se calcula",
        f"- **Sistema:** {card['system']}",
        f"- **Objetivo:** {card['objective']}",
        f"- **Entidades:** {card['entities']}",
        f"- **Variables de estado:** {card['state']}",
        f"- **Eventos:** {card['events']}",
        f"- **Parametros:** {card['parameters']}",
        f"- **Variables de entrada:** {card['inputs']}",
        f"- **Variables de salida:** {card['outputs']}",
        f"- **Supuestos:** {card['assumptions']}",
        f"- **Restricciones:** {card['restrictions']}",
        f"- **Alcance:** {card['scope']}",
        "",
    ]
    if not result:
        lines.append("El simulador no fue ejecutado en esta sesion.")
        return "\n".join(lines)

    metrics = result["metrics"]
    lines.extend(["### Lectura rapida", ""])
    lines.append(f"- **Que paso:** {metrics.get('resultado', 'No disponible')}")
    lines.append(f"- **Que significa:** {metrics.get('interpretacion', 'No disponible')}")
    lines.append(f"- **Que conviene hacer:** {metrics.get('recomendacion', 'No disponible')}")
    lines.append(f"- **Decision:** {metrics.get('decision', 'No disponible')}")
    lines.append("")
    lines.append("### Indicadores principales")
    for key_metric, value in metrics.items():
        if key_metric in {"resultado", "interpretacion", "recomendacion", "decision"}:
            continue
        lines.append(f"- **{_metric_label(key_metric)}:** {_fmt(value)}")
    return "\n".join(lines)


def generate_markdown_report(results: dict[str, dict | None], verification: dict[str, dict] | None = None) -> str:
    date = datetime.now().strftime("%d/%m/%Y %H:%M")
    verification = verification or {}
    verification_lines = []
    for model, checks in verification.items():
        verification_lines.append(f"### {model}")
        for check, ok in checks.items():
            verification_lines.append(f"- {check.replace('_', ' ')}: {'cumple' if ok else 'revisar'}")
    verification_text = "\n".join(verification_lines) if verification_lines else "La verificacion se completa al ejecutar los simuladores."

    return f"""# Informe academico - Simuladores VitaCookies

**Fecha:** {date}

**Materia:** Modelos y Simulacion  
**Proyecto:** Evaluacion integradora intercatedra entre Ingenieria en Sistemas y Nutricion  
**Producto:** Galletita vegetal sustentable con avena, lentejas, manzana y zanahoria.

## Portada

El presente informe documenta una herramienta de simulacion desarrollada para apoyar decisiones antes y despues del testeo sensorial de VitaCookies. La herramienta integra simulacion de eventos discretos y Monte Carlo para analizar riesgos operativos, stock y viabilidad productiva/comercial.

## Descripcion general

El objetivo no es predecir exactamente el evento, sino construir modelos defendibles que permitan comparar escenarios, cuantificar incertidumbre y justificar recomendaciones concretas para el equipo de Nutricion.

## Simulaciones del tablero

Estas simulaciones anticipan riesgos operativos y comerciales: concurrencia del formulario, stock de porciones y viabilidad preliminar. Su proposito es apoyar decisiones con supuestos claros y acciones preventivas.

{_model_section("digital", results.get("digital"))}

{_model_section("stock", results.get("stock"))}

{_model_section("viability", results.get("viability"))}

## Escenarios

Todos los simuladores trabajan con escenarios optimista, esperado y pesimista. Estos escenarios modifican parametros relevantes del modelo: demanda, tiempos, desperdicio, costos, aceptacion o capacidad. No son etiquetas visuales, sino cambios efectivos en las distribuciones simuladas.

## Chequeos internos

{verification_text}

## Validacion del modelo

La validacion se realiza comparando los resultados simulados con datos reales del evento. Las metricas a contrastar son: cantidad real de comensales, tiempo observado de carga del formulario, momentos de mayor concurrencia, porciones consumidas, porciones desperdiciadas, aceptacion sensorial e indicadores de viabilidad.

Luego del evento se pueden ajustar los parametros base: tasa de llegada, probabilidad de prueba, porcentaje de desperdicio, aceptacion sensorial y demanda esperada.

## Analisis para toma de decisiones

- Si aumenta la probabilidad de saturacion digital, se recomienda escalonar los envios y tener respaldo.
- Si aumenta la probabilidad de faltante, se recomienda producir mas porciones o definir reserva.
- Si baja la probabilidad de rentabilidad, se recomienda revisar precio, costos, desperdicio o aceptacion sensorial.

## Limitaciones

- Los modelos simplifican comportamientos individuales.
- La capacidad del formulario es estimada si no se dispone de medicion tecnica real.
- Los costos comerciales deben reemplazarse por datos reales si el producto escala.
- La aceptacion sensorial se resume como variable agregada.

## Mejoras futuras

- Importar respuestas reales del formulario digital.
- Guardar historiales de escenarios.
- Exportar graficos al informe final.
"""


def generate_docx_report(markdown_text: str) -> bytes:
    from docx import Document

    document = Document()
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            document.add_heading(line[2:], level=0)
        elif line.startswith("## "):
            document.add_heading(line[3:], level=1)
        elif line.startswith("### "):
            document.add_heading(line[4:], level=2)
        elif line.startswith("- "):
            document.add_paragraph(line[2:], style="List Bullet")
        elif line[0:2].isdigit() and ". " in line[:4]:
            document.add_paragraph(line, style="List Number")
        else:
            document.add_paragraph(line.replace("**", ""))
    output = BytesIO()
    document.save(output)
    return output.getvalue()

