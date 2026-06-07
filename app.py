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
        #MainMenu, [data-testid="stDecoration"], [data-testid="stAppDeployButton"], button[title="Deploy"], [aria-label="Deploy"] {
            display:none !important;
        }
        .stApp {
            background:
                linear-gradient(180deg, rgba(255,255,255,.92), rgba(255,255,255,.72)),
                linear-gradient(135deg, #f3f7ef 0%, #fff8ec 48%, #eef4f7 100%);
            color:var(--ink);
        }
        .stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3 {
            color:var(--ink);
            letter-spacing:0;
        }
        .main .block-container {
            max-width:1320px;
            padding:1.05rem 2.1rem 2.4rem;
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
            border-radius:14px;
            padding:1.05rem 1.2rem;
            background:
                linear-gradient(120deg, rgba(18,84,61,.94) 0%, rgba(31,122,90,.90) 44%, rgba(224,122,63,.92) 100%);
            box-shadow:0 14px 32px rgba(32,44,38,.12);
            margin-bottom:.65rem;
        }
        .hero::after {
            content:"";
            position:absolute;
            right:-60px;
            top:-94px;
            width:230px;
            height:230px;
            border-radius:50%;
            border:32px solid rgba(255,255,255,.12);
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
            padding:.28rem .58rem;
            border-radius:999px;
            background:rgba(255,255,255,.14);
            color:#f4fff8 !important;
            border:1px solid rgba(255,255,255,.22);
            font-size:.72rem;
            font-weight:750;
            text-transform:uppercase;
        }
        .hero h1 {
            margin:.46rem 0 .18rem;
            color:#ffffff !important;
            font-size:clamp(2.05rem,4.1vw,3.4rem);
            line-height:1;
            font-weight:850;
        }
        .hero p {
            color:#f3fff5 !important;
            max-width:920px;
            font-size:1rem;
            line-height:1.45;
            margin:.38rem 0 0;
        }
        .hero-meta {
            display:flex;
            gap:.45rem;
            flex-wrap:wrap;
            margin-top:.72rem;
        }
        .hero-chip {
            background:rgba(255,255,255,.92);
            color:#183029 !important;
            border:1px solid rgba(255,255,255,.36);
            border-radius:999px;
            padding:.34rem .58rem;
            font-weight:700;
            font-size:.8rem;
        }
        .workflow-strip {
            display:grid;
            grid-template-columns:repeat(3, minmax(0, 1fr));
            gap:.65rem;
            margin:.65rem 0 .75rem;
        }
        .workflow-step {
            display:grid;
            grid-template-columns:auto 1fr;
            gap:.75rem;
            align-items:start;
            background:rgba(255,255,255,.86);
            border:1px solid rgba(25,45,37,.10);
            border-radius:12px;
            padding:.78rem .85rem;
            box-shadow:0 8px 20px rgba(32,44,38,.06);
            min-height:88px;
        }
        .workflow-step h3 {
            color:var(--leaf-dark) !important;
            margin:.05rem 0 .22rem;
            font-size:.95rem;
            font-weight:820;
        }
        .workflow-step p {
            color:var(--muted) !important;
            margin:0;
            line-height:1.35;
            font-size:.86rem;
        }
        .step-kicker {
            display:inline-grid;
            place-items:center;
            width:32px;
            height:32px;
            border-radius:9px;
            background:#e9f4ec;
            color:var(--leaf-dark) !important;
            font-weight:900;
            font-size:.82rem;
        }
        .model-box {
            background:rgba(255,255,255,.9);
            border:1px solid rgba(25,45,37,.10);
            border-left:5px solid var(--carrot);
            border-radius:12px;
            padding:.78rem .9rem;
            margin:.75rem 0 .7rem;
            box-shadow:0 8px 18px rgba(32,44,38,.05);
        }
        .model-box strong {
            color:#17372c !important;
            font-size:1rem;
        }
        .model-box br {
            display:block;
            margin:.2rem 0;
        }
        .simple-note {
            background:#f4faf6;
            border:1px solid rgba(31,122,90,.18);
            border-left:5px solid var(--leaf);
            border-radius:12px;
            padding:.82rem .95rem;
            margin:.55rem 0 .85rem;
            color:#183029 !important;
            line-height:1.42;
            font-weight:560;
        }
        .simple-note strong {
            color:var(--leaf-dark) !important;
        }
        .decision-grid {
            display:grid;
            grid-template-columns:repeat(2, minmax(0, 1fr));
            gap:.65rem;
            margin:.25rem 0 .85rem;
        }
        .decision-card {
            background:#fff;
            border:1px solid rgba(25,45,37,.12);
            border-radius:12px;
            padding:.85rem;
            box-shadow:0 8px 18px rgba(32,44,38,.05);
            min-height:94px;
        }
        .decision-card .label {
            color:#6a756f !important;
            text-transform:uppercase;
            font-size:.74rem;
            font-weight:850;
            margin-bottom:.35rem;
        }
        .decision-card .body {
            color:#21332d !important;
            line-height:1.34;
            font-weight:560;
        }
        .decision-card.result { border-top:4px solid var(--blue); }
        .decision-card.interpretation { border-top:4px solid var(--gold); }
        .decision-card.recommendation { border-top:4px solid var(--carrot); }
        .decision-card.decision { border-top:4px solid var(--leaf); }
        [data-testid="stMetric"] {
            background:#ffffff;
            border-radius:12px;
            padding:.72rem .82rem;
            border:1px solid rgba(25,45,37,.10);
            box-shadow:0 8px 18px rgba(32,44,38,.05);
        }
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"] * {
            color:var(--leaf-dark) !important;
        }
        div[data-testid="stMetricValue"] * {
            font-weight:850 !important;
            line-height:1.05 !important;
        }
        [data-testid="stForm"] {
            background:rgba(255,255,255,.9);
            border-radius:12px;
            padding:.9rem;
            border:1px solid rgba(25,45,37,.10);
            box-shadow:0 8px 20px rgba(32,44,38,.05);
        }
        [data-testid="stWidgetLabel"] * {
            color:#31463d !important;
            font-weight:760;
        }
        [data-baseweb="input"],
        [data-baseweb="select"] > div {
            background:#ffffff !important;
            border-color:#cbd8cf !important;
            border-radius:8px !important;
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
            border-radius:10px !important;
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
            border-radius:10px !important;
            font-weight:760 !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap:.5rem;
            position:sticky;
            top:3.45rem;
            z-index:3;
            overflow-x:auto;
            background:rgba(255,255,255,.86);
            backdrop-filter:blur(10px);
            border:1px solid rgba(25,45,37,.10);
            padding:.36rem;
            border-radius:12px;
            box-shadow:0 8px 18px rgba(32,44,38,.06);
        }
        .stTabs [data-baseweb="tab"] {
            background:transparent;
            border-radius:9px;
            color:#263a33 !important;
            padding:.5rem .82rem;
            font-weight:780;
            white-space:nowrap;
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
            border-radius:10px;
            box-shadow:0 6px 14px rgba(32,44,38,.04);
        }
        [data-testid="stDataFrame"] {
            border-radius:14px;
            overflow:hidden;
        }
        @media (max-width: 900px) {
            .main .block-container { padding:.85rem 1rem 1.6rem; }
            .decision-grid { grid-template-columns:1fr; }
            .hero { padding:1rem; }
            .hero h1 { font-size:2.25rem; }
            .hero p { font-size:.95rem; line-height:1.4; }
            .workflow-strip {
                display:flex;
                gap:.55rem;
                overflow-x:auto;
                padding-bottom:.15rem;
                scroll-snap-type:x proximity;
            }
            .workflow-step {
                min-width:252px;
                min-height:96px;
                scroll-snap-align:start;
            }
            .stTabs [data-baseweb="tab-list"] {
                top:2.95rem;
                border-radius:10px;
            }
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
        [data-testid="stAppDeployButton"],
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
        .main [data-testid="stNumberInput"] input,
        .main [data-testid="stNumberInput"] input[type="number"],
        .main [data-testid="stNumberInput"] [data-baseweb="input"] input,
        .main [data-testid="stNumberInput"] [data-baseweb="input"] * {
            color:#10201a !important;
            -webkit-text-fill-color:#10201a !important;
            caret-color:#10201a !important;
        }
        .main [data-testid="stNumberInput"] [data-baseweb="input"],
        .main [data-testid="stNumberInput"] [data-baseweb="input"] > div {
            background:#ffffff !important;
            border-color:#cbd8cf !important;
        }
        [data-testid="stMain"] [data-testid="stNumberInput"] input,
        [data-testid="stMain"] [data-testid="stNumberInput"] input[type="number"],
        [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"] input,
        [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"] * {
            color:#10201a !important;
            -webkit-text-fill-color:#10201a !important;
            caret-color:#10201a !important;
        }
        [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"],
        [data-testid="stMain"] [data-testid="stNumberInput"] [data-baseweb="input"] > div {
            background:#ffffff !important;
            border-color:#cbd8cf !important;
        }
        [data-testid="stMain"] [data-testid="stNumberInput"] button {
            background:#eef4ef !important;
            color:#10201a !important;
            border-left:1px solid #cbd8cf !important;
        }
        [data-testid="stMain"] [data-testid="stNumberInput"] button *,
        [data-testid="stMain"] [data-testid="stNumberInput"] button svg {
            color:#10201a !important;
            fill:#10201a !important;
            stroke:#10201a !important;
        }
        [data-testid="stPlotlyChart"] svg text {
            fill:#17372c !important;
            opacity:1 !important;
        }
        [data-testid="stPlotlyChart"] .legendtext,
        [data-testid="stPlotlyChart"] .legendtitletext,
        [data-testid="stPlotlyChart"] .xtick text,
        [data-testid="stPlotlyChart"] .ytick text,
        [data-testid="stPlotlyChart"] .xtitle,
        [data-testid="stPlotlyChart"] .ytitle,
        [data-testid="stPlotlyChart"] .colorbar text {
            fill:#263a33 !important;
            opacity:1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    for key in ["digital", "stock", "viability", "verification"]:
        st.session_state.setdefault(key, None if key != "verification" else {})
    if st.session_state.get("_model_cache_version") != MODEL_CACHE_VERSION:
        st.session_state.digital = None
        st.session_state.stock = None
        st.session_state.viability = None
        st.session_state.verification = {}
        st.session_state["_model_cache_version"] = MODEL_CACHE_VERSION


CHART_TEXT = "#17372c"
CHART_MUTED = "#4f6259"
CHART_GRID = "#dfe8df"
CHART_AXIS = "#b7c6bd"
CHART_LABELS = {
    "minuto": "Minuto",
    "utilizacion_pct": "Utilizacion (%)",
    "formularios_activos": "Formularios activos",
    "capacidad": "Capacidad",
    "escenario": "Escenario",
    "variable": "Dato que cambia",
    "factor": "Cambio aplicado",
    "factor_label": "Cambio aplicado",
    "value": "Valor",
    "prob_saturacion_pct": "Riesgo de saturacion (%)",
    "pico_p95": "Pico prudente (P95)",
    "minutos_saturados_promedio": "Minutos saturados promedio",
    "prob_quiebre_pct": "Riesgo de faltante (%)",
    "stock_recomendado": "Porciones sugeridas",
    "prob_rentabilidad_pct": "Chance de rentabilidad (%)",
    "ganancia_promedio": "Ganancia promedio ($)",
    "impacto_ganancia": "Impacto en ganancia",
    "demanda": "Demanda",
    "sobrantes": "Sobrantes",
    "ganancia": "Ganancia",
    "demanda_efectiva": "Demanda efectiva",
    "aceptacion": "Aceptacion",
    "aceptacion_pct": "Aceptacion (%)",
    "mejora": "Mejora",
}
RUNS_HELP = "Cantidad de veces que el modelo repite el experimento virtual para estimar probabilidades, promedios y percentiles."
MODEL_CACHE_VERSION = "humanized-charts-v2"


def factor_label(factor: float) -> str:
    pct = int(round((float(factor) - 1) * 100))
    if pct == 0:
        return "Base"
    return f"{pct:+d}%"


def chart_label(value: object) -> str:
    text = str(value)
    return CHART_LABELS.get(text, text.replace("_", " ").capitalize())


def polish_chart(fig: go.Figure, height: int = 390) -> go.Figure:
    for trace in fig.data:
        if getattr(trace, "name", None):
            trace.name = chart_label(trace.name)

    for axis_name in ("xaxis", "yaxis"):
        axis = getattr(fig.layout, axis_name, None)
        if axis and axis.title and axis.title.text:
            axis.title.text = chart_label(axis.title.text)

    if fig.layout.legend and fig.layout.legend.title and fig.layout.legend.title.text:
        fig.layout.legend.title.text = chart_label(fig.layout.legend.title.text)

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Segoe UI, Arial, sans-serif", color=CHART_TEXT, size=13),
        title=dict(font=dict(size=18, color=CHART_TEXT), x=0.02, xanchor="left"),
        margin=dict(l=52, r=28, t=68, b=54),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(color=CHART_TEXT, size=12),
            title=dict(font=dict(color=CHART_MUTED, size=12)),
        ),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor=CHART_AXIS, font=dict(color=CHART_TEXT)),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=CHART_AXIS,
        zeroline=False,
        tickfont=dict(color=CHART_MUTED, size=12),
        title_font=dict(color=CHART_TEXT, size=13),
        tickcolor=CHART_AXIS,
        ticks="outside",
    )
    fig.update_yaxes(
        gridcolor=CHART_GRID,
        linecolor=CHART_AXIS,
        zeroline=False,
        tickfont=dict(color=CHART_MUTED, size=12),
        title_font=dict(color=CHART_TEXT, size=13),
        tickcolor=CHART_AXIS,
        ticks="outside",
    )
    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color=CHART_MUTED, size=12),
            title=dict(font=dict(color=CHART_TEXT, size=13)),
            outlinecolor=CHART_AXIS,
        )
    )
    fig.update_annotations(font_color=CHART_TEXT)
    return fig


