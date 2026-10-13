
import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# SUNSTRIPE INTELLIGENCE
# Renewable Energy Location Intelligence
# Solar | Battery Storage | Wind
# ============================================================

st.set_page_config(
    page_title="Sunstripe Intelligence | Location Intelligence",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME: SUNSTRIPE BLACK, IVORY AND RED
# TYPOGRAPHY: DM SANS ONLY
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --ink: #10111A;
    --navy: #050714;
    --red: #E8392D;
    --paper: #FBF9F7;
    --white: #FFFFFF;
    --line: #E7E0DB;
    --muted: #716A65;
    --soft: #F2EEEA;
}

html, body, [class*="css"], button, input, textarea, select {
    font-family: 'DM Sans', Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: var(--paper);
    color: var(--ink);
    font-size: 14px;
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

/* Header */

.topbar {
    background: var(--navy);
    color: var(--white);
    margin: -1rem -1rem 1.7rem -1rem;
    padding: 22px 24px 15px;
    border-bottom: 2px solid var(--red);
}

.brand {
    font-family: 'DM Sans', Arial, sans-serif !important;
    text-align: center;
    font-size: 25px;
    font-weight: 700;
    letter-spacing: -0.7px;
    color: #FFFFFF;
}

.brand .accent {
    color: #F04438;
}

.brand-tagline {
    text-align: center;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2px;
    color: #D0CFD7;
    text-transform: uppercase;
    margin-top: 5px;
}

.navrow {
    display: flex;
    justify-content: center;
    gap: 27px;
    flex-wrap: wrap;
    margin-top: 20px;
    color: #F4F3F5;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0;
}

.navitem {
    padding: 8px 0;
    border-bottom: 2px solid transparent;
}

.navitem.active {
    color: #FFFFFF;
    border-color: var(--red);
}

/* Main heading */

.eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--red);
    margin: 5px 0 12px;
}

.hero {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: clamp(32px, 3.4vw, 43px);
    font-weight: 700;
    font-style: normal !important;
    line-height: 1.18;
    letter-spacing: -1.4px;
    color: var(--red);
    margin: 10px 0 14px;
}

.subtitle {
    font-size: 15px;
    font-weight: 400;
    line-height: 1.75;
    color: #625B56;
    max-width: 900px;
    margin-bottom: 24px;
}

/* KPI cards */

.kpi-card {
    background: rgba(255,255,255,0.7);
    border: 1px solid var(--line);
    padding: 17px 18px;
    min-height: 104px;
    border-radius: 2px;
}

.kpi-value {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 28px;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: -0.7px;
    color: var(--red);
    overflow-wrap: anywhere;
}

.kpi-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
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
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 7px 12px;
    background: #FFFDFA;
    color: #5F5752;
    font-size: 12px;
    font-weight: 500;
}

.section-title {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 16px;
    font-weight: 700;
    color: #1B1918;
    border-top: 1px solid var(--line);
    padding-top: 18px;
    margin-top: 22px;
    margin-bottom: 12px;
}

.section-note {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    color: var(--muted);
    text-transform: uppercase;
}

/* Tabs */

.stTabs [data-baseweb="tab-list"] {
    gap: 25px;
    border-bottom: 1px solid var(--line);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
    border-radius: 0;
    padding: 12px 0;
    color: #5D5550;
}

.stTabs [aria-selected="true"] {
    color: var(--red) !important;
    border-bottom: 2px solid var(--red) !important;
}

/* Metrics */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.7);
    border: 1px solid var(--line);
    border-radius: 2px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    font-size: 12px;
    font-weight: 500;
}

div[data-testid="stMetricValue"] {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 27px;
    font-weight: 700;
    color: var(--red);
}

/* Buttons */

.stButton button, .stDownloadButton button {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 13px;
    font-weight: 600;
    border-radius: 22px;
    border: 1px solid var(--red);
    color: var(--red);
    background: transparent;
    transition: all 0.15s ease;
}

.stButton button:hover, .stDownloadButton button:hover {
    background: var(--red);
    color: #FFFFFF;
    border-color: var(--red);
}

/* Data tables and inputs */

div[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
}

div[data-testid="stFileUploader"] {
    border: 1px solid var(--line);
    padding: 10px;
    border-radius: 4px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] div,
div[data-testid="stMultiSelect"] div {
    font-family: 'DM Sans', Arial, sans-serif !important;
    font-size: 13px;
}

hr {
    border-color: var(--line);
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: var(--navy);
    border-right: 1px solid #272936;
}

section[data-testid="stSidebar"] * {
    font-family: 'DM Sans', Arial, sans-serif !important;
    color: #F5F3F5;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF;
    font-weight: 700;
}

section[data-testid="stSidebar"] hr {
    border-color: #343542;
}

section[data-testid="stSidebar"] input {
    color: #151515 !important;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #C7C3CB;
}

/* Footer */

