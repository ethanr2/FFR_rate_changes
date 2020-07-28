# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:33:08 2020

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

TRUNC = (dt(1969, 2, 25),dt(1997,1,1))
COLS_RGDP = ('gRGDPB1','gRGDPF0', 'gRGDPF1', 'gRGDPF2')

def get_rgdp():
    rgdp_df = pd.read_excel('data/GBweb_Row_Format.xlsx',sheet_name = 'gRGDP')
    rgdp_df['GBdate'] = pd.to_datetime(rgdp_df['GBdate'], format= '%Y%m%d')
    rgdp_df = rgdp_df.set_index('GBdate', drop= False)
    dates = rgdp_df.pop('GBdate')
    
    rgdp_df = rgdp_df.loc[(TRUNC[0] < dates) & (dates < TRUNC[1]),COLS_RGDP]
    rgdp_df = rgdp_df.loc[~rgdp_df['gRGDPF2'].isnull(),:]
    return rgdp_df.sort_index()

def get_intended_rates():
    int_rate = pd.read_excel('data/RomerandRomerDataAppendix.xls', usecols = [0,1,2])
    int_rate['MTGDATE'] = int_rate['MTGDATE'].astype(str)
    #we want to drop the information about the day. we're only interested in the month.
    date_convert = lambda x: dt.strptime(x, '%m%d%y')
    int_rate['mtg_date'] = int_rate.pop('MTGDATE').apply(date_convert) 
    dates = int_rate['mtg_date']
    int_rate = int_rate.loc[(TRUNC[0] < dates) & (dates < TRUNC[1]), :]
    int_rate = int_rate.set_index('mtg_date', drop = False)
    return int_rate.sort_index()
rgdp = get_rgdp()
int_rate = get_intended_rates()
rgdp['ffr'] = int_rate['OLDTARG']

ir_date = int_rate.pop('mtg_date')
rgdp_date = rgdp.index.to_series()

for date in ir_date:
    i= rgdp_date.searchsorted(date) -1
    print('ir_date: {}, rgdp_Date: {}'.format(date, rgdp_date.iloc[i]))
#%%