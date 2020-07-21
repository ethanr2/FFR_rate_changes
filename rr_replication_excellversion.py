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

TRUNC = 1997

rgdp_df = pd.read_excel('data/GBweb_Row_Format.xlsx',sheet_name = 'gRGDP')
dates = rgdp_df['DATE']
rgdp_df = rgdp_df.set_index('DATE', drop = True)
#%%
rgdp_df = rgdp_df.loc[dates > TRUNC,:]

rgdp_df

#%%