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

## First attemp in Creating the map

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

5. Dataset use ISO code to represent different countries. In the topojson, different shape can be identified by different standards, e.g. according to sovereign states, map units etc. Luckily, boundary data in the topojson contain the ISO name property for me to match with dataset. The ISO code is also used as the id for each shape in the svg

Using the code from lab, I successfully generate a world map

![](http://ww3.sinaimg.cn/large/006tNbRwgy1felxotz5vij312s0feq5y.jpg)

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
under5 = pd.read_csv("data/Pre-processing/Under5Mortarity.csv")
vaccine = pd.read_csv("data/Pre-processing/vaccine.csv")
incidence = pd.read_csv("data/Pre-processing/incidence.csv")

# Find the number of ISO code covered in each dataset
# ref:https://chrisalbon.com/python/pandas_list_unique_values_in_column.html
print("ISO Code in under5: {0}, vaccine: {1}, incidence: {2}".format(len(under5['ISO Code'].unique()), len(vaccine.ISO_code.unique()), len(incidence.ISO_code.unique())))

# print the intersection of ISO_code of 3 datasets
# ref:http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Index.intersection.html
under5_idx = pd.Index(under5['ISO Code'])
vaccine_idx = pd.Index(vaccine.ISO_code.unique())
incidence_idx = pd.Index(incidence.ISO_code.unique())
common_countries = under5_idx.intersection(vaccine_idx).intersection(incidence_idx)
print(len(common_countries))
```

pandas run on 0.19.2 version which ignores the \ufeff Byte Order Marker at the begining of csv files (ref: https://github.com/pandas-dev/pandas/issues/4793)

Result

```
ISO Code in under5: 196, vaccine: 194, incidence: 194
194
```

Therefore, there are data for 194 unique ISO code in the datasets. As I want to list the countries in a dropdown for people to choose a specific country, I need to compute the intersection of countries in datasets and in the map. Output the ISO list from python

```python
import json
ISO_list_file = open("data/Pre-processing/ISO_list_in_dataset.json", "w")
ISO_list_file.write(json.dumps(list(common_countries.to_series())))
ISO_list_file.close()
```

In the map, `ADM0_A3` is used as the ID of each shape. This is because some of the countries do not have ISO code in the metadata of the shape (UK is divided into England, Wales, Scotland and North Ireland with each shape having no ISO code but they all have the same `ADM0_A3` code `GBR`). I store the `ADM0_A3` code in a list using the following code

```javascript
var ISO_List = [];

// in update code
areas
	.enter()
	...
    .each(function(d) {
        if (ISO_List.indexOf(d.properties.ADM0_A3) === -1) {
            ISO_List.push(d.properties.ADM0_A3)
        }
    })

// in init()
d3.queue()
	...
    .await(function(error, world, ...){
        ...
        draw(world);
		$.getJSON("data/Pre-processing/ISO_list_in_dataset.json", function(data) {
            alert(_.intersection(data, ISO_List))
		})
    })
```

It is found that there are 193 intersection and the result is put back to `ISO_List` for displaying country list.

Next, convertion of ISO code to country names

From https://en.wikipedia.org/wiki/ISO_3166-1, I got the conversion table of ISO code to country names and then convert to json file with the following code

```python
import csv
ISO2Names = {}
with open("data/Pre-processing/ISO2Names.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        ISO2Names[row[0]] = row[1]
ISO2Name_File = open("data/Pre-processing/ISO2Name.json", "w")
ISO2Name_File.write(json.dumps(ISO2Names))
ISO2Name_File.close()
```

Now, there are common keys for the data to match. 

Then, the datasets have to be filtered.

```python
under5_filtered = under5.loc[under5['ISO Code'].isin(common_countries)]
vaccine_filtered = vaccine.loc[vaccine.ISO_code.isin(common_countries)]
incidence_filtered = incidence.loc[incidence.ISO_code.isin(common_countries)]
```

Under 5 mortarity dataset contains many zeros and they should be converted to `NaN` by the following code

```python
import numpy as np
under5_filtered = under5_filtered.replace(0.0, np.nan)
```

Now the data are prepared for d3.js to read



Time series, missing data. Interpolate



## Visualisation Work

I want to use a colour scale to visualise the mortarity rates. I have to decide between a continuous colour scale and discrete colour scale. This answer https://gis.stackexchange.com/a/86679 in stackexchange gives me a clear guide in choosing between the two. The pros and cons of the two are listed below

### Continuous Colour Scale (un-classed map)

#### Pros

- Accurate

#### Cons

- Sensitive to outlier
- Human perception to colour is not linear

### Discrete Colour Scale (maps with 'bins')

#### Pros

- Robust to outliers
- Colours can be perceived clearly and distinctly

#### Cons

- Data lost

Therefore, discrete colour scale is employed.

Plot the histogram of the value of data

```python
import matplotlib
import matplotlib.pyplot as plt
%matplotlib inline
matplotlib.style.use('ggplot')
under5_filtered.plot.hist()
```

![](http://ww4.sinaimg.cn/large/006tNbRwgy1fevpq42771j30as071dgf.jpg)

A majority of the lies between 0 - 50 interval and the code

```python
under5.max(numeric_only=True).max()
```

the maximum value of the whole dataset is 443.5.

In order to compare data across different years, I used a consistent colour scale throughout the time period. 

After passing the data using D3.js, I got the choropleth map for 2015 mortarity rate as follow

![](http://ww1.sinaimg.cn/large/006tNbRwgy1fewu5tsu4cj30q20acmyh.jpg)





MaterializeCSS is used as the webpage framework

![](http://ww1.sinaimg.cn/large/006tNbRwgy1fexy6xcayjj31400kb0v3.jpg)

Prototype of the visualisation with MaterializeCSS. Left hand side is the setting panel and allow user to select country to display and on the right  hand side the details of the country selected. The map is in the central panel and the blank space below the map is planned to show the vaccination rate across the year. I planned to show everything in the screen without scrolling. However, I find it impractical as the map dimensions are in fixed ratio and hence only certain width:height ratio of the browser window can show the remaining graph clearly