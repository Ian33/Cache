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
import dash_ag_grid as dag

# add a note ####
# added a second note #
# a forth comment

# added a third note possibly in a branch?
import dash
from dash import html
from dash.dependencies import Input, Output, State
from dash import dcc
#from dash import html
from dash import dash_table
import pandas as pd
from datetime import date
import dash_datetimepicker
import dash_daq as daq

import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots
from scipy import stats, interpolate
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d, UnivariateSpline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sqlalchemy import create_engine
import urllib
# long call back 
# https://dash.plotly.com/long-callbacks
#import diskcache
from dash.long_callback import DiskcacheLongCallbackManager
from dash.long_callback import CeleryLongCallbackManager
#from celery import Celery
#cache = diskcache.Cache("./cache")
#long_callback_manager = DiskcacheLongCallbackManager(cache)



#celery_app = Celery(
#    __name__, broker="redis://localhost:6379/0", backend="redis://localhost:6379/1", external_stylesheets=external_stylesheets
#)
#long_callback_manager = CeleryLongCallbackManager(celery_app)

#app = dash.Dash(__name__, long_callback_manager=long_callback_manager)

## fix copy of slice error with df.loc[df.A > 5, 'A'] = 1000

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# a new comment
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets, long_callback_manager=long_callback_manager)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#Driver = 'SQL Server'
#Server = 'KCITSQLPRNRPX01'
#Database = 'gData'
#Trusted_Connection = 'yes'

config = configparser.ConfigParser()
config.read('gdata_config.ini')

comparison_sites = configparser.ConfigParser()
comparison_sites.read('gdata_config.ini')


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



Discharge_Table = 'tblDischargeGauging'
Discharge_Table_Raw = 'D_Value'
Discharge_DateTime = 'D_TimeDate'

Site_Table = 'tblGaugeLLID'

# Gives a string of available parameters to the SQL query
Available_Parameters = 'AirTemp, Barometer, Conductivity, DO, FlowLevel, Humidity, LakeLevel, pH, Piezometer, Precip, Relative_Humidity, SolarRad, Turbidity, WaterTemp, Water_Quality, Wind'
#filepath = r'C:/Users/ihiggins/cache.pkl'
#pickle.dump(Available_Parameters, open(filepath, 'wb'))
# Available_Parameters = Available_Parameters.tolist()
# Get site list
# Query SQL every sql query will need its own CONN
# INITIAL AVAILABLE BAROMOTERS

with sql_engine.begin() as conn:
        #gage_lookup = pd.read_sql_query('select G_ID, SITE_CODE from tblGaugeLLID;', conn)
        Available_Baros = pd.read_sql_query(
                        f"SELECT {config['site_identification']['site']} "
                        f"FROM {Site_Table} WHERE STATUS = 'Active' AND Barometer = 'True' ORDER BY {config['site_identification']['site']} ASC;", conn)

Available_Baros = Available_Baros[config['site_identification']
                    ["site"]].values.tolist()

# Barometer Association Table
Barometer_Association_Table = 'tblBaroLoggerAssociation'
with sql_engine.begin() as conn:
    Available_Sites = pd.read_sql_query("select SITE_CODE, G_ID from tblGaugeLLID WHERE STATUS = 'Active' ORDER BY SITE_CODE ASC;", conn)
    # site_sql_id = pd.read_sql_query(f"select G_ID as site_sql_id from tblGaugeLLID WHERE SITE_CODE = {site_number};", conn)
# this will need to change when there is more then just flowlevel
vlist = Available_Sites['SITE_CODE'].values.tolist()


