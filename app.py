
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from io import StringIO

st.set_page_config(page_title="SunStripe Intelligence", page_icon="🔴", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;1,500&display=swap');
:root { --ink:#080b18; --red:#e8392d; --paper:#fbf9f7; --line:#e8e1dc; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--paper); color:var(--ink); }
.block-container { max-width:1450px; padding-top:.8rem; padding-bottom:2rem; }
header[data-testid="stHeader"] { background:transparent; }
#MainMenu, footer {visibility:hidden;}
div[data-testid="stToolbar"] {visibility:hidden;}
.topbar {background:#050714;color:white;margin:-1rem -1rem 0 -1rem;padding:18px 28px;border-bottom:1px solid #292b37;}
.brand {font-size:23px;font-weight:700;letter-spacing:-.8px;text-align:center;color:white;}
.brand span {color:#ff5145;}
.navrow {display:flex;justify-content:center;gap:30px;color:#f5f3f1;font-size:13px;font-weight:600;margin-top:16px;}
.navrow span {padding:6px 0;border-bottom:2px solid transparent;}
.navrow .active {border-color:#e8392d;}
.eyebrow {font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#e8392d;font-weight:700;margin-bottom:8px;}
.hero {font-family:'Playfair Display',serif;font-size:42px;line-height:1.12;font-style:italic;color:#e8392d;letter-spacing:-1px;margin:18px 0 12px;}
.subhero {color:#6f6762;font-size:14px;max-width:780px;margin-bottom:24px;}
.kpi {border:1px solid var(--line);padding:16px 18px;background:rgba(255,255,255,.48);min-height:92px;}
.kpi-num {font-family:'Playfair Display',serif;font-size:30px;line-height:1.05;color:#e8392d;}
.kpi-label {font-size:12px;color:#655d58;margin-top:8px;}
.strip {display:flex;gap:0;border:1px solid var(--line);margin:22px 0 14px;background:rgba(255,255,255,.4);}
.strip-item {padding:14px 16px;flex:1;border-right:1px solid var(--line);}
.strip-item:last-child {border-right:0;}
.strip-num {font-family:'Playfair Display',serif;font-size:24px;color:#e8392d;}
.strip-label {font-size:11px;color:#756d67;margin-top:3px;}
.pills {display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 24px;}
.pill {border:1px solid #e7dfda;border-radius:24px;padding:6px 12px;font-size:11px;color:#625a55;background:#fffdfa;}
.section-head {display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--line);padding-top:18px;margin-top:18px;}
.section-title {font-size:13px;font-weight:700;color:#282321;}
.mini {font-size:11px;color:#807771;}
div[data-testid="stMetric"] {background:rgba(255,255,255,.55);border:1px solid var(--line);padding:12px 15px;border-radius:2px;}
div[data-testid="stMetricLabel"] {font-size:12px;color:#766f6a;}
div[data-testid="stMetricValue"] {font-family:'Playfair Display',serif;color:#e8392d;}
.stTabs [data-baseweb="tab-list"] {gap:22px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"] {background:transparent;border-radius:0;padding:10px 2px;color:#5d5550;font-size:13px;}
.stTabs [aria-selected="true"] {color:#e8392d !important;border-bottom:2px solid #e8392d !important;}
.stButton button {border-radius:20px;border:1px solid #e8392d;color:#e8392d;background:transparent;}
.stButton button:hover {background:#e8392d;color:white;border-color:#e8392d;}
div[data-testid="stDataFrame"] {border:1px solid var(--line);}
hr {border-color:var(--line);}
</style>
""", unsafe_allow_html=True)

SAMPLE = """asset_id,asset_name,technology,status,state,operator,capacity_mw,latitude,longitude,nearest_substation_km,resource_score,land_score,grid_score,environment_score,market_score,flood_risk,protected_area,interconnection_status
SOL-DEMO-01,Example Solar Texas,Solar,Operating,Texas,Demo Operator,250,31.20,-99.20,4.5,85,78,72,88,70,low,false,Unknown
BESS-DEMO-01,Example BESS Texas,BESS,Planned,Texas,Demo Storage,200,32.10,-97.80,2.1,60,82,88,90,92,low,false,Unknown
WIN-DEMO-01,Example Wind Iowa,Wind,Operating,Iowa,Demo Wind,300,42.00,-94.50,8.0,90,70,68,72,62,low,false,Unknown
HYB-DEMO-01,Example Hybrid New Mexico,Hybrid,Proposed,New Mexico,Demo Renewables,150,34.60,-106.00,6.0,82,75,80,86,78,unknown,false,Unknown
BESS-DEMO-02,Example BESS California,BESS,Proposed,California,Demo Storage,100,35.20,-119.10,3.0,55,65,78,85,95,high,false,Unknown
SOL-DEMO-02,Example Solar Georgia,Solar,Planned,Georgia,Demo Solar,180,32.70,-83.40,7.0,76,80,70,84,68,low,false,Unknown
WIN-DEMO-02,Example Wind Texas,Wind,Planned,Texas,Demo Wind,400,33.00,-101.00,10.0,88,75,65,78,80,low,false,Unknown
BESS-DEMO-03,Example BESS New York,BESS,Proposed,New York,Demo Storage,80,42.80,-75.00,5.0,55,72,75,90,84,low,false,Unknown
"""

REQUIRED = [
    "asset_id", "asset_name", "technology", "capacity_mw",
    "latitude", "longitude", "state"
]
SCORE_COLS = [
    "resource_score", "land_score", "grid_score",
    "environment_score", "market_score"
]
WEIGHTS = {
    "Solar": {"resource_score": .30, "land_score": .20, "grid_score": .25, "environment_score": .15, "market_score": .10},
    "BESS": {"resource_score": .15, "land_score": .15, "grid_score": .30, "environment_score": .15, "market_score": .25},
    "Wind": {"resource_score": .35, "land_score": .15, "grid_score": .20, "environment_score": .20, "market_score": .10},
    "Hybrid": {"resource_score": .25, "land_score": .15, "grid_score": .25, "environment_score": .15, "market_score": .20},
}
COLORS = {
    "Solar": [235, 177, 45, 210],
    "BESS": [45, 115, 225, 210],
    "Wind": [40, 155, 100, 210],
    "Hybrid": [150, 85, 195, 210],
}

def read_assets(upload):
    df = pd.read_csv(upload) if upload else pd.read_csv(StringIO(SAMPLE))
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    defaults = {
        "status": "Unknown", "operator": "Unknown",
        "nearest_substation_km": None, "resource_score": 50,
        "land_score": 50, "grid_score": 50,
        "environment_score": 50, "market_score": 50,
        "flood_risk": "unknown", "protected_area": False,
        "interconnection_status": "Unknown",
    }
    for col, value in defaults.items():
        if col not in df:
            df[col] = value

    numeric_cols = [
        "capacity_mw", "latitude", "longitude",
        "nearest_substation_km", *SCORE_COLS
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["capacity_mw", "latitude", "longitude"]).copy()
    df = df[
        df.latitude.between(-90, 90)
        & df.longitude.between(-180, 180)
        & (df.capacity_mw >= 0)
    ]

    df["technology"] = df["technology"].astype(str).str.strip().str.title()
    df = df[df.technology.isin(WEIGHTS)].copy()
    df["flood_risk"] = df["flood_risk"].fillna("unknown").astype(str).str.lower()
    df["protected_area"] = (
        df["protected_area"].fillna(False).astype(str).str.lower()
        .isin(["true", "1", "yes", "y"])
    )

    for col in SCORE_COLS:
        df[col] = df[col].fillna(50).clip(0, 100)

    if df.empty:
        raise ValueError("No valid asset records found.")
    return df

def score_assets(df):
    df = df.copy()
    df["suitability_score"] = df.apply(
        lambda r: round(
            sum(r[col] * weight for col, weight in WEIGHTS[r["technology"]].items()),
            1
        ),
        axis=1,
    )

    def classify(row):
        if row["protected_area"]:
            return "Review required"
        if row["flood_risk"] == "high":
            return "High risk"
        if row["suitability_score"] >= 75:
            return "Priority"
        if row["suitability_score"] >= 55:
            return "Conditional"
        return "Lower priority"

    df["screening_status"] = df.apply(classify, axis=1)
    return df

# Header inspired by the SunStripe Intelligence reference design
st.markdown("""
<div class="topbar">
  <div class="brand">Sunstripe <span>Intelligence</span></div>
  <div class="navrow">
    <span class="active">ASSETS</span><span>GRID</span><span>SCREENING</span>
    <span>MARKETS</span><span>RESEARCH</span><span>ABOUT</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔴 SunStripe")
    st.caption("LOCATION INTELLIGENCE")
    upload = st.file_uploader("Upload asset CSV", type=["csv"])
    grid_upload = st.file_uploader("Upload grid / substation CSV", type=["csv"])
    st.divider()
    st.markdown("**Filter asset universe**")
    techs = st.multiselect("Technology", list(WEIGHTS), default=list(WEIGHTS))

    try:
        raw = score_assets(read_assets(upload))
    except Exception as e:
        st.error(str(e))
        st.stop()

    state_options = sorted(raw.state.dropna().astype(str).unique())
    states = st.multiselect("State", state_options, default=state_options)
    max_mw = max(1, int(raw.capacity_mw.max()))
    cap = st.slider("Capacity (MW)", 0, max_mw, (0, max_mw))
    min_score = st.slider("Minimum score", 0, 100, 0)
    st.caption("Sample records are illustrative. Upload verified datasets for real screening.")

filtered = raw[
    raw.technology.isin(techs)
    & raw.state.astype(str).isin(states)
    & raw.capacity_mw.between(*cap)
    & (raw.suitability_score >= min_score)
].copy()

grid = pd.DataFrame()
if grid_upload:
    try:
        grid = pd.read_csv(grid_upload)
        grid.columns = [str(c).strip().lower() for c in grid.columns]
        if not {"name", "latitude", "longitude"}.issubset(grid.columns):
            raise ValueError("Grid CSV requires name, latitude, longitude.")
        grid["latitude"] = pd.to_numeric(grid["latitude"], errors="coerce")
        grid["longitude"] = pd.to_numeric(grid["longitude"], errors="coerce")
        grid = grid.dropna(subset=["latitude", "longitude"])
        grid = grid[
            grid.latitude.between(-90, 90)
            & grid.longitude.between(-180, 180)
        ]
    except Exception as e:
        st.warning(f"Grid upload issue: {e}")
        grid = pd.DataFrame()

st.markdown(
    '<div class="eyebrow">● SUNSTRIPE PULSE &nbsp; / &nbsp; LOCATION INTELLIGENCE</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="hero">Find the next right place<br>to build.</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subhero">A unified screening workspace for utility-scale solar, battery storage and wind development. Explore assets, compare location signals and prioritize sites for deeper diligence.</div>',
    unsafe_allow_html=True
)

a, b, c, d = st.columns(4)
with a:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{len(filtered):,}</div><div class="kpi-label">Assets in current view</div></div>',
        unsafe_allow_html=True
    )
with b:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{filtered.capacity_mw.sum():,.0f} MW</div><div class="kpi-label">Represented capacity</div></div>',
        unsafe_allow_html=True
    )
with c:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{int((filtered.screening_status=="Priority").sum())}</div><div class="kpi-label">Higher-priority sites</div></div>',
        unsafe_allow_html=True
    )
with d:
    st.markdown(
        f'<div class="kpi"><div class="kpi-num">{int((filtered.technology=="BESS").sum())}</div><div class="kpi-label">Storage assets in view</div></div>',
        unsafe_allow_html=True
    )

counts = filtered.technology.value_counts()
pills = "".join(
    f'<span class="pill">{t} &nbsp; {int(counts.get(t, 0))} assets</span>'
    for t in WEIGHTS
)
st.markdown(f'<div class="pills">{pills}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="strip">
 <div class="strip-item"><div class="strip-num">{int((filtered.screening_status=="Priority").sum())}</div><div class="strip-label">Priority review</div></div>
 <div class="strip-item"><div class="strip-num">{int((filtered.screening_status=="Conditional").sum())}</div><div class="strip-label">Conditional review</div></div>
 <div class="strip-item"><div class="strip-num">{int((filtered.screening_status=="High risk").sum()+(filtered.screening_status=="Review required").sum())}</div><div class="strip-label">Risk flags to investigate</div></div>
 <div class="strip-item"><div class="strip-num">{filtered.state.nunique() if len(filtered) else 0}</div><div class="strip-label">States represented</div></div>
</div>
""", unsafe_allow_html=True)

tab_assets, tab_map, tab_screen, tab_market, tab_method = st.tabs(
    ["Open asset universe", "Map view", "Site screening", "Portfolio analytics", "Methodology & data"]
)

with tab_assets:
    st.markdown(
        '<div class="section-head"><div class="section-title">Asset universe</div><div class="mini">FILTERED RECORDS · EXPORT AVAILABLE</div></div>',
        unsafe_allow_html=True
    )
    if filtered.empty:
        st.info("No records match the selected filters.")
    else:
        cols = [
            "asset_id", "asset_name", "technology", "state", "status",
            "capacity_mw", "suitability_score", "screening_status",
            "nearest_substation_km"
        ]
        show = filtered[[col for col in cols if col in filtered.columns]].copy()
        show.columns = [col.replace("_", " ").title() for col in show.columns]
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.download_button(
            "Download filtered assets CSV",
            filtered.to_csv(index=False).encode("utf-8"),
            "sunstripe_assets.csv",
            "text/csv"
        )
        st.caption("Scores depend on the quality of uploaded input data.")

with tab_map:
    st.markdown(
        '<div class="section-head"><div class="section-title">Geospatial intelligence</div><div class="mini">ASSET + GRID OVERLAY</div></div>',
        unsafe_allow_html=True
    )
    if filtered.empty:
        st.info("No assets to display.")
    else:
        md = filtered.copy()
        md["color"] = md.technology.map(COLORS)
        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                data=md,
                get_position="[longitude, latitude]",
                get_fill_color="color",
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
                    get_fill_color=[80, 80, 85, 190],
                    get_radius=2500,
                    radius_min_pixels=3,
                    pickable=True,
                )
            )
        view = pdk.ViewState(
            latitude=float(md.latitude.mean()),
            longitude=float(md.longitude.mean()),
            zoom=3,
            pitch=0,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view,
                tooltip={
                    "html": "<b>{asset_name}</b><br/>{technology} · {state}<br/>{capacity_mw} MW · Score {suitability_score}"
                },
            ),
            use_container_width=True,
        )
        st.caption(
            "Solar = gold · BESS = blue · Wind = green · Hybrid = purple · "
            "Grid records = grey. Proximity does not prove available interconnection capacity."
        )

with tab_screen:
    st.markdown(
        '<div class="section-head"><div class="section-title">Site screening desk</div><div class="mini">WEIGHTED, TECHNOLOGY-SPECIFIC SCORING</div></div>',
        unsafe_allow_html=True
    )
    if filtered.empty:
        st.info("No sites available under current filters.")
    else:
        aid = st.selectbox(
            "Choose an asset",
            filtered.asset_id.astype(str),
            format_func=lambda x: (
                f"{x} — {filtered.loc[filtered.asset_id.astype(str).eq(x), 'asset_name'].iloc[0]}"
            ),
        )
        r = filtered[filtered.asset_id.astype(str).eq(aid)].iloc[0]
        x, y = st.columns([1, 2])
        with x:
            st.markdown(f"### {r.asset_name}")
            st.metric("Suitability score", f"{r.suitability_score}/100")
            st.write(f"**Technology:** {r.technology}")
            st.write(f"**Location:** {r.state}")
            st.write(f"**Capacity:** {r.capacity_mw:,.1f} MW")
            st.write(f"**Classification:** {r.screening_status}")
            st.write(f"**Interconnection status:** {r.interconnection_status}")
            if pd.notna(r.nearest_substation_km):
                st.write(f"**Reported substation distance:** {r.nearest_substation_km} km")
        with y:
            comp = pd.DataFrame({
                "Dimension": ["Resource", "Land", "Grid", "Environment", "Market"],
                "Score": [r[col] for col in SCORE_COLS],
            })
            fig = px.bar(
                comp, x="Dimension", y="Score", range_y=[0, 100],
                text="Score", title="Location factor breakdown"
            )
            fig.update_traces(textposition="outside", marker_color="#e8392d")
            fig.update_layout(
                plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
                font_family="DM Sans"
            )
            st.plotly_chart(fig, use_container_width=True)
        st.warning(
            "A screening score is not a permitting, environmental, engineering, "
            "land-title or bankability determination. Verify all constraints with authoritative sources."
        )

with tab_market:
    st.markdown(
        '<div class="section-head"><div class="section-title">Portfolio intelligence</div><div class="mini">CURRENT FILTERED DATASET</div></div>',
        unsafe_allow_html=True
    )
    if filtered.empty:
        st.info("No data to chart.")
    else:
        left, right = st.columns(2)
        with left:
            techcap = filtered.groupby("technology", as_index=False).capacity_mw.sum()
            fig = px.bar(
                techcap, x="technology", y="capacity_mw", color="technology",
                title="Capacity by technology"
            )
            fig.update_layout(
                plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
                font_family="DM Sans"
            )
            st.plotly_chart(fig, use_container_width=True)
        with right:
            statecap = (
                filtered.groupby("state", as_index=False).capacity_mw.sum()
                .sort_values("capacity_mw", ascending=False).head(12)
            )
            fig = px.bar(
                statecap, x="state", y="capacity_mw",
                title="States by represented capacity"
            )
            fig.update_traces(marker_color="#e8392d")
            fig.update_layout(
                plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
                font_family="DM Sans"
            )
            st.plotly_chart(fig, use_container_width=True)

        status = (
            filtered.screening_status.value_counts()
            .rename_axis("Classification").reset_index(name="Assets")
        )
        fig = px.pie(
            status, names="Classification", values="Assets",
            hole=.55, title="Screening classifications"
        )
        fig.update_layout(
            plot_bgcolor="#fbf9f7", paper_bgcolor="#fbf9f7",
            font_family="DM Sans"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_method:
    st.markdown(
        '<div class="section-head"><div class="section-title">Data model & methodology</div><div class="mini">TRANSPARENT ASSUMPTIONS</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        "**Required asset CSV columns:** `asset_id`, `asset_name`, `technology`, "
        "`capacity_mw`, `latitude`, `longitude`, `state`."
    )
    st.markdown(
        "**Optional columns:** `status`, `operator`, `nearest_substation_km`, "
        "`resource_score`, `land_score`, `grid_score`, `environment_score`, "
        "`market_score`, `flood_risk`, `protected_area`, `interconnection_status`."
    )
    st.markdown(
        "**Optional grid CSV columns:** `name`, `latitude`, `longitude`; "
        "optional `voltage_kv`, `owner`, `status`."
    )

    weights = []
    for technology, weight_map in WEIGHTS.items():
        weights.append({
            "Technology": technology,
            **{
                key.replace("_score", "").title(): f"{value:.0%}"
                for key, value in weight_map.items()
            },
        })
    st.dataframe(pd.DataFrame(weights), use_container_width=True, hide_index=True)

    st.markdown("""
**Recommended production data integrations**
- EIA-860/860M for generator and planned project inventories.
- ISO/RTO sources for interconnection queues, nodal prices and market information.
- NREL resource data for solar and wind.
- USGS elevation, FEMA flood hazards and USFWS environmental layers.
- Transmission owner and utility GIS data for substations and lines.
- State/county parcel, zoning, land-use and permitting sources.

This version does not fetch live data. Missing score fields default to 50 for demo purposes.
Screening classifications are preliminary labels, not verified development conclusions.
Store API keys in Streamlit Secrets, never in source code.
""")

st.divider()
st.caption(
    "SUNSTRIPE INTELLIGENCE · LOCATION INTELLIGENCE FOR SOLAR, STORAGE & WIND · DEMONSTRATION BUILD"
)
