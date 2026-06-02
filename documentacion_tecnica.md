# Documentacion tecnica - Simuladores VitaCookies

## 1. Proposito del sistema

El sistema acompana el testeo sensorial de VitaCookies, una galletita vegetal sustentable elaborada con avena, lentejas, manzana y zanahoria. La herramienta permite simular escenarios antes y despues del evento para apoyar decisiones del equipo de Nutricion.

El proyecto no busca una prediccion exacta, sino un modelo claro, justificable y comunicable para la materia Modelos y Simulacion.

## 2. Arquitectura

La aplicacion separa interfaz y logica:

- `app.py`: interfaz Streamlit, controles, metricas, graficos y descargas.
- `simulators/queue_simulator.py`: modelo de carga simultanea del formulario digital.
- `simulators/stock_simulator.py`: modelo Montecarlo de stock.
- `simulators/viability_simulator.py`: modelo Montecarlo productivo/comercial.
- `utils/report_generator.py`: generacion de informe academico en Markdown.

Esta separacion facilita explicar los modelos y modificar supuestos sin tocar la interfaz.

## 3. Simulador de envio simultaneo del formulario digital

### Objetivo

Determinar si durante el evento el formulario digital puede saturarse por muchos envios simultaneos.

### Tipo de modelo

Simulacion de eventos discretos con llegadas aleatorias y carga concurrente del formulario.

### Supuestos

- Las llegadas se aproximan mediante un proceso de Poisson.
- Cada comensal puede usar su propio dispositivo.
- El cuello de botella digital no es la cantidad de celulares, sino la capacidad concurrente del formulario/servidor.
- El tiempo de carga del formulario es positivo y variable.

### Variables de entrada

- Tasa estimada de envios por hora.
- Duracion del evento.
- Capacidad del formulario en envios simultaneos.
- Tiempo promedio de carga del formulario.
- Escenario: optimista, esperado o pesimista.

### Variables de salida

- Envios simulados.
- Pico de carga del formulario.
- Momento del pico de carga.
- Minutos con saturacion digital.
- Porcentaje de tiempo saturado.
- Recomendacion operativa.

### Interpretacion

Si el pico de envios supera la capacidad del formulario, el riesgo esta en la carga digital y conviene escalonar los envios.

## 4. Simulador de stock de porciones

### Objetivo

Estimar si la cantidad de porciones preparadas alcanza para cubrir la demanda del testeo sensorial, considerando desperdicio y variabilidad.

### Tipo de modelo

Simulacion Montecarlo.

### Supuestos

- La cantidad de comensales reales puede desviarse de la cantidad esperada.
- No todos los comensales necesariamente prueban el producto.
- Existe desperdicio de proceso o servicio.
- La cantidad recomendada utiliza un percentil alto de demanda y un margen de seguridad.

### Variables de entrada

- Cantidad inicial de porciones.
- Cantidad esperada de comensales.
- Probabilidad de que cada comensal pruebe el producto.
- Porcentaje de desperdicio.
- Margen de seguridad.
- Cantidad de corridas.
- Escenario.

### Variables de salida

- Probabilidad de quiebre de stock.
- Demanda promedio y demanda alta estimada.
- Porciones faltantes promedio.
- Porciones sobrantes promedio.
- Desperdicio promedio.
- Porciones recomendadas.
- Estado: stock suficiente, stock ajustado o alto riesgo de quiebre.

### Interpretacion

Una probabilidad de quiebre baja indica que el stock es suficiente. Una probabilidad moderada indica stock ajustado. Una probabilidad alta justifica aumentar la produccion o planificar una reserva.

## 5. Simulador de viabilidad productiva/comercial

### Objetivo

Evaluar si VitaCookies podria ser viable productiva y comercialmente despues del testeo sensorial.

### Tipo de modelo

Simulacion Montecarlo de costos, demanda, desperdicio y aceptacion sensorial.

### Supuestos

- La aceptacion sensorial impacta en la demanda efectiva.
- El desperdicio reduce la cantidad vendible por lote.
- Los costos por lote pueden variar.
- El precio de venta se considera constante durante cada simulacion.
- Los costos fijos se recuperan mediante el margen de contribucion.

### Variables de entrada

- Costo por lote.
- Unidades por lote.
- Costos fijos.
- Desperdicio productivo.
- Precio de venta.
- Demanda esperada.
- Aceptacion sensorial esperada.
- Cantidad de corridas.
- Escenario.

### Variables de salida

- Costo unitario promedio.
- Demanda efectiva promedio.
- Punto de equilibrio.
- Ganancia promedio.
- Rango probable de ganancia.
- Probabilidad de rentabilidad.
- Estado: viable, parcialmente viable o no viable.

### Interpretacion

El producto se considera viable si la probabilidad de rentabilidad es alta y la ganancia esperada es positiva. Si la probabilidad es intermedia, se considera parcialmente viable y requiere ajustes. Si el margen es insuficiente o no se alcanza el punto de equilibrio, se considera no viable.

## 6. Escenarios

Los escenarios modifican los parametros de forma simple y defendible:

- **Optimista:** menor tiempo de atencion, menor desperdicio, mayor capacidad o mayor aceptacion.
- **Esperado:** valores base cargados por el usuario.
- **Pesimista:** mayor concentracion de demanda, mayor desperdicio, mayor costo o menor aceptacion.

Esta comparacion ayuda a comunicar riesgos durante la presentacion oral.

## 7. Validaciones

Los modelos aplican controles basicos:

- valores minimos positivos para tiempos, costos y capacidades;
- limites para probabilidades y porcentajes;
- recorte de valores simulados para evitar tiempos, demandas o porciones negativas;
- cantidad minima de corridas Montecarlo.

## 8. Limitaciones

- No se modelan comportamiento individual detallado ni fallas reales de conectividad.
- No se incorporan fallas reales de conectividad o caidas del servicio.
- La aceptacion sensorial se resume como una probabilidad agregada.
- Los costos deben reemplazarse por datos reales si el equipo de Nutricion los obtiene.

## 9. Mejoras futuras

- Importar resultados del formulario digital.
- Comparar automaticamente simulacion previa contra datos reales.
- Exportar informe en DOCX o PDF.
- Incorporar perfiles de comensales y segmentacion sensorial.
- Guardar historiales de escenarios para comparaciones entre clases.
