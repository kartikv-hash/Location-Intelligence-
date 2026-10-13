
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# SUNSTRIPE INTELLIGENCE
# Renewable Energy Location Intelligence | United States
# Solar | BESS | Wind
# ============================================================

st.set_page_config(
    page_title="Sunstripe Intelligence",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# SUNSTRIPE BRAND THEME
# Midnight navy | Warm ivory | Restrained red | Editorial type
# ------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;1,500&display=swap');

:root {
    --ink: #080B18;
    --navy: #050714;
    --red: #E8392D;
    --paper: #FBF9F7;
    --white: #FFFFFF;
    --line: #E8E1DC;
    --muted: #766F6A;
    --soft: #F2EEEA;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--paper);
    color: var(--ink);
}

.block-container {
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 2.5rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

div[data-testid="stToolbar"] {
    visibility: hidden;
}

/* Brand navigation */

.topbar {
    background: var(--navy);
    color: var(--white);
    margin: -1rem -1rem 1.6rem -1rem;
    padding: 20px 24px 16px;
    border-bottom: 2px solid var(--red);
}

.brand {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.8px;
    text-align: center;
    color: var(--white);
}

.brand .accent {
    color: #FF5145;
}

.brand-tagline {
    font-size: 10px;
    letter-spacing: 2.5px;
    text-align: center;
    margin-top: 4px;
    color: #C8C6CE;
    text-transform: uppercase;
}

.navrow {
    display: flex;
    justify-content: center;
    gap: 26px;
    flex-wrap: wrap;
    color: #F5F3F1;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .6px;
    margin-top: 19px;
}

.navitem {
    padding: 6px 0;
    border-bottom: 2px solid transparent;
}

.navitem.active {
    border-color: var(--red);
    color: white;
}

/* Editorial heading */

.eyebrow {
    font-size: 11px;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: var(--red);
    font-weight: 700;
    margin: 5px 0 10px;
}

.hero {
    font-family: 'Playfair Display', serif;
    font-size: clamp(32px, 4vw, 47px);
    line-height: 1.1;
    font-style: italic;
    color: var(--red);
    letter-spacing: -1.1px;
    margin: 12px 0 15px;
}

.subtitle {
    font-size: 14px;
    line-height: 1.8;
    color: #6F6762;
    max-width: 850px;
    margin-bottom: 23px;
}

/* KPI cards */

.kpi-card {
    background: rgba(255,255,255,.62);
    border: 1px solid var(--line);
    padding: 17px;
    min-height: 102px;
}

.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 29px;
    line-height: 1.2;
    color: var(--red);
    overflow-wrap: anywhere;
}

.kpi-label {
    font-size: 11px;
    color: #766F6A;
    margin-top: 9px;
    line-height: 1.5;
}

.section-title {
    font-size: 14px;
    font-weight: 700;
    color: #282321;
    border-top: 1px solid var(--line);
    padding-top: 18px;
    margin-top: 22px;
    margin-bottom: 12px;
}

.section-note {
    font-size: 11px;
    letter-spacing: .5px;
    color: #807771;
    text-transform: uppercase;
}

.pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 17px 0 22px;
}

.pill {
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 6px 12px;
    background: #FFFDFA;
    color: #625A55;
    font-size: 11px;
}

/* Streamlit widgets */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.65);
    border: 1px solid var(--line);
    border-radius: 3px;
    padding: 13px 15px;
}

div[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif;
    color: var(--red);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    border-bottom: 1px solid var(--line);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    padding: 11px 2px;
    color: #5D5550;
    font-size: 12px;
}

.stTabs [aria-selected="true"] {
    color: var(--red) !important;
    border-bottom: 2px solid var(--red) !important;
}

.stButton button, .stDownloadButton button {
    border-radius: 22px;
    border: 1px solid var(--red);
    color: var(--red);
    background: transparent;
    font-weight: 600;
}

.stButton button:hover, .stDownloadButton button:hover {
    background: var(--red);
    color: white;
    border-color: var(--red);
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
}

div[data-testid="stFileUploader"] {
    border: 1px solid var(--line);
    padding: 10px;
    border-radius: 4px;
}

hr {
    border-color: var(--line);
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: var(--navy);
    border-right: 1px solid #252735;
}

section[data-testid="stSidebar"] * {
    color: #F5F3F1;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #C7C3CA;
}

