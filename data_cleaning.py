# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 08:22:14 2022

@author: IHiggins
"""

import base64
import datetime as dt
from datetime import timedelta
from datetime import datetime
import io
import pyodbc
import configparser
# add a note ####
# added a second note #
# a forth comment

# added a third note possibly in a branch?
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from datetime import date
import dash_datetimepicker
import dash_daq as daq

import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots

def fill_timeseries(data):
    # make sure it is in datetime
    data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    data['datetime'] = data['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))
    data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    data.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/cache_check/data_cleaning/todatetime.csv")
    # get origianal interval
    delta = (data.tail(1).iloc[0, 0])-(data.head(1).iloc[0,0])
    # compare to records to get change in time per timestamp
    interval = (delta/(data.shape[0])).total_seconds()
    interval = int(round((interval/60),0))
    # resample
    data.set_index("datetime", inplace=True)
    '''
    if interval < 30 and interval >=15:
        data = data.resample('15T').interpolate(method='linear')
        data.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/cache_check/data_cleaning/fill.csv")
    if interval < 15 and interval >=5:
        data = data.resample('15T').interpolate(method='linear')
        data.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/cahce_check/data_cleaning/fill.csv")
    else:
        data = data
        #data = data.resample('15T')
    '''
    data = data.resample('15T').interpolate(method='linear')
    data.reset_index(level=None, drop=False, inplace=True)
    fill_timeseries.delta = delta
    fill_timeseries.interval = interval
    data.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/cache_check/data_cleaning/resampled.csv")
    #data['datetime'] = data['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))
    return data
'''
data = pd.read_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/clean_check.csv", index_col=0)
fill_timeseries(data)
print(f"delta {fill_timeseries.delta}")
print(f"interval {fill_timeseries.interval}")
'''