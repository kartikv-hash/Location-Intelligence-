
import io
import json
import os
import hashlib
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import numpy as np
import folium
from folium.plugins import Draw, MousePosition
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from fpdf import FPDF


# ============================================================
# SUNSTRIPE SELECT
# Solar | Wind | Battery Energy Storage Systems
# ============================================================

st.set_page_config(
    page_title="Sunstripe SELECT",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG = "#FBF9F7"
NAVY = "#050714"
RED = "#E8392D"
BLACK = "#000000"
WHITE = "#FFFFFF"
LINE = "#E7E0DB"
FONT = "Inter, 'DM Sans', Arial, sans-serif"

TECH_COLORS = {
    "Solar": "#D9A72E",
    "Wind": "#41986A",
    "BESS": "#3979CC",
    "Other": "#89817B",
}

# Transmission-line colors by nominal voltage (kV).
# Requested examples: 138 kV = orange; 240 kV = green.
VOLTAGE_COLORS = {
    34.5: "#17A2B8",  # Teal
    46:   "#5B8E7D",  # Sage
    69:   "#8E44AD",  # Purple
    115:  "#2F80ED",  # Blue
    138:  "#F28C28",  # Orange
    161:  "#D94841",  # Vermilion
    230:  "#6C5CE7",  # Violet
    240:  "#2E8B57",  # Green
    345:  "#C49A00",  # Gold
    500:  "#C1121F",  # Deep red
    765:  "#343A40",  # Charcoal
}
UNKNOWN_VOLTAGE_COLOR = "#777777"
CUSTOM_VOLTAGE_PALETTE = [
    "#008C95", "#AA3377", "#4477AA", "#CC6677", "#228833",
    "#66CCEE", "#AA4499", "#999933", "#332288", "#DDCC77",
]

EIA_PAGE = "https://www.eia.gov/electricity/data/eia860m/index.php"
MAX_UPLOAD_MB = 50

# Plotly renamed the Mapbox Express API to MapLibre in newer releases.
# Select the available API at runtime so the app works across Streamlit Cloud
# environments instead of crashing on px.scatter_mapbox in newer Plotly.
USE_MAPLIBRE_API = hasattr(px, "scatter_map") and hasattr(go, "Scattermap")
MAP_TRACE_CLASS = go.Scattermap if USE_MAPLIBRE_API else go.Scattermapbox
MAP_LAYOUT_KEY = "map" if USE_MAPLIBRE_API else "mapbox"


# ============================================================
# THEME: SUNSTRIPE BLACK, IVORY AND RED
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

/* One consistent, modern type system across Streamlit widgets and page content. */
html, body, button, input, textarea, select,
[data-testid="stAppViewContainer"] *,
[data-testid="stSidebar"] * {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
}

/* Keep Streamlit's icon glyphs on their own icon font. */
.material-icons, .material-symbols-rounded, [data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}

.stApp {
    background: #FBF9F7;
    color: #000000 !important;
}

.block-container {
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

/* Main-page typography */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main small,
[data-testid="stAppViewContainer"] .main strong {
    color: #000000;
}

/* Sunstripe header */
.topbar {
    background: #050714;
    color: #FFFFFF;
    margin: -1rem -1rem 1.7rem -1rem;
    padding: 22px 24px 15px;
    border-bottom: 2px solid #E8392D;
}

.brand {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    text-align: center;
    font-size: 25px;
    font-weight: 700;
    letter-spacing: -0.7px;
    color: #FFFFFF !important;
}

.brand .accent {
    color: #E8392D !important;
}

.brand-tagline {
    text-align: center;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1.8px;
    color: #FFFFFF !important;
    text-transform: uppercase;
    margin-top: 5px;
}

.navrow {
    display: flex;
    justify-content: center;
    gap: 27px;
    flex-wrap: wrap;
    margin-top: 20px;
    font-size: 13px;
    font-weight: 600;
}

.navitem {
    padding: 8px 0;
    color: #FFFFFF !important;
    border-bottom: 2px solid transparent;
}

.navitem.active {
    color: #E8392D !important;
    border-color: #E8392D;
}

/* Main heading */
.eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #E8392D !important;
    margin: 5px 0 12px;
}

.hero {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    font-size: clamp(32px, 3.4vw, 43px);
    font-weight: 700;
    font-style: normal;
    line-height: 1.18;
    letter-spacing: -1.2px;
    color: #E8392D !important;
    margin: 10px 0 14px;
}

.subtitle {
    font-size: 15px;
    font-weight: 400;
    line-height: 1.7;
    color: #000000 !important;
    max-width: 900px;
    margin-bottom: 24px;
}

/* KPI cards */
.kpi-card {
    background: rgba(255,255,255,0.75);
    border: 1px solid #E7E0DB;
    padding: 17px 18px;
    min-height: 100px;
    border-radius: 2px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.25;
    color: #E8392D !important;
    overflow-wrap: anywhere;
}

.kpi-label {
    font-size: 12px;
    font-weight: 500;
    color: #000000 !important;
    margin-top: 8px;
    line-height: 1.5;
}

.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #000000 !important;
    border-top: 1px solid #E7E0DB;
    padding-top: 18px;
    margin-top: 22px;
    margin-bottom: 12px;
}

.pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 14px 0 20px;
}

.pill {
    border: 1px solid #E7E0DB;
    border-radius: 20px;
    padding: 7px 12px;
    background: #FFFDFA;
    color: #000000 !important;
    font-size: 12px;
    font-weight: 500;
}

/* Visible tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 22px;
    border-bottom: 1px solid #E7E0DB;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
    border-radius: 0;
    padding: 12px 0;
    color: #000000 !important;
}

.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {
    color: #000000 !important;
    font-size: 13px !important;
}

.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {
    color: #E8392D !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.75);
    border: 1px solid #E7E0DB;
    border-radius: 2px;
    padding: 14px;
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color: #000000 !important;
}

div[data-testid="stMetricValue"] {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    font-size: 26px;
    font-weight: 700;
    color: #E8392D !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    font-size: 13px;
    font-weight: 600;
    border-radius: 22px;
    border: 1px solid #E8392D;
    color: #E8392D !important;
    background: transparent;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #E8392D !important;
    color: #FFFFFF !important;
}

/* Captions, dataframes and labels */
div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] *,
div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] *,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color: #000000 !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #E7E0DB;
}

.stApp input, .stApp textarea {
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    color: #000000 !important;
}

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #000000 !important;
    opacity: 0.7;
}

/* Sunstripe AI chat: readable input, soft borders and warm, friendly message cards. */
div[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1px solid #E7DCD5 !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 28px rgba(25, 20, 35, 0.09) !important;
    padding: 5px 8px !important;
    transition: border-color .18s ease, box-shadow .18s ease;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #E8392D !important;
    box-shadow: 0 0 0 3px rgba(232, 57, 45, 0.12), 0 10px 28px rgba(25, 20, 35, 0.08) !important;
}
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] [data-baseweb="textarea"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #171923 !important;
    caret-color: #E8392D !important;
    font-family: 'Inter', 'DM Sans', Arial, sans-serif !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #777681 !important;
    opacity: 1 !important;
}
div[data-testid="stChatInput"] button {
    background: #E8392D !important;
    color: #FFFFFF !important;
    border: 0 !important;
    border-radius: 12px !important;
    min-width: 38px !important;
    min-height: 38px !important;
    transition: transform .16s ease, background .16s ease;
}
div[data-testid="stChatInput"] button:hover {
    background: #C92C24 !important;
    transform: translateY(-1px);
}
div[data-testid="stChatMessage"] {
    border: 1px solid #EEE4DE;
    border-radius: 18px;
    background: #FFFFFF;
    padding: 14px 17px;
    margin: 10px 0;
    box-shadow: 0 4px 14px rgba(25, 20, 35, 0.035);
}
/* Keep all AI response content readable on the white chat card, especially tables. */
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] td,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] th {
    color: #171923 !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] table {
    color: #171923 !important;
    border-collapse: collapse !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] th {
    background: #F3F4F6 !important;
    color: #111827 !important;
    font-weight: 700 !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] td,
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] th {
    border-bottom: 1px solid #E5E7EB !important;
    padding: 8px 10px !important;
}
div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] a {
    color: #B42318 !important;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #FFFFFF 0%, #FFF9F5 100%);
    border-color: #F0E4DD;
}
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #FFF1EB;
    border-color: #F2D4C9;
}
.stButton button {
    transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 13px rgba(232, 57, 45, 0.12);
}

hr {
    border-color: #E7E0DB;
}

/* Dark sidebar */
section[data-testid="stSidebar"] {
    background: #050714;
    border-right: 1px solid #272936;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] hr {
    border-color: #343542;
}

section[data-testid="stSidebar"] input {
    background: #FFFFFF !important;
    color: #000000 !important;
}

.footer {
    text-align: center;
    color: #000000 !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 10px 0;
}

