from __future__ import annotations

from datetime import datetime
from math import isinf
from typing import Any


def _fmt(value: Any, decimals: int = 2) -> str:
    if value is None:
        return "No disponible"
    if isinstance(value, float) and isinf(value):
        return "No alcanzable con margen negativo"
    if isinstance(value, (int, float)):
        return f"{value:,.{decimals}f}"
    return str(value)


def _section_result(title: str, result: dict | None, interpretation: str) -> str:
    if not result:
        return f"## {title}\n\nEl simulador no fue ejecutado en esta sesión.\n"

    metrics = result["metrics"]
    lines = [f"## {title}", "", "### Resultados principales", ""]
    for key, value in metrics.items():
        if key.startswith("recomendacion"):
            continue
        label = key.replace("_", " ").capitalize()
        lines.append(f"- **{label}:** {_fmt(value)}")

    lines.extend(
        [
            "",
            "### Interpretación",
            "",
            interpretation,
            "",
            "### Recomendación para Nutrición",
            "",
            metrics.get("recomendacion", "No disponible."),
        ]
    )
    return "\n".join(lines)


def generate_markdown_report(results: dict[str, dict | None]) -> str:
    """Builds an academic Markdown report from the last executed simulations."""
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    queue = results.get("queue")
    stock = results.get("stock")
    viability = results.get("viability")

    queue_interpretation = (
        "El modelo permite estimar si la carga simultánea del formulario digital puede superar "
        "la capacidad concurrente considerada. Se asume que cada comensal puede usar su propio "
        "celular, por lo que el recurso limitado no es el dispositivo sino la concurrencia de envíos."
    )
    stock_interpretation = (
        "La simulación estima la demanda efectiva de porciones a partir de comensales esperados, "
        "probabilidad de prueba y desperdicio. El resultado sirve para decidir si conviene producir "
        "más, sostener el stock previsto o aceptar cierto sobrante para reducir el riesgo de quiebre."
    )
    viability_interpretation = (
        "El modelo combina demanda, aceptación sensorial, costos, desperdicio y precio de venta. "
        "No reemplaza un estudio comercial completo, pero permite justificar una decisión preliminar "
        "sobre escalabilidad del producto después del testeo."
    )

    report = f"""# Informe técnico - Simuladores VitaCookies

**Fecha de generación:** {generated_at}

## Descripción general

VitaCookies es una propuesta de galletitas vegetales sustentables elaboradas con avena, lentejas, manzana y zanahoria. Este proyecto digital apoya el trabajo integrador entre Ingeniería en Sistemas y Nutrición mediante tres simuladores orientados a anticipar riesgos, evaluar escenarios y producir recomendaciones antes y después del testeo sensorial.

El formulario digital de referencia para la evaluación sensorial se encuentra en: https://vita-cookies-form-v.vercel.app/

## Objetivo general

Desarrollar una herramienta clara, defendible y útil para la toma de decisiones del equipo de Nutrición, integrando un modelo de carga digital, inventario y Montecarlo productivo/comercial.

## Modelos implementados

- **Envío simultáneo del formulario digital:** simulación de eventos discretos con llegadas aleatorias y carga concurrente del formulario.
- **Stock de porciones:** simulación Montecarlo de demanda, desperdicio y faltantes.
- **Viabilidad productiva/comercial:** simulación Montecarlo de costos, aceptación, demanda, punto de equilibrio y ganancia.

## Variables de entrada

- Tasa estimada de envíos, duración del evento, capacidad concurrente del formulario y tiempo promedio de carga.
- Porciones iniciales, comensales esperados, probabilidad de prueba, desperdicio, margen de seguridad y corridas Montecarlo.
- Costo por lote, unidades por lote, desperdicio productivo, precio, demanda esperada, aceptación sensorial, costos fijos y corridas Montecarlo.

## Variables de salida

- Envíos simulados, pico de carga digital, minutos saturados, porcentaje de tiempo saturado y recomendación operativa.
- Probabilidad de quiebre de stock, demanda estimada, faltantes, sobrantes, desperdicio y porciones recomendadas.
- Costo unitario, punto de equilibrio, ganancia esperada, probabilidad de rentabilidad y recomendación de viabilidad.

## Supuestos del modelo

- Las llegadas se aproximan mediante un proceso aleatorio de Poisson.
- Los tiempos de carga del formulario se modelan con distribuciones positivas para evitar valores irreales.
- La aceptación sensorial se interpreta como proporción de demanda efectiva.
- Los escenarios optimista, esperado y pesimista modifican demanda, tiempos, desperdicio, costos y aceptación.
- Los resultados son estimaciones para apoyar decisiones, no predicciones exactas.

{_section_result("Simulador 1 - Envío simultáneo del formulario digital", queue, queue_interpretation)}

{_section_result("Simulador 2 - Stock de porciones", stock, stock_interpretation)}

{_section_result("Simulador 3 - Viabilidad productiva/comercial", viability, viability_interpretation)}

## Escenarios ejecutados

La aplicación permite ejecutar escenarios optimista, esperado y pesimista. Para presentación oral se recomienda mostrar primero el escenario esperado y luego contrastarlo con el pesimista para justificar medidas preventivas.

## Recomendaciones concretas para Nutrición

- Usar tandas de envío si se espera una concentración alta de comensales.
- Tener una alternativa de respaldo si el formulario no responde durante el pico.
- Preparar stock con margen de seguridad cuando la probabilidad de quiebre supere valores moderados.
- Registrar datos reales el día del testeo para recalibrar los supuestos antes de la entrega final.
- Comparar aceptación sensorial real contra la aceptación estimada para revisar viabilidad productiva.

## Limitaciones

- No se modelan fallos reales de conectividad ni comportamiento individual detallado.
- Los costos y precios son supuestos editables; deben reemplazarse por datos reales cuando estén disponibles.
- La aceptación sensorial se simplifica como una variable agregada.

## Posibles mejoras futuras

- Importar automáticamente resultados del formulario digital.
- Comparar simulación previa contra resultados reales posteriores al evento.
- Exportar gráficos e indicadores en formato PDF o DOCX.
- Incorporar segmentación por perfil de juez/comensal.
"""
    return report
