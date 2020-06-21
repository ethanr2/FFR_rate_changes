# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 21:45:44 2020

@author: ethan
"""

from datetime import date
from datetime import datetime as dt
from time import time

import numpy as np
import pandas as pd
from scipy import stats
from scipy import interpolate as interp

from bokeh.io import export_png,output_file,show
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter, LabelSet,ColumnDataSource, Label
from bokeh.models.tickers import FixedTicker
from bokeh.layouts import row, column

import requests
import re
# Grap Romer and Romer's intended rate change series directly.
def get_intended_rates():
    int_rate = pd.read_excel('data/RomerandRomerDataAppendix.xls', usecols = [0,1,2])
    int_rate['MTGDATE'] = int_rate['MTGDATE'].astype(str)
    int_rate['MTGDATE'] = int_rate['MTGDATE'].apply(lambda x: dt.strptime(x, '%m%d%y')) 
    int_rate = int_rate.set_index('MTGDATE')
    
    return int_rate
df = get_intended_rates()
df
#%%
SERIES = {
    'q_jrfb':'IP', 
    'q_pgnp': 'GNP_Def', 
    'q_gnp72': 'RGDP'
    }
def parse_greenbook(name)
with open('data/greenbook_forecasts/1982may.txt') as f:
    lines = f.readlines()
    data = {}
    data['years'] = lines[6].strip().split('    ')
    data['Q'] = lines[7].strip().split('      ')
    ind = lines[8].find('-')
    for line in lines:
        reg = re.search('\[(.*?)\]', line)
        if reg and reg.group(1) in SERIES:
            data[reg.group(1)] = line[ind:].strip().split('   ')
            #rint(line)
    data = pd.DataFrame(data)
    for col in SERIES:
        data[SERIES[col]] = data[col]
        data.drop(col, axis = 1, inplace= True)
    # Find the Date of forecast
    whole_doc = ''.join(lines)
    reg = re.search(r"'(.*?)'", whole_doc).group(1)
    
    data['mtg_date'] = dt.strptime(reg, '_%Y_%m_%d')
    #print(data)
#%%

















