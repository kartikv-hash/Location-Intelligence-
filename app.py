
import io
import re
from datetime import date
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# SUNSTRIPE LOCATION INTELLIGENCE
# Public US Solar, Wind and Battery Project Explorer
# ============================================================

st.set_page_config(
    page_title="Sunstripe Location Intelligence",
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
FONT = "DM Sans, Arial, sans-serif"

TECH_COLORS = {
    "Solar": "#D9A72E",
    "Wind": "#41986A",
    "BESS": "#3979CC",
    "Other": "#89817B",
}

EIA_PAGE = "https://www.eia.gov/electricity/data/eia860m/index.php"


# ============================================================
# SUNSTRIPE THEME
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --navy: #050714;
    --red: #E8392D;
    --paper: #FBF9F7;
    --line: #E7E0DB;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
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

/* Main text on ivory background */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main small,
[data-testid="stAppViewContainer"] .main strong {
    color: #000000;
}

/* Sunstripe navigation */
.topbar {
    background: #050714;
    color: #FFFFFF;
    margin: -1rem -1rem 1.7rem -1rem;
    padding: 22px 24px 15px;
    border-bottom: 2px solid #E8392D;
}

.brand {
    font-family: 'DM Sans', Arial, sans-serif !important;
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

.eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #E8392D !important;
    margin: 5px 0 12px;
}

.hero {
    font-family: 'DM Sans', Arial, sans-serif !important;
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
    font-family: 'DM Sans', Arial, sans-serif !important;
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
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 26px;
    font-weight: 700;
    color: #E8392D !important;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 13px;
    font-weight: 600;
    border-radius: 22px;
    border: 1px solid #E8392D;
    color: #E8392D !important;
    background: transparent;
}

.stButton button:hover, .stDownloadButton button:hover {
    background: #E8392D !important;
    color: #FFFFFF !important;
}

/* Captions, dataframes and inputs */
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
    font-family: 'DM Sans', Arial, sans-serif !important;
    color: #000000 !important;
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
</style>
""", unsafe_allow_html=True)


# ============================================================
# PLOTLY THEME
# All chart labels, axes and legends remain readable
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
# EIA PUBLIC DATA CONNECTOR
# Dynamically finds the newest XLSX link on the EIA-860M page.
# No API key required. Internet access is required.
# ============================================================

@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def download_eia_inventory():
    response = requests.get(
        EIA_PAGE,
        timeout=30,
        headers={"User-Agent": "SunstripeLocationIntelligence/1.0"},
    )
    response.raise_for_status()
    html = response.text

    # Discover XLSX files linked by EIA rather than assuming a
    # permanent month/year filename.
    links = re.findall(
        r"""href\s*=\s*["']([^"']+\.xlsx(?:\?[^"']*)?)["']""",
        html,
        flags=re.IGNORECASE,
    )

    links = [
        urljoin(EIA_PAGE, href)
        for href in links
        if "generator" in href.lower() and "/xls/" in href.lower()
    ]

    if not links:
        raise RuntimeError(
            "No EIA-860M generator spreadsheet was found on the official page."
        )

    # EIA's page is listed latest month first.
    workbook_url = links[0]

    file_response = requests.get(
        workbook_url,
        timeout=90,
        headers={"User-Agent": "SunstripeLocationIntelligence/1.0"},
    )
    file_response.raise_for_status()

    workbook_bytes = file_response.content

    if not workbook_bytes:
        raise RuntimeError("The EIA workbook download was empty.")

    return workbook_bytes, workbook_url


