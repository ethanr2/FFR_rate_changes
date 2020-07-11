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
import os

# Grap Romer and Romer's intended rate change series directly.
def get_intended_rates():
    int_rate = pd.read_excel('data/RomerandRomerDataAppendix.xls', usecols = [0,1,2])
    int_rate['MTGDATE'] = int_rate['MTGDATE'].astype(str)
    int_rate['MTGDATE'] = int_rate['MTGDATE'].apply(lambda x: dt.strptime(x, '%m%d%y')) 
    int_rate = int_rate.set_index('MTGDATE')
    
    return int_rate
df = get_intended_rates()
print(df)

#%%
SERIES = {
    'q_jrfb':'IP', 
    'q_pgnp': 'GNP_Def',
    'q_pgdp': 'GDP_Def',
    'q_gnp72': 'RGDP_0',
    'q_gnp82': 'RGDP_1',
    'q_gdp87_cw': 'RGDP_2',
    'q_gdp87': 'RGDP_3',
    'q_gdp92_cw': 'RGDP_4'
    }
def parse_greenbook(name):
    with open('data/greenbook_forecasts/' + name) as f:
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
        # Convert data to a DataFrame and fix datatypes.
        data = pd.DataFrame(data)
        data['years'] = data['years'].astype(int)
        data['Q'] = data['Q'].apply(lambda x: int(x[-1]))
        
        # Just renaming the columns
        for col in SERIES:
            if col in data:
                data[SERIES[col]] = data[col]
                data.drop(col, axis = 1, inplace= True)
            
        # Find the date of current forecast
        whole_doc = ''.join(lines)
        reg = re.search(r"'(.*?)'", whole_doc).group(1)
        mtg_date = dt.strptime(reg, '_%Y_%m_%d')
        mtg_Y = mtg_date.year
        mtg_Q = (mtg_date.month - 1)//3 + 1
        data['mtg_date'] = mtg_date
        data['mtg_Y'] = mtg_Y
        data['mtg_Q'] = mtg_Q
        
        # We need to find the index of the current meeting 
        crit_1 = data['years'] == mtg_Y
        crit_2 = data['Q'] == mtg_Q
        row = data.loc[crit_1 & crit_2,:]
        idx = row.index[0] 
        
        # Using idx, we can now filter relative to the current meeting
        data = data.iloc[idx - 1: idx + 3,:]
        
    return data


files = os.scandir('data/greenbook_forecasts')
df_list = []
for file in files:
    print(file.name)    
    df_list.append(parse_greenbook(file.name))
#%%
data = pd.concat(df_list, ignore_index = True).sort_values('mtg_date')

temp = data.loc[:,['mtg_date','RGDP_0', 'RGDP_1', 'RGDP_2', 'RGDP_3', 'RGDP_4']]
print(temp)
#%%












