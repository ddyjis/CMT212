# README.MD

The steps I used to create this visualisation

## Creating the map

http://www.tnoda.com/blog/2013-12-07

### Get Geo Data

1. get 1:10m Cultural Vectors of Countries data from http://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-details/

2. install GDAL and Topojson to convert shapefiles to GeoJSON and then to Topojson.
   1. GeoJSON and Topojson can be easily passed to Javascript

   2. I could also select to exclude Antartica

   3. The GeoJSON generated is 23.8 MB in size which is not appropriate for webpages

   4. Topojson could have smaller file size so it is chosen to be the file format for geo data

      1. According to http://stackoverflow.com/questions/16628638/how-to-run-topojson, topojson executible is now changed to geo2topo. However, after checking `-h`, there is no attribute picking function as desctibed in tnoda.com
      2. However, the topojson file created is 19.3 MB which is still very large

   5. ```bash
      ogr2ogr -f GeoJSON -where "su_a3 <> 'ATA'" countries.json ne_10m_admin_0_map_units.shp
      ```

   6. ```bash
      geo2topo -o countries.topo.json countries.json
      ```

3. use http://www.mapshaper.org/ to simplify the geo data while preserving the shape of each countries

   1. import the `countries.topo.json` and simplify it to 10%
   2. the resulting topojson file is 676 KB which is suitable for web

4. http://jsonviewer.stack.hu/ is useful in displaying the structure of JSON 

5. Data use ISO code to represent different countries. In the topojson, different shape can be identified by different standards, e.g. according to sovereign states, map units etc. 



## Analysing Data

Got the data for vaccine coverage, disease incidence, under 5 child motarity rate

check http://www.who.int/immunization/diseases/en/ for correspoinding vaccines, disease pairs

### Vaccine and targeted disease