def normalize_header(value):
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def read_eia_sheets(workbook_bytes, workbook_url):
    """
    Read each workbook sheet and detect its table header.
    Raw source fields are preserved for the project detail view.
    """
    excel = pd.ExcelFile(io.BytesIO(workbook_bytes), engine="openpyxl")
    frames = []

    for sheet in excel.sheet_names:
        raw = pd.read_excel(
            io.BytesIO(workbook_bytes),
            sheet_name=sheet,
            header=None,
            engine="openpyxl",
        )

        if raw.empty:
            continue

        header_row = None
        max_search = min(40, len(raw))

        for i in range(max_search):
            cells = [
                normalize_header(v)
                for v in raw.iloc[i].tolist()
                if pd.notna(v)
            ]

            has_name = any("plant name" in c for c in cells)
            has_generator = any("generator id" in c for c in cells)
            has_technology = any("technology" in c for c in cells)
            has_capacity = any("capacity" in c for c in cells)

            if has_name and (
                has_generator or has_technology or has_capacity
            ):
                header_row = i
                break

        if header_row is None:
            # Fallback for tabs with headers already on the first row.
            first_row = [
                normalize_header(v)
                for v in raw.iloc[0].tolist()
                if pd.notna(v)
            ]
            if any("plant name" in c for c in first_row):
                header_row = 0
            else:
                continue

        headers = [
            str(v).strip() if pd.notna(v) else f"unnamed_{j}"
            for j, v in enumerate(raw.iloc[header_row].tolist())
        ]

        df = raw.iloc[header_row + 1:].copy()
        df.columns = headers
        df = df.dropna(how="all")

        # Avoid unnamed filler columns.
        useful = [
            c for c in df.columns
            if not str(c).lower().startswith("unnamed")
            and not str(c).lower().startswith("unnamed_")
        ]
        df = df[useful].copy()

        if not df.empty:
            df["EIA Workbook Sheet"] = sheet
            df["EIA Source URL"] = workbook_url
            frames.append(df)

    if not frames:
        raise RuntimeError(
            "The EIA workbook downloaded, but no generator tables were detected."
        )

    return pd.concat(frames, ignore_index=True, sort=False)


