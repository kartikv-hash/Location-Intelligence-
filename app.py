
import io
import re
import zipfile
import html
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
import pydeck as pdk
import requests
import streamlit as st


# ============================================================
# SUNSTRIPE LOCATION INTELLIGENCE
# Solar | Wind | Battery Energy Storage Systems
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
MAX_UPLOAD_MB = 50


# ============================================================
# THEME: SUNSTRIPE BLACK, IVORY AND RED
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], button, input, textarea, select {
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

/* Keep large interactive maps inside the main content width. */
[data-testid="stPydeckChart"],
[data-testid="stDeckGlJsonChart"],
[data-testid="stVegaLiteChart"] {
    max-width: 100% !important;
    overflow: hidden !important;
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
.stButton button,
.stDownloadButton button {
    font-family: 'DM Sans', Arial, sans-serif !important;
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
    font-family: 'DM Sans', Arial, sans-serif !important;
    color: #000000 !important;
}

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #000000 !important;
    opacity: 0.7;
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

@media (max-width: 768px) {
    .brand { font-size: 22px; }
    .navrow { gap: 14px; font-size: 12px; }
    .hero { font-size: 32px; letter-spacing: -0.7px; }
    .subtitle { font-size: 14px; }
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
Explore US renewable energy projects. Choose Solar, Wind or BESS to filter
the entire workspace, inspect available project information and export
individual project records.
</div>
""", unsafe_allow_html=True)


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
# WORKSPACE TABS
# ============================================================

tab_map, tab_register, tab_details, tab_analytics, tab_method, tab_grid = st.tabs([
    "Location explorer",
    "Project register",
    "Project details",
    "Technology analytics",
    "Data & limitations",
    "Transmission grid",
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
        f"Current technology selection: {technology_choice}. "
        "Only records containing valid coordinates appear on the map."
    )

    map_data = filtered.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    map_data = map_data[
        map_data["latitude"].between(-90, 90)
        & map_data["longitude"].between(-180, 180)
    ]

    if map_data.empty:
        st.warning(
            "No usable coordinates are available for the selected records. "
            "Use the project register and detail view, or upload coordinates."
        )
    else:
        fig_map = px.scatter_map(
            map_data,
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
            map_style="open-street-map",
            zoom=3,
            height=620,
            labels={
                "technology_display": "Technology",
                "plant_code": "Plant code",
                "generator_id": "Generator ID",
                "nameplate_capacity_mw": "Capacity (MW)",
                "status": "Status",
            },
        )

        fig_map.update_layout(
            font=dict(family=FONT, size=13, color=BLACK),
            paper_bgcolor=BG,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(
                font=dict(family=FONT, size=12, color=BLACK),
                bgcolor="rgba(251,249,247,0.92)",
            ),
        )

        st.plotly_chart(fig_map, use_container_width=True)

    st.caption(
        "A generator coordinate does not establish parcel boundaries, "
        "buildable acreage or interconnection feasibility."
    )


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
        {"Feature": "Parcel ownership / valuation", "Status": "Not connected"},
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
# TRANSMISSION GRID EXPLORER (ADDED FEATURE)
# Upload the transmission Excel workbook and KMZ together.
# Existing asset views and logic above are retained.
# ============================================================

@st.cache_data(show_spinner=False, max_entries=2)
def parse_transmission_excel(excel_bytes):
    """Read and standardize transmission-line attributes from Excel."""
    df = pd.read_excel(io.BytesIO(excel_bytes), engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    aliases = {
        "line_id": [
            "Transmission Line Unique Identifier", "ID", "Line ID", "Unique Identifier"
        ],
        "object_id": ["Object ID", "OBJECTID"],
        "line_type": ["Line Type", "TYPE"],
        "status": ["Operational Status of Line", "Status", "STATUS"],
        "voltage_kv": ["Voltage (Kilovolts)", "Voltage", "VOLTAGE"],
        "voltage_class": ["Voltage Class", "VOLT_CLASS"],
        "owner": ["Transmission Line Ownership Entity", "Owner", "OWNER"],
        "origin_substation": ["Origin Substation Name", "SUB_1", "Origin Substation"],
        "destination_substation": ["Destination Substation Name", "SUB_2", "Destination Substation"],
        "source": ["Data Source Reference", "Source", "SOURCE"],
        "validation_method": ["Validation Method", "VAL_METHOD"],
        "shape_length": ["Shape Length", "Shape__Length", "Shape Length.1"],
    }
    lookup = {re.sub(r"[^a-z0-9]+", "", c.lower()): c for c in df.columns}
    for target, options in aliases.items():
        if target not in df.columns:
            for option in options:
                key = re.sub(r"[^a-z0-9]+", "", option.lower())
                if key in lookup:
                    df[target] = df[lookup[key]]
                    break
        if target not in df.columns:
            df[target] = "Unknown" if target != "voltage_kv" else pd.NA

    df["line_id"] = df["line_id"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    df["voltage_kv"] = pd.to_numeric(df["voltage_kv"], errors="coerce")
    # The source uses -999999 as an unavailable/placeholder voltage value.
    df.loc[df["voltage_kv"] <= 0, "voltage_kv"] = pd.NA
    for c in ["line_type", "status", "voltage_class", "owner", "origin_substation", "destination_substation"]:
        df[c] = df[c].fillna("Unknown").astype(str).str.strip()
    return df


def _desc_fields(description):
    """Extract key/value attributes from the HTML table embedded in KML."""
    text = html.unescape(description or "")
    pairs = re.findall(r"<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*([^<]*?)\s*</td>", text, flags=re.I)
    return {re.sub(r"\s+", "", k).upper(): v.strip() for k, v in pairs}


@st.cache_data(show_spinner=False, max_entries=2)
def parse_transmission_kmz(kmz_bytes, max_points_per_line=12):
    """Stream the KMZ KML and simplify line paths for browser performance."""
    lines = []
    nodes = []
    ns = "{http://www.opengis.net/kml/2.2}"
    with zipfile.ZipFile(io.BytesIO(kmz_bytes)) as archive:
        kml_names = [n for n in archive.namelist() if n.lower().endswith(".kml")]
        if not kml_names:
            raise ValueError("The KMZ does not contain a KML file.")
        with archive.open(kml_names[0]) as kml_stream:
            for _, placemark in ET.iterparse(kml_stream, events=("end",)):
                if placemark.tag != ns + "Placemark":
                    continue
                name_el = placemark.find(ns + "name")
                desc_el = placemark.find(ns + "description")
                attrs = _desc_fields(desc_el.text if desc_el is not None else "")
                line_id = attrs.get("ID") or (name_el.text.strip() if name_el is not None and name_el.text else "")
                object_id = attrs.get("OBJECTID", "")

                # A placemark can contain one or more LineString elements.
                paths = []
                for coord_el in placemark.iter(ns + "coordinates"):
                    raw = (coord_el.text or "").strip()
                    if not raw:
                        continue
                    coords = []
                    for token in raw.split():
                        parts = token.split(",")
                        if len(parts) >= 2:
                            try:
                                lon, lat = float(parts[0]), float(parts[1])
                                if -180 <= lon <= 180 and -90 <= lat <= 90:
                                    coords.append([lon, lat])
                            except (TypeError, ValueError):
                                pass
                    if len(coords) >= 2:
                        # Keep endpoints and evenly spaced intermediate vertices.
                        if len(coords) > max_points_per_line:
                            indexes = sorted(set(round(i * (len(coords) - 1) / (max_points_per_line - 1)) for i in range(max_points_per_line)))
                            coords = [coords[i] for i in indexes]
                        paths.append(coords)

                if paths:
                    # Most features contain one path. Preserve separate paths as separate records.
                    for path_no, path in enumerate(paths):
                        lines.append({
                            "line_id": str(line_id).strip(),
                            "object_id": str(object_id).strip(),
                            "path": path,
                        })
                        nodes.append({"line_id": str(line_id).strip(), "end": "Origin", "longitude": path[0][0], "latitude": path[0][1]})
                        nodes.append({"line_id": str(line_id).strip(), "end": "Destination", "longitude": path[-1][0], "latitude": path[-1][1]})
                placemark.clear()
    return pd.DataFrame(lines), pd.DataFrame(nodes)


def find_repository_file(extension, preferred_terms):
    """Find a data file committed alongside app.py, without a Streamlit uploader."""
    repo_dir = Path(__file__).resolve().parent
    candidates = [
        p for p in repo_dir.iterdir()
        if p.is_file() and p.suffix.lower() == extension.lower()
        and not p.name.startswith(".")
    ]
    if not candidates:
        return None
    # Prefer files whose names match transmission/grid keywords.
    def score(path):
        name = path.name.lower()
        return sum(1 for term in preferred_terms if term in name), path.stat().st_size
    candidates.sort(key=score, reverse=True)
    return candidates[0]




def is_valid_kmz(path):
    """Return True only when the file is a readable ZIP archive containing KML."""
    try:
        if path is None or not Path(path).is_file() or Path(path).stat().st_size < 4:
            return False
        if not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path, "r") as archive:
            return any(name.lower().endswith(".kml") for name in archive.namelist())
    except (OSError, zipfile.BadZipFile):
        return False


def download_release_kmz(url, destination):
    """Download and validate a real KMZ, rejecting HTML pages and LFS pointers."""
    response = requests.get(
        url,
        headers={"User-Agent": "SunstripeLocationIntelligence/1.0", "Accept": "application/octet-stream"},
        timeout=(20, 300),
        allow_redirects=True,
    )
    response.raise_for_status()
    content = response.content
    if len(content) < 4 or not zipfile.is_zipfile(io.BytesIO(content)):
        preview = content[:160].decode("utf-8", errors="replace").replace("\n", " ")
        if content.startswith(b"version https://git-lfs.github.com/spec/v1"):
            reason = "GitHub returned a Git LFS pointer, not the file content."
        elif b"<html" in content[:500].lower() or b"<!doctype html" in content[:500].lower():
            reason = "GitHub returned an HTML page instead of the KMZ asset."
        else:
            reason = f"The downloaded content is not a ZIP/KMZ archive. Response preview: {preview[:120]}"
        raise ValueError(reason)
    with zipfile.ZipFile(io.BytesIO(content), "r") as archive:
        if not any(name.lower().endswith(".kml") for name in archive.namelist()):
            raise ValueError("The downloaded ZIP does not contain a .kml file, so it is not a usable KMZ.")
    Path(destination).write_bytes(content)
    return Path(destination)


@st.cache_data(show_spinner=False, max_entries=2)
def parse_transmission_excel_file(file_path, file_mtime, file_size):
    """Load transmission attributes from a workbook committed to the repository."""
    del file_mtime, file_size  # Included in the cache key so file updates invalidate it.
    df = pd.read_excel(file_path, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    aliases = {
        "line_id": ["Transmission Line Unique Identifier", "ID", "Line ID", "Unique Identifier"],
        "object_id": ["Object ID", "OBJECTID"],
        "line_type": ["Line Type", "TYPE"],
        "status": ["Operational Status of Line", "Status", "STATUS"],
        "voltage_kv": ["Voltage (Kilovolts)", "Voltage", "VOLTAGE"],
        "voltage_class": ["Voltage Class", "VOLT_CLASS"],
        "owner": ["Transmission Line Ownership Entity", "Owner", "OWNER"],
        "origin_substation": ["Origin Substation Name", "SUB_1", "Origin Substation"],
        "destination_substation": ["Destination Substation Name", "SUB_2", "Destination Substation"],
        "source": ["Data Source Reference", "Source", "SOURCE"],
        "validation_method": ["Validation Method", "VAL_METHOD"],
        "shape_length": ["Shape Length", "Shape__Length", "Shape Length.1"],
    }
    lookup = {re.sub(r"[^a-z0-9]+", "", c.lower()): c for c in df.columns}
    for target, options in aliases.items():
        if target not in df.columns:
            for option in options:
                key = re.sub(r"[^a-z0-9]+", "", option.lower())
                if key in lookup:
                    df[target] = df[lookup[key]]
                    break
        if target not in df.columns:
            df[target] = pd.NA if target == "voltage_kv" else "Unknown"

    df["line_id"] = df["line_id"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    df["voltage_kv"] = pd.to_numeric(df["voltage_kv"], errors="coerce")
    df.loc[df["voltage_kv"] <= 0, "voltage_kv"] = pd.NA
    for c in ["line_type", "status", "voltage_class", "owner", "origin_substation", "destination_substation"]:
        df[c] = df[c].fillna("Unknown").astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False, max_entries=2)
def parse_transmission_kmz_file(file_path, file_mtime, file_size, max_points_per_line=12):
    """Read KML paths from a KMZ committed to the repository."""
    del file_mtime, file_size  # Included in the cache key so file updates invalidate it.
    lines = []
    nodes = []
    ns = "{http://www.opengis.net/kml/2.2}"
    with zipfile.ZipFile(file_path) as archive:
        kml_names = [n for n in archive.namelist() if n.lower().endswith(".kml")]
        if not kml_names:
            raise ValueError("The KMZ does not contain a KML file.")
        with archive.open(kml_names[0]) as kml_stream:
            for _, placemark in ET.iterparse(kml_stream, events=("end",)):
                if placemark.tag != ns + "Placemark":
                    continue
                name_el = placemark.find(ns + "name")
                desc_el = placemark.find(ns + "description")
                attrs = _desc_fields(desc_el.text if desc_el is not None else "")
                line_id = attrs.get("ID") or (name_el.text.strip() if name_el is not None and name_el.text else "")
                object_id = attrs.get("OBJECTID", "")
                paths = []
                for coord_el in placemark.iter(ns + "coordinates"):
                    raw = (coord_el.text or "").strip()
                    if not raw:
                        continue
                    coords = []
                    for token in raw.split():
                        parts = token.split(",")
                        if len(parts) >= 2:
                            try:
                                lon, lat = float(parts[0]), float(parts[1])
                                if -180 <= lon <= 180 and -90 <= lat <= 90:
                                    coords.append([lon, lat])
                            except (TypeError, ValueError):
                                pass
                    if len(coords) >= 2:
                        if len(coords) > max_points_per_line:
                            indexes = sorted(set(round(i * (len(coords) - 1) / (max_points_per_line - 1)) for i in range(max_points_per_line)))
                            coords = [coords[i] for i in indexes]
                        paths.append(coords)
                for path in paths:
                    lines.append({"line_id": str(line_id).strip(), "object_id": str(object_id).strip(), "path": path})
                    nodes.append({"line_id": str(line_id).strip(), "end": "Origin", "longitude": path[0][0], "latitude": path[0][1]})
                    nodes.append({"line_id": str(line_id).strip(), "end": "Destination", "longitude": path[-1][0], "latitude": path[-1][1]})
                placemark.clear()
    return pd.DataFrame(lines), pd.DataFrame(nodes)


with tab_grid:
    st.markdown('<div class="section-title">US transmission line explorer</div>', unsafe_allow_html=True)
    st.write(
        "The transmission network is loaded automatically from files committed to your GitHub repository. "
        "No file upload inside Streamlit is required. The Excel supplies line attributes and substation names; "
        "the KMZ supplies the geographic line paths."
    )

    excel_path = find_repository_file(".xlsx", ["transmission", "line", "grid"])
    kmz_path = find_repository_file(".kmz", ["transmission", "line", "grid"])

    # A Git LFS pointer or HTML download can have a .kmz extension but is not
    # a usable archive. Validate the local file before attempting to parse it.
    if not is_valid_kmz(kmz_path):
        transmission_release_url = (
            "https://github.com/kartikv-hash/Location-Intelligence-/releases/"
            "download/transmission-v1/"
            "US_Electric_Power_Transmission_Lines_-5914890627387387697.kmz"
        )
        try:
            with st.spinner("Validating transmission KMZ and checking the GitHub Release asset..."):
                downloaded_kmz = Path("/tmp/US_Electric_Power_Transmission_Lines_-5914890627387387697.kmz")
                kmz_path = download_release_kmz(transmission_release_url, downloaded_kmz)
        except Exception as download_error:
            st.error("The KMZ file was found, but it is not a valid KMZ archive, and the GitHub Release download did not return the real file.")
            st.code(str(download_error))
            st.markdown(
                "**Fix:** Open the repository's **Releases** page and confirm that tag `transmission-v1` has the actual KMZ attached as a release asset. "
                "Do not attach a Git LFS pointer or a GitHub webpage. If the KMZ is stored with Git LFS, configure Streamlit to retrieve the actual LFS content."
            )
            kmz_path = None

    if excel_path is None or kmz_path is None:
        st.error("Transmission files were not found next to app.py in the GitHub repository.")
        st.markdown(
            "**Upload both files to the same repository folder as `app.py`:**  "
            "one `.xlsx` workbook and one `.kmz` file. Then commit the changes and let Streamlit redeploy."
        )
        st.caption("The app automatically selects the Excel and KMZ whose filenames contain transmission, line or grid, where possible.")
    else:
        st.caption(f"Excel source: `{excel_path.name}` · KMZ source: `{kmz_path.name}`")
        st.info(
            "The KMZ is large, so the first load may take several minutes. Parsed results are cached; "
            "subsequent filter changes should not re-parse the files."
        )
        try:
            with st.spinner("Loading repository Excel and parsing KMZ geometry. This may take a few minutes..."):
                excel_stat = excel_path.stat()
                kmz_stat = kmz_path.stat()
                grid_attributes = parse_transmission_excel_file(
                    str(excel_path), excel_stat.st_mtime, excel_stat.st_size
                )
                grid_lines, grid_nodes = parse_transmission_kmz_file(
                    str(kmz_path), kmz_stat.st_mtime, kmz_stat.st_size
                )

                grid_lines["line_id"] = grid_lines["line_id"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
                grid_attributes["line_id"] = grid_attributes["line_id"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
                join_cols = [
                    "line_id", "line_type", "status", "voltage_kv", "voltage_class", "owner",
                    "origin_substation", "destination_substation", "source", "validation_method"
                ]
                attributes_for_join = grid_attributes[[c for c in join_cols if c in grid_attributes.columns]].drop_duplicates("line_id")
                joined = grid_lines.merge(attributes_for_join, on="line_id", how="left")

                node_attributes = attributes_for_join[[
                    c for c in ["line_id", "origin_substation", "destination_substation"]
                    if c in attributes_for_join.columns
                ]].drop_duplicates("line_id")
                node_df = grid_nodes.merge(node_attributes, on="line_id", how="left")
                node_df["node_name"] = node_df.get("origin_substation", "Unknown")
                destination_mask = node_df["end"].eq("Destination")
                if "destination_substation" in node_df.columns:
                    node_df.loc[destination_mask, "node_name"] = node_df.loc[destination_mask, "destination_substation"]
                node_df["node_name"] = node_df["node_name"].fillna("Unknown").astype(str)

            st.success(f"Loaded {len(joined):,} transmission-line geometry records from the repository KMZ.")

            matched_lines = joined["voltage_kv"].notna().sum() if "voltage_kv" in joined else 0
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Line geometry records", f"{len(joined):,}")
            g2.metric("Matched voltage records", f"{matched_lines:,}")
            g3.metric("Reported line owners", f"{joined['owner'].replace('Unknown', pd.NA).nunique(dropna=True):,}" if "owner" in joined else "N/A")
            g4.metric("Endpoint node records", f"{len(node_df):,}")

            with st.expander("Filter the transmission network", expanded=True):
                voltage_options = sorted(joined["voltage_class"].dropna().astype(str).unique()) if "voltage_class" in joined else []
                chosen_voltage = st.multiselect("Voltage class", voltage_options, default=voltage_options, key="grid_voltage_filter")
                status_options = sorted(joined["status"].dropna().astype(str).unique()) if "status" in joined else []
                chosen_line_status = st.multiselect("Operational status", status_options, default=status_options, key="grid_status_filter")
                owner_search = st.text_input("Filter by owner (optional)", key="grid_owner_filter", placeholder="Enter part of a utility / owner name")
                show_nodes = st.checkbox("Show connected endpoint nodes / reported substations (may increase map load size)", value=False, key="grid_show_nodes")

            grid_filtered = joined.copy()
            if chosen_voltage and "voltage_class" in grid_filtered:
                grid_filtered = grid_filtered[grid_filtered["voltage_class"].astype(str).isin(chosen_voltage)]
            if chosen_line_status and "status" in grid_filtered:
                grid_filtered = grid_filtered[grid_filtered["status"].astype(str).isin(chosen_line_status)]
            if owner_search.strip() and "owner" in grid_filtered:
                grid_filtered = grid_filtered[grid_filtered["owner"].astype(str).str.contains(owner_search.strip(), case=False, na=False, regex=False)]

            visible_ids = set(grid_filtered["line_id"].astype(str))
            node_filtered = node_df[node_df["line_id"].astype(str).isin(visible_ids)].copy()
            if not node_filtered.empty:
                node_filtered["_lon"] = node_filtered["longitude"].round(3)
                node_filtered["_lat"] = node_filtered["latitude"].round(3)
                node_filtered = node_filtered.drop_duplicates(subset=["node_name", "_lon", "_lat"])

            st.caption(
                f"Showing {len(grid_filtered):,} transmission-line paths after filters. "
                "Endpoint nodes are located from line geometry and labelled with reported substation names from Excel."
            )

            if grid_filtered.empty:
                st.warning("No transmission lines match these filters.")
            else:
                # IMPORTANT: send only the fields needed for map rendering to the
                # browser. Sending the entire joined dataframe (94k paths plus all
                # Excel attributes) can exceed Streamlit's 200 MB message limit.
                map_columns = [
                    "path", "line_id", "owner", "voltage_kv", "voltage_class",
                    "status", "origin_substation", "destination_substation",
                ]
                map_columns = [c for c in map_columns if c in grid_filtered.columns]
                map_data = grid_filtered[map_columns].copy()
                map_data["path"] = map_data["path"].apply(
                    lambda path: path if isinstance(path, list) else []
                )

                line_layer = pdk.Layer(
                    "PathLayer",
                    data=map_data,
                    id="transmission_lines",
                    get_path="path",
                    get_color=[130, 70, 160, 190],
                    get_width=3,
                    width_min_pixels=2,
                    width_scale=1,
                    pickable=True,
                    auto_highlight=True,
                )
                layers = [line_layer]
                if show_nodes and not node_filtered.empty:
                    # Deduplicate nearby endpoints to avoid sending 189k markers
                    # to the browser. The full transmission-line geometry remains.
                    node_filtered = node_filtered.copy()
                    node_filtered["_lon_grid"] = node_filtered["longitude"].round(2)
                    node_filtered["_lat_grid"] = node_filtered["latitude"].round(2)
                    node_filtered = node_filtered.drop_duplicates(
                        subset=["_lon_grid", "_lat_grid"]
                    ).head(25000)
                    node_map_data = node_filtered[
                        ["longitude", "latitude", "node_name", "line_id", "end"]
                    ].copy()
                    node_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=node_map_data,
                        get_position="[longitude, latitude]",
                        get_radius=500,
                        radius_min_pixels=2,
                        radius_max_pixels=6,
                        get_fill_color=[5, 7, 20, 210],
                        get_line_color=[255, 255, 255, 220],
                        line_width_min_pixels=1,
                        pickable=True,
                    )
                    layers.append(node_layer)

                view_state = pdk.ViewState(latitude=39.5, longitude=-98.35, zoom=3, pitch=0)
                tooltip = {
                    "html": "<b>Line ID:</b> {line_id}<br/><b>Owner:</b> {owner}<br/><b>Voltage:</b> {voltage_kv} kV<br/><b>Class:</b> {voltage_class}<br/><b>Status:</b> {status}<br/><b>Origin:</b> {origin_substation}<br/><b>Destination:</b> {destination_substation}",
                    "style": {"backgroundColor": "#050714", "color": "white"},
                }
                # Click a line to select it. Streamlit returns the selected
                # feature's properties, which we display below the map.
                try:
                    map_event = st.pydeck_chart(
                        pdk.Deck(
                            layers=layers,
                            initial_view_state=view_state,
                            tooltip=tooltip,
                            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                        ),
                        height=620,
                        use_container_width=True,
                        on_select="rerun",
                        selection_mode="single-object",
                        key="transmission_line_map",
                    )
                except TypeError:
                    # Older Streamlit versions don't support chart selection.
                    map_event = None
                    st.pydeck_chart(
                        pdk.Deck(
                            layers=layers,
                            initial_view_state=view_state,
                            tooltip=tooltip,
                            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                        ),
                        height=620,
                        use_container_width=True,
                    )
                    st.info(
                        "Hover over a transmission line to see its summary. "
                        "To click a line and open its details, update Streamlit "
                        "to version 1.40 or later in requirements.txt."
                    )

                # Extract selected features from Streamlit's PyDeck selection event.
                # Streamlit versions differ slightly in the shape of this payload.
                selected_feature = None
                if map_event is not None:
                    try:
                        selection = (
                            map_event.get("selection", {})
                            if isinstance(map_event, dict)
                            else getattr(map_event, "selection", {})
                        )
                        objects = (
                            selection.get("objects", {})
                            if isinstance(selection, dict)
                            else getattr(selection, "objects", {})
                        )
                        if isinstance(objects, dict):
                            for layer_objects in objects.values():
                                if layer_objects:
                                    selected_feature = layer_objects[0]
                                    break
                    except Exception:
                        selected_feature = None

                if selected_feature is not None and not isinstance(selected_feature, dict):
                    try:
                        selected_feature = dict(selected_feature)
                    except Exception:
                        selected_feature = {}

                selected_line_id = ""
                if isinstance(selected_feature, dict):
                    selected_line_id = str(selected_feature.get("line_id", "")).strip()

                # Reliable fallback: users can paste a line ID from a map click,
                # tooltip, or the records table if click-selection isn't supported
                # by the deployed Streamlit version/browser.
                with st.expander("Find a line by ID", expanded=not bool(selected_line_id)):
                    lookup_id = st.text_input(
                        "Transmission line ID",
                        value=selected_line_id,
                        placeholder="Enter or paste a line ID",
                        key="grid_lookup_line_id",
                    ).strip()
                    lookup_clicked = st.button(
                        "Show line information",
                        key="grid_lookup_line_button",
                    )
                    if lookup_clicked and lookup_id:
                        selected_line_id = lookup_id

                selected_rows = (
                    grid_filtered[
                        grid_filtered["line_id"].astype(str).str.strip() == selected_line_id
                    ]
                    if selected_line_id else pd.DataFrame()
                )

                if not selected_rows.empty:
                    selected_row = selected_rows.iloc[0]
                    st.markdown("### Selected transmission line")
                    d1, d2, d3 = st.columns(3)
                    d1.metric("Line ID", str(selected_row.get("line_id", "Unknown")))
                    voltage_value = selected_row.get("voltage_kv", pd.NA)
                    d2.metric(
                        "Voltage",
                        f"{float(voltage_value):,.0f} kV"
                        if pd.notna(voltage_value) else "Not reported",
                    )
                    d3.metric("Operational status", str(selected_row.get("status", "Not reported")))

                    details = {
                        "Line ID": selected_row.get("line_id", "Not reported"),
                        "Object ID": selected_row.get("object_id", "Not reported"),
                        "Line type": selected_row.get("line_type", "Not reported"),
                        "Voltage (kV)": selected_row.get("voltage_kv", "Not reported"),
                        "Voltage class": selected_row.get("voltage_class", "Not reported"),
                        "Operational status": selected_row.get("status", "Not reported"),
                        "Owner": selected_row.get("owner", "Not reported"),
                        "Origin substation": selected_row.get("origin_substation", "Not reported"),
                        "Destination substation": selected_row.get("destination_substation", "Not reported"),
                        "Source": selected_row.get("source", "Not reported"),
                        "Validation method": selected_row.get("validation_method", "Not reported"),
                        "Shape length": selected_row.get("shape_length", "Not reported"),
                    }
                    details_df = pd.DataFrame(
                        [{k: (v if pd.notna(v) else "Not reported") for k, v in details.items()}]
                    ).T.reset_index()
                    details_df.columns = ["Attribute", "Value"]
                    st.dataframe(details_df, hide_index=True, use_container_width=True)
                elif selected_line_id:
                    st.warning(
                        "No line with that ID was found in the currently filtered records. "
                        "Clear or adjust filters, or use an ID from the Transmission line records table."
                    )
                else:
                    st.info(
                        "Click a transmission line to inspect it. If clicking does not select a line "
                        "in your browser, open **Find a line by ID** and paste an ID from the records table. "
                        "Hovering over a line shows a quick summary."
                    )

                with st.expander("Transmission line records", expanded=False):
                    table_cols = [
                        "line_id", "line_type", "status", "voltage_kv", "voltage_class", "owner",
                        "origin_substation", "destination_substation", "source", "validation_method"
                    ]
                    table_cols = [c for c in table_cols if c in grid_filtered.columns]
                    st.dataframe(grid_filtered[table_cols].drop(columns=["path"], errors="ignore"), use_container_width=True, hide_index=True, height=350)
                    st.download_button(
                        "Download filtered transmission lines CSV",
                        data=grid_filtered.drop(columns=["path"], errors="ignore").to_csv(index=False).encode("utf-8"),
                        file_name="sunstripe_transmission_lines_filtered.csv",
                        mime="text/csv",
                        key="download_grid_lines",
                    )

                st.warning(
                    "Endpoint node positions are inferred from line geometry, not independently verified substation coordinates. "
                    "These records do not establish available interconnection capacity."
                )
        except Exception as exc:
            st.error("Could not load the transmission files from the repository.")
            st.exception(exc)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div class="footer">
SUNSTRIPE LOCATION INTELLIGENCE · SOLAR / STORAGE / WIND
</div>
""", unsafe_allow_html=True)
