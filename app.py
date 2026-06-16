from __future__ import annotations

from html import escape

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from simulators.post_test_simulator import (
    ACCEPTANCE_SUMMARY,
    BASE_COST_PER_50_UNITS,
    BASE_UNITS_FOR_COST,
    DigitalPostInputs,
    RECOMMENDED_PROFIT_MARGIN,
    StockPostInputs,
    ViabilityPostInputs,
    simulate_digital_post,
    simulate_stock_post,
    simulate_viability_post,
    verification_checks,
)
from utils.report_generator import MODEL_CARDS, generate_docx_report, generate_markdown_report


st.set_page_config(page_title="VitaCookies | Modelos y Simulacion", page_icon=":cookie:", layout="wide")
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
    if st.session_state.digital is None:
        st.session_state.digital = simulate_digital_post(DigitalPostInputs())
        st.session_state.verification["Formulario digital"] = verification_checks(st.session_state.digital)
    if st.session_state.stock is None:
        st.session_state.stock = simulate_stock_post(StockPostInputs())
        st.session_state.verification["Stock"] = verification_checks(st.session_state.stock)
    if st.session_state.viability is None:
        st.session_state.viability = simulate_viability_post(ViabilityPostInputs(0.0, 500))
        st.session_state.verification["Viabilidad"] = verification_checks(st.session_state.viability)


