```python
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# SUNSTRIPE LOCATION INTELLIGENCE
# Solar | Wind | Battery Energy Storage Systems
# ============================================================

st.set_page_config(
    page_title="SunStripe Location Intelligence",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- THEME --------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F7F8;
        color: #182A36;
    }
    [data-testid="stSidebar"] {
        background-color: #102A36;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    .main-title {
        font-size: 34px;
        font-weight: 750;
        color: #102A36;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 15px;
        color: #60717D;
        margin-bottom: 24px;
    }
    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #E0E6E9;
    }
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #102A36;
        margin-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- LOAD DATA --------------------

@st.cache_data
def load_asset_data():
    # Requested CSV-loading code
    assets = pd.read_csv("renewable_asset_register.csv")
    return assets


def load_uploaded_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return None


# -------------------- HEADER --------------------

st.markdown(
    '<div class="main-title">SUNSTRIPE LOCATION INTELLIGENCE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Renewable energy asset discovery and site-screening platform | United States'
    '</div>',
    unsafe_allow_html=True,
)

# -------------------- DATA INPUT --------------------

try:
    assets = load_asset_data()
    data_loaded = True
    data_message = "Repository CSV loaded successfully."
except FileNotFoundError:
    assets = None
    data_loaded = False
    data_message = (
        "The file renewable_asset_register.csv was not found in the "
        "repository root. Upload it below or add it to the repository."
    )
except Exception as exc:
    assets = None
    data_loaded = False
    data_message = f"Could not load the repository CSV: {exc}"

with st.sidebar:
    st.markdown("## SUNSTRIPE")
    st.caption("LOCATION INTELLIGENCE")
    st.divider()

    st.markdown("### Data source")
    st.caption("Default: renewable_asset_register.csv")

    uploaded_file = st.file_uploader(
        "Or upload an asset register",
        type=["csv"],
        help="Upload a CSV with renewable energy asset information.",
    )

    if uploaded_file is not None:
        try:
            assets = load_uploaded_data(uploaded_file)
            data_loaded = True
            data_message = "Uploaded CSV loaded successfully."
        except Exception as exc:
            assets = None
            data_loaded = False
            data_message = f"Could not read uploaded CSV: {exc}"

if not data_loaded or assets is None:
    st.error(data_message)
    st.info(
        "Keep renewable_asset_register.csv in the same repository folder "
        "as app.py. Check that the filename matches exactly."
    )
    st.stop()

st.success(data_message)

# -------------------- NORMALIZE COLUMN NAMES --------------------

assets.columns = [
    str(column).strip().lower().replace(" ", "_")
    for column in assets.columns
]

# Support common alternative column names.
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

for standard_name, possible_names in column_aliases.items():
    if standard_name not in assets.columns:
        for alternative in possible_names:
            if alternative in assets.columns:
                assets[standard_name] = assets[alternative]
                break

# Create missing display columns so the app can handle different CSV schemas.
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

# Clean data types.
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
        assets[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )

# Normalize technology labels for consistent filtering.
def classify_technology(value):
    value = str(value).lower()

    if "solar" in value or "photovoltaic" in value or value == "pv":
        return "Solar"

    if "wind" in value:
        return "Wind"

    if (
        "battery" in value
        or "storage" in value
        or "bess" in value
    ):
        return "BESS"

    return "Other"


assets["technology_display"] = assets["technology_group"].apply(
    classify_technology
)

# Keep a row identifier for tables and downloads.
assets = assets.reset_index(drop=True)
assets["asset_record_id"] = assets.index + 1

# -------------------- SIDEBAR FILTERS --------------------

with st.sidebar:
    st.divider()
    st.markdown("### Asset filters")

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

# -------------------- APPLY FILTERS --------------------

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
        capacity_range[0],
        capacity_range[1],
    )
]

# -------------------- KPI METRICS --------------------

total_records = len(filtered_assets)
total_capacity = filtered_assets["nameplate_capacity_mw"].sum()
total_storage = filtered_assets["nameplate_energy_capacity_mwh"].sum()
states_covered = filtered_assets["state"].nunique()

solar_count = (
    filtered_assets["technology_display"] == "Solar"
).sum()
wind_count = (
    filtered_assets["technology_display"] == "Wind"
).sum()
bess_count = (
    filtered_assets["technology_display"] == "BESS"
).sum()

st.markdown("### National asset overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Asset records", f"{total_records:,}")
c2.metric("Nameplate capacity", f"{total_capacity:,.1f} MW")
c3.metric("Storage energy", f"{total_storage:,.1f} MWh")
c4.metric("States represented", f"{states_covered:,}")

st.caption(
    "Metrics reflect the current filters and the records in the loaded CSV. "
    "Asset records are not necessarily unique projects."
)

# -------------------- TECHNOLOGY SUMMARY --------------------

st.markdown(
    '<div class="section-title">Technology portfolio</div>',
    unsafe_allow_html=True,
)

t1, t2, t3 = st.columns(3)

t1.metric("Solar records", f"{solar_count:,}")
t2.metric("Wind records", f"{wind_count:,}")
t3.metric("BESS records", f"{bess_count:,}")

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
            hole=0.55,
            title="Asset records by technology",
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(t=60, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No records match the current filters.")

with right:
    state_capacity = (
        filtered_assets.groupby("state", as_index=False)[
            "nameplate_capacity_mw"
        ]
        .sum()
        .sort_values("nameplate_capacity_mw", ascending=False)
        .head(15)
    )

    if not state_capacity.empty:
        fig = px.bar(
            state_capacity,
            x="state",
            y="nameplate_capacity_mw",
            title="Top 15 states by recorded capacity",
            labels={
                "state": "State",
                "nameplate_capacity_mw": "Capacity (MW)",
            },
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(t=60, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No state capacity data is available.")

# -------------------- ASSET MAP --------------------

st.markdown(
    '<div class="section-title">Geographic asset intelligence</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Map markers show the coordinates available in the asset register. "
    "Plant-level coordinates are not parcel boundaries or buildable-area assessments."
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
        height=600,
        map_style="open-street-map",
        labels={
            "technology_display": "Technology",
            "nameplate_capacity_mw": "Capacity (MW)",
            "nameplate_energy_capacity_mwh": "Storage energy (MWh)",
            "lifecycle_group": "Lifecycle/status",
        },
    )
    fig_map.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning(
        "No valid latitude and longitude values are available for the "
        "selected records. The table below is still available."
    )

# -------------------- SEARCHABLE ASSET REGISTER --------------------

st.markdown(
    '<div class="section-title">Asset register</div>',
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

if search_term.strip():
    search_mask = filtered_assets[searchable_columns].apply(
        lambda column: column.astype(str).str.contains(
            search_term.strip(),
            case=False,
            na=False,
        )
    ).any(axis=1)

    filtered_assets = filtered_assets[search_mask]

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
    column
    for column in display_columns
    if column in filtered_assets.columns
]

st.dataframe(
    filtered_assets[display_columns],
    use_container_width=True,
    hide_index=True,
    height=450,
)

csv_data = filtered_assets.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered asset register (CSV)",
    data=csv_data,
    file_name="sunstripe_filtered_asset_register.csv",
    mime="text/csv",
)

# -------------------- LOCATION SCREENING DISCLAIMER --------------------

st.divider()
st.markdown("### Data and screening limitations")

st.write(
    """
    - This dashboard summarizes the data supplied in the CSV. It does not
      independently verify every asset or its operating status.
    - Generator-level records may represent multiple records at the same
      facility and should not be treated as unique development projects.
    - Plant coordinates do not establish parcel boundaries, land ownership,
      available acreage, interconnection feasibility or environmental
      suitability.
    - Nameplate capacity and storage energy are different measures. MW
      describes power capacity; MWh describes stored energy capacity.
    - Land prices, parcel acreage, transmission access, queue status,
      flood risk, wetlands, protected habitats, zoning and permitting need
      separate data sources and verification before investment decisions.
    """
)

st.caption("SUNSTRIPE | Renewable Energy Location Intelligence")
```