/* Sunstripe AI welcome card and starter prompts. */
.ss-ai-hero {
    display: flex;
    align-items: flex-start;
    gap: 18px;
    position: relative;
    overflow: hidden;
    background: linear-gradient(115deg, #FFF1E9 0%, #FFFAF6 56%, #F6F4FB 100%);
    border: 1px solid #F0DED5;
    border-top: 3px solid #E8392D;
    border-radius: 22px;
    padding: 22px 24px 20px;
    margin: 6px 0 14px;
    box-shadow: 0 10px 30px rgba(42, 28, 34, 0.045);
}
.ss-ai-hero::after {
    content: "";
    position: absolute;
    width: 170px;
    height: 170px;
    border-radius: 50%;
    right: -50px;
    top: -82px;
    background: rgba(232, 57, 45, 0.065);
    pointer-events: none;
}
.ss-ai-orb {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 48px;
    width: 48px;
    height: 48px;
    border-radius: 16px;
    color: #FFFFFF !important;
    font-size: 25px;
    background: linear-gradient(145deg, #F54C3F 0%, #D52D25 100%);
    box-shadow: 0 7px 17px rgba(232, 57, 45, 0.22);
}
.ss-ai-copy { min-width: 0; flex: 1; }
.ss-ai-eyebrow {
    font-size: 10px;
    font-weight: 800;
    line-height: 1.4;
    letter-spacing: 1.55px;
    color: #D93429 !important;
    margin: 1px 0 6px;
}
.ss-ai-eyebrow span { color: #B9A39A !important; padding: 0 4px; }
.ss-ai-title {
    font-size: clamp(21px, 2.2vw, 27px);
    font-weight: 750;
    line-height: 1.24;
    letter-spacing: -0.75px;
    color: #111526 !important;
    margin: 0 0 7px;
}
.ss-ai-description {
    max-width: 800px;
    color: #55515A !important;
    font-size: 13px;
    line-height: 1.65;
}
.ss-ai-tags { display: flex; gap: 7px; flex-wrap: wrap; margin-top: 13px; }
.ss-ai-tags span {
    padding: 5px 10px;
    border: 1px solid rgba(221, 205, 197, .88);
    border-radius: 999px;
    background: rgba(255,255,255,.72);
    color: #39343A !important;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}
.ss-ai-live {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    flex: 0 0 auto;
    margin: 2px 0 0 auto;
    padding: 7px 10px;
    border: 1px solid #D8E9D9;
    border-radius: 999px;
    background: rgba(255,255,255,.75);
    color: #386846 !important;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}
.ss-ai-live-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #38A169;
    box-shadow: 0 0 0 3px rgba(56,161,105,.12);
}

@media (max-width: 768px) {
    .brand { font-size: 22px; }
    .navrow { gap: 14px; font-size: 12px; }
    .hero { font-size: 32px; letter-spacing: -0.7px; }
    .subtitle { font-size: 14px; }
    .ss-ai-hero { padding: 17px 15px; gap: 12px; border-radius: 18px; }
    .ss-ai-orb { flex-basis: 40px; width: 40px; height: 40px; border-radius: 13px; }
    .ss-ai-live { display: none; }
    .ss-ai-title { font-size: 21px; }
    .ss-ai-description { font-size: 12px; }
    .ss-ai-tags { gap: 5px; }
    .ss-ai-tags span { font-size: 10px; padding: 4px 8px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# PLOTLY THEME
# ============================================================

def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=13, color=BLACK),
        title=dict(
            font=dict(family=FONT, size=16, color=BLACK),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            font=dict(family=FONT, size=12, color=BLACK),
            title=dict(font=dict(family=FONT, size=12, color=BLACK)),
            bgcolor="rgba(251,249,247,0)",
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        margin=dict(t=65, b=40, l=45, r=25),
        hoverlabel=dict(
            bgcolor=WHITE,
            font=dict(family=FONT, size=12, color=BLACK),
            bordercolor=LINE,
        ),
    )

    fig.update_xaxes(
        title_font=dict(family=FONT, size=12, color=BLACK),
        tickfont=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showline=True,
        linecolor=LINE,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        title_font=dict(family=FONT, size=12, color=BLACK),
        tickfont=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showgrid=True,
        gridcolor=LINE,
        zeroline=False,
    )

    return fig


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def column_key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def check_upload_size(upload):
    if upload is not None and upload.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"Upload must be smaller than {MAX_UPLOAD_MB} MB.")


# ============================================================
# STANDARDIZE ASSET DATA
# This function is used by ALL data sources.
# It always creates technology_display.
# ============================================================

def standardize_assets(
    data,
    source_name="User dataset",
    source_url="",
):
    df = data.copy()

    # Preserve input field names while cleaning whitespace.
    df.columns = [
        str(c).strip().replace("\n", " ")
        for c in df.columns
    ]

    lookup = {}
    for col in df.columns:
        lookup.setdefault(column_key(col), col)

    def find_column(candidates):
        for candidate in candidates:
            found = lookup.get(column_key(candidate))
            if found is not None:
                return found
        return None

    aliases = {
        "plant_name": [
            "plant name", "plant_name", "project name",
            "project_name", "facility name", "facility_name", "name",
        ],
        "state": [
            "plant state", "state", "state name",
            "plant state abbreviation",
        ],
        "county": ["county", "plant county", "county name"],
        "plant_code": ["plant code", "plant id", "plant_id"],
        "generator_id": ["generator id", "generator"],
        "entity_name": [
            "entity name", "utility name", "operator", "owner",
        ],
        "entity_id": ["entity id", "utility id"],
        "producer_type": ["plant producer type", "producer type"],
        "technology_group": [
            "technology group", "technology_group", "technology",
            "technology type", "energy type", "fuel type",
        ],
        "technology_display": ["technology_display", "technology display"],
        "energy_source_code": ["energy source code", "energy source"],
        "prime_mover_code": ["prime mover code", "prime mover"],
        "nameplate_capacity_mw": [
            "nameplate capacity (mw)", "nameplate capacity mw",
            "nameplate_capacity_mw", "capacity (mw)", "capacity_mw",
            "nameplate mw", "mw",
        ],
        "net_summer_capacity_mw": [
            "net summer capacity (mw)", "net summer capacity mw",
        ],
        "energy_capacity_mwh": [
            "energy capacity mwh", "energy_capacity_mwh",
            "storage capacity mwh", "nameplate energy capacity mwh",
            "nameplate_energy_capacity_mwh",
        ],
        "status": [
            "status", "operating status", "lifecycle status",
            "lifecycle group", "lifecycle_group", "project status",
        ],
        "operating_year": ["operating year"],
        "operating_month": ["operating month"],
        "planned_operating_year": ["planned operating year", "planned year"],
        "planned_operating_month": ["planned operating month", "planned month"],
        "latitude": [
            "plant latitude", "latitude", "plant_latitude", "lat",
        ],
        "longitude": [
            "plant longitude", "longitude", "plant_longitude", "lon", "lng",
        ],
    }

    # Save a supplied preclassified technology field before rebuilding it.
    supplied_technology_display = None
    display_col = find_column(["technology_display", "technology display"])

    if display_col is not None:
        supplied_technology_display = df[display_col].copy()

    # Build the standard fields. Never rely on a column already being present.
    for standard, candidates in aliases.items():
        if standard == "technology_display":
            continue

        original = find_column(candidates)

        if standard not in df.columns and original is not None:
            df[standard] = df[original]

    defaults = {
        "plant_name": "Unnamed asset",
        "state": "Unknown",
        "county": "Unknown",
        "plant_code": None,
        "generator_id": None,
        "entity_name": "Not reported",
        "entity_id": None,
        "producer_type": "Not reported",
        "technology_group": "Unknown",
        "energy_source_code": "",
        "prime_mover_code": "",
        "nameplate_capacity_mw": None,
        "net_summer_capacity_mw": None,
        "energy_capacity_mwh": None,
        "status": "Not reported",
        "operating_year": None,
        "operating_month": None,
        "planned_operating_year": None,
        "planned_operating_month": None,
        "latitude": None,
        "longitude": None,
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    numeric_columns = [
        "nameplate_capacity_mw",
        "net_summer_capacity_mw",
        "energy_capacity_mwh",
        "latitude",
        "longitude",
        "operating_year",
        "operating_month",
        "planned_operating_year",
        "planned_operating_month",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in [
        "plant_name",
        "state",
        "county",
        "entity_name",
        "technology_group",
        "status",
    ]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    # Technology classification using the reported technology, fuel code,
    # prime mover and any supplied preclassified technology.
    technology = df["technology_group"].fillna("").astype(str).str.lower()
    energy = df["energy_source_code"].fillna("").astype(str).str.lower()
    mover = df["prime_mover_code"].fillna("").astype(str).str.lower()

    is_bess = (
        technology.str.contains(r"battery|storage|bess", regex=True)
        | mover.str.fullmatch("ba", na=False)
        | energy.str.fullmatch("mwh", na=False)
    )

    is_wind = (
        technology.str.contains("wind", na=False)
        | energy.str.fullmatch("wnd", na=False)
        | energy.str.fullmatch("wds", na=False)
    )

    is_solar = (
        technology.str.contains(
            r"solar|photovoltaic|concentrat|solar pv",
            regex=True,
        )
        | energy.str.fullmatch("sun", na=False)
        | mover.str.fullmatch("pv", na=False)
    )

    # IMPORTANT: technology_display is ALWAYS explicitly created here.
    df["technology_display"] = "Other"
    df.loc[is_solar, "technology_display"] = "Solar"
    df.loc[is_wind, "technology_display"] = "Wind"
    df.loc[is_bess, "technology_display"] = "BESS"

    # Preserve recognized labels supplied by the source.
    if supplied_technology_display is not None:
        supplied = (
            supplied_technology_display
            .reindex(df.index)
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        supplied_mapping = {
            "solar": "Solar",
            "pv": "Solar",
            "wind": "Wind",
            "bess": "BESS",
            "battery": "BESS",
            "battery storage": "BESS",
            "storage": "BESS",
            "other": "Other",
        }

        mapped = supplied.map(supplied_mapping)
        valid = mapped.notna()
        df.loc[valid, "technology_display"] = mapped[valid]

    # Assign provenance.
    df["source_dataset"] = source_name
    df["source_url"] = source_url or ""

    df = df.reset_index(drop=True)

    # Stable within this loaded dataset; unique even for repeated plant IDs.
    plant = df["plant_code"].fillna("").astype(str)
    generator = df["generator_id"].fillna("").astype(str)

    df["record_id"] = [
        f"{plant.iloc[i]}-{generator.iloc[i]}-{i}"
        for i in range(len(df))
    ]

    return df


# ============================================================
# CSV / EXCEL INPUT
# ============================================================

@st.cache_data
def load_repository_csv():
    raw = pd.read_csv("renewable_asset_register.csv")

    # FIX: repository CSV must go through the same standardizer
    # as uploads and the EIA data before filtering.
    return standardize_assets(
        raw,
        source_name="Repository CSV",
    )


def load_uploaded_file(upload):
    check_upload_size(upload)
    filename = upload.name.lower()

    if filename.endswith(".csv"):
        raw = pd.read_csv(upload)
    elif filename.endswith(".xlsx"):
        raw = pd.read_excel(upload, engine="openpyxl")
    elif filename.endswith(".xls"):
        raw = pd.read_excel(upload, engine="xlrd")
    else:
        raise ValueError("Please upload a CSV, XLSX or XLS file.")

    return standardize_assets(
        raw,
        source_name=f"Uploaded: {upload.name}",
    )


# ============================================================
# OPTIONAL EIA DOWNLOAD
# Only runs when the user explicitly selects EIA live inventory.
# ============================================================

def detect_workbook_engine(content):
    if content.startswith(b"PK"):
        return "openpyxl"

    if content.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        return "xlrd"

    return None


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def download_eia_inventory():
    headers = {
        "User-Agent": "Mozilla/5.0 SunstripeLocationIntelligence/1.0",
        "Accept": "*/*",
        "Referer": EIA_PAGE,
    }

    page_response = requests.get(
        EIA_PAGE,
        headers=headers,
        timeout=20,
    )
    page_response.raise_for_status()

    hrefs = re.findall(
        r"""href\s*=\s*["']([^"']+\.(?:xlsx|xls|zip)(?:\?[^"']*)?)["']""",
        page_response.text,
        flags=re.IGNORECASE,
    )

    candidates = []

    for href in hrefs:
        url = urljoin(EIA_PAGE, href)

        if (
            any(ext in url.lower() for ext in [".xlsx", ".xls", ".zip"])
            and url not in candidates
        ):
            candidates.append(url)

    if not candidates:
        raise RuntimeError(
            "No Excel or ZIP workbook links were detected on the EIA page."
        )

    errors = []

    for url in candidates[:8]:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=45,
            )
            response.raise_for_status()
            content = response.content

            if not content:
                raise ValueError("Download is empty.")

            # If EIA links to a ZIP archive, locate an Excel workbook within it.
            if zipfile.is_zipfile(io.BytesIO(content)):
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    excel_files = [
                        name for name in archive.namelist()
                        if name.lower().endswith((".xlsx", ".xls"))
                        and not name.startswith("__MACOSX/")
                    ]

                    if not excel_files:
                        raise ValueError(
                            "ZIP archive contains no Excel workbook."
                        )

                    # Prefer generator-related workbook names.
                    excel_files.sort(
                        key=lambda name: (
                            "generator" not in name.lower(),
                            name.lower(),
                        )
                    )

                    content = archive.read(excel_files[0])

            engine = detect_workbook_engine(content)

            if engine is None:
                content_type = response.headers.get(
                    "Content-Type", "unknown"
                )
                preview = content[:100].decode(
                    "utf-8", errors="replace"
                ).replace("\n", " ")

                raise ValueError(
                    "Response is not a recognized Excel file. "
                    f"Content-Type={content_type}; preview={preview[:80]}"
                )

            # Verify format before returning the bytes.
            pd.ExcelFile(io.BytesIO(content), engine=engine)

            return content, url, engine

        except Exception as exc:
            errors.append(
                f"{url}: {type(exc).__name__}: {exc}"
            )

    raise RuntimeError(
        "Could not download a readable EIA workbook.\n"
        + "\n".join(errors)
    )


def find_header_row(df):
    for i in range(min(40, len(df))):
        values = [
            column_key(value)
            for value in df.iloc[i].tolist()
            if pd.notna(value)
        ]

        has_plant = any("plantname" in value for value in values)
        has_generator = any("generatorid" in value for value in values)
        has_technology = any("technology" in value for value in values)
        has_capacity = any("capacity" in value for value in values)

        if has_plant and (
            has_generator or has_technology or has_capacity
        ):
            return i

    return None


def parse_eia_workbook(content, engine):
    excel = pd.ExcelFile(
        io.BytesIO(content),
        engine=engine,
    )

    frames = []

    for sheet in excel.sheet_names:
        raw = pd.read_excel(
            io.BytesIO(content),
            sheet_name=sheet,
            header=None,
            engine=engine,
        )

        if raw.empty:
            continue

        header_row = find_header_row(raw)

        if header_row is None:
            continue

        headers = [
            str(value).strip() if pd.notna(value)
            else f"unnamed_{i}"
            for i, value in enumerate(raw.iloc[header_row].tolist())
        ]

        table = raw.iloc[header_row + 1:].copy()
        table.columns = headers
        table = table.dropna(how="all")

        table = table[
            [
                col for col in table.columns
                if not str(col).lower().startswith("unnamed")
            ]
        ].copy()

        if not table.empty:
            table["EIA Workbook Sheet"] = sheet
            frames.append(table)

    if not frames:
        raise RuntimeError(
            "The workbook opened, but no recognizable generator table "
            "was found. The workbook layout may have changed."
        )

    return pd.concat(frames, ignore_index=True, sort=False)


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def load_eia_assets():
    content, workbook_url, engine = download_eia_inventory()

    raw = parse_eia_workbook(content, engine)

    normalized = standardize_assets(
        raw,
        source_name="EIA-860M monthly inventory",
        source_url=workbook_url,
    )

    normalized = normalized[
        normalized["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()

    if normalized.empty:
        raise RuntimeError(
            "No Solar, Wind or BESS records were recognized in the workbook."
        )

    return normalized, workbook_url


# ============================================================
# TRANSMISSION GRID LINE INGESTION AND VOLTAGE STYLING
# Supports GeoJSON LineString/MultiLineString and CSV lines with
# a GeoJSON/WKT geometry field or from/to endpoint coordinates.
# ============================================================

def normalize_voltage_kv(raw_value):
    """Return a display label such as '138 kV' from kV or volt values."""
    if raw_value is None or pd.isna(raw_value):
        return "Unknown kV"

    text = str(raw_value).strip()
    if not text or text.lower() in {"nan", "none", "null", "unknown", "n/a"}:
        return "Unknown kV"

    # Handle multiple voltage values by using the first reported value.
    # Example: '138000;230000' -> 138 kV. Review multi-voltage assets at source.
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", " "))
    if not match:
        return "Unknown kV"

    try:
        value = float(match.group(0))
    except ValueError:
        return "Unknown kV"

    # Most GIS datasets store voltage in volts (e.g. 138000 V); others store kV.
    if abs(value) >= 1000:
        value /= 1000.0

    if value <= 0 or value > 1500:
        return "Unknown kV"

    if abs(value - round(value)) < 0.15:
        value = int(round(value))
        return f"{value} kV"

    return f"{value:g} kV"


def voltage_value_from_label(label):
    match = re.search(r"\d+(?:\.\d+)?", str(label))
    return float(match.group(0)) if match else float("inf")


def build_voltage_color_map(labels):
    """Provide a distinct, stable color for each voltage level in the upload."""
    labels = set(labels)
    color_map = {}
    if "Unknown kV" in labels:
        color_map["Unknown kV"] = UNKNOWN_VOLTAGE_COLOR
    custom_labels = []

    for label in labels:
        value = voltage_value_from_label(label)
        if value == float("inf"):
            continue

        matched_key = next(
            (key for key in VOLTAGE_COLORS if abs(float(key) - value) < 0.15),
            None,
        )
        if matched_key is not None:
            color_map[label] = VOLTAGE_COLORS[matched_key]
        else:
            custom_labels.append(label)

    custom_labels.sort(key=lambda x: (voltage_value_from_label(x), x))
    for i, label in enumerate(custom_labels):
        color_map[label] = CUSTOM_VOLTAGE_PALETTE[i % len(CUSTOM_VOLTAGE_PALETTE)]

    return color_map


def iter_line_segments(geometry):
    """Yield coordinate sequences from GeoJSON line geometries."""
    if not isinstance(geometry, dict):
        return

    geom_type = geometry.get("type", "")
    coordinates = geometry.get("coordinates")

    if geom_type == "LineString" and isinstance(coordinates, list):
        yield coordinates
    elif geom_type == "MultiLineString" and isinstance(coordinates, list):
        for segment in coordinates:
            yield segment
    elif geom_type == "GeometryCollection":
        for child in geometry.get("geometries", []):
            yield from iter_line_segments(child)
    elif geom_type == "Feature":
        yield from iter_line_segments(geometry.get("geometry", {}))


def clean_coordinate_segment(coordinates):
    """Validate GeoJSON coordinate tuples [longitude, latitude, ...]."""
    if not isinstance(coordinates, (list, tuple)):
        return None

    clean = []
    for point in coordinates:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        try:
            lon, lat = float(point[0]), float(point[1])
        except (TypeError, ValueError):
            continue
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            clean.append((lon, lat))

    return clean if len(clean) >= 2 else None


def parse_wkt_linestring(value):
    """Parse WKT LINESTRING and MULTILINESTRING values from grid CSVs."""
    if not isinstance(value, str):
        return []
    text = value.strip()
    upper = text.upper()
    if not (upper.startswith("LINESTRING") or upper.startswith("MULTILINESTRING")):
        return []

    # Split a MULTILINESTRING into its component coordinate groups without
    # breaking on commas inside each group. This intentionally supports the
    # common 2D GIS form used by transmission datasets.
    body_start = text.find("(")
    body_end = text.rfind(")")
    if body_start < 0 or body_end <= body_start:
        return []
    body = text[body_start + 1:body_end].strip()
    groups = []
    if upper.startswith("LINESTRING"):
        groups = [body.strip().strip("()").strip()]
    else:
        depth = 0
        start = None
        for i, char in enumerate(body):
            if char == "(":
                if depth == 0:
                    start = i + 1
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and start is not None:
                    groups.append(body[start:i])
                    start = None
        if not groups:
            groups = [body.replace("(", "").replace(")", "")]

    output = []
    for group in groups:
        points = []
        for pair in group.split(","):
            numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", pair)
            if len(numbers) >= 2:
                # WKT GIS convention: x=longitude, y=latitude.
                points.append((float(numbers[0]), float(numbers[1])))
        if len(points) >= 2:
            output.append(points)
    return output


def find_voltage_column(columns):
    # Prefer explicit kV / voltage fields over unrelated fields.
    normalized = [(column_key(c), c) for c in columns]
    priorities = ["voltagekv", "nominalvoltage", "operatingvoltage", "voltage", "kv", "volts"]
    for wanted in priorities:
        for key, original in normalized:
            if key == wanted or (wanted == "voltage" and key.startswith("voltage")):
                return original
    for key, original in normalized:
        if "voltage" in key or key.endswith("kv"):
            return original
    return None


def _read_grid_source(source, filename=None):
    """Read a path, Streamlit upload, or bytes into (filename, content)."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        return filename or path.name, path.read_bytes()
    if isinstance(source, (bytes, bytearray)):
        return filename or "grid_data.bin", bytes(source)
    name = filename or getattr(source, "name", "grid_data.csv")
    if hasattr(source, "seek"):
        source.seek(0)
    content = source.read()
    if hasattr(source, "seek"):
        source.seek(0)
    return name, content


def _voltage_from_properties(properties, fallback_text=""):
    """Read voltage from a property field, with a label/name fallback."""
    properties = properties or {}
    col = find_voltage_column(properties.keys())
    if col is not None and properties.get(col) not in (None, ""):
        candidate = properties.get(col)
        if pd.notna(candidate) and str(candidate).strip():
            return candidate

    for key, value in properties.items():
        key_norm = column_key(key)
        if ("voltage" in key_norm or key_norm.endswith("kv") or key_norm == "volts") and value not in (None, ""):
            if pd.notna(value) and str(value).strip():
                return value

    text = str(fallback_text or "")
    match = re.search(r"(?i)(\d+(?:\.\d+)?)\s*k\s*v\b", text)
    if match:
        return match.group(1) + " kV"
    # KML layer names occasionally encode voltage in volts, e.g. 138000.
    match = re.search(r"(?<!\d)(\d{4,6})(?!\d)", text)
    if match:
        value = int(match.group(1))
        if 10000 <= value <= 800000:
            return value
    return None


def _parse_kml_coordinates(text):
    """Parse KML coordinates: lon,lat[,alt] whitespace separated."""
    points = []
    if not text:
        return points
    for token in text.strip().split():
        parts = token.split(",")
        if len(parts) < 2:
            continue
        try:
            points.append((float(parts[0]), float(parts[1])))
        except (TypeError, ValueError):
            continue
    return points


def _local_xml_name(tag):
    return tag.rsplit("}", 1)[-1].lower() if "}" in tag else tag.lower()


def _parse_kml_or_kmz(content, filename):
    """Parse KML/KMZ line geometries and point features with voltage metadata."""
    grouped = {}
    points = []
    segment_count = 0

    def add_line(coords, voltage_raw):
        nonlocal segment_count
        clean = clean_coordinate_segment(coords)
        if not clean:
            return
        label = normalize_voltage_kv(voltage_raw)
        grouped.setdefault(label, []).append(
            ([point[0] for point in clean], [point[1] for point in clean])
        )
        segment_count += 1

    if filename.lower().endswith(".kmz"):
        try:
            archive = zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile as exc:
            raise ValueError("The KMZ file is not a valid ZIP/KMZ archive.") from exc
        with archive:
            kml_names = [n for n in archive.namelist() if n.lower().endswith(".kml")]
            if not kml_names:
                raise ValueError("No KML document was found inside the KMZ archive.")
            documents = [(n, archive.read(n)) for n in kml_names]
    else:
        documents = [(filename, content)]

    for document_name, xml_content in documents:
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as exc:
            raise ValueError(f"Could not parse KML document {document_name}: {exc}") from exc

        placemarks = [el for el in root.iter() if _local_xml_name(el.tag) == "placemark"]
        for placemark in placemarks:
            name = ""
            description = ""
            properties = {}

            for child in placemark.iter():
                tag = _local_xml_name(child.tag)
                if tag == "name" and not name:
                    name = (child.text or "").strip()
                elif tag == "description" and not description:
                    description = (child.text or "").strip()
                elif tag == "data":
                    prop_name = child.attrib.get("name")
                    if prop_name:
                        for sub in child:
                            if _local_xml_name(sub.tag) == "value":
                                properties[prop_name] = (sub.text or "").strip()
                elif tag == "simpledata":
                    prop_name = child.attrib.get("name")
                    if prop_name:
                        properties[prop_name] = (child.text or "").strip()

            voltage_raw = _voltage_from_properties(
                properties, f"{name} {description} {document_name}"
            )

            for element in placemark.iter():
                tag = _local_xml_name(element.tag)
                if tag not in {"linestring", "point"}:
                    continue
                coord_text = ""
                for child in element.iter():
                    if _local_xml_name(child.tag) == "coordinates":
                        coord_text = child.text or ""
                        break
                coords = _parse_kml_coordinates(coord_text)

                if tag == "linestring":
                    add_line(coords, voltage_raw)
                elif tag == "point" and coords:
                    lon, lat = coords[0]
                    if -180 <= lon <= 180 and -90 <= lat <= 90:
                        points.append({
                            "name": name or "Grid / substation",
                            "longitude": lon,
                            "latitude": lat,
                            "voltage_label": normalize_voltage_kv(voltage_raw),
                            "source_file": filename,
                        })

    return grouped, segment_count, points


def load_transmission_lines(source, filename=None):
    """Load CSV, GeoJSON, KML or KMZ; return lines, count and grid points."""
    if source is None:
        return {}, 0, []

    name, content = _read_grid_source(source, filename)
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"Grid file exceeds the {MAX_UPLOAD_MB} MB limit.")

    lower_name = name.lower()
    grouped = {}
    points = []
    segment_count = 0

    def add_segment(coords, voltage_raw):
        nonlocal segment_count
        cleaned = clean_coordinate_segment(coords)
        if not cleaned:
            return
        label = normalize_voltage_kv(voltage_raw)
        grouped.setdefault(label, []).append(
            ([point[0] for point in cleaned], [point[1] for point in cleaned])
        )
        segment_count += 1

    def add_point(lon, lat, point_name, voltage_raw=None):
        try:
            lon, lat = float(lon), float(lat)
        except (TypeError, ValueError):
            return
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            points.append({
                "name": str(point_name or "Grid / substation"),
                "longitude": lon,
                "latitude": lat,
                "voltage_label": normalize_voltage_kv(voltage_raw),
                "source_file": name,
            })

    def add_geometry(geometry, properties=None, label_text=""):
        if not isinstance(geometry, dict):
            return
        properties = properties or {}
        voltage_raw = _voltage_from_properties(properties, label_text)
        geom_type = geometry.get("type", "")
        coords = geometry.get("coordinates")

        if geom_type == "Feature":
            props = geometry.get("properties") or properties
            add_geometry(geometry.get("geometry") or {}, props, label_text)
        elif geom_type == "GeometryCollection":
            for child in geometry.get("geometries", []):
                add_geometry(child, properties, label_text)
        elif geom_type == "LineString":
            add_segment(coords, voltage_raw)
        elif geom_type == "MultiLineString":
            for segment in coords or []:
                add_segment(segment, voltage_raw)
        elif geom_type == "Point" and isinstance(coords, (list, tuple)) and len(coords) >= 2:
            add_point(coords[0], coords[1], label_text, voltage_raw)
        elif geom_type == "MultiPoint":
            for pt in coords or []:
                if len(pt) >= 2:
                    add_point(pt[0], pt[1], label_text, voltage_raw)

    if lower_name.endswith((".kmz", ".kml")):
        grouped, segment_count, points = _parse_kml_or_kmz(content, name)

    elif lower_name.endswith((".geojson", ".json")):
        try:
            document = json.loads(content.decode("utf-8-sig"))
        except Exception as exc:
            raise ValueError(f"Cannot read GeoJSON/JSON file: {exc}") from exc

        if document.get("type") == "FeatureCollection":
            features = document.get("features", [])
        elif document.get("type") == "Feature":
            features = [document]
        else:
            features = [{"type": "Feature", "geometry": document, "properties": {}}]

        for feature in features:
            properties = feature.get("properties") or {}
            feature_name = (
                properties.get("name") or properties.get("Name")
                or properties.get("substation") or properties.get("id") or name
            )
            add_geometry(feature.get("geometry") or {}, properties, str(feature_name))

    elif lower_name.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as exc:
            raise ValueError(f"Cannot read grid CSV: {exc}") from exc

        norm_cols = {column_key(c): c for c in df.columns}
        voltage_col = find_voltage_column(df.columns)
        geometry_col = next(
            (norm_cols[k] for k in ["geometry", "geojson", "linegeometry", "coordinates", "wkt"] if k in norm_cols),
            None,
        )

        endpoint_aliases = {
            "from_lon": ["fromlon", "fromlongitude", "startlon", "startlongitude", "lon1", "longitude1", "x1"],
            "from_lat": ["fromlat", "fromlatitude", "startlat", "startlatitude", "lat1", "latitude1", "y1"],
            "to_lon": ["tolon", "tolongitude", "endlon", "endlongitude", "lon2", "longitude2", "x2"],
            "to_lat": ["tolat", "tolatitude", "endlat", "endlatitude", "lat2", "latitude2", "y2"],
        }
        endpoint_cols = {
            standard: next((norm_cols[a] for a in aliases if a in norm_cols), None)
            for standard, aliases in endpoint_aliases.items()
        }

        lat_col = next((norm_cols[k] for k in ["latitude", "lat", "y"] if k in norm_cols), None)
        lon_col = next((norm_cols[k] for k in ["longitude", "lon", "long", "lng", "x"] if k in norm_cols), None)
        name_col = next((norm_cols[k] for k in ["name", "label", "substation", "substationname", "gridname", "facilityname", "plantname", "id"] if k in norm_cols), None)

        for _, row in df.iterrows():
            voltage_raw = row.get(voltage_col) if voltage_col else None
            feature_name = row.get(name_col) if name_col else name
            handled_line = False

            if geometry_col is not None and pd.notna(row.get(geometry_col)):
                raw_geometry = row.get(geometry_col)
                parsed = None
                if isinstance(raw_geometry, dict):
                    parsed = raw_geometry
                elif isinstance(raw_geometry, str):
                    text = raw_geometry.strip()
                    try:
                        parsed = json.loads(text)
                    except (json.JSONDecodeError, TypeError):
                        for segment in parse_wkt_linestring(text):
                            add_segment(segment, voltage_raw)
                            handled_line = True

                if isinstance(parsed, dict):
                    add_geometry(parsed, {voltage_col: voltage_raw} if voltage_col else {}, str(feature_name))
                    handled_line = True
                elif isinstance(parsed, list) and parsed:
                    if isinstance(parsed[0], (list, tuple)) and len(parsed[0]) >= 2 and isinstance(parsed[0][0], (int, float)):
                        add_segment(parsed, voltage_raw)
                    else:
                        for segment in parsed:
                            add_segment(segment, voltage_raw)
                    handled_line = True

            if not handled_line and all(endpoint_cols.values()):
                try:
                    add_segment([
                        [float(row[endpoint_cols["from_lon"]]), float(row[endpoint_cols["from_lat"]])],
                        [float(row[endpoint_cols["to_lon"]]), float(row[endpoint_cols["to_lat"]])],
                    ], voltage_raw)
                    handled_line = True
                except (TypeError, ValueError, KeyError):
                    pass

            # Point-like grid/substation CSVs can be shown at the same time.
            if lat_col is not None and lon_col is not None:
                add_point(row.get(lon_col), row.get(lat_col), feature_name, voltage_raw)

    else:
        raise ValueError("Supported grid files: CSV, GeoJSON, JSON, KML and KMZ.")

    if segment_count == 0 and not points:
        raise ValueError(
            "No valid grid geometries or points were found. Use a KMZ/KML with "
            "LineString or Point features, GeoJSON with line/point geometry, or "
            "CSV with WKT/GeoJSON geometry, endpoint coordinates, or latitude/longitude."
        )

    return grouped, segment_count, points


def discover_repository_grid_files():
    """Find transmission files in the repository, including generically named CSVs."""
    root = Path(__file__).resolve().parent
    excluded_dirs = {".git", ".venv", "venv", "__pycache__", ".streamlit", "node_modules"}
    grid_name_pattern = re.compile(
        r"(transmission|trans.?line|power.?line|grid|substation|electric.?line|network|pylons|electricity.?infrastructure)",
        re.IGNORECASE,
    )
    candidates = []
    asset_csv_names = {"renewable_asset_register.csv"}
    # These are known non-grid data families; don't accidentally treat them as line files.
    unrelated_name_pattern = re.compile(r"(lmp|price|pricing|settlement|eia.?860|asset.?register|renewable.?asset|generation|demand|weather)", re.I)

    for path in root.rglob("*"):
        if not path.is_file() or any(part in excluded_dirs for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix not in {".csv", ".geojson", ".json", ".kml", ".kmz"}:
            continue
        if path.name.lower() in asset_csv_names:
            continue

        # Spatial formats are considered grid inputs. For CSV/JSON, accept a
        # grid-oriented filename OR inspect headers so a file named data.csv
        # is still detected when it contains line geometry/coordinates/voltage.
        if suffix in {".kmz", ".kml", ".geojson"} or grid_name_pattern.search(path.stem):
            candidates.append(path)
            continue
        if suffix == ".json" and grid_name_pattern.search(path.name):
            candidates.append(path)
            continue
        if suffix == ".csv" and not unrelated_name_pattern.search(path.stem):
            try:
                headers = pd.read_csv(path, nrows=0).columns
                normalized = {column_key(c) for c in headers}
                has_geometry = bool(normalized & {"geometry", "geojson", "linegeometry", "wkt", "coordinates", "shape", "geom", "thegeom"})
                has_endpoints = bool(normalized & {"fromlon", "fromlongitude", "startlon", "lon1", "x1"}) and bool(normalized & {"tolon", "tolongitude", "endlon", "lon2", "x2"})
                has_spatial_points = bool(normalized & {"latitude", "lat", "y"}) and bool(normalized & {"longitude", "lon", "long", "lng", "x"})
                has_line_attributes = bool(normalized & {"lineid", "transmissionlineid", "circuitid", "assetid", "featureid"}) and bool(normalized & {"voltage", "voltagekv", "nominalvoltage", "kv", "volts"})
                if has_geometry or has_endpoints or has_spatial_points or has_line_attributes:
                    candidates.append(path)
            except Exception:
                # A grid-named CSV is included above; unreadable generic CSVs are ignored.
                pass

    # Keep KMZ/KML geometry sources first, then CSVs/attributes; stable ordering.
    return sorted(set(candidates), key=lambda p: (p.suffix.lower() == ".csv", str(p).lower()))

def transmission_line_traces(grouped_lines):
    """Create map line traces plus the exact colors used for the legend."""
    labels = list(grouped_lines.keys())
    colors = build_voltage_color_map(labels)
    traces = []

    def sort_key(label):
        return (voltage_value_from_label(label), label)

    for label in sorted(labels, key=sort_key):
        all_lon, all_lat = [], []
        for lons, lats in grouped_lines[label]:
            all_lon.extend(lons)
            all_lat.extend(lats)
            all_lon.append(None)
            all_lat.append(None)

        traces.append(
            MAP_TRACE_CLASS(
                lon=all_lon,
                lat=all_lat,
                mode="lines",
                line=dict(color=colors[label], width=4),
                name=f"{label} transmission",
                legendgroup=f"transmission-{label}",
                showlegend=True,
                hovertemplate=f"<b>{label}</b><br>Transmission line<extra></extra>",
            )
        )

    return traces, colors


def transmission_legend_html(color_map):
    """HTML legend that stays readable on the Sunstripe ivory background."""
    if not color_map:
        return ""

    labels = sorted(
        color_map.keys(),
        key=lambda label: (voltage_value_from_label(label), label),
    )

    items = []
    for label in labels:
        color = color_map[label]
        items.append(
            '<span style="display:inline-flex;align-items:center;gap:7px;'
            'border:1px solid #E7E0DB;border-radius:16px;padding:6px 10px;'
            'margin:3px 5px 3px 0;background:#FFFDFA;color:#000000;'
            'font:12px DM Sans,Arial,sans-serif;">'
            f'<span style="display:inline-block;width:24px;height:4px;'
            f'border-radius:2px;background:{color};"></span>{label}</span>'
        )

    return (
        '<div style="margin:10px 0 14px;color:#000000;">'
        '<div style="font-weight:700;font-size:13px;margin-bottom:5px;">'
        'Transmission voltage legend</div>'
        + ''.join(items)
        + '</div>'
    )


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="topbar">
    <div class="brand">
        Sunstripe <span class="accent">SELECT</span>
    </div>
    <div class="brand-tagline">
        Know Where To Build
    </div>
    <div class="navrow">
        <span class="navitem active">SITE INTELLIGENCE</span>
        <span class="navitem">INTERCONNECTION</span>
        <span class="navitem">GRID &amp; NODAL</span>
        <span class="navitem">NEIGHBORHOOD</span>
        <span class="navitem">ALTERNATIVES</span>
        <span class="navitem">LAND &amp; REAL ESTATE</span>
    </div>
</div>
<div class="eyebrow">● LOCATION INTELLIGENCE / UNITED STATES</div>
<div class="hero">Find the right place to build.</div>
<div class="subtitle">
Location and Site Intelligence for Renewable Energy and Large Loads
</div>
""", unsafe_allow_html=True)


# ============================================================
# SUNSTRIPE AI — REAL-TIME RESEARCH CHATBOX
# Uses Groq chat completions + built-in browser search.
# Configure GROQ_API_KEY in Streamlit Secrets.
# ============================================================

def _sunstripe_ai_answer(chat_messages):
    """Fast Groq response; avoid slow browser-search retries in the chat path."""
    api_key = ""
    model = "openai/gpt-oss-20b"
    try:
        api_key = str(st.secrets.get("GROQ_API_KEY", "")).strip().strip("\"'")
        model = str(st.secrets.get("GROQ_MODEL", model)).strip() or model
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY", "").strip().strip("\"'")
    if not api_key:
        raise RuntimeError(
            "Sunstripe AI needs GROQ_API_KEY in Streamlit Secrets. Add it in Streamlit Cloud → Settings → Secrets."
        )

    instructions = """You are Sunstripe SELECT AI, a concise analyst copilot for utility-scale solar, wind, BESS, large loads and US power markets. Help with site screening, land, permitting, transmission, interconnection, nodal/LMP analysis, competitors and market/regulatory research. Do not invent live prices, grid capacity, parcel facts or project status. Clearly label assumptions and explain when live data is not connected. Keep answers practical and concise. For site evaluations, use the supplied coordinates and clearly separate preliminary screening from verified due diligence."""
    messages = [{"role": "system", "content": instructions}]
    for item in chat_messages[-8:]:
        role = item.get("role", "user")
        if role not in ("user", "assistant"):
            continue
        content = str(item.get("content", "")).strip()
        if content:
            messages.append({"role": role, "content": content})

    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_completion_tokens": 1200,
    }
    try:
        response = requests.post(endpoint, headers=headers, json=body, timeout=(5, 25))
    except requests.Timeout as exc:
        raise RuntimeError("Sunstripe AI timed out after 25 seconds. Please try again; no repeated retries were made.") from exc
    except requests.RequestException as exc:
        raise RuntimeError("Could not connect to Groq. Please try again shortly.") from exc

    if response.status_code >= 400:
        try:
            payload = response.json()
            detail = payload.get("error", {}).get("message", response.text[:300])
        except (ValueError, AttributeError):
            detail = response.text[:300]
        if response.status_code == 401:
            raise RuntimeError("Groq rejected the API key. Check GROQ_API_KEY in Streamlit Secrets.")
        if response.status_code == 429:
            raise RuntimeError("Groq rate limit or quota reached. Wait for the limit to reset and try again.")
        if response.status_code >= 500:
            raise RuntimeError("Groq is temporarily returning a server error. Please retry shortly.")
        raise RuntimeError(f"Groq API error ({response.status_code}): {str(detail)[:300]}")

    payload = response.json()
    choices = payload.get("choices", [])
    answer = str(choices[0].get("message", {}).get("content") or "").strip() if choices else ""
    if not answer:
        raise RuntimeError("Groq returned no text. Please try again.")

    # Do not imply that a live web search was performed. Preserve any URLs the model provides.
    import re
    urls = re.findall(r"https?://[^\s)\]}>]+", answer)
    sources = []
    for url in urls:
        clean_url = url.rstrip(".,;:")
        if not any(source.get("url") == clean_url for source in sources):
            sources.append({"title": clean_url, "url": clean_url})
    return answer, sources[:8]


st.markdown(
    """
    <section class="ss-ai-hero">
      <div class="ss-ai-orb" aria-hidden="true">✦</div>
      <div class="ss-ai-copy">
        <div class="ss-ai-eyebrow">SUNSTRIPE AI <span>•</span> GROQ AI ANALYST</div>
        <div class="ss-ai-title">Your energy intelligence copilot</div>
        <div class="ss-ai-description">Tell me what you’re working on. I’ll help you explore sites, grid access, power markets and renewable opportunities.</div>
        <div class="ss-ai-tags"><span>☀️ Solar</span><span>🌬️ Wind</span><span>🔋 BESS</span><span>⚡ Grid &amp; nodal</span></div>
      </div>
      <div class="ss-ai-live"><span class="ss-ai-live-dot"></span> AI assistant ready</div>
    </section>
    """,
    unsafe_allow_html=True,
)

if "sunstripe_ai_messages" not in st.session_state:
    st.session_state.sunstripe_ai_messages = [
        {"role": "assistant", "content": "Hi! I’m Sunstripe AI 👋\n\nI can help you evaluate a site, unpack an interconnection issue, research a market, or compare solar, wind and BESS opportunities. What are we exploring today?", "sources": []}
    ]

# Clickable starter prompts feed directly into the same chat pipeline.
_sunstripe_starters = [
    ("☀️  Screen a solar site", "Help me screen a potential utility-scale solar site. What inputs and constraints should I evaluate first?"),
    ("🔋  Explore BESS revenue", "Help me evaluate a utility-scale BESS opportunity, including duration, revenue streams, and the market data required."),
    ("⚡  Check grid & nodal", "Explain how to assess interconnection and nodal price risk for a renewable or BESS project in the US."),
    ("🌬️  Compare technologies", "Compare solar, wind, and BESS development opportunities for a US project, and tell me what project details you need."),
]
_starter_cols = st.columns(4, gap="small")
for _starter_index, (_starter_label, _starter_prompt) in enumerate(_sunstripe_starters):
    with _starter_cols[_starter_index]:
        if st.button(_starter_label, key=f"sunstripe_ai_starter_{_starter_index}", use_container_width=True):
            st.session_state["sunstripe_ai_pending_prompt"] = _starter_prompt
            st.rerun()

with st.container(border=True):
    for _msg in st.session_state.sunstripe_ai_messages:
        with st.chat_message(_msg["role"]):
            st.markdown(_msg["content"])
            if _msg.get("sources"):
                with st.expander(f"🔎 Sources ({len(_msg['sources'])})"):
                    for _source in _msg["sources"]:
                        st.markdown(f"- [{_source['title']}]({_source['url']})")

    _ai_prompt = st.chat_input(
        "Ask about a site, grid node, BESS opportunity or power market…",
        key="sunstripe_ai_prompt",
    )
    _pending_ai_prompt = st.session_state.pop("sunstripe_ai_pending_prompt", None)
    if _pending_ai_prompt:
        _ai_prompt = _pending_ai_prompt

    if _ai_prompt:
        st.session_state.sunstripe_ai_messages.append({"role": "user", "content": _ai_prompt, "sources": []})
        with st.chat_message("user"):
            st.markdown(_ai_prompt)
        with st.chat_message("assistant"):
            with st.spinner("Sunstripe AI is researching…"):
                try:
                    _ai_answer, _ai_sources = _sunstripe_ai_answer(st.session_state.sunstripe_ai_messages)
                    st.markdown(_ai_answer)
                    if _ai_sources:
                        with st.expander(f"🔎 Sources ({len(_ai_sources)})"):
                            for _source in _ai_sources:
                                st.markdown(f"- [{_source['title']}]({_source['url']})")
                    st.session_state.sunstripe_ai_messages.append({"role": "assistant", "content": _ai_answer, "sources": _ai_sources})
                except Exception as _ai_error:
                    st.error(str(_ai_error))
                    st.session_state.sunstripe_ai_messages.append({"role": "assistant", "content": f"I couldn’t complete that request: {_ai_error}", "sources": []})
        st.rerun()


# ============================================================
# DATA SOURCE SELECTOR
# REPOSITORY CSV IS THE DEFAULT
# ============================================================

with st.sidebar:
    st.markdown("## Sunstripe")
    st.caption("LOCATION INTELLIGENCE PLATFORM")
    st.divider()

    data_mode = st.radio(
        "Project data source",
        [
            "Repository CSV",
            "Upload a file",
            "EIA live inventory",
        ],
        index=0,
        key="data_mode",
    )

    uploaded_file = None

    if data_mode == "Upload a file":
        uploaded_file = st.file_uploader(
            "Upload project data",
            type=["csv", "xls", "xlsx"],
        )

    st.divider()
    st.markdown("### Transmission & grid")
    repository_grid_files = discover_repository_grid_files()
    if repository_grid_files:
        st.caption("Auto-detected repository grid files:")
        for grid_path in repository_grid_files:
            st.caption(f"• {grid_path.relative_to(Path(__file__).resolve().parent)}")
    else:
        st.caption("No grid files found in the repository yet.")
    st.caption("Repository grid files load automatically. Upload additional files only if needed.")
    transmission_files = st.file_uploader(
        "Additional transmission / grid files",
        type=["geojson", "json", "csv", "kml", "kmz"],
        accept_multiple_files=True,
        key="transmission_grid_upload",
        help=(
            "Supported: CSV line/point data, GeoJSON, KML and KMZ. Files already "
            "committed to GitHub are detected automatically by filename or spatial format."
        ),
    )


# ============================================================
# LOAD DATA
# ============================================================

source_label = ""
source_url = ""

try:
    if data_mode == "Repository CSV":
        assets = load_repository_csv()
        source_label = "Repository CSV: renewable_asset_register.csv"

    elif data_mode == "Upload a file":
        if uploaded_file is None:
            st.info(
                "Select 'Upload a file' and upload your CSV or Excel workbook "
                "using the sidebar."
            )
            st.stop()

        assets = load_uploaded_file(uploaded_file)
        source_label = f"User-uploaded dataset: {uploaded_file.name}"

    else:
        with st.spinner("Downloading and validating EIA data..."):
            assets, source_url = load_eia_assets()

        source_label = "EIA-860M monthly generator inventory"

except FileNotFoundError:
    st.error(
        "renewable_asset_register.csv was not found in the repository root. "
        "Add it to GitHub or choose Upload a file in the sidebar."
    )
    st.stop()

except Exception as exc:
    st.error("The selected dataset could not be loaded.")
    st.code(f"{type(exc).__name__}: {exc}")

    st.markdown(f"[Open the official EIA data page]({EIA_PAGE})")

    st.info(
        "Use Repository CSV or Upload a file to continue without the live "
        "EIA download."
    )
    st.stop()


# Load repository transmission/grid files automatically. Uploads are additive.
transmission_groups = {}
transmission_segment_count = 0
grid_point_records = []
transmission_source_names = []
transmission_load_errors = []

repository_grid_files = discover_repository_grid_files()

sources_to_load = [(path, path.name) for path in repository_grid_files]
for uploaded_grid_file in (transmission_files or []):
    sources_to_load.append((uploaded_grid_file, uploaded_grid_file.name))

for grid_source, grid_filename in sources_to_load:
    try:
        if hasattr(grid_source, "seek"):
            grid_source.seek(0)
        groups, count, points = load_transmission_lines(
            grid_source,
            filename=grid_filename,
        )
        for voltage_label, segments in groups.items():
            transmission_groups.setdefault(voltage_label, []).extend(segments)
        transmission_segment_count += count
        grid_point_records.extend(points)
        transmission_source_names.append(grid_filename)
    except Exception as exc:
        transmission_load_errors.append(f"{grid_filename}: {exc}")

if transmission_load_errors:
    with st.sidebar.expander("Grid file warnings", expanded=False):
        for message in transmission_load_errors:
            st.warning(message)

grid_points = pd.DataFrame(grid_point_records)
if not grid_points.empty:
    grid_points = grid_points.drop_duplicates(
        subset=["name", "longitude", "latitude", "source_file"]
    ).reset_index(drop=True)


# ============================================================
# DEFENSIVE VALIDATION
# This prevents the original technology_display KeyError.
# ============================================================

if "technology_display" not in assets.columns:
    assets = standardize_assets(
        assets,
        source_name=source_label or "Loaded dataset",
        source_url=source_url,
    )

if "technology_display" not in assets.columns:
    st.error(
        "Technology classification could not be created. "
        "Check the technology, fuel type or energy source column in your CSV."
    )
    st.stop()


# ============================================================
# TECHNOLOGY SELECTION
# ============================================================

st.markdown(
    '<div class="section-title">Select technology</div>',
    unsafe_allow_html=True,
)

technology_choice = st.radio(
    "Show projects",
    ["All technologies", "Solar", "Wind", "BESS"],
    horizontal=True,
    key="technology_choice",
)

if technology_choice == "All technologies":
    working = assets[
        assets["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()
else:
    working = assets[
        assets["technology_display"] == technology_choice
    ].copy()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:
    st.divider()
    st.markdown("### Asset filters")

    state_options = sorted(
        working["state"].fillna("Unknown").astype(str).unique().tolist()
    )

    selected_states = st.multiselect(
        "State",
        state_options,
        default=[],
        help="Leave empty to include all states.",
    )

    status_options = sorted(
        working["status"].fillna("Unknown").astype(str).unique().tolist()
    )

    selected_statuses = st.multiselect(
        "Project / generator status",
        status_options,
        default=status_options,
    )

    working["nameplate_capacity_mw"] = pd.to_numeric(
        working["nameplate_capacity_mw"],
        errors="coerce",
    )

    max_mw = working["nameplate_capacity_mw"].max()
    max_mw = max(1.0, float(max_mw)) if pd.notna(max_mw) else 1.0

    capacity_range = st.slider(
        "Nameplate capacity (MW)",
        min_value=0.0,
        max_value=max_mw,
        value=(0.0, max_mw),
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = working[
    working["status"].fillna("Unknown").astype(str).isin(selected_statuses)
].copy()

if selected_states:
    filtered = filtered[
        filtered["state"].fillna("Unknown").astype(str).isin(selected_states)
    ].copy()

filtered["nameplate_capacity_mw"] = pd.to_numeric(
    filtered["nameplate_capacity_mw"],
    errors="coerce",
)

filtered = filtered[
    filtered["nameplate_capacity_mw"].between(*capacity_range)
].copy()


# ============================================================
# KPI SUMMARY
# ============================================================

records_count = len(filtered)
capacity_total = filtered["nameplate_capacity_mw"].sum()
state_count = filtered["state"].nunique()

plant_count = (
    filtered["plant_code"].nunique()
    if "plant_code" in filtered
    else records_count
)

technology_counts = filtered["technology_display"].value_counts()

solar_count = int(technology_counts.get("Solar", 0))
wind_count = int(technology_counts.get("Wind", 0))
bess_count = int(technology_counts.get("BESS", 0))

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{records_count:,}</div><div class="kpi-label">'
        'Generator records in view</div></div>',
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{capacity_total:,.1f} MW</div><div class="kpi-label">'
        'Represented nameplate capacity</div></div>',
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{plant_count:,}</div><div class="kpi-label">'
        'Distinct plant codes</div></div>',
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{state_count:,}</div><div class="kpi-label">'
        'States represented</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="pill-row">'
    f'<span class="pill">Solar · {solar_count:,}</span>'
    f'<span class="pill">Wind · {wind_count:,}</span>'
    f'<span class="pill">BESS · {bess_count:,}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

st.caption(f"Data source: {source_label}")

if source_url:
    st.markdown(f"[Open source workbook]({source_url})")

if data_mode == "EIA live inventory":
    st.info(
        "EIA monthly information is preliminary and may be revised."
    )


# ============================================================
# PLOTLY CHART THEME
# ============================================================

def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=13, color=BLACK),
        title=dict(
            font=dict(family=FONT, size=16, color=BLACK),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            font=dict(family=FONT, size=12, color=BLACK),
            title=dict(font=dict(family=FONT, size=12, color=BLACK)),
            bgcolor="rgba(251,249,247,0)",
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        margin=dict(t=65, b=40, l=45, r=25),
        hoverlabel=dict(
            bgcolor=WHITE,
            font=dict(family=FONT, size=12, color=BLACK),
            bordercolor=LINE,
        ),
    )

    fig.update_xaxes(
        title_font=dict(family=FONT, size=12, color=BLACK),
        tickfont=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        title_font=dict(family=FONT, size=12, color=BLACK),
        tickfont=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showgrid=True,
        gridcolor=LINE,
        zeroline=False,
    )

    return fig



# ============================================================
# SITEIQ MODULE (integrated as a workspace tab)
# ============================================================

# ════════════════════════════════════════════════════════════════
# GEOCODING — free Nominatim
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def geocode(query):
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": query, "format": "json", "limit": 1, "countrycodes": "us"},
                         headers={"User-Agent": "SiteIQ/1.0"}, timeout=8)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", "")
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=3600)
def reverse_geocode(lat, lon):
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse",
                         params={"lat": lat, "lon": lon, "format": "json"},
                         headers={"User-Agent": "SiteIQ/1.0"}, timeout=8)
        data = r.json()
        addr = data.get("address", {})
        county = addr.get("county", "Unknown")
        state = addr.get("state", "Unknown")
        return county, state, data.get("display_name", "")
    except Exception:
        return "Unknown", "Unknown", ""

# ════════════════════════════════════════════════════════════════
# DATA GENERATION ENGINE
# ════════════════════════════════════════════════════════════════
def estimate_solar_irradiance(lat):
    return int(np.clip(280 - (lat - 25) * 3.2, 140, 270))

def estimate_wind_speed(lat, lon):
    base = 5.0
    if -104 < lon < -95 and 30 < lat < 48: base = 8.5
    elif -100 < lon < -90 and 35 < lat < 45: base = 7.0
    elif lon > -80: base = 5.5
    elif lon < -115: base = 6.0
    return round(base + np.random.uniform(-0.8, 0.8), 1)

def estimate_precip(lat, lon):
    if lon < -110: return round(np.random.uniform(8, 18), 1)
    if lon < -95: return round(np.random.uniform(18, 35), 1)
    return round(np.random.uniform(30, 55), 1)

def estimate_elevation(lat, lon):
    if lon < -110: return int(np.random.uniform(3000, 7000))
    if lon < -100: return int(np.random.uniform(1500, 4000))
    if lon < -90: return int(np.random.uniform(600, 1500))
    return int(np.random.uniform(100, 1200))

def get_wholesale_market(lat, lon):
    if -108 < lon < -93 and 26 < lat < 37: return "ERCOT"
    if lon > -80 and lat > 40: return "NYISO"
    if lon > -85 and lat > 38: return "PJM"
    if -105 < lon < -85 and lat > 36: return "MISO"
    if lon < -115: return "CAISO"
    if -105 < lon < -93 and lat < 37: return "SPP"
    return "MISO"

def generate_soil_data(lat, lon):
    np.random.seed(int(abs(lat * 100 + lon * 100)) % 100000)
    soil_templates = {
        "arid": [
            {"type": "Sandy loam", "group": "A", "suitability": 75, "drainage": "Well drained", "bedrock_ft": 5.0, "hydric": 0, "farmland": "Not Prime"},
            {"type": "Clay loam", "group": "C", "suitability": 55, "drainage": "Moderately drained", "bedrock_ft": 3.5, "hydric": 0, "farmland": "Conditionally Prime"},
            {"type": "Silty clay", "group": "D", "suitability": 40, "drainage": "Poorly drained", "bedrock_ft": 1.8, "hydric": 0, "farmland": "Not Prime"},
        ],
        "plains": [
            {"type": "Silt loam", "group": "B", "suitability": 85, "drainage": "Well drained", "bedrock_ft": 6.0, "hydric": 0, "farmland": "Prime"},
            {"type": "Silty clay loam", "group": "C", "suitability": 65, "drainage": "Moderately drained", "bedrock_ft": 4.0, "hydric": 0, "farmland": "Conditionally Prime"},
            {"type": "Clay", "group": "D", "suitability": 35, "drainage": "Poorly drained", "bedrock_ft": 2.0, "hydric": 1, "farmland": "Not Prime"},
        ],
        "east": [
            {"type": "Loam", "group": "B", "suitability": 80, "drainage": "Well drained", "bedrock_ft": 6.0, "hydric": 0, "farmland": "Prime"},
            {"type": "Sandy clay loam", "group": "C", "suitability": 60, "drainage": "Moderately drained", "bedrock_ft": 3.0, "hydric": 0, "farmland": "Not Prime"},
            {"type": "Muck/Peat", "group": "A/D", "suitability": 15, "drainage": "Very poorly drained", "bedrock_ft": 6.0, "hydric": 1, "farmland": "Not Prime"},
        ],
    }
    region = "arid" if lon < -105 else "plains" if lon < -90 else "east"
    soils = []
    templates = soil_templates[region]
    remaining = 100.0
    for i, t in enumerate(templates):
        pct = round(np.random.uniform(20, 50), 1) if i < len(templates) - 1 else remaining
        pct = min(pct, remaining)
        remaining -= pct
        soils.append({**t, "quality": np.random.randint(2, 6), "pct": pct})
    return soils

def generate_species(lat, lon):
    np.random.seed(int(abs(lat * 100 + lon * 100)) % 99999)
    all_species = [
        {"name": "Northern Long-Eared Bat", "scientific": "Myotis septentrionalis", "status": "Endangered", "range_lat": (30, 48), "range_lon": (-105, -70)},
        {"name": "Monarch Butterfly", "scientific": "Danaus plexippus", "status": "Proposed Threatened", "range_lat": (25, 48), "range_lon": (-110, -70)},
        {"name": "Bald Eagle", "scientific": "Haliaeetus leucocephalus", "status": "Recovery", "range_lat": (25, 50), "range_lon": (-130, -65)},
        {"name": "Indiana Bat", "scientific": "Myotis sodalis", "status": "Endangered", "range_lat": (33, 46), "range_lon": (-100, -75)},
        {"name": "Lesser Prairie-Chicken", "scientific": "Tympanuchus pallidicinctus", "status": "Threatened", "range_lat": (31, 39), "range_lon": (-104, -96)},
        {"name": "Desert Tortoise", "scientific": "Gopherus agassizii", "status": "Threatened", "range_lat": (32, 38), "range_lon": (-118, -110)},
        {"name": "Red-cockaded Woodpecker", "scientific": "Leuconotopicus borealis", "status": "Endangered", "range_lat": (28, 37), "range_lon": (-96, -76)},
        {"name": "Rusty Patched Bumble Bee", "scientific": "Bombus affinis", "status": "Endangered", "range_lat": (38, 48), "range_lon": (-95, -72)},
    ]
    found = []
    for sp in all_species:
        if sp["range_lat"][0] <= lat <= sp["range_lat"][1] and sp["range_lon"][0] <= lon <= sp["range_lon"][1]:
            concern = "Species of Concern" if np.random.random() < 0.4 else "May Occur"
            found.append({"name": sp["name"], "scientific": sp["scientific"], "status": sp["status"], "concern": concern})
    return found

def generate_site_data(lat, lon, acres, county, state):
    np.random.seed(int(abs(lat * 1000 + lon * 1000)) % 99999)
    irr = estimate_solar_irradiance(lat)
    wind = estimate_wind_speed(lat, lon)
    precip = estimate_precip(lat, lon)
    elev = estimate_elevation(lat, lon)
    market = get_wholesale_market(lat, lon)
    soils = generate_soil_data(lat, lon)
    species = generate_species(lat, lon)

    wetland_pct = np.clip(np.random.exponential(3), 0, 35)
    wetland_acres = round(acres * wetland_pct / 100, 1)
    flood_score = int(np.clip(np.random.normal(40, 20), 0, 100))
    flood_zones = ["X (Minimal)", "X (Moderate)", "AE", "A"]
    flood_zone = flood_zones[min(3, flood_score // 30)]

    trans_dist = round(np.random.exponential(3) + 0.2, 2)
    sub_dist = round(trans_dist + np.random.uniform(0.5, 8), 2)
    trans_cap = int(np.random.choice([138, 230, 345, 500]) * np.random.uniform(2, 8))

    solar_panels = int(acres * 650 * 0.95)
    solar_mw = round(acres * 0.29, 1)
    solar_mwh = int(solar_mw * irr / 245 * 1157)
    solar_lease = int(np.clip(irr * 1.1 - 5 + np.random.uniform(-20, 20), 80, 350))

    wind_turbines = round(acres / 80, 1)
    wind_mw = round(wind_turbines * 3.3, 1)
    wind_mwh = int(wind_mw * wind / 7.5 * 3100)
    wind_lease = int(np.clip(wind * 5 - 2 + np.random.uniform(-5, 10), 15, 80))

    land_val = int(np.random.lognormal(7.5, 0.8))
    sentiment_opts = ["Positive", "Positive", "Mixed", "Mixed", "Unsure"]
    sentiment = np.random.choice(sentiment_opts)

    soc = len([sp for sp in species if sp["concern"] == "Species of Concern"])
    species_level = "High" if soc >= 2 else "Moderate" if soc == 1 else "Low"

    permits_fed = np.random.randint(2, 7)
    permits_state = np.random.randint(2, 8)

    avg_high = round(80 - (lat - 30) * 1.5 + np.random.uniform(-3, 3), 1)
    avg_low = round(avg_high - 25 + np.random.uniform(-3, 3), 1)

    value_index = {
        "Land": int(np.clip(np.random.normal(40, 15), 1, 99)),
        "Solar Energy": int(np.clip((irr - 140) / 1.3 + np.random.normal(0, 5), 1, 99)),
        "Wind Energy": int(np.clip((wind - 4) * 15 + np.random.normal(0, 5), 1, 99)),
        "Available Power": int(np.clip(100 - trans_dist * 8, 5, 95)),
        "Energy Storage": int(np.random.uniform(15, 50)),
        "Green Power": int(np.clip((irr - 150) / 1.5 + wind * 3, 10, 90)),
        "Carbon Credits": int(np.random.uniform(5, 30)),
        "Water": int(np.clip(precip * 2 + np.random.normal(0, 8), 10, 95)),
        "Building Suitability": int(np.mean([s["suitability"] for s in soils])),
    }
    risk_index = {
        "Electricity Blackout": int(np.random.uniform(20, 90)),
        "Cost Of Electricity": int(np.random.uniform(40, 95)),
        "Electrical Connection": int(np.clip(100 - trans_dist * 6, 10, 95)),
        "Drought": int(np.clip(100 - precip * 1.8, 5, 95)),
        "Wildfire": int(np.clip(95 - precip * 1.5 + np.random.normal(0, 10), 5, 99)),
        "Natural Earthquakes": int(np.random.uniform(0, 40)),
        "Tornado": int(np.clip(50 + (lon + 95) * 2, 10, 99)) if -105 < lon < -80 else int(np.random.uniform(5, 40)),
        "Straight Line Wind": int(np.random.uniform(30, 99)),
        "Hail": int(np.random.uniform(15, 85)),
        "Flood": flood_score,
    }

    land_covers = [
        {"type": "Cropland", "pct": np.random.uniform(20, 60)},
        {"type": "Shrubland/Grassland", "pct": np.random.uniform(10, 40)},
        {"type": "Forest", "pct": np.random.uniform(2, 25)},
        {"type": "Developed", "pct": np.random.uniform(1, 8)},
        {"type": "Wetland", "pct": wetland_pct},
    ]
    total_pct = sum(lc["pct"] for lc in land_covers)
    land_cover = [{"type": lc["type"], "acres": round(lc["pct"] / total_pct * acres, 1)} for lc in land_covers]

    return {
        "lat": lat, "lon": lon, "county": county, "state": state,
        "total_acres": acres, "buildable_acres": round(acres - wetland_acres - acres * 0.02, 0),
        "land_value_per_acre": land_val, "total_land_value": land_val * int(acres),
        "value_index": value_index, "risk_index": risk_index,
        "solar_irradiance_wm2": irr, "direct_irradiance_wm2": irr - int(np.random.uniform(15, 30)),
        "corrected_irradiance_wm2": irr,
        "avg_wind_speed_ms": wind, "avg_wind_speed_mph": round(wind * 2.237, 0),
        "annual_precip_in": precip,
        "avg_elevation_ft": elev, "min_elevation_ft": elev - int(np.random.uniform(20, 80)),
        "max_elevation_ft": elev + int(np.random.uniform(20, 80)),
        "avg_slope_deg": round(np.random.uniform(0.3, 5), 1),
        "max_slope_deg": round(np.random.uniform(3, 18), 1),
        "avg_high_temp_f": avg_high, "avg_low_temp_f": avg_low,
        "soils": soils, "land_cover": land_cover,
        "solar_lease_per_acre": solar_lease, "solar_panels_possible": solar_panels,
        "solar_max_capacity_mw": solar_mw, "solar_max_annual_mwh": solar_mwh,
        "wind_lease_per_acre": wind_lease, "wind_turbines_possible": wind_turbines,
        "wind_max_capacity_mw": wind_mw, "wind_max_annual_mwh": wind_mwh,
        "nearest_trans_dist_mi": trans_dist, "nearest_trans_capacity_mw": trans_cap,
        "nearest_sub_dist_mi": sub_dist, "wholesale_market": market,
        "federal_wetland_acres": wetland_acres,
        "flood_risk_score": flood_score, "flood_zone": flood_zone,
        "species_list": species, "species_concerns": species_level,
        "permits_needed": permits_fed + permits_state,
        "federal_permits": permits_fed, "state_permits": permits_state,
        "community_sentiment": sentiment,
        "trans_owner": "Regional Utility",
        "sub_name": f"{county[:10]} Sub",
    }

# ════════════════════════════════════════════════════════════════
# PDF
# ════════════════════════════════════════════════════════════════
def build_pdf(d, score, bd):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    def sec(t):
        pdf.set_font("Helvetica","B",12); pdf.set_fill_color(30,41,59); pdf.set_text_color(255,255,255)
        pdf.cell(0,8,f"  {t}",fill=True,ln=True); pdf.set_text_color(0,0,0); pdf.ln(2)
    def kv(k,v):
        pdf.set_font("Helvetica","",10); pdf.cell(85,6,str(k)); pdf.set_font("Helvetica","B",10); pdf.cell(0,6,str(v),ln=True)
    def th(cols,ws):
        pdf.set_font("Helvetica","B",8); pdf.set_fill_color(226,232,240)
        for i,c in enumerate(cols): pdf.cell(ws[i],6,c,1,fill=True,align="C")
        pdf.ln()
    def tr(vals,ws):
        pdf.set_font("Helvetica","",7)
        for i,v in enumerate(vals): pdf.cell(ws[i],5,str(v)[:30],1,align="C")
        pdf.ln()

    pdf.add_page()
    pdf.set_font("Helvetica","B",22); pdf.cell(0,15,"SiteIQ Feasibility Report",ln=True,align="C")
    pdf.set_font("Helvetica","",12)
    pdf.cell(0,8,f"{d['county']}, {d['state']}",ln=True,align="C")
    pdf.cell(0,8,f"Coordinates: {d['lat']:.4f}, {d['lon']:.4f}",ln=True,align="C")
    pdf.cell(0,8,f"Date: {datetime.now().strftime('%B %d, %Y')}",ln=True,align="C")
    pdf.ln(8)
    sec("Key Details")
    kv("Site Score",f"{score}/100"); kv("Total Acreage",f"{d['total_acres']:,.1f}")
    kv("Buildable Acreage",f"{d['buildable_acres']:,.0f}"); kv("Land Value",f"${d['land_value_per_acre']:,}/ac")
    kv("Wholesale Market",d["wholesale_market"]); kv("Trans. Distance",f"{d['nearest_trans_dist_mi']} mi")
    kv("Substation Distance",f"{d['nearest_sub_dist_mi']} mi"); kv("Permits Needed",str(d["permits_needed"]))
    kv("Species Concern",d["species_concerns"]); kv("Community Sentiment",d["community_sentiment"])
    pdf.ln(3); sec("Score Breakdown")
    for k,v in bd.items(): kv(k,f"{v}/100")
    pdf.add_page(); sec("Value Index")
    cw=[100,50]; th(["Category","Score"],cw)
    for k,v in d["value_index"].items(): tr([k,str(v)],cw)
    pdf.ln(3); sec("Risk Index"); th(["Category","Score"],cw)
    for k,v in d["risk_index"].items(): tr([k,str(v)],cw)
    pdf.add_page(); sec("Land & Topography")
    kv("Elevation",f"{d['avg_elevation_ft']:,} ft (min {d['min_elevation_ft']:,}, max {d['max_elevation_ft']:,})")
    kv("Slope",f"{d['avg_slope_deg']} deg avg, {d['max_slope_deg']} deg max")
    kv("Precipitation",f"{d['annual_precip_in']} in/yr"); kv("Solar Irradiance",f"{d['solar_irradiance_wm2']} W/m2")
    kv("Wind Speed",f"{d['avg_wind_speed_ms']} m/s"); kv("Temp",f"{d['avg_high_temp_f']}F / {d['avg_low_temp_f']}F")
    pdf.ln(3); sec("Soil Analysis")
    sw=[30,18,14,16,32,22]; th(["Type","Suit.","Grp","Hydric","Drainage","Bedrock"],sw)
    for s in d["soils"]: tr([s["type"],str(s["suitability"]),s["group"],"Yes" if s["hydric"] else "No",s["drainage"][:14],f"{s['bedrock_ft']}ft"],sw)
    pdf.ln(3); sec("Solar"); kv("Lease",f"${d['solar_lease_per_acre']}/ac/yr"); kv("Capacity",f"{d['solar_max_capacity_mw']} MW"); kv("Output",f"{d['solar_max_annual_mwh']:,} MWh/yr")
    sec("Wind"); kv("Lease",f"${d['wind_lease_per_acre']}/ac/yr"); kv("Capacity",f"{d['wind_max_capacity_mw']} MW"); kv("Output",f"{d['wind_max_annual_mwh']:,} MWh/yr")
    if d["species_list"]:
        pdf.add_page(); sec("Protected Species")
        spw=[60,45,45]; th(["Name","Status","Concern"],spw)
        for sp in d["species_list"]: tr([sp["name"],sp["status"],sp["concern"]],spw)
    pdf.add_page(); pdf.ln(20); pdf.set_font("Helvetica","B",14)
    pdf.cell(0,10,"Generated by SiteIQ",ln=True,align="C")
    pdf.set_font("Helvetica","",9)
    pdf.cell(0,7,"Data sources: USGS, USFWS, FEMA, NRCS, ISO market data, EPA",ln=True,align="C")
    return bytes(pdf.output())


def compute_score(d, w):
    solar_s = min(100, d["value_index"].get("Solar Energy",50))
    trans_s = max(0, 100 - d["nearest_trans_dist_mi"]*10)
    wet_s = max(0, 100 - (d["federal_wetland_acres"]/max(d["total_acres"],1))*500)
    flood_s = max(0, 100 - d["flood_risk_score"])
    soil_s = np.mean([s["suitability"] for s in d["soils"]]) if d["soils"] else 50
    sent_s = {"Positive":90,"Mixed":55,"Unsure":40,"Negative":15}.get(d["community_sentiment"],50)
    cost_s = max(0, 100-(d["land_value_per_acre"]/100))
    t = (trans_s*w["Transmission"]/100 + solar_s*w["Solar"]/100 + wet_s*w["Wetlands"]/100
         + flood_s*w["Flood"]/100 + soil_s*w["Soil"]/100 + sent_s*w["Sentiment"]/100 + cost_s*w["Cost"]/100)
    bd = {"Transmission":round(trans_s),"Solar":round(solar_s),"Wetlands":round(wet_s),
          "Flood":round(flood_s),"Soil":round(soil_s),"Sentiment":round(sent_s),"Cost":round(cost_s)}
    return round(t), bd


def idx_chart(data, title, cs):
    df = pd.DataFrame({"Cat":list(data.keys()),"Score":list(data.values())}).sort_values("Score",ascending=True)
    fig = px.bar(df,x="Score",y="Cat",orientation="h",color="Score",color_continuous_scale=cs,range_color=[0,100])
    fig.update_layout(height=max(260,len(data)*28),showlegend=False,margin=dict(l=10,r=10,t=30,b=10),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=BLACK,size=11),
        xaxis=dict(range=[0,100],gridcolor=LINE),yaxis=dict(gridcolor=LINE),coloraxis_showscale=False,title=title)
    return fig




def generate_lmp_history(base, days=365):
    dates = [datetime(2024,1,1)+timedelta(days=i) for i in range(days)]
    prices = base + np.cumsum(np.random.randn(days)*1.2)
    prices = np.clip(prices + 8*np.sin(np.linspace(0,2*np.pi,days)),5,120)
    return pd.DataFrame({"Date":dates,"LMP ($/MWh)":np.round(prices,2)})


def render_siteiq():
    st.markdown("""<style>\n.concern-high{background:#fee2e2;border-left:4px solid #ef4444;padding:12px;border-radius:6px;margin:6px 0;color:#111}\n.concern-mod{background:#fef3c7;border-left:4px solid #f59e0b;padding:12px;border-radius:6px;margin:6px 0;color:#111}\n.concern-low{background:#dcfce7;border-left:4px solid #22c55e;padding:12px;border-radius:6px;margin:6px 0;color:#111}\n</style>""", unsafe_allow_html=True)
    with st.expander("SiteIQ controls", expanded=True):
        st.markdown("## ⚡ SiteIQ")
        st.caption("Renewable Energy Site Screening & Fatal Flaw Analysis")

        # ── Back-link to ERCOT BESS Dashboard ──────────────────
        st.markdown(
            '<a href="https://ercot-bess-dashboard-nhh9eztsqeuqxxuz97kacu.streamlit.app/" target="_blank">'
            '<button style="width:100%;padding:8px;margin-top:6px;background:#0f172a;color:#5de0a5;'
            'border:1px solid #1e3a2a;border-radius:8px;cursor:pointer;font-size:13px;">'
            '⚡ Open ERCOT BESS Dashboard</button></a>',
            unsafe_allow_html=True
        )
        # ───────────────────────────────────────────────────────

        st.divider()
        st.markdown("### 1. Find Your Site")
        search_q = st.text_input("Search address or place", placeholder="e.g. Runnels County, TX")
        search_btn = st.button("Search", use_container_width=True)
        st.caption("— or click directly on the map —")
        st.divider()
        st.markdown("### 2. Set Acreage")
        acres = st.number_input("Project Acreage", 10, 10000, 500, step=50)
        st.divider()
        st.markdown("### 3. Scoring Weights")
        w = {}
        w["Transmission"] = st.slider("Transmission",0,40,20)
        w["Solar"] = st.slider("Solar Resource",0,40,20)
        w["Wetlands"] = st.slider("Wetland Risk",0,40,15)
        w["Flood"] = st.slider("Flood Risk",0,40,10)
        w["Soil"] = st.slider("Soil Suitability",0,40,15)
        w["Sentiment"] = st.slider("Community",0,40,10)
        w["Cost"] = st.slider("Land Cost",0,40,10)
        tw = sum(w.values())
        if tw != 100: st.warning(f"Total: {tw}% (need 100%)")
        else: st.success("Weights: 100%")

    # ── State ──
    if "sel_lat" not in st.session_state: st.session_state.sel_lat = None
    if "sel_lon" not in st.session_state: st.session_state.sel_lon = None
    if "site_data" not in st.session_state: st.session_state.site_data = None

    if search_btn and search_q:
        lat, lon, name = geocode(search_q)
        if lat:
            st.session_state.sel_lat = lat
            st.session_state.sel_lon = lon
            st.session_state.site_data = None
        else:
            st.error("Location not found. Try a different search.")

    # ── Header ──
    st.markdown("# ⚡ SiteIQ — Renewable Energy Siting Intelligence")
    st.markdown("> **Click anywhere on the map** or **search an address** to analyze any land parcel in the US.")

    # ── Map ──
    center = [st.session_state.sel_lat or 39.0, st.session_state.sel_lon or -98.0]
    zoom = 13 if st.session_state.sel_lat else 5
    m = folium.Map(location=center, zoom_start=zoom, tiles=None)
    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                     attr="Esri",name="Satellite").add_to(m)
    folium.TileLayer(tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                     attr="CartoDB",name="Dark").add_to(m)
    folium.TileLayer(tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                     attr="OSM",name="Street").add_to(m)
    MousePosition(position="bottomleft",separator=" | ",prefix="Coords:").add_to(m)
    if st.session_state.sel_lat:
        folium.Marker([st.session_state.sel_lat, st.session_state.sel_lon],
                      icon=folium.Icon(color="purple",icon="bolt",prefix="fa"),
                      tooltip="Selected Site").add_to(m)
        d_box = (acres ** 0.5) * 0.00135
        folium.Rectangle(
            bounds=[[st.session_state.sel_lat - d_box/2, st.session_state.sel_lon - d_box/2],
                    [st.session_state.sel_lat + d_box/2, st.session_state.sel_lon + d_box/2]],
            color="#6366f1", weight=2, fill=True, fill_color="#6366f1", fill_opacity=0.15,
            tooltip=f"~{acres} acres AOI",
        ).add_to(m)
    folium.LayerControl().add_to(m)

    map_out = st_folium(m, width=None, height=500, returned_objects=["last_clicked"])

    if map_out and map_out.get("last_clicked"):
        clat = map_out["last_clicked"]["lat"]
        clng = map_out["last_clicked"]["lng"]
        if 24 < clat < 50 and -130 < clng < -65:
            st.session_state.sel_lat = clat
            st.session_state.sel_lon = clng
            st.session_state.site_data = None
            st.rerun()

    if not st.session_state.sel_lat:
        st.info("Click on the map or search an address in the sidebar to begin analysis.")
        return

    lat = st.session_state.sel_lat
    lon = st.session_state.sel_lon
    county, state, display_name = reverse_geocode(lat, lon)

    if st.session_state.site_data is None or st.session_state.site_data.get("total_acres") != acres:
        st.session_state.site_data = generate_site_data(lat, lon, acres, county, state)

    d = st.session_state.site_data
    score, bd = compute_score(d, w)

    color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    st.markdown(f"""<div style='display:flex;align-items:center;gap:24px;margin:16px 0'>
        <div style='font-size:3.5rem;font-weight:900;color:{color}'>{score}</div>
        <div><div style='font-size:1.3rem;font-weight:700'>{county}, {state}</div>
        <div style='color:#111827'>{lat:.4f}, {lon:.4f} | {acres:,} acres | {d['buildable_acres']:,.0f} buildable | {d['wholesale_market']} Market</div></div>
    </div>""", unsafe_allow_html=True)

    tab_summary, tab_env, tab_infra, tab_market, tab_export = st.tabs([
        "Summary", "Environmental", "Infrastructure", "Market", "Export",
    ])

    # ━━━ SUMMARY ━━━
    with tab_summary:
        c1,c2,c3 = st.columns(3)
        with c1:
            cls = {"High":"concern-high","Moderate":"concern-mod","Low":"concern-low"}.get(d["species_concerns"],"concern-low")
            st.markdown(f"<div class='{cls}'><b>Protected Species</b><br>{d['species_concerns']} Concern<br>{len(d['species_list'])} species in range</div>",unsafe_allow_html=True)
        with c2:
            wcls = "concern-high" if d["federal_wetland_acres"]>30 else "concern-mod" if d["federal_wetland_acres"]>10 else "concern-low"
            st.markdown(f"<div class='{wcls}'><b>Wetlands / Flood</b><br>{d['federal_wetland_acres']:.1f} ac wetlands<br>Flood Zone: {d['flood_zone']}</div>",unsafe_allow_html=True)
        with c3:
            pcls = "concern-high" if d["permits_needed"]>10 else "concern-mod" if d["permits_needed"]>5 else "concern-low"
            st.markdown(f"<div class='{pcls}'><b>Permits</b><br>{d['permits_needed']} total<br>{d['federal_permits']} Fed / {d['state_permits']} State</div>",unsafe_allow_html=True)

        st.markdown("### Key Metrics")
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        with m1: st.metric("Solar",f"{d['solar_max_capacity_mw']} MW")
        with m2: st.metric("Wind",f"{d['wind_max_capacity_mw']} MW")
        with m3: st.metric("Irradiance",f"{d['solar_irradiance_wm2']} W/m2")
        with m4: st.metric("Wind Speed",f"{d['avg_wind_speed_ms']} m/s")
        with m5: st.metric("Trans. Dist",f"{d['nearest_trans_dist_mi']} mi")
        with m6: st.metric("Land Value",f"${d['land_value_per_acre']:,}/ac")

        st.markdown("### Value & Risk Indexes")
        vi_c, ri_c = st.columns(2)
        with vi_c: st.plotly_chart(idx_chart(d["value_index"],"Value Index",["#ef4444","#f59e0b","#22c55e"]),use_container_width=True)
        with ri_c: st.plotly_chart(idx_chart(d["risk_index"],"Risk Index",["#22c55e","#f59e0b","#ef4444"]),use_container_width=True)

        st.markdown("### Score Breakdown")
        cats = list(bd.keys()); vals = list(bd.values())
        fig_r = go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill="toself",fillcolor="rgba(99,102,241,0.2)",line=dict(color="#6366f1",width=2)))
        fig_r.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",radialaxis=dict(visible=True,range=[0,100])),showlegend=False,height=350,margin=dict(l=60,r=60,t=30,b=30),paper_bgcolor="rgba(0,0,0,0)",font=dict(color=BLACK))
        st.plotly_chart(fig_r,use_container_width=True)

    # ━━━ ENVIRONMENTAL ━━━
    with tab_env:
        st.markdown("### Soil Analysis")
        soil_df = pd.DataFrame(d["soils"])
        disp_cols = {"type":"Type","quality":"Quality","group":"Group","pct":"Coverage %","suitability":"Suitability","hydric":"Hydric","drainage":"Drainage","bedrock_ft":"Bedrock (ft)","farmland":"Farmland Status"}
        soil_df = soil_df.rename(columns=disp_cols)
        soil_df["Hydric"] = soil_df["Hydric"].map({0:"No",1:"Yes"})
        st.dataframe(soil_df[list(disp_cols.values())],use_container_width=True,hide_index=True)

        s1,s2 = st.columns(2)
        with s1:
            fig = px.bar(soil_df,x="Type",y="Suitability",color="Suitability",color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],range_color=[0,100],title="Soil Suitability")
            fig.update_layout(height=280,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=BLACK),coloraxis_showscale=False)
            st.plotly_chart(fig,use_container_width=True)
        with s2:
            fig2 = px.bar(soil_df,x="Type",y="Bedrock (ft)",title="Bedrock Depth",color="Bedrock (ft)",color_continuous_scale=["#fbbf24","#22c55e"])
            fig2.update_layout(height=280,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=BLACK),coloraxis_showscale=False)
            st.plotly_chart(fig2,use_container_width=True)

        st.markdown("### Protected Species")
        if d["species_list"]:
            for sp in d["species_list"]:
                ccls = "concern-high" if sp["concern"]=="Species of Concern" else "concern-mod"
                st.markdown(f"<div class='{ccls}'><b>{sp['name']}</b> (<i>{sp['scientific']}</i>)<br>Status: <b>{sp['status']}</b> | Assessment: <b>{sp['concern']}</b></div>",unsafe_allow_html=True)
        else:
            st.success("No protected species of concern identified in this area.")

        st.markdown("### Wetlands & Flood")
        wc1,wc2,wc3 = st.columns(3)
        with wc1: st.metric("Wetland Acres",f"{d['federal_wetland_acres']:.1f}")
        with wc2: st.metric("Flood Zone",d["flood_zone"])
        with wc3: st.metric("Flood Score",f"{d['flood_risk_score']}/100")

        st.markdown("### Land Cover")
        lc_df = pd.DataFrame(d["land_cover"])
        fig_lc = px.pie(lc_df,values="acres",names="type",hole=0.4,color_discrete_sequence=px.colors.qualitative.Set3)
        fig_lc.update_layout(height=320,paper_bgcolor="rgba(0,0,0,0)",font=dict(color=BLACK))
        st.plotly_chart(fig_lc,use_container_width=True)

        st.markdown("### Topography")
        t1,t2,t3,t4 = st.columns(4)
        with t1: st.metric("Elevation",f"{d['avg_elevation_ft']:,} ft")
        with t2: st.metric("Slope (avg)",f"{d['avg_slope_deg']}°")
        with t3: st.metric("Precipitation",f"{d['annual_precip_in']} in/yr")
        with t4: st.metric("Temp (H/L)",f"{d['avg_high_temp_f']}° / {d['avg_low_temp_f']}°F")

    # ━━━ INFRASTRUCTURE ━━━
    with tab_infra:
        st.markdown("### Grid Access")
        g1,g2,g3 = st.columns(3)
        with g1: st.metric("Trans. Distance",f"{d['nearest_trans_dist_mi']} mi"); st.metric("Capacity",f"{d['nearest_trans_capacity_mw']} MW")
        with g2: st.metric("Substation",f"{d['sub_name']}"); st.metric("Distance",f"{d['nearest_sub_dist_mi']} mi")
        with g3: st.metric("Market",d["wholesale_market"]); st.metric("Sentiment",d["community_sentiment"])

        st.markdown("### Solar Potential")
        so1,so2,so3,so4 = st.columns(4)
        with so1: st.metric("Lease",f"${d['solar_lease_per_acre']}/ac/yr")
        with so2: st.metric("Capacity",f"{d['solar_max_capacity_mw']} MW")
        with so3: st.metric("Output",f"{d['solar_max_annual_mwh']:,} MWh/yr")
        with so4: st.metric("Panels",f"{d['solar_panels_possible']:,}")

        st.markdown("### Wind Potential")
        wi1,wi2,wi3,wi4 = st.columns(4)
        with wi1: st.metric("Lease",f"${d['wind_lease_per_acre']}/ac/yr")
        with wi2: st.metric("Capacity",f"{d['wind_max_capacity_mw']} MW")
        with wi3: st.metric("Output",f"{d['wind_max_annual_mwh']:,} MWh/yr")
        with wi4: st.metric("Turbines",f"{d['wind_turbines_possible']}")

    # ━━━ MARKET ━━━
    with tab_market:
        st.markdown(f"### {d['wholesale_market']} Market Pricing")
        np.random.seed(42)
        base = {"ERCOT":38,"MISO":30,"PJM":42,"CAISO":52,"SPP":28,"NYISO":48}.get(d["wholesale_market"],35)
        lmp = generate_lmp_history(base)
        fig_l = px.area(lmp,x="Date",y="LMP ($/MWh)",title="12-Month LMP History")
        fig_l.update_traces(fillcolor="rgba(99,102,241,0.2)",line_color="#6366f1")
        fig_l.update_layout(height=320,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=BLACK),xaxis=dict(gridcolor=LINE),yaxis=dict(gridcolor=LINE))
        st.plotly_chart(fig_l,use_container_width=True)

        mc1,mc2,mc3,mc4 = st.columns(4)
        with mc1: st.metric("Avg LMP",f"${lmp['LMP ($/MWh)'].mean():.1f}/MWh")
        with mc2: st.metric("Peak LMP",f"${lmp['LMP ($/MWh)'].max():.1f}/MWh")
        with mc3: st.metric("Min LMP",f"${lmp['LMP ($/MWh)'].min():.1f}/MWh")
        with mc4: st.metric("Volatility",f"{lmp['LMP ($/MWh)'].std():.1f}")

        st.markdown("### Revenue Estimate")
        solar_rev = d["solar_max_annual_mwh"] * lmp["LMP ($/MWh)"].mean() / 1000
        wind_rev = d["wind_max_annual_mwh"] * lmp["LMP ($/MWh)"].mean() / 1000
        r1,r2,r3 = st.columns(3)
        with r1: st.metric("Solar Revenue",f"${solar_rev:,.0f}k/yr")
        with r2: st.metric("Wind Revenue",f"${wind_rev:,.0f}k/yr")
        with r3: st.metric("Solar Lease Income",f"${d['solar_lease_per_acre']*acres:,}/yr")

    # ━━━ EXPORT ━━━
    with tab_export:
        st.markdown("### Download Report")
        pdf_bytes = build_pdf(d, score, bd)
        fname = f"SiteIQ_{county.replace(' ','_')}_{state}_{datetime.now().strftime('%Y%m%d')}.pdf"
        st.download_button("Download PDF Report", data=pdf_bytes, file_name=fname, mime="application/pdf", type="primary")

        st.divider()
        e1,e2 = st.columns(2)
        with e1:
            csv = pd.DataFrame([{"lat":lat,"lon":lon,"county":county,"state":state,"acres":acres,
                "score":score,"solar_mw":d["solar_max_capacity_mw"],"wind_mw":d["wind_max_capacity_mw"],
                "trans_dist":d["nearest_trans_dist_mi"],"wetland_ac":d["federal_wetland_acres"],
                "flood":d["flood_zone"],"species":d["species_concerns"],"sentiment":d["community_sentiment"],
                "market":d["wholesale_market"],"land_value":d["land_value_per_acre"]}])
            st.download_button("Download CSV",csv.to_csv(index=False),file_name="SiteIQ_analysis.csv",mime="text/csv")
        with e2:
            geo = {"type":"FeatureCollection","features":[{"type":"Feature",
                "geometry":{"type":"Point","coordinates":[lon,lat]},
                "properties":{"score":score,"acres":acres,"county":county,"state":state}}]}
            st.download_button("Download GeoJSON",json.dumps(geo,indent=2),file_name="SiteIQ_site.geojson",mime="application/json")