app.layout = html.Div([
    # dcc.Location(id='url', refresh=False),
    # Select a Site
    # Site = site name site_sql_id is site number
    dcc.Dropdown(
        id='site',
        options=[{'label': i, 'value': i} for i in vlist],
        value='0', style={'display': 'block'}), html.Div(id='site_sql_id', style={'display': 'none'}),

    # Select a Parameter - get options from callback
    html.Div(
        dcc.Dropdown(id='Parameter', value='0'),
        # Create element to hide/show, in this case an 'Input Component'
        # <-- This is the line that will be changed by the dropdown callback
        style={'display': 'block'}
    ),
    # toggle between SQL query and file upload
    html.Div(
        daq.ToggleSwitch(id='Select_Data_Source', value=False),
    ),
    html.Div(id='Select_Data_Source_Output'),

    # Barometric Correction Radio Button
    # dynamic visability https://stackoverflow.com/questions/50213761/changing-visibility-of-a-dash-component-by-updating-other-component
    html.Div(
        # Create element to hide/show, in this case an 'Input Component'
        # dcc.store(id='Barometer_Data'),
        dcc.RadioItems(id='Barometer_Button',
                       options=[
                           {'label': 'Preform Barometric Correction', 'value': 'Baro'},
                           {'label': 'Do Not Preform Barometric Correction',
                               'value': 'No_Baro'}
                       ], value='No_Baro'), style={'display': 'block'}  # <-- This is the line that will be changed by the dropdown callback
    ),

    html.Div(
        dcc.Dropdown(
            id='Available_Barometers',
            options=[{'label': i, 'value': i} for i in Available_Baros],
            value="0",
            style={'display': 'none'}
        ),
    ),
    html.Button('Delete Association', id='Delete_Association', n_clicks=0),
    html.Div(id='New_Callback'),
    # Import file structures
    html.Div(
        # Create element to hide/show, in this case an 'Input Component'
        dcc.RadioItems(id='File_Structure',
                       options=[
                        {'label': 'onset_U20', 'value': 'onset_U20'},
                        {'label': 'onset_U24', 'value': 'onset_U24'},
                        {'label': 'aqua4plus_ct2x', 'value': 'aqua4plus_ct2x'},
                        {'label': 'csv', 'value': 'csv'}],
                       value='onset_U20'), style={'display': 'block'}  # <-- This is the line that will be changed by the dropdown callback
    ),

    # CSV Trimming
    html.Div([
        html.Div(daq.NumericInput(id='HEADER_ROWS', label='HEADER ROWS', labelPosition='top', value=1,), style={'width': '10%', 'display': 'inline-block'}),
        html.Div(daq.NumericInput(id='FOOTER_ROWS', label='FOOTER ROWS', labelPosition='top',value=0,), style={'width': '10%', 'display': 'inline-block'}),
        html.Div(daq.NumericInput(id='TIMESTAMP_COLUMN',label='TIMESTAMP_COLUMN', labelPosition='top', value=0,), style={'width': '10%', 'display': 'inline-block'}),
        html.Div(daq.NumericInput(id= 'DATA_COLUMN', label='DATA_COLUMN', labelPosition='top',value=1,), style={'width': '10%', 'display': 'inline-block'}),
    ]),

    dcc.Upload(
        id='datatable-upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
    ),
    # date time picker not native to dash see https://community.plotly.com/t/dash-timepicker/6541/10
    
    html.Div(
        # startDate and endDate are Dash specific variables
        dash_datetimepicker.DashDatetimepicker(
            id='select_range', startDate='', endDate=''),
        # Create element to hide/show, in this case an 'Input Component'
        # <-- This is the line that will be changed by the dropdown callback
        style={'display': 'block'}
    ),

    # page_action='none',
    html.Div(
        # Create element to hide/show, in this case an 'Input Component'
        dcc.RadioItems(id='select_data_level',
                       options=[
                           {'label': 'data', 'value': 'data'},
                           {'label': 'corrected_data', 'value': 'corrected_data'}
                       ], value='data'), style={'display': 'block'},  # <-- This is the line that will be changed by the dropdown callback
    ),
    # page_action='none',
    html.Div(id='output-container-date-picker-range'),

    # returns a graph
    html.Div(id='graph_output', style={'width': '100%', 'display': 'inline-block'}),
    html.Div(id="graph_where"),

    html.Div(
        dcc.Dropdown(
            id='Ratings',
            value='NONE'
        ),
        style={'display': 'block'}
    ),

    html.Div(id="display"),
    dcc.Store(id='import_data', storage_type='memory'),
    dcc.Store(id="barometer_corrected_data", storage_type='memory'),
    # visable data table
    # html.Div(dcc.RadioItems(['all data', 'observations','discharge observations'], 'All Data', id = "filter_options", inline=True)),
    
    html.Div([
    html.Div(
        dash_table.DataTable(
            id="Corrected_Data",
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
                'width': '200px', 'maxWidth': '200px', 'minWidth': '100px', },
            style_data_conditional=[{'if': {'column_id': 'comparison',}, 'backgroundColor': 'rgb(222,203,228)','color': 'black'},
                                    #{'if': {'column_id': 'parameter_observation', 'filter_query': '{} > 0'}, 'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{parameter_observation} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'observation_stage'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'datetime'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                    #{'if': {'filter_query': '{observation_stage} > 0','column_id': 'offset'},  'backgroundColor': 'rgb(179,226,205)','color': 'black'},
                                   
                                   # {'if': {'filter_query': '{{parameter_observation}} > {0}'),'backgroundColor': '#FF4136','color': 'white'},
            ],    
    
    ),style={'width': '80%', 'display': 'inline-block'}),
    
    html.Div([
            html.Div([
                dcc.Dropdown(id='comparison_site',options=[{'label': i, 'value': i} for i in vlist],value='0'), 
                html.Div(id='comparison_site_sql_id', style={'display': 'none'})
                    ]),
            html.Div(dcc.Dropdown(id='comparison_parameter', value='0'),),
            dcc.Checklist(id="checklist", options=['comparison_site'],value=['comparison_site'],inline=True),
            html.Div(html.Button('interpolate', id='interpolate_button')), 
            html.Div([   
                html.Button(id="run_pause", children="Run Job!"),
                html.Div([html.P(id="paragraph_id", children=["Button not clicked"])]),
                html.Div([daq.ToggleSwitch(id='realtime_update'),]), #dynamic default so sql query doesnt automatically correct for obs
                # html.Div([daq.ToggleSwitch(id='realtime_update', value=True),]), default automatically update
                html.Div(id='realtime_update_info'),
                ], style={'display': 'inline-block'}),
            html.Div([
                html.Div([html.P(id="header_rows_title", children=["add header rows"])]),
                dcc.Input(id="header_rows", type="number", value = 0,min=0, max=100, step=1,)
                ], style={'display': 'inline-block'}),

    ], style={'width': '20%', 'display': 'inline-block'}),
]),
  

    # fill_width=False, style_data={'width': '200px','maxWidth': '200px','minWidth': '100px',},
    html.Div(
        dash_table.DataTable(
            id="Initial_Data_Correction",
            virtualization=True,
        ),
        style={"display": "none"},
    ),
   
    # html.Br(),
    html.Div([  # big block
        html.Button('upload_data', id='upload_data_button', n_clicks=0),
        html.Div(id='upload_data_children', style={'width': '5%', 'display': 'inline-block'}),

        html.Button('export_data', id='export_data_button', n_clicks=0),
        html.Div(id='export_data_children', style={'width': '5%', 'display': 'inline-block'}),
    ]),

])


