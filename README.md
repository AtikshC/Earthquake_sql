# Real‑Time Earthquake Monitoring & Alert System

**Fetch and store 5 years of historical + live earthquake data from USGS into SQLite.**

![Earthquake](https://earthquake.usgs.gov/favicon.ico)

## 🚀 Overview

This Python script ingests  
1. All earthquakes in the past **5 years** (in 7‑day chunks),  
2. The latest hour’s events,  
and stores them in a local `earthquakes.db` SQLite database.  
You can then query, dashboard, or alert on any magnitude or timeframe.

## ⚙️ Features

- Bulk‐fetch historical data in manageable windows to avoid API limits  
- Real‑time hourly updates via USGS GeoJSON feed  
- De‐duplication via `INSERT OR IGNORE`  
- Summary reports: total count, top 10 magnitudes, recent major quakes  

## 🛠 Prerequisites

- Python 3.7 or newer  
- [requests](https://pypi.org/project/requests/)  

```bash
pip install requests
