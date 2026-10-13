
import json
import math
from datetime import date
from io import StringIO, BytesIO

import numpy as np
import numpy_financial as npf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st
from pyproj import Geod
from shapely.geometry import shape


# ============================================================
# SUNSTRIPE INTELLIGENCE
# US Renewable Energy Location Intelligence
# Solar | BESS | Wind | Hybrid
# ============================================================

st.set_page_config(
    page_title="SunStripe Intelligence",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAX_UPLOAD_MB = 25
GEOD = Geod(ellps="WGS84")
SQM_PER_ACRE = 4046.8564224

TECHNOLOGIES = [
    "Solar", "BESS", "Wind", "Solar + BESS", "Wind + BESS", "Hybrid"
]

WEIGHTS = {
    "Solar": {
        "resource_score": .30, "land_score": .20,
        "grid_score": .25, "environment_score": .15,
        "market_score": .10,
    },
    "BESS": {
        "resource_score": .15, "land_score": .15,
        "grid_score": .30, "environment_score": .15,
        "market_score": .25,
    },
    "Wind": {
        "resource_score": .35, "land_score": .15,
        "grid_score": .20, "environment_score": .20,
        "market_score": .10,
    },
    "Solar + BESS": {
        "resource_score": .25, "land_score": .15,
        "grid_score": .25, "environment_score": .15,
        "market_score": .20,
    },
    "Wind + BESS": {
        "resource_score": .30, "land_score": .15,
        "grid_score": .25, "environment_score": .15,
        "market_score": .15,
    },
    "Hybrid": {
        "resource_score": .25, "land_score": .15,
        "grid_score": .25, "environment_score": .15,
        "market_score": .20,
    },
}

COLORS = {
    "Solar": [235, 177, 45, 215],
    "BESS": [45, 115, 225, 215],
    "Wind": [40, 155, 100, 215],
    "Solar + BESS": [205, 110, 45, 215],
    "Wind + BESS": [105, 120, 185, 215],
    "Hybrid": [150, 85, 195, 215],
}

SCORE_COLUMNS = [
    "resource_score", "land_score", "grid_score",
    "environment_score", "market_score"
]

REQUIRED_ASSET_COLUMNS = [
    "asset_id", "asset_name", "technology",
    "capacity_mw", "latitude", "longitude", "state"
]

OPTIONAL_ASSET_DEFAULTS = {
    "status": "Unknown",
    "operator": "Unknown",
    "gross_acres": np.nan,
    "nearest_substation_km": np.nan,
    "resource_score": np.nan,
    "land_score": np.nan,
    "grid_score": np.nan,
    "environment_score": np.nan,
    "market_score": np.nan,
    "flood_risk": "Unknown",
    "protected_area": False,
    "interconnection_status": "Unknown",
    "iso_rto": "Unknown",
    "annual_mwh": np.nan,
    "source": "Not supplied",
    "source_date": "",
    "notes": "",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;1,500&display=swap');

:root {
    --ink:#080b18;
    --red:#e8392d;
    --paper:#fbf9f7;
    --line:#e8e1dc;
    --muted:#766f6a;
}
html, body, [class*="css"] {
    font-family:'DM Sans',sans-serif;
}
.stApp {
    background:var(--paper);
    color:var(--ink);
}
.block-container {
    max-width:1500px;
    padding-top:.8rem;
    padding-bottom:2rem;
}
header[data-testid="stHeader"] {
    background:transparent;
}
#MainMenu, footer {
    visibility:hidden;
}
.topbar {
    background:#050714;
    color:white;
    margin:-1rem -1rem 0 -1rem;
    padding:18px 28px;
    border-bottom:1px solid #292b37;
}
.brand {
    font-size:23px;
    font-weight:700;
    letter-spacing:-.8px;
    text-align:center;
    color:white;
}
.brand span {
    color:#ff5145;
}
.navrow {
    display:flex;
    justify-content:center;
    gap:25px;
    flex-wrap:wrap;
    color:#f5f3f1;
    font-size:12px;
    font-weight:600;
    margin-top:15px;
}
.navrow span {
    padding:6px 0;
    border-bottom:2px solid transparent;
}
.navrow .active {
    border-color:#e8392d;
}
.eyebrow {
    font-size:12px;
    letter-spacing:.08em;
    text-transform:uppercase;
    color:#e8392d;
    font-weight:700;
    margin-bottom:8px;
}
.hero {
    font-family:'Playfair Display',serif;
    font-size:43px;
    line-height:1.12;
    font-style:italic;
    color:#e8392d;
    letter-spacing:-1px;
    margin:18px 0 12px;
}
.subhero {
    color:#6f6762;
    font-size:14px;
    max-width:850px;
    margin-bottom:24px;
}
.kpi {
    border:1px solid var(--line);
    padding:16px 18px;
    background:rgba(255,255,255,.5);
    min-height:91px;
}
.kpi-num {
    font-family:'Playfair Display',serif;
    font-size:28px;
    line-height:1.15;
    color:#e8392d;
}
.kpi-label {
    font-size:12px;
    color:#655d58;
    margin-top:8px;
}
.strip {
    display:flex;
    flex-wrap:wrap;
    border:1px solid var(--line);
    margin:22px 0 14px;
    background:rgba(255,255,255,.4);
}
.strip-item {
    padding:13px 16px;
    flex:1;
    min-width:115px;
    border-right:1px solid var(--line);
}
.strip-num {
    font-family:'Playfair Display',serif;
    font-size:24px;
    color:#e8392d;
}
.strip-label {
    font-size:11px;
    color:#756d67;
    margin-top:3px;
}
.pills {
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    margin:10px 0 24px;
}
.pill {
    border:1px solid #e7dfda;
    border-radius:24px;
    padding:6px 12px;
    font-size:11px;
    color:#625a55;
    background:#fffdfa;
}
.section-head {
    border-top:1px solid var(--line);
    padding-top:18px;
    margin-top:12px;
    margin-bottom:14px;
}
.section-title {
    font-size:14px;
    font-weight:700;
    color:#282321;
}
div[data-testid="stMetric"] {
    background:rgba(255,255,255,.55);
    border:1px solid var(--line);
    padding:12px 15px;
    border-radius:2px;
}
div[data-testid="stMetricValue"] {
    font-family:'Playfair Display',serif;
    color:#e8392d;
}
.stTabs [data-baseweb="tab-list"] {
    gap:18px;
    border-bottom:1px solid var(--line);
}
.stTabs [data-baseweb="tab"] {
    background:transparent;
    border-radius:0;
    padding:10px 2px;
    color:#5d5550;
    font-size:12px;
}
.stTabs [aria-selected="true"] {
    color:#e8392d !important;
    border-bottom:2px solid #e8392d !important;
}
.stButton button {
    border-radius:20px;
    border:1px solid #e8392d;
    color:#e8392d;
    background:transparent;
}
.stButton button:hover {
    background:#e8392d;
    color:white;
    border-color:#e8392d;
}
div[data-testid="stDataFrame"] {
    border:1px solid var(--line);
}
hr {
    border-color:var(--line);
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA AND VALIDATION
# ============================================================

SAMPLE_ASSETS = """asset_id,asset_name,technology,status,state,operator,capacity_mw,latitude,longitude,gross_acres,nearest_substation_km,resource_score,land_score,grid_score,environment_score,market_score,flood_risk,protected_area,interconnection_status,iso_rto,annual_mwh,source,source_date,notes
DEMO-SOL-01,Illustrative Solar Candidate,Solar,Screening,Texas,Demo Only,200,31.2,-99.2,1400,8,75,65,60,80,70,Unknown,false,Unknown,ERCOT,,Synthetic demonstration record,,Not a real site
DEMO-BESS-01,Illustrative BESS Candidate,BESS,Screening,Texas,Demo Only,100,32.1,-97.8,20,3,50,70,80,75,75,Unknown,false,Unknown,ERCOT,,Synthetic demonstration record,,Not a real site
DEMO-WIND-01,Illustrative Wind Candidate,Wind,Screening,Iowa,Demo Only,300,42,-94.5,9000,12,80,70,60,70,65,Unknown,false,Unknown,MISO,,Synthetic demonstration record,,Not a real site
DEMO-HYB-01,Illustrative Hybrid Candidate,Hybrid,Screening,New Mexico,Demo Only,150,34.6,-106,1000,6,75,70,75,80,70,Unknown,false,Unknown,Other,,Synthetic demonstration record,,Not a real site
"""

def check_upload_size(upload):
    if upload is not None and upload.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(
            f"File exceeds the {MAX_UPLOAD_MB} MB upload limit."
        )

def canonical_technology(value):
    raw = str(value).strip().lower()
    mapping = {
        "solar": "Solar",
        "solar pv": "Solar",
        "bess": "BESS",
        "battery": "BESS",
        "battery storage": "BESS",
        "wind": "Wind",
        "solar + bess": "Solar + BESS",
        "solar+bess": "Solar + BESS",
        "solar plus storage": "Solar + BESS",
        "wind + bess": "Wind + BESS",
        "wind+bess": "Wind + BESS",
        "wind plus storage": "Wind + BESS",
        "hybrid": "Hybrid",
    }
    return mapping.get(raw, str(value).strip())

def load_assets(upload):
    check_upload_size(upload)
    if upload is None:
        df = pd.read_csv(StringIO(SAMPLE_ASSETS))
    else:
        df = pd.read_csv(upload)

    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED_ASSET_COLUMNS if c not in df]
    if missing:
        raise ValueError(
            "Asset CSV is missing required columns: " + ", ".join(missing)
        )

    for col, default in OPTIONAL_ASSET_DEFAULTS.items():
        if col not in df:
            df[col] = default

    num_cols = [
        "capacity_mw", "latitude", "longitude", "gross_acres",
        "nearest_substation_km", *SCORE_COLUMNS, "annual_mwh"
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["technology"] = df["technology"].map(canonical_technology)
    df["protected_area"] = (
        df["protected_area"].fillna(False).astype(str).str.lower()
        .isin(["true", "1", "yes", "y"])
    )
    df["flood_risk"] = (
        df["flood_risk"].fillna("unknown").astype(str).str.lower()
    )

    df = df.dropna(
        subset=["asset_id", "asset_name", "capacity_mw", "latitude", "longitude"]
    ).copy()

    df = df[
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & (df["capacity_mw"] >= 0)
        & df["technology"].isin(TECHNOLOGIES)
    ].copy()

    if df.empty:
        raise ValueError("No valid asset rows remain after validation.")

    # Track incomplete evidence rather than treating missing values as verified.
    df["missing_score_count"] = df[SCORE_COLUMNS].isna().sum(axis=1)

    # Neutral score is a placeholder for sorting only.
    for col in SCORE_COLUMNS:
        df[col] = df[col].fillna(50).clip(0, 100)

    if df["source"].eq("Not supplied").all() and upload is not None:
        df["source"] = "User upload; source not documented"

    return df

def calculate_suitability(df):
    df = df.copy()
    df["suitability_score"] = df.apply(
        lambda r: round(
            sum(r[c] * w for c, w in WEIGHTS[r["technology"]].items()), 1
        ),
        axis=1,
    )

    def classification(r):
        if r["protected_area"]:
            return "High-risk review"
        if r["flood_risk"] == "high":
            return "High-risk review"
        if r["missing_score_count"] >= 3:
            return "Insufficient data"
        if r["suitability_score"] >= 75:
            return "Priority candidate"
        if r["suitability_score"] >= 60:
            return "Promising, subject to diligence"
        if r["suitability_score"] >= 45:
            return "Further investigation"
        return "High-risk candidate"

    df["screening_status"] = df.apply(classification, axis=1)

    def confidence(r):
        if r["missing_score_count"] >= 4:
            return "Low"
        if r["missing_score_count"] >= 2:
            return "Medium-low"
        if r["missing_score_count"] == 1:
            return "Medium"
        return "Input scores complete; source verification required"

    df["data_confidence"] = df.apply(confidence, axis=1)
    return df


# ============================================================
# SPATIAL FUNCTIONS
# ============================================================

def geojson_acres(geojson_obj):
    """Geodesic acreage for Polygon/MultiPolygon features in WGS84 GeoJSON."""
    if not isinstance(geojson_obj, dict):
        raise ValueError("GeoJSON must be a JSON object.")

    if geojson_obj.get("type") == "FeatureCollection":
        features = geojson_obj.get("features", [])
    elif geojson_obj.get("type") == "Feature":
        features = [geojson_obj]
    else:
        features = [{
            "type": "Feature",
            "geometry": geojson_obj,
            "properties": {},
        }]

    total = 0.0
    included = 0

    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue

        geom = shape(geometry)
        if geom.geom_type not in ("Polygon", "MultiPolygon"):
            continue

        area_m2, _ = GEOD.geometry_area_perimeter(geom)
        total += abs(area_m2)
        included += 1

    if included == 0:
        raise ValueError("No Polygon or MultiPolygon geometry was found.")

    return total / SQM_PER_ACRE, included

def nearest_point_distance_km(latitude, longitude, grid):
    """Geodesic point-to-point proximity. Does not calculate line routing."""
    if grid.empty:
        return None, None

    valid = grid.dropna(subset=["latitude", "longitude"]).copy()
    if valid.empty:
        return None, None

    _, _, distances = GEOD.inv(
        np.full(len(valid), float(longitude)),
        np.full(len(valid), float(latitude)),
        valid["longitude"].astype(float).to_numpy(),
        valid["latitude"].astype(float).to_numpy(),
    )
    idx = int(np.argmin(distances))
    return (
        float(distances[idx] / 1000),
        str(valid.iloc[idx].get("name", "Unnamed grid feature"))
    )


# ============================================================
# LAND COMPARABLES
# ============================================================

COMPS_REQUIRED = [
    "state", "acres", "property_price", "sale_date", "transaction_type"
]

def load_comparables(upload):
    if upload is None:
        return pd.DataFrame()

    check_upload_size(upload)
    df = pd.read_csv(upload)
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in COMPS_REQUIRED if c not in df]
    if missing:
        raise ValueError(
            "Comparable CSV is missing columns: " + ", ".join(missing)
        )

    if "source" not in df:
        df["source"] = "Not supplied"
    if "source_url" not in df:
        df["source_url"] = ""
    if "land_use" not in df:
        df["land_use"] = "Unknown"

    df["acres"] = pd.to_numeric(df["acres"], errors="coerce")
    df["property_price"] = pd.to_numeric(df["property_price"], errors="coerce")
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["transaction_type"] = (
        df["transaction_type"].astype(str).str.strip().str.lower()
    )
    df["state"] = df["state"].astype(str).str.strip().str.lower()

    df = df[
        (df["acres"] > 0)
        & (df["property_price"] > 0)
        & df["sale_date"].notna()
    ].copy()

    df["price_per_acre"] = df["property_price"] / df["acres"]
    return df

def screen_comparables(
    comps, state, acres, transaction_type, max_age_years
):
    if comps.empty:
        return comps.copy()

    cut_date = pd.Timestamp(date.today()) - pd.Timedelta(
        days=int(365.25 * max_age_years)
    )
    out = comps[
        (comps["state"] == str(state).strip().lower())
        & (comps["sale_date"] >= cut_date)
        & (comps["transaction_type"] == transaction_type.lower())
    ].copy()

    # Broad acreage comparability filter. Can be disabled when target area is unknown.
    if acres and acres > 0:
        out = out[
            out["acres"].between(max(0.1, acres / 4), acres * 4)
        ].copy()

    return out.sort_values("sale_date", ascending=False)

def valuation_confidence(comps):
    if comps.empty:
        return "Insufficient data"

    count = len(comps)
    median_age_days = (
        pd.Timestamp(date.today()) - comps["sale_date"].median()
    ).days

    if count >= 8 and median_age_days <= 730:
        return "Higher screening confidence"
    if count >= 4 and median_age_days <= 1461:
        return "Medium screening confidence"
    return "Low screening confidence"


# ============================================================
# LEASE, LAND AND PROJECT FINANCIAL FUNCTIONS
# ============================================================

def lease_schedule(acres, annual_rent_per_acre, escalation_pct,
                   discount_rate_pct, term_years):
    rate = annual_rent_per_acre
    escalation = escalation_pct / 100
    discount = discount_rate_pct / 100
    rows = []
    pv = 0.0

    for year in range(1, int(term_years) + 1):
        annual_rent = acres * rate * ((1 + escalation) ** (year - 1))
        discounted = annual_rent / ((1 + discount) ** year)
        pv += discounted
        rows.append({
            "Year": year,
            "Annual lease payment ($)": annual_rent,
            "Discounted payment ($)": discounted,
        })

    return pd.DataFrame(rows), pv

def calculate_npv_irr(capex, annual_net_cashflow, life, discount_rate):
    cashflows = [-float(capex)] + [
        float(annual_net_cashflow)
    ] * int(life)

    npv = float(npf.npv(discount_rate, cashflows))
    try:
        irr = float(npf.irr(cashflows))
        if not np.isfinite(irr):
            irr = np.nan
    except Exception:
        irr = np.nan

    if annual_net_cashflow > 0:
        payback = capex / annual_net_cashflow
    else:
        payback = np.nan

    return npv, irr, payback

def maximum_land_price(non_land_capex, annual_net_cashflow,
                       life_years, target_irr_pct):
    rate = target_irr_pct / 100
    if rate <= -1:
        return np.nan

    pv_cashflow = sum(
        annual_net_cashflow / ((1 + rate) ** year)
        for year in range(1, int(life_years) + 1)
    )
    return pv_cashflow - non_land_capex


# ============================================================
# BESS PRICE SERIES
# ============================================================

def load_lmp(upload):
    if upload is None:
        return pd.DataFrame()

    check_upload_size(upload)
    df = pd.read_csv(upload)
    df.columns = [str(c).strip().lower() for c in df.columns]

    time_col = next(
        (c for c in ["timestamp", "datetime", "date_time", "time", "interval_start"]
         if c in df.columns),
        None
    )
    price_col = next(
        (c for c in ["lmp", "price", "price_usd_mwh", "dam_lmp", "rt_lmp"]
         if c in df.columns),
        None
    )

    if time_col is None or price_col is None:
        raise ValueError(
            "LMP CSV must contain a timestamp/datetime column and an "
            "LMP/price column."
        )

    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df[time_col], errors="coerce", utc=True),
        "lmp": pd.to_numeric(df[price_col], errors="coerce"),
    })
    out = out.dropna().sort_values("timestamp")

    if out.empty:
        raise ValueError("No valid time and price observations found.")

    return out