def standardize_assets(df, source_name):
    """
    Standardize key columns while retaining all original source fields.
    """
    df = df.copy()

    # Build a lookup tolerant of spaces, case and punctuation.
    def key(column):
        return re.sub(r"[^a-z0-9]+", "", str(column).lower())

    lookup = {}
    for col in df.columns:
        lookup.setdefault(key(col), col)

    def find_column(candidates):
        for candidate in candidates:
            found = lookup.get(key(candidate))
            if found is not None:
                return found
        return None

    mappings = {
        "plant_name": [
            "Plant Name", "plant_name", "project_name", "facility_name", "name"
        ],
        "state": [
            "Plant State", "State", "Plant State Abbreviation", "state_name"
        ],
        "county": ["County", "Plant County", "county_name"],
        "plant_code": ["Plant Code", "Plant ID", "Plant Id", "plant_id"],
        "generator_id": ["Generator ID", "Generator Id", "generator"],
        "entity_name": ["Entity Name", "Utility Name", "Operator", "Owner"],
        "producer_type": ["Plant Producer Type", "Producer Type"],
        "technology_group": ["Technology", "Technology Type", "technology_group"],
        "energy_source_code": ["Energy Source Code", "Energy Source"],
        "prime_mover_code": ["Prime Mover Code", "Prime Mover"],
        "nameplate_capacity_mw": [
            "Nameplate Capacity (MW)", "Nameplate Capacity MW",
            "nameplate_capacity_mw", "Capacity (MW)", "capacity_mw"
        ],
        "net_summer_capacity_mw": [
            "Net Summer Capacity (MW)", "Net Summer Capacity MW"
        ],
        "status": ["Status", "Operating Status", "Lifecycle Status"],
        "operating_year": ["Operating Year", "Operating Year "],
        "operating_month": ["Operating Month", "Operating Month "],
        "planned_operating_year": [
            "Planned Operating Year", "Planned Year"
        ],
        "planned_operating_month": [
            "Planned Operating Month", "Planned Month"
        ],
        "latitude": [
            "Plant Latitude", "Latitude", "Plant Lat", "latitude"
        ],
        "longitude": [
            "Plant Longitude", "Longitude", "Plant Lon", "longitude"
        ],
        "entity_id": ["Entity ID", "Utility ID"],
    }

    for standard, candidates in mappings.items():
        if standard not in df.columns:
            original = find_column(candidates)
            if original is not None:
                df[standard] = df[original]

    defaults = {
        "plant_name": "Unnamed plant",
        "state": "Unknown",
        "county": "Unknown",
        "plant_code": None,
        "generator_id": None,
        "entity_name": "Not reported",
        "producer_type": "Not reported",
        "technology_group": "Unknown",
        "energy_source_code": "",
        "prime_mover_code": "",
        "nameplate_capacity_mw": None,
        "net_summer_capacity_mw": None,
        "status": "Not reported",
        "operating_year": None,
        "operating_month": None,
        "planned_operating_year": None,
        "planned_operating_month": None,
        "latitude": None,
        "longitude": None,
        "entity_id": None,
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    for col in [
        "nameplate_capacity_mw", "net_summer_capacity_mw",
        "latitude", "longitude", "operating_year",
        "operating_month", "planned_operating_year",
        "planned_operating_month",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    tech_text = df["technology_group"].fillna("").astype(str).str.lower()
    source_text = df["energy_source_code"].fillna("").astype(str).str.lower()
    mover_text = df["prime_mover_code"].fillna("").astype(str).str.lower()
    name_text = df["plant_name"].fillna("").astype(str).str.lower()

    is_bess = (
        tech_text.str.contains(r"batter|storage", regex=True)
        | mover_text.str.fullmatch("ba", na=False)
        | source_text.str.fullmatch("mwh", na=False)
    )

    is_wind = (
        tech_text.str.contains("wind", na=False)
        | source_text.str.fullmatch("wnd", na=False)
        | source_text.str.fullmatch("wds", na=False)
    )

    is_solar = (
        tech_text.str.contains(r"solar|photovoltaic|concentrat", regex=True)
        | source_text.str.fullmatch("sun", na=False)
        | mover_text.str.fullmatch("pv", na=False)
    )

    # BESS has precedence if generator fields identify battery storage.
    df["technology_display"] = "Other"
    df.loc[is_solar, "technology_display"] = "Solar"
    df.loc[is_wind, "technology_display"] = "Wind"
    df.loc[is_bess, "technology_display"] = "BESS"

    df["source_dataset"] = source_name

    # Unique row key for project selection, preserving Plant Code + Generator.
    df = df.reset_index(drop=True)
    df["record_id"] = [
        f"{df.iloc[i]['plant_code']}-{df.iloc[i]['generator_id']}-{i}"
        for i in range(len(df))
    ]

    return df


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def load_eia_assets():
    workbook_bytes, workbook_url = download_eia_inventory()
    raw = read_eia_sheets(workbook_bytes, workbook_url)
    normalized = standardize_assets(
        raw,
        "EIA-860M public monthly inventory",
    )

    # Include the requested technologies only.
    normalized = normalized[
        normalized["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()

    if normalized.empty:
        raise RuntimeError(
            "The workbook loaded but no Solar, Wind or BESS generator records "
            "were recognized. Inspect the current EIA column layout."
        )

    return normalized, workbook_url


# ============================================================
# LOAD CSV DATA
# ============================================================

@st.cache_data
def load_repository_csv():
    return pd.read_csv("renewable_asset_register.csv")


def load_csv_assets(uploaded_file):
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file)
        return standardize_assets(raw, "User-uploaded CSV")

    raw = load_repository_csv()
    return standardize_assets(raw, "Repository CSV")


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="topbar">
    <div class="brand">
        Sunstripe <span class="accent">Location Intelligence</span>
    </div>
    <div class="brand-tagline">
        Intelligence Platform for Energy Infrastructure
    </div>
    <div class="navrow">
        <span class="navitem active">ASSETS</span>
        <span class="navitem">GRID</span>
        <span class="navitem">SCREENING</span>
        <span class="navitem">MARKETS</span>
        <span class="navitem">RESEARCH</span>
        <span class="navitem">ABOUT</span>
    </div>
</div>

<div class="eyebrow">● LOCATION INTELLIGENCE / UNITED STATES</div>
<div class="hero">Find the right place to build.</div>
<div class="subtitle">
Explore the US renewable energy fleet, filter projects by technology,
inspect generator-level records and examine reported capacity, status,
ownership and location information.
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR: DATA SOURCE
# ============================================================

with st.sidebar:
    st.markdown("## Sunstripe")
    st.caption("LOCATION INTELLIGENCE PLATFORM")
    st.divider()

    data_source = st.radio(
        "Project data source",
        [
            "EIA public inventory",
            "Repository / uploaded CSV",
        ],
        index=0,
        help=(
            "EIA public inventory downloads the latest workbook linked from "
            "the official EIA-860M page. CSV mode uses your own repository "
            "or uploaded records."
        ),
    )

    uploaded_csv = None

    if data_source == "Repository / uploaded CSV":
        uploaded_csv = st.file_uploader(
            "Upload renewable asset CSV",
            type=["csv"],
        )

    st.divider()
    st.markdown("### Technology")
    st.caption("Select one technology to update the whole workspace.")


# ============================================================
# LOAD SELECTED SOURCE
# ============================================================

source_url = EIA_PAGE

if data_source == "EIA public inventory":
    try:
        with st.spinner("Connecting to the official EIA inventory..."):
            all_assets, source_url = load_eia_assets()
        source_label = "Official EIA-860M monthly generator inventory"
        source_note = (
            "EIA monthly inventory; capacities and status may be preliminary."
        )
    except Exception as exc:
        st.error(
            "The EIA dataset could not be downloaded or parsed. "
            "You can switch to Repository / uploaded CSV in the sidebar."
        )
        st.code(str(exc))
        st.markdown(
            f"[Open the official EIA-860M inventory]({EIA_PAGE})"
        )
        st.stop()
else:
    try:
        all_assets = load_csv_assets(uploaded_csv)
        source_label = (
            "User-uploaded CSV" if uploaded_csv is not None
            else "Repository renewable_asset_register.csv"
        )
        source_note = "Project information is limited to fields in the CSV."
    except FileNotFoundError:
        st.error(
            "renewable_asset_register.csv was not found in your GitHub "
            "repository. Upload a CSV or add that file to the repository root."
        )
        st.stop()
    except Exception as exc:
        st.error(f"Unable to read asset CSV: {exc}")
        st.stop()


# ============================================================
# TECHNOLOGY SELECTOR
# Selection filters map, KPIs, table, chart and details together.
# ============================================================

technology_choice = st.radio(
    "Show projects",
    ["All technologies", "Solar", "Wind", "BESS"],
    horizontal=True,
    key="technology_choice",
)

if technology_choice == "All technologies":
    filtered_assets = all_assets[
        all_assets["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()
else:
    filtered_assets = all_assets[
        all_assets["technology_display"] == technology_choice
    ].copy()

with st.sidebar:
    state_values = sorted(
        filtered_assets["state"].dropna().astype(str).unique().tolist()
    )

    selected_states = st.multiselect(
        "State",
        state_values,
        default=[],
        help="Leave empty to include all states.",
    )

    status_values = sorted(
        filtered_assets["status"].fillna("Unknown").astype(str).unique().tolist()
    )

    selected_statuses = st.multiselect(
        "Project / generator status",
        status_values,
        default=status_values,
    )

    max_capacity = pd.to_numeric(
        filtered_assets["nameplate_capacity_mw"], errors="coerce"
    ).max()

    max_capacity = (
        max(1.0, float(max_capacity))
        if pd.notna(max_capacity)
        else 1.0
    )

    capacity_range = st.slider(
        "Nameplate capacity (MW)",
        min_value=0.0,
        max_value=max_capacity,
        value=(0.0, max_capacity),
    )


filtered_assets = filtered_assets[
    filtered_assets["status"].fillna("Unknown").astype(str).isin(selected_statuses)
].copy()

if selected_states:
    filtered_assets = filtered_assets[
        filtered_assets["state"].astype(str).isin(selected_states)
    ].copy()

filtered_assets["nameplate_capacity_mw"] = pd.to_numeric(
    filtered_assets["nameplate_capacity_mw"], errors="coerce"
)

filtered_assets = filtered_assets[
    filtered_assets["nameplate_capacity_mw"].between(
        capacity_range[0], capacity_range[1]
    )
].copy()


# ============================================================
# PORTFOLIO KPIs
# ============================================================

total_records = len(filtered_assets)

total_mw = filtered_assets["nameplate_capacity_mw"].sum()

states_count = filtered_assets["state"].nunique()

plants_count = (
    filtered_assets["plant_code"].nunique()
    if "plant_code" in filtered_assets
    else total_records
)

total_mwh = (
    pd.to_numeric(
        filtered_assets.get(
            "energy_capacity_mwh",
            pd.Series(index=filtered_assets.index, dtype=float),
        ),
        errors="coerce",
    ).sum()
)

technology_counts = filtered_assets["technology_display"].value_counts()

solar_count = int(technology_counts.get("Solar", 0))
wind_count = int(technology_counts.get("Wind", 0))
bess_count = int(technology_counts.get("BESS", 0))

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{total_records:,}</div><div class="kpi-label">'
        'Generator records in view</div></div>',
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{total_mw:,.1f} MW</div><div class="kpi-label">'
        'Represented nameplate capacity</div></div>',
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{plants_count:,}</div><div class="kpi-label">'
        'Distinct plant codes in view</div></div>',
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{states_count:,}</div><div class="kpi-label">'
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

st.caption(
    f"Data source: {source_label}. "
    f"{source_note}"
)

if data_source == "EIA public inventory":
    st.markdown(f"[View original dataset on EIA]({source_url})")


# ============================================================
# MAIN WORKSPACE
# ============================================================

tab_map, tab_projects, tab_details, tab_analytics, tab_sources = st.tabs([
    "Location explorer",
    "Project register",
    "Project details",
    "Technology analytics",
    "Data & limitations",
])


# ============================================================
# LOCATION EXPLORER
# ============================================================

with tab_map:
    st.markdown(
        '<div class="section-title">Geographic asset intelligence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        f"Map scope: {technology_choice}. "
        "The map displays only records with usable latitude and longitude."
    )

    map_data = filtered_assets.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    map_data = map_data[
        map_data["latitude"].between(-90, 90)
        & map_data["longitude"].between(-180, 180)
    ]

    if map_data.empty:
        st.warning(
            "The filtered data contains no usable coordinates. "
            "The project register and project-detail view remain available. "
            "Upload a dataset with latitude and longitude for mapping."
        )
    else:
        fig_map = px.scatter_map(
            map_data,
            lat="latitude",
            lon="longitude",
            color="technology_display",
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
            color_discrete_map=TECH_COLORS,
            map_style="open-street-map",
            zoom=3,
            height=620,
            labels={
                "technology_display": "Technology",
                "plant_code": "Plant code",
                "generator_id": "Generator ID",
                "nameplate_capacity_mw": "Nameplate capacity (MW)",
                "status": "Status",
                "state": "State",
                "county": "County",
            },
        )

        fig_map.update_layout(
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            font=dict(family=FONT, size=13, color=BLACK),
            legend=dict(
                font=dict(family=FONT, size=12, color=BLACK),
                bgcolor="rgba(251,249,247,0.9)",
            ),
            margin=dict(t=10, b=10, l=10, r=10),
        )

        st.plotly_chart(fig_map, use_container_width=True)

        st.caption(
            "Plant/generator coordinates are not parcel boundaries. "
            "A mapped location does not establish land availability "
            "or interconnection feasibility."
        )


# ============================================================
# PROJECT REGISTER
# ============================================================

with tab_projects:
    st.markdown(
        '<div class="section-title">Project and generator register</div>',
        unsafe_allow_html=True,
    )

    search_text = st.text_input(
        "Search projects",
        placeholder="Search project, owner, plant code, state or county",
        key="project_search",
    )

    searchable_fields = [
        "plant_name", "state", "county", "entity_name",
        "technology_group", "generator_id", "plant_code",
        "status", "energy_source_code", "prime_mover_code",
    ]

    searchable_fields = [
        c for c in searchable_fields if c in filtered_assets.columns
    ]

    search_results = filtered_assets.copy()

    if search_text.strip():
        mask = search_results[searchable_fields].apply(
            lambda col: col.astype(str).str.contains(
                search_text.strip(), case=False, na=False, regex=False
            )
        ).any(axis=1)

        search_results = search_results[mask].copy()

    display_fields = [
        "plant_name",
        "technology_display",
        "entity_name",
        "state",
        "county",
        "plant_code",
        "generator_id",
        "nameplate_capacity_mw",
        "net_summer_capacity_mw",
        "status",
        "operating_year",
        "planned_operating_year",
    ]

    display_fields = [
        c for c in display_fields if c in search_results.columns
    ]

    shown = search_results[display_fields].copy()

    if "technology_display" in shown:
        shown = shown.rename(
            columns={"technology_display": "Technology"}
        )

    st.dataframe(
        shown,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    st.caption(f"{len(search_results):,} records match this view.")

    st.download_button(
        "Download filtered projects CSV",
        data=search_results.to_csv(index=False).encode("utf-8"),
        file_name="sunstripe_filtered_projects.csv",
        mime="text/csv",
    )


# ============================================================
# SELECT A PROJECT
# Use the same technology- and filter-restricted dataset.
# ============================================================

with tab_details:
    st.markdown(
        '<div class="section-title">Full project information</div>',
        unsafe_allow_html=True,
    )

    if filtered_assets.empty:
        st.info("No projects match the selected filters.")
    else:
        detail_options = filtered_assets.copy()

        detail_options["_display"] = (
            detail_options["plant_name"].fillna("Unnamed plant").astype(str)
            + " | "
            + detail_options["state"].fillna("Unknown").astype(str)
            + " | "
            + detail_options["technology_display"].astype(str)
            + " | "
            + detail_options["nameplate_capacity_mw"].fillna(0).map(
                lambda x: f"{x:,.2f} MW"
            )
            + " | Record "
            + detail_options["record_id"].astype(str)
        )

        display_to_id = dict(
            zip(detail_options["_display"], detail_options["record_id"])
        )

        selected_display = st.selectbox(
            "Select a project / generator",
            options=detail_options["_display"].tolist(),
        )

        selected_record_id = display_to_id[selected_display]

        selected_project = filtered_assets[
            filtered_assets["record_id"] == selected_record_id
        ].iloc[0]

        st.markdown(f"### {selected_project['plant_name']}")

        p1, p2, p3, p4 = st.columns(4)

        p1.metric(
            "Technology",
            selected_project["technology_display"],
        )

        p2.metric(
            "Nameplate capacity",
            (
                f"{selected_project['nameplate_capacity_mw']:,.2f} MW"
                if pd.notna(selected_project["nameplate_capacity_mw"])
                else "Not reported"
            ),
        )

        p3.metric(
            "State",
            str(selected_project.get("state", "Not reported")),
        )

        p4.metric(
            "Reported status",
            str(selected_project.get("status", "Not reported")),
        )

        st.markdown(
            '<div class="section-title">Key project information</div>',
            unsafe_allow_html=True,
        )

        key_fields = [
            ("Plant name", "plant_name"),
            ("Technology", "technology_group"),
            ("Plant code / ID", "plant_code"),
            ("Generator ID", "generator_id"),
            ("Owner / reporting entity", "entity_name"),
            ("Entity ID", "entity_id"),
            ("Plant producer type", "producer_type"),
            ("Energy source code", "energy_source_code"),
            ("Prime mover code", "prime_mover_code"),
            ("Nameplate capacity (MW)", "nameplate_capacity_mw"),
            ("Net summer capacity (MW)", "net_summer_capacity_mw"),
            ("Status", "status"),
            ("State", "state"),
            ("County", "county"),
            ("Latitude", "latitude"),
            ("Longitude", "longitude"),
            ("Operating year", "operating_year"),
            ("Operating month", "operating_month"),
            ("Planned operating year", "planned_operating_year"),
            ("Planned operating month", "planned_operating_month"),
        ]

        key_data = []

        for label, field in key_fields:
            value = selected_project.get(field, None)

            if value is None or pd.isna(value) or str(value).strip() == "":
                value = "Not reported in this record"

            if field in [
                "nameplate_capacity_mw", "net_summer_capacity_mw",
                "latitude", "longitude",
            ] and isinstance(value, (float, int)):
                value = f"{value:,.5f}" if field in ["latitude", "longitude"] else f"{value:,.2f}"

            key_data.append({
                "Information": label,
                "Value": str(value),
            })

        st.dataframe(
            pd.DataFrame(key_data),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            '<div class="section-title">Complete source record</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            "This table contains all columns available for the selected row, "
            "including original EIA fields when the EIA source is selected."
        )

        raw_record = selected_project.drop(labels=["_display"], errors="ignore")

        raw_data = pd.DataFrame({
            "Field": raw_record.index.astype(str),
            "Value": [
                "Not reported" if pd.isna(v) else str(v)
                for v in raw_record.values
            ],
        })

        st.dataframe(
            raw_data,
            use_container_width=True,
            hide_index=True,
            height=550,
        )

        record_csv = selected_project.to_frame().T.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download this project's complete record",
            data=record_csv,
            file_name=f"sunstripe_project_{selected_record_id}.csv",
            mime="text/csv",
        )

        original_url = selected_project.get("EIA Source URL", EIA_PAGE)

        st.markdown(
            f"[Open official source page]({original_url})"
        )

        st.warning(
            "The public inventory provides reported generator/facility information, "
            "not a complete commercial project dossier. Parcel ownership, land "
            "price, permits, environmental assessments, interconnection study "
            "results and financial performance are not guaranteed to be included."
        )


# ============================================================
# TECHNOLOGY ANALYTICS
# ============================================================

with tab_analytics:
    st.markdown(
        '<div class="section-title">Technology analytics</div>',
        unsafe_allow_html=True,
    )

    if filtered_assets.empty:
        st.info("No records to chart.")
    else:
        by_state = (
            filtered_assets.groupby("state", as_index=False)
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
            hovertemplate=(
                "<b>%{x}</b><br>Capacity: %{y:,.1f} MW<extra></extra>"
            ),
        )

        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

        counts_by_status = (
            filtered_assets.groupby("status", as_index=False)
            .size()
            .rename(columns={"size": "Generator records"})
            .sort_values("Generator records", ascending=False)
        )

        fig2 = px.bar(
            counts_by_status,
            x="status",
            y="Generator records",
            text="Generator records",
            title=f"{technology_choice}: records by reported status",
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

with tab_sources:
    st.markdown(
        '<div class="section-title">Data source and methodology</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
**Selected source:** {source_label}

**Official EIA-860M inventory:**  
{EIA_PAGE}

The monthly EIA inventory contains generator-level information about existing
and proposed capacity. EIA notes that monthly values are preliminary and may
be revised in subsequent releases.

**Important distinctions**

- A generator record is not necessarily the same as an overall project.
- A single power plant can contain several generator records.
- A storage record may expose power capacity without providing energy capacity in MWh.
- Coordinates may be absent from some records.
- The source does not guarantee parcel, ownership, permitting, market revenue
  or interconnection feasibility data.
- The map and project-detail view can display only fields actually reported
  in the selected source.
""")

    st.markdown(
        '<div class="section-title">Other public source directories</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
- [EIA annual generator inventory (EIA-860)](https://www.eia.gov/electricity/data/eia860/)
- [EIA electricity data](https://www.eia.gov/electricity/data.php)
- [NREL developer resources](https://developer.nrel.gov/)
- [USGS National Map](https://www.usgs.gov/the-national-map-data-delivery)
- [FEMA flood maps](https://www.fema.gov/flood-maps)
- [US Fish and Wildlife Service](https://www.fws.gov/)
- [ERCOT](https://www.ercot.com/)
- [CAISO](https://www.caiso.com/)
- [MISO](https://www.misoenergy.org/)
- [PJM](https://www.pjm.com/)
""")

    st.markdown(
        '<div class="section-title">Data status</div>',
        unsafe_allow_html=True,
    )

    health = pd.DataFrame([
        {
            "Component": "Technology filtering",
            "Status": "Implemented",
        },
        {
            "Component": "Full source record viewer",
            "Status": "Implemented",
        },
        {
            "Component": "EIA public workbook connector",
            "Status": "Implemented; requires internet access",
        },
        {
            "Component": "Project coordinates and map",
            "Status": "Only when coordinates are available",
        },
        {
            "Component": "Parcel ownership and valuation",
            "Status": "Not connected",
        },
        {
            "Component": "Verified interconnection capacity",
            "Status": "Not connected",
        },
        {
            "Component": "Live prices and project revenues",
            "Status": "Not connected",
        },
    ])

    st.dataframe(
        health,
        use_container_width=True,
        hide_index=True,
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
