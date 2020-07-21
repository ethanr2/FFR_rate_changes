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


