/**
 * Tropospheric Ozone Analysis over Punjab, Pakistan
 * --------------------------------------------------
 * Retrieves and analyses tropospheric ozone using Sentinel-5P (TROPOMI),
 * producing a daily time series and a mean spatial composite over a region.
 *
 * Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)
 * Sensor : COPERNICUS/S5P/OFFL/L3_O3
 * Notes  : Reprojection to EPSG:4326 applied to avoid sinusoidal-grid artefacts.
 *          Replace the geometry import with your own AOI asset.
 */

// ------------------------------------------------------------------
// 1. Area of interest (replace with your own boundary asset)
// ------------------------------------------------------------------
var punjab = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
               .filter(ee.Filter.eq('country_na', 'Pakistan'))
               .geometry();

var startDate = '2026-01-01';
var endDate   = '2026-04-01';

// ------------------------------------------------------------------
// 2. Load Sentinel-5P ozone, scale, and clip
// ------------------------------------------------------------------
var o3 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_O3')
           .select('O3_column_number_density')
           .filterDate(startDate, endDate)
           .filterBounds(punjab);

// Convert mol/m^2 to Dobson Units (1 DU = 2.1415e-5 kg/m^2 of O3)
var molToDU = 2241.15; // mol/m^2 -> DU approximate scaling factor

// ------------------------------------------------------------------
// 3. Daily series helper (avoids chart wobble from sub-daily passes)
// ------------------------------------------------------------------
function dailySeries(collection, region, scale) {
  var days = ee.List.sequence(0, ee.Date(endDate).difference(ee.Date(startDate), 'day').subtract(1));
  var imgs = days.map(function (d) {
    var t0 = ee.Date(startDate).advance(d, 'day');
    var t1 = t0.advance(1, 'day');
    var daily = collection.filterDate(t0, t1).mean()
                  .reproject({crs: 'EPSG:4326', scale: scale});
    return daily.set('system:time_start', t0.millis()).set('date', t0.format('YYYY-MM-dd'));
  });
  return ee.ImageCollection.fromImages(imgs);
}

var o3Daily = dailySeries(o3, punjab, 7000);

// ------------------------------------------------------------------
// 4. Time-series chart
// ------------------------------------------------------------------
var chart = ui.Chart.image.series({
  imageCollection: o3Daily.select('O3_column_number_density'),
  region: punjab,
  reducer: ee.Reducer.mean(),
  scale: 7000
}).setOptions({
  title: 'Daily Mean Tropospheric Ozone Column — Punjab',
  vAxis: {title: 'O3 column (mol/m^2)'},
  hAxis: {title: 'Date'},
  lineWidth: 2,
  pointSize: 3
});
print(chart);

// ------------------------------------------------------------------
// 5. Mean spatial composite
// ------------------------------------------------------------------
var o3Mean = o3.mean()
               .reproject({crs: 'EPSG:4326', scale: 7000})
               .clip(punjab);

var vis = {
  min: 0.12, max: 0.16,
  palette: ['blue', 'cyan', 'green', 'yellow', 'orange', 'red']
};

Map.centerObject(punjab, 6);
Map.addLayer(o3Mean, vis, 'Mean O3 column', false);
print('Mean O3 composite ready.');
