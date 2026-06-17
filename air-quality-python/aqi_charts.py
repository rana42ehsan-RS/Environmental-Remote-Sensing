"""
Air Quality Chart Generator
---------------------------
Produces publication-quality charts (AQI category bands, PM trends, station
rankings) from processed AQMS data for monthly EPA Punjab reports.

Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)
"""

import numpy as np
import matplotlib.pyplot as plt

AQI_BANDS = [
    (0, 50, "#16a34a", "Good"),
    (50, 100, "#ca8a04", "Moderate"),
    (100, 150, "#ea580c", "Sensitive"),
    (150, 200, "#dc2626", "Unhealthy"),
    (200, 300, "#9333ea", "Very Unhealthy"),
    (300, 500, "#7e1f1f", "Hazardous"),
]


def plot_daily_aqi(days, aqi, month_label, out_path="aqi_trend.png"):
    """Daily AQI line over coloured health-category bands."""
    fig, ax = plt.subplots(figsize=(13, 4.5), facecolor="white")
    for lo, hi, color, _ in AQI_BANDS:
        ax.axhspan(lo, hi, alpha=0.09, color=color)
    ax.plot(days, aqi, color="#1e293b", lw=2.5, marker="o", ms=5,
            mfc="white", mec="#1e293b", mew=1.5, zorder=5)
    ax.set_ylabel("AQI")
    ax.set_title(f"Daily AQI — Provincial Mean | {month_label}",
                 fontweight="bold")
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_station_ranking(stations, aqi_values, out_path="station_ranking.png"):
    """Horizontal bar chart of stations ranked by AQI."""
    order = np.argsort(aqi_values)
    names = [stations[i] for i in order]
    vals = [aqi_values[i] for i in order]
    colors = ["#9333ea" if v >= 200 else "#dc2626" if v >= 150
              else "#ea580c" for v in vals]

    fig, ax = plt.subplots(figsize=(10, 7), facecolor="white")
    ax.barh(names, vals, color=colors, height=0.72, edgecolor="white")
    for i, v in enumerate(vals):
        ax.text(v + 2, i, f"{v}", va="center", fontsize=8, fontweight="bold")
    ax.axvline(150, color="#dc2626", lw=1.5, ls="--", label="AQI 150")
    ax.set_xlabel("Monthly Average AQI")
    ax.legend(fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    days = list(range(1, 32))
    demo_aqi = list(np.linspace(210, 100, 31))
    plot_daily_aqi(days, demo_aqi, "March 2026")
    plot_station_ranking(["UET", "LWMC", "FMDRC", "PKLI", "Chakwal"],
                         [192, 237, 176, 151, 94])
    print("Charts generated.")
