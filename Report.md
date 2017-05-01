# Report

## Introduction

This visualisation intends to explore the relationship between vaccine coverage and the mortality rates of children under 5 years old. 

### Datasets

2 Datasets are used for this visualisation. They are the [World Immunisation Coverage](http://www.who.int/entity/immunization/monitoring_surveillance/data/coverage_series.xls?ua=1) from WHO and [Global Child Mortality Rate](https://data.unicef.org/wp-content/uploads/2015/12/U5MR_mortality_rate_39.xlsx) from UNICEF. In addition, I also used the geo data from [Natural Earth](http://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-details/)

- Immunisation data: located in `data/Raw/coverage_series.xls`, contains the adoption of 20 vaccine in 194 countries in years between 1980 and 2015.
- Child Mortality Rate: located in `data/Raw/U5MR_mortality_rate_39.xlsx`, conatins the estimates of child mortality rate in 197 countries in years between 1950 and 2015
- Geo data: located in `data/Raw/GeoData`, is a 1:10m Cultural Vector of Countries data in shapefile format.

### Visualisation

My visualisation use D3.js v4 combined with jQuery and underscore.js. It consist of 3 parts. The first part is a world map showing the mortality rates across the globe.

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff52cksov1j30rr0j5ac7.jpg)

The mortality rate is represented by different gradient of reds. Countries that have no data are represented in pale white. Users can hovor the countries and a tooltip showing the country name and the mortality rate will appear. There is also a slider for user to select the year. When pressing the play button, the year will increase in regular interval so as to visualise the changes in child death over time. Audience can select a country to investigate from the dropdown list or by clicking the country on the map.

The second part is a grid of donut charts. When a country is selected, the page is scrolled to these charts. 

