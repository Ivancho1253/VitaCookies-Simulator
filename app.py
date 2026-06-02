from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from simulators.queue_simulator import QueueInputs, simulate_queue, simulate_queue_scenarios
from simulators.stock_simulator import StockInputs, simulate_stock, simulate_stock_scenarios
from simulators.viability_simulator import (
    ViabilityInputs,
    simulate_viability,
    simulate_viability_scenarios,
)
from utils.report_generator import generate_markdown_report


st.set_page_config(
    page_title="VitaCookies | Simuladores",
    page_icon="🍪",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --vc-green: #2f6f4e;
            --vc-mint: #dcefe4;
            --vc-carrot: #e7893f;
            --vc-apple: #bf4e45;
            --vc-ink: #25342f;
            --vc-paper: #fffaf1;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(220, 239, 228, .95), transparent 34%),
                linear-gradient(135deg, #fffaf1 0%, #f7efe0 38%, #eef7ef 100%);
            color: var(--vc-ink);
        }
        header,
        [data-testid="stHeader"] {
            background: #0f1517 !important;
            color: #f7fff9 !important;
        }
        header *,
        [data-testid="stHeader"] *,
        [data-testid="stToolbar"] *,
        [data-testid="stStatusWidget"] * {
            color: #f7fff9 !important;
            fill: #f7fff9 !important;
            stroke: #f7fff9 !important;
        }
        #MainMenu,
        [data-testid="stDecoration"],
        [data-testid="stActionButton"],
        button[title="Deploy"],
        [aria-label="Deploy"] {
            display: none !important;
            visibility: hidden !important;
        }
        .stApp,
        .stApp p,
        .stApp span,
        .stApp label,
        .stApp div,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6 {
            color: var(--vc-ink);
        }
        [data-testid="stSidebar"] {
            background: #f7f2e8;
            border-right: 1px solid rgba(47, 111, 78, .16);
        }
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: #25342f !important;
        }
        .main .block-container { padding-top: 1.4rem; max-width: 1240px; }
        .hero {
            border: 1px solid rgba(47, 111, 78, .18);
            background: linear-gradient(135deg, rgba(255,250,241,.92), rgba(220,239,228,.82));
            border-radius: 18px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 16px 42px rgba(37, 52, 47, .08);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            color: var(--vc-green);
            font-size: clamp(2rem, 4vw, 3.4rem);
            letter-spacing: 0;
        }
        .hero p { margin: .5rem 0 0; font-size: 1.05rem; color: #465b53; max-width: 900px; }
        .pill-row { display: flex; gap: .5rem; flex-wrap: wrap; margin-top: 1rem; }
        .pill {
            border-radius: 999px;
            padding: .35rem .7rem;
            background: #ffffffb8;
            border: 1px solid rgba(47, 111, 78, .18);
            font-size: .86rem;
            color: #385149 !important;
        }
        .info-card {
            border-radius: 14px;
            padding: 1rem 1.1rem;
            background: rgba(255, 255, 255, .72);
            border: 1px solid rgba(47, 111, 78, .14);
            box-shadow: 0 10px 24px rgba(37, 52, 47, .06);
            min-height: 118px;
        }
        .info-card h3 { margin: 0 0 .35rem; color: var(--vc-green) !important; font-size: 1.02rem; }
        .info-card p { margin: 0; color: #52645e !important; font-size: .93rem; }
        .section-title {
            margin-top: 1rem;
            padding: .85rem 1rem;
            border-left: 6px solid var(--vc-carrot);
            background: rgba(255, 255, 255, .58);
            border-radius: 12px;
            color: var(--vc-ink) !important;
        }
        .section-title,
        .section-title strong,
        .section-title br {
            color: var(--vc-ink) !important;
        }
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, .76);
            border: 1px solid rgba(47, 111, 78, .14);
            border-radius: 14px;
            padding: .8rem .9rem;
            box-shadow: 0 8px 20px rgba(37, 52, 47, .05);
        }
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] * { color: #52645e !important; }
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * { color: var(--vc-green) !important; }
        .stTabs [data-baseweb="tab-list"] { gap: .35rem; }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,.62);
            border-radius: 999px;
            padding: .55rem 1rem;
            border: 1px solid rgba(47,111,78,.12);
            color: #25342f !important;
        }
        .stTabs [data-baseweb="tab"] * {
            color: #25342f !important;
        }
        .stTabs [aria-selected="true"] {
            background: var(--vc-green) !important;
            color: white !important;
        }
        .stTabs [aria-selected="true"] * {
            color: white !important;
        }
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] * {
            color: #25342f;
        }
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, .40);
            border-radius: 16px;
            padding: 1rem;
            border: 1px solid rgba(47, 111, 78, .10);
        }
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        [data-testid="stNumberInput"] label,
        [data-testid="stSelectbox"] label {
            color: #2f473d !important;
            font-weight: 650;
        }
        input,
        textarea,
        [data-baseweb="select"] div,
        [data-baseweb="input"] input {
            color: #f8fbf7 !important;
        }
        [data-baseweb="input"],
        [data-baseweb="select"] > div {
            background-color: #26302d !important;
            border-color: rgba(255, 255, 255, .24) !important;
        }
        button[kind="secondary"],
        .stButton button,
        .stDownloadButton button,
        .stLinkButton a {
            background: #ffffff !important;
            border: 1px solid rgba(47, 111, 78, .28) !important;
            color: #25342f !important;
        }
        button[kind="primary"],
        .stFormSubmitButton button {
            background: var(--vc-green) !important;
            border: 1px solid var(--vc-green) !important;
            color: #ffffff !important;
        }
        .stFormSubmitButton button *,
        button[kind="primary"] * {
            color: #ffffff !important;
        }
        button:disabled,
        button[disabled] {
            background: #e7eadf !important;
            color: #68766f !important;
            border-color: #d1d8cc !important;
            opacity: 1 !important;
        }
        button:disabled *,
        button[disabled] * {
            color: #68766f !important;
        }
        .stAlert,
        .stAlert * {
            color: #25342f !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    for key in ("queue_result", "stock_result", "viability_result"):
        st.session_state.setdefault(key, None)


def scenario_badge(text: str) -> None:
    st.caption(f"Escenario activo: {text}")


def show_recommendation(status: str, recommendation: str) -> None:
    if any(word in status.lower() for word in ["alto", "no viable", "riesgo", "satur"]):
        st.error(f"**{status}**. {recommendation}")
    elif any(word in status.lower() for word in ["ajustado", "parcial"]):
        st.warning(f"**{status}**. {recommendation}")
    else:
        st.success(f"**{status}**. {recommendation}")


def render_intro() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>VitaCookies</h1>
            <p>Simuladores para anticipar carga del formulario digital, stock y viabilidad de galletitas vegetales sustentables en el testeo sensorial con Nutrición.</p>
            <div class="pill-row">
                <span class="pill">Avena</span>
                <span class="pill">Lentejas</span>
                <span class="pill">Manzana</span>
                <span class="pill">Zanahoria</span>
                <span class="pill">Formulario digital</span>
                <span class="pill">Modelos y Simulación</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="info-card"><h3>💻 Formulario digital</h3><p>Evalúa si los envíos simultáneos pueden saturar la carga del formulario.</p></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="info-card"><h3>📦 Stock de porciones</h3><p>Estima faltantes, sobrantes y cantidad recomendada con Montecarlo.</p></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="info-card"><h3>📈 Viabilidad</h3><p>Combina costos, demanda y aceptación sensorial para decidir si conviene escalar.</p></div>',
            unsafe_allow_html=True,
        )


