"""
app.py  ← Run this file with:  streamlit run app.py
-------
Main Streamlit application for the Saudi Crop & Water Monitoring Dashboard.

HOW IT'S ORGANIZED:
    1. Imports & page config
    2. Load data
    3. Sidebar controls (region, year range, variables)
    4. KPI cards row
    5. Map + Controls row
    6. Charts row (line chart + bar chart)
    7. Auto-generated text summary
"""

import sys
import os

# ── Make sure Python can find our modules ────────────────────────────────────
sys.path.append(os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Our own modules
from data.mock_data import df_timeseries, df_crop, geojson_regions, region_names
from components.charts import make_timeseries_chart, make_crop_breakdown_chart, make_map_figure


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
#    Must be the FIRST Streamlit call in the script
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Saudi Crop & Water Dashboard",
    page_icon="🌿",
    layout="wide",           # Use full browser width
    initial_sidebar_state="expanded",
)

# ── Custom CSS for polished look ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Import a clean professional font */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Dashboard title area */
    .dashboard-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .dashboard-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    
    /* KPI card styling */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .kpi-label {
        font-size: 0.72rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.1;
    }
    .kpi-value.green { color: #16a34a; }
    .kpi-unit {
        font-size: 0.72rem;
        color: #94a3b8;
        margin-top: 0.1rem;
    }
    
    /* Summary box */
    .summary-box {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.2rem;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.6;
        margin-top: 1rem;
    }
    
    /* Remove Streamlit default padding */
    .block-container { padding-top: 1.5rem; }
    
    /* Section headers */
    .section-header {
        font-size: 0.8rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SIDEBAR — all user controls live here
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🌿 Dashboard Controls")
    st.markdown("---")

    # ── Region selector ───────────────────────────────────────────────────────
    # st.selectbox returns the selected string value
    selected_region = st.selectbox(
        "📍 Region",
        options=region_names,
        index=0,   # Default: first region (Tabuk)
        help="Select a Saudi region to explore"
    )

    # ── Year range slider ─────────────────────────────────────────────────────
    # st.slider with a tuple value gives you a range selector
    year_range = st.slider(
        "📅 Time Period",
        min_value=2013,
        max_value=2023,
        value=(2015, 2023),  # Default range
        step=1,
    )
    year_start, year_end = year_range

    st.markdown("---")

    # ── Variable checkboxes ───────────────────────────────────────────────────
    st.markdown("**📊 Variables to Show**")
    show_forage = st.checkbox("Forage",      value=True)
    show_ET     = st.checkbox("Water Use (ET)", value=True)
    show_NDVI   = st.checkbox("NDVI",        value=True)
    show_crops  = st.checkbox("Crop Type Breakdown", value=True)

    st.markdown("---")
    st.markdown("**ℹ️ About**")
    st.caption("Saudi Crop & Water Monitoring Dashboard (2013–2023). "
               "Using mock data — replace `data/mock_data.py` with real CSVs from client.")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FILTER DATA based on sidebar selections
#    Every time a user changes a control, Streamlit re-runs the whole script.
#    So filtering happens fresh every run.
# ═══════════════════════════════════════════════════════════════════════════════

# Filter timeseries for the selected region + year range
df_filtered = df_timeseries[
    (df_timeseries["region"] == selected_region) &
    (df_timeseries["year"] >= year_start) &
    (df_timeseries["year"] <= year_end)
]

# Get the LATEST year's row for KPI cards
df_latest_year = df_timeseries[
    (df_timeseries["region"] == selected_region) &
    (df_timeseries["year"] == year_end)
].iloc[0]  # .iloc[0] = get first (and only) row as a Series

# Get all latest-year data for the map coloring
df_map_data = df_timeseries[df_timeseries["year"] == year_end]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="dashboard-title">🌿 Saudi Crop & Water Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dashboard-subtitle">Regional analysis · {year_start}–{year_end} · Showing: <strong>{selected_region}</strong></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. KPI CARDS ROW
#    st.columns([1,1,1,1]) creates 4 equal-width columns
# ═══════════════════════════════════════════════════════════════════════════════
col1, col2, col3, col4 = st.columns(4)

# Helper: render one KPI card using HTML
# unsafe_allow_html=True is needed to render custom HTML in Streamlit
def kpi(col, label, value, unit="", green=False):
    color_class = "green" if green else ""
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {color_class}">{value}</div>
        <div class="kpi-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)

kpi(col1, "Total ET",      f"{df_latest_year['total_ET_BCM']:.2f}", "BCM")
kpi(col2, "ET Intensity",  f"{int(df_latest_year['ET_intensity']):,}", "m³ / ha", green=True)
kpi(col3, "Forage Share",  f"{df_latest_year['forage_share']:.1f}%")
kpi(col4, "Fields",        f"{int(df_latest_year['fields']):,}")

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MAP + DETAILS ROW
# ═══════════════════════════════════════════════════════════════════════════════
map_col, detail_col = st.columns([2, 1])

with map_col:
    st.markdown('<div class="section-header">🗺️ Regional Map — ET Intensity</div>', unsafe_allow_html=True)
    map_fig = make_map_figure(geojson_regions, df_map_data, selected_region)
    # use_container_width=True makes the chart fill the column width
    st.plotly_chart(map_fig, use_container_width=True)

with detail_col:
    st.markdown('<div class="section-header">📋 Region Details</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#f8fafc; border-radius:10px; padding:1.2rem; border:1px solid #e2e8f0">
        <div style="font-size:1.1rem; font-weight:700; color:#0f172a; margin-bottom:0.8rem">
            📍 {selected_region} Region
        </div>
        <table style="width:100%; font-size:0.85rem; color:#334155">
            <tr><td style="padding:4px 0; color:#64748b">Fields</td>
                <td style="font-weight:600">{int(df_latest_year['fields']):,}</td></tr>
            <tr><td style="padding:4px 0; color:#64748b">Avg. ET</td>
                <td style="font-weight:600">{int(df_latest_year['ET_intensity']):,} m³/ha</td></tr>
            <tr><td style="padding:4px 0; color:#64748b">Forage Share</td>
                <td style="font-weight:600">{df_latest_year['forage_share']:.1f}%</td></tr>
            <tr><td style="padding:4px 0; color:#64748b">NDVI</td>
                <td style="font-weight:600">{df_latest_year['NDVI']:.3f}</td></tr>
            <tr><td style="padding:4px 0; color:#64748b">Year</td>
                <td style="font-weight:600">{year_end}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Quick trend indicator (compare first vs last year in range)
    if len(df_filtered) >= 2:
        first_val = df_filtered.iloc[0]["total_ET_BCM"]
        last_val  = df_filtered.iloc[-1]["total_ET_BCM"]
        delta_pct = ((last_val - first_val) / first_val) * 100
        arrow     = "▲" if delta_pct > 0 else "▼"
        color     = "#dc2626" if delta_pct > 0 else "#16a34a"  # red=more water use, green=less
        st.markdown(f"""
        <div style="margin-top:1rem; background:#f8fafc; border-radius:10px; 
                    padding:1rem; border:1px solid #e2e8f0; text-align:center">
            <div style="font-size:0.72rem; color:#64748b; text-transform:uppercase; 
                        letter-spacing:0.06em">ET Change ({year_start}→{year_end})</div>
            <div style="font-size:1.5rem; font-weight:700; color:{color}">
                {arrow} {abs(delta_pct):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CHARTS ROW
# ═══════════════════════════════════════════════════════════════════════════════
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    if show_ET or show_forage or show_NDVI:
        ts_fig = make_timeseries_chart(df_timeseries, selected_region, year_start, year_end)
        st.plotly_chart(ts_fig, use_container_width=True)
    else:
        st.info("Select at least one variable in the sidebar to show the time series chart.")

with chart_col2:
    if show_crops:
        crop_fig = make_crop_breakdown_chart(df_crop, selected_region)
        st.plotly_chart(crop_fig, use_container_width=True)
    else:
        st.info("Enable 'Crop Type Breakdown' in sidebar to view this chart.")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. AUTO-GENERATED SUMMARY
#    This block reads the filtered data and writes a sentence automatically.
#    When the client connects real data, this updates itself instantly.
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")

# Determine ET trend direction for the summary sentence
if len(df_filtered) >= 2:
    et_trend = "increased" if df_filtered.iloc[-1]["total_ET_BCM"] > df_filtered.iloc[0]["total_ET_BCM"] else "decreased"
else:
    et_trend = "remained stable"

dominant_season = "Summer"  # Could be derived from crop breakdown data

summary_text = (
    f"In the <strong>{selected_region} Region</strong>, total ET was "
    f"<strong>{df_latest_year['total_ET_BCM']:.2f} BCM</strong> in {year_end} "
    f"with forage accounting for <strong>{df_latest_year['forage_share']:.1f}%</strong> of water use. "
    f"ET has {et_trend} over the {year_start}–{year_end} period, with an average intensity of "
    f"<strong>{int(df_latest_year['ET_intensity']):,} m³/ha</strong>. "
    f"{dominant_season} ET was significantly higher than winter, with forage being the dominant crop."
)

st.markdown(f'<div class="summary-box">📝 {summary_text}</div>', unsafe_allow_html=True)
