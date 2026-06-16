# Documentacion tecnica y academica

## Enfoque metodologico post-testeo

La herramienta VitaCookies ahora trabaja con datos reales obtenidos durante el testeo sensorial. Se eliminaron corridas aleatorias, escenarios hipoteticos y probabilidades simuladas. El objetivo es transformar mediciones observadas en indicadores defendibles para la toma de decisiones.

## Analisis 1 - Flujo real del formulario digital

- **Sistema:** formulario digital respondido por evaluadores durante el testeo.
- **Objetivo:** medir carga real, duracion de recoleccion y pico por minuto.
- **Entidades:** evaluadores, respuestas, formulario digital, capacidad operativa.
- **Variables de estado:** respuestas por minuto, acumulado, utilizacion y minutos saturados.
- **Eventos:** envio real de cada respuesta.
- **Parametros:** respuestas registradas, duracion observada y capacidad aceptable por minuto.
- **Entrada:** 44 respuestas registradas entre 08:10 y 09:32.
- **Salida:** pico observado, utilizacion maxima y decision operativa.
- **Restricciones:** no registra fallas de red si no aparecen reflejadas en los datos.

## Analisis 2 - Stock real de galletitas

- **Sistema:** produccion y consumo de galletitas durante el testeo.
- **Objetivo:** medir consumo real y sobrante final.
- **Entidades:** galletitas producidas, galletitas consumidas, sobrantes y respuestas.
- **Variables de estado:** producidas, consumidas, sobrantes y porcentaje de sobrante.
- **Entrada:** 50 galletitas producidas y 5 sobrantes aproximadas.
- **Salida:** 45 consumidas estimadas, consumo porcentual y produccion sugerida para un proximo testeo similar.
- **Restricciones:** las sobrantes son aproximadas segun el dato informado por el equipo.

## Analisis 3 - Aceptabilidad y escala productiva

- **Sistema:** produccion a mayor escala usando la aceptabilidad real del testeo.
- **Objetivo:** proyectar costo, ingresos y ganancia para producir mas galletitas.
- **Entidades:** respuestas de aceptabilidad, galletitas a producir, costo fijo de 50 unidades, precio e ingresos.
- **Variables de estado:** aceptabilidad positiva, costo unitario estimado, produccion objetivo, ingresos y ganancia estimada.
- **Entrada:** 41 respuestas positivas sobre 50 galletitas testeadas, costo fijo de $15.000 cada 50 galletitas, precio unitario y cantidad objetivo.
- **Salida:** aceptabilidad positiva, unidades aceptadas estimadas, costo unitario, precio de equilibrio, precio recomendado y ganancia estimada.
- **Restricciones:** el costo se proyecta proporcionalmente; si cambia la escala real de compras o produccion, debe recalibrarse.

## Resultados sensoriales observados

- **Aceptabilidad positiva:** 41 de 50 galletitas testeadas.
- **Intencion de consumo diario o favorable:** 30 de 42 respuestas.
- **Preferencia frente a ultraprocesado:** 39 de 42 respuestas.
- **Color promedio:** 3.79 sobre 5.
- **Aroma promedio:** 3.32 sobre 5.
- **Sabor promedio:** 4.06 sobre 5.
- **Textura promedio:** 2.74 sobre 5.

## Verificacion

Se controla que:

- no haya cantidades negativas en las metricas operativas;
- los datos post-testeo esten cargados;
- no existan corridas aleatorias;
- el informe se genere con los resultados observados.

## Decision academica

El testeo muestra buena aceptabilidad general y un stock bien dimensionado. El principal punto de mejora esta en la textura/crocancia, mientras que el sabor aparece como el atributo mas fuerte. La decision economica depende de definir un precio unitario suficiente frente al costo fijo de $15.000 cada 50 galletitas.

## Defensa oral

La defensa debe enfocarse en:

1. explicar que la version actual es post-testeo;
2. mostrar los datos reales del formulario;
3. justificar el balance de stock con 50 producidas y 5 sobrantes;
4. destacar aceptacion positiva y preferencia frente a ultraprocesados;
5. proponer mejora de textura/crocancia;
6. explicar como el precio unitario y la escala determinan la viabilidad final frente al costo de $15.000 cada 50 galletitas.
