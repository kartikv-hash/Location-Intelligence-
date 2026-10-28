
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
