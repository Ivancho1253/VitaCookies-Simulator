# VitaCookies - Simuladores academicos de Modelos y Simulacion

Herramienta Streamlit para la evaluacion integradora intercatedra entre Ingenieria en Sistemas y Nutricion.

Producto: galletita vegetal sustentable elaborada con avena, lentejas, manzana y zanahoria.

## Objetivo academico

Apoyar la toma de decisiones antes y despues del testeo sensorial mediante:

- simulacion de eventos discretos;
- simulacion Monte Carlo;
- analisis de escenarios;
- analisis de sensibilidad;
- verificacion;
- validacion posterior con datos reales;
- informe academico automatico.

## Instalacion

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion

```bash
streamlit run app.py
```

## Simuladores

### 1. Flujo de personas y formulario digital

Modelo: simulacion de eventos discretos.

Evalua llegada de personas, degustacion, tiempo para completar/enviar formulario, concurrencia y saturacion del sistema.

Decision que ayuda a tomar: si conviene escalonar envios, reforzar el formulario o preparar respaldo.

### 2. Stock de porciones

Modelo: Monte Carlo.

Evalua demanda variable, desperdicio, asistencia y probabilidad de consumo.

Decision que ayuda a tomar: cuantas porciones preparar para evitar quiebre sin generar desperdicio excesivo.

### 3. Viabilidad productiva/comercial

Modelo: Monte Carlo economico.

Evalua demanda, aceptacion sensorial, costos, desperdicio, precio y rentabilidad.

Decision que ayuda a tomar: si el producto es viable, parcialmente viable o no viable.

## Escenarios

Cada simulador incluye:

- Optimista;
- Esperado;
- Pesimista.

Los escenarios modifican parametros reales del modelo, no son solo etiquetas visuales.

## Verificacion

La app verifica:

- ausencia de tiempos negativos;
- ausencia de cantidades negativas;
- probabilidades validas;
- costos no negativos;
- respuesta frente a cambios de parametros.

## Validacion

Despues del evento se comparan:

- asistentes simulados vs reales;
- tiempos de formulario;
- picos de carga;
- porciones consumidas;
- desperdicio real;
- aceptacion sensorial real;
- costos reales.

Con esos datos se recalibran los parametros y se ejecuta la simulacion posterior.

## Informe automatico

La barra lateral permite descargar:

- informe Markdown;
- informe DOCX.

Incluye portada, modelos, entidades, variables, eventos, supuestos, resultados, interpretacion, recomendaciones, limitaciones, mejoras futuras y guia de defensa oral.

## Guia para defensa oral

1. Explicar el problema de cada simulador.
2. Indicar el tipo de modelo usado.
3. Mostrar escenarios y sensibilidad.
4. Presentar resultado, interpretacion y decision.
5. Explicar como se validara con datos reales del testeo.

