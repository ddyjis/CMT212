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

Raw dataset from the source at in `data/Raw`  in Excel spreadsheet format. I manually converted them to CSV format. They were then pre-processed using Pandas. Complete codes for preparation can be seen in `preprocessing.py` and comments in `index.html`. Codes are also explained below

Since the data are from different sources, I need to find the common ISO codes between the datasets. 

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

Besides, consider the nature of the datasets, mortality data is the number of death per 1000 children at birth while vaccine coverage data is the percentage of adoption. I standardise both datasets and prepare them for JavaScript to read.

```python
# standardise data and arrange columns in increasing order for JavaScript to read
under5 = under5.set_index("ISO Code").ix[:, 2:].apply(pd.to_numeric, errors="coerce").apply(lambda x: x/1000)
vaccine = vaccine.set_index(["ISO_code", "Vaccine"]).ix[:, 2:].apply(lambda x: x/100)
vaccine = vaccine[vaccine.columns[::-1]]

# find the maximum value in the under5 dataset
print("Maximum value of mortality rate between 1980 and 2015: {0}".format(under5.iloc[:, 30:].max(numeric_only=True).max()))
```

And the output is

```
Maximum value of mortality rate between 1980 and 2015: 0.3369
```

Now the data is ready for analysis and visualisation. They are output to `data/under5.csv` and `data/vaccine.csv`.

### Analysis of Data

The aim of this visualisation is to show the relationship between immunisation coverage and child mortality rate. First, I analysed the dataset separately.

```python
%matplotlib notebook
import pandas as pd
import numpy
import pprint
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import grangercausalitytests as gctest
from sklearn.linear_model import LinearRegression

pp = pprint.PrettyPrinter(indent=4)

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

The two histograms above shows the distribution of mortality rates in the world in 1980 and 2015 respectively. They are plotted with the same scales in x and y axis. It can be seen that children survival got much improved in 35 years. The whole distribution shifted to the left with higher peak. Both histograms consist of 10 bins. The bins for the maximum value in 1980 was at around 0.3 while that for 2015 was at around 0.15 which means the country with the worst situation had reduced the mortality rate by a half.

The median of mortality rate reduced from 0.0750 to 0.0177 which means majority of countries have their child survivor rates improved. The mean is not compared as it should be weighted by the population of each country. 

For the vaccine dataset, I computed the numbers of countries that used certain vaccination in 1980 and 2015 as well as the number of countries that had used a vaccine during the period.

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

print("In 1980")
pp.pprint(vaccine_distribution_1980)
print("In 2015")
pp.pprint(vaccine_distribution_2015)
print("Over the period")
pp.pprint(vaccine_distribution)
vaccine_dis_data_1980 = pd.DataFrame(data=list(vaccine_distribution_1980.items())).set_index(0).sort_values(1)
vaccine_dis_data_2015 = pd.DataFrame(data=list(vaccine_distribution_2015.items())).set_index(0).sort_values(1)
vaccine_dis_data = pd.DataFrame(data=list(vaccine_distribution.items())).set_index(0).sort_values(1)
print("In 1980")
vaccine_dis_data_1980.plot(kind="bar", title="In 1980")
print("In 2015")
vaccine_dis_data_2015.plot(kind="bar", title="In 2015")
print("Over the period")
vaccine_dis_data.plot(kind="bar", title="Over the period")
```

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff6jksgaegj30gt0gz751.jpg)

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff6jl7lo3uj30hv0jfgnf.jpg)

