import pandas as pd

under5 = pd.read_csv("data/Pre-processing/Under5Mortarity.csv")
vaccine = pd.read_csv("data/Pre-processing/vaccine.csv")
incidence = pd.read_csv("data/Pre-processing/incidence.csv")
input("Read data files")

print("ISO Code in under5: {0}, vaccine: {1}, incidence: {2}".format(len(under5['ISO Code'].unique()), len(vaccine.ISO_code.unique()), len(incidence.ISO_code.unique())))
input("Printed ISO Code counts")

under5_idx = pd.Index(under5['ISO Code'])
vaccine_idx = pd.Index(vaccine.ISO_code.unique())
incidence_idx = pd.Index(incidence.ISO_code.unique())
common_countries = under5_idx.intersection(vaccine_idx).intersection(incidence_idx)
print(len(common_countries))
input("Printed common countries count")

import json
ISO_File = open("data/Pre-processing/ISO_list_in_dataset.json", "w")
ISO_File.write(json.dumps(list(common_countries.to_series())))
ISO_File.close()
input("Outputted common countries")

import csv
ISO2Names = {}
with open("data/Pre-processing/ISO2Names.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        ISO2Names[row[0]] = row[1]
ISO2Name_File = open("data/Pre-processing/ISO2Name.json", "w")
ISO2Name_File.write(json.dumps(ISO2Names))
ISO2Name_File.close()
input("Outputted ISO to Names conversion")

import numpy as np
# under5_filtered = under5_filtered.replace(0.0, np.nan)
under5 = under5.replace(0.0, np.nan)
input("Replaced 0.0 to NaN")

list(under5.count(axis='index'))
print(under5.max(numeric_only=True).max())
input("Printed max mortarity rate")

under5.to_csv("data/under5.csv")
vaccine.to_csv("data/vaccine.csv")
incidence.to_csv("data/incidence.csv")
input("Outputted processed data")

import matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline
matplotlib.style.use('ggplot')
under5.plot.hist()
input("Plotted histogram")

under5_timeseries = {}
for country in common_countries:
    for i in range(len(under5)):
        if under5.iloc[i]["ISO Code"] == country:
            under5_timeseries[country] = pd.Series(data=under5.iloc[i][3:], index=list(under5.transpose().index)[3:])
input("Saved under5 Time Series")

vaccine_types = list(vaccine.Vaccine.unique())
vaccine_timeseries = {}
for country in common_countries:
    for v in vaccine_types:
        for i in range(len(vaccine)):
            if vaccine.iloc[i]["ISO_code"] == country and vaccine.iloc[i]["Vaccine"] == v:
                vaccine_timeseries[country] = pd.Series(data=vaccine.iloc[i][4:], index=list(vaccine.transpose().index)[4:])
                print("Country: {0}/{1}, Vaccine: {2}/{3}".format(list(common_countries).index(country), len(common_countries), vaccine_types.index(v), len(vaccine_types)))