![](http://ww1.sinaimg.cn/large/006tNbRwgy1ff52ek6z1bj30qx0jcjty.jpg)

Each of these donut chart shows the corresponding vaccine coverage of selected country. If the country never adopt a certain vaccine, the vaccine is not shown. If no data is available for that vaccine in that year, there will be no donut but a no data statement. Users can choose a vaccine by clicking.

The third part is the time series plot showing the trends of vaccine coverage and child death rate over time.

![](http://ww3.sinaimg.cn/large/006tNbRwgy1ff52zf0rdzj30rh0hvdi0.jpg)

Vaccine is shown in green and mortality is shown in red. Data points are connected by smooth lines. If there is no data in some years, the line is shown in different segments. When users hover on a data point, a tooltip appears showing the year and data for that point.

## Development of the Visualisation

### Data Preparation

#### Datasets

Raw dataset from the source at in `data/Raw`  in Excel spreadsheet format. I manually converted them to CSV format. They were then pre-processed using Pandas. The codes could be seen in `preprocessing.py` or `preprocessing.ipynb`

Since the data are from different sources, I found the common ISO between the dataset with Pandas. There were 194 countries in common and they were outputted to `data/Pre-processing/ISO_list_in_dataset.json` file for the visualisation to read.

#### Geo Data

With reference to this [blog](http://www.tnoda.com/blog/2013-12-07), I converted the shapefile downloaded to TopoJSON format which could be easily passed to Javascipt. I create my own TopoJSON from shapefile instead of using pre-existing JSON files because I have higher freedom in manipulating the JSON like I can exclude Anatartica during convertion using the code

```bash
ogr2ogr -f GeoJSON -where "su_a3 <> 'ATA'" countries.json ne_10m_admin_0_map_units.shp
geo2topo -o countries.topo.json countries.json
```

The TopoJSON generated was 19.3 MB which was not appropriate for webpages. I used [mapshaper](http://www.mapshaper.org/) to simplify geo data and the resulting TopoJSON file was 676 KB which was acceptable for web.

There were many attributes associated with the shapes. I tried `ISO_A3` and `ADM0_A3` as the id of each shape. `ISO_A3` divided UK into 4 different regions and neither of each matched with the ISO code of the UK. `ADM0_A3` considered the UK as the same region but some countries in Africa did not match with the ISO code. In the end, I used `ADM0_A3` field as the id and manually modify the mismatching field.

Then I matched the ISO codes in TopoJSON with ISO codes from dataset using the following code

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

It was found that there were 193 intersections and the result is put back to `ISO_List` in the JavaScript code. This was used to generate the list of country for users to choose.

#### Back to Dataset

To convert ISO code to names, I got the ISO code table from Wikipedia and convert that to `data/Pre-processing/ISO2Name.json`

Besides, consider the nature of the datasets, mortality data is the number of death per 1000 children at birth while vaccine coverage data is the percentage of adoption. I standardise both datasets and prepare them for JavaScript to read.

Moreover, I listed out the vaccine adopted by each country and save that to `data/Vaccine_in_Country.json`

### Analysis of Data



### Things to Determine Before Visualisation

#### Language and/or Packages to use

As I had used python to do some manipulation on the data, I could use python with matplotlib. However, as I learned D3.js from lecture, I am more familiar with using D3.js for visualisation. In addition, D3.js is a JavaScript library and can be run on any platform with modern browsers. Therefore, <u>JavaScript and D3.js</u> is used together with other libraries such as <u>jQuery</u> for DOM manipulation and <u>Underscore.js</u> for functional programming with JavaScript objects.

I use <u>Materialize</u> as the front-end framework as it is based on Material Design. It is minimalistic and simple to arrange HTML elements. I also use <u>Font Awesome</u> to display some symbols in the webpage.

#### Time Frame

The aim of the visualisation is to compare between immunisation coverage and child mortality rate. Therefore, I decided to set the time frame as the common period of both data, i.e. <u>between 1980 and 2015</u>.

#### Nature of Colour Scale

I wanted to use a colour scale to visualise the mortality rates. I had to decide between a continuous colour scale. This [answer](https://gis.stackexchange.com/a/86679) from StackExchange gave me a clear guide in choosing between the two. A continuous colour scale is a accurate representation of the data but it is sensitive to outliers and human perception to colour is not linear. On the other hand, despite there are data lost in discrete colour scale, it is robust to outliers and the colours can be perceived clearly and distinctly. Therefore, <u>discrete colour scale</u> is used

#### Level of Gradient of Colour on Map

The maximum value of mortality with 1980 and 2015 is 0.3369. It makes sense to divide the data into <u>7 intervals from 0.00 to 0.35</u> and the distribution of mortality rates is as follow:

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5eu8z66sj30al06pq3f.jpg)

After passing the data to D3.js, I got the choropleth map for the mortality rate in 2015 as follow which was satisfactory as the difference between countries was distinguishable.

![](http://ww1.sinaimg.cn/large/006tNbRwgy1fewu5tsu4cj30q20acmyh.jpg)

#### Choices of colours

To tell the story effectively, colours with underlying meanings close to the data itself should be used so that people can intuitively get the message. According to [Color Wheel Pro](http://www.color-wheel-pro.com/color-meaning.html), 

> Red is the color of fire and blood, ...
>
> Green is the color of nature. It symbolizes growth, harmony, freshness, and fertility. ...

Therefore, I used <u>red</u> to represent mortality data and <u>green</u> to represent vaccine coverage.

#### Typography

Typography should be easy to read so I planned to use sans serif font. The Materialize framework uses Roboto as the default font. Therefore, I use <u>Roboto</u> in the visualisation.

### Prototypes of the Visualisation

#### First Prototype

![](http://ww1.sinaimg.cn/large/006tNbRwgy1fexy6xcayjj31400kb0v3.jpg)



This is the first prototype of the visualisation. Left hand side was the setting panel and users were allowed to choose country and year to display. Right hand side was to show the details of the country selected. The area below the map was planned to show the vaccination rates across the year. I intended to show everything in one screen without scrolling. However, it is impractical as the map dimensions are in fixed ratio, potentially causing the graph at the bottom to appear too small. Therefore, this prototype was abandoned.

#### Second Prototype

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5ll3r0auj30rf0i3gni.jpg)

This was the second prototype. The map was more or less the same as the final one. When a country was selected, the time series plot appears.

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5jkxd3nej30pt0fa0tc.jpg)

Users can select the vaccine from the dropdown menu and the corresponding graph will be plotted. I found it not effective enough as I think it would be better for user to select a particular vaccine before displaying the graph. This idea led to the final version of my visualisation.

#### Final Visualisation

In the final visualisation, instead of a dropdown menu for vaccine, I displayed all vaccine together with their coverage of the country in donut charts.

![](http://ww3.sinaimg.cn/large/006tNbRwgy1ff5lvdzu9yj30rf0ieju3.jpg)

By making use of the grid framework of Materialize, I can easily add many donut charts and assigning classes to `div` elements. Users can click on a vaccine type to further investigate the adoptin trend of the vaccine over the year. To let the users know they cna select the vaccine by clicking anywhere with the `div` element, I added shadow box effect when user hover the `div` element.

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5m3delvaj313j0kcac9.jpg)

In the time series plots, I added data points in 

#### Other abandoned ideas

##### Preventable Disease Data

## Reflective Evaluation