def bar_chart(
    data,
    x: str,
    y: str,
    title: str,
    y_title: str,
    height: int = 340,
    color: str = "#1f7a5a",
) -> go.Figure:
    fig = px.bar(data, x=x, y=y, title=title, text=y, color_discrete_sequence=[color])
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis_title=y_title, xaxis_title=None)
    return polish_chart(fig, height)


def grouped_bar_chart(
    data,
    x: str,
    y: str,
    color: str,
    title: str,
    y_title: str,
    height: int = 340,
) -> go.Figure:
    fig = px.bar(data, x=x, y=y, color=color, barmode="group", title=title, text=y)
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis_title=y_title, xaxis_title=None)
    return polish_chart(fig, height)


def simple_note(body: str) -> None:
    st.markdown(f'<div class="simple-note"><strong>En simple:</strong> {escape(body)}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def compute_digital_result(
    arrival: float,
    duration: int,
    tasting: float,
    form_time: float,
    capacity: int,
    runs: int,
    scenario: str,
    seed: int,
    cache_version: str,
) -> tuple[dict, dict[str, bool]]:
    inputs = DigitalFlowInputs(arrival, duration, tasting, form_time, capacity, runs, scenario, seed)
    result = simulate_digital_flow(inputs)
    result["scenarios"] = digital_scenarios(inputs)
    result["sensitivity"] = digital_sensitivity(inputs)
    return result, digital_verification(result)