# Select file source
@app.callback(
    Output('Select_Data_Source_Output', 'children'),
    Input('Select_Data_Source', 'value'))
def update_output(Select_Data_Source):
    if Select_Data_Source is False:
        return 'File Import'
    if Select_Data_Source is True:
        return 'Database Query'


# display file upload
@app.callback(
    Output('datatable-upload', component_property='style'),
    Input('Select_Data_Source', 'value'))
def display_upload(Select_Data_Source):
    if Select_Data_Source is False:
        return {'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}
        # return {'display': 'block'}
    if Select_Data_Source is True:
        return {'display': 'none'}


# display file structure
@app.callback(
    Output('File_Structure', component_property='style'),
    Input('Select_Data_Source', 'value'))
def display_file_structure(Select_Data_Source):
    if Select_Data_Source is False:
        return {'display': 'block'}
        # return {'display': 'block'}
    if Select_Data_Source is True:
        return {'display': 'none'}

# run pause
@app.callback(
    Output('realtime_update', 'value'),
    Input('Select_Data_Source', 'value'))
def run_pause(select_data_source):
    # I think True should be sql query but that does not seem to work, however I think the true and false are confusing
    if select_data_source == False:  # if file upload automatically correct
        return True  # ealtime Update off
    if select_data_source == True: # if sql pause correction so uploaded data can be shown

        return False



# ONSET
@app.callback(
    Output('HEADER_ROWS', 'value'),
    Output('FOOTER_ROWS', 'value'),
    Output('TIMESTAMP_COLUMN', 'value'),
    Output('DATA_COLUMN', 'value'),
    Input('File_Structure', 'value'),
    Input('Parameter', 'value'))
def special_csv(file_structure, parameter):
    if parameter == "water_temperature":
        return list(config["file_structure_water_temperature"][file_structure].split(","))
    elif parameter == 'Conductivity' or parameter == 'conductivity':
        return list(config["file_structure_conducitvity"][file_structure].split(","))
    else:
        if file_structure == 'onset_U20':
            #return 2, 3, 1, 2
            return list(config["file_structure_discharge"][file_structure].split(","))
           # return config["file_structure_discharge"][file_structure]
        if file_structure == 'onset_U24':
            return 2, 3, 1, 4
        if file_structure == 'csv':
            return 1, 0, 0, 1


# CSV cutting one callback
@app.callback(
    Output('HEADER_ROWS', component_property='style'),
    Output('FOOTER_ROWS', component_property='style'),
    Output('TIMESTAMP_COLUMN', component_property='style'),
    Output('DATA_COLUMN', component_property='style'),
    Input('File_Structure', 'value'))
def display_csv_trimmer(File_Structure):
    if File_Structure == 'csv':
        return {'display': 'inline-block'}, {'display': 'inline-block'}, {'display': 'inline-block'}, {'display': 'inline-block'}
        # return {'display': 'block'}
    else:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

# Show or hide barometric selector; if a file is uploaded to application display the barometric pressure question
@app.callback(
    Output(component_id='Barometer_Button', component_property='style'),
    # esentially an inital pop up vs a delayed popup
    Input('Select_Data_Source', 'value'),
    # Input('datatable-upload', 'contents'),
    Input('Parameter', 'value'))
def show_hide_baro(Select_Data_Source, value):
    if Select_Data_Source is False:
        if value == "LakeLevel" or value == "Piezometer" or value == "FlowLevel" or value == "discharge" or value == "lake_level" or value == "water_level" or value == "groundwater_level":
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    if Select_Data_Source is True:
        return {'display': 'none'}


# Show or hide barometric search
@app.callback(
    Output(component_id='Available_Barometers', component_property='style'),
    Input('Barometer_Button', 'value'),
    Input('Select_Data_Source', 'value'),
    Input('Parameter', 'value'),
    Input(component_id='Barometer_Button', component_property='style'),)
def display_barometer_search(Barometer_Button, Select_Data_Source, value, style):
    if style == {'display': 'none'} or Barometer_Button == 'No_Baro':
        return {'display': 'none'}
    if style != {'display': 'none'}:
        return {'display': 'inline-block'}


# Get SQL Number from G_ID: site=name Site_Code site_sql_id = sql number G_ID
@app.callback(
    Output(component_id='site_sql_id', component_property='children'),
    Input(component_id='site', component_property='value'))
def get_sql_number_from_gid(site_value):
    if site_value != "0":
        search = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([site_value])]
        value = search.iloc[0, 1]
        return "{}".format(value)
    else:
        value = "0"
        return 'You have selected "{}"'.format(value)

# companion get sql number
@app.callback(
    Output(component_id='comparison_site_sql_id', component_property='children'),
    Input(component_id='comparison_site', component_property='value'))
def get_companion_sql_number_from_gid(site_value):
    if site_value != "0":
        search = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([site_value])]
        value = search.iloc[0, 1]
        return "{}".format(value)
    else:
        value = "0"
        return 'You have selected "{}"'.format(value)
# Barometer Search


