# Environmental Remote Sensing & Geospatial Analysis

Scientific programming for environmental monitoring, air quality analysis, and geospatial decision-support built with **Google Earth Engine**, **Python**, and open geospatial libraries.

**Author:** Ehsan Ul Haq GIS Specialist, Environment Protection & Climate Change Department (EP&CCD), Government of Punjab, Pakistan
**Background:** M.Phil. Space Science (CGPA 3.65), University of Punjab · 3 publications · ~10 years in GIS, remote sensing & environmental monitoring
**Contact:** rana42ehsan@gmail.com

---

## Overview

This repository collects working code from my professional and research work in satellite remote sensing and environmental geospatial analysis. The scripts span cloud-based Earth observation (Google Earth Engine), provincial-scale air quality data processing, multi-criteria spatial decision modelling, and GIS interpolation/mapping in Python.

The focus throughout is **turning large environmental and satellite datasets into decision-ready outputs** — maps, indices, trends, and reports — for government and research use.

---

## Repository Structure

```
.
├── google-earth-engine/
│   ├── tropospheric_ozone_analysis.js      # Sentinel-5P (TROPOMI) ozone time-series
│   ├── smog_vulnerability_index.js         # Multi-layer smog vulnerability mapping
│   ├── crop_residue_fire_analysis.js       # MODIS active-fire / crop-burning detection
│   └── cholistan_rainwater_ahp.js          # MCDA/AHP rainwater harvesting site selection
│
├── air-quality-python/
│   ├── aqms_data_processor.py              # AQMS CSV parsing & provincial statistics
│   └── aqi_charts.py                       # Publication-quality AQI/pollutant charts
│
├── gis-python/
│   ├── rbf_noise_interpolation.py          # RBF spatial interpolation + contour mapping
│   └── shapefile_generator.py             # Programmatic shapefile creation (GeoPandas)
│
└── README.md
```

---

## Projects

### 1. Google Earth Engine — Atmospheric & Environmental Analysis

Cloud-based processing of multi-temporal satellite archives for environmental monitoring:

- **Tropospheric Ozone Analysis** — Sentinel-5P (TROPOMI) ozone column retrieval and time-series analysis over Punjab, with reprojection handling and daily compositing.
- **Smog Vulnerability Index** — combines satellite aerosol (MAIAC AOD), fire, and meteorological layers into a weighted vulnerability index, classified by district.
- **Crop Residue Fire Analysis** — MODIS (MYD14A1) active-fire detection for crop-burning seasons, with district-level aggregation sorted by fire count.

### 2. Cholistan Rainwater Harvesting — MCDA / AHP Site Selection

A multi-criteria decision analysis model integrating:
- SRTM-derived slope
- HydroSHEDS flow accumulation
- OpenLandMap soil clay content
- Sentinel-2 NDVI
- Landsat-8 Bare Soil Index

Combined using **Analytic Hierarchy Process (AHP)** weights (flow accumulation 35%, slope 25%, soil 20%, NDVI 12%, dune penalty 8%; consistency ratio ≈ 0.06), exported as GeoTIFF and shapefile at 30 m resolution.

### 3. Air Quality Data Processing (Python)

Tools used to produce monthly provincial air quality reports for the Environmental Monitoring Centre (EMC), EPA Punjab:
- Parsing raw AQMS station CSVs (47+ stations, 6 pollutants)
- Computing per-station and daily provincial means, dominant-pollutant frequency, and PEQS exceedance
- Generating publication-quality matplotlib charts (AQI category bands, PM/gas trends, station rankings)

### 4. GIS Interpolation & Mapping (Python)

- **RBF spatial interpolation** of point measurements (e.g. ambient noise) clipped to administrative boundaries, with contour generation.
- **Programmatic shapefile creation** with full attribute schema, projection, and metadata using GeoPandas.

---

## Tools & Technologies

| Domain | Tools |
|--------|-------|
| Cloud EO | Google Earth Engine (JavaScript API) |
| Languages | Python, JavaScript (GEE), R (basic) |
| Geospatial (Python) | GeoPandas, Shapely, SciPy, Rasterio |
| Visualisation | Matplotlib, NumPy, Pandas |
| Desktop GIS | ArcGIS Pro, QGIS, ESA SNAP, ERDAS IMAGINE |
| Satellite data | Sentinel-1/2/5P, Landsat 8/9, MODIS, SRTM, GRACE |

---

## Selected Publications

- Atmospheric compositions over South Asia — *IJIST* (2021)
- Tropospheric ozone over Saudi Arabia — *IJIST* (2019)
- Water stress on rice crops using remote sensing — *IJASD* (2019)
- GIS-based rice disease identification — M.Sc. thesis (2016)

---

## Note

These scripts are shared as representative samples of scientific programming and geospatial methodology. Some were developed for government deliverables; dataset paths and credentials have been removed or generalised. They are intended to demonstrate methods and coding approach rather than to run unmodified.