@st.cache_data(show_spinner=False)
def compute_stock_result(
    initial: int,
    diners: int,
    trial: float,
    waste: float,
    safety: float,
    runs: int,
    scenario: str,
    seed: int,
    cache_version: str,
) -> tuple[dict, dict[str, bool]]:
    inputs = StockInputs(initial, diners, trial, waste, safety, runs, scenario, seed + 100)
    result = simulate_stock(inputs)
    result["scenarios"] = stock_scenarios(inputs)
    result["sensitivity"] = stock_sensitivity(inputs)
    return result, stock_verification(result)


@st.cache_data(show_spinner=False)
def compute_viability_result(
    batch_cost: float,
    units: int,
    fixed: float,
    waste: float,
    price: float,
    demand: int,
    acceptance: float,
    runs: int,
    scenario: str,
    seed: int,
    cache_version: str,
) -> tuple[dict, dict[str, bool]]:
    inputs = ViabilityInputs(batch_cost, units, fixed, waste, price, demand, acceptance, runs, scenario, seed + 200)
    result = simulate_viability(inputs)
    result["scenarios"] = viability_scenarios(inputs)
    result["sensitivity"] = viability_sensitivity(inputs)
    result["critical"] = critical_variables(result["sensitivity"])
    result["impacts"] = improvement_impacts(inputs)
    return result, viability_verification(result)