def render_data_guidance() -> None:
    with st.expander("¿De dónde salen los datos de probabilidad, desperdicio y aceptación?"):
        st.markdown(
            """
            Estos valores son **supuestos del modelo** antes del testeo y se reemplazan por **datos reales** después del evento.

            - **Probabilidad de que un comensal pruebe:** antes del evento se estima según convocatoria y accesibilidad del stand. Después se calcula como `personas que probaron / personas que asistieron`.
            - **Porcentaje de desperdicio:** antes se estima por pruebas de cocina, porciones rotas, sobrantes no servibles o pérdidas de preparación. Después se calcula como `porciones perdidas / porciones preparadas`.
            - **Aceptación sensorial:** antes se usa una hipótesis, por ejemplo 0.65 a 0.75. Después se calcula desde el formulario: porcentaje de respuestas positivas, intención de consumo o promedio normalizado de agrado.
            - **Demanda esperada:** antes surge de invitados esperados, difusión y horario. Después se ajusta con asistentes reales y respuestas cargadas.
            - **Capacidad del formulario:** si el formulario está alojado en una plataforma web, se estima de forma conservadora. Para la defensa, lo importante es evaluar el riesgo de muchos envíos en el mismo minuto, no conocer el servidor exacto.

            Para la entrega: usá el escenario **Esperado** con los supuestos más razonables y el **Pesimista** para justificar medidas preventivas.
            """
        )


