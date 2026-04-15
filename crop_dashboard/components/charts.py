"""
charts.py
---------
All Plotly chart functions for the dashboard.
Each function takes a DataFrame + filters and returns a Plotly figure.
Keeping charts in a separate file = easy to update without touching the main app.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# ── COLOR PALETTE ─────────────────────────────────────────────────────────────
COLORS = {
    "ET":      "#2563eb",   # blue  - Total ET line
    "forage":  "#16a34a",   # green - Forage share line
    "NDVI":    "#65a30d",   # lime  - NDVI line
    "Forage":  "#16a34a",
    "Cereals": "#2563eb",
    "Vegetables": "#f59e0b",
    "Other":   "#9ca3af",
    "bg":      "#ffffff",
    "grid":    "#f1f5f9",
}


def make_timeseries_chart(df: pd.DataFrame, region: str, year_start: int, year_end: int) -> go.Figure:
    """
    Dual-axis line chart: Total ET (BCM) on left axis, Forage % on right axis.
    
    Args:
        df         - full timeseries dataframe from mock_data
        region     - selected region name
        year_start - filter start year
        year_end   - filter end year
    
    Returns: Plotly Figure
    """
    # Filter by region and year range
    filtered = df[(df["region"] == region) &
                  (df["year"] >= year_start) &
                  (df["year"] <= year_end)]

    fig = go.Figure()

    # ── LINE 1: Total ET (left y-axis) ────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=filtered["year"],
        y=filtered["total_ET_BCM"],
        name="Total ET",
        line=dict(color=COLORS["ET"], width=2.5),
        mode="lines+markers",
        marker=dict(size=6),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Total ET: %{y:.2f} BCM<extra></extra>",
    ))

    # ── LINE 2: Forage Share % (right y-axis) ─────────────────────────────────
    fig.add_trace(go.Scatter(
        x=filtered["year"],
        y=filtered["forage_share"],
        name="Forage %",
        line=dict(color=COLORS["forage"], width=2.5),
        mode="lines+markers",
        marker=dict(size=6),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Forage Share: %{y:.1f}%<extra></extra>",
    ))

    # ── LINE 3: NDVI (right y-axis, secondary) ────────────────────────────────
    fig.add_trace(go.Scatter(
        x=filtered["year"],
        y=filtered["NDVI"] * 100,  # scale to % range for visibility
        name="NDVI",
        line=dict(color=COLORS["NDVI"], width=2, dash="dot"),
        mode="lines+markers",
        marker=dict(size=5),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>NDVI (scaled): %{y:.1f}<extra></extra>",
    ))

    # ── LAYOUT ────────────────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(text=f"ET & Forage Share Over Time ({year_start}–{year_end})",
                   font=dict(size=14, color="#1e293b")),
        xaxis=dict(tickmode="linear", dtick=1, gridcolor=COLORS["grid"]),
        yaxis=dict(title="BCM", gridcolor=COLORS["grid"], titlefont=dict(color=COLORS["ET"])),
        yaxis2=dict(title="%", overlaying="y", side="right",
                    titlefont=dict(color=COLORS["forage"]), showgrid=False),
        legend=dict(orientation="h", y=-0.2, x=0),
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        margin=dict(l=40, r=40, t=50, b=60),
        hovermode="x unified",
    )

    return fig


def make_crop_breakdown_chart(df: pd.DataFrame, region: str) -> go.Figure:
    """
    Stacked bar chart showing crop type breakdown by season.
    
    Args:
        df     - crop breakdown dataframe
        region - selected region
    
    Returns: Plotly Figure
    """
    filtered = df[df["region"] == region]

    crop_types = ["Forage", "Cereals", "Vegetables", "Other"]
    seasons    = filtered["season"].tolist()

    fig = go.Figure()

    for crop in crop_types:
        fig.add_trace(go.Bar(
            name=crop,
            x=seasons,
            y=filtered[crop].tolist(),
            marker_color=COLORS[crop],
            hovertemplate=f"<b>{crop}</b><br>%{{y}}%<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title=dict(text=f"Crop Breakdown in {region}", font=dict(size=14, color="#1e293b")),
        xaxis=dict(title="", gridcolor=COLORS["grid"]),
        yaxis=dict(title="%", gridcolor=COLORS["grid"]),
        legend=dict(orientation="h", y=-0.25, x=0),
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        margin=dict(l=40, r=20, t=50, b=60),
    )

    return fig


def make_map_figure(geojson: dict, df_latest: pd.DataFrame, selected_region: str) -> go.Figure:
    """
    Choropleth map of Saudi regions colored by ET intensity.
    Highlights the selected region.
    
    Args:
        geojson         - GeoJSON FeatureCollection
        df_latest       - single-year filtered dataframe
        selected_region - currently selected region name
    
    Returns: Plotly Figure
    """
    # Merge ET data into GeoJSON properties for coloring
    et_map = df_latest.set_index("region")["ET_intensity"].to_dict()

    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson,
        locations=[f["properties"]["name"] for f in geojson["features"]],
        z=[et_map.get(f["properties"]["name"], 0) for f in geojson["features"]],
        featureidkey="properties.name",
        colorscale="Greens",
        zmin=7000, zmax=9500,
        marker_opacity=0.75,
        marker_line_width=2,
        marker_line_color="white",
        colorbar=dict(title="ET (m³/ha)", thickness=12, len=0.6),
        hovertemplate="<b>%{location}</b><br>ET: %{z} m³/ha<extra></extra>",
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": 25.5, "lon": 42.5},
            zoom=4.2,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=340,
    )

    return fig
