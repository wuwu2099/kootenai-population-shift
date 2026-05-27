# Kootenai County Population Shift Analysis (2000–2024)

## Project Overview

This project analyzes the spatial shift of population distribution in Kootenai County, Idaho from 2000 to 2024 using U.S. Census tract-level population data and Cartographic boundary files.

The project combines:
- Census API population data
- Cartographic boundary files
- Spatial joins and choropleth mapping
- Population-weighted center calculations
- Temporal movement analysis

---

## Objectives

- Visualize tract-level population distribution patterns
- Calculate population-weighted centers
- Measure spatial movement of population centers
- Build a reproducible GIS workflow in Python

---

## Tools and Libraries

- Python
- GeoPandas
- Pandas
- Matplotlib
- Shapely
- requests
- pathlib
- zipfile

---

## Workflow

1. Download census tract shapefiles (cartographic boundary files)
2. Collect tract population data using Census API
3. Standardize GEOID fields
4. Join population data to tract geometries
5. Reproject to projected CRS (EPSG:26911)
6. Map population distribution across census tracts 
7. Calculate population-weighted centers
8. Visualize spatial movement of population centers over time
9. Animated temporal maps of population shift

---

## Outputs

### Choropleth Maps

(Add image later)

### Population Center Shift

(Add image later)

---

## Technical Components

- Census API integration
- GIS spatial analysis
- GeoPandas workflows
- Coordinate system handling
- Spatial-temporal visualization
- Data cleaning and standardization

---