def render_report_download() -> None:
    report = generate_markdown_report(
        {
            "queue": st.session_state.queue_result,
            "stock": st.session_state.stock_result,
            "viability": st.session_state.viability_result,
        }
    )
    st.download_button(
        "Generar informe Markdown",
        data=report,
        file_name="informe_tecnico_vitacookies.md",
        mime="text/markdown",
        use_container_width=True,
    )


def render_queue_tab(seed: int) -> None:
    st.markdown(
        '<div class="section-title"><strong>Simulador 1: envío simultáneo del formulario digital</strong><br>Estima si muchos comensales cargando el formulario al mismo tiempo pueden superar la capacidad de respuesta del sistema.</div>',
        unsafe_allow_html=True,
    )
    with st.form("queue_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            arrival_rate = st.number_input("Tasa estimada de envíos (personas/hora)", 1.0, 500.0, 55.0, 5.0)
            duration = st.number_input("Duración del evento (min)", 10, 360, 90, 5)
        with col2:
            form_time = st.number_input("Tiempo promedio de carga del formulario (min)", 0.5, 30.0, 3.0, 0.5)
            server_capacity = st.number_input("Capacidad estimada de envíos simultáneos", 1, 500, 45, 5)
        with col3:
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1)
            submitted = st.form_submit_button("Ejecutar simulación digital")

    if submitted:
        inputs = QueueInputs(
            arrival_rate_per_hour=arrival_rate,
            event_duration_min=duration,
            server_capacity=server_capacity,
            avg_form_time_min=form_time,
            scenario=scenario,
            seed=seed,
        )
        result = simulate_queue(inputs)
        result["scenario_table"] = simulate_queue_scenarios(inputs)
        st.session_state.queue_result = result

    result = st.session_state.queue_result
    if not result:
        st.info("Cargá los parámetros y ejecutá el simulador para ver pico de carga, saturación y recomendación.")
        return

    metrics = result["metrics"]
    scenario_badge(scenario if "scenario" in locals() else "última ejecución")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Envíos simulados", f"{metrics['personas_simuladas']}")
    k2.metric("Pico simultáneo", f"{metrics['pico_carga_formulario']}")
    k3.metric("Capacidad estimada", f"{metrics['capacidad_formulario_ajustada']}")
    k4.metric("Minutos saturados", f"{metrics['minutos_saturados_formulario']}")
    k5.metric("Tiempo saturado", f"{metrics['porcentaje_tiempo_saturado']:.1f}%")

    c1, c2 = st.columns([1.3, 1])
    with c1:
        timeline = result["timeline"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timeline["minuto"], y=timeline["envios_formulario_activos"], name="Formulario activo", line=dict(color="#2f6f4e", width=3)))
        fig.add_trace(go.Scatter(x=timeline["minuto"], y=timeline["capacidad_formulario"], name="Capacidad formulario", line=dict(color="#e7893f", dash="dash")))
        fig.update_layout(title="Evolución temporal de envíos simultáneos", xaxis_title="Minuto", yaxis_title="Envíos activos", template="plotly_white", height=390)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        submissions = result["people"]
        fig = px.histogram(submissions, x="tiempo_carga_formulario_min", nbins=18, title="Distribución del tiempo de carga", color_discrete_sequence=["#2f6f4e"])
        fig.update_layout(template="plotly_white", xaxis_title="Minutos", yaxis_title="Envíos", height=390)
        st.plotly_chart(fig, use_container_width=True)

    show_recommendation(metrics["estado_general"], metrics["recomendacion"])
    st.caption(f"Pico estimado en el minuto {metrics['pico_carga_min']:.0f}.")
    fig = px.bar(result["scenario_table"], x="escenario", y=["pico_formulario", "capacidad", "minutos_saturados"], barmode="group", title="Comparación rápida entre escenarios")
    fig.update_layout(template="plotly_white", yaxis_title="Valor")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Ver datos simulados"):
        st.dataframe(result["people"].round(2), use_container_width=True)


