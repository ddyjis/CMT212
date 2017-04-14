#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:02:39 2017

@author: ddyjis
"""

import pandas as pd

under5 = pd.read_csv("data/Under5Mortarity.csv")
vaccine = pd.read_csv("data/vaccine.csv")
incidence = pd.read_csv("data/incidence.csv")

print("ISO Code in under5: {0}, vaccine: {1}, incidence: {2}".format(len(under5['ISO Code'].unique()), len(vaccine.ISO_code.unique()), len(incidence.ISO_code.unique())))

under5_idx = pd.Index(under5['ISO Code'])
vaccine_idx = pd.Index(vaccine.ISO_code.unique())
incidence_idx = pd.Index(incidence.ISO_code.unique())
common_countries = under5_idx.intersection(vaccine_idx).intersection(incidence_idx)
print(len(common_countries))

under5 = under5[under5['ISO Code'].isin(common_countries)]