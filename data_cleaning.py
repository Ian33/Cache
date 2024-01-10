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
from scipy.optimize import curve_fit
from numpy.polynomial import polynomial as P
from scipy import stats, interpolate
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d, UnivariateSpline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

def fill_timeseries(data):
    data.drop_duplicates(subset=['datetime'], keep='first', inplace=True)
    data.dropna(subset=['datetime'], inplace=True)
    #data.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/cache_error_df.csv")
    #data['estimate'] = 0
    # make sure it is in datetime
    data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    data['datetime'] = data['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))
    data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
  
    # get origianal interval
    delta = (data.tail(1).iloc[0, 0])-(data.head(1).iloc[0,0])
    # compare to records to get change in time per timestamp
    interval = (delta/(data.shape[0])).total_seconds()
    interval = int(round((interval/60),0))
    # resample
    #data['data'] = data['data'].astype(float, errors="ignore")
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
    # resample to 15 minute
    
    #data = data.resample('15T').asfreq(fill_value="NaN")
    data = data.resample('15T').interpolate(method='linear', limit=4)
    
    data.reset_index(level=None, drop=False, inplace=True)
    data['estimate'] = 0
    
    def f(x):
        if x['data'] == "NaN": return str(1)
        else: return x['estimate']
    data['estimate'] = data.apply(f, axis=1)
    data['data'] = data['data'].astype(float, errors="ignore")
    #data['data'].interpolate(inplace=True)
    
    return data

def interpolate_function(df):
    #df.dropna(subset=["comparison"], inplace=True)
    df.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/interp_input.csv")
    training_data = df[df.estimate == 0]
    training_data  = training_data.dropna(subset=["comparison"])
    training_data  = training_data.dropna(subset=["corrected_data"])
    
    # x independent - comparison
    # y dependent - missing data/ corrected_data
    
    # interpolate only works wit linear
    #interpolate_1d = interp1d(x_array, y_array, fill_value="extrapolate")
    
    # you can use multiple x sites but dont reshape then
    #scaler = StandardScaler().fit(xtrain.values)
    #https://www.google.com/search?q=fill+missing+hydrology+time+series+data+in+python&rlz=1C1GCEB_enUS963US963&oq=fi&aqs=chrome.0.69i59j69i57j46i131i433j69i60j69i61j69i60l3.1785j1j4&sourceid=chrome&ie=UTF-8#fpstate=ive&vld=cid:b0109594,vid:2NAJUCxFSso
    
    # x independent (comparison) y dependent (corrected_data)
    # train test split
    x_train, x_test, y_train, y_test = train_test_split(training_data["comparison"].to_numpy().reshape(-1, 1), training_data["corrected_data"].to_numpy().reshape(-1, 1),random_state=1)
    #scaler
    scaler=StandardScaler().fit(x_train)
    x_train_scaled = scaler.transform(x_train)
    x_test_scaled = scaler.transform(x_test)
    regr = MLPRegressor(random_state=1, max_iter=5000).fit(x_train_scaled, np.ravel(y_train))
    #ypredict = regr.predict(x_train_scaled)
    print(regr.score(x_test_scaled, y_test))

    for index, row in df.iterrows():
        if (row['estimate'] == 1 or np.isnan(row['corrected_data']) or 'corrected_data' == 'nan' or 'corrected_data' == "") and not np.isnan(row['comparison']):
            rowscaled = scaler.transform(np.array(row["comparison"], dtype=object).reshape(-1, 1))
            df.loc[index,['data']] = regr.predict(rowscaled)
            df.loc[index,['estimate']] = 1
  
        else: 
             df.loc[index,['corrected_data']] = df.loc[index,['corrected_data']]
    df.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/comparison.csv")
    return df
   


def data_conversion(df, parameter):
    # water level conversion
    # if water level is centegrade
    if parameter == "WaterTemp" or parameter == "water_temperature":
        if df['data'].mean() < 20:
            df = df
           
        else:
            df['data'] = (df['data']-32)*(5/9)
    else:
        df = df
    
    return df

def reformat_data(df):
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    
    if 'data' in df.columns:
        df['data'] = df['data'].astype(float, errors="ignore")
        df['data'] = df['data'].round(2)
    if 'corrected_data' in df.columns:
        df['corrected_data'] = df['corrected_data'].astype(float, errors="ignore")
        df['corrected_data'] = df['corrected_data'].round(2)
    if 'observation' in df.columns:
        df['observation'] = df['observation'].astype(float, errors="ignore")
    if 'observation_stage' in df.columns:
        df['observation_stage'] = df['observation_stage'].astype(float, errors="ignore")
    if 'parameter_observation' in df.columns:
        df['parameter_observation'] = df['parameter_observation'].astype(float, errors="ignore")
    if 'offset' in df.columns:
        df['offset'] = df['offset'].astype(float, errors="ignore")
    if 'discharge' in df.columns:
        df['discharge'] = df['discharge'].astype(float, errors="ignore")
    if 'q_observation' in df.columns:
        df['q_observation'] = df['q_observation'].astype(float, errors="ignore")
    if 'Discharge_Rating' in df.columns:
        df['Discharge_Rating'] = df['Discharge_Rating'].astype(float, errors="ignore")
    if 'q_offset' in df.columns:
        df['q_offset'] = df['q_offset'].astype(float, errors="ignore")
    if 'comparison' in df.columns:
        df['comparison'] = df['comparison'].astype(float, errors="ignore")
    if 'estimate' in df.columns:
        df['estimate'] = df['estimate'].astype(int, errors="ignore")
    if 'measurement_number' in df.columns:
        df['measurement_number'] = df['measurement_number'].astype(float, errors="ignore")
    if 'discharge_observation' in df.columns:
        df['discharge_observation'] = df['discharge_observation'].astype(float, errors="ignore")

    return df

def style_formatting():
    style_data_conditional = ({'if': {'column_id': 'comparison',}, 'backgroundColor': 'rgb(222,203,228)','color': 'black'},
                              {'if': {'filter_query': '{parameter_observation} > 0','column_id': 'parameter_observation'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                              {'if': {'filter_query': '{parameter_observation} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                              #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                              {'if': {'filter_query': '{observation_stage} > 0','column_id': 'observation_stage'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                              {'if': {'filter_query': '{observation_stage} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                              {'if': {'filter_query': '{observation_stage} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},)
                                   
                                   # {'if': {'filter_query': '{{parameter_observation}} > {0}'),'backgroundColor': '#FF4136','color': 'white'},
               

    return style_data_conditional

def add_comparison_site(comparison_site_sql_id, comparison_parameter, df):
     # add comparison df

        from import_data import sql_import
        start_date = df.loc[df.index == 0, "datetime"].item()
        end_date =   df.loc[df.index == df.index[-1], "datetime"].item()
        df_comparison = sql_import(comparison_parameter, comparison_site_sql_id, start_date, end_date) # fx converts to PST and out of PST

        df_comparison = df_comparison[['datetime', "corrected_data"]]
        df_comparison.rename(columns={"corrected_data": "comparison"}, inplace=True)
        df = df.merge(df_comparison, on="datetime", how = "outer")
        return df

def rating_curve_equations(df, gzf):
    df_sort = df.sort_values(by=['observation_stage']).copy()
    
    # poly fit
    #poly_fit_equation = np.poly1d(np.polyfit(((df_sort['observation_stage']-gzf)).to_numpy(), (df_sort['discharge_observation']).to_numpy(), 2))
   # df_sort['poly_fit_line'] = poly_fit_equation(df_sort['observation_stage']-gzf)

    # linear regression
    # linregressor (x,y) x = discharge y =
    #inear_regression_equation =  stats.linregress((df_sort['observation_stage']-gzf).to_numpy(), (df_sort['discharge_observation']).to_numpy())
    #df_sort['linear_regression_line']  = (((inear_regression_equation.intercept)-gzf) + (inear_regression_equation.slope*(df_sort['observation_stage'])-gzf))


    #linear_regression_log =  stats.linregress(np.log(df_sort['observation_stage']).to_numpy(), np.log(df_sort['discharge_observation']).to_numpy())
    #df_sort['linear_regression_log']  = (((linear_regression_log.intercept)) + ( linear_regression_log.slope*(df_sort['observation_stage'])))
    #linear_regression_log_gzf =  stats.linregress(np.log(df_sort['observation_stage']-gzf).to_numpy(), np.log(df_sort['discharge_observation']).to_numpy())
    #df_sort['linear_regression_log_gzf']  = (((linear_regression_log_gzf.intercept)) + (linear_regression_log_gzf.slope*(df_sort['observation_stage'])))

   



    print("stats")
    #print(f" Linear Regression intercept {linear_regression_equation.intercept} slope {linear_regression_equation.slope}")
    #print(f" Linear Regression Log intercept {linear_regression_log.intercept} slope {linear_regression_log.slope}")
    #print(f" Linear Regression Log  GZF intercept {linear_regression_log_gzf.intercept} slope {linear_regression_log_gzf.slope}")
     # line between points
    
    #interpolate_function = interpolate.interp1d(((df_sort['observation_stage']-gzf).to_numpy()), df_sort['discharge_observation'].to_numpy(), bounds_error = True)
    df_sort = df_sort.sort_values(by=['observation_stage']).copy()
    #df_x = df_sort.groupby('observation_stage', as_index=False).mean()
    interpolate_function = interpolate.interp1d(((df_sort['observation_stage']-gzf).to_numpy()), df_sort['discharge_observation'].to_numpy(), bounds_error = False)
    interpolate_stage = interpolate.interp1d(df_sort['discharge_observation'].to_numpy(), ((df_sort['observation_stage']-gzf).to_numpy()), bounds_error = False)
    df_sort['interpolate'] = interpolate_function((df_sort['observation_stage']-gzf))
    #df_x = df_sort.sort_values(by = ['observation_stage', 'discharge_observation'], ascending = [True, True], na_position = 'first')
    
    #df_x = df_x.reindex(['observation_stage'])
    #df_x = df_x.sort_values(by = 'discharge_observation')

    #df_sort = df_sort.sort_values(by=['measurement_number']).copy()
    return df_sort, interpolate_function, interpolate_stage
'''
data = pd.read_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/clean_check.csv", index_col=0)
fill_timeseries(data)
print(f"delta {fill_timeseries.delta}")
print(f"interval {fill_timeseries.interval}")
'''