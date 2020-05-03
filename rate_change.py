
# -*- coding: utf-8 -*-

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

# Global Constants
SERIES_IDS = { 
        'FFR_upper': 'DFEDTARU', # Federal Funds Target Range - Upper Limit 
        'IOR': 'IORR',  #  Interest Rate on Required Reserves
        'FFR': 'DFEDTAR', # Federal Funds Target Rate (DISCONTINUED) 
        'T-1Month': 'DGS1MO', # 1-Month Treasury Constant Maturity Rate
        'prate': 'TERMCBPER24NS', # Finance Rate on Personal Loans at Commercial Banks, 24 Month Loan
        }
SERIES_TITLES = {
        'T-1Month': '1 Month Treasury Yield',
        'prate': '24-Month Personal Loan Rate'
        }
URL = 'https://api.stlouisfed.org/fred/series/observations?series_id={}&api_key={}&observation_start={}&sort_order=desc&file_type=json'
with open('FRED_API_key.txt') as file:
    KEY = file.read()
DATA_START_DATE = '2001-07-01'
IOR_START_DATE = dt(year = 2008, month = 12, day = 16) # When the first IOR payments begin
DATES = pd.read_excel('data/dates.xlsx')['Date'].sort_values() # FOMC meeting dates

# Global variables to be defined in get_regressors
name = 'imgs/{}_{}day.png'
x_title = '1-Month Treasury Yield 24 Hours Before FOMC Meeting'

# Gathers data and constructs consolidated dataset
def get_data():
    out = {}
    for k in ('FFR_upper', 'IOR', 'FFR', 'T-1Month', 'prate'):    
        data = requests.get(URL.format(SERIES_IDS[k], KEY, DATA_START_DATE)).json()
        data = pd.DataFrame(data['observations'])
        data.index = pd.DatetimeIndex(data['date'])
        data['value'] = data['value'].apply(lambda x: float(x)/100 if not x =='.' else np.nan)
        out[k] = data['value']
        
    return pd.DataFrame(out)

# Fill NaNs for forward progation and fills FFR target blanks with IOR
def fill_NaNs(rates):
    rates['prate'] = rates['prate'].fillna(method ='ffill')
    rates.loc[IOR_START_DATE:,'FFR'] = rates.loc[IOR_START_DATE:,'IOR'] 
    rates['T-1Month'] = rates['T-1Month'].fillna(method ='ffill')
    
    return rates

# Gets the lagged data for regression and filters unecessary data
def get_regressor(rates, ser_name, mean = False, lag = 1):
    global name
    if not mean:
        rates['reg'] = rates[ser_name].shift(lag)
        name = name.format(ser_name, lag)
    else:        
        rates['reg'] = rates[ser_name].rolling('{}d'.format(lag)).mean()
        name = name.format('mean_' + ser_name, lag) 
    set_title(ser_name, mean, lag)
    
    return rates.loc[DATES, ['FFR','reg']]

def set_title(ser_name, mean, lag):
    global x_title
    if lag == 1:
        x_title = '{} 24 Hours Before FOMC Meeting'.format(SERIES_TITLES[ser_name])
    elif mean:
        x_title = 'Average {} {} Days Before FOMC Meeting'.format(SERIES_TITLES[ser_name], lag)
    else:
        x_title = '{} {} Days Before FOMC Meeting'.format(SERIES_TITLES[ser_name], lag)

def set_up(x, y, truncated = True, margins = None):
    if truncated: 
        b = (3 * y.min() - y.max())/2
    else:
        b = y.min()
    if margins == None:    
        xrng = (x.min(),x.max())
        yrng = (b,y.max())
    else:
        xrng = (x.min() - margins,x.max() + margins)
        yrng = (b - margins,y.max() + margins)
        
    x = x.dropna()
    y = y.dropna()
    
    return(x,y,xrng,yrng)


# Chart of a regression e.g. inflation vs money supply
def chart2(df):
    xdata, ydata, xrng, yrng = set_up(df['reg'], df['FFR'], 
                                          truncated = False, margins = .005)
    
#    xrng = (0, xrng[1])
#    yrng = (0, yrng[1])
    p = figure(width = 750, height = 600,
               title="Interest👏Rates👏are👏Endogenous👏", 
               x_axis_label = x_title, 
               y_axis_label = 'Federal Funds Rate Target', 
               y_range = yrng, x_range = xrng)
    p.line(xrng,[0,0], color = 'black')
    p.line([0,0],yrng, color = 'black')
    
#    spec = dt(year = 2008, day = 16, month = 9)
#    p.circle(xdata[spec], ydata[spec], color = 'red', size = 2)
#    lehman = Label(x = xdata[spec], y = ydata[spec]+.005, 
#                   text = 'September 16th, 2008')
#    p.add_layout(lehman)
#    xdata = xdata.drop(spec)
#    ydata = ydata.drop(spec)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(xdata, ydata)
    leg = 'R = {:.4f}, P-Value = {:.4e}, Slope = {:.4f}'.format(r_value,p_value,slope)
    p.line(xdata, xdata*slope + intercept, legend_label = leg, color = 'black')
    p.circle(xdata,ydata, color = 'blue',size = 2)
    

    
    
    p.xaxis[0].ticker.desired_num_ticks = 10
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.formatter=NumeralTickFormatter(format="0.0%")
    p.yaxis.formatter=NumeralTickFormatter(format="0.0%")
    p.legend.location = 'bottom_right'
    
    export_png(p,name)
    
    return p
rates = get_data()
rates = fill_NaNs(rates)
df = get_regressor(rates, 'T-1Month', True, 7)
df2 = get_regressor(rates, 'T-1Month')
print(df)

show(row(chart2(df), chart2(df2)))
#show(chart2(df, 1))

#%%

#xdata, ydata, xrng, yrng = set_up(df['lag1-T-1Month'], df['DFEDTAR'], 
#                                  truncated = False, margins = .005)
#slope, intercept, r_value, p_value, std_err = stats.linregress(xdata, ydata)
#
#resid = ydata - (slope*xdata + intercept)
#resid = resid*100
#print(resid.sort_values()[:-9:-1].to_clipboard())