def bess_daily_spread_proxy(lmp_df, power_mw, duration_hours, rte_pct):
    """
    Indicative one-cycle daily block comparison.
    Uses contiguous charge and later discharge blocks each day.
    This is not a market-grade dispatch optimizer.
    """
    if lmp_df.empty:
        return pd.DataFrame()

    hourly = (
        lmp_df.set_index("timestamp")["lmp"]
        .resample("1h").mean().dropna()
    )
    duration = int(duration_hours)
    rte = rte_pct / 100
    rows = []

    for day, series in hourly.groupby(hourly.index.date):
        values = series.to_numpy(dtype=float)
        times = series.index

        if len(values) < 2 * duration:
            continue

        best_profit = None
        best_charge = None
        best_discharge = None

        for charge_start in range(0, len(values) - duration + 1):
            charge_end = charge_start + duration
            charge_price = float(
                values[charge_start:charge_end].mean()
            )

            for discharge_start in range(
                charge_end, len(values) - duration + 1
            ):
                discharge_end = discharge_start + duration
                discharge_price = float(
                    values[discharge_start:discharge_end].mean()
                )

                delivered_mwh = power_mw * duration
                charge_cost = (
                    delivered_mwh * charge_price / rte
                )
                discharge_revenue = (
                    delivered_mwh * discharge_price
                )
                profit = discharge_revenue - charge_cost

                if best_profit is None or profit > best_profit:
                    best_profit = profit
                    best_charge = charge_price
                    best_discharge = discharge_price

        if best_profit is not None:
            rows.append({
                "date": str(day),
                "best_charge_block_avg_lmp": best_charge,
                "best_later_discharge_block_avg_lmp": best_discharge,
                "estimated_gross_margin_proxy_usd": best_profit,
            })

    return pd.DataFrame(rows)


