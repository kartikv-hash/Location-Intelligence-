
import io
import re
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
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
# SUNSTRIPE BRAND THEME
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

/* Black typography on the main ivory background */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main small,
[data-testid="stAppViewContainer"] .main strong {
    color: #000000;
}

/* Brand header */
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

/* Editorial heading */
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
    font-style: normal !important;
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

/* KPIs */
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

/* Tabs */
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

/* Tables, captions, labels */
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
# DATA LOADING HELPERS
# ============================================================

def check_upload_size(upload):
    if upload is not None and upload.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"Please keep uploads below {MAX_UPLOAD_MB} MB.")


@st.cache_data
def load_repository_csv():
    return pd.read_csv("renewable_asset_register.csv")


def normalize_column_key(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def standardize_assets(df, source_name, source_url=""):
    """
    Preserve original columns while standardizing common project fields.
    """

    df = df.copy()
    df.columns = [
        str(c).strip().replace("\n", " ")
        for c in df.columns
    ]

    lookup = {}
    for col in df.columns:
        lookup.setdefault(normalize_column_key(col), col)

    aliases = {
        "plant_name": [
            "plant name", "plant_name", "project name",
            "facility name", "name",
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
            "technology", "technology type", "technology group",
            "technology_group", "energy type", "fuel type",
        ],
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

    for standard, candidates in aliases.items():
        if standard not in df.columns:
            for candidate in candidates:
                found = lookup.get(normalize_column_key(candidate))
                if found is not None:
                    df[standard] = df[found]
                    break

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
        "plant_name", "state", "county", "entity_name",
        "technology_group", "status",
    ]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    tech = df["technology_group"].fillna("").astype(str).str.lower()
    energy = df["energy_source_code"].fillna("").astype(str).str.lower()
    mover = df["prime_mover_code"].fillna("").astype(str).str.lower()

    # EIA classification plus common CSV labels.
    is_bess = (
        tech.str.contains(r"battery|storage|bess", regex=True)
        | mover.str.fullmatch("ba", na=False)
        | energy.str.fullmatch("mwh", na=False)
    )

    is_wind = (
        tech.str.contains("wind", na=False)
        | energy.str.fullmatch("wnd", na=False)
        | energy.str.fullmatch("wds", na=False)
    )

    is_solar = (
        tech.str.contains(r"solar|photovoltaic|concentrat", regex=True)
        | energy.str.fullmatch("sun", na=False)
        | mover.str.fullmatch("pv", na=False)
    )

    df["technology_display"] = "Other"
    df.loc[is_solar, "technology_display"] = "Solar"
    df.loc[is_wind, "technology_display"] = "Wind"
    df.loc[is_bess, "technology_display"] = "BESS"

    # Support pre-classified repository datasets.
    if "technology_display" in lookup.values():
        original_display = next(
            c for c in df.columns
            if normalize_column_key(c) == "technologydisplay"
        )
        mapped_display = df[original_display].astype(str).str.strip().str.title()
        df.loc[mapped_display.isin(["Solar", "Wind", "Bess"]), "technology_display"] = (
            mapped_display[mapped_display.isin(["Solar", "Wind", "Bess"])]
            .replace({"Bess": "BESS"})
        )

    df["source_dataset"] = source_name
    df["source_url"] = source_url or ""
    df = df.reset_index(drop=True)

    plant = df["plant_code"].fillna("").astype(str)
    generator = df["generator_id"].fillna("").astype(str)

    df["record_id"] = [
        f"{plant.iloc[i]}-{generator.iloc[i]}-{i}"
        for i in range(len(df))
    ]

    return df


def load_user_file(upload):
    check_upload_size(upload)
    name = upload.name.lower()

    if name.endswith(".csv"):
        raw = pd.read_csv(upload)
    elif name.endswith(".xlsx"):
        raw = pd.read_excel(upload, engine="openpyxl")
    elif name.endswith(".xls"):
        raw = pd.read_excel(upload, engine="xlrd")
    else:
        raise ValueError("Unsupported file type. Use CSV, XLS or XLSX.")

    return standardize_assets(raw, f"Uploaded: {upload.name}")


# ============================================================
# OPTIONAL EIA CONNECTOR
# This is NOT called unless selected by the user.
# ============================================================

@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def download_eia_inventory():
    headers = {
        "User-Agent": "Mozilla/5.0 SunstripeLocationIntelligence/1.0",
        "Accept": "*/*",
        "Referer": EIA_PAGE,
    }

    page = requests.get(EIA_PAGE, headers=headers, timeout=20)
    page.raise_for_status()

    # EIA links can point to legacy XLS or modern XLSX workbooks.
    hrefs = re.findall(
        r"""href\s*=\s*["']([^"']+\.(?:xlsx|xls)(?:\?[^"']*)?)["']""",
        page.text,
        flags=re.IGNORECASE,
    )

    candidates = []
    for href in hrefs:
        url = urljoin(EIA_PAGE, href)
        if "generator" in url.lower() and url not in candidates:
            candidates.append(url)

    if not candidates:
        raise RuntimeError(
            "No generator Excel links were found on the EIA page."
        )

    errors = []

    for url in candidates[:6]:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=40,
            )
            response.raise_for_status()
            content = response.content

            if not content:
                raise ValueError("Empty download.")

            # Try format detection and actual workbook parsing.
            engines = []
            if content.startswith(b"PK"):
                engines.append("openpyxl")
            elif content.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
                engines.append("xlrd")
            else:
                # Some servers return a workbook with unexpected headers.
                engines = ["xlrd", "openpyxl"]

            last_error = None

            for engine in engines:
                try:
                    pd.ExcelFile(io.BytesIO(content), engine=engine)
                    return content, url, engine
                except Exception as exc:
                    last_error = exc

            raise ValueError(
                f"Download is not a readable Excel workbook. "
                f"Content-Type={response.headers.get('Content-Type')}; "
                f"parser error={last_error}"
            )

        except Exception as exc:
            errors.append(f"{url}: {type(exc).__name__}: {exc}")

    raise RuntimeError(
        "Could not download and parse the recent EIA workbooks.\n"
        + "\n".join(errors)
    )


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def load_eia_assets():
    content, workbook_url, engine = download_eia_inventory()

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

        header_row = None

        for i in range(min(40, len(raw))):
            values = [
                normalize_column_key(v)
                for v in raw.iloc[i].tolist()
                if pd.notna(v)
            ]

            has_plant = any("plantname" in v for v in values)
            has_generator = any("generatorid" in v for v in values)
            has_technology = any("technology" in v for v in values)
            has_capacity = any("capacity" in v for v in values)

            if has_plant and (
                has_generator or has_technology or has_capacity
            ):
                header_row = i
                break

        if header_row is None:
            continue

        headers = [
            str(v).strip() if pd.notna(v) else f"unnamed_{j}"
            for j, v in enumerate(raw.iloc[header_row].tolist())
        ]

        df = raw.iloc[header_row + 1:].copy()
        df.columns = headers
        df = df.dropna(how="all")
        df = df[
            [
                c for c in df.columns
                if not str(c).lower().startswith("unnamed")
            ]
        ]

        if not df.empty:
            df["EIA Workbook Sheet"] = sheet
            frames.append(df)

    if not frames:
        raise RuntimeError(
            "EIA workbook was downloaded but no recognizable generator "
            "table was found."
        )

    raw = pd.concat(frames, ignore_index=True, sort=False)

    normalized = standardize_assets(
        raw,
        "EIA-860M monthly inventory",
        workbook_url,
    )

    normalized = normalized[
        normalized["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()

    if normalized.empty:
        raise RuntimeError(
            "No Solar, Wind or BESS records could be identified in the EIA file."
        )

    return normalized, workbook_url


# ============================================================
# BRAND HEADER
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
Explore US renewable energy projects. Select Solar, Wind or BESS to filter
the map, project register, analytics and complete source-record view.
</div>
""", unsafe_allow_html=True)


# ============================================================
# DATA SOURCE CONTROLS
# CSV IS THE DEFAULT TO PREVENT STARTUP DELAYS.
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
        help=(
            "Repository CSV loads renewable_asset_register.csv. "
            "EIA live inventory makes an external request only when selected."
        ),
    )

    uploaded_file = None

    if data_mode == "Upload a file":
        uploaded_file = st.file_uploader(
            "Upload CSV, XLS or XLSX",
            type=["csv", "xls", "xlsx"],
        )

try:
    if data_mode == "Repository CSV":
        assets = load_repository_csv()
        source_label = "Repository CSV: renewable_asset_register.csv"
        source_url = ""

    elif data_mode == "Upload a file":
        if uploaded_file is None:
            st.info("Upload your project dataset in the sidebar.")
            st.stop()

        assets = load_user_file(uploaded_file)
        source_label = f"User upload: {uploaded_file.name}"
        source_url = ""

    else:
        with st.spinner(
            "EIA was selected. Downloading and validating the workbook..."
        ):
            assets, source_url = load_eia_assets()

        source_label = "EIA-860M monthly generator inventory"

except FileNotFoundError:
    st.error(
        "renewable_asset_register.csv was not found in the repository root. "
        "Add the CSV to GitHub or select Upload a file in the sidebar."
    )
    st.stop()

except Exception as exc:
    st.error(f"Could not load the selected dataset: {exc}")

    st.markdown(f"[Open official EIA data page]({EIA_PAGE})")

    st.info(
        "Choose Repository CSV or Upload a file from the sidebar to continue "
        "without the EIA download."
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
# FILTERS
# ============================================================

with st.sidebar:
    st.divider()
    st.markdown("### Asset filters")

    states = sorted(
        working["state"].fillna("Unknown").astype(str).unique().tolist()
    )

    selected_states = st.multiselect(
        "State",
        states,
        default=[],
        help="Leave empty to include all states.",
    )

    statuses = sorted(
        working["status"].fillna("Unknown").astype(str).unique().tolist()
    )

    selected_statuses = st.multiselect(
        "Project / generator status",
        statuses,
        default=statuses,
    )

    working["nameplate_capacity_mw"] = pd.to_numeric(
        working["nameplate_capacity_mw"], errors="coerce"
    )

    max_mw = working["nameplate_capacity_mw"].max()
    max_mw = max(1.0, float(max_mw)) if pd.notna(max_mw) else 1.0

    capacity_range = st.slider(
        "Capacity range (MW)",
        min_value=0.0,
        max_value=max_mw,
        value=(0.0, max_mw),
    )


filtered = working[
    working["status"].fillna("Unknown").astype(str).isin(selected_statuses)
].copy()

if selected_states:
    filtered = filtered[
        filtered["state"].fillna("Unknown").astype(str).isin(selected_states)
    ].copy()

filtered = filtered[
    pd.to_numeric(
        filtered["nameplate_capacity_mw"], errors="coerce"
    ).between(*capacity_range)
].copy()


# ============================================================
# KPI OVERVIEW
# ============================================================

record_count = len(filtered)

capacity_total = pd.to_numeric(
    filtered["nameplate_capacity_mw"], errors="coerce"
).sum()

plant_count = (
    filtered["plant_code"].nunique()
    if "plant_code" in filtered else record_count
)

state_count = filtered["state"].nunique()
technology_counts = filtered["technology_display"].value_counts()

solar_count = int(technology_counts.get("Solar", 0))
wind_count = int(technology_counts.get("Wind", 0))
bess_count = int(technology_counts.get("BESS", 0))

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{record_count:,}</div>'
        '<div class="kpi-label">Generator records in view</div></div>',
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{capacity_total:,.1f} MW</div>'
        '<div class="kpi-label">Represented capacity</div></div>',
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{plant_count:,}</div>'
        '<div class="kpi-label">Distinct plant codes</div></div>',
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">{state_count:,}</div>'
        '<div class="kpi-label">States represented</div></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="pill-row">'
    f'<span class="pill">Solar · {solar_count:,}</span>'
    f'<span class="pill">Wind · {wind_count:,}</span>'
    f'<span class="pill">BESS · {bess_count:,}</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.caption(f"Data source: {source_label}")

if source_url:
    st.markdown(f"[Open selected EIA workbook]({source_url})")

if data_mode == "EIA live inventory":
    st.info(
        "EIA monthly inventory values are preliminary and may be revised."
    )


# ============================================================
# UNIVERSAL PLOTLY STYLE
# ============================================================

def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT, size=13, color=BLACK),
        title=dict(
            font=dict(family=FONT, size=16, color=BLACK),
            x=0,
        ),
        legend=dict(
            font=dict(family=FONT, size=12, color=BLACK),
            bgcolor="rgba(251,249,247,0)",
            title=dict(font=dict(family=FONT, size=12, color=BLACK)),
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
        tickfont=dict(family=FONT, size=12, color=BLACK),
        title_font=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        tickfont=dict(family=FONT, size=12, color=BLACK),
        title_font=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showgrid=True,
        gridcolor=LINE,
        zeroline=False,
    )

    return fig


# ============================================================
# MAIN WORKSPACE
# ============================================================

tab_map, tab_register, tab_detail, tab_analytics, tab_method = st.tabs([
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
        f"Current selection: {technology_choice}. "
        "Only rows with valid coordinates appear on the map."
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
            "No usable coordinates are available in the selected data. "
            "The register and project details are still available."
        )
    else:
        fig = px.scatter_map(
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

        fig.update_layout(
            font=dict(family=FONT, size=13, color=BLACK),
            paper_bgcolor=BG,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(
                font=dict(family=FONT, size=12, color=BLACK),
                bgcolor="rgba(251,249,247,0.92)",
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "A generator location is not a parcel boundary and does not establish "
        "available acreage or interconnection feasibility."
    )


# ============================================================
# PROJECT REGISTER
# ============================================================

with tab_register:
    st.markdown(
        '<div class="section-title">Project and generator register</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search project records",
        placeholder="Plant name, owner, state, county or generator ID",
    )

    search_cols = [
        "plant_name", "state", "county", "entity_name",
        "technology_group", "generator_id", "plant_code",
        "status", "energy_source_code", "prime_mover_code",
    ]
    search_cols = [c for c in search_cols if c in filtered.columns]

    results = filtered.copy()

    if search.strip():
        matches = results[search_cols].apply(
            lambda col: col.astype(str).str.contains(
                search.strip(), case=False, na=False, regex=False
            )
        ).any(axis=1)

        results = results[matches].copy()

    display_cols = [
        "plant_name", "technology_display", "entity_name",
        "state", "county", "plant_code", "generator_id",
        "nameplate_capacity_mw", "net_summer_capacity_mw",
        "energy_capacity_mwh", "status", "operating_year",
        "planned_operating_year",
    ]
    display_cols = [c for c in display_cols if c in results.columns]

    st.dataframe(
        results[display_cols],
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    st.caption(f"{len(results):,} records displayed.")

    st.download_button(
        "Download filtered project records",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="sunstripe_filtered_projects.csv",
        mime="text/csv",
    )


# ============================================================
# PROJECT DETAILS
# ============================================================

with tab_detail:
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

        label = st.selectbox(
            "Select a project / generator",
            options["_display"].tolist(),
        )

        record_id = label_to_id[label]

        project = filtered[
            filtered["record_id"] == record_id
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

        st.markdown(
            '<div class="section-title">Project summary</div>',
            unsafe_allow_html=True,
        )

        important_fields = [
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
            ("Reported status", "status"),
            ("State", "state"),
            ("County", "county"),
            ("Latitude", "latitude"),
            ("Longitude", "longitude"),
            ("Operating year", "operating_year"),
            ("Operating month", "operating_month"),
            ("Planned operating year", "planned_operating_year"),
            ("Planned operating month", "planned_operating_month"),
            ("Data source", "source_dataset"),
        ]

        detail_rows = []

        for field_label, field_name in important_fields:
            value = project.get(field_name, None)

            if value is None or pd.isna(value) or str(value).strip() == "":
                value = "Not reported in this record"
            elif field_name in ["latitude", "longitude"]:
                value = f"{float(value):.6f}"
            elif field_name in [
                "nameplate_capacity_mw",
                "net_summer_capacity_mw",
                "energy_capacity_mwh",
            ]:
                value = f"{float(value):,.2f}"

            detail_rows.append({
                "Information": field_label,
                "Value": str(value),
            })

        st.dataframe(
            pd.DataFrame(detail_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            '<div class="section-title">Every available source field</div>',
            unsafe_allow_html=True,
        )

        raw_record = project.drop(labels=["_display"], errors="ignore")

        raw_details = pd.DataFrame({
            "Field": raw_record.index.astype(str),
            "Value": [
                "Not reported" if pd.isna(v) else str(v)
                for v in raw_record.values
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
            file_name=f"sunstripe_project_{record_id}.csv",
            mime="text/csv",
        )

        record_source = project.get("source_url", "")

        if isinstance(record_source, str) and record_source.startswith("https://"):
            st.markdown(f"[Open source workbook]({record_source})")
        elif data_mode == "EIA live inventory":
            st.markdown(f"[Open official EIA data page]({EIA_PAGE})")

        st.warning(
            "This view shows data available in the source record. It does not "
            "guarantee parcel boundaries, land ownership, project permits, "
            "interconnection results, storage duration, revenue or project economics."
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
        st.info("No data available for analysis.")
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
                "nameplate_capacity_mw": "Capacity (MW)",
            },
        )

        fig.update_traces(
            marker_color=RED,
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(family=FONT, size=11, color=BLACK),
            cliponaxis=False,
        )

        st.plotly_chart(style_chart(fig), use_container_width=True)

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

        st.plotly_chart(style_chart(fig2), use_container_width=True)


# ============================================================
# SOURCES AND LIMITATIONS
# ============================================================

with tab_method:
    st.markdown(
        '<div class="section-title">Data sources and methodology</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
**Current dataset:** {source_label}

**Official EIA-860M inventory:**  
{EIA_PAGE}

EIA-860M provides preliminary generator-level records for existing and
proposed generation. Monthly values may be revised. Generator-level records
are not necessarily equivalent to individual development projects.
""")

    st.markdown("#### Additional authoritative source directories")

    sources = pd.DataFrame([
        {
            "Provider": "EIA",
            "Purpose": "Generator inventory",
            "URL": "https://www.eia.gov/electricity/data/eia860m/index.php",
        },
        {
            "Provider": "EIA annual inventory",
            "Purpose": "Annual generator detail",
            "URL": "https://www.eia.gov/electricity/data/eia860/",
        },
        {
            "Provider": "NREL",
            "Purpose": "Renewable resources",
            "URL": "https://developer.nrel.gov/",
        },
        {
            "Provider": "USGS",
            "Purpose": "Elevation and terrain",
            "URL": "https://www.usgs.gov/",
        },
        {
            "Provider": "FEMA",
            "Purpose": "Flood hazard information",
            "URL": "https://www.fema.gov/flood-maps",
        },
        {
            "Provider": "USFWS",
            "Purpose": "Wetlands and ecological screening",
            "URL": "https://www.fws.gov/",
        },
        {
            "Provider": "ERCOT",
            "Purpose": "Texas market and grid data",
            "URL": "https://www.ercot.com/",
        },
        {
            "Provider": "CAISO",
            "Purpose": "California market and grid data",
            "URL": "https://www.caiso.com/",
        },
        {
            "Provider": "MISO",
            "Purpose": "Regional market and grid data",
            "URL": "https://www.misoenergy.org/",
        },
        {
            "Provider": "PJM",
            "Purpose": "Regional market and interconnection data",
            "URL": "https://www.pjm.com/",
        },
    ])

    st.dataframe(
        sources,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn("Official source"),
        },
    )

    st.markdown(
        '<div class="section-title">Implementation status</div>',
        unsafe_allow_html=True,
    )

    status_df = pd.DataFrame([
        {"Feature": "Technology selection", "Status": "Implemented"},
        {"Feature": "Project register and search", "Status": "Implemented"},
        {"Feature": "Full source-record details", "Status": "Implemented"},
        {"Feature": "CSV/XLS/XLSX upload", "Status": "Implemented"},
        {"Feature": "Optional EIA workbook connector", "Status": "Implemented; depends on source availability"},
        {"Feature": "Map", "Status": "Requires coordinates"},
        {"Feature": "Parcel ownership and valuation", "Status": "Not connected"},
        {"Feature": "Verified interconnection capacity", "Status": "Not connected"},
        {"Feature": "Live market prices and revenues", "Status": "Not connected"},
    ])

    st.dataframe(
        status_df,
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
