# Documentacion tecnica y academica

## Enfoque metodologico

El proyecto VitaCookies utiliza modelos de simulacion para apoyar decisiones de Nutricion antes y despues de un testeo sensorial. La herramienta no busca certeza absoluta, sino comparar escenarios bajo incertidumbre.

## Simulador 1 - Flujo de personas y formulario digital

- **Sistema:** evento sensorial con comensales que degustan y completan un formulario digital.
- **Objetivo:** estimar saturacion por envios simultaneos.
- **Entidades:** comensales, formulario, servidor/capacidad concurrente.
- **Variables de estado:** formularios activos, utilizacion, minutos saturados.
- **Eventos:** llegada, fin de degustacion, inicio de formulario, envio.
- **Parametros:** tasa de llegada, duracion, tiempos promedio, capacidad.
- **Entrada:** escenario y parametros operativos.
- **Salida:** probabilidad de saturacion, pico, minuto pico, utilizacion y decision.
- **Supuestos:** cada persona usa su propio celular.
- **Restricciones:** no se modelan fallas reales de red.
- **Alcance:** apoyo operativo al evento.

## Simulador 2 - Stock de porciones

- **Sistema:** inventario de porciones.
- **Objetivo:** estimar quiebre y stock recomendado.
- **Entidades:** comensales, porciones, demanda, desperdicio.
- **Variables de estado:** porciones utiles, faltantes, sobrantes.
- **Eventos:** asistencia, decision de probar, consumo, desperdicio.
- **Modelo:** Monte Carlo.
- **Salida:** probabilidad de quiebre, percentiles, sobrantes, faltantes y recomendacion.

## Simulador 3 - Viabilidad productiva/comercial

- **Sistema:** produccion y venta potencial.
- **Objetivo:** estimar rentabilidad preliminar.
- **Entidades:** lotes, unidades, demanda, consumidores, costos.
- **Variables de estado:** costo total, ingresos, ganancia.
- **Eventos:** produccion, desperdicio, venta.
- **Modelo:** Monte Carlo.
- **Salida:** costo unitario, punto de equilibrio, ganancia, probabilidad rentable.

## Escenarios

Los escenarios modifican parametros:

- **Optimista:** menor riesgo, menor desperdicio, mejor aceptacion o mayor capacidad.
- **Esperado:** supuestos base.
- **Pesimista:** mayor demanda concentrada, mayor desperdicio, mayores costos o menor aceptacion.

## Analisis de sensibilidad

Permite identificar que variable afecta mas el resultado:

- tasa de envios y capacidad para formulario;
- probabilidad de prueba y desperdicio para stock;
- precio, costos, aceptacion y desperdicio para viabilidad.

## Verificacion

Se controla que:

- no haya tiempos negativos;
- no haya cantidades negativas;
- las probabilidades esten entre 0 y 1;
- los costos no sean negativos;
- el modelo responda ante cambios de parametros.

## Validacion

La validacion se realiza luego del testeo sensorial. Se comparan resultados simulados contra datos reales:

- asistencia real;
- tiempo real de formulario;
- consumo real;
- desperdicio real;
- aceptacion sensorial real;
- costos reales.

Con esos datos se recalibran los modelos y se ejecuta una simulacion posterior.

## Limitaciones

- No se modelan preferencias individuales completas.
- La capacidad del formulario es una estimacion si no hay medicion tecnica.
- La aceptacion sensorial se resume como variable agregada.

## Defensa oral

La defensa debe enfocarse en:

1. problema que resuelve cada simulador;
2. modelo usado;
3. escenarios;
4. sensibilidad;
5. decision sugerida para Nutricion;
6. validacion posterior con datos reales.