.footer {
    text-align: center;
    color: #827A74;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.1px;
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
        letter-spacing: -0.8px;
    }

    .subtitle {
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

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

<div class="eyebrow">● LOCATION INTELLIGENCE / UNITED STATES</div>

<div class="hero">
    Find the right place to build.
</div>

<div class="subtitle">
    A unified intelligence workspace for renewable energy asset discovery,
    location screening and portfolio analysis. Explore Solar, Battery Energy
    Storage and Wind assets across the United States.
</div>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_repository_csv():
    return pd.read_csv("renewable_asset_register.csv")


with st.sidebar:
    st.markdown("## Sunstripe")
    st.caption("INTELLIGENCE PLATFORM")
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
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()
else:
    try:
        assets = load_repository_csv()
        data_message = "Repository CSV loaded successfully."
    except FileNotFoundError:
        st.error(
            "renewable_asset_register.csv was not found. Add it to the "
            "repository root or upload it using the sidebar."
        )
        st.stop()
    except Exception as exc:
        st.error(f"Could not load the repository CSV: {exc}")
        st.stop()


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

assets.columns = [
    str(column).strip().lower().replace(" ", "_")
    for column in assets.columns
]

aliases = {
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

for standard, alternatives in aliases.items():
    if standard not in assets.columns:
        for alternative in alternatives:
            if alternative in assets.columns:
                assets[standard] = assets[alternative]
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
    "technology_group", "plant_name", "state", "county", "lifecycle_group"
]:
    assets[column] = (
        assets[column].fillna("Unknown").astype(str).str.strip()
    )


def classify_technology(value):
    value = str(value).strip().lower()

    if any(word in value for word in ["solar", "photovoltaic"]):
        return "Solar"
    if value == "pv":
        return "Solar"
    if "wind" in value:
        return "Wind"
    if any(word in value for word in ["battery", "storage", "bess"]):
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
    technologies = sorted(
        assets["technology_display"].dropna().unique().tolist()
    )

    selected_technologies = st.multiselect(
        "Technology",
        options=technologies,
        default=technologies,
    )

    states = sorted(assets["state"].dropna().unique().tolist())

    selected_states = st.multiselect(
        "State",
        options=states,
        default=[],
        help="Leave empty to include all states.",
    )

    statuses = sorted(
        assets["lifecycle_group"].dropna().unique().tolist()
    )

    selected_statuses = st.multiselect(
        "Lifecycle / status",
        options=statuses,
        default=statuses,
    )

    min_capacity = max(
        0.0,
        float(assets["nameplate_capacity_mw"].min())
    )
    max_capacity = max(
        min_capacity,
        float(assets["nameplate_capacity_mw"].max())
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
    st.caption("SUNSTRIPE INTELLIGENCE")
    st.caption("Renewable energy asset screening")


# ============================================================
# APPLY FILTERS
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
# EXECUTIVE SUMMARY
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
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{total_records:,}</div>'
        f'<div class="kpi-label">Asset records in view</div></div>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{total_capacity:,.1f} MW</div>'
        f'<div class="kpi-label">Represented power capacity</div></div>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{total_storage:,.1f} MWh</div>'
        f'<div class="kpi-label">Represented storage energy</div></div>',
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{states_covered:,}</div>'
        f'<div class="kpi-label">States represented</div></div>',
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
# MAIN WORKSPACE
# ============================================================

tab_overview, tab_map, tab_register, tab_method = st.tabs([
    "Executive overview",
    "Location explorer",
    "Asset register",
    "Data & methodology",
])


# ============================================================
# OVERVIEW
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
                hole=0.60,
                title="Asset records by technology",
                color="Technology",
                color_discrete_map={
                    "Solar": "#D9A72E",
                    "Wind": "#41986A",
                    "BESS": "#3979CC",
                    "Other": "#A39B95",
                },
            )
            fig.update_layout(
                paper_bgcolor="#FBF9F7",
                plot_bgcolor="#FBF9F7",
                font_family="DM Sans",
                font_size=12,
                font_color="#282321",
                margin=dict(t=65, b=20, l=15, r=15),
                legend_title_text="",
            )
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
            )
            fig.update_traces(marker_color="#E8392D")
            fig.update_layout(
                paper_bgcolor="#FBF9F7",
                plot_bgcolor="#FBF9F7",
                font_family="DM Sans",
                font_size=12,
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
            title="Asset records by reported lifecycle status",
        )
        fig.update_traces(marker_color="#E8392D")
        fig.update_layout(
            paper_bgcolor="#FBF9F7",
            plot_bgcolor="#FBF9F7",
            font_family="DM Sans",
            font_size=12,
            font_color="#282321",
            xaxis_title="",
            yaxis_title="Asset records",
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# LOCATION EXPLORER
# ============================================================

with tab_map:
    st.markdown(
        '<div class="section-title">Geographic asset intelligence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Explore reported asset locations. Coordinates do not establish "
        "parcel boundaries or buildable land."
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
                "Solar": "#D9A72E",
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
            font_size=12,
            font_color="#282321",
        )

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning(
            "No valid coordinates were found. Check the latitude and "
            "longitude columns in your CSV."
        )


# ============================================================
# ASSET REGISTER
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
        "plant_name",
        "state",
        "county",
        "technology_group",
        "technology_display",
        "lifecycle_group",
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
# DATA & METHODOLOGY
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
    | `nameplate_energy_capacity_mwh` / `energy_capacity_mwh` | Energy capacity in MWh |
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
    - The platform analyzes the provided CSV and does not independently
      verify every asset record.
    - A point location is not a parcel boundary or buildable-area assessment.
    - MW is power capacity; MWh is energy capacity.
    - External sources listed here are references, not active data integrations.
    - Interconnection capacity, land ownership, permitting, environmental
      constraints, resource quality and market economics require additional
      verified datasets and dedicated analysis.
    """)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div class="footer">
    SUNSTRIPE INTELLIGENCE &nbsp; · &nbsp;
    ENERGY INFRASTRUCTURE &nbsp; · &nbsp;
    SOLAR / STORAGE / WIND
</div>
""", unsafe_allow_html=True)
