# README.MD

The steps I used to create this visualisation

## Datasets

I found 3 datasets related to children health. Namely:

1. Under 5 Mortarity in countries across the world from UNICEF
2. Vaccine coverage across the world from WHO
3. Vaccine curable diseases incident rate across the world from WHO

I believe these data are related and hope to provide evidence that vaccine is effective in saving children's lives

## Do I really need a map?

My datasets contain geographic information. It is intuitive to think to visualise them on a map. However, is the location matter in telling the story? Will 2D scatter plot or bar charts enough to deliver the message? Deepter consideration is needed in finalising the design. 

The objective of the visualisation in to investigate the effectiveness of vaccine in saving children's lives. If I were to visualise the data in a map, it would be better to show the result, i.e. the under 5 mortality rates, on it. The next question is, do I really need a map? The mortarity rates much lower in developed countries and higher in developing countries. These two types of countries are geographically distributed. Europe and North America are well developed while Africa and part of Asia are still developing. In addition, the data span across years. Visualising on a map can show the trend and the distribution across the globe.

To make the whole visulaisation easy to follow, only one dataset is shown on a map while the other two will be shown using line charts.

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

5. Data use ISO code to represent different countries. In the topojson, different shape can be identified by different standards, e.g. according to sovereign states, map units etc. Luckily, boundary data in the topojson contain the ISO name property so I do not have to convert/combine boundaries



## Analysing Data

Got the data for vaccine coverage, disease incidence, under 5 child motarity rate

check http://www.who.int/immunization/diseases/en/ for correspoinding vaccines, disease pairs

### Preprocessing

All data given were in spreadsheet format. Combine sheets into the same sheet and then save as csv format.

Under 5 mortarity rate is in reversed column order as vaccine coverage and disease incidence rate. It is reversed in excel.

Under 5 mortarity rate is the Probability of dying between birth and exactly 5 years of age, expressed per 1,000 live births. ( https://data.unicef.org/topic/child-survival/under-five-mortality/ )

I got the dataset from 2 sources, vaccine coverage and vaccine curible diseases incidence rate from WHO and under 5 martarity rate from UNICEF. All 3 datasets contains worldwide data. Have to check if they cover the same set of countries/regions.

```python
import pandas as pd
under5 = pd.read_csv("data/Under5Mortarity.csv")
vaccine = pd.read_csv("data/vaccine.csv")
incidence = pd.read_csv("data/incidence.csv")

# Find the number of countries covered in each dataset
# ref:https://chrisalbon.com/python/pandas_list_unique_values_in_column.html
print("Countries in under5: {0}, vaccine: {1}, incidence: {2}".format(len(under5['Country Name'].unique()), len(vaccine.Cname.unique()), len(incidence.Cname.unique())))

# print the intersection of countries of 3 datasets
# ref:http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Index.intersection.html
under5_idx = pd.Index(under5['Country Name'])
vaccine_idx = pd.Index(vaccine.Cname.unique())
incidence_idx = pd.Index(incidence.Cname.unique())
common_countries = under5_idx.intersection(vaccine_idx).intersection(incidence_idx)
print(len(common_countries))
```

pandas run on 0.19.2 version which ignores the \ufeff Byte Order Marker at the begining of csv files