def render_stock_tab(seed: int) -> None:
    st.markdown(
        '<div class="section-title"><strong>Simulador 2: stock de porciones</strong><br>Montecarlo para estimar quiebre de stock, sobrantes, faltantes, desperdicio y cantidad mínima recomendada.</div>',
        unsafe_allow_html=True,
    )
    with st.form("stock_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            initial = st.number_input("Cantidad inicial de porciones", 1, 5000, 80, 5)
            diners = st.number_input("Cantidad esperada de comensales", 1, 5000, 90, 5)
        with col2:
            trial_probability = st.slider("Probabilidad de que cada comensal pruebe", 0.0, 1.0, 0.75, 0.01)
            waste = st.slider("Porcentaje de desperdicio", 0.0, 0.60, 0.06, 0.01)
            safety = st.slider("Margen de seguridad", 0.0, 0.80, 0.12, 0.01)
        with col3:
            runs = st.number_input("Cantidad de corridas", 100, 100000, 8000, 500)
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="stock_scenario")
            submitted = st.form_submit_button("Ejecutar simulación de stock")

    if submitted:
        inputs = StockInputs(initial, diners, trial_probability, waste, safety, runs, scenario, seed + 100)
        result = simulate_stock(inputs)
        result["scenario_table"] = simulate_stock_scenarios(inputs)
        st.session_state.stock_result = result

    result = st.session_state.stock_result
    if not result:
        st.info("Ejecutá el simulador para estimar riesgo de quiebre y porciones recomendadas.")
        return

    metrics = result["metrics"]
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Prob. de quiebre", f"{metrics['probabilidad_quiebre_pct']:.1f}%")
    k2.metric("Demanda promedio", f"{metrics['demanda_promedio']:.1f}")
    k3.metric("Faltante prom.", f"{metrics['porciones_faltantes_prom']:.1f}")
    k4.metric("Sobrante prom.", f"{metrics['porciones_sobrantes_prom']:.1f}")
    k5.metric("Porciones recomendadas", f"{metrics['porciones_recomendadas']}")

    c1, c2 = st.columns(2)
    simulations = result["simulations"]
    with c1:
        fig = px.histogram(simulations, x="demanda_porciones", nbins=28, title="Distribución de demanda de porciones", color_discrete_sequence=["#2f6f4e"])
        fig.update_layout(template="plotly_white", xaxis_title="Porciones demandadas", yaxis_title="Frecuencia")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(simulations, x="porciones_sobrantes", nbins=28, title="Distribución de sobrantes", color_discrete_sequence=["#e7893f"])
        fig.update_layout(template="plotly_white", xaxis_title="Porciones sobrantes", yaxis_title="Frecuencia")
        st.plotly_chart(fig, use_container_width=True)

    show_recommendation(metrics["estado"], metrics["recomendacion"])
    fig = px.bar(result["scenario_table"], x="escenario", y=["prob_quiebre_pct", "recomendadas"], barmode="group", title="Stock: comparación entre escenarios")
    fig.update_layout(template="plotly_white", yaxis_title="Valor")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Resumen estadístico"):
        st.dataframe(simulations.describe().T.round(2), use_container_width=True)


