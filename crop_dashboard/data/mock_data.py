"""
mock_data.py
------------
Generates realistic sample data for the Saudi Crop & Water dashboard.
When you get real data from the client, you replace this with CSV loaders.
"""

import pandas as pd
import numpy as np
import json

# ── 1. REGION METADATA ──────────────────────────────────────────────────────
# Each Saudi region with its coordinates and basic stats
REGIONS = {
    "Tabuk":    {"lat": 28.38, "lon": 36.57, "fields": 1235, "color": "#2ecc71"},
    "Riyadh":   {"lat": 24.68, "lon": 46.72, "fields": 980,  "color": "#3498db"},
    "Al-Qassim":{"lat": 26.32, "lon": 43.97, "fields": 760,  "color": "#e67e22"},
    "Al-Jouf":  {"lat": 29.89, "lon": 38.99, "fields": 540,  "color": "#9b59b6"},
    "Hail":     {"lat": 27.52, "lon": 41.69, "fields": 430,  "color": "#e74c3c"},
}

# ── 2. TIME SERIES DATA ──────────────────────────────────────────────────────
def generate_timeseries() -> pd.DataFrame:
    """
    Returns a DataFrame with yearly ET and forage stats per region.
    
    Columns:
        region        - region name
        year          - 2013 to 2023
        total_ET_BCM  - total evapotranspiration (billion cubic meters)
        ET_intensity  - ET per hectare (m³/ha)
        forage_share  - % of water used by forage crops
        NDVI          - vegetation index (0–1 scale * 10 for display)
    """
    np.random.seed(42)  # Fixed seed = same data every run (good for demos)
    rows = []

    for region, meta in REGIONS.items():
        # Each region gets a slightly different baseline
        base_ET = {"Tabuk": 1.0, "Riyadh": 0.7, "Al-Qassim": 0.55,
                   "Al-Jouf": 0.45, "Hail": 0.38}[region]
        
        for year in range(2013, 2024):
            noise = np.random.normal(0, 0.05)
            rows.append({
                "region":       region,
                "year":         year,
                "total_ET_BCM": round(base_ET + noise, 3),
                "ET_intensity": int(8000 + np.random.randint(-400, 600)),
                "forage_share": round(55 + np.random.uniform(-5, 10), 1),
                "NDVI":         round(0.35 + np.random.uniform(-0.05, 0.1), 3),
                "fields":       meta["fields"] + np.random.randint(-50, 50),
            })

    return pd.DataFrame(rows)


# ── 3. CROP BREAKDOWN DATA ───────────────────────────────────────────────────
def generate_crop_breakdown() -> pd.DataFrame:
    """
    Returns crop type percentages per region and season.
    
    This is what powers the stacked bar chart (Crop Breakdown).
    """
    rows = []
    seasons = ["Summer", "Winter", "Forage", "Other"]

    for region in REGIONS:
        for season in seasons:
            # Forage dominates in Summer/Forage seasons
            if season == "Summer":
                vals = [65, 15, 12, 8]
            elif season == "Winter":
                vals = [30, 35, 20, 15]
            elif season == "Forage":
                vals = [20, 10, 60, 10]
            else:
                vals = [10, 10, 10, 70]

            rows.append({
                "region":  region,
                "season":  season,
                "Forage":  vals[0] + np.random.randint(-5, 5),
                "Cereals": vals[1] + np.random.randint(-3, 3),
                "Vegetables": vals[2] + np.random.randint(-3, 3),
                "Other":   vals[3] + np.random.randint(-2, 2),
            })

    return pd.DataFrame(rows)


# ── 4. GEOJSON (Simplified bounding boxes for demo) ──────────────────────────
def generate_geojson() -> dict:
    """
    Returns a GeoJSON FeatureCollection with simplified region polygons.
    
    NOTE: Replace with real shapefiles from the client using geopandas:
        import geopandas as gpd
        gdf = gpd.read_file("saudi_regions.shp")
        geojson = json.loads(gdf.to_json())
    """
    features = []
    # Simplified rectangles around each region center (for demo only)
    offsets = 1.5  # degrees

    for region, meta in REGIONS.items():
        lat, lon = meta["lat"], meta["lon"]
        features.append({
            "type": "Feature",
            "properties": {"name": region, "fields": meta["fields"]},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon - offsets, lat - offsets],
                    [lon + offsets, lat - offsets],
                    [lon + offsets, lat + offsets],
                    [lon - offsets, lat + offsets],
                    [lon - offsets, lat - offsets],
                ]]
            }
        })

    return {"type": "FeatureCollection", "features": features}


# ── EXPORT everything as easy-to-use variables ───────────────────────────────
df_timeseries   = generate_timeseries()
df_crop         = generate_crop_breakdown()
geojson_regions = generate_geojson()
region_names    = list(REGIONS.keys())
