from __future__ import annotations

from html import escape

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from simulators.digital_flow_simulator import (
    DigitalFlowInputs,
    scenario_comparison as digital_scenarios,
    sensitivity_analysis as digital_sensitivity,
    simulate_digital_flow,
    verification_checks as digital_verification,
)
from simulators.stock_simulator import (
    StockInputs,
    scenario_comparison as stock_scenarios,
    sensitivity_analysis as stock_sensitivity,
    simulate_stock,
    verification_checks as stock_verification,
)
from simulators.viability_simulator import (
    ViabilityInputs,
    critical_variables,
    improvement_impacts,
    scenario_comparison as viability_scenarios,
    sensitivity_analysis as viability_sensitivity,
    simulate_viability,
    verification_checks as viability_verification,
)
from utils.report_generator import MODEL_CARDS, generate_docx_report, generate_markdown_report


st.set_page_config(page_title="VitaCookies | Modelos y Simulacion", page_icon="🍪", layout="wide")
px.defaults.color_discrete_sequence = ["#1f7a5a", "#e07a3f", "#3f6fb5", "#b94d57", "#8a6f34"]
px.defaults.template = "plotly_white"


def css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink:#18231f;
            --muted:#5d6d66;
            --surface:#ffffff;
            --surface-soft:#f5f3ec;
            --line:#d8ded3;
            --leaf:#1f7a5a;
            --leaf-dark:#13543d;
            --carrot:#e07a3f;
            --tomato:#b94d57;
            --blue:#3f6fb5;
            --gold:#9c7a2e;
            --shadow: 0 18px 45px rgba(32, 44, 38, .12);
        }
        header, [data-testid="stHeader"] {
            background:#101817 !important;
            color:#f5fff9 !important;
            border-bottom:1px solid rgba(255,255,255,.08);
        }
        header *, [data-testid="stHeader"] *, [data-testid="stToolbar"] * {
            color:#f5fff9 !important; fill:#f5fff9 !important; stroke:#f5fff9 !important;
        }
        #MainMenu, [data-testid="stDecoration"], button[title="Deploy"], [aria-label="Deploy"] {
            display:none !important;
        }
        .stApp {
            background:
                linear-gradient(180deg, rgba(255,255,255,.76), rgba(255,255,255,.28)),
                linear-gradient(135deg, #f2f7ef 0%, #fff8ec 42%, #edf3f8 100%);
            color:var(--ink);
        }
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3 {
            color:var(--ink);
            letter-spacing:0;
        }
        .main .block-container {
            max-width:1320px;
            padding:1.7rem 2.2rem 3rem;
        }
        [data-testid="stSidebar"] {
            background:#111b18;
            border-right:1px solid rgba(255,255,255,.08);
        }
        [data-testid="stSidebar"] * {
            color:#edf8f1 !important;
        }
        [data-testid="stSidebar"] [data-testid="stNumberInput"] label,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
            color:#bed7ca !important;
        }
        [data-testid="stSidebar"] [data-baseweb="input"] {
            background:#0c1211 !important;
            border:1px solid rgba(255,255,255,.16) !important;
        }
        [data-testid="stSidebar"] .stDownloadButton button,
        [data-testid="stSidebar"] .stLinkButton a {
            background:#eff7ef !important;
            color:#10201a !important;
            border:1px solid rgba(255,255,255,.18) !important;
            border-radius:10px !important;
            font-weight:700 !important;
        }
        .hero {
            position:relative;
            overflow:hidden;
            border:1px solid rgba(31,122,90,.18);
            border-radius:22px;
            padding:1.75rem 1.9rem;
            background:
                linear-gradient(120deg, rgba(18,84,61,.94) 0%, rgba(31,122,90,.90) 44%, rgba(224,122,63,.92) 100%);
            box-shadow:var(--shadow);
            margin-bottom:1rem;
        }
        .hero::after {
            content:"";
            position:absolute;
            right:-60px;
            top:-70px;
            width:260px;
            height:260px;
            border-radius:50%;
            border:38px solid rgba(255,255,255,.12);
        }
        .hero-inner {
            position:relative;
            z-index:1;
            max-width:980px;
        }
        .eyebrow {
            display:inline-flex;
            align-items:center;
            gap:.45rem;
            padding:.34rem .7rem;
            border-radius:999px;
            background:rgba(255,255,255,.14);
            color:#f4fff8 !important;
            border:1px solid rgba(255,255,255,.22);
            font-size:.82rem;
            font-weight:750;
            text-transform:uppercase;
        }
        .hero h1 {
            margin:.65rem 0 .25rem;
            color:#ffffff !important;
            font-size:clamp(2.35rem,5vw,4.4rem);
            line-height:1;
            font-weight:850;
        }
        .hero p {
            color:#f3fff5 !important;
            max-width:920px;
            font-size:1.08rem;
            line-height:1.55;
            margin:.5rem 0 0;
        }
        .hero-meta {
            display:flex;
            gap:.65rem;
            flex-wrap:wrap;
            margin-top:1.15rem;
        }
        .hero-chip {
            background:rgba(255,255,255,.92);
            color:#183029 !important;
            border:1px solid rgba(255,255,255,.36);
            border-radius:999px;
            padding:.42rem .72rem;
            font-weight:700;
            font-size:.86rem;
        }
        .card {
            background:rgba(255,255,255,.82);
            border:1px solid rgba(25,45,37,.10);
            border-radius:16px;
            padding:1.05rem 1.05rem 1rem;
            min-height:132px;
            box-shadow:0 12px 30px rgba(32,44,38,.08);
        }
        .card h3 {
            color:var(--leaf-dark) !important;
            margin:.15rem 0 .48rem;
            font-size:1.02rem;
            font-weight:820;
        }
        .card p {
            color:var(--muted) !important;
            margin:0;
            line-height:1.45;
            font-size:.94rem;
        }
        .card-kicker {
            display:inline-grid;
            place-items:center;
            width:34px;
            height:34px;
            margin-bottom:.55rem;
            border-radius:10px;
            background:#e9f4ec;
            color:var(--leaf-dark) !important;
            font-weight:900;
        }
        .model-box {
            background:rgba(255,255,255,.82);
            border:1px solid rgba(25,45,37,.10);
            border-left:7px solid var(--carrot);
            border-radius:16px;
            padding:1rem 1.05rem;
            margin:.9rem 0 1rem;
            box-shadow:0 10px 25px rgba(32,44,38,.06);
        }
        .model-box strong {
            color:#17372c !important;
            font-size:1.05rem;
        }
        .model-box br {
            display:block;
            margin:.2rem 0;
        }
        .decision-grid {
            display:grid;
            grid-template-columns:repeat(4, minmax(0, 1fr));
            gap:.8rem;
            margin:.3rem 0 1rem;
        }
        .decision-card {
            background:#fff;
            border:1px solid rgba(25,45,37,.12);
            border-radius:16px;
            padding:1rem;
            box-shadow:0 12px 26px rgba(32,44,38,.07);
            min-height:132px;
        }
        .decision-card .label {
            color:#6a756f !important;
            text-transform:uppercase;
            font-size:.74rem;
            font-weight:850;
            margin-bottom:.45rem;
        }
        .decision-card .body {
            color:#21332d !important;
            line-height:1.38;
            font-weight:560;
        }
        .decision-card.result { border-top:5px solid var(--blue); }
        .decision-card.interpretation { border-top:5px solid var(--gold); }
        .decision-card.recommendation { border-top:5px solid var(--carrot); }
        .decision-card.decision { border-top:5px solid var(--leaf); }
        [data-testid="stMetric"] {
            background:#ffffff;
            border-radius:16px;
            padding:1rem;
            border:1px solid rgba(25,45,37,.10);
            box-shadow:0 10px 24px rgba(32,44,38,.07);
        }
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"] * {
            color:var(--leaf-dark) !important;
        }
        div[data-testid="stMetricValue"] * {
            font-weight:850 !important;
        }
        [data-testid="stForm"] {
            background:rgba(255,255,255,.78);
            border-radius:18px;
            padding:1.1rem;
            border:1px solid rgba(25,45,37,.10);
            box-shadow:0 12px 32px rgba(32,44,38,.07);
        }
        [data-testid="stWidgetLabel"] * {
            color:#31463d !important;
            font-weight:760;
        }
        [data-baseweb="input"],
        [data-baseweb="select"] > div {
            background:#ffffff !important;
            border-color:#cbd8cf !important;
            border-radius:10px !important;
        }
        input,
        [data-baseweb="select"] div {
            color:#13231d !important;
            font-weight:650 !important;
        }
        .stFormSubmitButton button {
            background:linear-gradient(135deg, var(--leaf) 0%, var(--leaf-dark) 100%) !important;
            color:white !important;
            border:1px solid var(--leaf-dark) !important;
            border-radius:12px !important;
            font-weight:850 !important;
            min-height:2.75rem;
            box-shadow:0 10px 22px rgba(31,122,90,.22);
        }
        .stButton button,
        .stDownloadButton button,
        .stLinkButton a {
            background:#ffffff !important;
            color:#183029 !important;
            border:1px solid rgba(31,122,90,.25) !important;
            border-radius:12px !important;
            font-weight:760 !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap:.5rem;
            background:rgba(255,255,255,.58);
            border:1px solid rgba(25,45,37,.10);
            padding:.42rem;
            border-radius:16px;
            box-shadow:0 10px 24px rgba(32,44,38,.06);
        }
        .stTabs [data-baseweb="tab"] {
            background:transparent;
            border-radius:12px;
            color:#263a33 !important;
            padding:.62rem .95rem;
            font-weight:780;
        }
        .stTabs [data-baseweb="tab"] * {
            color:#263a33 !important;
        }
        .stTabs [aria-selected="true"] {
            background:#163d30 !important;
        }
        .stTabs [aria-selected="true"] * {
            color:#ffffff !important;
        }
        .stAlert {
            border-radius:14px;
            border:1px solid rgba(25,45,37,.12);
        }
        .stAlert * {
            color:#25342f !important;
        }
        [data-testid="stExpander"] {
            background:rgba(255,255,255,.68);
            border:1px solid rgba(25,45,37,.10);
            border-radius:14px;
            box-shadow:0 8px 20px rgba(32,44,38,.05);
        }
        [data-testid="stDataFrame"] {
            border-radius:14px;
            overflow:hidden;
        }
        @media (max-width: 900px) {
            .main .block-container { padding:1rem; }
            .decision-grid { grid-template-columns:1fr; }
            .hero { padding:1.35rem; }
        }

        /* Contrast fixes for Streamlit/BaseWeb components. Keep these last. */
        [data-testid="stHeader"] [data-testid="stToolbar"],
        [data-testid="stHeader"] [data-testid="stToolbar"] *,
        [data-testid="stToolbar"] button,
        [data-testid="stToolbar"] svg {
            color:#ffffff !important;
            fill:#ffffff !important;
            stroke:#ffffff !important;
        }
        [data-testid="stToolbar"] [aria-label="Deploy"],
        [data-testid="stToolbar"] button[title="Deploy"],
        [data-testid="stDeployButton"],
        [data-testid="stActionButton"] {
            display:none !important;
        }
        .main [data-testid="stNumberInput"] [data-baseweb="input"],
        .main [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        .main [data-testid="stNumberInput"] [data-baseweb="input"] input,
        .main [data-testid="stTextInput"] [data-baseweb="input"],
        .main [data-testid="stTextInput"] [data-baseweb="input"] input {
            background:#ffffff !important;
            color:#10201a !important;
            -webkit-text-fill-color:#10201a !important;
            caret-color:#10201a !important;
        }
        .main [data-testid="stNumberInput"] button {
            background:#eef4ef !important;
            color:#10201a !important;
            border-left:1px solid #cbd8cf !important;
        }
        .main [data-testid="stNumberInput"] button *,
        .main [data-testid="stNumberInput"] button svg {
            color:#10201a !important;
            fill:#10201a !important;
            stroke:#10201a !important;
        }
        [data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="input"],
        [data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="input"] input {
            background:#0c1211 !important;
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            caret-color:#ffffff !important;
        }
        [data-testid="stSidebar"] [data-testid="stNumberInput"] button {
            background:#17231f !important;
            color:#ffffff !important;
            border-left:1px solid rgba(255,255,255,.18) !important;
        }
        [data-testid="stSidebar"] [data-testid="stNumberInput"] button *,
        [data-testid="stSidebar"] [data-testid="stNumberInput"] button svg {
            color:#ffffff !important;
            fill:#ffffff !important;
            stroke:#ffffff !important;
        }
        .stDownloadButton button,
        .stLinkButton a,
        .stButton button {
            color:#10201a !important;
            -webkit-text-fill-color:#10201a !important;
        }
        .stDownloadButton button *,
        .stLinkButton a *,
        .stButton button * {
            color:#10201a !important;
            -webkit-text-fill-color:#10201a !important;
        }
        .stFormSubmitButton button,
        .stFormSubmitButton button * {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
        }
        [data-testid="stNumberInput"] input,
        [data-testid="stNumberInput"] input[type="number"],
        [data-testid="stNumberInput"] [data-baseweb="input"] input,
        [data-testid="stNumberInput"] [data-baseweb="input"] * {
            color:#ffffff !important;
            -webkit-text-fill-color:#ffffff !important;
            caret-color:#ffffff !important;
        }
        [data-testid="stNumberInput"] [data-baseweb="input"],
        [data-testid="stNumberInput"] [data-baseweb="input"] > div {
            background:#252831 !important;
            border-color:#3d4350 !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] *,
        [data-testid="stSelectbox"] [data-baseweb="select"] div {
            color:#10201a !important;
            -webkit-text-fill-color:#10201a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    for key in ["digital", "stock", "viability", "verification"]:
        st.session_state.setdefault(key, None if key != "verification" else {})


def polish_chart(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#25342f", size=13),
        title=dict(font=dict(size=18, color="#17372c"), x=0.02, xanchor="left"),
        margin=dict(l=34, r=24, t=62, b=36),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, linecolor="#d8ded3", zeroline=False)
    fig.update_yaxes(gridcolor="#e9eee7", linecolor="#d8ded3", zeroline=False)
    return fig


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-inner">
                <div class="eyebrow">Modelos y Simulacion aplicada</div>
                <h1>VitaCookies</h1>
                <p>Tablero academico para anticipar riesgos, comparar escenarios y convertir el testeo sensorial en decisiones claras para Nutricion.</p>
                <div class="hero-meta">
                    <span class="hero-chip">Eventos discretos</span>
                    <span class="hero-chip">Monte Carlo</span>
                    <span class="hero-chip">Validacion posterior</span>
                    <span class="hero-chip">Informe DOCX</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="card"><div class="card-kicker">01</div><h3>Flujo digital</h3><p>Evalua llegada, degustacion y concurrencia del formulario para detectar picos de saturacion.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="card"><div class="card-kicker">02</div><h3>Stock sensorial</h3><p>Calcula quiebre, sobrantes, desperdicio y porciones recomendadas bajo incertidumbre.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="card"><div class="card-kicker">03</div><h3>Decision comercial</h3><p>Relaciona aceptacion, costos, demanda y ganancia para defender una recomendacion final.</p></div>', unsafe_allow_html=True)


def model_box(key: str) -> None:
    card = MODEL_CARDS[key]
    with st.expander("Modelado formal del simulador"):
        st.markdown(
            f"""
            - **Sistema:** {card['system']}
            - **Objetivo:** {card['objective']}
            - **Entidades:** {card['entities']}
            - **Variables de estado:** {card['state']}
            - **Eventos:** {card['events']}
            - **Parametros:** {card['parameters']}
            - **Variables de entrada:** {card['inputs']}
            - **Variables de salida:** {card['outputs']}
            - **Supuestos:** {card['assumptions']}
            - **Restricciones:** {card['restrictions']}
            - **Alcance:** {card['scope']}
            """
        )


def decision_panel(metrics: dict) -> None:
    st.markdown("### Resultado, interpretacion y decision")
    st.markdown(
        f"""
        <div class="decision-grid">
            <div class="decision-card result">
                <div class="label">Resultado</div>
                <div class="body">{escape(str(metrics["resultado"]))}</div>
            </div>
            <div class="decision-card interpretation">
                <div class="label">Interpretacion</div>
                <div class="body">{escape(str(metrics["interpretacion"]))}</div>
            </div>
            <div class="decision-card recommendation">
                <div class="label">Recomendacion</div>
                <div class="body">{escape(str(metrics["recomendacion"]))}</div>
            </div>
            <div class="decision-card decision">
                <div class="label">Decision sugerida</div>
                <div class="body">{escape(str(metrics["decision"]))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def digital_tab(seed: int) -> None:
    st.markdown('<div class="model-box"><strong>Simulador 1: flujo de personas y formulario digital</strong><br><span>Eventos discretos para estimar riesgo de saturacion por envios simultaneos.</span></div>', unsafe_allow_html=True)
    model_box("digital")
    with st.form("digital_form"):
        a, b, c = st.columns(3)
        with a:
            arrival = st.number_input("Tasa de llegada (personas/hora)", 1.0, 600.0, 70.0, 5.0)
            duration = st.number_input("Duracion del evento (min)", 10, 360, 90, 5)
        with b:
            tasting = st.number_input("Tiempo promedio de degustacion (min)", 0.5, 30.0, 4.0, 0.5)
            form_time = st.number_input("Tiempo para completar y enviar formulario (min)", 0.5, 30.0, 4.0, 0.5)
        with c:
            capacity = st.number_input("Capacidad concurrente estimada", 1, 500, 20, 1)
            runs = st.number_input("Corridas", 100, 50000, 3000, 500)
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="digital_scenario")
        submitted = st.form_submit_button("Ejecutar simulacion digital")
    if submitted:
        inputs = DigitalFlowInputs(arrival, duration, tasting, form_time, capacity, runs, scenario, seed)
        result = simulate_digital_flow(inputs)
        result["scenarios"] = digital_scenarios(inputs)
        result["sensitivity"] = digital_sensitivity(inputs)
        st.session_state.digital = result
        st.session_state.verification["Formulario digital"] = digital_verification(result)
    result = st.session_state.digital
    if not result:
        st.info("Ejecuta el simulador para ver concurrencia, utilizacion, saturacion y recomendacion.")
        return
    m = result["metrics"]
    k = st.columns(5)
    k[0].metric("Prob. saturacion", f"{m['probabilidad_saturacion_pct']:.1f}%")
    k[1].metric("Pico carga", f"{m['pico_carga']}")
    k[2].metric("Pico P95", f"{m['pico_p95']:.0f}")
    k[3].metric("Min. saturados", f"{m['minutos_saturados']}")
    k[4].metric("Utilizacion max.", f"{m['utilizacion_maxima_pct']:.1f}%")
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        tl = result["timeline"]
        fig.add_trace(go.Scatter(x=tl["minuto"], y=tl["formularios_activos"], name="Formularios activos", line=dict(color="#2f6f4e", width=3)))
        fig.add_trace(go.Scatter(x=tl["minuto"], y=tl["capacidad"], name="Capacidad", line=dict(color="#e7893f", dash="dash")))
        fig.update_layout(template="plotly_white", title="Linea temporal de concurrencia", xaxis_title="Minuto", yaxis_title="Formularios activos")
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(tl, x="minuto", y="utilizacion_pct", title="Utilizacion del sistema (%)", color_discrete_sequence=["#bf4e45"])
        fig.add_hline(y=100, line_dash="dash", line_color="#e7893f")
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    decision_panel(m)
    st.plotly_chart(polish_chart(px.bar(result["scenarios"], x="escenario", y=["prob_saturacion_pct", "pico_p95"], barmode="group", title="Comparacion de escenarios"), 360), use_container_width=True)
    st.plotly_chart(polish_chart(px.bar(result["sensitivity"], x="variable", y="prob_saturacion_pct", color="factor", barmode="group", title="Analisis de sensibilidad"), 360), use_container_width=True)


def stock_tab(seed: int) -> None:
    st.markdown('<div class="model-box"><strong>Simulador 2: stock de porciones</strong><br><span>Monte Carlo para estimar quiebre, sobrantes, faltantes, percentiles y stock recomendado.</span></div>', unsafe_allow_html=True)
    model_box("stock")
    with st.form("stock_form"):
        a, b, c = st.columns(3)
        with a:
            initial = st.number_input("Porciones iniciales", 1, 5000, 90, 5)
            diners = st.number_input("Comensales esperados", 1, 5000, 100, 5)
        with b:
            trial = st.slider("Probabilidad de prueba", 0.0, 1.0, 0.75, 0.01)
            waste = st.slider("Porcentaje de desperdicio", 0.0, 0.70, 0.06, 0.01)
        with c:
            safety = st.slider("Margen de seguridad", 0.0, 1.0, 0.12, 0.01)
            runs = st.number_input("Corridas", 100, 50000, 5000, 500, key="stock_runs")
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="stock_scenario")
        submitted = st.form_submit_button("Ejecutar simulacion de stock")
    if submitted:
        inputs = StockInputs(initial, diners, trial, waste, safety, runs, scenario, seed + 100)
        result = simulate_stock(inputs)
        result["scenarios"] = stock_scenarios(inputs)
        result["sensitivity"] = stock_sensitivity(inputs)
        st.session_state.stock = result
        st.session_state.verification["Stock"] = stock_verification(result)
    result = st.session_state.stock
    if not result:
        st.info("Ejecuta el simulador para ver riesgo de quiebre y stock recomendado.")
        return
    m = result["metrics"]
    k = st.columns(5)
    k[0].metric("Prob. quiebre", f"{m['probabilidad_quiebre_pct']:.1f}%")
    k[1].metric("Demanda P95", f"{m['demanda_p95']:.0f}")
    k[2].metric("Faltante prom.", f"{m['faltante_promedio']:.1f}")
    k[3].metric("Sobrante prom.", f"{m['sobrante_promedio']:.1f}")
    k[4].metric("Stock recomendado", f"{m['stock_recomendado']}")
    df = result["simulations"]
    c1, c2 = st.columns(2)
    c1.plotly_chart(polish_chart(px.histogram(df, x="demanda", nbins=30, title="Distribucion de demanda"), 380), use_container_width=True)
    c2.plotly_chart(polish_chart(px.histogram(df, x="sobrantes", nbins=30, title="Distribucion de sobrantes"), 380), use_container_width=True)
    decision_panel(m)
    st.plotly_chart(polish_chart(px.bar(result["scenarios"], x="escenario", y=["prob_quiebre_pct", "stock_recomendado"], barmode="group", title="Comparacion de escenarios"), 360), use_container_width=True)
    st.plotly_chart(polish_chart(px.bar(result["sensitivity"], x="variable", y="prob_quiebre_pct", color="factor", barmode="group", title="Analisis de sensibilidad"), 360), use_container_width=True)


def viability_tab(seed: int) -> None:
    st.markdown('<div class="model-box"><strong>Simulador 3: viabilidad productiva y comercial</strong><br><span>Monte Carlo para evaluar costo, punto de equilibrio, ganancia y probabilidad de rentabilidad.</span></div>', unsafe_allow_html=True)
    model_box("viability")
    with st.form("viability_form"):
        a, b, c = st.columns(3)
        with a:
            batch_cost = st.number_input("Costo por lote ($)", 1.0, 10_000_000.0, 4500.0, 100.0)
            units = st.number_input("Unidades por lote", 1, 10000, 50, 5)
            fixed = st.number_input("Costos fijos ($)", 0.0, 10_000_000.0, 15000.0, 500.0)
        with b:
            waste = st.slider("Desperdicio productivo", 0.0, 0.80, 0.08, 0.01)
            price = st.number_input("Precio de venta ($)", 1.0, 100000.0, 180.0, 10.0)
            demand = st.number_input("Demanda esperada", 1, 100000, 300, 10)
        with c:
            acceptance = st.slider("Aceptacion sensorial", 0.0, 1.0, 0.70, 0.01)
            runs = st.number_input("Corridas", 100, 50000, 5000, 500, key="viability_runs")
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="viability_scenario")
        submitted = st.form_submit_button("Ejecutar simulacion de viabilidad")
    if submitted:
        inputs = ViabilityInputs(batch_cost, units, fixed, waste, price, demand, acceptance, runs, scenario, seed + 200)
        result = simulate_viability(inputs)
        result["scenarios"] = viability_scenarios(inputs)
        result["sensitivity"] = viability_sensitivity(inputs)
        result["critical"] = critical_variables(result["sensitivity"])
        result["impacts"] = improvement_impacts(inputs)
        st.session_state.viability = result
        st.session_state.verification["Viabilidad"] = viability_verification(result)
    result = st.session_state.viability
    if not result:
        st.info("Ejecuta el simulador para ver rentabilidad y variables criticas.")
        return
    m = result["metrics"]
    break_even = "No alcanzable" if m["punto_equilibrio"] == float("inf") else f"{m['punto_equilibrio']:.0f}"
    k = st.columns(5)
    k[0].metric("Prob. rentable", f"{m['probabilidad_rentabilidad_pct']:.1f}%")
    k[1].metric("Ganancia prom.", f"${m['ganancia_promedio']:,.0f}")
    k[2].metric("Ganancia P10", f"${m['ganancia_p10']:,.0f}")
    k[3].metric("Costo unitario", f"${m['costo_unitario_promedio']:,.2f}")
    k[4].metric("Punto equilibrio", break_even)
    df = result["simulations"]
    c1, c2 = st.columns(2)
    fig = px.histogram(df, x="ganancia", nbins=35, title="Distribucion de ganancias")
    fig.add_vline(x=0, line_dash="dash", line_color="#bf4e45")
    c1.plotly_chart(polish_chart(fig, 380), use_container_width=True)
    c2.plotly_chart(polish_chart(px.scatter(df.sample(min(len(df), 700), random_state=7), x="demanda_efectiva", y="ganancia", color="aceptacion", title="Ganancia segun demanda efectiva"), 380), use_container_width=True)
    decision_panel(m)
    st.plotly_chart(polish_chart(px.bar(result["scenarios"], x="escenario", y=["prob_rentabilidad_pct", "ganancia_promedio"], barmode="group", title="Comparacion de escenarios"), 360), use_container_width=True)
    st.plotly_chart(polish_chart(px.bar(result["critical"], x="variable", y="impacto_ganancia", title="Variables criticas por impacto en ganancia"), 360), use_container_width=True)
    st.plotly_chart(polish_chart(px.bar(result["impacts"], x="mejora", y=["ganancia_promedio", "prob_rentabilidad_pct"], barmode="group", title="Impacto de mejorar aceptacion o reducir desperdicio"), 360), use_container_width=True)


def verification_validation_section() -> None:
    st.header("Verificacion y validacion")
    with st.expander("Verificacion computacional"):
        if not st.session_state.verification:
            st.info("Ejecuta los simuladores para completar los chequeos.")
        for model, checks in st.session_state.verification.items():
            st.subheader(model)
            for name, ok in checks.items():
                st.write(f"{'Cumple' if ok else 'Revisar'} - {name.replace('_', ' ')}")
    with st.expander("Validacion contra el evento real"):
        st.markdown(
            """
            Despues del testeo sensorial se deben comparar las simulaciones con datos reales:

            - asistentes reales vs comensales esperados;
            - tiempo real promedio para completar el formulario;
            - momento de mayor carga digital;
            - porciones consumidas y desperdiciadas;
            - aceptacion sensorial real obtenida del formulario;
            - costos reales de preparacion.

            Con esos datos se recalibran los parametros y se ejecuta una simulacion posterior.
            """
        )


def data_guidance() -> None:
    with st.expander("Como estimar probabilidades, desperdicio y aceptacion"):
        st.markdown(
            """
            Antes del evento, estos valores son supuestos defendibles. Despues del evento, se reemplazan por mediciones:

            - **Probabilidad de prueba:** personas que probaron / asistentes.
            - **Desperdicio:** porciones perdidas o no servibles / porciones preparadas.
            - **Aceptacion sensorial:** porcentaje de respuestas positivas o promedio normalizado del formulario.
            - **Demanda esperada:** asistentes reales o estimacion de convocatoria.
            - **Capacidad concurrente:** estimacion conservadora del formulario/plataforma; sirve para evaluar riesgo de pico.
            """
        )


def report_buttons() -> None:
    markdown = generate_markdown_report(
        {"digital": st.session_state.digital, "stock": st.session_state.stock, "viability": st.session_state.viability},
        st.session_state.verification,
    )
    st.download_button("Generar Informe Markdown", markdown, "informe_vitacookies.md", "text/markdown", use_container_width=True)
    st.download_button("Generar Informe DOCX", generate_docx_report(markdown), "informe_vitacookies.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)


def oral_defense() -> None:
    st.header("Guia para defensa oral")
    st.markdown(
        """
        - **Formulario digital:** muestra como la simulacion de eventos discretos permite decidir si se deben escalonar envios.
        - **Stock:** muestra como Monte Carlo justifica una cantidad recomendada de porciones bajo incertidumbre.
        - **Viabilidad:** muestra si el producto es viable y que variable conviene mejorar primero.
        - **Validacion:** explica que los datos reales del evento reemplazan los supuestos y permiten recalibrar.
        - **Conclusion:** la herramienta no solo calcula numeros; convierte escenarios en decisiones para Nutricion.
        """
    )


def main() -> None:
    css()
    init_state()
    hero()
    data_guidance()
    with st.sidebar:
        st.title("VitaCookies")
        st.caption("Panel de simulacion academica")
        seed = st.number_input("Semilla aleatoria", 0, 999999, 42, 1)
        st.link_button("Abrir formulario digital", "https://vita-cookies-form-v.vercel.app/", use_container_width=True)
        st.divider()
        st.caption("Entregables")
        report_buttons()
    tabs = st.tabs(["Flujo digital", "Stock", "Viabilidad", "Verificacion", "Defensa oral"])
    with tabs[0]:
        digital_tab(seed)
    with tabs[1]:
        stock_tab(seed)
    with tabs[2]:
        viability_tab(seed)
    with tabs[3]:
        verification_validation_section()
    with tabs[4]:
        oral_defense()


if __name__ == "__main__":
    main()
