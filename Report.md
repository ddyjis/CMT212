# Report

## Introduction

This visualisation intends to explore the relationship between vaccine coverage and the mortality rates of children under 5 years old. This project is also available on [GitHub](https://github.com/ddyjis/CMT212)

### Datasets

2 Datasets are used for this visualisation. They are the [World Immunisation Coverage](http://www.who.int/entity/immunization/monitoring_surveillance/data/coverage_series.xls?ua=1) from WHO and [Global Child Mortality Rate](https://data.unicef.org/wp-content/uploads/2015/12/U5MR_mortality_rate_39.xlsx) from UNICEF. In addition, I also used the geo data from [Natural Earth](http://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-details/).

- Immunisation data: located in `data/Raw/coverage_series.xls`, contains the adoption of 20 vaccines in 194 countries in years between 1980 and 2015.
- Under 5 mortality rate: located in `data/Raw/U5MR_mortality_rate_39.xlsx`, conatins the estimates of child mortality rate in 197 countries in years between 1950 and 2015.
- Geo data: located in `data/Raw/GeoData`, is a 1:10m Cultural Vector of Countries data in shapefile format.

### Visualisation

My visualisation use D3.js v4 combined with jQuery and underscore.js. It consists of 3 parts. The first part is a <u>world map</u> showing the <u>mortality rates</u> across the globe.

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff52cksov1j30rr0j5ac7.jpg)

The mortality rate is represented by different gradients of red. Countries that have no data are represented in pale white. Users can hovor the countries and a tooltip showing the country name and the mortality rate will appear. There is also a slider for users to select the year. When users press the <u>play button</u>, the year will increase in regular interval so as to visualise the changes in child mortality over time. Audience can <u>select a country to investigate</u> from the dropdown list or by clicking the country on the map.

The second part is a grid of <u>donut charts</u>. When a country is selected, the page is scrolled to these charts. 

![](http://ww1.sinaimg.cn/large/006tNbRwgy1ff52ek6z1bj30qx0jcjty.jpg)

Each of these donut charts show the corresponding <u>vaccine coverage</u> of the selected country. If the country never adopted a certain vaccine, the vaccine is not shown. If no data is available for that vaccine in that year, there will be a "No data" statement instead of a donut chart. Users can choose a vaccine by a mouse click.<div style="page-break-after: always;"></div>

The third part is the <u>time series plot</u> showing the trends of <u>vaccine coverage</u> and <u>child death rate</u> over time.

![](http://ww3.sinaimg.cn/large/006tNbRwgy1ff52zf0rdzj30rh0hvdi0.jpg)

Vaccine coverage is shown in green and mortality rate is shown in red. Data points are connected by smooth lines. If there is missing values, the line will be shown in different segments. When users hover on a data point, a tooltip appears showing the year and data for that point.

## Development of the Visualisation

### Data Preparation

#### Datasets

Raw dataset from the source are in `data/Raw`  in Excel spreadsheet format. I manually converted them to CSV format. They were then pre-processed using Pandas. Complete code for preparation can be seen in `preprocessing.py` and comments in `index.html`. Code explanation:

Since the data are from different sources, I need to <u>find the common ISO codes between the datasets</u>. 

```python
%matplotlib notebook
import numpy as np
import pandas as pd
import json
import csv
import matplotlib
import matplotlib.pyplot as plt

# read in datasets
under5 = pd.read_csv("data/Pre-processing/Under5Mortarity.csv")
vaccine = pd.read_csv("data/Pre-processing/vaccine.csv")

# display the number of countries in each dataset
print("ISO Code in under5: {0}, vaccine: {1}".format(len(under5['ISO Code'].unique()), len(vaccine.ISO_code.unique())))
print("Total Vaccine: {0}".format(len(vaccine.Vaccine.unique())))

# find the common countries across the three datasets
under5_idx = pd.Index(under5['ISO Code'])
vaccine_idx = pd.Index(vaccine.ISO_code.unique())
common_countries = under5_idx.intersection(vaccine_idx)
print("Number of common countries: {0}".format(len(common_countries)))

# output the common countries to JSON file
ISO_File = open("data/Pre-processing/ISO_list_in_dataset.json", "w")
ISO_File.write(json.dumps(list(common_countries.to_series())))
ISO_File.close()
```

And the output are as follow

```
ISO Code in under5: 197, vaccine: 194
Total Vaccine: 20
Number of common countries: 194
```

There were 194 countries in common and they were outputted to `data/Pre-processing/ISO_list_in_dataset.json` file for the visualisation to read.

#### Geo Data

With reference to this [blog](http://www.tnoda.com/blog/2013-12-07), I converted the shapefile to TopoJSON format which could be easily passed to JavaScript. I <u>create my own TopoJSON</u> from shapefile instead of using pre-existing JSON files because I have higher freedom in manipulating the JSON file like I can exclude Anatartica during convertion using the code

```bash
ogr2ogr -f GeoJSON -where "su_a3 <> 'ATA'" countries.json ne_10m_admin_0_map_units.shp
geo2topo -o countries.topo.json countries.json
```

The TopoJSON generated was 19.3 MB which was not appropriate for webpages. I used [mapshaper](http://www.mapshaper.org/) to simplify the geo data and the resulting TopoJSON file was reduced to 676 KB which was acceptable for web.

There were many attributes associated with the shapes. I tried `ISO_A3` and `ADM0_A3` as the id of each shape. `ISO_A3` considered UK as 4 different regions and neither of each matched with the ISO code of the UK. `ADM0_A3` considered the UK as the same region but some countries in Africa do not match with the ISO code. In the end, I used `ADM0_A3` <u>field as the id</u> and manually modify the mismatching fields.

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

It was found that there were 193 intersections and the result is put back to `ISO_List` in the JavaScript code. This was used to generate the list of countries for users to choose.

#### Back to Dataset

To convert ISO code to names, I got the ISO code table from Wikipedia and converted that into `data/Pre-processing/ISO2Name.json`

```python
# convert ISO to Country Names convertion table from CSV to JSON format
ISO2Names = {}
with open("data/Pre-processing/ISO2Names.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        ISO2Names[row[0]] = row[1]
ISO2Name_File = open("data/Pre-processing/ISO2Name.json", "w")
ISO2Name_File.write(json.dumps(ISO2Names))
ISO2Name_File.close()
```

Besides, consider the nature of the datasets, mortality data is the number of deaths per 1000 children before 5 while vaccine coverage data is the percentage of adoption. I <u>standardise both datasets</u> and prepare them for JavaScript to read.

```python
# standardise data and arrange columns in increasing order for JavaScript to read
under5 = under5.set_index("ISO Code").ix[:, 2:].apply(pd.to_numeric, errors="coerce").apply(lambda x: x/1000)
vaccine = vaccine.set_index(["ISO_code", "Vaccine"]).ix[:, 2:].apply(lambda x: x/100)
vaccine = vaccine[vaccine.columns[::-1]]

# find the maximum value in the under5 dataset
print("Maximum value of mortality rate between 1980 and 2015: {0}".format(under5.iloc[:, 30:].max(numeric_only=True).max()))
```

And the maximum mortality rate within the timeframe was

```
Maximum value of mortality rate between 1980 and 2015: 0.3369
```

Now the data is ready for analysis and visualisation. They are output to `data/under5.csv` and `data/vaccine.csv`.

### Analysis of Data

The complete code for analysis can be found in `data-analysis.py`. 

The aim of this visualisation is to show the relationship between immunisation coverage and child mortality rate. First, I <u>analysed the datasets separately</u>.

```python
# read in the dataset
under5 = pd.read_csv("data/under5.csv")
vaccine = pd.read_csv("data/vaccine.csv")
under5 = under5.set_index("ISO Code")
vaccine = vaccine.set_index(["ISO_code", "Vaccine"]).sort_index(level="ISO_code")

# select only data from 1980 to 2015
under5 = under5.iloc[:, list(range(30,66))]

# plot the change in mortality rates distribution between 1980 and 2015 under the same x and y axis
under5.iloc[:, [0, 35]].hist(grid=False, sharex=True, sharey=True, layout=(2,1))

# calculate the median of mortality rate in 1980 and 2015
print("Median of mortality rate in 1980: {0:.4f}".format(under5.ix[:, 0].dropna().median()))
print("Median of mortality rate in 2015: {0:.4f}".format(under5.ix[:, -1].dropna().median()))
```

![](http://ww1.sinaimg.cn/large/006tNbRwgy1ff6f2vd0ipj30f00en74x.jpg)

```
Median of mortality rate in 1980: 0.0750
Median of mortality rate in 2015: 0.0177
```

The two <u>histograms</u> above shows the distribution of mortality rates in the world in 1980 and 2015 respectively. They are plotted with the same scales in x-axis and y-axis. It can be seen that children <u>survival got much improved</u> in that 35 years. The whole distribution shifted to the left with higher peak. It can also be seen that country with the worst situation had reduced the mortality rate by at least half.

The <u>median</u> of mortality rate reduced from 0.0750 to 0.0177 which means majority of countries have their child survivor rates improved.

For the vaccine dataset, I computed the number of countries that used certain vaccine in 1980 and 2015 as well as the number of countries that had used a vaccine during the period.

```python
# find the vaccine usage based on each vaccine
vaccine_distribution_1980 = {}
for c, v in vaccine.ix[:, 0].dropna().index:
    vaccine_distribution_1980.setdefault(v, 0)
    vaccine_distribution_1980[v] += 1

vaccine_distribution_2015 = {}
for c, v in vaccine.ix[:, -1].dropna().index:
    vaccine_distribution_2015.setdefault(v, 0)
    vaccine_distribution_2015[v] += 1
    
vaccine_distribution = {}
for c, v in vaccine.index:
    vaccine_distribution.setdefault(v, 0)
    vaccine_distribution[v] += 1

pp.pprint(vaccine_distribution_1980)
pp.pprint(vaccine_distribution_2015)
pp.pprint(vaccine_distribution)
vaccine_dis_data_1980 = pd.DataFrame(data=list(vaccine_distribution_1980.items())).set_index(0).sort_values(1)
vaccine_dis_data_2015 = pd.DataFrame(data=list(vaccine_distribution_2015.items())).set_index(0).sort_values(1)
vaccine_dis_data = pd.DataFrame(data=list(vaccine_distribution.items())).set_index(0).sort_values(1)
vaccine_dis_data_1980.plot(kind="bar", title="In 1980")
vaccine_dis_data_2015.plot(kind="bar", title="In 2015")
vaccine_dis_data.plot(kind="bar", title="Over the period")
```

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff6jksgaegj30gt0gz751.jpg)

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff6jl7lo3uj30hv0jfgnf.jpg)

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff6jlzb3bxj30hn0k6jtf.jpg)

In 1980, only <u>5 types of vaccine</u> were used, while in 2015, <u>20 types of vaccine</u> were adopted. Over the whole period, <u>all</u> 194 countries adopted <u>MCV1, DTP3 and Pol3</u> while <u>JapEnc is the least</u> adopted.

When looking at the usage of vaccine based on each country,

```python
# find the vaccine used in each country
vaccine_in_country = {}
for c, v in vaccine.index:
    vaccine_in_country.setdefault(c, []).append(v)

max = 0
for c in vaccine_in_country:
    if len(vaccine_in_country[c]) >= max:
        max = len(vaccine_in_country[c])
        print(max, c)
print("Maximum number of vaccine a country adopt: {0}".format(max))

country_adoption = {}
for i in range(1, 21):
    country_adoption.setdefault(i, 0)
for c in vaccine_in_country:
    country_adoption[len(vaccine_in_country[c])] += 1
    
pp.pprint(country_adoption)
pd.DataFrame(data=list(country_adoption.items())).set_index(0).plot(kind="bar")
```

![](http://ww4.sinaimg.cn/large/006tNbRwgy1ff6l2o4vohj30hs0dcjs6.jpg)

It is found that MHL (Marshall Islands), is the only country that adopted all 20 vaccine. A majority of countries adopted <u>12 - 16 types of vaccine</u>.

To further investigate the data, as the two datasets consist of collections of time series, I also did <u>testings for time series</u> on the data. Augmented Dickey-Fuller Test is the test for <u>stationarity</u> of a time series. If a time series is stationary, its joint probability distribution does not change over time. In other words, there is no trend present in the time series. I carried out Augmented Dickey-Fuller Test for records in the two datasets for mortality trends as well as the vaccine adoption trends. `statsmodels` is a python library that provides time series analysis tools. The following is the codes I used:

```python
# function for testing time series stationarity using Augmented Dickey-Fuller Test
# it returns boolean value indicating there are trend in the time series or not
def test_stationarity(timeseries, sig=0.05):
    dftest = adfuller(timeseries, autolag="AIC")
    if dftest[0] < dftest[4]["1%"]:
        return 0.01 <= sig
    elif dftest[0] < dftest[4]["5%"]:
        return 0.05 <= sig
    elif dftest[0] < dftest[4]["10%"]:
        return 0.10 <= sig
    else:
        return False
    
# test for stationary of under5 for each country
under5_sig = []
for c in under5.index:
    # extract one record from under5 and interpolate and then remove nan data
    # this is to prepare the data for the Augmented Dickey-Fuller Test
    data = under5.ix[c].to_frame().apply(pd.to_numeric, errors="coerce").interpolate().dropna()
    have_trend = False
    # only country with enough record are tested, others are assumed stationary
    if len(data) > 9:
        have_trend = test_stationarity(sum(data.values.tolist(), []), 0.05)
    if have_trend:
        under5_sig.append(c)
print("Country with trend in under 5 mortarity rates")
pp.pprint(under5_sig)
```

It is found that <u>78 countries had trend in the mortarity rates</u> and I plotted them on a map in `analysis.html`

![](http://ww3.sinaimg.cn/large/006tNbRwgy1fezels9n3gj31400fzq4x.jpg)

It can be seen that South America, part of <u>Africa and Middle East, Northern Europe and Asia</u> had <u>significant trends</u>, probably declines, in mortality rates. Developed countries such as the those in <u>North America and Europe showed no trends</u>. This is could be explained by their sophisticated social welfare before the period that keep children healthy so their trends were steady. The <u>central part of Africa did not show a trend</u>. These countries were still relatively high in child mortality rates in 2015.

Then I tested for trend of each vaccine in each country,

```python
# test for stationary of each vaccine in each country
vaccine_sig = {}
for c, v in vaccine.index:
    data = vaccine.ix[c].ix[v].to_frame().apply(pd.to_numeric, errors="coerce")[v].interpolate().dropna().to_frame()
    have_trend = False
    if len(data) > 9:
        have_trend = test_stationarity(sum(data.values.tolist(), []), 0.05)
    if have_trend:
        vaccine_sig.setdefault(c, []).append(v)
print("Vaccine introduced in each country")
pp.pprint(vaccine_sig)
```

<u>166 countries showed trends in the vaccine coverage</u>. These could be an indicator of a country started to use that vaccine between 1980 and 2015.

Last but not least, I tested for the <u>relationship between the two collections of time series</u>. After reading this [blog](https://svds.com/avoiding-common-mistakes-with-time-series/), I decided to use <u>Granger Causality Tests</u> instead of correlation to test for relationship between vaccine adoption and child mortality. This is because once there are trends in the two time series, even the trend is small, the resulting <u>correlation could be very high. Pearson correlation is not a good measure</u> for the relationship between time series. Granger Causality is a kind of "artificial" causality. If a time series $X_1$ statistically predicts another time series $X_2$, $X_1$ is said to be Granger-causing $X_2$. Granger Causality is not true causality but it provides a statistical measure to reveal the relationship of two time series.<div style="page-break-after: always;"></div>

The following are the codes to test for Granger Causality

```python
# function for removing trend pattern if the time series is not stationary
def detrend(x, y):
    model = LinearRegression()
    model.fit(x, y)
    trend = model.predict(x)
    return [y[i] - trend[i] for i in range(len(y))]

# check if the two data ISO code are inconsistent
for c, v in vaccine.index:
    if c not in under5.index:
        print(c)
        
# check granger causality
vaccine_granger_cause = []

for c, v in vaccine.index:
    # get data the way same as above, u for under5 and v for vaccine
    v_data = vaccine.ix[c].ix[v].to_frame().apply(pd.to_numeric, errors="coerce")[v].interpolate().dropna().to_frame()
    u_data = under5.ix[c].to_frame().apply(pd.to_numeric, errors="coerce").interpolate().dropna()

    # get only the common years of results
    length = min(len(u_data), len(v_data))
    u_data = u_data[-length:]
    v_data = v_data[-length:]

    # test if the time series have trend in them
    v_has_trend = False
    if len(v_data) > 9:
        v_has_trend = test_stationarity(sum(v_data.values.tolist(), []), 0.05)
    u_has_trend = False
    if len(u_data) > 9:
        u_has_trend = test_stationarity(sum(u_data.values.tolist(), []), 0.05)
    
    # remove trend and make stationary time series for granger causality test
    if v_has_trend:
        x = [int(i) for i in v_data.index]
        x = numpy.reshape(x, (len(x), 1))
        y = v_data.values
        y = numpy.reshape(y, (len(y), 1))
        v_detrend = detrend(x, y)
        v_detrend = [float(i) for i in v_detrend]
    else:
        v_detrend = [float(i) for i in v_data.values]
    if u_has_trend:
        x = [int(i) for i in u_data.index]
        x = numpy.reshape(x, (len(x), 1))
        y = u_data.values
        y = numpy.reshape(y, (len(y), 1))
        u_detrend = detrend(x, y)
        u_detrend = [float(i) for i in u_detrend]
    else:
        u_detrend = [float(i) for i in u_data.values]

    d = {"Under5": u_detrend, "Vaccine": v_detrend}
    try:
        # grangercausalitytests test 
        max_lag = 6
        test = gctest(pd.DataFrame(data=d), max_lag, verbose=False)
        # lags stores the possible number of lags with average p-value less than 0.05
        lags = []
        for lag in test:
            average_p = 0
            for k in test[lag][0]:
                average_p += test[lag][0][k][1]/4
            if average_p < 0.05:
                lags.append(lag)
        if max(lags) < max_lag:
            vaccine_granger_cause.append(tuple([c, v, max(lags)]))
    except ValueError:
        pass

# show the results
country_improved = {}
vaccine_count = {k: 0 for k in list(vaccine.index.levels[1])}
for c, v, l in vaccine_granger_cause:
    country_improved.setdefault(c, []).append(v)
    vaccine_count[v] += 1
print("Country with mortarity rate 'Granger caused'")
pp.pprint(country_improved)
print(len(country_improved))
print("Counts of vaccine that 'Granger caused' change in mortarity")
pp.pprint(vaccine_count)
```

It is found that <u>165 countries</u> had their child mortality 'Granger-caused' by various kinds of vaccine. Among the 20 vaccines, <u>BCG, DTP3, HepB3, MCV1, Pol3 and TT2Plus</u> 'Granger-caused' changes in child mortality rates in more than 10 countries. This suggests these vaccine could be the factor that improves child survival rates. 

It should be reminded that vaccine could be a factor that reduce child mortality. There could be other factors that improves child survival or factors that affects both vaccine coverage and children health.

### Things to Determine Before Visualisation

#### Language and/or Packages to use

As I had used python to do some manipulation on the data, I could use python with matplotlib for the visualisation. However, as I learned D3.js from lecture, I am more familiar with it. In addition, D3.js is a JavaScript library and can be run on any platform with modern browsers. Therefore, <u>JavaScript and D3.js</u> are used together with other libraries such as <u>jQuery</u> for DOM manipulation and <u>Underscore.js</u> for functional programming with JavaScript objects.

I use <u>Materialize</u> as the front-end framework as it is based on Material Design. It is minimalistic and simple to arrange HTML elements. I also use <u>Font Awesome</u> to display some symbols in the webpage.

#### 

#### Time Frame

The aim of the visualisation is to compare between immunisation coverage and child mortality rate. Therefore, I decided to set the time frame as the common period of both data, i.e. <u>between 1980 and 2015</u>.

#### Nature of Colour Scale

I wanted to use a colour scale to visualise the mortality rates. I had to decide between a continuous colour scale and discrete colour scale. This [answer](https://gis.stackexchange.com/a/86679) from StackExchange gave me a clear guide in choosing between the two. A continuous colour scale is an accurate representation of the data but it is sensitive to outliers and human perception to colour is not linear. On the other hand, despite there are data lost in discrete colour scale, it is robust to outliers and the colours can be perceived clearly and distinctly. Therefore, <u>discrete colour scale</u> is used.

#### Level of Gradient of Colour on Map

The maximum value of mortality with 1980 and 2015 is 0.3369. It makes sense to divide the data into <u>7 intervals from 0.00 to 0.35</u>.

After passing the data to D3.js, I got the choropleth map for the mortality rate in 2015 as follow which was satisfactory as the difference between countries was distinguishable.

![](http://ww1.sinaimg.cn/large/006tNbRwgy1fewu5tsu4cj30q20acmyh.jpg)

#### Choices of colours

To tell the story effectively, colours with underlying meanings close to the data itself should be used so that audience can intuitively get the message. According to [Color Wheel Pro](http://www.color-wheel-pro.com/color-meaning.html), 

> Red is the color of fire and blood, ...
>
> Green is the color of nature. It symbolizes growth, harmony, freshness, and fertility. ...

Therefore, I used <u>red</u> to represent mortality data and <u>green</u> to represent vaccine coverage.

#### Typography

Typography should be easy to read so I planned to use sans serif fonts. The Materialize framework uses Roboto as the default font. Therefore, I use <u>Roboto</u> in the visualisation for consistence.<div style="page-break-after: always;"></div>

### Prototypes of the Visualisation

#### First Prototype

![](http://ww1.sinaimg.cn/large/006tNbRwgy1fexy6xcayjj31400kb0v3.jpg)



This is the first prototype of the visualisation. 

<u>Left hand side</u> was the setting panel and users were allowed to choose which country and year to display. I used the <u>dropdown menu</u> as well as the <u>range input</u> from Materialize to give a clean Material Design look. For the play function, I manipulated the events and values of the range input using jQuery. Both `change` and `input` events can update the map when users move the slider. `input` allows updating without releasing the mouse, but it is not support in IE. There is a <u>trade-off</u> between compatibility and efficiency in visualisation. In the end, I chose to use `change` for better compatibility. <u>Right hand side</u> was to show the details of the country selected. The <u>area below the map</u> was planned to show the vaccination rates across the year. 

I intended to show everything <u>in one screen</u> without scrolling. However, it is impractical as the map dimensions are in fixed ratio, potentially causing the graph at the bottom to appear too small. Therefore, the structure of this prototype was abandoned but the <u>dropdown and the slider were kept</u>.<div style="page-break-after: always;"></div>

#### Second Prototype

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5ll3r0auj30rf0i3gni.jpg)

This was the second prototype. The map was more or less the same as the final one. When a country was selected, the time series plot appears.

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5jkxd3nej30pt0fa0tc.jpg)

Users can select the vaccine from the dropdown menu and the corresponding graph will be plotted. I found it not effective enough as I think it would be better for <u>user to select a particular vaccine</u> instead of automatically displaying the first vaccine on the list. This idea led to the final version of my visualisation.

#### Final Visualisation

In the final visualisation, instead of a dropdown menu for vaccine, I displayed all vaccine together with their coverage of the country in donut charts.

![](http://ww3.sinaimg.cn/large/006tNbRwgy1ff5lvdzu9yj30rf0ieju3.jpg)

By making use of the grid framework of Materialize, I can easily add many donut charts by assigning classes to `div` elements. Users can <u>click on a vaccine type to further investigate</u> the adoption trend over the year. To let the users know they can select the vaccine by clicking the `div` element, I added shadow box effect when user hover it.

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff5m3delvaj313j0kcac9.jpg)

In the time series plots, I added data points to both series. When users hover on the data points, details such as the year and rate appear in a tooltip. The scale for vaccine coverage is fixed to show whether there is a high or low adoption rate. The scale for mortality rate depends on the maximum mortality rate between 1980 and 2015. This scale changes so that it can reflect the changes during that time and hence audience can infer on the potential effects of vaccines.

Coverage is represented by circles and is displayed above mortality rate which represented by squares. This arrangement is used because users are allowed to hover both data when the <u>two data intersect</u> as illustrated below

![](http://ww3.sinaimg.cn/large/006tNbRwgy1ff62ilhkm7j307h04smxc.jpg)

![](http://ww1.sinaimg.cn/large/006tNbRwgy1ff62i50nhyj308504s74h.jpg)

I also added a floating button at the lower right corner for users to quickly going back to the top of the page and select another country. When users select another country, a new set of donut charts is rendered but the time series plot will be hidden. This is because previously selected vaccine may not be adopted in newly selected country. To <u>prevent users' confusion</u> for the absence of data, I hide the plot and require users to select a vaccine again.

#### Other abandoned ideas

##### Preventable Disease Data

At the beginning I also got the data for <u>incidence for vaccine-preventable diseases</u>. I planned to show how vaccine can prevent people suffering from diseases. However, when I further investigate the relationship between vaccines and those diseases, I found that there are many-to-many relationships between them. Some vaccines are targeted at several diseases and some diseases could be prevented by several vaccines. Together with mortality data, the relationships are <u>too complicated to visualise</u>. Therefore, I only used 2 datasets.<div style="page-break-after: always;"></div>

## Reflective Evaluation

### Strength of my work

- All my visualisations are <u>interactive</u>. Users can hover on the map and the time series plot for further information. This helps users understand the data more easily .
- There are <u>hierarchies</u> in the visualisation. Users can reveal more detailed information as they go along each steps. When data changes in the map, the donut charts are updated and the plots are hidden to prevent confusion.
- The visualisation follows <u>simplistic</u> design. By increasing the data:ink ratio, data is delivered with minimum of extra ink that distract audiences. 

### Weakness of my work

- The <u>animation</u> of the map updates at <u>fixed time interval</u>. I have asked others to evaluate my work and they had different opinions to this function. Some of them wanted the updating to slow down so as to have longer time to observe the changes of each country while others wanted it to be faster so that the changes across a longer time are more obvious. What I could do is to allow users to <u>manually adjust</u> the speed with the slider.
- Only <u>one vaccine</u> can be compared to the mortality. More vaccine should be allowed to compare at a time as one vaccine maybe only part of the factors that affect mortality rates. However, a plot with 21 time series is too complex to delivery information. Perhaps I could allow users to pick several vaccines but the maximum number of vaccines that can be selected required <u>further investigation</u>.

### Reflection on my learning

Before doing this project, I thought what I learned from lecture was enough for me to finish the task. However, after going through the challenges, I realised that what I know was very little. With the help of Google, StackOverflow and the codes from bl.ocks.org, I acquired the information I needed to complete the task.

While doing the coursework, I learned how to carry out <u>data cleansing</u> such as removing `NaN` values, interpolating missing data using pandas. I had experience in <u>data analysis</u> including getting summaries of datasets, using libraries to carry out statistical tests for datasets. I understood more about <u>time series analysis</u>. I also realised that the <u>trade-off</u> between <u>compatibility</u> and <u>visual efficiency</u> is also a concern in visualisation. In addition, I learned how to <u>visualise data</u> in browsers using D3.js and how to use Chrome inspector to <u>debug</u> JavaScript codes.

Overall, this is a meaningful project and I learned a lot from doing it. I am sure I can do better if I were to do similar project again.

