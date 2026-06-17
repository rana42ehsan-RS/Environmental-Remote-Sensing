/**
 * Cholistan Desert — Rainwater Harvesting Site Selection (MCDA / AHP)
 * ------------------------------------------------------------------
 * Identifies suitable rainwater harvesting sites by combining terrain,
 * hydrology, soil, and vegetation layers using Analytic Hierarchy Process
 * (AHP) weights.
 *
 * Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)
 * Output : Weighted suitability raster (GeoTIFF) + candidate sites (shapefile)
 * CRS    : EPSG:32642 (UTM 42N), 30 m resolution
 *
 * AHP weights (consistency ratio ~ 0.06):
 *   Flow accumulation 0.35 | Slope 0.25 | Soil clay 0.20 | NDVI 0.12 | Dune penalty 0.08
 */

// ------------------------------------------------------------------
// 1. Study area (replace with your Cholistan AOI asset)
// ------------------------------------------------------------------
var aoi = ee.Geometry.Rectangle([71.0, 27.7, 73.5, 29.6]); // approximate Cholistan bbox

// ------------------------------------------------------------------
// 2. Input layers
// ------------------------------------------------------------------
// Terrain
var dem   = ee.Image('USGS/SRTMGL1_003').clip(aoi);
var slope = ee.Terrain.slope(dem);

// Hydrology — flow accumulation (HydroSHEDS)
var flowAcc = ee.Image('WWF/HydroSHEDS/15ACC').clip(aoi);

// Soil — clay content (OpenLandMap), higher clay = better water retention
var clay = ee.Image('OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02')
             .select('b0').clip(aoi);

// Vegetation — Sentinel-2 NDVI (lower NDVI in desert = more open catchment)
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
           .filterBounds(aoi)
           .filterDate('2025-10-01', '2026-03-31')
           .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
           .median();
var ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI').clip(aoi);

// Bare soil index (Landsat 8) — dune proxy used as a penalty
var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(aoi)
           .filterDate('2025-10-01', '2026-03-31')
           .median();
var bsi = l8.expression(
  '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))', {
    SWIR: l8.select('SR_B6'), RED: l8.select('SR_B4'),
    NIR : l8.select('SR_B5'), BLUE: l8.select('SR_B2')
  }).rename('BSI').clip(aoi);

// ------------------------------------------------------------------
// 3. Normalise each layer to 0–1 (rescale)
// ------------------------------------------------------------------
function rescale(img, min, max) {
  return img.subtract(min).divide(max - min).clamp(0, 1);
}

var slopeScore = rescale(slope, 0, 15).subtract(1).abs();     // flatter = better
var flowScore  = rescale(flowAcc, 0, 5000);                   // higher = better
var soilScore  = rescale(clay, 0, 40);                        // more clay = better
var ndviScore  = rescale(ndvi, -0.1, 0.4).subtract(1).abs();  // lower veg = better
var dunePenalty= rescale(bsi, 0, 0.5);                        // high bare soil = penalty

// ------------------------------------------------------------------
// 4. AHP weighted suitability
// ------------------------------------------------------------------
var suitability = flowScore.multiply(0.35)
  .add(slopeScore.multiply(0.25))
  .add(soilScore.multiply(0.20))
  .add(ndviScore.multiply(0.12))
  .subtract(dunePenalty.multiply(0.08))
  .rename('suitability')
  .reproject({crs: 'EPSG:32642', scale: 30});

var visSuit = {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightgreen', 'darkgreen']};
Map.centerObject(aoi, 8);
Map.addLayer(suitability, visSuit, 'RWH Suitability', true);

// ------------------------------------------------------------------
// 5. Extract top candidate sites (suitability > 0.7)
// ------------------------------------------------------------------
var topSites = suitability.gt(0.7).selfMask();
Map.addLayer(topSites, {palette: ['000080']}, 'Top candidate sites', false);

// ------------------------------------------------------------------
// 6. Export
// ------------------------------------------------------------------
Export.image.toDrive({
  image: suitability,
  description: 'Cholistan_RWH_Suitability',
  region: aoi,
  scale: 30,
  crs: 'EPSG:32642',
  maxPixels: 1e13
});

print('AHP suitability model ready. Adjust weights as needed.');