@app.callback(
    Output(component_id='Available_Barometers', component_property='value'),
    Input(component_id='site_sql_id', component_property='children'),
    Input(component_id='Barometer_Button', component_property='value'),
    Input('Available_Barometers', 'style'))
def update_dp(site_sql_id, Barometer_Button, style):
    # if Site == '0':
    # return [{'label': '0', 'value': '0'}]
    if style != {'display': 'none'}:

        with sql_engine.begin() as conn:
            Baro_Gage = pd.read_sql_query('select WaterLevel_GID, Airpressure_GID from '+str(Barometer_Association_Table)+';', conn)
        
        Baro_Gage.reset_index()

        Baro_Gage_search = Baro_Gage.loc[Baro_Gage['WaterLevel_GID'].isin([site_sql_id])]
        # ILOC is row, column
        if Baro_Gage_search.empty:
            Baro_ID = ""
        else:
            Baro_ID = Baro_Gage_search.iloc[0, 1]
            search_2 = Available_Sites.loc[Available_Sites['G_ID'].isin([Baro_ID])]
            B_ID_Lookup = search_2.iloc[0, 0]
            return str(B_ID_Lookup)
    else:
        return str("")


# Delete Barometer Association
'''
@app.callback(
    Output('New_Callback', 'children'),
    Input(component_id='Available_Barometers', component_property='value'),
    Input(component_id='Site', component_property='value'),
    Input('Delete_Association', 'n_clicks'),)

def delete_association(n_clicks, Site, Available_Barometers):
    # if n_clicks == 1:
        # conn_7 = SQL_String
        # get g_id
        # s earch = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([Site])]
        # G_ID_Lookup = search.iloc[0,1]
        # search_2 = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([Available_Barometers])]
        # B_ID_Lookup = search_2.iloc[0,1]
        # cursor = conn_7.cursor()
        # conn_7.execute('delete from '+str(Barometer_Association_Table)+' WHERE WaterLevel_GID = '+str(G_ID_Lookup)+'')
        # conn_7.commit()
        # conn_8 = SQL_String
        # cursor = conn_8.cursor()
        # cursor.execute('INSERT INTO '+str(Barometer_Association_Table)+' (WaterLevel_GID, Airpressure_GID) VALUES(?,?)', str(G_ID_Lookup), str(search_2))
        # conn_8.commit()
        # return html.Div(str(search))
    # else:
        # return html.Div("nada")
'''


# Get Parameters
@app.callback(
    Output(component_id='Parameter', component_property='options'),
    Output(component_id='Parameter', component_property='style'),
    Input(component_id='site', component_property='value'),
    Input(component_id="site_sql_id", component_property="children"))
def update_parameters(site_value, site_sql_id):
    if site_value == '0':
        return [{'label': '0', 'value': '0'}], {'display': 'block'}
    if site_value != '0':
        # NEW CONN STRING
        with sql_engine.begin() as conn:
            Parameters = pd.read_sql_query(f"SELECT {Available_Parameters} from {config['parameters']['parameter_table']} WHERE G_ID = '{site_sql_id}' AND STATUS = 'Active';", conn)
        if "WaterTemp" in Parameters.columns:
            Parameters = Parameters.rename(
                columns={"WaterTemp": "water_temperature"})
        # vlist.set_index('SITE_CODE', inplace=True)
        Parameters = Parameters.loc[:, (Parameters != 0).any(axis=0)]
        # returns list of columns for dropdown
        Parameters = Parameters.columns.values.tolist()
        return [{'label': i, 'value': i} for i in Parameters], {'display': 'block'}

# companion parameters
@app.callback(
    Output(component_id='comparison_parameter', component_property='options'),
    Output(component_id='comparison_parameter', component_property='style'),
    Input(component_id='comparison_site', component_property='value'),
    Input(component_id="comparison_site_sql_id", component_property="children"))
def update_companion_parameters(site_value, site_sql_id):
    if site_value == '0':
        return [{'label': '0', 'value': '0'}], {'display': 'block'}
    if site_value != '0':
        # NEW CONN STRING
        with sql_engine.begin() as conn:
            Parameters = pd.read_sql_query(f"SELECT {Available_Parameters} from {config['parameters']['parameter_table']} WHERE G_ID = '{site_sql_id}' AND STATUS = 'Active';", conn)
        if "WaterTemp" in Parameters.columns:
            Parameters = Parameters.rename(
                columns={"WaterTemp": "water_temperature"})
        # vlist.set_index('SITE_CODE', inplace=True)
        Parameters = Parameters.loc[:, (Parameters != 0).any(axis=0)]
        # returns list of columns for dropdown
        Parameters = Parameters.columns.values.tolist()
        return [{'label': i, 'value': i} for i in Parameters], {'display': 'block'}

# Ratings
@app.callback(
    # Output('Ratings', 'value'),
    Output('Ratings', 'options'),
    Output('Ratings', 'style'),
    Input('Parameter', 'value'),
    Input('site_sql_id', 'children'))
def Select_Ratings(Parameter_value, site_sql_id):
   #print("select ratings")
    if Parameter_value == "FlowLevel":
        with sql_engine.begin() as conn:
            Ratings = pd.read_sql_query(f"select RatingNumber from tblFlowRatings WHERE G_ID = '{site_sql_id}' GROUP BY RatingNumber ORDER BY RatingNumber DESC;", conn)
        Ratings = Ratings['RatingNumber'].values.tolist()
    
        return [{'label': i, 'value': i} for i in Ratings], {'display': 'block'}
    else:
        return [{'label': "NONE", 'value': "NONE"}], {'display': 'none'}

