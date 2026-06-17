"""
RBF Spatial Interpolation of Point Measurements
-----------------------------------------------
Interpolates point measurements (e.g. ambient noise levels) across a study
area using Radial Basis Function (multiquadric) interpolation, clips the
surface to an administrative boundary, and draws contour lines.

Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)
Method : scipy.interpolate.Rbf (multiquadric) + Gaussian smoothing
CRS    : WGS84 (EPSG:4326)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
from scipy.ndimage import gaussian_filter
from shapely.geometry import Point, Polygon
from shapely.vectorized import contains


def interpolate_surface(lons, lats, values, bbox, resolution=200,
                        smooth=0.8, sigma=5, clip_range=None):
    """
    Build an interpolated surface over a bounding box.

    Parameters
    ----------
    lons, lats, values : array-like   point coordinates and measured values
    bbox               : (minlon, minlat, maxlon, maxlat)
    resolution         : grid size per axis
    smooth, sigma      : RBF smoothing and Gaussian filter strength
    clip_range         : optional (vmin, vmax) to clamp interpolated values

    Returns
    -------
    glon, glat, grid   : meshgrid arrays and the interpolated surface
    """
    minlon, minlat, maxlon, maxlat = bbox
    glon, glat = np.meshgrid(
        np.linspace(minlon, maxlon, resolution),
        np.linspace(minlat, maxlat, resolution),
    )

    rbf = Rbf(lons, lats, values, function="multiquadric",
              smooth=smooth, epsilon=0.05)
    grid = rbf(glon, glat)
    grid = gaussian_filter(grid, sigma=sigma)

    if clip_range:
        grid = np.clip(grid, *clip_range)

    return glon, glat, grid


def clip_to_boundary(glon, glat, grid, boundary: Polygon):
    """Mask grid cells that fall outside the boundary polygon."""
    inside = contains(boundary, glon.ravel(), glat.ravel())
    mask = ~inside.reshape(grid.shape)
    return np.ma.masked_array(grid, mask=mask)


def plot_surface(glon, glat, grid, boundary, points, contour_levels,
                 out_path="interpolated_map.png", cmap="RdYlGn_r"):
    """Render the interpolated surface with boundary, points and contours."""
    fig, ax = plt.subplots(figsize=(11, 9), facecolor="white")

    extent = [glon.min(), glon.max(), glat.min(), glat.max()]
    ax.imshow(grid, extent=extent, origin="lower", cmap=cmap,
              alpha=0.7, aspect="auto", interpolation="bicubic")

    # Boundary outline
    bx, by = boundary.exterior.xy
    ax.plot(bx, by, color="#0f172a", lw=2.5, zorder=5)

    # Contours
    cs = ax.contour(glon, glat, grid, levels=contour_levels,
                    colors="black", linewidths=1.0, alpha=0.7)
    ax.clabel(cs, fmt="%1.0f", fontsize=8)

    # Measurement points
    for lon, lat, val in points:
        ax.scatter(lon, lat, s=90, color="white", edgecolors="black",
                   linewidths=1.2, zorder=6)
        ax.text(lon, lat, f"{val:.0f}", fontsize=7, ha="center",
                va="center", zorder=7)

    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("RBF Multiquadric Interpolation", fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    # Example: noise measurements with simple demo coordinates
    points = [
        (74.21, 31.31, 71.4), (74.20, 31.30, 71.4), (74.22, 31.32, 73.6),
        (74.18, 31.30, 76.4), (74.30, 31.55, 79.8), (74.31, 31.58, 78.9),
    ]
    lons = np.array([p[0] for p in points])
    lats = np.array([p[1] for p in points])
    vals = np.array([p[2] for p in points])

    bbox = (74.15, 31.28, 74.35, 31.60)
    boundary = Polygon([
        (74.15, 31.28), (74.35, 31.28), (74.35, 31.60),
        (74.15, 31.60), (74.15, 31.28),
    ])

    glon, glat, grid = interpolate_surface(lons, lats, vals, bbox,
                                           clip_range=(68, 83))
    grid_m = clip_to_boundary(glon, glat, grid, boundary)
    plot_surface(glon, glat, grid_m, boundary, points,
                 contour_levels=[70, 75, 78, 80])
