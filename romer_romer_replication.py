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

with open('data/greenbook_forecasts/1982may.txt') as f:
    lines = f.readlines()

#%%

