# ============================================================
# LOCATION EXPLORER: SEPARATE RENEWABLE AND TRANSMISSION MAPS
# ============================================================

# Main workspace tabs follow the SIGNAL flow as closely as the existing
# feature set permits. SiteIQ includes the site/community screening tools;
# Transmission network covers interconnection/grid visibility; asset and
# project views support alternatives/competitor review. Land & Real Estate is last.
tab_siteiq, tab_transmission_map, tab_asset_map, tab_register, tab_details, tab_analytics, tab_method, tab_land_parcel = st.tabs([
    "SiteIQ",
    "Transmission network",
    "Renewable assets",
    "Project register",
    "Project details",
    "Technology analytics",
    "Data & limitations",
    "Land & Real Estate",
])

with tab_siteiq:
    render_siteiq()


def fit_map_view(latitudes, longitudes, width=1350, height=700, zoom_padding=0.45):
    """Calculate a map center/zoom that fits the supplied geographic extent."""
    import math

    clean_pairs = []
    for lat, lon in zip(latitudes, longitudes):
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon)):
            continue
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            clean_pairs.append((lat, lon))

    if not clean_pairs:
        return {"lat": 39.0, "lon": -98.0}, 3.0

    lats = [p[0] for p in clean_pairs]
    lons = [p[1] for p in clean_pairs]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    center = {"lat": (lat_min + lat_max) / 2, "lon": (lon_min + lon_max) / 2}

    # Use projected Mercator span for vertical fitting and geographic span for
    # horizontal fitting. The margin ensures endpoints are not clipped.
    lon_span = max(lon_max - lon_min, 0.02)
    zoom_x = math.log2((width * 360.0) / (512.0 * lon_span))

    def mercator_y(latitude):
        latitude = max(-85.0, min(85.0, latitude))
        radians = math.radians(latitude)
        return math.log(math.tan(math.pi / 4.0 + radians / 2.0))

    mercator_span = max(mercator_y(lat_max) - mercator_y(lat_min), 0.0001)
    zoom_y = math.log2((height * 2.0 * math.pi) / (512.0 * mercator_span))
    zoom = max(0.0, min(15.0, min(zoom_x, zoom_y) - zoom_padding))
    return center, zoom


