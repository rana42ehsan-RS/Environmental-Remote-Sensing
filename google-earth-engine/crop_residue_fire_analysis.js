/**
 * Crop Residue Fire Analysis — Punjab
 * -----------------------------------
 * Detects active fires from MODIS (crop-burning seasons) and aggregates fire
 * counts by district, sorted highest to lowest.
 *
 * Author : Ehsan Ul Haq (GIS Specialist, EP&CCD Punjab)
 * Asset  : MODIS/061/MYD14A1 (Aqua, daily, 1 km) — publicly accessible
 */

var districts = ee.FeatureCollection('FAO/GAUL/2015/level2')
                  .filter(ee.Filter.eq('ADM1_NAME', 'Punjab'));

var fires = ee.ImageCollection('MODIS/061/MYD14A1')
              .select('FireMask')
              .filterDate('2025-10-01', '2025-12-31')
              .map(function (img) {
                // Classes 7,8,9 = low/nominal/high-confidence fire
                return img.gte(7).rename('fire')
                          .copyProperties(img, ['system:time_start']);
              });

var fireSum = fires.sum().unmask(0)
                .reproject({crs: 'EPSG:4326', scale: 1000})
                .rename('fire_count');

var byDistrict = fireSum.reduceRegions({
  collection: districts,
  reducer: ee.Reducer.sum(),
  scale: 1000
}).sort('sum', false);   // highest fire count first

print('Fire counts by district (high to low):', byDistrict);

var chart = ui.Chart.feature.byFeature(byDistrict.limit(15), 'ADM2_NAME', 'sum')
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Active Fire Counts by District (Top 15)',
    hAxis: {title: 'District', slantedText: true},
    vAxis: {title: 'Fire pixel count'},
    legend: {position: 'none'},
    colors: ['#c0392b']
  });
print(chart);

Map.centerObject(districts, 7);
Map.addLayer(fireSum.clip(districts),
  {min: 0, max: 20, palette: ['white', 'yellow', 'orange', 'red', 'darkred']},
  'Fire density');
