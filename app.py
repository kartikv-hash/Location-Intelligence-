
import io
import json
import re
import zipfile
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    """Basic WKT LINESTRING parser for CSV uploads."""
    if not isinstance(value, str):
        return []
    text = value.strip()
    if not text.upper().startswith("LINESTRING"):
        return []
    body_start = text.find("(")
    body_end = text.rfind(")")
    if body_start < 0 or body_end <= body_start:
        return []

    points = []
    body = text[body_start + 1:body_end]
    for pair in body.split(","):
        numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", pair)
        if len(numbers) >= 2:
            # WKT GIS convention: x=longitude, y=latitude.
            points.append((float(numbers[0]), float(numbers[1])))
    return [points] if len(points) >= 2 else []


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


def load_transmission_lines(upload):
    """Return {voltage_label: [(lons, lats), ...]} and feature count."""
    if upload is None:
        return {}, 0

    check_upload_size(upload)
    filename = upload.name.lower()
    grouped = {}
    segment_count = 0

    def add_segment(coords, voltage_raw):
        nonlocal segment_count
        points = clean_coordinate_segment(coords)
        if not points:
            return
        label = normalize_voltage_kv(voltage_raw)
        grouped.setdefault(label, []).append(
            ([p[0] for p in points], [p[1] for p in points])
        )
        segment_count += 1

    def add_geojson_geometry(geometry, voltage_raw):
        for segment in iter_line_segments(geometry):
            add_segment(segment, voltage_raw)

    if filename.endswith((".geojson", ".json")):
        upload.seek(0)
        document = json.load(upload)

        if document.get("type") == "FeatureCollection":
            features = document.get("features", [])
        elif document.get("type") == "Feature":
            features = [document]
        else:
            features = [{"type": "Feature", "geometry": document, "properties": {}}]

        for feature in features:
            properties = feature.get("properties") or {}
            voltage_col = find_voltage_column(properties.keys())
            voltage_raw = properties.get(voltage_col) if voltage_col else None
            add_geojson_geometry(feature.get("geometry") or {}, voltage_raw)

    elif filename.endswith(".csv"):
        upload.seek(0)
        df = pd.read_csv(upload)
        normalized_columns = {column_key(c): c for c in df.columns}
        voltage_col = find_voltage_column(df.columns)
        geometry_col = next(
            (normalized_columns[k] for k in ["geometry", "geojson", "linegeometry", "coordinates", "wkt"] if k in normalized_columns),
            None,
        )

        endpoint_aliases = {
            "from_lon": ["fromlon", "fromlongitude", "startlon", "startlongitude", "lon1", "longitude1", "x1"],
            "from_lat": ["fromlat", "fromlatitude", "startlat", "startlatitude", "lat1", "latitude1", "y1"],
            "to_lon": ["tolon", "tolongitude", "endlon", "endlongitude", "lon2", "longitude2", "x2"],
            "to_lat": ["tolat", "tolatitude", "endlat", "endlatitude", "lat2", "latitude2", "y2"],
        }
        endpoint_cols = {}
        for standard, aliases in endpoint_aliases.items():
            endpoint_cols[standard] = next(
                (normalized_columns[a] for a in aliases if a in normalized_columns),
                None,
            )

        for _, row in df.iterrows():
            voltage_raw = row.get(voltage_col) if voltage_col else None
            handled = False

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
                            handled = True

                if isinstance(parsed, dict):
                    if parsed.get("type") == "Feature":
                        add_geojson_geometry(parsed.get("geometry") or {}, voltage_raw)
                    elif parsed.get("type") in {"LineString", "MultiLineString", "GeometryCollection"}:
                        add_geojson_geometry(parsed, voltage_raw)
                    elif isinstance(parsed.get("coordinates"), list):
                        # Geometry column may contain only a coordinate array.
                        coordinates = parsed["coordinates"]
                        if coordinates and isinstance(coordinates[0], (list, tuple)):
                            if coordinates[0] and isinstance(coordinates[0][0], (int, float)):
                                add_segment(coordinates, voltage_raw)
                            else:
                                for segment in coordinates:
                                    add_segment(segment, voltage_raw)
                    handled = True

                elif isinstance(parsed, list) and parsed:
                    if isinstance(parsed[0], (list, tuple)) and len(parsed[0]) >= 2 and isinstance(parsed[0][0], (int, float)):
                        add_segment(parsed, voltage_raw)
                    else:
                        for segment in parsed:
                            add_segment(segment, voltage_raw)
                    handled = True

            if not handled and all(endpoint_cols.values()):
                try:
                    coords = [
                        [float(row[endpoint_cols["from_lon"]]), float(row[endpoint_cols["from_lat"]])],
                        [float(row[endpoint_cols["to_lon"]]), float(row[endpoint_cols["to_lat"]])],
                    ]
                    add_segment(coords, voltage_raw)
                except (TypeError, ValueError, KeyError):
                    continue
    else:
        raise ValueError("Transmission grid upload must be GeoJSON, JSON or CSV.")

    if segment_count == 0:
        raise ValueError(
            "No valid transmission line geometries were found. Use GeoJSON with "
            "LineString/MultiLineString features, or CSV with a geometry/WKT field "
            "or from/to latitude and longitude columns. Include a voltage/voltage_kv "
            "property or column for voltage-based colors."
        )

    return grouped, segment_count


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
            go.Scattermap(
                lon=all_lon,
                lat=all_lat,
                mode="lines",
                line=dict(color=colors[label], width=2.5),
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

    st.divider()
    st.markdown("### Transmission grid")
    st.caption("Upload transmission lines to show voltage-colored linework on the map.")
    transmission_file = st.file_uploader(
        "Transmission lines (GeoJSON or CSV)",
        type=["geojson", "json", "csv"],
        key="transmission_grid_upload",
        help=(
            "Recommended: GeoJSON LineString/MultiLineString features with a "
            "voltage or voltage_kv property. CSV also supports WKT/GeoJSON geometry "
            "or from/to latitude-longitude columns."
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


# Load uploaded transmission lines independently from the asset data.
transmission_groups = {}
transmission_segment_count = 0
transmission_load_error = None

if transmission_file is not None:
    try:
        transmission_file.seek(0)
        transmission_groups, transmission_segment_count = load_transmission_lines(
            transmission_file
        )
    except Exception as exc:
        transmission_load_error = str(exc)
        st.sidebar.error(f"Transmission line upload: {exc}")


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

tab_map, tab_register, tab_details, tab_analytics, tab_method = st.tabs([
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

    line_traces, line_color_map = transmission_line_traces(transmission_groups)

    if map_data.empty and not line_traces:
        st.warning(
            "No usable asset coordinates or transmission lines are available. "
            "Upload an asset dataset with latitude/longitude and/or a transmission "
            "line GeoJSON/CSV in the sidebar."
        )
    else:
        if not map_data.empty:
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
        else:
            # Still show the transmission network even if assets lack coordinates.
            line_lats, line_lons = [], []
            for segments in transmission_groups.values():
                for lons, lats in segments:
                    line_lons.extend(lons)
                    line_lats.extend(lats)
            center_lat = sum(line_lats) / len(line_lats) if line_lats else 39.0
            center_lon = sum(line_lons) / len(line_lons) if line_lons else -98.0
            fig_map = go.Figure()
            fig_map.update_layout(
                map=dict(
                    style="open-street-map",
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=4,
                ),
                height=620,
            )

        # Draw each voltage group as its own line trace so it appears in Plotly's legend.
        for trace in line_traces:
            fig_map.add_trace(trace)

        fig_map.update_layout(
            font=dict(family=FONT, size=13, color=BLACK),
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(
                title=dict(text="Technology / transmission voltage"),
                font=dict(family=FONT, size=12, color=BLACK),
                bgcolor="rgba(251,249,247,0.94)",
                x=1.01,
                y=1,
                xanchor="left",
                yanchor="top",
            ),
        )

        st.plotly_chart(fig_map, use_container_width=True)

        if line_color_map:
            st.markdown(
                transmission_legend_html(line_color_map),
                unsafe_allow_html=True,
            )
            st.caption(
                f"Transmission network loaded: {transmission_segment_count:,} line segments. "
                "Line colors represent the voltage reported in the uploaded dataset."
            )
        elif transmission_file is None:
            st.info(
                "To display the transmission grid, upload a GeoJSON line dataset or a "
                "CSV with voltage plus line geometry / endpoint coordinates in the sidebar."
            )

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
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div class="footer">
SUNSTRIPE LOCATION INTELLIGENCE · SOLAR / STORAGE / WIND
</div>
""", unsafe_allow_html=True)
