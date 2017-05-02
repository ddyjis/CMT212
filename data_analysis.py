import pandas as pd
import numpy
import pprint
import json
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import grangercausalitytests as gctest
from sklearn.linear_model import LinearRegression

# for pretty-printing dictionaries
pp = pprint.PrettyPrinter(indent=4)

# read in the dataset
under5 = pd.read_csv("data/under5.csv")
vaccine = pd.read_csv("data/vaccine.csv")
under5 = under5.set_index("ISO Code")
vaccine = vaccine.set_index(["ISO_code", "Vaccine"]).sort_index(level="ISO_code")

# select only data from 1980 to 2015
under5 = under5.iloc[:, list(range(30,66))]

###############################
# test for individual dataset #
###############################

# plot the change in mortality rates distribution between 1980 and 2015 under the same x and y axis
under5.iloc[:, [0, 35]].hist(grid=False, sharex=True, sharey=True, layout=(2,1))

# medians of mortality rates
print("Median of mortality rate in 1980: {0:.4f}".format(under5.ix[:, 0].dropna().median()))
print("Median of mortality rate in 2015: {0:.4f}".format(under5.ix[:, -1].dropna().median()))

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

# find the vaccine used in each country
vaccine_in_country = {}
for c, v in vaccine.index:
    vaccine_in_country.setdefault(c, []).append(v)

v_in_c_file = open("data/Vaccine_in_Country.json", "w")
v_in_c_file.write(json.dumps(vaccine_in_country))
v_in_c_file.close()

max_num = 0
for c in vaccine_in_country:
    if len(vaccine_in_country[c]) >= max_num:
        max_num = len(vaccine_in_country[c])
        print(max_num, c)
print("Maximum number of vaccine a country adopt: {0}".format(max_num))

country_adoption = {}
for i in range(1, 21):
    country_adoption.setdefault(i, 0)
    
for c in vaccine_in_country:
    country_adoption[len(vaccine_in_country[c])] += 1
    
pp.pprint(country_adoption)
pd.DataFrame(data=list(country_adoption.items())).set_index(0).plot(kind="bar")

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
print("Number of countries that had trends in mortality rates: {0}".format(len(under5_sig)))

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
print("Number of countries that have trend using vaccine: {0}".format(len(vaccine_sig)))

##########################################
# test for relationship between datasets #
##########################################

# function for removing trend pattern if the time series is not stationary
def detrend(x, y):
    model = LinearRegression()
    model.fit(x, y)
    trend = model.predict(x)
    return [y[i] - trend[i] for i in range(len(y))]

# check if the two data ISO code are inconsistent
# expected to have no output
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
        #
        # maximum lag is set to 6 to find vaccine that lead the mortality by at most 5 years
        # leading more than 5 years are not considered as vaccine should not have effects 
        # on under 5 mortality for more than 5 years before
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