# Pick Range, query existing data in SQL Database
@app.callback(
    # Output('output-container-date-picker-range', 'children'),
    Output('import_data', 'data'),
    # Input(component_id='Barometer_Button', component_property='value'),
    Input('select_range', 'startDate'),  # startDate is a dash parameter
    Input('select_range', 'endDate'),
    Input("site_sql_id", "children"),
    Input(component_id='Parameter', component_property='value'),
    Input('datatable-upload', 'contents'),
    Input('datatable-upload', 'filename'),
    Input('HEADER_ROWS', 'value'),
    Input('FOOTER_ROWS', 'value'),
    Input('TIMESTAMP_COLUMN', 'value'),
    Input('DATA_COLUMN', 'value'),
    Input('Select_Data_Source', 'value')
    # Input(component_id='Available_Barometers', component_property='value'),
    # State('Barometer_Button', 'value')
)
def update_daterange(startDate, endDate, site_sql_id, parameter, contents, filename, header_rows, footer_rows, timestamp_column, data_column, data_source):
    # Call and process incoming data
    # if there is no csv file (northing in contents) query data from sql server
    # contents = holder of imported data, when data is being imported contents = True
    # data_source is if we are quering the server vs importing data, select_data_source False is file import True is SQL query
    # program corrects off the "data" column but other values are pulled
    # if contents is None:  # nothin in datatable upload
    if data_source == True:  # query sql server
        # sql import, seperate module becuause its used by comparison upload
        from import_data import sql_import
        df = sql_import(parameter, site_sql_id, startDate, endDate)
        return  df.to_json(orient="split")
    if data_source == False:  # file upload
        # try 
        # with open(file_path, 'r') as file:
        # file_contents = file.read()
        # and run get field observations after data import for better error control
        if contents is not None:  # if there is a file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            # Assume that the user uploaded a CSV file
            # this assumes the file name ends in 'csv' or 'xls'
            def dateparse (time):    
                return pd.to_datetime( time, format='%Y%m%d %H:M:S', errors='ignore')
            # Assume that the user uploaded an excel file
            if 'xls' in filename or 'xlsx' in filename:
                df_import = pd.read_excel(decoded, usecols=[int(timestamp_column), int(
                    data_column)], skiprows=int(header_rows), skipfooter=int(footer_rows), names=['datetime', 'data'], parse_dates=[0], date_parser=dateparse)
            else: # if its a a csv or they didnt specift
                df_import = pd.read_csv(io.StringIO(decoded.decode('utf-8')), usecols=[int(
                    timestamp_column), int(data_column)], skiprows=int(header_rows), skipfooter=int(footer_rows), names=['datetime', 'data'], parse_dates=[0], date_parser=dateparse)
            return df_import.to_json(orient="split")
        if contents is None:  # nothing to upload
            df = pd.DataFrame()
            return df.to_json(orient="split")


    
@app.callback(
    Output("barometer_corrected_data", 'data'),
    #Input('datatable-upload-container', 'data'),
    Input('import_data', 'data'),
    # Input('datatable-upload-container', 'columns'),
    Input(component_id='Barometer_Button', component_property='value'),
    Input(component_id='Available_Barometers', component_property='value'),
    Input(component_id='Select_Data_Source', component_property='value'),
    Input("Parameter", "value"))
def update_Barometer(rows, Barometer_Button, Available_Barometers, Select_Data_Source, parameter):
    # barometer_corrected_data
    df = pd.read_json(rows, orient="split")

    if df.empty:
        df = pd.DataFrame()
        return df.to_json(orient="split")
    else:
        
        # df['DateTime'] = pd.strftime(df['DateTime'], format= '%Y%m%d %H:M:S', errors='ignore')
        # ISO-8601 Standard has a T between the date and time
        if Barometer_Button == "Baro" and Select_Data_Source is False:  # data source false is file import
            try:
                search = Available_Sites.loc[Available_Sites["SITE_CODE"].isin([Available_Barometers])]
                if search.empty:
                    #df['corrected_data'] = 0
                    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True
                else:
                    B_ID_Lookup = search.iloc[0, 1]
                    # THIS IS DUMB, ITS A PLACHHOULDER there needs to be a formula to convert wl feet
                    if df['data'].mean() < 30:
                        df['data'] = round((df['data']*68.9476), 3)

                    if df['data'].mean() > 999:
                        df['data'] = df['data']
                
                    from import_data import sql_import
                    baro_start_date = df.loc[df.index == 0, "datetime"].item()
                    baro_end_date =   df.loc[df.index == df.index[-1], "datetime"].item()
                    barometer_query = sql_import("barometer", B_ID_Lookup, baro_start_date, baro_end_date) # fx converts to PST and out of PST
                    
                    barometer_query = barometer_query.rename(columns = {"corrected_data": "barometer_data"})
                
                    # resample barometer to 5 minutes
                    barometer_query = barometer_query.set_index("datetime").resample('5T').interpolate(method='linear').reset_index(level=None, drop=False)

                    df = pd.merge(df,barometer_query[['datetime', "barometer_data"]],on=['datetime'])
                    df['data'] = ((df['data']-df["barometer_data"]) * 0.0335).round(3)
                    # Also a shotty conversion using a standard pressure
                    #df = df[['datetime', 'data']]
                    df = df.drop(['barometer_data'], axis=1)
                    return  df.to_json(orient="split")
            except TypeError:
                return df.to_json(orient="split")
            # If we arnt using a barometer this is just a passthrough
        else:
          
            return df.to_json(orient="split")
        