with tab_asset_map:
    st.markdown(
        '<div class="section-title">Geographic asset intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Renewable asset map")
    st.caption(
        f"Current technology selection: {technology_choice}. "
        "This map shows renewable assets only. Open the Transmission network tab for a separate full-grid map."
    )

    if transmission_load_errors:
        with st.expander("Transmission / grid file loading errors", expanded=False):
            for message in transmission_load_errors:
                st.warning(message)

    # Sanitize asset coordinates and keep this map independent of grid features.
    map_data = filtered.dropna(subset=["latitude", "longitude"]).copy()
    map_data["latitude"] = pd.to_numeric(map_data["latitude"], errors="coerce")
    map_data["longitude"] = pd.to_numeric(map_data["longitude"], errors="coerce")
    map_data = map_data[
        map_data["latitude"].between(-90, 90)
        & map_data["longitude"].between(-180, 180)
    ]

    if not map_data.empty:
        asset_center, asset_zoom = fit_map_view(
            map_data["latitude"].tolist(), map_data["longitude"].tolist(),
            height=560, zoom_padding=0.55,
        )
        map_kwargs = dict(
            data_frame=map_data,
            lat="latitude",
            lon="longitude",
            color="technology_display",
            color_discrete_map=TECH_COLORS,
            hover_name="plant_name",
            hover_data={
                "state": True,
                "county": True,
                "plant_code": True,
                "generator_id": True,
                "nameplate_capacity_mw": ":,.2f",
                "status": True,
                "latitude": False,
                "longitude": False,
            },
            center=asset_center,
            zoom=asset_zoom,
            height=560,
            labels={
                "technology_display": "Technology",
                "plant_code": "Plant code",
                "generator_id": "Generator ID",
                "nameplate_capacity_mw": "Capacity (MW)",
                "status": "Status",
            },
        )
        if USE_MAPLIBRE_API:
            fig_assets = px.scatter_map(map_style="open-street-map", **map_kwargs)
        else:
            fig_assets = px.scatter_mapbox(mapbox_style="open-street-map", **map_kwargs)

        fig_assets.update_layout(
            **{MAP_LAYOUT_KEY: dict(
                style="open-street-map", center=asset_center, zoom=asset_zoom,
            )},
            font=dict(family=FONT, size=13, color=BLACK),
            paper_bgcolor=BG,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(
                title=dict(text="Technology"),
                font=dict(family=FONT, size=12, color=BLACK),
                bgcolor="rgba(251,249,247,0.94)",
                x=0.015, y=0.985, xanchor="left", yanchor="top",
            ),
        )
        st.plotly_chart(fig_assets, use_container_width=True, key="renewable_assets_map")
    else:
        st.info("No renewable assets with valid coordinates match the current technology filter.")


# ============================================================
# DEDICATED TRANSMISSION NETWORK MAP
# ============================================================

with tab_transmission_map:
    st.markdown(
        '<div class="section-title">Transmission network</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Explore the U.S. transmission grid using the interactive map. Pan and zoom, "
        "use the map controls, and select a transmission line to view its available attributes."
    )

    interactive_grid_map_url = (
        "https://www.arcgis.com/apps/mapviewer/index.html"
        "?layers=d77284d1a97a426eaf960bab4764999c"
    )
    st.markdown(
        "<div style='border:1px solid #E7E0DB;border-radius:10px;overflow:hidden;"
        "background:#FFFDFA;padding:6px;'>",
        unsafe_allow_html=True,
    )
    st.components.v1.iframe(
        src=interactive_grid_map_url,
        height=820,
        scrolling=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        f"[Open interactive map in a new tab]({interactive_grid_map_url})"
    )
    st.caption(
        "Feature information and pop-ups depend on the attributes available in the map layer. "
        "If the map is blocked by browser or organization policy, open it in a new tab."
    )

# ============================================================
# PROJECT REGISTER / DETAILS / ANALYTICS / DATA SOURCES
# ============================================================

# ============================================================
# PROJECT REGISTER
# ============================================================

with tab_register:
    st.markdown(
        '<div class="section-title">Project and generator register</div>',
        unsafe_allow_html=True,
    )

    search_text = st.text_input(
        "Search project records",
        placeholder="Plant name, owner, state, county or generator ID",
    )

    searchable_columns = [
        "plant_name",
        "state",
        "county",
        "entity_name",
        "technology_group",
        "generator_id",
        "plant_code",
        "status",
        "energy_source_code",
        "prime_mover_code",
    ]

    searchable_columns = [
        c for c in searchable_columns if c in filtered.columns
    ]

    results = filtered.copy()

    if search_text.strip() and searchable_columns:
        matches = results[searchable_columns].apply(
            lambda col: col.astype(str).str.contains(
                search_text.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        results = results[matches].copy()

    display_columns = [
        "plant_name",
        "technology_display",
        "entity_name",
        "state",
        "county",
        "plant_code",
        "generator_id",
        "nameplate_capacity_mw",
        "net_summer_capacity_mw",
        "energy_capacity_mwh",
        "status",
        "operating_year",
        "planned_operating_year",
    ]

    display_columns = [
        c for c in display_columns if c in results.columns
    ]

    st.dataframe(
        results[display_columns],
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    st.caption(f"{len(results):,} matching records.")

    st.download_button(
        "Download filtered project records",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="sunstripe_filtered_projects.csv",
        mime="text/csv",
    )


# ============================================================
# PROJECT DETAILS
# ============================================================

with tab_details:
    st.markdown(
        '<div class="section-title">Complete project information</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No records match the current filters.")
    else:
        options = filtered.copy()

        options["_display"] = (
            options["plant_name"].fillna("Unnamed plant").astype(str)
            + " | "
            + options["state"].fillna("Unknown").astype(str)
            + " | "
            + options["technology_display"].astype(str)
            + " | "
            + options["nameplate_capacity_mw"].fillna(0).map(
                lambda x: f"{x:,.2f} MW"
            )
            + " | "
            + options["record_id"].astype(str)
        )

        label_to_id = dict(
            zip(options["_display"], options["record_id"])
        )

        chosen = st.selectbox(
            "Select a project or generator",
            options["_display"].tolist(),
        )

        chosen_id = label_to_id[chosen]

        project = filtered[
            filtered["record_id"] == chosen_id
        ].iloc[0]

        st.markdown(f"### {project['plant_name']}")

        d1, d2, d3, d4 = st.columns(4)

        d1.metric("Technology", project["technology_display"])

        mw = project["nameplate_capacity_mw"]
        d2.metric(
            "Nameplate capacity",
            f"{mw:,.2f} MW" if pd.notna(mw) else "Not reported",
        )

        d3.metric("State", str(project.get("state", "Unknown")))
        d4.metric("Status", str(project.get("status", "Not reported")))

        key_fields = [
            ("Plant name", "plant_name"),
            ("Technology", "technology_group"),
            ("Plant code", "plant_code"),
            ("Generator ID", "generator_id"),
            ("Owner / reporting entity", "entity_name"),
            ("Entity ID", "entity_id"),
            ("Producer type", "producer_type"),
            ("Energy source code", "energy_source_code"),
            ("Prime mover code", "prime_mover_code"),
            ("Nameplate capacity (MW)", "nameplate_capacity_mw"),
            ("Net summer capacity (MW)", "net_summer_capacity_mw"),
            ("Energy capacity (MWh)", "energy_capacity_mwh"),
            ("Status", "status"),
            ("State", "state"),
            ("County", "county"),
            ("Latitude", "latitude"),
            ("Longitude", "longitude"),
            ("Operating year", "operating_year"),
            ("Operating month", "operating_month"),
            ("Planned operating year", "planned_operating_year"),
            ("Planned operating month", "planned_operating_month"),
            ("Source dataset", "source_dataset"),
        ]

        detail_rows = []

        for label, field in key_fields:
            value = project.get(field, None)

            if value is None or pd.isna(value) or str(value).strip() == "":
                value = "Not reported in this record"
            elif field in ("latitude", "longitude"):
                value = f"{float(value):.6f}"
            elif field in (
                "nameplate_capacity_mw",
                "net_summer_capacity_mw",
                "energy_capacity_mwh",
            ):
                value = f"{float(value):,.2f}"

            detail_rows.append({
                "Information": label,
                "Value": str(value),
            })

        st.markdown(
            '<div class="section-title">Key project information</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            pd.DataFrame(detail_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            '<div class="section-title">Complete source record</div>',
            unsafe_allow_html=True,
        )

        raw_record = project.drop(
            labels=["_display"], errors="ignore"
        )

        raw_details = pd.DataFrame({
            "Field": raw_record.index.astype(str),
            "Value": [
                "Not reported" if pd.isna(value) else str(value)
                for value in raw_record.values
            ],
        })

        st.dataframe(
            raw_details,
            use_container_width=True,
            hide_index=True,
            height=500,
        )

        st.download_button(
            "Download complete project record",
            data=raw_record.to_frame().T.to_csv(index=False).encode("utf-8"),
            file_name=f"sunstripe_project_{chosen_id}.csv",
            mime="text/csv",
        )

        record_url = project.get("source_url", "")

        if isinstance(record_url, str) and record_url.startswith("https://"):
            st.markdown(f"[Open source workbook]({record_url})")
        elif data_mode == "EIA live inventory":
            st.markdown(f"[Open official EIA page]({EIA_PAGE})")

        st.warning(
            "This view shows the available fields from the selected dataset. "
            "Parcel ownership, land valuation, permits, interconnection studies, "
            "storage duration and project revenue may require separate sources."
        )


# ============================================================
# TECHNOLOGY ANALYTICS
# ============================================================

with tab_analytics:
    st.markdown(
        '<div class="section-title">Technology analytics</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No records available for the current filters.")
    else:
        by_state = (
            filtered.groupby("state", as_index=False)
            ["nameplate_capacity_mw"].sum()
            .sort_values("nameplate_capacity_mw", ascending=False)
            .head(15)
        )

        fig = px.bar(
            by_state,
            x="state",
            y="nameplate_capacity_mw",
            text="nameplate_capacity_mw",
            title=f"{technology_choice}: capacity by state",
            labels={
                "state": "State",
                "nameplate_capacity_mw": "Nameplate capacity (MW)",
            },
        )

        fig.update_traces(
            marker_color=RED,
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(family=FONT, size=11, color=BLACK),
            cliponaxis=False,
        )

        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

        by_status = (
            filtered.groupby("status", as_index=False)
            .size()
            .rename(columns={"size": "Generator records"})
            .sort_values("Generator records", ascending=False)
        )

        fig2 = px.bar(
            by_status,
            x="status",
            y="Generator records",
            text="Generator records",
            title=f"{technology_choice}: records by status",
        )

        fig2.update_traces(
            marker_color=RED,
            textposition="outside",
            textfont=dict(family=FONT, size=11, color=BLACK),
            cliponaxis=False,
        )

        fig2 = style_chart(fig2)
        st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# DATA SOURCES AND LIMITATIONS
# ============================================================

with tab_method:
    st.markdown(
        '<div class="section-title">Data sources and methodology</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    **Transmission grid color coding**

    Transmission lines are colored by the kV value in the uploaded line dataset:
    - **138 kV — orange**
    - **240 kV — green**
    - 69 kV — purple; 115 kV — blue; 161 kV — vermilion; 230 kV — violet;
      345 kV — gold; 500 kV — deep red; 765 kV — charcoal.

    Other reported voltage levels receive a separate color automatically. Lines
    with no recognized voltage are shown in grey. The legend only appears for
    voltage classes present in the uploaded transmission dataset.
    """)

    st.markdown(f"""
**Current dataset:** {source_label}

**Official EIA-860M page:**  
{EIA_PAGE}

EIA's monthly inventory contains reported generator information for existing
and proposed generation. Monthly data may be preliminary and revised.

A generator-level row is not necessarily a distinct development project.
Some records may not have coordinates or reported storage energy capacity.
""")

    sources = pd.DataFrame([
        {
            "Provider": "EIA monthly inventory",
            "Purpose": "Generator records",
            "Official source": EIA_PAGE,
        },
        {
            "Provider": "EIA annual inventory",
            "Purpose": "Annual generator data",
            "Official source": "https://www.eia.gov/electricity/data/eia860/",
        },
        {
            "Provider": "NREL",
            "Purpose": "Renewable resource information",
            "Official source": "https://developer.nrel.gov/",
        },
        {
            "Provider": "USGS",
            "Purpose": "Elevation and terrain",
            "Official source": "https://www.usgs.gov/",
        },
        {
            "Provider": "FEMA",
            "Purpose": "Flood hazard information",
            "Official source": "https://www.fema.gov/flood-maps",
        },
        {
            "Provider": "USFWS",
            "Purpose": "Wetlands and ecology",
            "Official source": "https://www.fws.gov/",
        },
        {
            "Provider": "ERCOT",
            "Purpose": "Texas power market",
            "Official source": "https://www.ercot.com/",
        },
        {
            "Provider": "CAISO",
            "Purpose": "California power market",
            "Official source": "https://www.caiso.com/",
        },
        {
            "Provider": "MISO",
            "Purpose": "Regional market information",
            "Official source": "https://www.misoenergy.org/",
        },
        {
            "Provider": "PJM",
            "Purpose": "Regional market information",
            "Official source": "https://www.pjm.com/",
        },
    ])

    st.dataframe(
        sources,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Official source": st.column_config.LinkColumn(
                "Official source"
            ),
        },
    )

    status_table = pd.DataFrame([
        {"Feature": "Solar / Wind / BESS selection", "Status": "Implemented"},
        {"Feature": "Technology-aware filtering", "Status": "Implemented"},
        {"Feature": "Project-level detail", "Status": "Implemented"},
        {"Feature": "Repository CSV normalization", "Status": "Implemented"},
        {"Feature": "CSV, XLS and XLSX upload", "Status": "Implemented"},
        {"Feature": "Optional EIA workbook connector", "Status": "Internet required"},
        {"Feature": "Repository transmission CSV/KMZ auto-discovery", "Status": "Implemented"},
        {"Feature": "Voltage-colored transmission lines + legend", "Status": "Implemented"},
        {"Feature": "Grid/substation points from spatial data", "Status": "When point geometry is present"},
        {"Feature": "Parcel ownership / assessor records", "Status": "Available when parcel data access is configured; coverage varies"},
        {"Feature": "Verified interconnection capacity", "Status": "Not connected"},
        {"Feature": "Live power-market prices", "Status": "Not connected"},
    ])

    st.markdown(
        '<div class="section-title">Implementation status</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        status_table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# LAND & REAL ESTATE — SITE AND PARCEL INTELLIGENCE (FINAL SIGNAL TAB)
# Native interactive map + coordinate-based assessor/parcel lookup.
# ============================================================


def _land_data_api_key():
    """Read the current Parceled key, preferring Streamlit deployment secrets.

    PARCELED_API_KEY is preferred; PARCEL_DATA_API_KEY remains supported.
    Secrets take priority over environment variables so a stale environment key
    cannot override the key configured for the deployed app.
    """
    try:
        for name in ("PARCELED_API_KEY", "PARCEL_DATA_API_KEY"):
            key = str(st.secrets.get(name, "")).strip().strip("\"'")
            if key:
                return key
    except Exception:
        pass
    for name in ("PARCELED_API_KEY", "PARCEL_DATA_API_KEY"):
        key = os.getenv(name, "").strip().strip("\"'")
        if key:
            return key
    return ""


def _land_geocode_address(query):
    """Resolve a US address or a 'latitude, longitude' pair."""
    query = str(query or "").strip()
    if not query:
        raise ValueError("Enter a US address or latitude, longitude.")

    coordinate_match = re.fullmatch(
        r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*",
        query,
    )
    if coordinate_match:
        lat = float(coordinate_match.group(1))
        lon = float(coordinate_match.group(2))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("The coordinates are outside the valid latitude/longitude range.")
        return lat, lon, f"Coordinates: {lat:.6f}, {lon:.6f}"

    response = requests.get(
        "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
        params={
            "address": query,
            "benchmark": "Public_AR_Current",
            "format": "json",
        },
        headers={"User-Agent": "SunstripeSelect/1.0"},
        timeout=15,
    )
    response.raise_for_status()
    body = response.json()
    matches = body.get("result", {}).get("addressMatches", [])
    if not matches:
        raise ValueError("No matching US address was found. Try a more complete address or enter coordinates.")
    match = matches[0]
    coordinates = match.get("coordinates", {})
    lon = float(coordinates["x"])
    lat = float(coordinates["y"])
    return lat, lon, match.get("matchedAddress", query)


def _parse_mcp_json(response):
    """Parse either JSON or server-sent-event JSON returned by the data API."""
    try:
        return response.json()
    except ValueError:
        pass

    for line in response.text.splitlines():
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload and payload != "[DONE]":
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    continue
    raise RuntimeError("The parcel-data service returned an unreadable response.")


@st.cache_data(ttl=900, show_spinner=False)
def _lookup_land_parcel(lat, lon, api_key):
    """Look up a parcel using the same endpoint, auth header, and known-good fields as Parceled's API Explorer."""
    clean_api_key = str(api_key or "").strip().strip("\\\"'")
    if not clean_api_key:
        raise RuntimeError("Add PARCELED_API_KEY in Streamlit Secrets before looking up a parcel.")

    # Match the working Parceled API Explorer exactly. Avoid an unrelated
    # coverage preflight and unverified schema fields that can mask the real result.
    query = """
    query GetParcel($lat: Float!, $lng: Float!) {
      getParcel(lat: $lat, lng: $lng) {
        parcel {
          parcelId
          state
        }
      }
    }
    """
    headers = {
        "Authorization": f"Bearer {clean_api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "SunstripeSelect/1.0",
    }

    try:
        response = requests.post(
            "https://www.parceled.ai/api/",
            json={"query": query, "variables": {"lat": float(lat), "lng": float(lon)}},
            headers=headers,
            timeout=25,
        )
        if response.status_code == 402:
            try:
                detail = response.json().get("message", "Parceled reports insufficient credits or a budget limit.")
            except ValueError:
                detail = "Parceled reports insufficient credits or a budget limit."
            raise RuntimeError(detail)
        if response.status_code == 429:
            raise RuntimeError("Parceled rate limit reached. Wait briefly, then retry.")
        if response.status_code in (401, 403):
            raise RuntimeError(
                f"Parceled rejected authentication (HTTP {response.status_code}). "
                "The request now matches the API Explorer's Bearer header and endpoint. "
                "Check that Streamlit Secrets contains the same active Parceled key; never paste the key into chat."
            )
        response.raise_for_status()
        payload = _parse_mcp_json(response)
        if not isinstance(payload, dict):
            raise RuntimeError("Parceled returned an unexpected response format.")
        if payload.get("errors"):
            messages = [str(item.get("message", "GraphQL request failed")) for item in payload["errors"] if isinstance(item, dict)]
            # Surface the real GraphQL error instead of replacing it with a generic auth warning.
            raise RuntimeError("Parceled GraphQL error: " + "; ".join(messages[:3]))
        get_parcel = (payload.get("data") or {}).get("getParcel") or {}
        if not isinstance(get_parcel, dict) or not isinstance(get_parcel.get("parcel"), dict):
            payload["message"] = "Parceled responded successfully, but no parcel was found at these coordinates. Try moving the point inside the parcel boundary."
        return payload

    except requests.Timeout as exc:
        raise RuntimeError("Parceled request timed out. Please try again.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise RuntimeError(f"Parceled request failed (HTTP {status}).") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not connect to Parceled: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Parceled returned invalid JSON. Please try again.") from exc


def _land_find_parcel_record(value):
    """Walk a variable API response and find its parcel record, if present."""
    if isinstance(value, list):
        for item in value:
            found = _land_find_parcel_record(item)
            if found is not None:
                return found
        return None
    if not isinstance(value, dict):
        return None

    for key, child in value.items():
        normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
        if normalized in {"parcel", "parcelrecord", "property", "propertyrecord"}:
            if isinstance(child, dict) and child:
                return child
            if isinstance(child, list) and child:
                first = next((item for item in child if isinstance(item, dict)), None)
                if first is not None:
                    return first

    record_keys = {
        re.sub(r"[^a-z0-9]", "", str(key).lower())
        for key in value
    }
    if record_keys & {
        "parcelid", "apn", "assessorparcelnumber", "owner", "ownername",
        "situsaddress", "address", "landsize", "acreage", "acres",
    }:
        return value

    for child in value.values():
        found = _land_find_parcel_record(child)
        if found is not None:
            return found
    return None


def _land_flatten_fields(value, parent=""):
    """Flatten nested parcel properties for a clean field/value table."""
    flat = {}
    if isinstance(value, dict):
        for key, child in value.items():
            label = f"{parent} · {key}" if parent else str(key)
            if isinstance(child, dict):
                flat.update(_land_flatten_fields(child, label))
            elif isinstance(child, list):
                if child and all(not isinstance(x, (dict, list)) for x in child):
                    flat[label] = ", ".join(str(x) for x in child)
                elif child:
                    flat[label] = f"{len(child)} record(s)"
            elif child is not None and str(child).strip() not in {"", "None", "null"}:
                flat[label] = child
    elif isinstance(value, list):
        for index, child in enumerate(value, start=1):
            flat.update(_land_flatten_fields(child, f"{parent or 'Record'} {index}"))
    return flat


def _land_get_field(record, aliases):
    if not isinstance(record, dict):
        return None
    lookup = {
        re.sub(r"[^a-z0-9]", "", str(key).lower()): value
        for key, value in record.items()
    }
    for alias in aliases:
        key = re.sub(r"[^a-z0-9]", "", alias.lower())
        value = lookup.get(key)
        if value is not None and str(value).strip() not in {"", "None", "null"}:
            return value
    return None


with tab_land_parcel:
    st.markdown(
        '<div class="section-title">Site & Land Parcel Intelligence</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Search a US address or coordinates, or click the map. When parcel records "
        "are connected, the selected parcel's available assessor and land information "
        "will load automatically."
    )

    # Use a deployment secret/environment variable for production; the session
    # input is available for quick testing without putting credentials in source code.
    configured_api_key = _land_data_api_key()
    with st.expander(
        "Parcel data connection",
        expanded=not bool(configured_api_key or st.session_state.get("land_parcel_api_key", "")),
    ):
        st.caption(
            "A parcel-data access key is required for real parcel identifiers and "
            "assessor records. The key is used server-side for this session. For a "
            "deployment-wide setup, set PARCELED_API_KEY in Streamlit secrets (PARCEL_DATA_API_KEY is also supported)."
        )
        session_api_key = st.text_input(
            "Parcel data access key",
            type="password",
            key="land_parcel_api_key",
            help="The key is not written into app.py. Configure Streamlit secrets for persistent deployment use.",
        )
        st.markdown(
            '[Parceled API documentation](https://parceled.ai/.well-known/openapi.yaml)'
        )
    parcel_api_key = configured_api_key or st.session_state.get("land_parcel_api_key", "").strip()

    if not parcel_api_key:
        st.info(
            "The interactive map is ready to use. Add the parcel data access key above "
            "to enable one-click property and assessor-record lookup. Without a data "
            "connection, this app cannot reliably show actual parcel ownership, sales, or values."
        )

    with st.form("land_parcel_address_form", clear_on_submit=False):
        address_col, search_col = st.columns([5, 1])
        with address_col:
            land_search_query = st.text_input(
                "Find a site",
                placeholder="Enter a US address or coordinates, e.g. 39.7392, -104.9903",
                key="land_parcel_search_query",
            )
        with search_col:
            st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
            land_search_submitted = st.form_submit_button(
                "Find site", type="primary", use_container_width=True
            )

    if "land_selected_lat" not in st.session_state:
        st.session_state.land_selected_lat = None
    if "land_selected_lon" not in st.session_state:
        st.session_state.land_selected_lon = None
    if "land_selected_label" not in st.session_state:
        st.session_state.land_selected_label = ""
    if "land_lookup_result" not in st.session_state:
        st.session_state.land_lookup_result = None
    if "land_lookup_key" not in st.session_state:
        st.session_state.land_lookup_key = None
    if "land_map_click_processed" not in st.session_state:
        st.session_state.land_map_click_processed = None

    if land_search_submitted:
        try:
            found_lat, found_lon, found_label = _land_geocode_address(land_search_query)
            st.session_state.land_selected_lat = found_lat
            st.session_state.land_selected_lon = found_lon
            st.session_state.land_selected_label = found_label
            st.session_state.land_lookup_result = None
            st.session_state.land_lookup_key = None
        except Exception as exc:
            st.error(str(exc))

    has_selected_location = (
        st.session_state.land_selected_lat is not None
        and st.session_state.land_selected_lon is not None
    )
    if has_selected_location:
        map_center = [st.session_state.land_selected_lat, st.session_state.land_selected_lon]
        map_zoom = 15
    else:
        map_center = [40.8, -90.5]
        map_zoom = 4

    parcel_map = folium.Map(
        location=map_center,
        zoom_start=map_zoom,
        tiles=None,
        control_scale=True,
        prefer_canvas=True,
    )
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        name="Street map",
        show=True,
    ).add_to(parcel_map)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satellite imagery",
        show=False,
    ).add_to(parcel_map)
    # Nationwide parcel-outline tiles render at detailed map zoom levels. They
    # display parcel geometry but do not expose private assessor attributes.
    folium.TileLayer(
        tiles=(
            "https://tiles.arcgis.com/tiles/KzeiCaQsMoeCfoCq/arcgis/rest/services/"
            "Regrid_Nationwide_Parcel_Boundaries_v1/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Parcel boundaries © Regrid; hosted by Esri",
        name="US parcel boundaries",
        overlay=True,
        control=True,
        show=True,
        min_zoom=15,
        max_zoom=17,
    ).add_to(parcel_map)
    MousePosition(
        position="bottomleft",
        separator=" | ",
        prefix="Coordinates:",
        num_digits=5,
    ).add_to(parcel_map)
    if has_selected_location:
        folium.Marker(
            [st.session_state.land_selected_lat, st.session_state.land_selected_lon],
            tooltip="Selected site",
            popup=st.session_state.land_selected_label or "Selected site",
            icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
        ).add_to(parcel_map)
    folium.LayerControl(collapsed=True).add_to(parcel_map)

    map_result = st_folium(
        parcel_map,
        width=None,
        height=600,
        key="sunstripe_land_parcel_map",
        returned_objects=["last_clicked"],
    )
    st.caption(
        "The nationwide parcel-outline layer becomes visible when zoomed in to "
        "parcel scale (zoom 15–17). Click a location to select it and load available "
        "property records below when the parcel-data connection is configured."
    )

    if map_result and map_result.get("last_clicked"):
        click_lat = float(map_result["last_clicked"]["lat"])
        click_lon = float(map_result["last_clicked"]["lng"])
        click_key = f"{click_lat:.6f},{click_lon:.6f}"
        if click_key != st.session_state.land_map_click_processed:
            st.session_state.land_map_click_processed = click_key
            st.session_state.land_selected_lat = click_lat
            st.session_state.land_selected_lon = click_lon
            st.session_state.land_selected_label = f"Selected map point: {click_lat:.6f}, {click_lon:.6f}"
            st.session_state.land_lookup_result = None
            st.session_state.land_lookup_key = None
            st.rerun()

    # A location is queried exactly once per selected coordinate when a key is available.
    if (
        parcel_api_key
        and st.session_state.land_selected_lat is not None
        and st.session_state.land_selected_lon is not None
    ):
        selected_lat = float(st.session_state.land_selected_lat)
        selected_lon = float(st.session_state.land_selected_lon)
        key_fingerprint = hashlib.sha256(parcel_api_key.encode("utf-8")).hexdigest()[:12]
        selected_key = f"{selected_lat:.6f},{selected_lon:.6f}:{key_fingerprint}"
        if selected_key != st.session_state.land_lookup_key:
            with st.spinner("Looking up parcel and assessor records…"):
                try:
                    result = _lookup_land_parcel(selected_lat, selected_lon, parcel_api_key)
                    st.session_state.land_lookup_result = {"ok": True, "data": result}
                    st.session_state.land_lookup_key = selected_key
                except Exception as exc:
                    st.session_state.land_lookup_result = {"ok": False, "error": str(exc)}
                    st.session_state.land_lookup_key = selected_key

    if st.session_state.land_selected_lat is not None:
        st.markdown(
            '<div class="section-title">Selected site</div>',
            unsafe_allow_html=True,
        )
        selected_lat_for_context = float(st.session_state.land_selected_lat)
        selected_lon_for_context = float(st.session_state.land_selected_lon)
        st.caption(
            f"{st.session_state.land_selected_label or 'Selected location'} · "
            f"{selected_lat_for_context:.6f}, {selected_lon_for_context:.6f}"
        )
        try:
            site_county, site_state, site_address = reverse_geocode(
                round(selected_lat_for_context, 5), round(selected_lon_for_context, 5)
            )
            site_context_cols = st.columns(3)
            site_context_cols[0].metric(
                "County", site_county if site_county and site_county != "Unknown" else "Not available"
            )
            site_context_cols[1].metric(
                "State", site_state if site_state and site_state != "Unknown" else "Not available"
            )
            site_context_cols[2].metric("Coordinates", f"{selected_lat_for_context:.4f}, {selected_lon_for_context:.4f}")
            if site_address:
                st.caption(f"Mapped location: {site_address}")
        except Exception:
            pass

        lookup_result = st.session_state.land_lookup_result
        if not parcel_api_key:
            st.info("Add the parcel data access key above to retrieve the selected parcel's actual property records.")
        elif lookup_result and not lookup_result.get("ok"):
            st.error(lookup_result.get("error", "Parcel lookup failed."))
        elif lookup_result and lookup_result.get("ok"):
            payload = lookup_result.get("data")
            # GraphQL returns parcel and assessor records as siblings. Combine them
            # for display while retaining the original response in the JSON expander.
            response_data = payload.get("data", {}) if isinstance(payload, dict) else {}
            get_parcel = response_data.get("getParcel", {}) if isinstance(response_data, dict) else {}
            parcel_record = get_parcel.get("parcel") if isinstance(get_parcel, dict) else None
            tax_assessor_record = get_parcel.get("taxAssessor") if isinstance(get_parcel, dict) else None
            if isinstance(parcel_record, dict) and isinstance(tax_assessor_record, dict):
                parcel_record = {**parcel_record, "taxAssessor": tax_assessor_record}
            if not isinstance(parcel_record, dict) or not parcel_record:
                parcel_record = _land_find_parcel_record(payload)
            if parcel_record:
                address_value = _land_get_field(
                    parcel_record,
                    ["address", "situsAddress", "propertyAddress", "siteAddress", "streetAddress"],
                )
                parcel_id = _land_get_field(
                    parcel_record,
                    ["parcelId", "parcel_id", "apn", "APN", "parcelNumber", "assessorParcelNumber", "parcelNumberFormatted"],
                )
                acreage = _land_get_field(
                    parcel_record,
                    ["acres", "acreage", "landAcres", "lotAcres", "landSizeAcres", "sizeAcres", "landSize"],
                )
                owner = _land_get_field(
                    parcel_record,
                    ["owner", "ownerName", "owner_name", "propertyOwner", "primaryOwner"],
                )
                sale_price = _land_get_field(
                    parcel_record,
                    ["lastSalePrice", "salePrice", "last_sale_price", "lastSaleAmount", "sale_amount"],
                )
                sale_date = _land_get_field(
                    parcel_record,
                    ["lastSaleDate", "saleDate", "last_sale_date", "recordedSaleDate"],
                )
                county = _land_get_field(parcel_record, ["county", "countyName"])
                state = _land_get_field(parcel_record, ["state", "stateName", "stateCode"])

                metric_cols = st.columns(3)
                metric_cols[0].metric("Property address", str(address_value or "Not reported"))
                metric_cols[1].metric("Parcel / APN", str(parcel_id or "Not reported"))
                metric_cols[2].metric("Land area", str(acreage or "Not reported"))

                detail_rows = []
                preferred = [
                    ("Owner", owner),
                    ("County", county),
                    ("State", state),
                    ("Last sale date", sale_date),
                    ("Last sale price", sale_price),
                ]
                for label, value in preferred:
                    if value is not None and str(value).strip():
                        detail_rows.append({"Property field": label, "Available record": value})

                flat_fields = _land_flatten_fields(parcel_record)
                already = {re.sub(r"[^a-z0-9]", "", row["Property field"].lower()) for row in detail_rows}
                preferred_alias_norms = {
                    "owner", "county", "state", "lastsaledate", "saleprice",
                    "lastsaleprice", "address", "situsaddress", "parcelid", "apn",
                    "acres", "acreage", "landsize", "landsiz acres".replace(" ", ""),
                }
                for field, value in flat_fields.items():
                    normalized_field = re.sub(r"[^a-z0-9]", "", field.lower())
                    if normalized_field not in preferred_alias_norms:
                        detail_rows.append({"Property field": field, "Available record": value})

                if county or state:
                    st.caption("Jurisdiction: " + ", ".join(str(v) for v in [county, state] if v))
                if detail_rows:
                    st.dataframe(
                        pd.DataFrame(detail_rows),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("A parcel record was returned, but it did not include additional displayable fields.")
                with st.expander("View complete parcel record"):
                    st.json(payload)
            else:
                st.warning(
                    "No parcel record was returned for this point. Move the marker to the parcel interior or try a nearby coordinate."
                )
                with st.expander("View lookup response"):
                    st.json(payload)

    st.caption(
        "Property data is sourced from assessor/recorder records where available. "
        "Coverage and field availability vary by jurisdiction; missing fields are not inferred."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div class="footer">
SUNSTRIPE LOCATION INTELLIGENCE · SOLAR / STORAGE / WIND
</div>
""", unsafe_allow_html=True)
