# 🌿 Saudi Crop & Water Monitoring Dashboard

A Streamlit dashboard for visualizing agricultural water use (ET), forage extent,
and crop classification across Saudi regions.

---

## 📁 Project Structure

```
crop_dashboard/
│
├── app.py                  ← MAIN FILE — run this
│
├── data/
│   └── mock_data.py        ← Sample data generator (replace with real CSVs later)
│
├── components/
│   └── charts.py           ← All Plotly chart functions
│
└── requirements.txt        ← Python packages needed
```

---

## 🚀 How to Run

### Step 1 — Install Python packages
```bash
pip install -r requirements.txt
```

### Step 2 — Run the app
```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## 🔄 Swapping in Real Client Data

When the client sends their files, you only need to edit `data/mock_data.py`:

### Replace timeseries CSV:
```python
# Instead of generate_timeseries(), do:
df_timeseries = pd.read_csv("path/to/client_et_data.csv")
```

### Replace GeoJSON:
```python
# Instead of generate_geojson(), do:
import geopandas as gpd
gdf = gpd.read_file("path/to/saudi_regions.shp")
geojson_regions = json.loads(gdf.to_json())
```

The rest of the app will update automatically — no other changes needed.

---

## 📊 Features

- **Interactive map** — choropleth colored by ET intensity
- **Region selector** — switch between Saudi regions
- **Year range slider** — filter 2013–2023
- **Variable checkboxes** — toggle Forage, ET, NDVI, Crop Breakdown
- **KPI cards** — Total ET, ET Intensity, Forage Share, Field count
- **Dual-axis line chart** — ET over time with Forage % overlay
- **Stacked bar chart** — crop breakdown by season
- **Auto-generated summary** — text updates with every filter change