# select data level
@app.callback(
    Output('select_data_level', 'style'),
    Input('Select_Data_Source', 'value'))
def data_level(Select_Data_Source):
    # file import
    if Select_Data_Source is False:
        return {'display': 'none'}
    # database query - data
    elif Select_Data_Source is True:
        return {'display': 'block'}

# FIELD Observations and Data
@app.callback(
    Output("Initial_Data_Correction", "data"),
    Output("Initial_Data_Correction", "columns"),
    Input('Parameter', 'value'),
    Input("barometer_corrected_data", "data"),
    Input(component_id="site_sql_id", component_property="children"),
    Input('select_range', 'startDate'),  # startDate is a dash parameter
    Input('select_range', 'endDate'),)
def get_observations(parameter_value, barometer_corrected_data, site_sql_id, startDate, endDate):
    ''''Takes data in question and finds cooresponding observations
    returns data, with columns for observations does not trim or cut
    send to correct_data'''
    data_check = pd.read_json(barometer_corrected_data, orient="split")
    
    def merge_observations(data, observations):
        if not observations.empty:
            # obserervations are queried for a df +/- 12 hour window, search for the first and last observation for a 1 hour window
            # search for obs before start of record
            first = pd.merge_asof(data.head(1), observations.sort_values(
                'datetime'), on=['datetime'], tolerance=pd.Timedelta("60m"), direction="backward")
            last = pd.merge_asof(data.tail(1), observations.sort_values(
                'datetime'), on=['datetime'], tolerance=pd.Timedelta("60m"), direction="forward")
          
            data = pd.merge_asof(data, observations.sort_values(
                'datetime'), on=['datetime'], tolerance=pd.Timedelta("15m"), direction="nearest")
            
            data.loc[data.index == 0] = first.values.tolist()
            data.loc[data.index == data.index[-1]] = last.values.tolist()
           
        else:
            data["observation_stage"] = np.nan
        return data
    
    if data_check.empty:
        return [{}], []
    else:
        try:
            data = pd.read_json(barometer_corrected_data, orient="split")
            from data_cleaning import fill_timeseries
            data = fill_timeseries(data)
            from import_data import get_observations_join
            observations = get_observations_join(parameter_value, site_sql_id, startDate, endDate)
            #field_observations = get_observations()
            df = merge_observations(data, observations)
            if parameter_value == "FlowLevel" or parameter_value == "discharge":
                #df = get_parameter_observation(data, field_observations, parameter_value)
                df.rename(columns={"parameter_observation": "q_observation"}, inplace=True)
            if parameter_value == "Conductivity" or parameter_value == "conductivity" or parameter_value == "water_temperature":
                #df = get_parameter_observation(data, field_observations, parameter_value)
                if "observation_stage" in df.columns:
                    df.drop(columns=["observation_stage"], inplace=True)
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
        except ValueError:
             data = pd.read_json(barometer_corrected_data, orient="split")
             return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

@app.callback(
#@app.long_callback(
    # CORRECT FIELD data to FIELD OBSERVATIONS
    Output("paragraph_id", "children"),
    Output("realtime_update_info", "children"),
    Output("Corrected_Data", "data"),
    Output("Corrected_Data", "columns"),
    #Output("Corrected_Data", "style_data_conditional"),
    # returning a blank df cant have deletable rows
    Output("Corrected_Data", "row_deletable"),
    Output(component_id='graph_output', component_property='children'),
    Input("header_rows","value"),
    Input("realtime_update", "value"),
    Input("run_pause", "n_clicks"),
    Input('interpolate_button', 'n_clicks'),
    Input('select_range', 'startDate'),  # startDate is a dash parameter
    Input('select_range', 'endDate'),
    Input('checklist', 'value'),
    #Input('interpolate_button', 'n_clicks'),
    Input('select_data_level', 'value'),
    Input('site', 'value'),
    Input('site_sql_id', 'children'),
    Input('comparison_site_sql_id', 'children'),
    Input('Ratings', 'value'),
    Input(component_id='Parameter', component_property='value'),
    Input('comparison_parameter', 'value'),
    Input("Initial_Data_Correction", "data"),
    Input("Initial_Data_Correction", "columns"),
    Input("Corrected_Data", "data"),
    State("Corrected_Data", "data"),
    State("Corrected_Data", "columns"),)
    # disable outputs while callback is running
    #This example uses running to set the disabled property of the button to True while the callback is running, and False when it completes
   # manager=long_callback_manager,)
    
