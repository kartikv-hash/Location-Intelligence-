
import io
import re
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# SUNSTRIPE LOCATION INTELLIGENCE
# US Solar | Wind | Battery Energy Storage Systems
# ============================================================

st.set_page_config(
    page_title="Sunstripe Location Intelligence",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- BRAND SETTINGS --------------------

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
# SUNSTRIPE THEME
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

/* Main content text */
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

/* Editorial header */
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

/* Streamlit metrics */
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

/* Text, captions and tables */
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

.stApp input,
.stApp textarea {
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
# FILE VALIDATION
# ============================================================

def check_upload_size(upload):
    if upload is not None and upload.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(
            f"File exceeds the {MAX_UPLOAD_MB} MB upload limit."
        )


# ============================================================
# EIA MONTHLY INVENTORY CONNECTOR
# Supports genuine XLS and XLSX workbooks.
# Validates file signatures before parsing.
# ============================================================

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
        timeout=30,
    )
    page_response.raise_for_status()

    links = re.findall(
        r"""href\s*=\s*["']([^"']+\.(?:xlsx|xls)(?:\?[^"']*)?)["']""",
        page_response.text,
        flags=re.IGNORECASE,
    )

    workbook_links = []

    for link in links:
        url = urljoin(EIA_PAGE, link)
        lower_url = url.lower()

        if "generator" in lower_url and url not in workbook_links:
            workbook_links.append(url)

    if not workbook_links:
        raise RuntimeError(
            "Could not detect generator workbook links on the EIA page. "
            "Use the manual workbook or CSV upload option."
        )

    errors = []

    # The EIA page normally lists the latest report first.
    for workbook_url in workbook_links[:8]:
        try:
            response = requests.get(
                workbook_url,
                headers=headers,
                timeout=90,
            )
            response.raise_for_status()

            content = response.content

            if not content:
                raise ValueError("The response was empty.")

            # XLSX is ZIP-based; XLS has an OLE signature.
            if content.startswith(b"PK\x03\x04"):
                engine = "openpyxl"
            elif content.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
                engine = "xlrd"
            else:
                content_type = response.headers.get(
                    "Content-Type", "unknown"
                )
                preview = content[:100].decode(
                    "utf-8", errors="replace"
                ).replace("\n", " ")

                raise ValueError(
                    "Downloaded response is not a recognized Excel file. "
                    f"Content-Type: {content_type}; "
                    f"response starts with: {preview[:80]}"
                )

            # Test the workbook before returning it.
            pd.ExcelFile(
                io.BytesIO(content),
                engine=engine,
            )

            return content, workbook_url, engine

        except Exception as exc:
            errors.append(
                f"{workbook_url}: {type(exc).__name__}: {exc}"
            )

    raise RuntimeError(
        "Unable to retrieve and open a recent EIA workbook.\n\n"
        + "\n".join(errors)
    )


# ============================================================
# READ EIA WORKBOOK
# ============================================================

def read_eia_workbook(workbook_bytes, engine):
    excel = pd.ExcelFile(
        io.BytesIO(workbook_bytes),
        engine=engine,
    )

    frames = []

    for sheet in excel.sheet_names:
        raw = pd.read_excel(
            io.BytesIO(workbook_bytes),
            sheet_name=sheet,
            header=None,
            engine=engine,
        )

        if raw.empty:
            continue

        header_row = None

        for i in range(min(50, len(raw))):
            values = [
                re.sub(
                    r"\s+", " ", str(value)
                ).strip().lower()
                for value in raw.iloc[i].tolist()
                if pd.notna(value)
            ]

            has_plant = any("plant name" in v for v in values)
            has_generator = any("generator id" in v for v in values)
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
            str(value).strip() if pd.notna(value)
            else f"unnamed_{i}"
            for i, value in enumerate(raw.iloc[header_row].tolist())
        ]

        df = raw.iloc[header_row + 1:].copy()
        df.columns = headers
        df = df.dropna(how="all")

        df = df[
            [
                c for c in df.columns
                if not str(c).lower().startswith("unnamed")
            ]
        ].copy()

        if not df.empty:
            df["EIA Workbook Sheet"] = sheet
            frames.append(df)

    if not frames:
        raise RuntimeError(
            "The workbook opened but no recognizable generator tables "
            "were detected. EIA may have changed the workbook layout."
        )

    return pd.concat(frames, ignore_index=True, sort=False)


