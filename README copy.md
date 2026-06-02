# VitaCookies - Simuladores para testeo sensorial

Herramienta Streamlit para apoyar el proyecto integrador entre Ingenieria en Sistemas y Nutricion. El producto analizado es **VitaCookies**, galletitas vegetales sustentables elaboradas con avena, lentejas, manzana y zanahoria.

La app permite anticipar riesgos antes del evento, cargar supuestos realistas y generar recomendaciones para el equipo de Nutricion.

Formulario digital de referencia: https://vita-cookies-form-v.vercel.app/

## Estructura del proyecto

```text
vitacookies_simuladores/
├── app.py
├── simulators/
│   ├── queue_simulator.py
│   ├── stock_simulator.py
│   └── viability_simulator.py
├── utils/
│   └── report_generator.py
├── requirements.txt
├── README.md
└── documentacion_tecnica.md
```

## Instalacion

Crear y activar un entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
streamlit run app.py
```

Luego abrir la URL local que muestra Streamlit, normalmente:

```text
http://localhost:8501
```

## Simuladores incluidos

### 1. Envio simultaneo del formulario digital

Modelo de eventos discretos. Evalua si muchos comensales cargando el formulario al mismo tiempo pueden superar la capacidad estimada del sistema.

Entradas principales:

- tasa estimada de envios;
- duracion del evento;
- capacidad del formulario en envios simultaneos;
- tiempo promedio de carga del formulario.

Salidas:

- envios simulados;
- pico de carga digital;
- minutos saturados;
- porcentaje de tiempo saturado;
- recomendacion operativa.

### 2. Stock de porciones

Modelo Montecarlo para estimar demanda, faltantes, sobrantes y desperdicio.

Entradas principales:

- porciones iniciales;
- comensales esperados;
- probabilidad de prueba;
- porcentaje de desperdicio;
- margen de seguridad;
- cantidad de corridas.

Salidas:

- probabilidad de quedarse sin porciones;
- porciones faltantes;
- porciones sobrantes;
- demanda estimada;
- cantidad recomendada de porciones.

### 3. Viabilidad productiva/comercial

Modelo Montecarlo para analizar si el producto podria escalarse despues del testeo sensorial.

Entradas principales:

- costo por lote;
- unidades por lote;
- desperdicio productivo;
- precio de venta;
- demanda esperada;
- aceptacion sensorial;
- costos fijos.

Salidas:

- costo unitario;
- punto de equilibrio;
- ganancia esperada;
- probabilidad de rentabilidad;
- recomendacion: viable, parcialmente viable o no viable.

## Escenarios

Cada simulador permite trabajar con tres escenarios:

- **Optimista:** menor riesgo operativo, menor desperdicio o mejor aceptacion.
- **Esperado:** comportamiento base.
- **Pesimista:** mayor demanda concentrada, mayor desperdicio, mayor costo o menor aceptacion.

Para una presentacion oral conviene mostrar el escenario esperado y luego contrastarlo con el pesimista para justificar acciones preventivas.

## Informe tecnico

En la barra lateral hay un boton **Generar informe Markdown**. El informe descargable incluye:

- titulo del proyecto;
- descripcion general;
- objetivos de cada simulador;
- modelos usados;
- variables de entrada y salida;
- supuestos;
- escenarios;
- resultados principales;
- interpretacion;
- recomendaciones para Nutricion;
- limitaciones y mejoras futuras.

El informe usa los ultimos resultados ejecutados en cada simulador. Si un simulador no fue ejecutado, queda indicado en el documento.

## Uso para la presentacion del 09/06

Antes del testeo sensorial:

- cargar valores estimados de llegada, stock, tiempos y aceptacion esperada;
- ejecutar escenarios esperado y pesimista;
- registrar capturas de KPIs y graficos;
- generar el informe Markdown como respaldo academico;
- proponer medidas concretas: tandas de formulario, respaldo digital y porciones recomendadas.

## Uso para la presentacion del 19/06

Despues del testeo sensorial:

- reemplazar supuestos por datos reales obtenidos en el evento;
- comparar lo previsto contra lo observado;
- recalibrar parametros de demanda, desperdicio y aceptacion;
- usar los resultados para recomendar mejoras productivas y comerciales.

## Interpretacion rapida

- Si el pico de carga supera la capacidad del formulario, conviene usar tandas de envio.
- Si la probabilidad de quiebre de stock supera 15%, el stock es riesgoso.
- Si la probabilidad de rentabilidad queda por debajo de 40%, no conviene escalar sin ajustar costos, precio o aceptacion.
