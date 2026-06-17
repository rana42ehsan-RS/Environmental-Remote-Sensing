"""
Shapefile Generator
-------------------
Programmatically creates an ESRI Shapefile from point measurements with a full
attribute schema, projection (.prj), and basic metadata using GeoPandas.

Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)
CRS    : WGS84 (EPSG:4326)
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def build_point_shapefile(records, out_path):
    """
    records : list of dicts with keys including 'Lat', 'Lon' plus attributes
    out_path: output .shp path
    """
    df = pd.DataFrame(records)
    df["geometry"] = df.apply(lambda r: Point(r["Lon"], r["Lat"]), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    gdf = gdf.drop(columns=["Lat", "Lon"])
    gdf.to_file(out_path, driver="ESRI Shapefile", encoding="utf-8")
    print(f"Shapefile written: {out_path} ({len(gdf)} features)")
    return gdf


if __name__ == "__main__":
    records = [
        {"Sr": 1, "Location": "Site A", "Lat": 31.31, "Lon": 74.21,
         "Value": 71.4, "Status": "Exceeds"},
        {"Sr": 2, "Location": "Site B", "Lat": 31.55, "Lon": 74.30,
         "Value": 79.8, "Status": "Exceeds"},
    ]
    build_point_shapefile(records, "monitoring_points.shp")
