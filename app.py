
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from io import StringIO

# ============================================================
# SUNSTRIPE LOCATION INTELLIGENCE
# Solar | Battery Energy Storage | Wind | Hybrid
# ============================================================

st.set_page_config(
    page_title="SunStripe Location Intelligence",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {
    background: rgba(128,128,128,0.08);
    border: 1px solid rgba(128,128,128,0.18);
    padding: 16px; border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌎 SunStripe Location Intelligence")
st.caption(
    "US renewable energy asset intelligence | Solar · BESS · Wind · Hybrid"
)

# ------------------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------------------

TECHNOLOGIES = ["Solar", "BESS", "Wind", "Hybrid"]

SCORE_COLUMNS = [
    "resource_score",
    "land_score",
    "grid_score",
    "environment_score",
    "market_score",
]

WEIGHTS = {
    "Solar": {
        "resource_score": 0.30,
        "land_score": 0.20,
        "grid_score": 0.25,
        "environment_score": 0.15,
        "market_score": 0.10,
    },
    "BESS": {
        "resource_score": 0.15,
        "land_score": 0.15,
        "grid_score": 0.30,
        "environment_score": 0.15,
        "market_score": 0.25,
    },
    "Wind": {
        "resource_score": 0.35,
        "land_score": 0.15,
        "grid_score": 0.20,
        "environment_score": 0.20,
        "market_score": 0.10,
    },
    "Hybrid": {
        "resource_score": 0.25,
        "land_score": 0.15,
        "grid_score": 0.25,
        "environment_score": 0.15,
        "market_score": 0.20,
    },
}

COLORS = {
    "Solar": [245, 185, 40, 210],
    "BESS": [40, 120, 240, 210],
    "Wind": [35, 165, 100, 210],
    "Hybrid": [155, 90, 210, 210],
}

# ------------------------------------------------------------
# 2. SAMPLE DATA
# Replace with a real asset dataset or upload your own CSV.
# All sample records below are illustrative, not real projects.
# ------------------------------------------------------------

SAMPLE_CSV = """asset_id,asset_name,technology,status,state,operator,capacity_mw,latitude,longitude,nearest_substation_km,resource_score,land_score,grid_score,environment_score,market_score,flood_risk,protected_area,interconnection_status
SOL-DEMO-01,Example Solar Texas,Solar,Operating,Texas,Demo Operator,250,31.20,-99.20,4.5,85,78,72,88,70,low,false,Unknown
BESS-DEMO-01,Example BESS Texas,BESS,Planned,Texas,Demo Storage,200,32.10,-97.80,2.1,60,82,88,90,92,low,false,Unknown
WIN-DEMO-01,Example Wind Iowa,Wind,Operating,Iowa,Demo Wind,300,42.00,-94.50,8.0,90,70,68,72,62,low,false,Unknown
HYB-DEMO-01,Example Hybrid New Mexico,Hybrid,Proposed,New Mexico,Demo Renewables,150,34.60,-106.00,6.0,82,75,80,86,78,unknown,false,Unknown
BESS-DEMO-02,Example BESS California,BESS,Proposed,California,Demo Storage,100,35.20,-119.10,3.0,55,65,78,85,95,high,false,Unknown
SOL-DEMO-02,Example Solar Georgia,Solar,Planned,Georgia,Demo Solar,180,32.70,-83.40,7.0,76,80,70,84,68,low,false,Unknown
WIN-DEMO-02,Example Wind Texas,Wind,Planned,Texas,Demo Wind,400,33.00,-101.00,10.0,88,75,65,78,80,low,false,Unknown
BESS-DEMO-03,Example BESS New York,BESS,Proposed,New York,Demo Storage,80,42.80,-75.00,5.0,55,72,75,90,84,low,false,Unknown
"""

# ------------------------------------------------------------
# 3. DATA VALIDATION
# ------------------------------------------------------------

REQUIRED_COLUMNS = [
    "asset_id",
    "asset_name",
    "technology",
    "capacity_mw",
    "latitude",
    "longitude",
    "state",
]

DEFAULTS = {
    "status": "Unknown",
    "operator": "Unknown",
    "nearest_substation_km": None,
    "resource_score": 50,
    "land_score": 50,
    "grid_score": 50,
    "environment_score": 50,
    "market_score": 50,
    "flood_risk": "unknown",
    "protected_area": False,
    "interconnection_status": "Unknown",
}


def load_assets(file):
    if file is None:
        df = pd.read_csv(StringIO(SAMPLE_CSV))
    else:
        df = pd.read_csv(file)

    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing required CSV columns: " + ", ".join(missing)
        )

    for col, default in DEFAULTS.items():
        if col not in df.columns:
            df[col] = default

    numeric_cols = [
        "capacity_mw",
        "latitude",
        "longitude",
        "nearest_substation_km",
        *SCORE_COLUMNS,
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["technology"] = (
        df["technology"].astype(str).str.strip().str.title()
    )

    df["flood_risk"] = (
        df["flood_risk"].fillna("unknown").astype(str).str.lower()
    )

    df["protected_area"] = (
        df["protected_area"]
        .fillna(False)
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes", "y"])
    )

    df = df.dropna(
        subset=["capacity_mw", "latitude", "longitude"]
    )

    df = df[
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & (df["capacity_mw"] >= 0)
        & df["technology"].isin(TECHNOLOGIES)
    ].copy()

    if df.empty:
        raise ValueError("No valid asset records found.")

    for col in SCORE_COLUMNS:
        df[col] = df[col].fillna(50).clip(0, 100)

    return df


# ------------------------------------------------------------
# 4. SCORING ENGINE
# ------------------------------------------------------------

def calculate_scores(df):
    df = df.copy()

    def score_asset(row):
        weights = WEIGHTS[row["technology"]]
        return round(
            sum(row[col] * weight for col, weight in weights.items()),
            1,
        )

    df["suitability_score"] = df.apply(score_asset, axis=1)

    def classify(row):
        # These are preliminary screening flags, not regulatory findings.
        if row["protected_area"]:
            return "Fatal Flaw - Review Required"

        if row["flood_risk"] == "high":
            return "High Risk - Review Required"

        if row["suitability_score"] >= 75:
            return "Higher Priority"

        if row["suitability_score"] >= 55:
            return "Conditional Review"

        return "Lower Priority"

    df["screening_status"] = df.apply(classify, axis=1)

    return df


# ------------------------------------------------------------
# 5. SIDEBAR
# ------------------------------------------------------------

st.sidebar.header("⚙️ Platform Controls")

uploaded_assets = st.sidebar.file_uploader(
    "Upload US asset register (CSV)",
    type=["csv"],
    help="Upload solar, BESS, wind and hybrid asset records.",
)

uploaded_grid = st.sidebar.file_uploader(
    "Upload grid/substation register (CSV)",
    type=["csv"],
    help="Required columns: name, latitude, longitude.",
)

try:
    assets = calculate_scores(load_assets(uploaded_assets))
except Exception as exc:
    st.error(f"Unable to load asset data: {exc}")
    st.info(
        "Required columns: asset_id, asset_name, technology, "
        "capacity_mw, latitude, longitude, state."
    )
    st.stop()

grid = pd.DataFrame()

if uploaded_grid is not None:
    try:
        grid = pd.read_csv(uploaded_grid)
        grid.columns = [str(c).strip().lower() for c in grid.columns]

        if not {"name", "latitude", "longitude"}.issubset(grid.columns):
            raise ValueError(
                "Grid CSV requires name, latitude and longitude."
            )

        grid["latitude"] = pd.to_numeric(grid["latitude"], errors="coerce")
        grid["longitude"] = pd.to_numeric(grid["longitude"], errors="coerce")
        grid = grid.dropna(subset=["latitude", "longitude"])
        grid = grid[
            grid["latitude"].between(-90, 90)
            & grid["longitude"].between(-180, 180)
        ]

    except Exception as exc:
        st.sidebar.error(f"Grid data error: {exc}")
        grid = pd.DataFrame()

st.sidebar.divider()
st.sidebar.subheader("Filter assets")

selected_tech = st.sidebar.multiselect(
    "Technology",
    TECHNOLOGIES,
    default=TECHNOLOGIES,
)

states = sorted(assets["state"].dropna().astype(str).unique())

selected_states = st.sidebar.multiselect(
    "State",
    states,
    default=states,
)

capacity_max = max(1, int(assets["capacity_mw"].max()))
capacity_range = st.sidebar.slider(
    "Capacity range (MW)",
    min_value=0,
    max_value=capacity_max,
    value=(0, capacity_max),
)

min_score = st.sidebar.slider(
    "Minimum suitability score",
    0,
    100,
    0,
)

risk_options = sorted(assets["screening_status"].unique())

selected_risks = st.sidebar.multiselect(
    "Screening classification",
    risk_options,
    default=risk_options,
)

st.sidebar.caption(
    "Scores depend on supplied data. Missing score inputs default to "
    "50 for demonstration and require validation."
)

# ------------------------------------------------------------
# 6. FILTERING
# ------------------------------------------------------------

filtered = assets[
    assets["technology"].isin(selected_tech)
    & assets["state"].astype(str).isin(selected_states)
    & assets["capacity_mw"].between(*capacity_range)
    & (assets["suitability_score"] >= min_score)
    & assets["screening_status"].isin(selected_risks)
].copy()

# ------------------------------------------------------------
# 7. KPI DASHBOARD
# ------------------------------------------------------------

st.subheader("Portfolio Overview")

total_assets = len(filtered)
total_mw = filtered["capacity_mw"].sum()
bess_mw = filtered.loc[
    filtered["technology"] == "BESS", "capacity_mw"
].sum()
solar_mw = filtered.loc[
    filtered["technology"] == "Solar", "capacity_mw"
].sum()
wind_mw = filtered.loc[
    filtered["technology"] == "Wind", "capacity_mw"
].sum()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Assets", f"{total_assets:,}")
k2.metric("Total Capacity", f"{total_mw:,.0f} MW")
k3.metric("Solar", f"{solar_mw:,.0f} MW")
k4.metric("BESS", f"{bess_mw:,.0f} MW")
k5.metric("Wind", f"{wind_mw:,.0f} MW")

if len(filtered):
    st.caption(
        f"Average suitability score: "
        f"{filtered['suitability_score'].mean():.1f}/100"
    )

st.divider()

# ------------------------------------------------------------
# 8. TABS
# ------------------------------------------------------------

tab_map, tab_register, tab_screen, tab_analytics, tab_data = st.tabs(
    [
        "🗺️ Asset Map",
        "📋 Asset Register",
        "🧭 Site Screening",
        "📊 Analytics",
        "📥 Data & Methodology",
    ]
)

# ------------------------------------------------------------
# 9. ASSET MAP
# ------------------------------------------------------------

with tab_map:
    st.subheader("Geospatial Asset Intelligence")

    if filtered.empty:
        st.info("No assets match the selected filters.")
    else:
        map_df = filtered.copy()

        map_df["marker_color"] = map_df["technology"].map(COLORS)

        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position="[longitude, latitude]",
                get_fill_color="marker_color",
                get_radius=4500,
                radius_min_pixels=4,
                radius_max_pixels=15,
                pickable=True,
                auto_highlight=True,
            )
        ]

        if not grid.empty:
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=grid,
                    get_position="[longitude, latitude]",
                    get_fill_color=[110, 110, 110, 200],
                    get_radius=2500,
                    radius_min_pixels=3,
                    radius_max_pixels=9,
                    pickable=True,
                )
            )

        view = pdk.ViewState(
            latitude=float(map_df["latitude"].mean()),
            longitude=float(map_df["longitude"].mean()),
            zoom=3,
            pitch=0,
        )

        tooltip = {
            "html": """
            <b>{asset_name}</b><br/>
            Technology: {technology}<br/>
            State: {state}<br/>
            Capacity: {capacity_mw} MW<br/>
            Score: {suitability_score}/100<br/>
            Status: {screening_status}
            """,
            "style": {
                "backgroundColor": "#172033",
                "color": "white",
            },
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view,
                tooltip=tooltip,
            ),
            use_container_width=True,
        )

        st.markdown(
            "**Legend:** 🟡 Solar · 🔵 BESS · 🟢 Wind · 🟣 Hybrid · "
            "⚫ Grid/substation records"
        )

        st.caption(
            "Grid markers represent supplied locations only. "
            "No interconnection capacity is inferred from proximity."
        )

