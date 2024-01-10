import os 
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import configparser
import sys
import os
from datetime import datetime
from datetime import timedelta
import urllib
import configparser
import time
import numpy as np
#import win32com.client as win32
#import schedule
import pyodbc
import pandas as pd
from sqlalchemy import create_engine

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 14:29:39 2021

@author: IHiggins
"""
import base64
import datetime as dt
from datetime import timedelta
from datetime import datetime
import io
import pyodbc
import configparser
import pickle 
from scipy import interpolate
from scipy.interpolate import interp1d, UnivariateSpline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
# add a note ####
# added a second note #
# a forth comment

# added a third note possibly in a branch?
import dash
from dash import html
from dash.dependencies import Input, Output, State
from dash import dcc, ctx 
#from dash import html
from dash import dash_table
import pandas as pd
from datetime import date
import dash_datetimepicker
import dash_daq as daq

import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# a new comment
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

config = configparser.ConfigParser()
config.read('gdata_config.ini')
#username = "cwtcmzqujpmszj"
#    password = "d9717d1ad9420277ea4b7a2332885a6e7cbc39073d29a0cfd9f733d2df6835b6"
host_name = "KCITSQLPRNRPX01"
db_name = "gData"
server = "KCITSQLPRNRPX01"
#10.82.12.39
driver = "SQL Server"
database = "gData"




# get site list
#sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection=yes;')
#sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)


#conn = sql_engine.raw_connection()

# new sql alchemy connection
server = config['sql_connection']['Server']
driver = config['sql_connection']['Driver']
database = config['sql_connection']['Database']
trusted_connection = config['sql_connection']['Trusted_Connection']
   

# pyodbc has a longer pooling then sql_alchemy and needs to be reset
pyodbc.pooling = False
# not sure this fast execumetry sped things up
# info on host name connection https://docs.sqlalchemy.org/en/14/dialects/mssql.html#connecting-to-pyodbc
sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection='+trusted_connection+';')
sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)

sql = f"select SITE_CODE as site_number, G_ID as site_sql_id from {config['parameters']['parameter_table']} WHERE STATUS = 'Active' AND FlowLevel = 'True'"
with sql_engine.begin() as conn:
    site_list = pd.read_sql_query(sql, conn)
vlist = site_list['site_number'].to_list()

app.layout = html.Div([
    # dcc.Location(id='url', refresh=False),
    # Select a Site
    # Site = site name site_sql_id is site number
    html.Div([
        html.Div(dcc.Dropdown(id='site_dropdown',options=[{'label': i, 'value': i} for i in vlist],value='31i'), style={'width': '20%', 'display': 'inline-block'}), 
            # set value to "0" for production
        #html.Div(id='site_sql_id', style={'display': 'block'}),
        # Select a Parameter - get options from callback
        # this is a hidden callback
        html.Div(dcc.Dropdown(id='Parameter', value='discharge'),style={'display': 'none'}),
        
        html.Div(daq.ToggleSwitch(id = "create_rating", label = 'create rating', labelPosition = 'bottom', value = "True"), style={'width': '10%', 'display': 'inline-block'}),
 

        html.Div(dcc.RangeSlider(min = 0, max = 0, value=[0, 0], id = 'monitoring_peroid_range_slider'), style={'width': '70%', 'display': 'inline-block'}),
        
    ]),
    html.Div([
    html.Div(
    dash_table.DataTable(
            id="field_observations",
            editable=True,
            sort_action="native",
            sort_mode="multi",
            fixed_rows={'headers': True},
            row_deletable=False,
            page_action='none',
            style_table={'height': '300px', 'overflowY': 'auto'},
            virtualization=True,
            fill_width=False,
            #filter_action='custom',
            filter_action = 'native',
            #filter_query = "'parameter_observation >= 0",
            style_data={
            'width': '125px', 'maxWidth': '125px', 'minWidth': '50px', },
 
            style_cell_conditional=[
                {'if': {'column_id': 'datetime'},'width': '40%'},
                {'if': {'column_id': 'observation_stage'},'width': '20%'},
                {'if': {'column_id': 'measurement_number'},'width': '20%'},
                {'if': {'column_id': 'discharge_observation'},'width': '20%'},]
            #style_data_conditional=[{'if': {'column_id': 'comparison',}, 'backgroundColor': 'rgb(222,203,228)','color': 'black'},
                                    #{'if': {'column_id': 'parameter_observation', 'filter_query': '{} > 0'}, 'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'observation_stage'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                   
                                   # {'if': {'filter_query': '{{parameter_observation}} > {0}'),'backgroundColor': '#FF4136','color': 'white'},
            #],    
    
    ),style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
    dash_table.DataTable(
            id="monitoring_peroid_table",
            editable=True,
            sort_action="native",
            sort_mode="multi",
            fixed_rows={'headers': True},
            row_deletable=False,
            page_action='none',
            style_table={'height': '300px', 'overflowY': 'auto'},
            virtualization=True,
            fill_width=False,
            #filter_action='custom',
            filter_action = 'native',
            #filter_query = "'parameter_observation >= 0",
            style_data={
            'width': '125px', 'maxWidth': '125px', 'minWidth': '50px', },
            #style_data_conditional=[{'if': {'column_id': 'comparison',}, 'backgroundColor': 'rgb(222,203,228)','color': 'black'},
                                    #{'if': {'column_id': 'parameter_observation', 'filter_query': '{} > 0'}, 'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'observation_stage'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                   
                                   # {'if': {'filter_query': '{{parameter_observation}} > {0}'),'backgroundColor': '#FF4136','color': 'white'},
            #],
            #dropdown={'rating': {'options': [{'label': 'true', 'value': 'true'},{'label': 'false', 'value': 'false'}]}
            
    
    ),style={'width': '25%', 'display': 'inline-block'}),
    html.Div(
    dash_table.DataTable(
            id="rating_points_table",
            editable=True,
            sort_action="native",
            sort_mode="multi",
            fixed_rows={'headers': True},
            row_deletable=False,
            page_action='none',
            style_table={'height': '300px', 'overflowY': 'auto'},
            virtualization=True,
            fill_width=False,
            #filter_action='custom',
            filter_action = 'native',
            #filter_query = "'parameter_observation >= 0",
            style_data={
            'width': '150px', 'maxWidth': '200px', 'minWidth': '50px', },
            #    'width': '165px', 'maxWidth': '165px', 'minWidth': '100px', },
            #style_data_conditional=[{'if': {'column_id': 'comparison',}, 'backgroundColor': 'rgb(222,203,228)','color': 'black'},
                                    #{'if': {'column_id': 'parameter_observation', 'filter_query': '{} > 0'}, 'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'observation_stage'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                   
                                   # {'if': {'filter_query': '{{parameter_observation}} > {0}'),'backgroundColor': '#FF4136','color': 'white'},
            #],
            #dropdown={'rating': {'options': [{'label': 'true', 'value': 'true'},{'label': 'false', 'value': 'false'}]}
            
    
    ),style={'width': '50%', 'display': 'inline-block'}),
    
    
    ]),
    html.Div([
        html.Div(html.Button('Add Row', id='editing-rows-button', n_clicks=0), style={'width': '33%', 'display': 'inline-block'}),
        html.Div(dcc.Input(id="gzf", type="number",debounce=True, value = 0, step = 0.01), style={'width': '33%', 'display': 'inline-block'}),
        html.Div(dcc.RadioItems(options = ['log', 'linear'], value = 'log', inline=True, id = 'graph_axis_type'), style={'width': '33%', 'display': 'inline-block'}),
        html.Div(html.Button('export', id='export_rating', n_clicks=0), style={'width': '33%', 'display': 'inline-block'}),
        html.Div(dcc.Input(id="rating_name", type="text",debounce=True, value = 0, step = 0.01), style={'width': '33%', 'display': 'inline-block'}),
         ]),
       # html.Div(
       
       # html.Div([id='stage_duplicate_error', style={'width': '33%', 'display': 'inline-block'}]),
            #html.Div([id='discharge_duplicate_error', style={'width': '33%', 'display': 'inline-block'}]),
           # html.Div([id='discharge_progress_error', style={'width': '33%', 'display': 'inline-block'}]),
        #style={'width': '33%', 'display': 'inline-block'}),
   
    html.Div(dcc.Dropdown(options=['0'],value=['0'],id='rating_points_checklist', multi=True),style={'width': '100%', 'display': 'inline-block'}),
    html.Div(dcc.Dropdown(options=['0'],value=['0'],id='rating_curves', multi=True),style={'width': '100%', 'display': 'inline-block'}),
    
    html.Div(id='rating_graph'),
    


    # display meta data
    html.Div(
    
    dash_table.DataTable(
            id="observation_statistics",
            editable=False,
            sort_action="native",
            sort_mode="multi",
            fixed_rows={'headers': True},
            row_deletable=False,
            page_action='none',
            style_table={'height': '300px', 'overflowY': 'auto'},
            virtualization=True,
            fill_width=False,
            #filter_action='custom',
            filter_action = 'native',
            #filter_query = "'parameter_observation >= 0",
            style_data={
            'width': '150px', 'maxWidth': '200px', 'minWidth': '50px', },
    )),
     html.Div([
        html.Div(id = 'stage_duplicate_error'),
        html.Div(id = 'discharge_duplicate_error'),
        html.Div(id = 'discharge_progress_error'),
        ]),
])
    
@app.callback(
    Output('field_observations', 'data'),
    Output('field_observations', 'columns'),
    #Output('rating_graph', 'children'),
    Output('monitoring_peroid_range_slider', 'min'),
    Output('monitoring_peroid_range_slider', 'max'),
    Output('monitoring_peroid_range_slider', 'value'),
    Output('rating_curves', 'options'),
    Input('site_dropdown', 'value'))
def show_field_observations(site):

    if site != "0":
            # get site list
        #sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection=yes;')
        #sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)
        #conn = sql_engine.raw_connection()

        sql = f"select SITE_CODE as site_number, G_ID as site_sql_id from {config['parameters']['parameter_table']} WHERE STATUS = 'Active' AND FlowLevel = 'True'"
        with sql_engine.begin() as conn:
            site_list = pd.read_sql_query(sql, conn)
        #conn.close()
        # get site_number (SITE_CODE) and site_sql_id (G_ID)
        #site = '31q'
        site_sql_id = site_list.loc[site_list['site_number'] == site, 'site_sql_id'].item()

        # get field observations
        with sql_engine.begin() as conn:
            field_observations = pd.read_sql_query(f"select {config['observation']['observation_id']} as observation_id, {config['observation']['datetime']} as datetime, {config['observation']['observation_stage']} as observation_stage, {config['observation']['observation_number']} as observation_number, convert (int, {config['observation']['measurement_number']}) as measurement_number "
                                                    f"from {config['observation']['observation_table']} "
                                                    f"WHERE {config['observation']['site_sql_id']} = '{str(site_sql_id)}';", conn)
       
        field_observations["datetime"] = pd.to_datetime(
        field_observations["datetime"], format='%Y-%m-%d %H:M:S', errors='ignore') - timedelta(hours=7)

        # get parameter information for discharge
        with sql_engine.begin() as conn:
            parameter_observation = pd.read_sql_query(
                                            f"select {config['observation']['observation_id']} as observation_id, convert (int, {config['observation']['observation_type']}) as observation_type, {config['observation']['observation_value']} as observation_value "# need these trailing 
                                            f"from {config['observation']['observation_value_table']} "
                                            f"WHERE {config['observation']['site_sql_id']} = {site_sql_id} "
                                            f"AND {config['observation']['observation_type']} = {2};", conn)
        

        parameter_observation["observation_id"] = parameter_observation["observation_id"].astype(np.int64)
        parameter_observation.rename(columns={"observation_value": "parameter_observation"}, inplace=True)

        field_observations = field_observations.merge(parameter_observation, on=["observation_id"], how="inner")
        field_observations.rename(columns={"parameter_observation": "discharge_observation"}, inplace=True)            

                
        field_observations.drop(columns=["observation_id", "observation_type", "observation_number"], inplace=True)   
   
        field_observations["datetime"] = pd.to_datetime(field_observations["datetime"], format='%Y-%m-%d %H:M:S', errors='ignore')
        
        min = field_observations['measurement_number'].min()
        
        max = field_observations['measurement_number'].max()

        #min = 5
        #max = 100
       
        # Get list of rating
        with sql_engine.begin() as conn:
            ratings = pd.read_sql_query(f"select RatingNumber from tblFlowRatings WHERE G_ID = '{site_sql_id}' GROUP BY RatingNumber ORDER BY RatingNumber DESC;", conn)
        ratings = ratings['RatingNumber'].values.tolist()
        
        # get rating offsets
        with sql_engine.begin() as conn:
            offsets = pd.read_sql_query(f"select Offset, Rating_Number from tblFlowRating_Stats;", conn)
        offsets['Rating_Number'] = offsets['Rating_Number'].str.strip()
        offsets = offsets[offsets['Rating_Number'].isin(ratings)]
        offsets = offsets.rename(columns={"Offset": "label", "Rating_Number": "value"})

        offsets["label"] = offsets.apply(lambda x: (f"rating {x['value']} gzf {x['label']}"), axis=1)
        #offsets['label'] = 
        #offsets= offsets["label"].apply(lambda x: x)
        offsets = offsets.to_dict('records')
        print("offsets")
        print(offsets)
       
       
      
       # for i in ratings:
        #        # get rating offset
        #        if i != 0:
        #            conn = sql_engine.raw_connection()
        #            rating_offsets = pd.read_sql_query(f"select Rating_Number from tblFlowRating_Stats WHERE Rating_Number = '{i}' GROUP BY Rating_Number ORDER BY Rating_Number DESC;", conn)
        #            #rating_offsets = rating_offsets['RatingNumber'].values.tolist()
        #            try:
        #                rating_offsets = rating_offsets.iloc[0, 0].astype(float)
        #            except:
        #                rating_offsets = 0 
        #            conn.close
        #        else:
        #            rating_offsets = 0
        #        ratings[i] = {'label': f"{i} {rating_offsets}", 'value':i}
        #        print(i)
        #print(rating_offsets)
     

        return field_observations.to_dict('records'), [{"name": i, "id": i} for i in field_observations.columns], min, max, [min,max], offsets
        # [{'label': l, 'value': v} for l, v in offsets]
    else:
        dash.no_update
 
@app.callback(
    #Output('rating_graph', 'children'),
    Output('monitoring_peroid_table', 'data'),
    Output('monitoring_peroid_table', 'columns'),
    Output('rating_points_checklist', 'options'),
    
    
    Input('site_dropdown', 'value'),
    Input('field_observations', 'data'),
    Input('field_observations', 'columns'),
    #Output('rating_graph', 'children'),
    Input('monitoring_peroid_range_slider', 'value'),
    State('monitoring_peroid_table', 'data'),
    State('monitoring_peroid_table', 'columns'),
    
    

    
)
def monitoring_peroid_range(site, field_observations_data, field_observations_columns, monitoring_peroid_range_value, rows, columns):
    #changed_id = [p['monitoring_peroid_range_slider'] for p in dash.callback_context.triggered][0]
    
    if site == "0":
        return dash.no_update
    
    else: 
        dff = pd.DataFrame(rows)
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if (dff.empty) | ('site_dropdown' in changed_id):  
            field_observations = pd.DataFrame(field_observations_data)
            monitoring_peroid = pd.DataFrame(field_observations_data)
        else:
            field_observations = pd.DataFrame(rows)
            monitoring_peroid = pd.DataFrame(rows)
        monitoring_peroid['measurement_number'].astype(float, errors="ignore")
        monitoring_peroid = monitoring_peroid.loc[(monitoring_peroid.measurement_number >= monitoring_peroid_range_value[0]) & (monitoring_peroid.measurement_number <= monitoring_peroid_range_value[1])]

         # get minimum stage
        #min_q = field_observations[field_observations.discharge_observation == field_observations.discharge_observation.min()]
        #min_q.loc[:,'measurement_number'] = 9999
        #monitoring_peroid = monitoring_peroid.append(min_q)
        ## get maximum discharge
        #max_q = field_observations[field_observations.discharge_observation == field_observations.discharge_observation.max()]
        #max_q.loc[:,'measurement_number'] = 9999
        #monitoring_peroid = monitoring_peroid.append(max_q)
      
        
       
        rows = monitoring_peroid.to_dict('records')
        return rows, [{"name": i, "id": i} for i in monitoring_peroid.columns], monitoring_peroid['measurement_number'].to_list()

@app.callback(
     #Output('rating_points_checklist', 'options'),
    Output('stage_duplicate_error', 'children'),
    Output('discharge_duplicate_error', 'children'),
    Output('discharge_progress_error', 'children'),
    Output('rating_points_checklist', 'value'),
    Output('rating_graph', 'children'),
    
    Output('rating_points_table', 'data'),
    Output('rating_points_table', 'columns'),
    Output('rating_points_table', 'row_deletable'),
    Output('observation_statistics', 'data'),
    Output('observation_statistics', 'columns'),
    Input("create_rating", "value"),
    Input("export_rating", "n_clicks"),
    Input("rating_name", "value"),
    Input('site_dropdown', 'value'),
    Input('rating_curves', 'value'),
    Input('rating_points_table', 'data'),
    Input('rating_points_table', 'columns'),
    Input('editing-rows-button', 'n_clicks'),
    Input('graph_axis_type', 'value'),
    Input('gzf', 'value'),
    

    #Input('site_dropdown', 'value'),
    Input('field_observations', 'data'),
    Input('field_observations', 'columns'),
    #Output('rating_graph', 'children'),
    Input('monitoring_peroid_range_slider', 'value'),
    Input('monitoring_peroid_table', 'data'),
    Input('monitoring_peroid_table', 'columns'),
    Input('rating_points_checklist', 'value'),
    State('rating_points_table', 'data'),
    State('rating_points_table', 'columns'),
   )
    
   
    #State('rating_points_table', 'data'),
    #State('rating_points_table', 'columns'))

def rating_curve(create_rating_status, export_rating, rating_name, site, rating_curves, rating_points_table_row, rating_points_table_column, n_clicks, graph_axis_type, gzf, field_observations_data, field_observations_columns, monitoring_peroid_range_value, monitoring_peroid_table_data, monitoring_peroid_table_columns, rating_points_values, rows, columns):
        #print(rating_points_values)
        #if rating_points_values != 0:
        #if rating_points_values.shape[0] != 0:
        from data_cleaning import reformat_data
        from data_cleaning import rating_curve_equations
        from cache_graph import rating_graph
        # rating
       
        field_observations = pd.DataFrame(field_observations_data)
        dff = pd.DataFrame(rows)
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if (dff.empty) | ('monitoring_peroid_range_slider' in changed_id) | ('site_dropdown'  in changed_id):  
            #monitoring_peroid_table_data = monitoring_peroid_table_data.append(pd.DataFrame(data={'datetime': [.01+gzf], 'col2': [.01]}, index=[0]))
            monitoring_peroid = pd.DataFrame(monitoring_peroid_table_data)
            monitoring_peroid = reformat_data(monitoring_peroid)
            rating_points = monitoring_peroid[((monitoring_peroid['measurement_number'] >= monitoring_peroid_range_value[0] ) & (monitoring_peroid['measurement_number'] <= monitoring_peroid_range_value[1]) ) | (monitoring_peroid['measurement_number'] == 9999)]
              
           
        else:
            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
            if 'editing-rows-button' in changed_id:
                rating_points_table_row.append({c['id']: 0 for c in columns})
                monitoring_peroid = pd.DataFrame(rating_points_table_row)
                monitoring_peroid = reformat_data(monitoring_peroid)
                rating_points = monitoring_peroid[
                    (
                        (monitoring_peroid['measurement_number'] >= monitoring_peroid_range_value[0] ) &
                        (monitoring_peroid['measurement_number'] <= monitoring_peroid_range_value[1]) &
                        (monitoring_peroid['measurement_number'].isin(rating_points_values))
                        ) | (monitoring_peroid['measurement_number'] == 9999)
                        | (monitoring_peroid['measurement_number'] == 0)]
               
                rating_points = reformat_data(monitoring_peroid) 
               
            else:
                
                monitoring_peroid = pd.DataFrame(rating_points_table_row)
                monitoring_peroid = reformat_data(monitoring_peroid)
            
                rating_points = monitoring_peroid[
                    (
                        (monitoring_peroid['measurement_number'] >= monitoring_peroid_range_value[0] ) &
                        (monitoring_peroid['measurement_number'] <= monitoring_peroid_range_value[1]) &
                        (monitoring_peroid['measurement_number'].isin(rating_points_values))
                        ) | (monitoring_peroid['measurement_number'] == 9999)
                        | (monitoring_peroid['measurement_number'] == 0)]
                # rating points is a copy of monitoring peroid that is edited
                rating_points = reformat_data(monitoring_peroid)
        
        # if we are creating a rating, create a rating
        if create_rating_status == "True":
            print("rating status is true")
            rating_points, interpolate_function, interpolate_stage = rating_curve_equations(rating_points, gzf)
            new_rating = pd.DataFrame(data={'stage': np.arange((rating_points['observation_stage'].min()), (rating_points['observation_stage'].max()), 0.01),
                                    'stage_offset': np.arange((rating_points['observation_stage'].min())-gzf, (rating_points['observation_stage'].max())-gzf, 0.01),
                                    'discharge': interpolate_function(np.arange((rating_points['observation_stage'].min())-gzf, (rating_points['observation_stage'].max())-gzf, 0.01)), })
        if create_rating_status != "True":
            rating_points = rating_points[["datetime", "observation_stage", "discharge_observation", "measurement_number"]]
            # rating status is false
            # if we are looking at an existing rating but havent selected one, dont do anything
            if rating_curves[0] == "0":
                print("no rating selected")
                return dash.no_update
                
               

            if rating_curves[0] != "0": 
                print("rating curve selected")
                rating_value = rating_curves[0]
                # get site sql id for gdata function
                #sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection=yes;')
                #sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)

                #conn = sql_engine.raw_connection()
                with sql_engine.begin() as conn:
                    sql = f"select SITE_CODE as site_number, G_ID as site_sql_id from {config['parameters']['parameter_table']} WHERE STATUS = 'Active' AND FlowLevel = 'True'"
                site_list = pd.read_sql_query(sql, conn)
                
                # get site_number (SITE_CODE) and site_sql_id (G_ID)
                 #site = '31q'
                site_sql_id = site_list.loc[site_list['site_number'] == site, 'site_sql_id'].item()
                from rating import rating_calculator, rating_points_from_rating
                # rating calculation status is not needed for this application only for cache
                rating_calculation_status, interpolate_function, interpolate_stage, gzf = rating_calculator(rating_value, site_sql_id)
                #new_rating = pd.DataFrame(data={'stage': np.arange((rating_points['observation_stage'].min()), (rating_points['observation_stage'].max()), 0.01),
                ##                    'discharge': interpolate_function(np.arange((rating_points['observation_stage'].min())-gzf, (rating_points['observation_stage'].max())-gzf, 0.01)), })
                # you dont need rating offsets
                new_rating, rating_offsets = rating_points_from_rating(site, rating_value)
                new_rating.rename(columns={'water_level_rating': "stage_offset"}, inplace=True)
                new_rating.rename(columns={'discharge_rating': "discharge"}, inplace=True)
                new_rating["stage"] = new_rating['stage_offset']+gzf
                #y=rating_points['water_level_rating'],
                    #    x=rating_points['discharge_rating'],
                new_rating = new_rating[['stage', 'stage_offset', 'discharge']]
                
       
        #new_rating = pd.DataFrame(data={'stage': np.arange((rating_points['observation_stage'].min()), (rating_points['observation_stage'].max()), 0.01),
        #                            'stage_offset': np.arange((rating_points['observation_stage'].min())-gzf, (rating_points['observation_stage'].max())-gzf, 0.01),
        #                            'discharge': interpolate_function(np.arange((rating_points['observation_stage'].min())-gzf, (rating_points['observation_stage'].max())-gzf, 0.01)), })
        new_rating['discharge'] = round(new_rating['discharge'],2)
                
        rating_points['stage_offset'] = round(rating_points['observation_stage']-gzf, 2)
        sort = rating_points.sort_values(by=['measurement_number'])
                #try:
        observation_statistics = pd.DataFrame(monitoring_peroid_table_data)
        observation_statistics['stage_offset'] = round(observation_statistics['observation_stage']-gzf, 2)

        observation_statistics['discharge_rating'] = interpolate_function(observation_statistics['observation_stage']-gzf)
        observation_statistics['discharge_rating'] = round(observation_statistics['discharge_rating'],2)



        observation_statistics["rating_stage_for_observation"] = interpolate_stage(observation_statistics[ 'discharge_observation'])
        observation_statistics['rating_shift'] = round(observation_statistics['rating_stage_for_observation'] - (observation_statistics['observation_stage']-gzf), 2)
        observation_statistics["rating_stage_for_observation"] = round(((observation_statistics["rating_stage_for_observation"]-(observation_statistics['observation_stage']-gzf))/observation_statistics['rating_stage_for_observation'])*100, 2)
        observation_statistics.rename(columns={'rating_stage_for_observation': 'precent_difference'}, inplace=True)


        #observation_statistics['rating_shift'] = round(observation_statistics['discharge_observation'] - interpolate_function(observation_statistics['observation_stage']-gzf), 2)
        #observation_statistics['precent_difference'] = round(((interpolate_function(observation_statistics['observation_stage']-gzf)-observation_statistics['discharge_observation'])/(interpolate_function(observation_statistics['observation_stage']-gzf)))*100, 1)
        observation_statistics = observation_statistics[['measurement_number', 'datetime', 'observation_stage', 'stage_offset', 'discharge_observation', 'discharge_rating', 'rating_shift', 'precent_difference']]
               # except:
                #    observation_statistics = pd.DataFrame(monitoring_peroid_table_data)
        fig = rating_graph(field_observations, monitoring_peroid, rating_points, gzf, graph_axis_type, site, rating_curves, new_rating, observation_statistics)
        sort = rating_points.sort_values(by=['observation_stage'])
                
                #return  stage_duplicate_error, discharge_duplicate_error, discharge_progress_error, sort['measurement_number'].to_list(), fig, rating_points.to_dict('records'), [{"name": i, "id": i} for i in rating_points.columns], True, observation_statistics.to_dict('records'), [{"name": i, "id": i} for i in observation_statistics.columns]
        stage_duplicate_error = ""
        if rating_points.duplicated(subset=['observation_stage']).any() == True:
                stage_duplicate_error = "duplicate stage"
        discharge_duplicate_error = ""
        if rating_points.duplicated(subset=['discharge_observation']).any() == True:
                discharge_duplicate_error = "duplicate discharge"
        discharge_progress_error = ""
        dicharge_check = new_rating.sort_values(by='stage_offset', ascending=True)
        if dicharge_check['discharge'].is_monotonic_increasing is False:
                discharge_progress_error = "not increasing"
       
       
        # upload rating
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'export_rating' in changed_id:
            new_rating = new_rating.sort_values(by = "stage_offset")
            new_rating = new_rating.rename(columns={"stage_offset": "WaterLevel"})
            new_rating = new_rating.rename(columns={"discharge": "Discharge"})
            new_rating['RatingNumber'] = str(rating_name)
            # get site sql id
            #sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection=yes;')
            #sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)
            #conn = sql_engine.raw_connection()
            with sql_engine.begin() as conn:
                sql = f"select SITE_CODE as site_number, G_ID as site_sql_id from {config['parameters']['parameter_table']} WHERE STATUS = 'Active' AND FlowLevel = 'True'"
            site_list = pd.read_sql_query(sql, conn)
            
            # get site_number (SITE_CODE) and site_sql_id (G_ID)
            #site = '31q'
            site_sql_id = site_list.loc[site_list['site_number'] == site, 'site_sql_id'].item()
            # make marker numbers
            
            markers = np.arange((1), ((new_rating.shape[0])+1), 1)
            
            new_rating['Marker'] = markers
            new_rating['Marker'] = new_rating['Marker'].astype(int)
        
            # get field observations
            conn = sql_engine.raw_connection()
            new_rating['G_ID'] = site_sql_id
            new_rating = new_rating[['G_ID', 'RatingNumber', 'WaterLevel', 'Discharge', 'Marker']].copy()
             
        #sql_alchemy_connection = urllib.parse.quote_plus(f"DRIVER={{driver}}; SERVER={server}; DATABASE={database}, Trusted_Connection={trusted_connection}")
        
            #sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection= True;')
            #sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)
            #cnxn = sql_engine.raw_connection()
            with sql_engine.begin() as conn:
                new_rating.to_sql("tblFlowRatings", sql_engine, method=None, if_exists='append', index=False)
        # try method=multi, None works
        # try chunksize int
            

            
            rating_stats = pd.DataFrame(data = {'Rating_Number': [rating_name], 'Offset': [gzf], 'AutoDTStamp': [date.today()], 'Notes': ["Ok Rating"]})
            with sql_engine.begin() as conn:
                rating_stats.to_sql("tblFlowRating_Stats", sql_engine, method=None, if_exists='append', index=False)

        return  stage_duplicate_error, discharge_duplicate_error, discharge_progress_error, sort['measurement_number'].to_list(), fig, rating_points.to_dict('records'), [{"name": i, "id": i} for i in rating_points.columns], True, observation_statistics.to_dict('records'), [{"name": i, "id": i} for i in observation_statistics.columns]

          
# You could also return a 404 "URL not found" page here
if __name__ == '__main__':
    app.run_server(port="8050",host='127.0.0.1',debug=True)