section[data-testid="stSidebar"] hr {
    border-color: #353643;
}

section[data-testid="stSidebar"] input {
    color: var(--ink);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# DATA LOADING
# ------------------------------------------------------------

@st.cache_data
def load_asset_data():
    # Default repository CSV
    assets = pd.read_csv("renewable_asset_register.csv")
    return assets


def load_uploaded_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return None


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown("""
<div class="topbar">
    <div class="brand">
        Sunstripe <span class="accent">Intelligence</span>
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
""", unsafe_allow_html=True)

st.markdown(
    '<div class="eyebrow">● LOCATION INTELLIGENCE / UNITED STATES</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero">Find the next right place<br>to build.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'A unified intelligence workspace for renewable energy asset discovery, '
    'location screening and portfolio analysis. Explore Solar, Battery Energy '
    'Storage and Wind assets across the United States.'
    '</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# DATA INPUT
# ------------------------------------------------------------

with st.sidebar:
    st.markdown("## Sunstripe")
    st.caption("INTELLIGENCE PLATFORM")
    st.divider()

    st.markdown("### Data source")
    st.caption("Default: renewable_asset_register.csv")

    uploaded_file = st.file_uploader(
        "Upload asset register",
        type=["csv"],
        help="Upload a CSV containing renewable energy asset information.",
    )

    st.divider()
    st.markdown("### Asset filters")

try:
    assets = load_asset_data()
    data_message = "Repository CSV loaded successfully."
except FileNotFoundError:
    assets = None
    data_message = (
        "renewable_asset_register.csv was not found in the repository root. "
        "Upload the file below or add it to the repository."
    )
except Exception as exc:
    assets = None
    data_message = f"Could not load the repository CSV: {exc}"

if uploaded_file is not None:
    try:
        assets = load_uploaded_data(uploaded_file)
        data_message = "Uploaded CSV loaded successfully."
    except Exception as exc:
        assets = None
        data_message = f"Could not read uploaded CSV: {exc}"

if assets is None:
    st.error(data_message)
    st.info(
        "Keep renewable_asset_register.csv in the same repository folder "
        "as app.py, or upload a compatible CSV using the sidebar."
    )
    st.stop()

assets.columns = [
    str(column).strip().lower().replace(" ", "_")
    for column in assets.columns
]

# ------------------------------------------------------------
# NORMALIZE COLUMN NAMES
# ------------------------------------------------------------

column_aliases = {
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
        "nameplate_energy_capacity_mwh", "energy_capacity_mwh",
        "storage_capacity_mwh", "mwh"
    ],
    "lifecycle_group": [
        "lifecycle_group", "status", "project_status", "operational_status"
    ],
    "source_year": ["source_year", "year"],
}

for standard_name, alternatives in column_aliases.items():
    if standard_name not in assets.columns:
        for alternative in alternatives:
            if alternative in assets.columns:
                assets[standard_name] = assets[alternative]
                break

defaults = {
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

for column, default in defaults.items():
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
    value = str(value).lower()

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


# ------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------

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

    minimum_capacity = float(
        max(0, assets["nameplate_capacity_mw"].min())
    )
    maximum_capacity = float(
        max(minimum_capacity, assets["nameplate_capacity_mw"].max())
    )

    if maximum_capacity > minimum_capacity:
        capacity_range = st.slider(
            "Capacity range (MW)",
            min_value=minimum_capacity,
            max_value=maximum_capacity,
            value=(minimum_capacity, maximum_capacity),
        )
    else:
        capacity_range = (minimum_capacity, maximum_capacity)

    st.divider()
    st.caption("SUNSTRIPE INTELLIGENCE")
    st.caption("Renewable asset data and location screening")


# ------------------------------------------------------------
# APPLY FILTERS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# KPI SUMMARY
# ------------------------------------------------------------

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
        'Represented nameplate capacity</div></div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{total_storage:,.1f} MWh</div><div class="kpi-label">'
        'Represented storage energy capacity</div></div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-value">'
        f'{states_covered:,}</div><div class="kpi-label">'
        'States represented</div></div>',
        unsafe_allow_html=True,
    )

technology_pills = (
    f'<span class="pill">Solar · {solar_count:,}</span>'
    f'<span class="pill">Wind · {wind_count:,}</span>'
    f'<span class="pill">BESS · {bess_count:,}</span>'
)

st.markdown(
    f'<div class="pill-row">{technology_pills}</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Metrics describe the filtered CSV dataset. Records may not represent "
    "unique development projects and are not necessarily independently verified."
)


# ------------------------------------------------------------
# NAVIGATION TABS
# ------------------------------------------------------------

tab_overview, tab_map, tab_assets, tab_data = st.tabs([
    "Executive overview",
    "Location explorer",
    "Asset register",
    "Data & methodology",
])


# ------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# ------------------------------------------------------------

with tab_overview:
    st.markdown(
        '<div class="section-title">Technology portfolio</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        technology_counts = (
            filtered_assets["technology_display"]
            .value_counts()
            .rename_axis("Technology")
            .reset_index(name="Asset records")
        )

        if not technology_counts.empty:
            fig = px.pie(
                technology_counts,
                names="Technology",
                values="Asset records",
                hole=0.60,
                title="Asset records by technology",
                color="Technology",
                color_discrete_map={
                    "Solar": "#DFAE2D",
                    "Wind": "#41986A",
                    "BESS": "#3979CC",
                    "Other": "#A39B95",
                },
            )
            fig.update_layout(
                paper_bgcolor="#FBF9F7",
                plot_bgcolor="#FBF9F7",
                font_family="DM Sans",
                font_color="#282321",
                margin=dict(t=65, b=20, l=15, r=15),
                legend_title_text="",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No records match the selected filters.")

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
            )
            fig.update_traces(
                marker_color="#E8392D",
                marker_line_width=0,
            )
            fig.update_layout(
                paper_bgcolor="#FBF9F7",
                plot_bgcolor="#FBF9F7",
                font_family="DM Sans",
                font_color="#282321",
                margin=dict(t=65, b=35, l=15, r=15),
                xaxis_title="",
                yaxis_title="Capacity (MW)",
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
            title="Assets by reported lifecycle status",
        )
        fig.update_traces(marker_color="#E8392D")
        fig.update_layout(
            paper_bgcolor="#FBF9F7",
            plot_bgcolor="#FBF9F7",
            font_family="DM Sans",
            font_color="#282321",
            xaxis_title="",
            yaxis_title="Asset records",
        )
        st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# TAB 2: LOCATION EXPLORER
# ------------------------------------------------------------

with tab_map:
    st.markdown(
        '<div class="section-title">Geographic asset intelligence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Explore reported asset locations across the United States. "
        "Plant coordinates are not parcel boundaries or buildable-area assessments."
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
            color_discrete_map={
                "Solar": "#DFAE2D",
                "Wind": "#41986A",
                "BESS": "#3979CC",
                "Other": "#8D8580",
            },
            labels={
                "technology_display": "Technology",
                "nameplate_capacity_mw": "Capacity (MW)",
                "nameplate_energy_capacity_mwh": "Storage energy (MWh)",
                "lifecycle_group": "Lifecycle / status",
            },
        )

        fig_map.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="#FBF9F7",
            font_family="DM Sans",
            font_color="#282321",
        )

        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown(
            '<div class="pill-row">'
            '<span class="pill">Solar · Gold</span>'
            '<span class="pill">Wind · Green</span>'
            '<span class="pill">BESS · Blue</span>'
            '<span class="pill">Other · Grey</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    else:
        st.warning(
            "No valid latitude and longitude values are available for the "
            "selected records. Check your CSV coordinate columns."
        )


# ------------------------------------------------------------
# TAB 3: ASSET REGISTER
# ------------------------------------------------------------

with tab_assets:
    st.markdown(
        '<div class="section-title">Renewable asset register</div>',
        unsafe_allow_html=True,
    )

    search_term = st.text_input(
        "Search asset name, state, county, technology or status",
        placeholder="Example: Texas, solar, battery...",
    )

    searchable_columns = [
        "plant_name",
        "state",
        "county",
        "technology_group",
        "technology_display",
        "lifecycle_group",
    ]

    search_results = filtered_assets.copy()

    if search_term.strip():
        search_mask = search_results[searchable_columns].apply(
            lambda column: column.astype(str).str.contains(
                search_term.strip(), case=False, na=False
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
        height=450,
        column_config={
            "asset_record_id": st.column_config.NumberColumn("Record ID"),
            "plant_name": st.column_config.TextColumn("Asset / plant name"),
            "technology_group": st.column_config.TextColumn("Reported technology"),
            "technology_display": st.column_config.TextColumn("Technology group"),
            "nameplate_capacity_mw": st.column_config.NumberColumn(
                "Capacity (MW)", format="%.2f"
            ),
            "nameplate_energy_capacity_mwh": st.column_config.NumberColumn(
                "Storage energy (MWh)", format="%.2f"
            ),
            "latitude": st.column_config.NumberColumn("Latitude", format="%.5f"),
            "longitude": st.column_config.NumberColumn("Longitude", format="%.5f"),
        },
    )

    st.caption(f"{len(search_results):,} asset records shown.")

    st.download_button(
        label="Download filtered asset register (CSV)",
        data=search_results.to_csv(index=False).encode("utf-8"),
        file_name="sunstripe_filtered_asset_register.csv",
        mime="text/csv",
    )


# ------------------------------------------------------------
# TAB 4: DATA & METHODOLOGY
# ------------------------------------------------------------

with tab_data:
    st.markdown(
        '<div class="section-title">Data provenance & methodology</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    **Default data source**

    `renewable_asset_register.csv` located in the root directory of the GitHub
    repository. A CSV can also be uploaded through the sidebar.

    **Supported common input columns**

    | Field | Purpose |
    |---|---|
    | `plant_name` / `project_name` | Plant or project name |
    | `technology_group` / `technology` | Reported technology |
    | `state` | State |
    | `county` | County |
    | `latitude` / `longitude` | Asset location |
    | `nameplate_capacity_mw` / `capacity_mw` | Power capacity in MW |
    | `nameplate_energy_capacity_mwh` / `energy_capacity_mwh` | Storage energy in MWh |
    | `lifecycle_group` / `status` | Reported asset status |
    | `source_year` / `year` | Source year |
    """)

    st.markdown(
        '<div class="section-title">Recommended authoritative data sources</div>',
        unsafe_allow_html=True,
    )

    source_rows = [
        {
            "Provider": "US Energy Information Administration",
            "Data use": "Generator and plant inventories",
            "Link": "https://www.eia.gov/opendata/",
        },
        {
            "Provider": "National Renewable Energy Laboratory",
            "Data use": "Renewable energy resource information",
            "Link": "https://developer.nrel.gov/",
        },
        {
            "Provider": "US Geological Survey",
            "Data use": "Elevation, terrain and hydrography",
            "Link": "https://www.usgs.gov/",
        },
        {
            "Provider": "Federal Emergency Management Agency",
            "Data use": "Flood hazard information",
            "Link": "https://www.fema.gov/flood-maps",
        },
        {
            "Provider": "US Fish and Wildlife Service",
            "Data use": "Wetlands and ecological screening",
            "Link": "https://www.fws.gov/",
        },
        {
            "Provider": "ERCOT",
            "Data use": "Texas market and grid information",
            "Link": "https://www.ercot.com/",
        },
        {
            "Provider": "CAISO",
            "Data use": "California market and grid information",
            "Link": "https://www.caiso.com/",
        },
        {
            "Provider": "MISO",
            "Data use": "Regional market and grid information",
            "Link": "https://www.misoenergy.org/",
        },
        {
            "Provider": "PJM",
            "Data use": "Regional market and interconnection information",
            "Link": "https://www.pjm.com/",
        },
    ]

    st.dataframe(
        pd.DataFrame(source_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Official source"),
        },
    )

    st.markdown(
        '<div class="section-title">Screening limitations</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    - This version displays data supplied in the asset register and does not
      independently verify every record.
    - Asset coordinates do not establish parcel boundaries or available acreage.
    - MW measures power capacity. MWh measures energy capacity.
    - This application does not currently connect automatically to the listed
      external data sources.
    - Land values, comparable transactions, parcel ownership, transmission
      capacity, environmental constraints and permitting restrictions require
      separate validated data and analysis.
    - Commercial use of datasets must comply with each provider's licensing terms.
    """)

st.divider()

st.markdown(
    '<div style="text-align:center;color:#807771;font-size:11px;'
    'letter-spacing:1px;padding:8px;">'
    'SUNSTRIPE INTELLIGENCE &nbsp; · &nbsp; ENERGY INFRASTRUCTURE'
    '</div>',
    unsafe_allow_html=True,
)
