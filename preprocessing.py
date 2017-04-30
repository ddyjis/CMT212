import numpy as np
import pandas as pd
import json
import csv
import matplotlib
import matplotlib.pyplot as plt

# read in datasets
under5 = pd.read_csv("data/Pre-processing/Under5Mortarity.csv") # data for moartarity rate for children under 5
vaccine = pd.read_csv("data/Pre-processing/vaccine.csv")        # data for vaccine coverates

# display the number of countries in each dataset
print("ISO Code in under5: {0}, vaccine: {1}".format(len(under5['ISO Code'].unique()), len(vaccine.ISO_code.unique())))

# find the common countries across the three datasets
under5_idx = pd.Index(under5['ISO Code'])
vaccine_idx = pd.Index(vaccine.ISO_code.unique())
common_countries = under5_idx.intersection(vaccine_idx)
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

# convert data to rates and arrange columns in increasing order of years
under5 = under5.set_index("ISO Code").ix[:, 2:].apply(pd.to_numeric, errors="coerce").apply(lambda x: x/1000)
vaccine = vaccine.set_index(["ISO_code", "Vaccine"]).ix[:, 2:].apply(lambda x: x/100)
vaccine = vaccine[vaccine.columns[::-1]]

# find the maximum value in the under5 dataset
print(under5.max(numeric_only=True).max())

# output the dataset to csv file
under5.to_csv("data/under5.csv")
vaccine.to_csv("data/vaccine.csv")

# plot the distribution of under5 data
matplotlib.style.use('ggplot')
pd.DataFrame(under5.values.flatten()).hist(bins=9)