"""
AQMS Air Quality Data Processor
-------------------------------
Parses raw Air Quality Monitoring Station (AQMS) CSV exports and computes
provincial statistics used in monthly air quality reports for the
Environmental Monitoring Centre (EMC), EPA Punjab.

Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)

Input  : Wide-format CSV where columns are "<Station> • <Parameter>"
Output : Per-station monthly means, daily provincial means, dominant-pollutant
         frequency, and PEQS exceedance flags.
"""

import re
import numpy as np
import pandas as pd

# Punjab Environmental Quality Standards (24-hr / relevant averaging limits)
PEQS = {
    "PM2.5 (µg/m3)": 35,
    "PM10 (µg/m3)": 150,
    "O3 (µg/m3)": 130,
    "SO2 (µg/m3)": 120,
    "NO2 (µg/m3)": 40,
    "CO (mg/m³)": 5,
}

PARAMS = ["AQI", "PM2.5 (µg/m3)", "PM10 (µg/m3)", "O3 (µg/m3)",
          "SO2 (µg/m3)", "NO2 (µg/m3)", "CO (mg/m³)"]


def load_month(csv_path: str, year_month: str) -> pd.DataFrame:
    """Load a CSV and keep rows for the given YYYY-MM period."""
    df = pd.read_csv(csv_path, low_memory=False)
    pattern = rf"{year_month}-\d{{2}}"
    data = df[df["Time"].astype(str).str.match(pattern, na=False)].copy()
    data["Time"] = pd.to_datetime(data["Time"])
    data = data.sort_values("Time").reset_index(drop=True)
    data["day"] = data["Time"].dt.day
    return data


def list_stations(df: pd.DataFrame) -> list:
    """Extract unique station names from the wide-format columns."""
    return sorted({c.split(" • ")[0] for c in df.columns if " • " in c})


def station_values(data: pd.DataFrame, station: str, param: str) -> pd.Series:
    col = f"{station} • {param}"
    if col in data.columns:
        return pd.to_numeric(data[col], errors="coerce").dropna()
    return pd.Series([], dtype=float)


def provincial_means(data: pd.DataFrame, stations: list) -> dict:
    """Mean across all stations and days for each parameter."""
    out = {}
    for p in PARAMS:
        vals = []
        for st in stations:
            vals.extend(station_values(data, st, p).tolist())
        out[p] = round(float(np.mean(vals)), 1) if vals else None
    return out


def station_table(data: pd.DataFrame, stations: list) -> pd.DataFrame:
    """Per-station monthly means, ranked by AQI (active stations only)."""
    rows = []
    for st in stations:
        row = {"Station": st}
        for p in PARAMS:
            v = station_values(data, st, p)
            row[p] = round(float(v.mean()), 1) if len(v) else None
        rows.append(row)
    table = pd.DataFrame(rows)
    table = table[table["AQI"].notna()]
    return table.sort_values("AQI", ascending=False).reset_index(drop=True)


def daily_provincial(data: pd.DataFrame, stations: list, param: str) -> list:
    """Daily provincial mean series for one parameter."""
    series = []
    for _, grp in data.groupby("day"):
        vals = []
        for st in stations:
            col = f"{st} • {param}"
            if col in data.columns:
                vals.extend(pd.to_numeric(grp[col], errors="coerce").dropna().tolist())
        series.append(round(float(np.mean(vals)), 1) if vals else None)
    return series


def dominant_frequency(data: pd.DataFrame, stations: list) -> pd.Series:
    """Frequency of each pollutant being the dominant driver (station-days)."""
    counts = {}
    for st in stations:
        col = f"{st} • Dominant"
        if col in data.columns:
            for v in data[col].dropna():
                v = str(v).strip()
                if v and v != "nan":
                    counts[v] = counts.get(v, 0) + 1
    total = sum(counts.values()) or 1
    return (pd.Series(counts).sort_values(ascending=False) / total * 100).round(1)


def exceedance_flags(means: dict) -> pd.DataFrame:
    """Compare provincial means against PEQS limits."""
    rows = []
    for param, limit in PEQS.items():
        val = means.get(param)
        if val is None:
            continue
        rows.append({
            "Parameter": param,
            "Mean": val,
            "PEQS": limit,
            "Ratio": round(val / limit, 2),
            "Status": "EXCEEDS" if val > limit else "Within",
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Example usage
    data = load_month("March_2026_AQMS.csv", "2026-03")
    stations = list_stations(pd.read_csv("March_2026_AQMS.csv", nrows=1))

    means = provincial_means(data, stations)
    print("Provincial means:", means)

    table = station_table(data, stations)
    print(f"\nActive stations: {len(table)}")
    print(table.head(10).to_string(index=False))

    print("\nDominant pollutant frequency (%):")
    print(dominant_frequency(data, stations).to_string())

    print("\nPEQS exceedance:")
    print(exceedance_flags(means).to_string(index=False))