CHART_TEXT = "#17372c"
CHART_MUTED = "#4f6259"
CHART_GRID = "#dfe8df"
CHART_AXIS = "#b7c6bd"
CHART_LABELS = {
    "minuto": "Minuto",
    "utilizacion_pct": "Utilizacion (%)",
    "formularios_activos": "Formularios activos",
    "capacidad": "Capacidad",
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
MODEL_CACHE_VERSION = "post-test-observed-v1"


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
                <div class="eyebrow">Analisis post-testeo</div>
                <h1>VitaCookies</h1>
                <p>Analiza los datos reales del formulario, el stock producido y la proyeccion para producir VitaCookies a mayor escala.</p>
                <div class="hero-meta">
                    <span class="hero-chip">Datos reales</span>
                    <span class="hero-chip">Post-testeo</span>
                    <span class="hero-chip">Indicadores observados</span>
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
                <div><h3>Formulario</h3><p>Resume respuestas reales, horario de carga y pico observado.</p></div>
            </div>
            <div class="workflow-step">
                <div class="step-kicker">02</div>
                <div><h3>Stock</h3><p>Compara galletitas producidas, consumidas y sobrantes.</p></div>
            </div>
            <div class="workflow-step">
                <div class="step-kicker">03</div>
                <div><h3>Escala</h3><p>Relaciona aceptabilidad real, precio, costo de 50 unidades y cantidad a producir.</p></div>
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


def digital_tab() -> None:
    st.markdown('<div class="model-box"><strong>Formulario post-testeo</strong><br><span>Analisis deterministico de respuestas registradas entre 08:10 y 09:32.</span></div>', unsafe_allow_html=True)
    model_box("digital")
    with st.form("digital_form"):
        a, b, c = st.columns(3)
        with a:
            responses = st.number_input("Respuestas registradas", 1, 5000, 44, 1)
        with b:
            duration = st.number_input("Duracion observada (min)", 1, 480, 82, 1)
        with c:
            capacity = st.number_input("Capacidad aceptable por minuto", 1, 500, 20, 1)
        submitted = st.form_submit_button("Actualizar analisis digital")
    if submitted:
        result = simulate_digital_post(DigitalPostInputs(responses, duration, capacity))
        st.session_state.digital = result
        st.session_state.verification["Formulario digital"] = verification_checks(result)
        st.success("Analisis digital actualizado.")
    result = st.session_state.digital
    m = result["metrics"]
    k = st.columns(5)
    k[0].metric("Respuestas", f"{m['respuestas_registradas']}")
    k[1].metric("Duracion", f"{m['duracion_recoleccion_min']} min")
    k[2].metric("Pico/min", f"{m['pico_respuestas_minuto']}")
    k[3].metric("Min. saturados", f"{m['minutos_saturados']}")
    k[4].metric("Uso max.", f"{m['utilizacion_maxima_pct']:.1f}%")
    simple_note(
        f"el pico observado fue de {m['pico_respuestas_minuto']} respuestas en un minuto. "
        "No se usan corridas aleatorias: la lectura sale de las marcas horarias reales."
    )
    tl = result["timeline"]
    c1, c2 = st.columns(2)
    c1.plotly_chart(polish_chart(px.bar(tl, x="minuto", y="respuestas", title="Respuestas reales por minuto"), 360), use_container_width=True)
    c2.plotly_chart(polish_chart(px.line(tl, x="minuto", y="acumulado", title="Respuestas acumuladas"), 360), use_container_width=True)
    decision_panel(m)


def stock_tab() -> None:
    st.markdown('<div class="model-box"><strong>Stock real de galletitas</strong><br><span>Calculo con unidades producidas, consumidas y sobrantes observadas.</span></div>', unsafe_allow_html=True)
    model_box("stock")
    with st.form("stock_form"):
        a, b, c = st.columns(3)
        with a:
            produced = st.number_input("Galletitas producidas", 1, 5000, 50, 1)
        with b:
            leftover = st.number_input("Sobrantes aproximadas", 0, 5000, 5, 1)
        with c:
            responses = st.number_input("Respuestas del formulario", 1, 5000, 44, 1, key="stock_responses")
        submitted = st.form_submit_button("Actualizar analisis de stock")
    if submitted:
        result = simulate_stock_post(StockPostInputs(produced, leftover, responses))
        st.session_state.stock = result
        st.session_state.verification["Stock"] = verification_checks(result)
        st.success("Analisis de stock actualizado.")
    result = st.session_state.stock
    m = result["metrics"]
    k = st.columns(5)
    k[0].metric("Producidas", f"{m['galletitas_producidas']}")
    k[1].metric("Consumidas", f"{m['galletitas_consumidas']}")
    k[2].metric("Sobrantes", f"{m['galletitas_sobrantes']}")
    k[3].metric("Consumo", f"{m['consumo_pct']:.1f}%")
    k[4].metric("Sugeridas", f"{m['produccion_sugerida_proximo_testeo']}")
    simple_note(
        f"se consumieron {m['galletitas_consumidas']} de {m['galletitas_producidas']} galletitas. "
        f"El sobrante aproximado fue {m['sobrante_pct']:.1f}%."
    )
    st.plotly_chart(polish_chart(px.bar(result["rows"], x="concepto", y="unidades", title="Balance real de stock"), 360), use_container_width=True)
    decision_panel(m)


def viability_tab() -> None:
    st.markdown('<div class="model-box"><strong>Aceptabilidad y escala productiva</strong><br><span>Proyeccion para producir mas galletitas usando la aceptabilidad real fija del testeo: 41 respuestas positivas sobre 50.</span></div>', unsafe_allow_html=True)
    model_box("viability")
    fixed_acceptability = ACCEPTANCE_SUMMARY["positive_satisfaction"] / ACCEPTANCE_SUMMARY["responses"] * 100
    unit_cost = BASE_COST_PER_50_UNITS / BASE_UNITS_FOR_COST
    simple_note(
        f"la aceptabilidad queda fija por el testeo: {fixed_acceptability:.1f}% "
        f"({ACCEPTANCE_SUMMARY['positive_satisfaction']} respuestas positivas sobre {ACCEPTANCE_SUMMARY['responses']} galletitas testeadas). "
        f"El costo tambien queda fijo: ${BASE_COST_PER_50_UNITS:,.0f} cada {BASE_UNITS_FOR_COST} galletitas, es decir ${unit_cost:,.0f} por unidad producida."
    )
    with st.form("viability_form"):
        a, b = st.columns(2)
        with a:
            price = st.number_input("Precio de venta unitario ($)", 0.0, 100000.0, 0.0, 10.0)
        with b:
            target = st.number_input("Cantidad a producir", 1, 100000, 500, 50)
        submitted = st.form_submit_button("Actualizar viabilidad")
    if submitted:
        result = simulate_viability_post(ViabilityPostInputs(price, target))
        st.session_state.viability = result
        st.session_state.verification["Viabilidad"] = verification_checks(result)
        st.success("Viabilidad actualizada.")
    result = st.session_state.viability
    m = result["metrics"]
    break_even_price = "Pendiente" if m["precio_equilibrio"] == float("inf") else f"${m['precio_equilibrio']:,.2f}"
    recommended_price = "Pendiente" if m["precio_recomendado"] == float("inf") else f"${m['precio_recomendado']:,.2f}"
    k = st.columns(5)
    k[0].metric("Costo total", f"${m['costo_estimado']:,.0f}")
    k[1].metric("Vendidas est.", f"{m['unidades_aceptadas_estimadas']}")
    k[2].metric("Sobrante est.", f"{m['unidades_no_vendidas_estimadas']}")
    k[3].metric("Ganancia/Perdida", f"${m['ganancia_estimada']:,.0f}")
    k[4].metric("Precio recom.", recommended_price)
    simple_note(
        f"para producir {m['produccion_objetivo']} galletitas el costo estimado es ${m['costo_estimado']:,.0f} "
        f"(${m['costo_unitario_estimado']:,.0f} por unidad). "
        f"El precio minimo para no perder plata es {break_even_price}; para ganar alrededor de {RECOMMENDED_PROFIT_MARGIN * 100:.0f}% conviene apuntar a {recommended_price}."
    )
    c1, c2 = st.columns(2)
    scores = result["scores"].copy()
    score_fig = px.bar(
        scores,
        x="atributo",
        y="promedio",
        text="promedio",
        title="Puntajes sensoriales promedio",
        color="atributo",
    )
    score_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    score_fig.update_yaxes(range=[0, 5])
    c1.plotly_chart(polish_chart(score_fig, 360), use_container_width=True)

    financial_df = result["financial_summary"]
    financial = px.bar(
        financial_df,
        x="concepto",
        y="monto",
        text="monto",
        title="Resultado proyectado para la produccion elegida",
        color="concepto",
    )
    financial.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    c2.plotly_chart(polish_chart(financial, 360), use_container_width=True)

    projection = result["scenarios"].melt(
        id_vars="produccion",
        value_vars=["ingresos_estimados", "costo_estimado", "ganancia_estimada"],
        var_name="indicador",
        value_name="monto",
    )
    projection["indicador"] = projection["indicador"].map(
        {
            "ingresos_estimados": "Ingresos",
            "costo_estimado": "Costo",
            "ganancia_estimada": "Ganancia",
        }
    )
    projection_fig = px.line(
        projection,
        x="produccion",
        y="monto",
        color="indicador",
        markers=True,
        title="Proyeccion por volumen de produccion",
    )
    projection_fig.update_yaxes(tickprefix="$")
    st.plotly_chart(polish_chart(projection_fig, 360), use_container_width=True)
    decision_panel(m)


def verification_validation_section() -> None:
    st.header("Chequeos")
    with st.expander("Chequeos internos"):
        if not st.session_state.verification:
            st.info("Carga los datos post-testeo para completar los chequeos.")
        for model, checks in st.session_state.verification.items():
            st.subheader(model)
            for name, ok in checks.items():
                st.write(f"{'Cumple' if ok else 'Revisar'} - {name.replace('_', ' ')}")
    with st.expander("Validacion contra el evento real"):
        st.markdown(
            """
            Esta version ya usa las mediciones del testeo:

            - respuestas reales del formulario;
            - horario real de carga y pico por minuto;
            - galletitas producidas, consumidas y sobrantes;
            - aceptacion sensorial real obtenida del formulario;
            - puntajes descriptivos reales de color, aroma, sabor y textura.

            Los unicos valores editables que no vienen del Excel son los economicos: costo y precio.
            """
        )


def data_guidance() -> None:
    with st.expander("Datos post-testeo cargados"):
        st.markdown(
            """
            La herramienta ahora trabaja con mediciones reales del testeo:

            - **Formulario:** 44 respuestas registradas entre 08:10 y 09:32.
            - **Stock:** 50 galletitas producidas y 5 sobrantes aproximadas.
            - **Aceptabilidad:** 41 respuestas positivas sobre 50 galletitas testeadas.
            - **Descriptivo:** sabor fue el atributo mejor puntuado; textura quedo como principal punto de mejora.
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
        st.caption("Panel post-testeo")
        st.link_button("Abrir formulario digital", "https://vita-cookies-form-v.vercel.app/", use_container_width=True)
        st.divider()
        st.caption("Entregables")
        report_buttons()
        st.divider()
        data_guidance()
    tabs = st.tabs(["Formulario", "Porciones", "Viabilidad", "Chequeos"])
    with tabs[0]:
        digital_tab()
    with tabs[1]:
        stock_tab()
    with tabs[2]:
        viability_tab()
    with tabs[3]:
        verification_validation_section()


if __name__ == "__main__":
    main()