![](http://ww2.sinaimg.cn/large/006tNbRwgy1ff6jlzb3bxj30hn0k6jtf.jpg)

In 1980, only 5 kinds of vaccination were used while in 2015, 20 different vaccine were adopted. Over the whole period, all 194 countries adopted MCV1, DTP3 and Pol3 while JapEnc is the least adopted.

When looking at the usage of vaccine based on each country,

```python
# find the vaccine used in each country
vaccine_in_country = {}
for c, v in vaccine.index:
    vaccine_in_country.setdefault(c, []).append(v)

v_in_c_file = open("data/Vaccine_in_Country.json", "w")
v_in_c_file.write(json.dumps(vaccine_in_country))
v_in_c_file.close()

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

It is found that MHL, which stands for Marshall Islands, is the only country that adopted all 20 vaccine. A majority of countries adopted 12 - 16 kinds of vaccination.

To further investigate the data, as the two dataset consist of collections  of time series, I also did testings for time series on the data. Augmented Dickey-Fuller Test is as test for stationarity of a time series. If a time series is stationary, its joint probability distribution does not change over time. In other word, there is no trend present in the time series. I carried out Augmented Dickey-Fuller Test for each data record to test for trends. `statsmodels` is a python library that provides time series analysis tools. The following is the codes I used to check for trends

```python
# function for testing time series stationarity using Augmented Dickey-Fuller Test
# it takes in a time series and significant level as parameters
# it returns boolean value indicating there are trend in the time series or not
# 
# adfuller takes a time series data and test if it is stationary or not
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
    # extract one record from under5 and convert the data to numeric 
    # and then interpolate the missing values in between the data
    # and then remove nan data at the beginning of the time series
    # this is to prepare the data for the Augmented Dickey-Fuller Test
    data = under5.ix[c].to_frame().apply(pd.to_numeric, errors="coerce").interpolate().dropna()
    have_trend = False
    # only country with enough record are tested, others are assumed stationary
    if len(data) > 9:
        # a list is needed to pass to adfuller but data.values.tolist() gives 
        # a column instead of a row so use sum(x, []) to convert it to a single list
        have_trend = test_stationarity(sum(data.values.tolist(), []), 0.05)
    if have_trend:
        under5_sig.append(c)
print("Country with trend in under 5 mortarity rates")
pp.pprint(under5_sig)
```

It is found that 78 countries had trend in the mortarity rates and I plotted them on a map in `analysis.html`

![](http://ww3.sinaimg.cn/large/006tNbRwgy1fezels9n3gj31400fzq4x.jpg)

It can be seen that South America, part of Africa and Middle East, Northern Europe and Asia had significant trends, probably declines, in mortality rates. Developed coutries such as the USA, Canada, Australia, European countries does not have trend. This is probably because they already had sophisticated social welfare before the period that keep children healthy. The central part of Africa did not show a trend. These countries were still relatively high in child mortality rates.

Then I tested for trend for each vaccine in each country,

```python
# test for stationary of each vaccine in each country
vaccine_sig = {}
for c, v in vaccine.index:
    # the structure for vaccine is different as it has 2 indice so the 
    # syntax here is a little bit different
    data = vaccine.ix[c].ix[v].to_frame().apply(pd.to_numeric, errors="coerce")[v].interpolate().dropna().to_frame()
    have_trend = False
    if len(data) > 9:
        have_trend = test_stationarity(sum(data.values.tolist(), []), 0.05)
    if have_trend:
        vaccine_sig.setdefault(c, []).append(v)
print("Vaccine introduced in each country")
pp.pprint(vaccine_sig)
```

166 countries showed trends in the vaccine coverage. These could be an indicator of a country started to use that vaccine between 1980 and 2015.

Last but not least, I tested for the relationship between the two collections of time series. After reading this [blog](https://svds.com/avoiding-common-mistakes-with-time-series/), I decided to use Granger Causality Tests instead of correlation to test for relationship between vaccine adoption and child mortality. This is because once there is trends in the two time series, even the trend is small, the resulting correlation could be very high. Pearson correlation is not a good measure for the relationship between time series. Granger Causality is a kind of "artificial" causality. If a time series $X_1$ statistically predicts another time series $X_2$, $X_1$ is said to be Granger-causes $X_2$. Granger Causality is not true causality but it provides a statistical measure to reveal the relationship of two time series.

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
        # grangercausalitytests test if the second time series "granger-cause" the first one
        # it takes at least 2 parameters: data and maxlag
        # data should contain exactly two time series of the same length
        # maxlag states the maximum lag between the two time series
        # 
        # grangercausalitytests contains 4 statistical tests to test if past values of the
        # second series has statistically significant effect on current value of the first series
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

It is found that 165 countries had their child mortality 'Granger-caused' by various kinds of vaccine. Out of the 20 vaccines, BCG, DTP3, HepB3, MCV1, Pol3 and TT2Plus 'Granger-caused' changes in child mortality rates in more than 10 countries. This suggests these vaccine could be the factor that improves child survival rates. It should be reminded that vaccine could be a factor that reduce child mortality. There could be other factors that improves child survival or factors that affects both vaccine coverage and children health.

### Things to Determine Before Visualisation

#### Language and/or Packages to use

As I had used python to do some manipulation on the data, I could use python with matplotlib. However, as I learned D3.js from lecture, I am more familiar with using D3.js for visualisation. In addition, D3.js is a JavaScript library and can be run on any platform with modern browsers. Therefore, <u>JavaScript and D3.js</u> is used together with other libraries such as <u>jQuery</u> for DOM manipulation and <u>Underscore.js</u> for functional programming with JavaScript objects.

I use <u>Materialize</u> as the front-end framework as it is based on Material Design. It is minimalistic and simple to arrange HTML elements. I also use <u>Font Awesome</u> to display some symbols in the webpage.

#### Time Frame

The aim of the visualisation is to compare between immunisation coverage and child mortality rate. Therefore, I decided to set the time frame as the common period of both data, i.e. <u>between 1980 and 2015</u>.

#### Nature of Colour Scale

I wanted to use a colour scale to visualise the mortality rates. I had to decide between a continuous colour scale. This [answer](https://gis.stackexchange.com/a/86679) from StackExchange gave me a clear guide in choosing between the two. A continuous colour scale is a accurate representation of the data but it is sensitive to outliers and human perception to colour is not linear. On the other hand, despite there are data lost in discrete colour scale, it is robust to outliers and the colours can be perceived clearly and distinctly. Therefore, <u>discrete colour scale</u> is used

#### Level of Gradient of Colour on Map

The maximum value of mortality with 1980 and 2015 is 0.3369. It makes sense to divide the data into <u>7 intervals from 0.00 to 0.35</u>.

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



This is the first prototype of the visualisation. 

Left hand side was the setting panel and users were allowed to choose country and year to display. I used the dropdown menu as well as the range input from Materialize to give a clean Material Design look. For the play function, I manipulated the events and values of the range input using jQuery. Both `change` and `input` events can update the map when user move the slider. `input` allows updating without releasing the mouse, but it is not support in IE. There is a trade-off between compatibility and efficiency in visualisation. In the end, I chose to use `change` for better compatibility. Right hand side was to show the details of the country selected. The area below the map was planned to show the vaccination rates across the year. 

I intended to show everything in one screen without scrolling. However, it is impractical as the map dimensions are in fixed ratio, potentially causing the graph at the bottom to appear too small. Therefore, the structure of this prototype was abandoned but the dropdown and the slider was kept.

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

In the time series plots, I added data points to both series. When users hover on the data points, details such as the year and rate appear in a tooltip. The scale for vaccine coverage is fixed to show whether there is a high or low adoption rate. The scale for mortality rate depends on the maximum mortality rate between 1980 and 2015. This scale changes so that it can reflect the changes during that time and hence audience can infer on the effects of vaccines.

Coverage is represented by circles while mortality rate is represented by squares. This arrangement is because users are allowed to hover both data when the two data intersect as illustrated below

![](http://ww3.sinaimg.cn/large/006tNbRwgy1ff62ilhkm7j307h04smxc.jpg)

![](http://ww1.sinaimg.cn/large/006tNbRwgy1ff62i50nhyj308504s74h.jpg)

I also added a floating button at the lower right corner for users to quickly going back to the top of the page and select another country. When users select another country, a new set of pie charts is rendered but the time series plot will be hided. This is because previously selected vaccine may not be adopted in newly selected country. To prevent users' confusion for the absence of data, I hide the plot and require users to select a vaccine again.

#### Other abandoned ideas

##### Preventable Disease Data

At the beginning I also got the data for incidence for vaccine-preventable disease. I planned to show how vaccine can prevent people suffering from diseases. However, when I further investigate the relationship between vaccine and those diseases, I found that there are many-to-many relationships between them. Some vaccines are targeted at several diseases and some diseases could be prevented by several vaccines. Together with mortality data, the relationships are too complicated to visualise. Therefore, I only used 2 datasets.

## Reflective Evaluation

### Strength of my work

- All my visualisations are interactive. Users can hover on the map and the time series plot for further information. This helps users more easily understand the data.
- There are hierarchy in the visualisation. Users reveals more detailed information as they go along each steps. When data changes in the map, the pie charts are updated and the plots are hided to prevent confusion.
- The visualisation follows simplistic design. By increasing the data:ink ratio, data is delivered with minimum of extra ink that distract audiences. 

### Weakness of my work

- The animation of the map updates at fixed interval. I have asked others to evaluate my work and they had different opinions to this function. Some of them wanted the updating to slow down so as to have longer time to observe the changes of each country while others wanted it to be faster so that the changes across a longer time are more obvious. What I could do is to allow users to manually adjust the speed with the slider.
- Only one vaccine can be compared to the mortality. More vaccine should be allowed to compare as a particular is probably not the only factor that affect mortality rates. However, a plot with 21 time series is too complex to delivery information. Perhaps I could allow users to pick several vaccines but the maximum number of vaccine that can be selected required further investigation.

### Reflection on my learning

Before doing this project, I thought what I learned from lecture was enough for me to finish the task. However, after going through the challenges, I realised that what I know was very little. With the help of Google, StackOverflow and the codes from bl.ocks.org, I acquired the information I needed to complete the task.

While doing the coursework, I learned how to carry out data cleansing such as removing `NaN` values, interpolating missing data using pandas. I had experience in data analysis including getting summaries of datasets, using libraries to carry out statistical tests for datasets. I understood more about time series analysis. I also realised that the trade-off between compatibility and visual efficiency is also a concern in visualisation. In addition, I learned how to visualise data in browsers using D3.js and how to use Chrome inspector to debug JavaScript codes.