@st.cache_data(show_spinner=False)
def cached_docx_report(markdown_text: str) -> bytes:
    return generate_docx_report(markdown_text)


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-inner">
                <div class="eyebrow">Simulador de decisiones</div>
                <h1>VitaCookies</h1>
                <p>Cambia los supuestos, ejecuta la simulacion y mira que conviene hacer con el formulario, las porciones y la viabilidad del producto.</p>
                <div class="hero-meta">
                    <span class="hero-chip">Formulario</span>
                    <span class="hero-chip">Porciones</span>
                    <span class="hero-chip">Costos</span>
                    <span class="hero-chip">Informe DOCX</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="workflow-strip">
            <div class="workflow-step">
                <div class="step-kicker">01</div>
                <div><h3>Formulario</h3><p>Ve si muchas respuestas juntas pueden trabar la carga.</p></div>
            </div>
            <div class="workflow-step">
                <div class="step-kicker">02</div>
                <div><h3>Porciones</h3><p>Estima si alcanza la produccion o si conviene preparar reserva.</p></div>
            </div>
            <div class="workflow-step">
                <div class="step-kicker">03</div>
                <div><h3>Viabilidad</h3><p>Prueba precio, costos y aceptacion para decidir si vale escalar.</p></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def model_box(key: str) -> None:
    card = MODEL_CARDS[key]
    with st.expander("Detalles del modelo (opcional)"):
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
    st.markdown("### Lectura rapida")
    st.markdown(
        f"""
        <div class="decision-grid">
            <div class="decision-card result">
                <div class="label">Que paso</div>
                <div class="body">{escape(str(metrics["resultado"]))}</div>
            </div>
            <div class="decision-card interpretation">
                <div class="label">Que significa</div>
                <div class="body">{escape(str(metrics["interpretacion"]))}</div>
            </div>
            <div class="decision-card recommendation">
                <div class="label">Que conviene hacer</div>
                <div class="body">{escape(str(metrics["recomendacion"]))}</div>
            </div>
            <div class="decision-card decision">
                <div class="label">Decision</div>
                <div class="body">{escape(str(metrics["decision"]))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def digital_tab(seed: int) -> None:
    st.markdown('<div class="model-box"><strong>Formulario digital</strong><br><span>Sirve para ver si muchas personas respondiendo juntas pueden superar la capacidad del formulario.</span></div>', unsafe_allow_html=True)
    model_box("digital")
    with st.form("digital_form"):
        a, b, c = st.columns(3)
        with a:
            arrival = st.number_input("Personas que llegan por hora", 1.0, 600.0, 70.0, 5.0)
            duration = st.number_input("Duracion del testeo (min)", 10, 360, 90, 5)
        with b:
            tasting = st.number_input("Minutos de degustacion", 0.5, 30.0, 4.0, 0.5)
            form_time = st.number_input("Minutos para responder", 0.5, 30.0, 4.0, 0.5)
        with c:
            capacity = st.number_input("Formularios simultaneos que aguanta", 1, 500, 20, 1)
            runs = st.number_input("Numero de simulaciones", 100, 50000, 3000, 500, help=RUNS_HELP)
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="digital_scenario")
        submitted = st.form_submit_button("Ejecutar simulacion digital")
    if submitted:
        with st.spinner("Ejecutando simulacion digital..."):
            result, checks = compute_digital_result(arrival, duration, tasting, form_time, capacity, runs, scenario, seed, MODEL_CACHE_VERSION)
        st.session_state.digital = result
        st.session_state.verification["Formulario"] = checks
        st.success("Simulacion digital lista.")
    result = st.session_state.digital
    if not result:
        st.info("Ejecuta el simulador para estimar si el formulario puede saturarse.")
        return
    m = result["metrics"]
    k = st.columns(5)
    k[0].metric("Riesgo de saturacion", f"{m['probabilidad_saturacion_pct']:.1f}%")
    k[1].metric("Pico esperado", f"{m['pico_promedio']:.1f}")
    k[2].metric("Pico prudente", f"{m['pico_p95']:.0f}")
    k[3].metric("Min. saturados prom.", f"{m['minutos_saturados_promedio']:.1f}")
    k[4].metric("Uso max. promedio", f"{m['utilizacion_maxima_promedio_pct']:.1f}%")
    simple_note(
        f"hay {m['probabilidad_saturacion_pct']:.1f}% de chances de que el formulario supere la capacidad. "
        f"Para estar tranquilos, prepararia el sistema para unos {m['pico_p95']:.0f} formularios simultaneos."
    )
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        tl = result["timeline"]
        fig.add_trace(go.Scatter(x=tl["minuto"], y=tl["formularios_activos"], name="Formularios activos", line=dict(color="#2f6f4e", width=3)))
        fig.add_trace(go.Scatter(x=tl["minuto"], y=tl["capacidad"], name="Capacidad", line=dict(color="#e7893f", dash="dash")))
        fig.update_layout(template="plotly_white", title="Ejemplo minuto a minuto", xaxis_title="Minuto", yaxis_title="Formularios activos")
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(tl, x="minuto", y="utilizacion_pct", title="Uso del formulario en ese ejemplo (%)", color_discrete_sequence=["#bf4e45"])
        fig.add_hline(y=100, line_dash="dash", line_color="#e7893f")
        polish_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    decision_panel(m)
    c1, c2 = st.columns(2)
    c1.plotly_chart(bar_chart(result["scenarios"], "escenario", "prob_saturacion_pct", "Riesgo por escenario", "% de simulaciones con saturacion", color="#bf4e45"), use_container_width=True)
    c2.plotly_chart(bar_chart(result["scenarios"], "escenario", "pico_p95", "Pico prudente por escenario", "Formularios simultaneos", color="#e07a3f"), use_container_width=True)
    sensitivity = result["sensitivity"].copy()
    sensitivity["factor_label"] = sensitivity["factor"].map(factor_label)
    st.plotly_chart(grouped_bar_chart(sensitivity, "variable", "prob_saturacion_pct", "factor_label", "Que dato mueve mas el riesgo", "Riesgo de saturacion (%)"), use_container_width=True)


def stock_tab(seed: int) -> None:
    st.markdown('<div class="model-box"><strong>Porciones para el testeo</strong><br><span>Sirve para estimar si las porciones alcanzan y cuanta reserva conviene preparar.</span></div>', unsafe_allow_html=True)
    model_box("stock")
    with st.form("stock_form"):
        a, b, c = st.columns(3)
        with a:
            initial = st.number_input("Porciones iniciales", 1, 5000, 90, 5)
            diners = st.number_input("Comensales esperados", 1, 5000, 100, 5)
        with b:
            trial_pct = st.slider("Personas que probarian (%)", 0, 100, 75, 1)
            waste_pct = st.slider("Desperdicio estimado (%)", 0, 70, 6, 1)
        with c:
            safety_pct = st.slider("Reserva extra (%)", 0, 100, 12, 1)
            runs = st.number_input("Numero de simulaciones", 100, 50000, 5000, 500, key="stock_runs", help=RUNS_HELP)
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="stock_scenario")
        submitted = st.form_submit_button("Ejecutar simulacion de stock")
    if submitted:
        with st.spinner("Ejecutando simulacion de stock..."):
            result, checks = compute_stock_result(initial, diners, trial_pct / 100, waste_pct / 100, safety_pct / 100, runs, scenario, seed, MODEL_CACHE_VERSION)
        st.session_state.stock = result
        st.session_state.verification["Porciones"] = checks
        st.success("Simulacion de stock lista.")
    result = st.session_state.stock
    if not result:
        st.info("Ejecuta el simulador para estimar riesgo de faltante y stock recomendado.")
        return
    m = result["metrics"]
    k = st.columns(5)
    k[0].metric("Riesgo de faltante", f"{m['probabilidad_quiebre_pct']:.1f}%")
    k[1].metric("Demanda alta", f"{m['demanda_p95']:.0f}")
    k[2].metric("Faltante promedio", f"{m['faltante_promedio']:.1f}")
    k[3].metric("Sobrante promedio", f"{m['sobrante_promedio']:.1f}")
    k[4].metric("Porciones sugeridas", f"{m['stock_recomendado']}")
    simple_note(
        f"con {initial} porciones, el riesgo de quedarse corto es {m['probabilidad_quiebre_pct']:.1f}%. "
        f"Para cubrir un dia exigente, prepararia cerca de {m['stock_recomendado']} porciones."
    )
    df = result["simulations"]
    c1, c2 = st.columns(2)
    c1.plotly_chart(polish_chart(px.histogram(df, x="demanda", nbins=30, title="Cuantas porciones podrian pedir"), 360), use_container_width=True)
    c2.plotly_chart(polish_chart(px.histogram(df, x="sobrantes", nbins=30, title="Cuantas porciones podrian sobrar"), 360), use_container_width=True)
    decision_panel(m)
    c1, c2 = st.columns(2)
    c1.plotly_chart(bar_chart(result["scenarios"], "escenario", "prob_quiebre_pct", "Riesgo de faltante por escenario", "% de simulaciones con faltante", color="#bf4e45"), use_container_width=True)
    c2.plotly_chart(bar_chart(result["scenarios"], "escenario", "stock_recomendado", "Porciones sugeridas por escenario", "Porciones", color="#e07a3f"), use_container_width=True)
    sensitivity = result["sensitivity"].copy()
    sensitivity["factor_label"] = sensitivity["factor"].map(factor_label)
    st.plotly_chart(grouped_bar_chart(sensitivity, "variable", "prob_quiebre_pct", "factor_label", "Que dato mueve mas el riesgo", "Riesgo de faltante (%)"), use_container_width=True)


def viability_tab(seed: int) -> None:
    st.markdown('<div class="model-box"><strong>Viabilidad del producto</strong><br><span>Sirve para probar si el precio, los costos y la aceptacion alcanzan para que el producto sea rentable.</span></div>', unsafe_allow_html=True)
    model_box("viability")
    with st.form("viability_form"):
        a, b, c = st.columns(3)
        with a:
            batch_cost = st.number_input("Costo por lote ($)", 1.0, 10_000_000.0, 4500.0, 100.0)
            units = st.number_input("Unidades por lote", 1, 10000, 50, 5)
            fixed = st.number_input("Costos fijos ($)", 0.0, 10_000_000.0, 15000.0, 500.0)
        with b:
            waste_pct = st.slider("Desperdicio productivo (%)", 0, 80, 8, 1)
            price = st.number_input("Precio de venta ($)", 1.0, 100000.0, 180.0, 10.0)
            demand = st.number_input("Demanda esperada", 1, 100000, 300, 10)
        with c:
            acceptance_pct = st.slider("Aceptacion esperada (%)", 0, 100, 70, 1)
            runs = st.number_input("Numero de simulaciones", 100, 50000, 5000, 500, key="viability_runs", help=RUNS_HELP)
            scenario = st.selectbox("Escenario", ["Optimista", "Esperado", "Pesimista"], index=1, key="viability_scenario")
        submitted = st.form_submit_button("Ejecutar simulacion de viabilidad")
    if submitted:
        with st.spinner("Ejecutando simulacion de viabilidad..."):
            result, checks = compute_viability_result(batch_cost, units, fixed, waste_pct / 100, price, demand, acceptance_pct / 100, runs, scenario, seed, MODEL_CACHE_VERSION)
        st.session_state.viability = result
        st.session_state.verification["Viabilidad"] = checks
        st.success("Simulacion de viabilidad lista.")
    result = st.session_state.viability
    if not result:
        st.info("Ejecuta el simulador para ver rentabilidad y variables criticas.")
        return
    m = result["metrics"]
    break_even = "No alcanzable" if m["punto_equilibrio"] == float("inf") else f"{m['punto_equilibrio']:.0f}"
    k = st.columns(5)
    k[0].metric("Chance rentable", f"{m['probabilidad_rentabilidad_pct']:.1f}%")
    k[1].metric("Ganancia promedio", f"${m['ganancia_promedio']:,.0f}")
    k[2].metric("Ganancia baja", f"${m['ganancia_p10']:,.0f}")
    k[3].metric("Costo unitario", f"${m['costo_unitario_promedio']:,.2f}")
    k[4].metric("Punto equilibrio", break_even)
    if m["punto_equilibrio"] == float("inf"):
        simple_note(
            f"la simulacion da {m['probabilidad_rentabilidad_pct']:.1f}% de chances de ganar dinero. "
            "Con estos costos y precio, el punto de equilibrio no se alcanza."
        )
    else:
        simple_note(
            f"la simulacion da {m['probabilidad_rentabilidad_pct']:.1f}% de chances de ganar dinero. "
            f"El punto de equilibrio queda cerca de {break_even} unidades."
        )
    df = result["simulations"]
    c1, c2 = st.columns(2)
    fig = px.histogram(df, x="ganancia", nbins=35, title="Que ganancia podria aparecer")
    fig.add_vline(x=0, line_dash="dash", line_color="#bf4e45")
    c1.plotly_chart(polish_chart(fig, 380), use_container_width=True)
    plot_df = df.sample(min(len(df), 700), random_state=7).copy()
    plot_df["aceptacion_pct"] = plot_df["aceptacion"] * 100
    c2.plotly_chart(polish_chart(px.scatter(plot_df, x="demanda_efectiva", y="ganancia", color="aceptacion_pct", title="Ganancia segun unidades vendidas"), 380), use_container_width=True)
    decision_panel(m)
    c1, c2 = st.columns(2)
    c1.plotly_chart(bar_chart(result["scenarios"], "escenario", "prob_rentabilidad_pct", "Chance rentable por escenario", "% de simulaciones rentables", color="#1f7a5a"), use_container_width=True)
    c2.plotly_chart(bar_chart(result["scenarios"], "escenario", "ganancia_promedio", "Ganancia promedio por escenario", "$", color="#e07a3f"), use_container_width=True)
    st.plotly_chart(polish_chart(px.bar(result["critical"], x="variable", y="impacto_ganancia", title="Variables criticas por impacto en ganancia"), 360), use_container_width=True)
    c1, c2 = st.columns(2)
    c1.plotly_chart(bar_chart(result["impacts"], "mejora", "ganancia_promedio", "Ganancia si mejora un dato", "$", color="#3f6fb5"), use_container_width=True)
    c2.plotly_chart(bar_chart(result["impacts"], "mejora", "prob_rentabilidad_pct", "Chance rentable si mejora un dato", "% de simulaciones rentables", color="#1f7a5a"), use_container_width=True)


def verification_validation_section() -> None:
    st.header("Chequeos")
    with st.expander("Chequeos internos"):
        if not st.session_state.verification:
            st.info("Ejecuta los simuladores para completar los chequeos.")
        for model, checks in st.session_state.verification.items():
            st.subheader(model)
            for name, ok in checks.items():
                st.write(f"{'Cumple' if ok else 'Revisar'} - {name.replace('_', ' ')}")


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
        {
            "digital": st.session_state.digital,
            "stock": st.session_state.stock,
            "viability": st.session_state.viability,
        },
        st.session_state.verification,
    )
    st.download_button("Generar Informe Markdown", markdown, "informe_vitacookies.md", "text/markdown", use_container_width=True)
    st.download_button("Generar Informe DOCX", cached_docx_report(markdown), "informe_vitacookies.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)


def main() -> None:
    css()
    init_state()
    hero()
    with st.sidebar:
        st.title("VitaCookies")
        st.caption("Panel de simulacion academica")
        seed = st.number_input("Semilla aleatoria", 0, 999999, 42, 1)
        st.link_button("Abrir formulario digital", "https://vita-cookies-form-v.vercel.app/", use_container_width=True)
        st.divider()
        st.caption("Entregables")
        report_buttons()
        st.divider()
        data_guidance()
    tabs = st.tabs(["Formulario", "Porciones", "Viabilidad", "Chequeos"])
    with tabs[0]:
        digital_tab(seed)
    with tabs[1]:
        stock_tab(seed)
    with tabs[2]:
        viability_tab(seed)
    with tabs[3]:
        verification_validation_section()


if __name__ == "__main__":
    main()
