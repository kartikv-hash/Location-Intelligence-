
import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# SUNSTRIPE LOCATION INTELLIGENCE
# Renewable Energy Asset Discovery | United States
# Solar | BESS | Wind
# ============================================================

st.set_page_config(
    page_title="Sunstripe Location Intelligence",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# BRAND AND TYPOGRAPHY
# ============================================================

BG = "#FBF9F7"
NAVY = "#050714"
RED = "#E8392D"
BLACK = "#000000"
WHITE = "#FFFFFF"
LINE = "#E7E0DB"
MUTED = "#000000"
FONT = "DM Sans, Arial, sans-serif"

TECH_COLORS = {
    "Solar": "#D9A72E",
    "Wind": "#41986A",
    "BESS": "#3979CC",
    "Other": "#89817B",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --navy: #050714;
    --red: #E8392D;
    --paper: #FBF9F7;
    --line: #E7E0DB;
    --black: #000000;
    --white: #FFFFFF;
}

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

/* Main content: black text on ivory */
[data-testid="stAppViewContainer"] .main {
    color: #000000 !important;
}

[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main li,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main small,
[data-testid="stAppViewContainer"] .main strong,
[data-testid="stAppViewContainer"] .main em {
    color: #000000;
}

/* Header */
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

/* Main title */
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

/* KPI cards */
.kpi-card {
    background: rgba(255,255,255,0.75);
    border: 1px solid #E7E0DB;
    padding: 17px 18px;
    min-height: 104px;
    border-radius: 2px;
}

.kpi-value {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 28px;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: -0.5px;
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

.pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 16px 0 22px;
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

.section-title {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 16px;
    font-weight: 700;
    color: #000000 !important;
    border-top: 1px solid #E7E0DB;
    padding-top: 18px;
    margin-top: 22px;
    margin-bottom: 12px;
}

/* Tabs: explicitly visible labels */
.stTabs [data-baseweb="tab-list"] {
    gap: 25px;
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
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div {
    color: #000000 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div {
    color: #E8392D !important;
    border-bottom-color: #E8392D !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.75);
    border: 1px solid #E7E0DB;
    border-radius: 2px;
    padding: 15px;
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricDelta"] {
    color: #000000 !important;
}

div[data-testid="stMetricValue"] {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 27px;
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
    border-color: #E8392D;
}

/* Tables and inputs */
div[data-testid="stDataFrame"] {
    border: 1px solid #E7E0DB;
}

div[data-testid="stDataFrame"] *,
div[data-testid="stTable"] * {
    color: #000000 !important;
}

div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] *,
div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] *,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li {
    color: #000000 !important;
}

.stApp input,
.stApp textarea {
    color: #000000 !important;
    font-family: 'DM Sans', Arial, sans-serif !important;
}

.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #000000 !important;
    opacity: 0.7;
}

hr {
    border-color: #E7E0DB;
}

/* Sidebar: white typography on midnight black */
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

/* Footer */
.footer {
    text-align: center;
    color: #000000 !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 10px 0;
}

@media (max-width: 768px) {
    .topbar {
        padding: 18px 12px 13px;
    }

    .brand {
        font-size: 22px;
    }

    .navrow {
        gap: 14px;
        font-size: 12px;
    }

    .hero {
        font-size: 32px;
        letter-spacing: -0.7px;
    }

    .subtitle {
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# UNIVERSAL PLOTLY THEME
# Apply this function to EVERY chart before displaying it.
# This fixes the pale legend, axes, and chart title problem.
# ============================================================

def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        font=dict(
            family=FONT,
            size=13,
            color=BLACK,
        ),
        title=dict(
            font=dict(
                family=FONT,
                size=16,
                color=BLACK,
            ),
            x=0,
            xanchor="left",
        ),
        legend=dict(
            font=dict(
                family=FONT,
                size=12,
                color=BLACK,
            ),
            title=dict(
                font=dict(
                    family=FONT,
                    size=12,
                    color=BLACK,
                )
            ),
            bgcolor="rgba(251,249,247,0)",
        ),
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        margin=dict(t=65, b=40, l=45, r=25),
        coloraxis_colorbar=dict(
            tickfont=dict(color=BLACK, family=FONT, size=12),
            title_font=dict(color=BLACK, family=FONT, size=12),
        ),
        hoverlabel=dict(
            bgcolor=WHITE,
            font=dict(
                family=FONT,
                size=12,
                color=BLACK,
            ),
            bordercolor=LINE,
        ),
    )

    fig.update_xaxes(
        title_font=dict(family=FONT, size=12, color=BLACK),
        tickfont=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showline=True,
        linecolor=LINE,
        linewidth=1,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        title_font=dict(family=FONT, size=12, color=BLACK),
        tickfont=dict(family=FONT, size=12, color=BLACK),
        automargin=True,
        showline=False,
        showgrid=True,
        gridcolor="#E8E1DC",
        gridwidth=1,
        zeroline=False,
    )

    return fig


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_repository_csv():
    return pd.read_csv("renewable_asset_register.csv")


with st.sidebar:
    st.markdown("## Sunstripe")
    st.caption("LOCATION INTELLIGENCE PLATFORM")
    st.divider()

    st.markdown("### Data source")
    st.caption("Default: renewable_asset_register.csv")

    uploaded_file = st.file_uploader(
        "Upload asset register",
        type=["csv"],
        help="Upload a CSV containing renewable energy asset records.",
    )

    st.divider()
    st.markdown("### Asset filters")


if uploaded_file is not None:
    try:
        assets = pd.read_csv(uploaded_file)
        data_message = "Uploaded CSV loaded successfully."
    except Exception as exc:
        st.error(f"Could not read uploaded CSV: {exc}")
        st.stop()
else:
    try:
        assets = load_repository_csv()
        data_message = "Repository CSV loaded successfully."
    except FileNotFoundError:
        st.error(
            "renewable_asset_register.csv was not found. Add the file "
            "to your repository root or upload it using the sidebar."
        )
        st.stop()
    except Exception as exc:
        st.error(f"Could not load repository CSV: {exc}")
        st.stop()


# ============================================================
# NORMALIZE COLUMNS
# ============================================================

assets.columns = [
    str(column).strip().lower().replace(" ", "_")
    for column in assets.columns
]

ALIASES = {
    "technology_group": [
        "technology_group", "technology", "energy_type", "fuel_type"
    ],
    "plant_name": [
        "plant_name", "project_name", "facility_name", "name"
    ],
    "state": ["state", "state_name"],
    "county": ["county", "county_name"],
    "latitude": ["latitude", "lat", "plant_latitude"],
    "longitude": ["longitude", "lon", "lng", "plant_longitude"],
    "nameplate_capacity_mw": [
        "nameplate_capacity_mw", "capacity_mw", "nameplate_mw", "mw"
    ],
    "nameplate_energy_capacity_mwh": [
        "nameplate_energy_capacity_mwh",
        "energy_capacity_mwh",
        "storage_capacity_mwh",
        "mwh",
    ],
    "lifecycle_group": [
        "lifecycle_group", "status", "project_status", "operational_status"
    ],
    "source_year": ["source_year", "year"],
}

for standard_name, alternatives in ALIASES.items():
    if standard_name not in assets.columns:
        for alternative in alternatives:
            if alternative in assets.columns:
                assets[standard_name] = assets[alternative]
                break

DEFAULTS = {
    "technology_group": "Unknown",
    "plant_name": "Unnamed asset",
    "state": "Unknown",
    "county": "Unknown",
    "latitude": None,
    "longitude": None,
    "nameplate_capacity_mw": 0,
    "nameplate_energy_capacity_mwh": 0,
    "lifecycle_group": "Unknown",
    "source_year": None,
}

for column, default in DEFAULTS.items():
    if column not in assets.columns:
        assets[column] = default

for column in [
    "latitude",
    "longitude",
    "nameplate_capacity_mw",
    "nameplate_energy_capacity_mwh",
]:
    assets[column] = pd.to_numeric(assets[column], errors="coerce")

assets["nameplate_capacity_mw"] = (
    assets["nameplate_capacity_mw"].fillna(0)
)

assets["nameplate_energy_capacity_mwh"] = (
    assets["nameplate_energy_capacity_mwh"].fillna(0)
)

for column in [
    "technology_group",
    "plant_name",
    "state",
    "county",
    "lifecycle_group",
]:
    assets[column] = (
        assets[column].fillna("Unknown").astype(str).str.strip()
    )


def classify_technology(value):
    value = str(value).strip().lower()

    if "solar" in value or "photovoltaic" in value or value == "pv":
        return "Solar"

    if "wind" in value:
        return "Wind"

    if "battery" in value or "storage" in value or "bess" in value:
        return "BESS"

    return "Other"


assets["technology_display"] = (
    assets["technology_group"].apply(classify_technology)
)

assets = assets.reset_index(drop=True)
assets["asset_record_id"] = assets.index + 1


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:
    available_technologies = sorted(
        assets["technology_display"].dropna().unique().tolist()
    )

    selected_technologies = st.multiselect(
        "Technology",
        options=available_technologies,
        default=available_technologies,
    )

    available_states = sorted(
        assets["state"].dropna().unique().tolist()
    )

    selected_states = st.multiselect(
        "State",
        options=available_states,
        default=[],
        help="Leave empty to include all states.",
    )

    available_statuses = sorted(
        assets["lifecycle_group"].dropna().unique().tolist()
    )

    selected_statuses = st.multiselect(
        "Lifecycle / status",
        options=available_statuses,
        default=available_statuses,
    )

    min_capacity = max(
        0.0, float(assets["nameplate_capacity_mw"].min())
    )
    max_capacity = max(
        min_capacity, float(assets["nameplate_capacity_mw"].max())
    )

    if max_capacity > min_capacity:
        capacity_range = st.slider(
            "Capacity range (MW)",
            min_value=min_capacity,
            max_value=max_capacity,
            value=(min_capacity, max_capacity),
        )
    else:
        capacity_range = (min_capacity, max_capacity)

    st.divider()
    st.caption("SUNSTRIPE LOCATION INTELLIGENCE")


# ============================================================
# FILTER DATA
# ============================================================

filtered_assets = assets[
    assets["technology_display"].isin(selected_technologies)
    & assets["lifecycle_group"].isin(selected_statuses)
].copy()

if selected_states:
    filtered_assets = filtered_assets[
        filtered_assets["state"].isin(selected_states)
    ]

filtered_assets = filtered_assets[
    filtered_assets["nameplate_capacity_mw"].between(
        capacity_range[0], capacity_range[1]
    )
].copy()


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
Explore renewable energy assets across the United States. Filter by technology,
state and capacity, inspect reported geographic locations, and review the
portfolio through consistent, readable analytics.
</div>
""", unsafe_allow_html=True)


# ============================================================
# KPI SUMMARY
# ============================================================

total_records = len(filtered_assets)
total_capacity = filtered_assets["nameplate_capacity_mw"].sum()
total_storage = filtered_assets["nameplate_energy_capacity_mwh"].sum()
states_covered = filtered_assets["state"].nunique()

solar_count = int(
    (filtered_assets["technology_display"] == "Solar").sum()
)
wind_count = int(
    (filtered_assets["technology_display"] == "Wind").sum()
)
bess_count = int(
    (filtered_assets["technology_display"] == "BESS").sum()
)

st.success(data_message)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{total_records:,}</div><div class="kpi-label">'
        'Asset records in view</div></div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{total_capacity:,.1f} MW</div><div class="kpi-label">'
        'Represented power capacity</div></div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{total_storage:,.1f} MWh</div><div class="kpi-label">'
        'Represented storage energy</div></div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{states_covered:,}</div><div class="kpi-label">'
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
    "Metrics describe the filtered CSV dataset. Records may not represent "
    "unique projects and are not necessarily independently verified."
)


# ============================================================
# TABS
# ============================================================

tab_overview, tab_map, tab_register, tab_method = st.tabs([
    "Executive overview",
    "Location explorer",
    "Asset register",
    "Data & methodology",
])


# ============================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================

with tab_overview:
    st.markdown(
        '<div class="section-title">Technology portfolio</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        tech_counts = (
            filtered_assets["technology_display"]
            .value_counts()
            .rename_axis("Technology")
            .reset_index(name="Asset records")
        )

        if not tech_counts.empty:
            fig = px.pie(
                tech_counts,
                names="Technology",
                values="Asset records",
                hole=0.58,
                title="Asset records by technology",
                color="Technology",
                color_discrete_map=TECH_COLORS,
                labels={
                    "technology_display": "Technology",
                    "Asset records": "Asset records",
                },
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                textfont=dict(
                    family=FONT,
                    size=12,
                    color=BLACK,
                ),
                marker=dict(
                    line=dict(color=BG, width=2)
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Records: %{value:,}<br>"
                    "Share: %{percent}<extra></extra>"
                ),
            )

            fig = style_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No assets match the selected filters.")

    with right:
        state_capacity = (
            filtered_assets.groupby("state", as_index=False)
            ["nameplate_capacity_mw"].sum()
            .sort_values("nameplate_capacity_mw", ascending=False)
            .head(15)
        )

        if not state_capacity.empty:
            fig = px.bar(
                state_capacity,
                x="state",
                y="nameplate_capacity_mw",
                title="Top 15 states by represented capacity",
                labels={
                    "state": "State",
                    "nameplate_capacity_mw": "Capacity (MW)",
                },
                text="nameplate_capacity_mw",
            )

            fig.update_traces(
                marker_color=RED,
                marker_line_width=0,
                texttemplate="%{text:,.0f}",
                textposition="outside",
                textfont=dict(
                    family=FONT,
                    size=10,
                    color=BLACK,
                ),
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Capacity: %{y:,.1f} MW<extra></extra>"
                ),
            )

            fig = style_chart(fig)
            fig.update_yaxes(
                rangemode="tozero",
                title_text="Capacity (MW)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No state capacity data is available.")

    st.markdown(
        '<div class="section-title">Lifecycle distribution</div>',
        unsafe_allow_html=True,
    )

    lifecycle_counts = (
        filtered_assets["lifecycle_group"]
        .value_counts()
        .rename_axis("Lifecycle / status")
        .reset_index(name="Asset records")
    )

    if not lifecycle_counts.empty:
        fig = px.bar(
            lifecycle_counts,
            x="Lifecycle / status",
            y="Asset records",
            title="Asset records by reported lifecycle status",
            text="Asset records",
        )

        fig.update_traces(
            marker_color=RED,
            texttemplate="%{text:,}",
            textposition="outside",
            textfont=dict(family=FONT, size=11, color=BLACK),
            cliponaxis=False,
        )

        fig = style_chart(fig)
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2: LOCATION EXPLORER
# ============================================================

with tab_map:
    st.markdown(
        '<div class="section-title">Geographic asset intelligence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Explore reported locations. Coordinates do not establish parcel "
        "boundaries, buildable acreage or interconnection feasibility."
    )

    map_data = filtered_assets.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    map_data = map_data[
        map_data["latitude"].between(-90, 90)
        & map_data["longitude"].between(-180, 180)
    ]

    if not map_data.empty:
        fig_map = px.scatter_map(
            map_data,
            lat="latitude",
            lon="longitude",
            color="technology_display",
            hover_name="plant_name",
            hover_data={
                "state": True,
                "county": True,
                "nameplate_capacity_mw": ":,.2f",
                "nameplate_energy_capacity_mwh": ":,.2f",
                "lifecycle_group": True,
                "latitude": False,
                "longitude": False,
            },
            zoom=3,
            height=610,
            map_style="open-street-map",
            color_discrete_map=TECH_COLORS,
            labels={
                "technology_display": "Technology",
                "nameplate_capacity_mw": "Capacity (MW)",
                "nameplate_energy_capacity_mwh": "Storage energy (MWh)",
                "lifecycle_group": "Lifecycle / status",
            },
        )

        # Apply consistent typography to map legends and hover labels.
        fig_map.update_layout(
            font=dict(family=FONT, size=13, color=BLACK),
            title_font=dict(family=FONT, size=16, color=BLACK),
            legend=dict(
                font=dict(family=FONT, size=12, color=BLACK),
                title=dict(font=dict(family=FONT, size=12, color=BLACK)),
                bgcolor="rgba(251,249,247,0.92)",
            ),
            paper_bgcolor=BG,
            margin=dict(t=12, b=12, l=12, r=12),
        )

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning(
            "No valid coordinates were found. Check the latitude and "
            "longitude columns in your CSV."
        )


# ============================================================
# TAB 3: ASSET REGISTER
# ============================================================

with tab_register:
    st.markdown(
        '<div class="section-title">Renewable asset register</div>',
        unsafe_allow_html=True,
    )

    search_term = st.text_input(
        "Search asset register",
        placeholder="Search name, state, county, technology or status",
    )

    search_columns = [
        "plant_name", "state", "county",
        "technology_group", "technology_display", "lifecycle_group",
    ]

    search_results = filtered_assets.copy()

    if search_term.strip():
        search_mask = search_results[search_columns].apply(
            lambda col: col.astype(str).str.contains(
                search_term.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        search_results = search_results[search_mask].copy()

    display_columns = [
        "asset_record_id",
        "plant_name",
        "technology_group",
        "technology_display",
        "state",
        "county",
        "nameplate_capacity_mw",
        "nameplate_energy_capacity_mwh",
        "lifecycle_group",
        "latitude",
        "longitude",
    ]

    display_columns = [
        column for column in display_columns
        if column in search_results.columns
    ]

    st.dataframe(
        search_results[display_columns],
        use_container_width=True,
        hide_index=True,
        height=460,
        column_config={
            "asset_record_id": st.column_config.NumberColumn("Record ID"),
            "plant_name": st.column_config.TextColumn("Asset / plant name"),
            "technology_group": st.column_config.TextColumn(
                "Reported technology"
            ),
            "technology_display": st.column_config.TextColumn(
                "Technology group"
            ),
            "nameplate_capacity_mw": st.column_config.NumberColumn(
                "Capacity (MW)", format="%.2f"
            ),
            "nameplate_energy_capacity_mwh": st.column_config.NumberColumn(
                "Storage energy (MWh)", format="%.2f"
            ),
            "latitude": st.column_config.NumberColumn(
                "Latitude", format="%.5f"
            ),
            "longitude": st.column_config.NumberColumn(
                "Longitude", format="%.5f"
            ),
        },
    )

    st.caption(f"{len(search_results):,} asset records shown.")

    st.download_button(
        "Download filtered asset register (CSV)",
        data=search_results.to_csv(index=False).encode("utf-8"),
        file_name="sunstripe_filtered_asset_register.csv",
        mime="text/csv",
    )


# ============================================================
# TAB 4: DATA AND METHODOLOGY
# ============================================================

with tab_method:
    st.markdown(
        '<div class="section-title">Data provenance and methodology</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
**Default data source**

`renewable_asset_register.csv` in the repository root. Alternatively,
upload a CSV through the sidebar.

**Recognized input fields**

| Field | Purpose |
|---|---|
| `plant_name` / `project_name` | Asset or project name |
| `technology_group` / `technology` | Technology |
| `state` | State |
| `county` | County |
| `latitude` / `longitude` | Geographic coordinates |
| `nameplate_capacity_mw` / `capacity_mw` | Power capacity in MW |
| `nameplate_energy_capacity_mwh` / `energy_capacity_mwh` | Storage energy in MWh |
| `lifecycle_group` / `status` | Reported asset status |
| `source_year` / `year` | Source year |
""")

    st.markdown(
        '<div class="section-title">Recommended authoritative sources</div>',
        unsafe_allow_html=True,
    )

    sources = pd.DataFrame([
        {
            "Provider": "US Energy Information Administration",
            "Data use": "Generator and plant inventories",
            "Official source": "https://www.eia.gov/opendata/",
        },
        {
            "Provider": "National Renewable Energy Laboratory",
            "Data use": "Renewable resource information",
            "Official source": "https://developer.nrel.gov/",
        },
        {
            "Provider": "US Geological Survey",
            "Data use": "Terrain, elevation and hydrography",
            "Official source": "https://www.usgs.gov/",
        },
        {
            "Provider": "Federal Emergency Management Agency",
            "Data use": "Flood hazard information",
            "Official source": "https://www.fema.gov/flood-maps",
        },
        {
            "Provider": "US Fish and Wildlife Service",
            "Data use": "Wetlands and ecological screening",
            "Official source": "https://www.fws.gov/",
        },
        {
            "Provider": "ERCOT",
            "Data use": "Texas grid and electricity market",
            "Official source": "https://www.ercot.com/",
        },
        {
            "Provider": "CAISO",
            "Data use": "California grid and electricity market",
            "Official source": "https://www.caiso.com/",
        },
        {
            "Provider": "MISO",
            "Data use": "Regional grid and market information",
            "Official source": "https://www.misoenergy.org/",
        },
        {
            "Provider": "PJM",
            "Data use": "Regional grid and market information",
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

    st.markdown(
        '<div class="section-title">Important limitations</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
- The platform analyzes the supplied CSV and does not independently verify every record.
- Asset coordinates do not establish parcel boundaries or available acreage.
- MW measures power capacity; MWh measures energy capacity.
- External sources listed here are references, not active data integrations.
- Land value, parcel ownership, interconnection capacity, resource quality,
  permitting, environmental constraints and market economics need additional
  verified datasets and dedicated analysis.
""")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div class="footer">
    SUNSTRIPE LOCATION INTELLIGENCE · ENERGY INFRASTRUCTURE · SOLAR / STORAGE / WIND
</div>
""", unsafe_allow_html=True)
