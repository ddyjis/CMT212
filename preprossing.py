import numpy as np
import pandas as pd
import json
import csv
import matplotlib
import matplotlib.pyplot as plt

# read in datasets
under5 = pd.read_csv("data/Pre-processing/Under5Mortarity.csv") # data for moartarity rate for children under 5
vaccine = pd.read_csv("data/Pre-processing/vaccine.csv")        # data for vaccine coverates
incidence = pd.read_csv("data/Pre-processing/incidence.csv")    # data for incidence of preventible disease

# display the number of countries in each dataset
print("ISO Code in under5: {0}, vaccine: {1}, incidence: {2}".format(len(under5['ISO Code'].unique()), len(vaccine.ISO_code.unique()), len(incidence.ISO_code.unique())))

# find the common countries across the three datasets
under5_idx = pd.Index(under5['ISO Code'])
vaccine_idx = pd.Index(vaccine.ISO_code.unique())
incidence_idx = pd.Index(incidence.ISO_code.unique())
common_countries = under5_idx.intersection(vaccine_idx).intersection(incidence_idx)
print(len(common_countries))

# output the common countries to JSON file
ISO_File = open("data/Pre-processing/ISO_list_in_dataset.json", "w")
ISO_File.write(json.dumps(list(common_countries.to_series())))
ISO_File.close()

# convert ISO to Country Names convertion table from CSV to JSON format
ISO2Names = {}
with open("data/Pre-processing/ISO2Names.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        ISO2Names[row[0]] = row[1]
ISO2Name_File = open("data/Pre-processing/ISO2Name.json", "w")
ISO2Name_File.write(json.dumps(ISO2Names))
ISO2Name_File.close()

# replace zeros in data to NaN
under5 = under5.replace(0.0, np.nan)

# find the maximum value in the under5 dataset
print(under5.max(numeric_only=True).max())

# output the dataset to csv file
under5.to_csv("data/under5.csv")
vaccine.to_csv("data/vaccine.csv")
incidence.to_csv("data/incidence.csv")

# plot the distribution of under5 data
matplotlib.style.use('ggplot')
under5_filtered.plot.hist()