def correct_data(header_rows, realtime_update, run_pause, interpolate_button, start_date, end_date, checklist, data_level, site, site_sql_id, comparison_site_sql_id, ratings_value, Parameter_value, comparison_parameter, Initial_Data_Correction_row, Initial_Data_Correction_column, row, Corrected_Data_row, Corrected_Data_column):

    '''Takes dataframe of data and observations from function: get_observations '''
    df = pd.DataFrame(Initial_Data_Correction_row)
    from data_cleaning import style_formatting
    from data_cleaning import data_conversion
    from discharge import discharge_calculation, finalize_discharge_dataframe
    
    # if there is no data to look at dont show data table
    # Input(component_id='Parameter', component_property='value'),
    
    # field observaions function returns the field observation (observation_stage)
    # and parameter_observation where applicable
    # you need the stage observation to get the parameter observation
    try:
        observation = config[Parameter_value]["observation_class"]
    except:
        observation = ""
    # on initial open we can select data vs corrected data
    # this is a bit hacky.  We are correcting off of the data column
    # but we can change the data in the data column on initial import


    # initial dataframe re-format
    from data_cleaning import reformat_data
    # df_raw = reformat_data(df_raw)  
    def parameter_calculation(df):
      
        if observation not in df.columns:
            df[observation] = "nan"
        if 'offset' not in df_raw.columns:
            df["offset"] = "nan"
        df['offset'] = df[observation] - df[data_level]
        df['offset'].interpolate( method='linear', inplace=True, axis=0, limit_direction='both')
        df['corrected_data'] = (df[data_level]+df['offset']).round(2)
        df['offset'] = (df[observation] - df["data"]).round(2)
       
        return df
    
    

    # if there is no data return a blank dataframe
    if df.empty:
        return dash.no_update
        # if there is data to look at read the datatable
    else:
        # first calculate parameter
        dff = pd.DataFrame(row)
        if dff.empty:
            df_raw = pd.DataFrame(Initial_Data_Correction_row)
            
        if not dff.empty:
            df_raw = pd.DataFrame(row)
        
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'run_pause' in changed_id or dff.empty or realtime_update is True:
            df_raw = reformat_data(df_raw) 
            df_raw = data_conversion(df_raw, Parameter_value)
            df_raw = parameter_calculation(df_raw)
            callback_state = "updating"
            realtime_update_info = "realtime updating; if slow pause"
        # I think you only need this run-pause once as the dash.no_update should stop downstream processes
        if 'run_pause' not in changed_id and not dff.empty and realtime_update is False:
             return dash.no_update
        if realtime_update is False:
            realtime_update_info = "realtime updating paused"

        # re-arrange non discharge dataframe
        if Parameter_value != 'FlowLevel':
            if "comparison" in df_raw.columns:
                df_raw = df_raw[["datetime", "data", "corrected_data", observation, "offset", "estimate", "comparison"]]
            if "comparison" not in df_raw.columns:
                df_raw = df_raw[["datetime", "data", "corrected_data", observation, "offset", "estimate"]]
        # calculate discharge
        if Parameter_value == 'FlowLevel':
                if not 'discharge' in df_raw.columns:
                    df_raw['discharge'] = 0
                if not 'q_observation' in df_raw.columns:
                    df_raw['q_observation'] = 'nan'
               
                if ratings_value == 'NONE':  # If there is no discharge calculate a discharge of zero
                    df_raw["q_offset"] = "nan"
                    df_raw["precent_q_change"] = "nan"
                    df_raw["RatingNumber"] = "NONE"
                else:
                    df_raw = discharge_calculation(df_raw, ratings_value, site_sql_id)
                    
                df_raw = finalize_discharge_dataframe(df_raw)
        # for whatever reasion this style conditional stopped working when i added the graph to the callback
        ### ADD comparison site
        from data_cleaning import add_comparison_site
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if comparison_parameter != "0" and 'comparison_parameter' in changed_id and "comparison_site" in checklist:
            if "comparison" in df_raw.columns:
               df_raw.drop(columns=['comparison'], inplace=True)
            else:
                df_raw = add_comparison_site(comparison_site_sql_id, comparison_parameter, df_raw)

        if "comparison_site" not in checklist:
            if "comparison" in df_raw.columns:
               df_raw.drop(columns=['comparison'], inplace=True)
            else:
                pass
        from cache_graph import graph_display
        #if (df_raw.empty or len(df_raw.columns) < 1):
        #    return dash.no_update
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        
        # if 'interpolate' in checklist and "comparison" in df_raw.columns:
        #if 'interpolate_button' in changed_id and "comparison" in df_raw.columns:
        if 'interpolate_button' in changed_id:
            #from data_cleaning import interpolate_function
            from interpolate.interpolation import cache_comparison_interpolation
            df_raw = cache_comparison_interpolation(df_raw, site, site_sql_id, Parameter_value, start_date, end_date)
    
        #if "header_rows" in changed_id:
        #if header_rows > 0:
               # if start_date == '':
        #        start_date = df.loc[df.datetime == df.datetime.min, "datetime"].item()
        #        start_date = df.loc[df.datetime == df.datetime.max, "datetime"].item()
                
        #        start_date = (start_date - timedelta(minutes=(header_rows)*15))
                #end_date = (end_date - timedelta(minutes=(0))).strftime("%m/%d/%Y %H:%M")
                
        #        from import_data import sql_import
                
        #        existing_data = sql_import(Parameter_value, site_sql_id, (start_date - timedelta(minutes=(header_rows)*15)), start_date)
                
        #        existing_data = existing_data[['datetime', 'corrected_data']]
        #        existing_data = existing_data.rename(columns={"corrected_data": "existing_data"})
                ## fill blanks in existing data
        #        if not existing_data.empty:
        #            df_raw = df_raw.merge(existing_data, on = "datetime", how = "outer")
        #            df_raw = df_raw.sort_values(by='datetime', ascending=False)
       
        df_raw = df_raw.sort_values(by='datetime', ascending=False)
        from graph_2 import cache_graph_export
      
        fig = cache_graph_export(df_raw, site_sql_id, site, Parameter_value)
        #return df_raw.to_dict('records'), [{"name": i, "id": i} for i in df_raw.columns], [], True, fig
        return [f"{realtime_update_info}"],[f"{callback_state}"], df_raw.to_dict('records'), [{"name": i, "id": i} for i in df_raw.columns], True, fig

