# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 14:07:13 2020

@author: ethan
"""

import os
from datetime import datetime as dt

import pandas as pd

import urllib.request
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_dir():
    if not os.path.isdir(dataPath):
        os.mkdir(dataPath)
        urllib.request.urlretrieve(URL, '{}/spf.xlsx'.format(dataPath))

URL = 'https://www.fedsearch.org/fomc-docs/search;jsessionid=F21F049CB8B080588FBF12A16BA983C7?advanced_search=true&from_year=2002&search_precision=All+Words&start={}&sort=Most+Recent+First&to_month=4&to_year=2020&number=10&fomc_document_type=policystatement&Search=Search&text=&from_month=12'

with webdriver.Chrome() as driver:
    dates = []
    for i in range(0,200, 10):
        driver.get(URL.format(i))
        lst = driver.find_elements_by_class_name('greentext')
        for tag in lst:
            text = tag.text
            dates.append(dt.strptime(text[26:36], '%m/%d/%Y'))
            print(dates[-1], end=', ')
        print()
dates = pd.Series(dates)
dates.to_excel('data/dates.xlsx')
#%%