# ============================================================
# NORMALIZE EIA OR CSV FIELDS
# Original fields are retained in the project detail view.
# ============================================================

def standardize_assets(df, source_name, source_url=""):
    df = df.copy()

    def column_key(name):
        return re.sub(r"[^a-z0-9]+", "", str(name).lower())

    lookup = {}
    for column in df.columns:
        lookup.setdefault(column_key(column), column)

    def locate(candidates):
        for candidate in candidates:
            found = lookup.get(column_key(candidate))
            if found is not None:
                return found
        return None

    mappings = {
        "plant_name": [
            "Plant Name", "plant_name", "project_name",
            "facility_name", "name"
        ],
        "state": [
            "Plant State", "State", "Plant State Abbreviation", "state_name"
        ],
        "county": ["County", "Plant County", "county_name"],
        "plant_code": ["Plant Code", "Plant ID", "plant_id"],
        "generator_id": ["Generator ID", "Generator"],
        "entity_name": ["Entity Name", "Utility Name", "Operator", "Owner"],
        "entity_id": ["Entity ID", "Utility ID"],
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
        "status": [
            "Status", "Operating Status", "Lifecycle Status",
            "Lifecycle Group", "lifecycle_group", "project_status"
        ],
        "operating_year": ["Operating Year"],
        "operating_month": ["Operating Month"],
        "planned_operating_year": [
            "Planned Operating Year", "Planned Year"
        ],
        "planned_operating_month": [
            "Planned Operating Month", "Planned Month"
        ],
        "latitude": [
            "Plant Latitude", "Latitude", "plant_latitude"
        ],
        "longitude": [
            "Plant Longitude", "Longitude", "plant_longitude"
        ],
    }

    for standard, candidates in mappings.items():
        original = locate(candidates)
        if original is not None:
            df[standard] = df[original]

    defaults = {
        "plant_name": "Unnamed plant",
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
        "status": "Not reported",
        "operating_year": None,
        "operating_month": None,
        "planned_operating_year": None,
        "planned_operating_month": None,
        "latitude": None,
        "longitude": None,
    }

    for col, default in defaults.items():
        if col not in df:
            df[col] = default

    numeric_cols = [
        "nameplate_capacity_mw",
        "net_summer_capacity_mw",
        "latitude",
        "longitude",
        "operating_year",
        "operating_month",
        "planned_operating_year",
        "planned_operating_month",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    tech = df["technology_group"].fillna("").astype(str).str.lower()
    source = df["energy_source_code"].fillna("").astype(str).str.lower()
    mover = df["prime_mover_code"].fillna("").astype(str).str.lower()

    bess_mask = (
        tech.str.contains(r"battery|storage", regex=True)
        | mover.str.fullmatch("ba", na=False)
        | source.str.fullmatch("mwh", na=False)
    )

    wind_mask = (
        tech.str.contains("wind", na=False)
        | source.str.fullmatch("wnd", na=False)
        | source.str.fullmatch("wds", na=False)
    )

    solar_mask = (
        tech.str.contains(r"solar|photovoltaic|concentrat", regex=True)
        | source.str.fullmatch("sun", na=False)
        | mover.str.fullmatch("pv", na=False)
    )

    # Retain unknown classifications rather than incorrectly calling them Solar.
    df["technology_display"] = "Other"
    df.loc[solar_mask, "technology_display"] = "Solar"
    df.loc[wind_mask, "technology_display"] = "Wind"
    df.loc[bess_mask, "technology_display"] = "BESS"

    df["source_dataset"] = source_name
    df["source_url"] = source_url or ""

    df = df.reset_index(drop=True)

    plant_codes = df["plant_code"].fillna("").astype(str)
    generator_ids = df["generator_id"].fillna("").astype(str)

    df["record_id"] = [
        f"{plant_codes.iloc[i]}-{generator_ids.iloc[i]}-{i}"
        for i in range(len(df))
    ]

    return df


# ============================================================
# LOAD EIA DATASET
# ============================================================

@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def load_eia_assets():
    content, url, engine = download_eia_inventory()
    raw = read_eia_workbook(content, engine)

    assets = standardize_assets(
        raw,
        "EIA-860M monthly inventory",
        url,
    )

    assets = assets[
        assets["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()

    if assets.empty:
        raise RuntimeError(
            "No Solar, Wind or BESS records were recognized. "
            "Inspect the downloaded EIA workbook's column format."
        )

    return assets, url


# ============================================================
# LOAD USER CSV OR EXCEL
# ============================================================

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
        raise ValueError("Upload a CSV, XLS or XLSX file.")

    return standardize_assets(
        raw,
        "User-uploaded dataset",
        "",
    )


@st.cache_data
def load_repository_csv():
    raw = pd.read_csv("renewable_asset_register.csv")
    return standardize_assets(raw, "Repository CSV", "")


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
Explore US renewable assets by technology. Select Solar, Wind or BESS to
filter the entire workspace, inspect project-level fields, review reported
capacity and download detailed records.
</div>
""", unsafe_allow_html=True)


# ============================================================
# DATA SOURCE SELECTOR
# ============================================================

with st.sidebar:
    st.markdown("## Sunstripe")
    st.caption("LOCATION INTELLIGENCE PLATFORM")
    st.divider()

    source_mode = st.radio(
        "Project data source",
        [
            "EIA live inventory",
            "Upload a file",
            "Repository CSV",
        ],
        index=0,
    )

    upload = None

    if source_mode == "Upload a file":
        upload = st.file_uploader(
            "Project data file",
            type=["csv", "xls", "xlsx"],
            help="Upload a CSV or EIA-style Excel workbook.",
        )

try:
    if source_mode == "EIA live inventory":
        with st.spinner("Connecting to EIA and checking workbook format..."):
            all_assets, actual_source_url = load_eia_assets()

        source_label = "EIA-860M monthly generator inventory"
        source_warning = (
            "Monthly EIA values are preliminary and can be revised."
        )

    elif source_mode == "Upload a file":
        if upload is None:
            st.info("Upload a CSV, XLS or XLSX file in the sidebar.")
            st.stop()

        all_assets = load_user_file(upload)
        actual_source_url = ""
        source_label = f"Uploaded file: {upload.name}"
        source_warning = (
            "The platform displays the fields in the uploaded source."
        )

    else:
        all_assets = load_repository_csv()
        actual_source_url = ""
        source_label = "renewable_asset_register.csv"
        source_warning = (
            "The platform displays the fields in the repository CSV."
        )

except Exception as exc:
    st.error("The selected dataset could not be loaded.")
    st.code(f"{type(exc).__name__}: {exc}")

    st.markdown(
        f"[Open official EIA-860M inventory]({EIA_PAGE})"
    )

    st.info(
        "If the EIA download fails, select 'Upload a file' in the sidebar "
        "and upload the official workbook downloaded manually from the "
        "EIA page, or use your asset CSV."
    )
    st.stop()


# ============================================================
# TECHNOLOGY SELECTOR
# Selection drives KPIs, map, register, charts and detail view.
# ============================================================

st.markdown(
    '<div class="section-title">Technology selection</div>',
    unsafe_allow_html=True,
)

technology_choice = st.radio(
    "Filter all project information by technology",
    ["All technologies", "Solar", "Wind", "BESS"],
    horizontal=True,
    key="technology_choice",
)

if technology_choice == "All technologies":
    working_assets = all_assets[
        all_assets["technology_display"].isin(["Solar", "Wind", "BESS"])
    ].copy()
else:
    working_assets = all_assets[
        all_assets["technology_display"] == technology_choice
    ].copy()


# ============================================================
# FILTERS
# ============================================================

with st.sidebar:
    st.divider()
    st.markdown("### Asset filters")

    state_options = sorted(
        working_assets["state"].fillna("Unknown").astype(str).unique()
    )

    selected_states = st.multiselect(
        "State",
        state_options,
        default=[],
        help="Leave empty to include all states.",
    )

    status_options = sorted(
        working_assets["status"].fillna("Unknown").astype(str).unique()
    )

    selected_statuses = st.multiselect(
        "Status",
        status_options,
        default=status_options,
    )

    working_assets["nameplate_capacity_mw"] = pd.to_numeric(
        working_assets["nameplate_capacity_mw"],
        errors="coerce",
    )

    max_mw = working_assets["nameplate_capacity_mw"].max()
    max_mw = max(1.0, float(max_mw)) if pd.notna(max_mw) else 1.0

    capacity_range = st.slider(
        "Capacity (MW)",
        min_value=0.0,
        max_value=max_mw,
        value=(0.0, max_mw),
    )


filtered = working_assets[
    working_assets["status"].fillna("Unknown").astype(str).isin(
        selected_statuses
    )
].copy()

if selected_states:
    filtered = filtered[
        filtered["state"].fillna("Unknown").astype(str).isin(
            selected_states
        )
    ].copy()

filtered = filtered[
    filtered["nameplate_capacity_mw"].between(*capacity_range)
].copy()


# ============================================================
# EXECUTIVE KPIs
# ============================================================

n_records = len(filtered)
n_capacity = filtered["nameplate_capacity_mw"].sum()
n_states = filtered["state"].nunique()
n_plants = (
    filtered["plant_code"].nunique()
    if "plant_code" in filtered
    else n_records
)

tech_counts = filtered["technology_display"].value_counts()

solar_count = int(tech_counts.get("Solar", 0))
wind_count = int(tech_counts.get("Wind", 0))
bess_count = int(tech_counts.get("BESS", 0))

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{n_records:,}</div><div class="kpi-label">'
        'Generator records in view</div></div>',
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{n_capacity:,.1f} MW</div><div class="kpi-label">'
        'Represented capacity</div></div>',
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{n_plants:,}</div><div class="kpi-label">'
        'Distinct plant codes</div></div>',
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{n_states:,}</div><div class="kpi-label">'
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

st.caption(f"Data source: {source_label}. {source_warning}")

if actual_source_url:
    st.markdown(f"[Open source workbook]({actual_source_url})")


# ============================================================
# CHART HELPER
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
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        margin=dict(t=65, b=40, l=45, r=25),
        hoverlabel=dict(
            bgcolor=WHITE,
            font=dict(family=FONT, size=12, color=BLACK),
        ),
    )

    fig.update_xaxes(
        tickfont=dict(family=FONT, size=12, color=BLACK),
        title_font=dict(family=FONT, size=12, color=BLACK),
        showgrid=False,
        automargin=True,
    )

    fig.update_yaxes(
        tickfont=dict(family=FONT, size=12, color=BLACK),
        title_font=dict(family=FONT, size=12, color=BLACK),
        gridcolor=LINE,
        showgrid=True,
        automargin=True,
    )

    return fig


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
        f"Current technology view: {technology_choice}. "
        "Only records with valid coordinates can appear on the map."
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
            "Use the project register to inspect records or load a dataset "
            "that includes latitude and longitude."
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
        "Generator coordinates do not establish parcel boundaries, usable "
        "land, available transmission capacity or interconnection feasibility."
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
        placeholder="Search project, owner, state, county or generator ID",
    )

    searchable_fields = [
        "plant_name", "state", "county", "entity_name",
        "technology_group", "generator_id", "plant_code",
        "status", "energy_source_code", "prime_mover_code",
    ]

    searchable_fields = [
        c for c in searchable_fields if c in filtered.columns
    ]

    search_results = filtered.copy()

    if search_text.strip():
        mask = search_results[searchable_fields].apply(
            lambda col: col.astype(str).str.contains(
                search_text.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        search_results = search_results[mask].copy()

    display_columns = [
        "plant_name", "technology_display", "entity_name",
        "state", "county", "plant_code", "generator_id",
        "nameplate_capacity_mw", "net_summer_capacity_mw",
        "status", "operating_year", "planned_operating_year",
    ]

    display_columns = [
        c for c in display_columns if c in search_results.columns
    ]

    st.dataframe(
        search_results[display_columns],
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    st.caption(f"{len(search_results):,} records shown.")

    st.download_button(
        "Download filtered projects CSV",
        data=search_results.to_csv(index=False).encode("utf-8"),
        file_name="sunstripe_filtered_projects.csv",
        mime="text/csv",
    )


# ============================================================
# PROJECT DETAILS
# ============================================================

with tab_details:
    st.markdown(
        '<div class="section-title">Full project information</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No projects match the current filters.")
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

        display_to_record = dict(
            zip(options["_display"], options["record_id"])
        )

        selected_label = st.selectbox(
            "Select a project or generator",
            options["_display"].tolist(),
        )

        selected_record = display_to_record[selected_label]

        project = filtered[
            filtered["record_id"] == selected_record
        ].iloc[0]

        st.markdown(f"### {project['plant_name']}")

        d1, d2, d3, d4 = st.columns(4)

        d1.metric("Technology", project["technology_display"])

        capacity = project["nameplate_capacity_mw"]
        d2.metric(
            "Nameplate capacity",
            f"{capacity:,.2f} MW" if pd.notna(capacity) else "Not reported",
        )

        d3.metric("State", str(project.get("state", "Not reported")))

        d4.metric("Reported status", str(project.get("status", "Not reported")))

        st.markdown(
            '<div class="section-title">Key project information</div>',
            unsafe_allow_html=True,
        )

        important_fields = [
            ("Plant name", "plant_name"),
            ("Technology", "technology_group"),
            ("Plant code / ID", "plant_code"),
            ("Generator ID", "generator_id"),
            ("Owner / entity", "entity_name"),
            ("Entity ID", "entity_id"),
            ("Producer type", "producer_type"),
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

        details = []

        for label, column in important_fields:
            value = project.get(column, None)

            if value is None or pd.isna(value) or str(value).strip() == "":
                value = "Not reported in this record"

            elif column in [
                "latitude", "longitude",
                "nameplate_capacity_mw", "net_summer_capacity_mw",
            ] and isinstance(value, (float, int)):
                if column in ["latitude", "longitude"]:
                    value = f"{value:.6f}"
                else:
                    value = f"{value:,.2f}"

            details.append({
                "Information": label,
                "Value": str(value),
            })

        st.dataframe(
            pd.DataFrame(details),
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
            data=project.drop(labels=["_display"], errors="ignore")
                .to_frame().T.to_csv(index=False).encode("utf-8"),
            file_name=f"sunstripe_project_{selected_record}.csv",
            mime="text/csv",
        )

        project_url = project.get("source_url", "")

        if isinstance(project_url, str) and project_url.startswith("https://"):
            st.markdown(f"[Open official source workbook]({project_url})")
        else:
            st.markdown(f"[Open EIA-860M source page]({EIA_PAGE})")

        st.warning(
            "Only fields supplied by the data source are available. "
            "Land ownership, parcel-level area, permits, detailed environmental "
            "studies, interconnection results, BESS energy duration and project "
            "revenue may require other sources."
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
        st.info("No records are available to chart.")
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

        status_counts = (
            filtered.groupby("status", as_index=False)
            .size()
            .rename(columns={"size": "Generator records"})
            .sort_values("Generator records", ascending=False)
        )

        fig2 = px.bar(
            status_counts,
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

        st.plotly_chart(style_chart(fig2), use_container_width=True)


# ============================================================
# DATA SOURCES AND LIMITATIONS
# ============================================================

with tab_sources:
    st.markdown(
        '<div class="section-title">Data sources and limitations</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
**Selected source:** {source_label}

**Official EIA-860M inventory:**  
{EIA_PAGE}

The EIA monthly inventory reports existing and proposed generating units.
Reported capacities are preliminary and can be revised in later releases.

**Data limitations**

- A generator record is not necessarily a unique development project.
- One plant may contain several generators.
- Coordinates are not guaranteed to be available for every record.
- Some storage records may not include MWh energy capacity.
- Land ownership, acreage, market revenue and interconnection capacity are
  not guaranteed to be included in the generator inventory.
""")

    st.markdown("#### Other authoritative source directories")

    st.markdown("""
- [EIA annual generator inventory](https://www.eia.gov/electricity/data/eia860/)
- [NREL developer resources](https://developer.nrel.gov/)
- [USGS National Map](https://www.usgs.gov/the-national-map-data-delivery)
- [FEMA flood maps](https://www.fema.gov/flood-maps)
- [US Fish and Wildlife Service](https://www.fws.gov/)
- [ERCOT](https://www.ercot.com/)
- [CAISO](https://www.caiso.com/)
- [MISO](https://www.misoenergy.org/)
- [PJM](https://www.pjm.com/)
""")

    health = pd.DataFrame([
        {"Feature": "Solar / Wind / BESS selector", "Status": "Implemented"},
        {"Feature": "Filtered project register", "Status": "Implemented"},
        {"Feature": "Full source record view", "Status": "Implemented"},
        {"Feature": "EIA workbook format validation", "Status": "Implemented"},
        {"Feature": "Manual CSV / XLS / XLSX upload", "Status": "Implemented"},
        {"Feature": "Map", "Status": "Requires valid coordinates"},
        {"Feature": "Parcel valuation", "Status": "Not connected"},
        {"Feature": "Verified grid capacity", "Status": "Not connected"},
        {"Feature": "Live power-market data", "Status": "Not connected"},
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