@app.callback(
    dash.dependencies.Output('upload_data_children', 'children'),
    [dash.dependencies.Input('upload_data_button', 'n_clicks')],
    Input('Corrected_Data', 'data'),
    Input('Parameter', 'value'),
    Input('site_sql_id', 'children'),
    Input('site', 'value'),
    )
def run_upload_data(n_clicks, rows, parameter, site_sql_id, site):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'upload_data_button' not in changed_id:
        return dash.no_update
    
    #today = pd.to_datetime("today")

    elif 'upload_data_button' in changed_id:
        df = pd.DataFrame(rows)
        notes_df = df
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if (df.empty or len(df.columns) < 1):
            return dash.no_update
        else:

            from cache_graph import graph
            #from cache_graph import save_fig
            from cache_graph import format_cache_data
            # IF THERE is existing eata drop it
            if "existing_data" in df.columns:
                df = df.loc[df.existing_data.isnull()]
            df, parameter, observation, end_time = format_cache_data(df, parameter)
            df_export = df.set_index('datetime')
            df_export.to_csv("W:/STS/hydro/GAUGE/Temp/Ian's Temp/" +
                str(site)+"_"+str(parameter)+"_"+str(end_time)+".csv")
            df_export.to_csv("C:/Users/ihiggins/OneDrive - King County/cache_upload/" +
                str(site)+"_"+str(parameter)+"_"+str(end_time)+".csv")

            from graph_2 import save_fig
            #fig = graph_display(df_raw, site, Parameter_value, observation)
            
            save_fig(df, site_sql_id, site, parameter)
            from sql_upload import full_upload
            if parameter == "Conductivity" or parameter == "conductivity":
                parameter = "Conductivity"
                df = df[["datetime", "data", "corrected_data", "estimate"]]
            if parameter == "water_level" or parameter == "LakeLevel":
                parameter = "water_level"
                df = df[["datetime", "data", "corrected_data", "estimate"]]
            if parameter == 'groundwater_level' or parameter == "Piezometer":
                parameter = "groundwater_level"
                df = df[["datetime", "data", "corrected_data", "estimate"]]
            if parameter == 'water_temperature':
                df = df[["datetime", "data", "corrected_data", "estimate"]]
            if parameter == "discharge" or parameter == "FlowLevel":
                parameter = "discharge"
                df = df[["datetime", "data", "corrected_data", "discharge", "estimate"]]
            full_upload(df, parameter, site_sql_id, 7)
            
            from workup_notes import workup_notes_main

            workup_notes_main(notes_df, parameter, site_sql_id, site)
            
            result = "  uploaded"

            return result
    else:
        return dash.no_update

@app.callback(
    dash.dependencies.Output('export_data_children', 'children'),
    [dash.dependencies.Input('export_data_button', 'n_clicks')],
    Input('Corrected_Data', 'data'),
    Input('Parameter', 'value'),
    Input('site_sql_id', 'children'),
    Input('site', 'value'),
    )
def run_export_data(n_clicks, rows, parameter, site_sql_id, site):
    ''' uses same function as update graph, this code is becomingly increasingly redundent '''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'export_data_button' not in changed_id:
        return dash.no_update
    
    if 'export_data_button' in changed_id:
        df_raw = pd.DataFrame(rows)
        #from cache_graph import graph
        #from cache_graph import save_fig
        from cache_graph import format_cache_data
        if (df_raw.empty or len(df_raw.columns) < 1):
            return dash.no_update
        else:
            df, parameter, observation, end_time = format_cache_data(df_raw, parameter)
            df_export = df.set_index('datetime')
            df_export.to_csv("W:/STS/hydro/GAUGE/Temp/Ian's Temp/" +
                str(site)+"_"+str(parameter)+"_"+str(end_time)+".csv")
            df_export.to_csv("C:/Users/ihiggins/OneDrive - King County/cache_upload/" +
                str(site)+"_"+str(parameter)+"_"+str(end_time)+".csv")

            from graph_2 import save_fig
            #fig = graph_display(df_raw, site, Parameter_value, observation)
            #fig = parameter_graph(df, site_sql_id, site, parameter)
            save_fig(df, site_sql_id, site, parameter)

            result = "  exported"
            return result
            #return result
    else:
        return dash.no_update
        print("")


# You could also return a 404 "URL not found" page here
if __name__ == '__main__':
    app.run_server(port="8050",host='127.0.0.1',debug=True)
   
    #app.run_server(host='0.0.0.0',port='8050')  
    # ethernet adapter ipv4 address 10.219.226.110
    #app.run_server(host='10.219.226.110',port='8050')  
    # ethernet adapter default gateway 10.219.224.1 # doesnt work
    #app.run_server(host='10.219.224.1',port='8050') # doesnt work
    # wireless lan adapter ipv4 address 192.168.0.193
   # app.run_server(host='192.168.0.193',port='8050') # launches but cannot access
    # default gateway  192.168.0.1
    #app.run_server(host='192.168.0.1',port='8050') # doesnt work
    # this computers actual ip address will be someting in the 192 range.
    # launch app with 0.0.0.0 and access it remotely with 192.x.x.x. ipaddress and port