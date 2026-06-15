# VitaCookies - Analisis post-testeo

Herramienta Streamlit para analizar los resultados reales del testeo sensorial de VitaCookies.

Producto: galletita vegetal sustentable elaborada con avena, lentejas, manzana y zanahoria.

## Datos cargados

- 44 respuestas registradas en el formulario.
- Testeo realizado el 11/6/2026 entre 08:10 y 09:32.
- 50 galletitas producidas.
- 5 galletitas sobrantes aproximadas.
- 45 galletitas consumidas estimadas.
- 41 respuestas positivas sobre 42 respuestas de aceptabilidad.

## Objetivo academico

Apoyar la toma de decisiones despues del testeo sensorial mediante:

- analisis del flujo real del formulario;
- balance real de stock;
- indicadores de aceptacion;
- proyeccion deterministica de escala con costo de producir 50 galletitas;
- verificacion;
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

## Modulos

### 1. Flujo digital

Analiza respuestas reales por minuto, acumulado, pico observado y utilizacion maxima frente a una capacidad aceptable por minuto.

### 2. Stock de galletitas

Compara galletitas producidas, consumidas y sobrantes. Sugiere una cantidad para un proximo testeo similar.

### 3. Aceptabilidad y escala productiva

Usa la aceptabilidad real del formulario, 41 respuestas positivas sobre 42, y permite cargar el costo de producir 50 galletitas cuando este confirmado. Con ese unico costo, el precio unitario y una cantidad objetivo, proyecta costo unitario, ingresos, ganancia estimada y precio de equilibrio para producir a mayor escala.

## Informe automatico

La barra lateral permite descargar:

- informe Markdown;
- informe DOCX.

El informe resume resultados, interpretacion, recomendacion, decision sugerida y guia para defensa oral.