def render_viability_tab(seed: int) -> None:
    st.markdown(
        '<div class="section-title"><strong>Simulador 3: viabilidad productiva/comercial</strong><br>Montecarlo para analizar costo unitario, punto de equilibrio, ganancia esperada y probabilidad de rentabilidad.</div>',
        unsafe_allow_html=True,
    )
    with st.form("viability_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            batch_cost = st.number_input("Costo por lote ($)", 1.0, 10_000_000.0, 4500.0, 100.0)
            units_per_batch = st.number_input("Unidades por lote", 1, 10000, 50, 5)
            fixed_cost = st.number_input("Costos fijos estimados ($)", 0.0, 10_000_000.0, 15000.0, 500.0)
        with col2:
            waste = st.slider("Desperdicio productivo", 0.0, 0.70, 0.08, 0.01)
            sale_price = st.number_input("Precio de venta estimado ($)", 1.0, 100000.0, 180.0, 10.0)
            demand = st.number_input("Demanda esperada", 1, 100000, 300, 10)
        with col3:
            acceptance = st.slider("Aceptación sensorial esperada", 0.0, 1.0, 0.70, 0.01)
            runs = st.number_input("Corridas Montecarlo", 100, 100000, 8000, 500, key="viab_runs")
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="viab_scenario")
            submitted = st.form_submit_button("Ejecutar simulación de viabilidad")

    if submitted:
        inputs = ViabilityInputs(batch_cost, units_per_batch, fixed_cost, waste, sale_price, demand, acceptance, runs, scenario, seed + 200)
        result = simulate_viability(inputs)
        result["scenario_table"] = simulate_viability_scenarios(inputs)
        st.session_state.viability_result = result

    result = st.session_state.viability_result
    if not result:
        st.info("Ejecutá el simulador para estimar rentabilidad y punto de equilibrio.")
        return

    metrics = result["metrics"]
    break_even = metrics["punto_equilibrio_unidades"]
    break_even_text = "No alcanzable" if break_even == float("inf") else f"{break_even:.0f}"
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Prob. rentable", f"{metrics['probabilidad_rentabilidad_pct']:.1f}%")
    k2.metric("Ganancia prom.", f"${metrics['ganancia_promedio']:,.0f}")
    k3.metric("Costo unitario", f"${metrics['costo_unitario_prom']:,.2f}")
    k4.metric("Punto equilibrio", break_even_text)
    k5.metric("Demanda efectiva", f"{metrics['demanda_efectiva_prom']:.1f}")

    simulations = result["simulations"]
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(simulations, x="ganancia", nbins=32, title="Distribución de ganancia", color_discrete_sequence=["#2f6f4e"])
        fig.add_vline(x=0, line_dash="dash", line_color="#bf4e45")
        fig.update_layout(template="plotly_white", xaxis_title="Ganancia ($)", yaxis_title="Frecuencia")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(simulations.sample(min(600, len(simulations)), random_state=7), x="demanda_efectiva", y="ganancia", color="aceptacion_sensorial", title="Ganancia según demanda efectiva", color_continuous_scale=["#bf4e45", "#e7893f", "#2f6f4e"])
        fig.update_layout(template="plotly_white", xaxis_title="Demanda efectiva", yaxis_title="Ganancia ($)")
        st.plotly_chart(fig, use_container_width=True)

    show_recommendation(metrics["estado"], metrics["recomendacion"])
    fig = px.bar(result["scenario_table"], x="escenario", y=["prob_rentabilidad_pct", "ganancia_promedio", "costo_unitario"], barmode="group", title="Viabilidad: comparación entre escenarios")
    fig.update_layout(template="plotly_white", yaxis_title="Valor")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Resumen estadístico"):
        st.dataframe(simulations.describe().T.round(2), use_container_width=True)


def main() -> None:
    inject_style()
    init_state()
    render_intro()
    render_data_guidance()

    with st.sidebar:
        st.title("Panel de simulación")
        st.caption("Proyecto intercátedra ISI + Nutrición")
        seed = st.number_input("Semilla aleatoria", 0, 999999, 42, 1)
        st.link_button("Abrir formulario digital", "https://vita-cookies-form-v.vercel.app/", use_container_width=True)
        st.divider()
        render_report_download()
        st.caption("El informe usa los últimos resultados ejecutados en cada simulador.")

    tab1, tab2, tab3 = st.tabs(
        [
            "💻 Formulario digital",
            "📦 Stock de porciones",
            "📈 Viabilidad comercial",
        ]
    )
    with tab1:
        render_queue_tab(seed)
    with tab2:
        render_stock_tab(seed)
    with tab3:
        render_viability_tab(seed)

    st.divider()
    st.caption("VitaCookies | Modelos y Simulación | Herramienta de apoyo para el testeo sensorial del 09/06 y análisis posterior del 19/06.")


if __name__ == "__main__":
    main()
