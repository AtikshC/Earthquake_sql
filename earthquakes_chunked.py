#!/usr/bin/env python3
import requests
import sqlite3
import datetime
import time
import sys

# ─ CONFIG ──────────────────────────────────────────────────────────────────────
YEARS_BACK   = 5
WINDOW_DAYS  = 7         # chunk size (days) for history fetch
MIN_MAGNITUDE = 1.0      # drop very tiny tremors to reduce payload
SQLITE_DB    = "earthquakes.db"
FDSN_URL     = "https://earthquake.usgs.gov/fdsnws/event/1/query"
HOURLY_URL   = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
MAX_RETRIES  = 3
RETRY_DELAY  = 5         # seconds between retries
# ────────────────────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(SQLITE_DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS Earthquakes (
      eq_id TEXT PRIMARY KEY,
      magnitude REAL,
      place TEXT,
      event_time TEXT,
      latitude REAL,
      longitude REAL,
      depth_km REAL,
      url TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    return conn, c

def safe_get(url, params=None):
    """GET with simple retry on disconnects or server hiccups."""
    for attempt in range(1, MAX_RETRIES+1):
        try:
            return requests.get(url, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Request error ({e}), retry {attempt}/{MAX_RETRIES}…")
            time.sleep(RETRY_DELAY)
    print("❌  Failed after retries; exiting.")
    sys.exit(1)

def fetch_historical(years, window_days, min_mag):
    today = datetime.datetime.utcnow().date()
    start = today - datetime.timedelta(days=365 * years)
    all_feats = []
    cur = start

    print(f"[1/2] Fetching {years}‑year history in {window_days}‑day windows…")
    while cur < today:
        end = min(cur + datetime.timedelta(days=window_days), today)
        params = {
            "format":      "geojson",
            "starttime":   cur.isoformat(),
            "endtime":     end.isoformat(),
            "minmagnitude": min_mag,
        }
        print(f"  • window {cur} → {end} …", end="", flush=True)
        resp = safe_get(FDSN_URL, params=params)
        resp.raise_for_status()
        feats = resp.json().get("features", [])
        print(f" {len(feats)} events")
        all_feats.extend(feats)
        cur = end
    return all_feats

def fetch_hourly():
    print("[2/2] Fetching last hour’s feed …", end="", flush=True)
    resp = safe_get(HOURLY_URL)
    resp.raise_for_status()
    feats = resp.json().get("features", [])
    print(f" {len(feats)} events")
    return feats

def parse_features(features):
    rows = []
    for f in features:
        props = f["properties"]
        evt_time = datetime.datetime.fromtimestamp(
            props["time"]/1000,
            datetime.timezone.utc
        ).isoformat()
        lon, lat, depth = f["geometry"]["coordinates"]
        rows.append((
            f["id"],
            props.get("mag"),
            props.get("place"),
            evt_time,
            lat, lon, depth,
            props.get("url")
        ))
    return rows

def upsert(c, rows):
    c.executemany("""
    INSERT OR IGNORE INTO Earthquakes
      (eq_id, magnitude, place, event_time, latitude, longitude, depth_km, url)
    VALUES (?,?,?,?,?,?,?,?);
    """, rows)

def summarize(c):
    total = c.execute("SELECT COUNT(*) FROM Earthquakes").fetchone()[0]
    print(f"\n✅ Total quakes recorded: {total:,}")

    print("\nTop 10 by magnitude:")
    for mag, place, evt in c.execute("""
      SELECT magnitude, place, event_time
        FROM Earthquakes
       ORDER BY magnitude DESC
       LIMIT 10;
    """):
        print(f"  • M{mag} @ {place} on {evt}")

    day_ago = (datetime.datetime.now(datetime.timezone.utc) -
               datetime.timedelta(days=1)).isoformat()
    print("\nMajor quakes (M ≥ 5.5 in last 24 h):")
    found = False
    for mag, place, evt in c.execute("""
      SELECT magnitude, place, event_time
        FROM Earthquakes
       WHERE magnitude >= 5.5
         AND event_time >= ?
       ORDER BY magnitude DESC;
    """, (day_ago,)):
        print(f"  • M{mag} @ {place} on {evt}")
        found = True
    if not found:
        print("  (none)")

def main():
    conn, c = init_db()

    hist_feats = fetch_historical(YEARS_BACK, WINDOW_DAYS, MIN_MAGNITUDE)
    rows_hist  = parse_features(hist_feats)
    upsert(c, rows_hist)
    conn.commit()
    print(f"Inserted {len(rows_hist)} historical events.")

    hour_feats = fetch_hourly()
    rows_hour  = parse_features(hour_feats)
    upsert(c, rows_hour)
    conn.commit()
    print(f"Inserted {len(rows_hour)} new hourly events.")

    summarize(c)
    conn.close()

if __name__ == "__main__":
    main()
