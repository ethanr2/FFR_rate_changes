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

SERIES = {
    'ru':'U', 
    'q_pgnp': 'Def_0',
    'q_pgdp': 'Def_1',
    'q_pgdp_cw': 'Def_2',
    'q_gnp72': 'RGDP_0',
    'q_gnp82': 'RGDP_1',
    'q_gdp87_cw': 'RGDP_2',
    'q_gdp87': 'RGDP_3',
    'q_gdp92_cw': 'RGDP_4'
    }

START = (1977, 4) # Quarters measured relative to 1977Q4
# Some greensheets appear to be missing, so im truncating the Romer and Romer appendix data.
TRUNC = (dt(year = 1978, month = 1, day = 1 ), dt(year = 1996, month = 12, day = 1))

# Grab Romer and Romer's intended rate change series directly.
def get_intended_rates():
    int_rate = pd.read_excel('data/RomerandRomerDataAppendix.xls', usecols = [0,1,2])
    int_rate['MTGDATE'] = int_rate['MTGDATE'].astype(str)
    #we want to drop the information about the day. we're only interested in the month.
    date_convert = lambda x: dt.strptime(x[-2:] + x[:-4], '%y%m')
    int_rate['mtg_date'] = int_rate.pop('MTGDATE').apply(date_convert) 
    int_rate = int_rate.loc[(int_rate['mtg_date'] >= TRUNC[0]), :]
    int_rate = int_rate.set_index('mtg_date')
    
    print(int_rate)
    return int_rate

# Gets the raw data from each individual Greensheet. 
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
        #mtg_date = dt.strptime(reg[:8], '_%Y_%m')
        try:
            mtg_date = dt.strptime(name[:-4], '%Y%B')
        except ValueError:
            mtg_date = dt.strptime(name[:-5], '%Y%B')
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

def get_raw_data():
    files = os.scandir('data/greenbook_forecasts')
    df_list = [] # put all the dataframes in a list to concat later.
    for file in files:
        print(file.name)    
        df_list.append(parse_greenbook(file.name))
    df = pd.concat(df_list, ignore_index = True).sort_values(by =['mtg_date','years','Q'])
    
    print(df)
    return df

def consolidate(data, name, keys):
    data[name] = 0
    for key in keys:
        col = data.pop(key)
        bools = ~col.isna()
        data.loc[bools, name] = col[bools].astype(float)

# Convert each year-quarter pair to an absolute quarter datapoint
def rel_q(data):
    data['mtg_rel_q'] = (data.pop('mtg_Y') - START[0])*4 + data.pop('mtg_Q') - START[1]
    abs_q = (data.pop('years') - START[0])*4 + data.pop('Q') - START[1]
    data['rel_q'] = abs_q - data['mtg_rel_q'] 
    
def clean_data(data):
    consolidate(data, 'RGDP', ('RGDP_0','RGDP_1', 'RGDP_2', 'RGDP_3', 'RGDP_4'))
    consolidate(data, 'pi', ('Def_0','Def_1', 'Def_2'))
    data['U'] = data['U'].astype(float)
    rel_q(data)
    data= data.loc[data['mtg_date'] <= TRUNC[1],:]
    print(data)
    return data

df = get_intended_rates()
raw_data = get_raw_data()

#%%

# Get_raw_data is intensive, a copy may save time if we need to reload.
temp = raw_data.copy() 
cleaned = clean_data(temp)

# Now that we have the raw data cleaned, we have to adjust and realign the data for the regression
grouped = cleaned.groupby('rel_q')
data = grouped.get_group(0)[['mtg_date', 'mtg_rel_q', 'U']]
data = data.set_index('mtg_date', drop = True)

data['const'] = 0
data['ffb_m'] = df['OLDTARG']
#go here
data['u_m,0'] = data.pop('U')
print(data)

#%%


