
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


dates = pd.read_excel('data/dates.xlsx')['Date'].sort_values()

rates = pd.read_csv('data/Daily_7_Day.csv', na_values = '.', index_col = 'DATE',
                    parse_dates = ['DATE'], infer_datetime_format = True)
temp = pd.read_csv('data/Daily.csv', na_values = '.', index_col = 'DATE',
                    parse_dates = ['DATE'], infer_datetime_format = True)
rates['T-1Month'] = temp['DGS1MO']
effr = pd.read_csv('data/Monthly.csv', na_values = '.', index_col = 'DATE',
                    parse_dates = ['DATE'], infer_datetime_format = True)
rates['effr'] = effr
rates['effr'] = rates['effr'].fillna(method ='ffill')

prate = pd.read_csv('data/TERMCBPER24NS.csv', na_values = '0', 
                    index_col = 'observation_date',
                    parse_dates = ['observation_date'], infer_datetime_format = True)
rates['prate'] =prate
rates['prate'] = rates['prate'].interpolate('time')
rates
#%%
start = dt(year = 2008, month = 12, day = 16)
rates.loc[start:,'DFEDTAR'] = rates.loc[start:,'IORR'] 
rates['T-1Month'] = rates['T-1Month'].fillna(method ='bfill')
rates['lag1-T-1Month'] = rates['T-1Month'].shift(1)
rates['lag7-T-1Month'] = rates['T-1Month'].shift(7)
rates['lag1-prate'] = rates['prate'].shift(1)
rates['lagged_mean7'] = rates['T-1Month'].rolling('7d', min_periods = 7).mean()
df = rates.loc[dates, ['DFEDTAR','lag1-prate', 'lag1-T-1Month', 
                       'lag7-T-1Month', 'lagged_mean7']]/100


#%%
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

# Chart of non-stationary time series, e.g. NGDP from 2008 to 2020    
def chart0(df):
    xdata, ydata, xrng, yrng = set_up(df.index,df['___'])
    
    p = figure(width = 1000, height = 500,
               title= '____', 
               x_axis_label = 'Date', x_axis_type = 'datetime',
               y_axis_label = '', 
               y_range = yrng, x_range = xrng)
    p.line(xrng,[0,0], color = 'black')
    
    p.line(xdata,ydata, color = 'blue', legend = '')
    
    p.xaxis[0].ticker.desired_num_ticks = 10
    p.legend.location = 'top_left'
    p.ygrid.grid_line_color = None
    p.yaxis.formatter=NumeralTickFormatter(format="____")
    
    export_png(p,'imgs/chart0.png')

    return p

# Chart of approximately stionary time series, e.g. PCE-Core inflation from 2008 to 2020
def chart1(df):
    xdata, ydata, xrng, yrng = set_up(df.index, df['__'], truncated = False)
    
    p = figure(width = 1000, height = 500,
               title="Interest👏Rates👏are👏Endogenous👏" , 
               x_axis_label = 'Date', x_axis_type = 'datetime',
               y_axis_label = '_', 
               y_range = yrng, x_range = xrng)
    p.line(xrng,[0,0], color = 'black')
    
    p.line(xdata,ydata, color = 'blue', legend = '_')
    
    p.xaxis[0].ticker.desired_num_ticks = 10
    p.legend.location = 'bottom_right'
    p.ygrid.grid_line_color = None
    p.yaxis.formatter=NumeralTickFormatter(format="0.0%")

    export_png(p,'imgs/chart1.png')

    return p

# Chart of a regression e.g. inflation vs money supply
def chart2(df, ver =1):
    if ver == 1:
        name = 'imgs/24hour.png'
        title = '1-Month Treasury Yield 24 Hours Before FOMC Meeting'
        xdata, ydata, xrng, yrng = set_up(df['lag1-T-1Month'], df['DFEDTAR'], 
                                          truncated = False, margins = .005)
    elif ver == 2:
        name = 'imgs/7day.png'
        title = '1-Month Treasury Yield 7 Days Before FOMC Meeting'
        xdata, ydata, xrng, yrng = set_up(df['lag7-T-1Month'], df['DFEDTAR'], 
                                          truncated = False, margins = .005)
    elif ver ==3:
        name = 'imgs/7day_lagmean.png'
        title = 'Average 1-Month Treasury Yield 7 Days Before FOMC Meeting'
        xdata, ydata, xrng, yrng = set_up(df['lagged_mean7'], df['DFEDTAR'], 
                                          truncated = False, margins = .005)
    elif ver ==4:
        name = 'imgs/1day_prate.png'
        title = '24-Month Personal Loan Rate 24 Hours Before FOMC Meeting'
        xdata, ydata, xrng, yrng = set_up(df['lag1-prate'], df['DFEDTAR'], 
                                          truncated = False, margins = .005)

    if ver ==4:
        yrng = (0, yrng[1])
    else:
        xrng = (0, xrng[1])
        yrng = (0, yrng[1])
    p = figure(width = 750, height = 600,
               title="Interest👏Rates👏are👏Endogenous👏", 
               x_axis_label = title, 
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
show(row(chart2(df, 1),chart2(df, 2), chart2(df, 3),chart2(df, 4)))
#show(chart2(df, 1))

#%%

#xdata, ydata, xrng, yrng = set_up(df['lag1-T-1Month'], df['DFEDTAR'], 
#                                  truncated = False, margins = .005)
#slope, intercept, r_value, p_value, std_err = stats.linregress(xdata, ydata)
#
#resid = ydata - (slope*xdata + intercept)
#resid = resid*100
#print(resid.sort_values()[:-9:-1].to_clipboard())