# ------------------------------------------------------------
# 10. ASSET REGISTER
# ------------------------------------------------------------

with tab_register:
    st.subheader("Renewable Asset Register")

    if filtered.empty:
        st.info("No assets match the selected filters.")
    else:
        display_cols = [
            "asset_id",
            "asset_name",
            "technology",
            "status",
            "state",
            "operator",
            "capacity_mw",
            "nearest_substation_km",
            "suitability_score",
            "screening_status",
            "interconnection_status",
        ]

        st.dataframe(
            filtered[display_cols],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download filtered asset register",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="sunstripe_asset_register.csv",
            mime="text/csv",
        )

# ------------------------------------------------------------
# 11. SITE SCREENING
# ------------------------------------------------------------

with tab_screen:
    st.subheader("Site-Level Screening")

    if filtered.empty:
        st.info("Upload assets or change the filters.")
    else:
        selected_id = st.selectbox(
            "Select an asset",
            filtered["asset_id"].astype(str).tolist(),
            format_func=lambda x: (
                f"{x} — "
                f"{filtered.loc[filtered['asset_id'].astype(str).eq(x), 'asset_name'].iloc[0]}"
            ),
        )

        row = filtered[
            filtered["asset_id"].astype(str) == selected_id
        ].iloc[0]

        left, right = st.columns([1, 2])

        with left:
            st.markdown(f"### {row['asset_name']}")
            st.write(f"**Asset ID:** {row['asset_id']}")
            st.write(f"**Technology:** {row['technology']}")
            st.write(f"**State:** {row['state']}")
            st.write(f"**Operator:** {row['operator']}")
            st.write(f"**Capacity:** {row['capacity_mw']:,.1f} MW")

            distance = row["nearest_substation_km"]
            if pd.notna(distance):
                st.write(f"**Reported substation distance:** {distance} km")
            else:
                st.write("**Substation distance:** Not available")

            st.metric(
                "Suitability Score",
                f"{row['suitability_score']}/100",
            )

            st.write(f"**Screening:** {row['screening_status']}")
            st.write(f"**Flood risk field:** {row['flood_risk']}")
            st.write(
                "**Protected-area flag:** "
                + ("Yes" if row["protected_area"] else "No")
            )
            st.write(
                f"**Interconnection status:** "
                f"{row['interconnection_status']}"
            )

        with right:
            component_df = pd.DataFrame({
                "Dimension": [
                    "Resource",
                    "Land",
                    "Grid",
                    "Environment",
                    "Market",
                ],
                "Score": [
                    row[c] for c in SCORE_COLUMNS
                ],
            })

            fig = px.bar(
                component_df,
                x="Dimension",
                y="Score",
                range_y=[0, 100],
                text="Score",
                title="Site Screening Dimensions",
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        st.warning(
            "Preliminary screening only. A low-risk or high-scoring record "
            "does not establish land availability, interconnection feasibility, "
            "environmental clearance, permitting approval or bankability. "
            "An unflagged record may simply lack verified data."
        )

# ------------------------------------------------------------
# 12. ANALYTICS
# ------------------------------------------------------------

with tab_analytics:
    st.subheader("Portfolio Analytics")

    if filtered.empty:
        st.info("No data available for the current selection.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            tech_capacity = (
                filtered.groupby("technology", as_index=False)
                ["capacity_mw"].sum()
            )

            fig1 = px.bar(
                tech_capacity,
                x="technology",
                y="capacity_mw",
                color="technology",
                title="Installed / Planned Capacity by Technology",
                labels={
                    "technology": "Technology",
                    "capacity_mw": "Capacity (MW)",
                },
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            state_capacity = (
                filtered.groupby("state", as_index=False)
                ["capacity_mw"].sum()
                .sort_values("capacity_mw", ascending=False)
                .head(15)
            )

            fig2 = px.bar(
                state_capacity,
                x="state",
                y="capacity_mw",
                title="Top States by Represented Capacity",
                labels={
                    "state": "State",
                    "capacity_mw": "Capacity (MW)",
                },
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            fig3 = px.histogram(
                filtered,
                x="suitability_score",
                color="technology",
                nbins=10,
                title="Suitability Score Distribution",
                labels={"suitability_score": "Score"},
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            status_counts = (
                filtered.groupby("screening_status")
                .size()
                .reset_index(name="asset_count")
            )

            fig4 = px.pie(
                status_counts,
                names="screening_status",
                values="asset_count",
                title="Screening Classification",
                hole=0.4,
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Score Comparison")

        score_summary = (
            filtered.groupby("technology")[SCORE_COLUMNS]
            .mean()
            .round(1)
            .reset_index()
        )

        st.dataframe(
            score_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Charts describe the uploaded or sample dataset, not the "
            "entire US renewable energy market unless your data covers it."
        )

# ------------------------------------------------------------
# 13. DATA & METHODOLOGY
# ------------------------------------------------------------

with tab_data:
    st.subheader("Upload Data Requirements")

    st.markdown("""
    **Required asset CSV columns**

    | Column | Meaning |
    |---|---|
    | `asset_id` | Unique asset identifier |
    | `asset_name` | Project or facility name |
    | `technology` | Solar, BESS, Wind or Hybrid |
    | `capacity_mw` | Power capacity in MW |
    | `latitude` | Latitude in decimal degrees |
    | `longitude` | Longitude in decimal degrees |
    | `state` | US state |

    **Optional asset columns**

    `status`, `operator`, `nearest_substation_km`, `resource_score`,
    `land_score`, `grid_score`, `environment_score`, `market_score`,
    `flood_risk`, `protected_area`, `interconnection_status`.

    **Grid/substation CSV**

    Required: `name`, `latitude`, `longitude`.

    Optional: `voltage_kv`, `owner`, `status`.
    """)

    st.subheader("Scoring Weights")

    weight_rows = []
    for technology, weights in WEIGHTS.items():
        item = {"Technology": technology}
        item.update({
            col.replace("_score", "").title(): f"{weight:.0%}"
            for col, weight in weights.items()
        })
        weight_rows.append(item)

    st.dataframe(
        pd.DataFrame(weight_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Weights are configurable starting assumptions, not validated "
        "industry benchmarks. Scores are only meaningful when the underlying "
        "inputs have consistent definitions and reliable sources."
    )

    st.subheader("Recommended Data Sources for Production")

    st.markdown("""
    - **EIA:** Generator inventory and planned generation data.
    - **NREL:** Solar and wind resource datasets.
    - **USGS:** Elevation and terrain datasets.
    - **FEMA:** Flood hazard mapping.
    - **USFWS:** Wetlands and protected-species information.
    - **ISO/RTOs:** Market prices, queues, curtailment and grid information.
    - **Utilities and transmission owners:** Substations, lines and applicable grid studies.
    - **County and state authorities:** Parcels, zoning, land-use restrictions and permits.

    Availability, licensing, geographic coverage and update frequency vary
    by source. Integrations must preserve source, retrieval date and data quality.
    """)

    st.subheader("Important Limitations")

    st.markdown("""
    1. Sample assets are fictional.
    2. The current version does not retrieve live external datasets.
    3. Substation proximity does not establish available grid capacity.
    4. Flood and protected-area flags are only as reliable as uploaded inputs.
    5. BESS revenue, 2-hour/4-hour sizing and wind/solar yield are not calculated
       from real market or resource time series in this version.
    6. Screening results are not engineering, environmental, legal or investment advice.
    """)

# ------------------------------------------------------------
# 14. FOOTER
# ------------------------------------------------------------

st.divider()
st.caption(
    "SunStripe Location Intelligence | Solar + Storage + Wind | "
    "Preliminary development screening"
)