# ============================================================
# SIDEBAR: INPUTS AND FILTERS
# ============================================================

st.markdown("""
<div class="topbar">
    <div class="brand">Sunstripe <span>Intelligence</span></div>
    <div class="navrow">
        <span class="active">OVERVIEW</span>
        <span>LAND</span>
        <span>SOLAR</span>
        <span>STORAGE</span>
        <span>WIND</span>
        <span>GRID</span>
        <span>MARKETS</span>
        <span>ECONOMICS</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔴 SunStripe")
    st.caption("LOCATION INTELLIGENCE PLATFORM")
    st.divider()

    st.markdown("**Upload data**")
    assets_file = st.file_uploader(
        "Renewable asset register (CSV)", type=["csv"], key="assets_csv"
    )
    grid_file = st.file_uploader(
        "Substations / grid points (CSV)", type=["csv"], key="grid_csv"
    )
    comps_file = st.file_uploader(
        "Land comparables (CSV)", type=["csv"], key="comps_csv"
    )
    lmp_file = st.file_uploader(
        "Historical power prices / LMP (CSV)", type=["csv"], key="lmp_csv"
    )
    boundary_file = st.file_uploader(
        "Candidate-site boundary (GeoJSON)", type=["json", "geojson"],
        key="site_geojson"
    )

    st.divider()
    st.markdown("**Portfolio filters**")

try:
    assets = calculate_suitability(load_assets(assets_file))
except Exception as exc:
    st.error(f"Asset data error: {exc}")
    st.stop()

try:
    comps = load_comparables(comps_file)
except Exception as exc:
    st.sidebar.error(f"Comparable data error: {exc}")
    comps = pd.DataFrame()

try:
    lmp_df = load_lmp(lmp_file)
except Exception as exc:
    st.sidebar.error(f"LMP data error: {exc}")
    lmp_df = pd.DataFrame()

grid = pd.DataFrame()
if grid_file is not None:
    try:
        check_upload_size(grid_file)
        grid = pd.read_csv(grid_file)
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

with st.sidebar:
    tech_filter = st.multiselect(
        "Technology", TECHNOLOGIES, default=TECHNOLOGIES
    )
    state_options = sorted(assets["state"].dropna().astype(str).unique())
    state_filter = st.multiselect(
        "State", state_options, default=state_options
    )
    max_capacity = max(1, int(math.ceil(assets["capacity_mw"].max())))
    capacity_filter = st.slider(
        "Capacity range (MW)",
        0, max_capacity, (0, max_capacity)
    )
    min_suitability = st.slider(
        "Minimum screening score", 0, 100, 0
    )

filtered = assets[
    assets["technology"].isin(tech_filter)
    & assets["state"].astype(str).isin(state_filter)
    & assets["capacity_mw"].between(*capacity_filter)
    & (assets["suitability_score"] >= min_suitability)
].copy()

selected_id = None
if not filtered.empty:
    with st.sidebar:
        selected_id = st.selectbox(
            "Active candidate",
            filtered["asset_id"].astype(str).tolist(),
            format_func=lambda x: (
                f"{x} — "
                f"{filtered.loc[filtered['asset_id'].astype(str).eq(x), 'asset_name'].iloc[0]}"
            ),
            key="active_candidate",
        )

active = None
if selected_id is not None:
    active = filtered[
        filtered["asset_id"].astype(str) == str(selected_id)
    ].iloc[0]


# ============================================================
# EXECUTIVE HEADER
# ============================================================

st.markdown(
    '<div class="eyebrow">● SUNSTRIPE PULSE / US LOCATION INTELLIGENCE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero">Find the next right place<br>to build.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subhero">A renewable energy development workspace for '
    'land affordability, GIS screening, grid context, renewable resources '
    'and preliminary project economics. Every output should be interpreted '
    'alongside its data source and confidence.</div>',
    unsafe_allow_html=True,
)

if assets_file is None:
    st.info(
        "Demo mode: the visible asset records are synthetic examples, "
        "not real projects or investment opportunities."
    )

capacity_total = filtered["capacity_mw"].sum() if len(filtered) else 0
bess_count = int(
    filtered["technology"].isin(["BESS", "Solar + BESS", "Wind + BESS", "Hybrid"]).sum()
)
priority_count = int(
    filtered["screening_status"].eq("Priority candidate").sum()
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{len(filtered):,}</div>'
        '<div class="kpi-label">Candidate records in view</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{capacity_total:,.0f} MW</div>'
        '<div class="kpi-label">Represented capacity</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{priority_count:,}</div>'
        '<div class="kpi-label">Priority-screen candidates</div></div>',
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{bess_count:,}</div>'
        '<div class="kpi-label">Storage / hybrid records</div></div>',
        unsafe_allow_html=True,
    )

type_counts = filtered["technology"].value_counts()
pill_html = "".join(
    f'<span class="pill">{t}: {int(type_counts.get(t, 0))}</span>'
    for t in TECHNOLOGIES
)
st.markdown(f'<div class="pills">{pill_html}</div>', unsafe_allow_html=True)

# Tabs keep this version in one app.py.
tabs = st.tabs([
    "Executive dashboard",
    "US location explorer",
    "Land intelligence",
    "Solar screening",
    "BESS intelligence",
    "Wind & hybrid",
    "Grid & environment",
    "Project economics",
    "Portfolio comparison",
    "Data & methodology",
])


# ============================================================
# TAB 1: EXECUTIVE DASHBOARD
# ============================================================

with tabs[0]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Portfolio pulse</div></div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.warning("No assets match the selected filters.")
    else:
        left, right = st.columns(2)

        with left:
            mix = (
                filtered.groupby("technology", as_index=False)
                ["capacity_mw"].sum()
            )
            fig = px.bar(
                mix, x="technology", y="capacity_mw",
                color="technology", title="Represented capacity by technology",
            )
            fig.update_layout(
                plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
                font_family="DM Sans", legend_title_text="Technology",
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            state_mix = (
                filtered.groupby("state", as_index=False)
                ["capacity_mw"].sum()
                .sort_values("capacity_mw", ascending=False)
                .head(12)
            )
            fig = px.bar(
                state_mix, x="state", y="capacity_mw",
                title="States by represented capacity",
            )
            fig.update_traces(marker_color="#e8392d")
            fig.update_layout(
                plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
                font_family="DM Sans",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Highest-ranked records in the current dataset**")
        rank_cols = [
            "asset_name", "technology", "state", "capacity_mw",
            "suitability_score", "screening_status", "data_confidence",
            "source", "source_date",
        ]
        st.dataframe(
            filtered.sort_values("suitability_score", ascending=False)[rank_cols].head(20),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Rankings reflect supplied inputs and configured weights. "
            "They are not verified investment recommendations."
        )


# ============================================================
# TAB 2: US LOCATION EXPLORER
# ============================================================

with tabs[1]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Geospatial site explorer</div></div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No matching assets to map.")
    else:
        map_data = filtered.copy()
        map_data["marker_color"] = map_data["technology"].map(COLORS)

        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
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
                    get_fill_color=[70, 70, 78, 205],
                    get_radius=2500,
                    radius_min_pixels=3,
                    pickable=True,
                )
            )

        geojson_obj = None
        boundary_acres = None
        if boundary_file is not None:
            try:
                boundary_file.seek(0)
                geojson_obj = json.load(boundary_file)
                boundary_acres, polygon_count = geojson_acres(geojson_obj)

                layers.append(
                    pdk.Layer(
                        "GeoJsonLayer",
                        data=geojson_obj,
                        stroked=True,
                        filled=True,
                        get_fill_color=[232, 57, 45, 35],
                        get_line_color=[232, 57, 45, 230],
                        line_width_min_pixels=2,
                        pickable=True,
                    )
                )
                st.success(
                    f"Uploaded boundary: {boundary_acres:,.2f} geodesic acres "
                    f"across {polygon_count} polygon feature(s)."
                )
            except Exception as exc:
                st.warning(f"Boundary could not be processed: {exc}")

        if active is not None:
            center_lat = float(active["latitude"])
            center_lon = float(active["longitude"])
            zoom = 7
        else:
            center_lat = float(map_data["latitude"].median())
            center_lon = float(map_data["longitude"].median())
            zoom = 3

        view = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=zoom,
            pitch=0,
        )

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view,
                tooltip={
                    "html": (
                        "<b>{asset_name}</b><br/>"
                        "Technology: {technology}<br/>"
                        "State: {state}<br/>"
                        "Capacity: {capacity_mw} MW<br/>"
                        "Score: {suitability_score}<br/>"
                        "Status: {screening_status}"
                    ),
                    "style": {
                        "backgroundColor": "#080b18",
                        "color": "white",
                    },
                },
            ),
            use_container_width=True,
        )

        st.caption(
            "Solar = gold | BESS = blue | Wind = green | Hybrid = purple | "
            "Grid records = charcoal. Points represent uploaded coordinates; "
            "a basemap or a nearby point does not establish interconnection feasibility."
        )

        if active is not None:
            st.markdown("**Active site coordinates**")
            st.write(
                f"Latitude: {active['latitude']:.6f} | "
                f"Longitude: {active['longitude']:.6f}"
            )

        if boundary_acres is not None:
            st.metric("Gross boundary acreage", f"{boundary_acres:,.2f} acres")
            st.caption(
                "Geodesic acreage from the supplied WGS84 GeoJSON geometry. "
                "Overlapping features can be double-counted; check topology "
                "before using multipart uploads for valuation."
            )


# ============================================================
# TAB 3: LAND INTELLIGENCE
# ============================================================

with tabs[2]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Land valuation & affordability</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "This module estimates land indicators only when comparable records "
        "are supplied. Asking prices, assessed values, recorded sales and "
        "renewable lease rates must remain separate data categories."
    )

    if active is None:
        st.info("Select an asset in the sidebar to evaluate its land assumptions.")
    else:
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            asset_acres = active.get("gross_acres", np.nan)
            default_acres = (
                float(asset_acres)
                if pd.notna(asset_acres) and asset_acres > 0
                else 0.0
            )
            gross_acres = st.number_input(
                "Gross parcel / site acreage",
                min_value=0.0,
                value=default_acres,
                step=10.0,
                help="Enter verified parcel area or use the calculated GeoJSON area.",
            )
        with lc2:
            exclusion_pct = st.slider(
                "Estimated constrained area (%)",
                min_value=0, max_value=100, value=15,
                help="User assumption until official spatial overlays calculate actual overlap.",
            )
        with lc3:
            max_age = st.slider(
                "Comparable age limit (years)",
                min_value=1, max_value=15, value=5,
            )

        if boundary_file is not None:
            try:
                boundary_file.seek(0)
                boundary_for_area = json.load(boundary_file)
                auto_acres, _ = geojson_acres(boundary_for_area)
                if st.button("Use uploaded GeoJSON acreage"):
                    st.session_state["gross_acres_override"] = auto_acres
                    st.rerun()
                if "gross_acres_override" in st.session_state:
                    gross_acres = float(st.session_state["gross_acres_override"])
            except Exception:
                pass

        usable_acres = gross_acres * (1 - exclusion_pct / 100)
        excluded_acres = gross_acres - usable_acres

        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("Gross acres", f"{gross_acres:,.2f}")
        ac2.metric("Estimated usable acres", f"{usable_acres:,.2f}")
        ac3.metric("Excluded-area assumption", f"{excluded_acres:,.2f}")

        st.divider()

        transaction_choice = st.selectbox(
            "Comparable record type",
            ["sale", "listing", "lease"],
            format_func=lambda x: {
                "sale": "Recorded property sales",
                "listing": "Listing / asking prices",
                "lease": "Land lease comparables",
            }[x],
        )

        eligible = screen_comparables(
            comps,
            state=active["state"],
            acres=gross_acres,
            transaction_type=transaction_choice,
            max_age_years=max_age,
        )

        if eligible.empty:
            st.warning(
                "Insufficient data for a reliable land valuation. Upload "
                "verified comparable records for the same state and record "
                "type. No property price is being invented."
            )
        else:
            ppa = eligible["price_per_acre"].dropna()
            if ppa.empty:
                st.warning("Comparable records contain no valid prices per acre.")
            else:
                low_ppa = float(ppa.quantile(.25))
                base_ppa = float(ppa.median())
                high_ppa = float(ppa.quantile(.75))
                confidence = valuation_confidence(eligible)

                v1, v2, v3, v4 = st.columns(4)
                v1.metric("Comparable records", f"{len(eligible)}")
                v2.metric("Median price per acre", f"${base_ppa:,.0f}")
                v3.metric("25th percentile / acre", f"${low_ppa:,.0f}")
                v4.metric("75th percentile / acre", f"${high_ppa:,.0f}")

                st.write(f"**Screening confidence:** {confidence}")
                st.write(
                    f"**Comparable period:** {eligible['sale_date'].min().date()} "
                    f"to {eligible['sale_date'].max().date()}"
                )
                st.write(
                    f"**Median transaction age:** "
                    f"{(pd.Timestamp(date.today()) - eligible['sale_date'].median()).days} days"
                )

                if gross_acres > 0:
                    low_val = low_ppa * gross_acres
                    base_val = base_ppa * gross_acres
                    high_val = high_ppa * gross_acres

                    st.markdown("#### Indicative land value range")
                    val_cols = st.columns(3)
                    val_cols[0].metric("Low indication", f"${low_val:,.0f}")
                    val_cols[1].metric("Base indication", f"${base_val:,.0f}")
                    val_cols[2].metric("High indication", f"${high_val:,.0f}")

                    st.caption(
                        "These are percentiles from selected comparables multiplied "
                        "by gross acres. They are not a formal appraisal and do not "
                        "include parcel-specific adjustments for zoning, access, "
                        "terrain, grid, environmental features or transaction terms."
                    )

                    asking = st.number_input(
                        "Landowner asking price ($; optional)",
                        min_value=0.0,
                        value=0.0,
                        step=100000.0,
                    )

                    if asking > 0:
                        ask_ppa = asking / gross_acres
                        delta_pct = (
                            (ask_ppa / base_ppa) - 1
                        ) * 100 if base_ppa else np.nan

                        q1, q2, q3 = st.columns(3)
                        q1.metric("Asking price per acre", f"${ask_ppa:,.0f}")
                        q2.metric("Premium / discount vs median", f"{delta_pct:+.1f}%")
                        q3.metric("Asking price / base indication", f"${asking-base_val:,.0f}")

                        if delta_pct > 0:
                            st.warning(
                                "The asking price is above the comparable median "
                                "on a per-acre basis. This does not prove overvaluation."
                            )
                        else:
                            st.info(
                                "The asking price is at or below the comparable median "
                                "on a per-acre basis. This alone does not establish a good investment."
                            )

                    candidate_tech = st.selectbox(
                        "Technology for preliminary land fit",
                        TECHNOLOGIES,
                        index=TECHNOLOGIES.index(active["technology"]),
                    )

                    st.markdown("#### Land-use capacity scenario")
                    if candidate_tech == "Solar":
                        acres_per_mw = st.number_input(
                            "Assumed acres per MWdc", 1.0, 30.0, 7.0, .5
                        )
                    elif candidate_tech == "BESS":
                        acres_per_mw = st.number_input(
                            "Assumed site acres per MW", .05, 10.0, .5, .05
                        )
                    elif candidate_tech == "Wind":
                        acres_per_mw = st.number_input(
                            "Assumed controlled acres per MW", 1.0, 150.0, 30.0, 1.0
                        )
                    else:
                        acres_per_mw = st.number_input(
                            "Assumed site acres per MW", .5, 50.0, 8.0, .5
                        )

                    estimated_mw = usable_acres / acres_per_mw if acres_per_mw > 0 else 0
                    st.metric(
                        "Indicative land-supported capacity",
                        f"{estimated_mw:,.1f} MW",
                    )
                    st.caption(
                        "User-configurable screening assumption. It is not a layout, "
                        "permit, interconnection, turbine-spacing or engineering result."
                    )

                    price_for_cost = asking if asking > 0 else base_val
                    if estimated_mw > 0:
                        st.metric(
                            "Land cost per indicative MW",
                            f"${price_for_cost / estimated_mw:,.0f}/MW",
                        )

                st.markdown("#### Selected comparable records")
                show_cols = [
                    c for c in [
                        "state", "acres", "property_price", "price_per_acre",
                        "sale_date", "transaction_type", "land_use",
                        "source", "source_url"
                    ] if c in eligible.columns
                ]
                st.dataframe(
                    eligible[show_cols],
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "Download screened comparables",
                    eligible.to_csv(index=False).encode("utf-8"),
                    "sunstripe_screened_comparables.csv",
                    "text/csv",
                )

        st.divider()
        st.markdown("#### Lease economics")
        le1, le2, le3, le4 = st.columns(4)
        with le1:
            lease_rate = st.number_input(
                "Annual lease rate ($/acre/year)",
                min_value=0.0, value=0.0, step=25.0,
            )
        with le2:
            escalation = st.number_input(
                "Annual rent escalation (%)",
                min_value=0.0, max_value=20.0, value=2.0, step=.5,
            )
        with le3:
            lease_term = st.number_input(
                "Lease term (years)",
                min_value=1, max_value=99, value=30,
            )
        with le4:
            discount = st.number_input(
                "Lease discount rate (%)",
                min_value=0.0, max_value=40.0, value=8.0, step=.5,
            )

        if lease_rate > 0 and usable_acres > 0:
            schedule, lease_pv = lease_schedule(
                usable_acres, lease_rate, escalation, discount, lease_term
            )
            st.metric(
                "Year-one lease payment",
                f"${usable_acres * lease_rate:,.0f}",
            )
            st.metric(
                "Present value of lease payments",
                f"${lease_pv:,.0f}",
            )
            st.dataframe(schedule, use_container_width=True, hide_index=True)
            st.download_button(
                "Download lease schedule",
                schedule.to_csv(index=False).encode("utf-8"),
                "sunstripe_lease_schedule.csv",
                "text/csv",
            )
        else:
            st.caption("Enter a lease rate and usable acreage to calculate lease economics.")


# ============================================================
# TAB 4: SOLAR SCREENING
# ============================================================

with tabs[3]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Solar development screening</div></div>',
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        solar_acres = st.number_input(
            "Usable land (acres)", 0.0, 1_000_000.0, 500.0, 25.0,
            key="solar_acres",
        )
        solar_acres_per_mw = st.number_input(
            "Acres per MWdc", 1.0, 30.0, 7.0, .5,
            key="solar_acres_mw",
        )
    with s2:
        dc_ac_ratio = st.number_input(
            "DC / AC ratio", 1.0, 2.5, 1.3, .05
        )
        yield_kwh_kw = st.number_input(
            "Assumed specific yield (kWh/kWdc/year)",
            500.0, 3000.0, 1700.0, 25.0,
        )
    with s3:
        capex_mw_solar = st.number_input(
            "Illustrative capex ($/MWdc)", 0.0, 20_000_000.0,
            1_000_000.0, 50_000.0,
        )
        solar_price = st.number_input(
            "Illustrative realized energy price ($/MWh)",
            0.0, 1000.0, 40.0, 1.0,
        )

    solar_mwdc = solar_acres / solar_acres_per_mw if solar_acres_per_mw else 0
    solar_mwac = solar_mwdc / dc_ac_ratio if dc_ac_ratio else 0
    solar_mwh = solar_mwdc * yield_kwh_kw
    solar_revenue = solar_mwh * solar_price
    solar_land_capex = solar_mwdc * capex_mw_solar

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Indicative DC capacity", f"{solar_mwdc:,.1f} MWdc")
    q2.metric("Indicative AC capacity", f"{solar_mwac:,.1f} MWac")
    q3.metric("Annual energy scenario", f"{solar_mwh:,.0f} MWh")
    q4.metric("Annual gross revenue scenario", f"${solar_revenue:,.0f}")

    st.caption(
        "Scenario calculation only. Yield, land density, price and capex are "
        "editable assumptions, not sourced resource data or EPC quotations."
    )

    solar_chart = pd.DataFrame({
        "Metric": ["DC capacity", "AC capacity"],
        "MW": [solar_mwdc, solar_mwac],
    })
    fig = px.bar(
        solar_chart, x="Metric", y="MW", text="MW",
        title="Solar configuration scenario"
    )
    fig.update_traces(marker_color="#e8392d", texttemplate="%{text:,.1f}")
    fig.update_layout(
        plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
        font_family="DM Sans",
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 5: BESS INTELLIGENCE
# ============================================================

with tabs[4]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Battery storage configuration & power-market screening</div></div>',
        unsafe_allow_html=True,
    )

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        bess_power = st.number_input(
            "Power rating (MW)", 0.1, 5000.0, 100.0, 5.0
        )
    with b2:
        bess_duration = st.selectbox(
            "Storage duration (hours)", [2, 4, 6, 8], index=1
        )
    with b3:
        bess_rte = st.number_input(
            "Round-trip efficiency (%)", 50.0, 100.0, 88.0, 1.0
        )
    with b4:
        bess_capex_mwh = st.number_input(
            "Illustrative installed cost ($/MWh)",
            0.0, 2_000_000.0, 250_000.0, 10_000.0,
        )

    bess_energy = bess_power * bess_duration
    bess_capex = bess_energy * bess_capex_mwh

    q1, q2, q3 = st.columns(3)
    q1.metric("Storage energy", f"{bess_energy:,.1f} MWh")
    q2.metric("Duration", f"{bess_duration} hours")
    q3.metric("Illustrative storage capex", f"${bess_capex:,.0f}")

    st.markdown("#### Historical nodal price analysis")
    if lmp_df.empty:
        st.info(
            "Upload a chronological price CSV in the sidebar to calculate "
            "price statistics and an indicative single-cycle arbitrage proxy."
        )
    else:
        p = lmp_df["lmp"]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Observations", f"{len(lmp_df):,}")
        k2.metric("Average LMP", f"${p.mean():,.2f}/MWh")
        k3.metric("90th − 10th percentile", f"${p.quantile(.9)-p.quantile(.1):,.2f}/MWh")
        k4.metric("Negative-price share", f"{(p < 0).mean()*100:.1f}%")

        period_df = lmp_df.set_index("timestamp").sort_index()
        hourly_avg = period_df["lmp"].resample("1h").mean().dropna()
        fig = px.line(
            hourly_avg.reset_index(), x="timestamp", y="lmp",
            title="Hourly average price series",
            labels={"timestamp": "Timestamp", "lmp": "Price ($/MWh)"},
        )
        fig.update_traces(line_color="#e8392d")
        fig.update_layout(
            plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
            font_family="DM Sans",
        )
        st.plotly_chart(fig, use_container_width=True)

        spread_df = bess_daily_spread_proxy(
            lmp_df, bess_power, bess_duration, bess_rte
        )

        if spread_df.empty:
            st.warning(
                "Not enough hourly price observations within each day for "
                "the selected storage duration."
            )
        else:
            total_proxy = spread_df[
                "estimated_gross_margin_proxy_usd"
            ].sum()
            k1, k2, k3 = st.columns(3)
            k1.metric("Days evaluated", f"{len(spread_df):,}")
            k2.metric("Sum of daily gross margin proxy", f"${total_proxy:,.0f}")
            k3.metric(
                "Mean daily proxy",
                f"${spread_df['estimated_gross_margin_proxy_usd'].mean():,.0f}",
            )
            st.dataframe(
                spread_df, use_container_width=True, hide_index=True
            )
            st.download_button(
                "Download BESS analysis CSV",
                spread_df.to_csv(index=False).encode("utf-8"),
                "sunstripe_bess_price_proxy.csv",
                "text/csv",
            )

        st.warning(
            "This is a simplified single-cycle price-spread proxy, not a "
            "validated dispatch backtest or bankable revenue forecast. It "
            "does not enforce independent charging power, state of charge, "
            "degradation, cycling limits, outages, market bids, ancillary "
            "services, interconnection limits, fees or settlement rules. "
            "Do not extrapolate the observed period into annual revenue without "
            "representative data and a validated dispatch model."
        )


# ============================================================
# TAB 6: WIND AND HYBRID SCREENING
# ============================================================

with tabs[5]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Wind and hybrid project screening</div></div>',
        unsafe_allow_html=True,
    )

    screen_technology = st.selectbox(
        "Technology scenario",
        ["Wind", "Solar + BESS", "Wind + BESS", "Hybrid"],
    )

    h1, h2, h3 = st.columns(3)

    with h1:
        controlled_acres = st.number_input(
            "Gross controlled land (acres)",
            min_value=0.0, value=5000.0, step=100.0,
        )
        developable_pct = st.slider(
            "Preliminary usable percentage", 0, 100, 60
        )

    with h2:
        if screen_technology == "Wind":
            area_per_mw = st.number_input(
                "Controlled acres per MW (wind)", .1, 200.0, 30.0, 1.0
            )
        elif screen_technology == "Hybrid":
            area_per_mw = st.number_input(
                "Land control acres per MW (hybrid)", .1, 100.0, 8.0, .5
            )
        else:
            area_per_mw = st.number_input(
                "Land control acres per MW (co-located)", .1, 100.0, 8.0, .5
            )

    with h3:
        wind_capacity_factor = st.number_input(
            "Illustrative capacity factor (%)", 0.0, 80.0, 40.0, 1.0
        )
        wind_price = st.number_input(
            "Illustrative realized price ($/MWh)", 0.0, 1000.0, 35.0, 1.0
        )

    available_acres = controlled_acres * developable_pct / 100
    land_supported_mw = available_acres / area_per_mw if area_per_mw else 0
    annual_mwh_wind = land_supported_mw * 8760 * wind_capacity_factor / 100
    annual_rev_wind = annual_mwh_wind * wind_price

    c1, c2, c3 = st.columns(3)
    c1.metric("Scenario usable acres", f"{available_acres:,.0f}")
    c2.metric("Indicative land-supported MW", f"{land_supported_mw:,.1f}")
    c3.metric("Annual gross revenue scenario", f"${annual_rev_wind:,.0f}")

    st.caption(
        "Wind land-control acreage is not equivalent to permanently occupied "
        "turbine footprint. No micrositing, setbacks, wake modelling, grid study "
        "or measured wind-resource assessment is performed by this scenario."
    )

    st.markdown("#### Hybrid diligence checklist")
    checklist_items = [
        "Verify export limit and shared interconnection rights",
        "Compare standalone and co-located capex",
        "Check renewable generation and charging time series",
        "Assess curtailment history and congestion",
        "Confirm parcel control, easements and access roads",
        "Model storage degradation and augmentation",
        "Verify market participation and charging constraints",
    ]
    for item in checklist_items:
        st.checkbox(item, key="hybrid_" + str(checklist_items.index(item)))


# ============================================================
# TAB 7: GRID AND ENVIRONMENT
# ============================================================

with tabs[6]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Grid accessibility & desktop constraint flags</div></div>',
        unsafe_allow_html=True,
    )

    if active is None:
        st.info("Select a candidate in the sidebar to calculate nearest uploaded grid point.")
    elif grid.empty:
        st.info(
            "Upload a grid/substation point CSV with columns name, latitude, longitude."
        )
    else:
        dist_km, grid_name = nearest_point_distance_km(
            active["latitude"], active["longitude"], grid
        )

        if dist_km is not None:
            g1, g2 = st.columns(2)
            g1.metric("Nearest uploaded grid point", grid_name)
            g2.metric("Geodesic point distance", f"{dist_km:.2f} km")

        st.caption(
            "Distances use WGS84 geodesic point-to-point measurement. "
            "If your CSV contains substations, the result is distance to the "
            "nearest supplied substation point; it does not measure distance "
            "to the nearest transmission line or prove available capacity."
        )

    if active is not None:
        st.markdown("#### Uploaded environmental screening fields")
        e1, e2, e3 = st.columns(3)
        e1.metric("Flood-risk input", str(active["flood_risk"]).title())
        e2.metric(
            "Protected-area flag",
            "Flagged" if active["protected_area"] else "Not flagged in input",
        )
        e3.metric(
            "Interconnection status",
            str(active["interconnection_status"]),
        )

        st.warning(
            "No official environmental overlay is queried automatically in "
            "this version. 'Not flagged in input' is not proof that a site is "
            "outside wetlands, floodplains, protected habitat, prime farmland, "
            "tribal lands or other regulated areas."
        )


# ============================================================
# TAB 8: PROJECT ECONOMICS
# ============================================================

with tabs[7]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Project economics & maximum supportable land cost</div></div>',
        unsafe_allow_html=True,
    )

    default_mw = (
        float(active["capacity_mw"])
        if active is not None and active["capacity_mw"] > 0
        else 100.0
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        project_mw = st.number_input(
            "Project capacity (MW)", .1, 10000.0, default_mw, 5.0
        )
        non_land_capex_per_mw = st.number_input(
            "Non-land capex ($/MW)", 0.0, 100_000_000.0,
            1_500_000.0, 50_000.0,
        )
        land_purchase_cost = st.number_input(
            "Land acquisition cost ($)", 0.0, 10_000_000_000.0,
            0.0, 100_000.0,
        )

    with f2:
        interconnection_cost = st.number_input(
            "Interconnection / upgrade allowance ($)",
            0.0, 10_000_000_000.0, 0.0, 100_000.0,
        )
        development_cost = st.number_input(
            "Development / other capex ($)",
            0.0, 10_000_000_000.0, 0.0, 100_000.0,
        )
        annual_revenue_per_mw = st.number_input(
            "Annual revenue assumption ($/MW/year)",
            0.0, 100_000_000.0, 150_000.0, 5_000.0,
        )

    with f3:
        annual_opex_per_mw = st.number_input(
            "Annual operating cost ($/MW/year)",
            0.0, 10_000_000.0, 30_000.0, 1_000.0,
        )
        project_life = st.number_input(
            "Project life (years)", 1, 60, 25
        )
        discount_rate = st.number_input(
            "Discount rate (%)", 0.0, 40.0, 8.0, .5
        )
        target_irr = st.number_input(
            "Target IRR (%)", 0.0, 50.0, 10.0, .5
        )

    non_land_total = (
        project_mw * non_land_capex_per_mw
        + interconnection_cost
        + development_cost
    )
    total_capex = non_land_total + land_purchase_cost
    annual_revenue = project_mw * annual_revenue_per_mw
    annual_opex = project_mw * annual_opex_per_mw
    net_cashflow = annual_revenue - annual_opex
    npv, irr, payback = calculate_npv_irr(
        total_capex,
        net_cashflow,
        project_life,
        discount_rate / 100,
    )
    max_land = maximum_land_price(
        non_land_total,
        net_cashflow,
        project_life,
        target_irr,
    )

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Total initial capex", f"${total_capex:,.0f}")
    q2.metric("Annual net cashflow proxy", f"${net_cashflow:,.0f}")
    q3.metric("NPV at discount rate", f"${npv:,.0f}")
    q4.metric("IRR proxy", f"{irr*100:.2f}%" if np.isfinite(irr) else "Not defined")

    st.metric(
        "Simple payback (years)",
        f"{payback:.1f}" if np.isfinite(payback) else "Not defined",
    )

    if max_land >= 0:
        st.success(
            f"Indicative maximum land purchase allowance at the target "
            f"{target_irr:.1f}% return: ${max_land:,.0f}"
        )
    else:
        st.warning(
            "The target return is not met under the supplied scenario even "
            "with a zero land purchase price. Review project economics."
        )

    st.caption(
        "Simplified unlevered constant-cashflow model. It excludes taxes, "
        "financing, debt sculpting, inflation, construction delays, degradation, "
        "merchant price variation, curtailment, tax credits, working capital, "
        "decommissioning and mid-life capex unless incorporated into your inputs. "
        "It is not a financing model."
    )

    economics = pd.DataFrame({
        "Metric": [
            "Project capacity (MW)",
            "Non-land capex ($)",
            "Land acquisition ($)",
            "Total initial capex ($)",
            "Annual revenue ($)",
            "Annual opex ($)",
            "Annual net cashflow proxy ($)",
            "NPV ($)",
            "IRR proxy (%)",
            "Simple payback (years)",
            "Maximum land allowance at target IRR ($)",
        ],
        "Value": [
            project_mw, non_land_total, land_purchase_cost, total_capex,
            annual_revenue, annual_opex, net_cashflow, npv,
            irr * 100 if np.isfinite(irr) else np.nan,
            payback, max_land,
        ],
    })

    st.download_button(
        "Download economics scenario",
        economics.to_csv(index=False).encode("utf-8"),
        "sunstripe_economics_scenario.csv",
        "text/csv",
    )


# ============================================================
# TAB 9: PORTFOLIO COMPARISON
# ============================================================

with tabs[8]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Portfolio comparison & development priorities</div></div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.info("No portfolio records are available.")
    else:
        portfolio = filtered.copy()

        if not grid.empty:
            distances = []
            nearest_names = []
            for _, row in portfolio.iterrows():
                d, n = nearest_point_distance_km(
                    row["latitude"], row["longitude"], grid
                )
                distances.append(d)
                nearest_names.append(n)

            portfolio["nearest_uploaded_grid_km"] = distances
            portfolio["nearest_uploaded_grid_name"] = nearest_names

        sort_by = st.selectbox(
            "Rank portfolio by",
            [
                "suitability_score",
                "capacity_mw",
                "resource_score",
                "grid_score",
                "land_score",
                "market_score",
            ],
        )
        ascending = sort_by != "suitability_score"

        st.dataframe(
            portfolio.sort_values(sort_by, ascending=ascending),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download portfolio comparison CSV",
            portfolio.to_csv(index=False).encode("utf-8"),
            "sunstripe_portfolio_comparison.csv",
            "text/csv",
        )

        compare_ids = st.multiselect(
            "Select sites for side-by-side comparison",
            portfolio["asset_id"].astype(str).tolist(),
            default=portfolio["asset_id"].astype(str).head(min(3, len(portfolio))).tolist(),
        )

        comparison = portfolio[
            portfolio["asset_id"].astype(str).isin(compare_ids)
        ].copy()

        compare_cols = [
            "asset_name", "technology", "state", "capacity_mw",
            "gross_acres", "suitability_score", "screening_status",
            "data_confidence", "nearest_substation_km",
            "interconnection_status", "source", "source_date",
        ]
        if "nearest_uploaded_grid_km" in comparison:
            compare_cols.append("nearest_uploaded_grid_km")

        st.markdown("**Selected site comparison**")
        st.dataframe(
            comparison[[c for c in compare_cols if c in comparison]],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# TAB 10: DATA, SOURCES AND METHODOLOGY
# ============================================================

with tabs[9]:
    st.markdown(
        '<div class="section-head"><div class="section-title">'
        'Data provenance, methodology & production checklist</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Asset CSV schema")
    st.code(
        "asset_id, asset_name, technology, capacity_mw, latitude, longitude, state\n"
        "Optional: status, operator, gross_acres, nearest_substation_km,\n"
        "resource_score, land_score, grid_score, environment_score, market_score,\n"
        "flood_risk, protected_area, interconnection_status, iso_rto, annual_mwh,\n"
        "source, source_date, notes",
        language="text",
    )

    st.markdown("#### Grid CSV schema")
    st.code(
        "name, latitude, longitude\n"
        "Optional: voltage_kv, owner, status, source, source_date",
        language="text",
    )

    st.markdown("#### Land comparables CSV schema")
    st.code(
        "state, acres, property_price, sale_date, transaction_type\n"
        "Optional: land_use, source, source_url",
        language="text",
    )
    st.markdown(
        "`transaction_type` must distinguish `sale`, `listing`, and `lease`. "
        "`property_price` should be the observed transaction or asking amount "
        "appropriate to that type, and `acres` must refer to the same property."
    )

    st.markdown("#### LMP CSV schema")
    st.code(
        "timestamp, lmp\n"
        "The timestamp should be parseable and prices must be expressed in $/MWh.",
        language="text",
    )

    st.markdown("#### Initial official-source directory")
    source_rows = [
        {
            "Provider": "EIA",
            "Use": "Generator and plant datasets",
            "URL": "https://www.eia.gov/opendata/",
            "Status": "Source directory only; connector not implemented",
        },
        {
            "Provider": "NREL",
            "Use": "Solar / wind resource and renewable data",
            "URL": "https://developer.nrel.gov/",
            "Status": "Source directory only; connector not implemented",
        },
        {
            "Provider": "USGS",
            "Use": "Elevation, terrain and hydrography",
            "URL": "https://www.usgs.gov/the-national-map-data-delivery",
            "Status": "Source directory only; connector not implemented",
        },
        {
            "Provider": "FEMA",
            "Use": "Flood hazard information",
            "URL": "https://www.fema.gov/flood-maps",
            "Status": "Source directory only; overlay not implemented",
        },
        {
            "Provider": "USFWS",
            "Use": "Wetlands and protected-species resources",
            "URL": "https://www.fws.gov/program/national-wetlands-inventory",
            "Status": "Source directory only; overlay not implemented",
        },
        {
            "Provider": "USDA NRCS",
            "Use": "Soils and agricultural land indicators",
            "URL": "https://websoilsurvey.nrcs.usda.gov/",
            "Status": "Source directory only; connector not implemented",
        },
        {
            "Provider": "US Census Bureau",
            "Use": "County boundaries and selected demographic data",
            "URL": "https://www.census.gov/geographies/mapping-files.html",
            "Status": "Source directory only; connector not implemented",
        },
        {
            "Provider": "ERCOT",
            "Use": "Texas power-market and grid information",
            "URL": "https://www.ercot.com/",
            "Status": "No automated market connector in this version",
        },
        {
            "Provider": "CAISO",
            "Use": "California ISO prices and grid information",
            "URL": "https://www.caiso.com/",
            "Status": "No automated market connector in this version",
        },
        {
            "Provider": "MISO",
            "Use": "MISO market and planning information",
            "URL": "https://www.misoenergy.org/",
            "Status": "No automated market connector in this version",
        },
        {
            "Provider": "PJM",
            "Use": "PJM market and interconnection information",
            "URL": "https://www.pjm.com/",
            "Status": "No automated market connector in this version",
        },
        {
            "Provider": "SPP",
            "Use": "SPP market and transmission information",
            "URL": "https://www.spp.org/",
            "Status": "No automated market connector in this version",
        },
        {
            "Provider": "NYISO",
            "Use": "New York market data",
            "URL": "https://www.nyiso.com/",
            "Status": "No automated market connector in this version",
        },
        {
            "Provider": "ISO New England",
            "Use": "New England market data",
            "URL": "https://www.iso-ne.com/",
            "Status": "No automated market connector in this version",
        },
    ]
    st.dataframe(
        pd.DataFrame(source_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn("Source URL"),
        },
    )

    st.markdown("#### Scoring weights")
    weight_rows = []
    for technology, weight_map in WEIGHTS.items():
        weight_rows.append({
            "Technology": technology,
            **{
                k.replace("_score", "").title(): f"{v:.0%}"
                for k, v in weight_map.items()
            },
        })
    st.dataframe(
        pd.DataFrame(weight_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Important technical limitations")
    st.markdown("""
- Asset records are not automatically fetched from EIA or ISO/RTO systems.
- There is no nationwide parcel database or parcel ownership search in this build.
- Property valuation requires uploaded comparable data with permission for intended use.
- Assessed value, transaction price, asking price and lease rate are different measures.
- Grid proximity does not indicate available interconnection capacity.
- The environmental fields are user-supplied flags, not GIS intersection results.
- Resource quality is not measured by the default score fields; scores need evidence and provenance.
- BESS spread results are screening proxies, not a market-grade dispatch optimization.
- There is no persistent PostGIS database, login, tenant isolation, billing or subscription enforcement.
- Public-data access does not automatically permit commercial redistribution. Verify current source terms.
""")

    st.markdown("#### Recommended production roadmap")
    roadmap = pd.DataFrame([
        {"Phase": 1, "Workstream": "GIS and land", "Next milestone": "GeoJSON and parcel connectors, land comparables, topology checks, provenance"},
        {"Phase": 2, "Workstream": "Authoritative data", "Next milestone": "EIA, resource, terrain, flood, wetlands and transmission data adapters"},
        {"Phase": 3, "Workstream": "Market intelligence", "Next milestone": "ISO/RTO ingestion, data normalization and validated BESS dispatch simulation"},
        {"Phase": 4, "Workstream": "Financial modelling", "Next milestone": "Detailed cash flows, financing, tax and sensitivity analysis"},
        {"Phase": 5, "Workstream": "Commercial SaaS", "Next milestone": "PostGIS, authentication, permissions, tenant isolation, audit and billing"},
    ])
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "SUNSTRIPE INTELLIGENCE | SOLAR • STORAGE • WIND | "
    "PRELIMINARY DECISION SUPPORT | VERIFY INPUT DATA BEFORE MAKING DEVELOPMENT OR INVESTMENT DECISIONS"
)
