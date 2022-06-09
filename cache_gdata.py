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
# add a note ####
# added a second note #
# a forth comment

# added a third note possibly in a branch?
import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
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

#Driver = 'SQL Server'
#Server = 'KCITSQLPRNRPX01'
#Database = 'gData'
#Trusted_Connection = 'yes'

config = configparser.ConfigParser()
config.read('gdata_config.ini')

#Driver = config['sql_connection']['Driver']
#Server = config['sql_connection']['Server']
#Database = config['sql_connection']['Database']
#Trusted_Connection = config['sql_connection']['Trusted_Connection']
SQL_String = pyodbc.connect('Driver={'+config['sql_connection']['Driver']+'};'
                            'Server='+config['sql_connection']['Server']+';'
                            'Database=' +
                            config['sql_connection']['Database']+';'
                            'Trusted_Connection='+config['sql_connection']['Trusted_Connection']+';')

Discharge_Table = 'tblDIschargeGauging'
Discharge_Table_Raw = 'D_Value'
Discharge_DateTime = 'D_TimeDate'

Site_Table = 'tblGaugeLLID'

# Gives a string of available parameters to the SQL query
Available_Parameters = 'AirTemp, Barometer, Conductivity, DO, FlowLevel, Humidity, LakeLevel, pH, Piezometer, Precip, Relative_Humidity, SolarRad, Turbidity, WaterTemp, Water_Quality, Wind'
# Available_Parameters = Available_Parameters.tolist()
# Get site list
# Query SQL every sql query will need its own CONN
# INITIAL AVAILABLE BAROMOTERS
conn_4 = SQL_String
Available_Baros = pd.read_sql_query(
    'select G_ID, SITE_CODE, Barometer, STATUS from '+str(Site_Table)+';', conn_4)
Available_Baros = Available_Baros[Available_Baros['STATUS'] == 'Active']
Available_Baros.sort_values(
    config['site_identification']["site"], inplace=True)
#vlist.set_index('SITE_CODE', inplace=True)
Available_Baros = Available_Baros[Available_Baros['Barometer'] == True]
Available_Baros = Available_Baros[config['site_identification']
                                  ["site"]].values.tolist()

# Barometer Association Table
Barometer_Association_Table = 'tblBaroLoggerAssociation'
conn_1 = SQL_String
Available_Sites = pd.read_sql_query(
    'select SITE_CODE, G_ID, FLOWLEVEL, STATUS from tblGaugeLLID;', conn_1)
Available_Sites = Available_Sites[Available_Sites['STATUS'] == 'Active']
# this will need to change when there is more then just flowlevel
# Available_Sites = Available_Sites[Available_Sites['FLOWLEVEL']== True]
Available_Sites.sort_values('SITE_CODE', inplace=True)
vlist = Available_Sites['SITE_CODE'].values.tolist()


app.layout = html.Div([
    # dcc.Location(id='url', refresh=False),
    # Select a Site
    # Site = site name site_sql_id is site number
    dcc.Dropdown(
        id='site',
        options=[{'label': i, 'value': i} for i in vlist],
        value='0'), html.Div(id='site_sql_id', style={'display': 'none'}),

    # Select a Parameter - get options from callback
    html.Div(
        dcc.RadioItems(id='Parameter', value='0'),
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
                           {'label': 'ONSET', 'value': 'ONSET'},
                           {'label': 'CSV', 'value': 'CSV'}
                       ], value='ONSET'), style={'display': 'block'}  # <-- This is the line that will be changed by the dropdown callback
    ),

    # CSV Trimming
    html.Div(
        daq.NumericInput(
            id='HEADER_ROWS',
            label='HEADER ROWS',
            labelPosition='bottom',
            value=1,
        ),
    ),

    html.Div(
        daq.NumericInput(
            id='FOOTER_ROWS',
            label='FOOTER ROWS',
            labelPosition='bottom',
            value=0,
        ),
    ),

    html.Div(
        daq.NumericInput(
            id='TIMESTAMP_COLUMN',
            label='TIMESTAMP_COLUMN',
            labelPosition='bottom',
            value=0,
        ),
    ),

    html.Div(
        daq.NumericInput(
            id='DATA_COLUMN',
            label='DATA_COLUMN',
            labelPosition='bottom',
            value=1,
        ),
    ),

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
                       ], value='corrected_data'), style={'display': 'block'},  # <-- This is the line that will be changed by the dropdown callback
    ),
    # page_action='none',
    html.Div(id='output-container-date-picker-range'),
    html.Div(
        # Create element to hide/show, in this case an 'Input Component'
        # This is the line that will be changed by the dropdown callback
        dcc.Graph(id='datatable-upload-graph'), style={'display': 'block'}
    ),

    html.Div(
        dcc.Dropdown(
            id='Ratings',
            value='NONE'
        ),
        style={'display': 'block'}
    ),

    html.Div(id="display"),
    dcc.Store(id='intermediate-value'),
    # visable data table
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
            style_data={
                'width': '200px', 'maxWidth': '200px', 'minWidth': '100px', },
        ),
    ),
    # fill_width=False, style_data={'width': '200px','maxWidth': '200px','minWidth': '100px',},
    html.Div(
        dash_table.DataTable(
            id="Initial_Data_Correction",
            virtualization=True,
        ),
        style={"display": "none"},
    ),
    html.Div(
        dash_table.DataTable(
            id="Barometer",
            virtualization=True
        ),
        style={"display": "none"}
    ),
    html.Div(
        dash_table.DataTable(
            id='datatable-upload-container',
            virtualization=True
        ),
        style={"display": "none"}
    ),
    # html.Br(),
    html.Div([  # big block

        html.Button('export_data', id='export_data_button', n_clicks=0),
        html.Div(id='export_data_children', style={'display': 'block'}),

        html.Button('upload_data', id='upload_data_button', n_clicks=0),
        html.Div(id='upload_data_children', style={'display': 'block'}),

        html.Button('export_upload_data',
                    id='export_upload_data_button', n_clicks=0),
        html.Div(id='export_upload_data_children', style={'display': 'block'}),


    ]),
    dcc.Download(id="download-dataframe-csv"),
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


# ONSET
@app.callback(
    Output('HEADER_ROWS', 'value'),
    Output('FOOTER_ROWS', 'value'),
    Output('TIMESTAMP_COLUMN', 'value'),
    Output('DATA_COLUMN', 'value'),
    Input('File_Structure', 'value'))
def special_csv(File_Structure):
    if File_Structure == 'ONSET':
        return 2, 3, 1, 2
    if File_Structure == 'CSV':
        return 1, 0, 0, 1


# CSV cutting
@app.callback(
    Output('HEADER_ROWS', component_property='style'),
    Input('File_Structure', 'value'))
def display_HEADER_ROWS(File_Structure):
    if File_Structure == 'CSV':
        return {'display': 'inline-block'}
        # return {'display': 'block'}
    else:
        return {'display': 'none'}


# CSV cutting
@app.callback(
    Output('FOOTER_ROWS', component_property='style'),
    Input('File_Structure', 'value'))
def display_FOOTER_ROWS(File_Structure):
    if File_Structure == 'CSV':
        return {'display': 'inline-block'}
        # return {'display': 'block'}
    else:
        return {'display': 'none'}


# CSV cutting
@app.callback(
    Output('TIMESTAMP_COLUMN', component_property='style'),
    Input('File_Structure', 'value'))
def display_TIMESTAMP(File_Structure):
    if File_Structure == 'CSV':
        return {'display': 'inline-block'}
        # return {'display': 'block'}
    else:
        return {'display': 'none'}


# CSV cutting
@app.callback(
    Output('DATA_COLUMN', component_property='style'),
    Input('File_Structure', 'value'))
def display_DATA(File_Structure):
    if File_Structure == 'CSV':
        return {'display': 'inline-block'}
        # return {'display': 'block'}
    else:
        return {'display': 'none'}


# Show or hide barometric selector; if a file is uploaded to application display the barometric pressure question
@app.callback(
    Output(component_id='Barometer_Button', component_property='style'),
    # esentially an inital pop up vs a delayed popup
    Input('Select_Data_Source', 'value'),
    # Input('datatable-upload', 'contents'),
    Input('Parameter', 'value'))
def show_hide_baro(Select_Data_Source, value):
    if Select_Data_Source is False:
        if value == "LakeLevel":
            return {'display': 'block'}
        if value == "Piezometer":
            return {'display': 'block'}
        if value == "FlowLevel":
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
        conn_6 = SQL_String
        Baro_Gage = pd.read_sql_query(
            'select WaterLevel_GID, Airpressure_GID from '+str(Barometer_Association_Table)+';', conn_6)
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
        return [{'label': '0', 'value': '0'}], {'display': 'none'}
    if site_value != '0':
        # NEW CONN STRING
        conn_3 = SQL_String
        Parameters = pd.read_sql_query('select G_ID, STATUS, '+str(
            Available_Parameters)+' from tblGaugeLLID WHERE G_ID= '+str(site_sql_id)+';', conn_3)
        # Filter by active sites
        Parameters = Parameters[Parameters['STATUS'] == 'Active']
        # remove the guide columns
        Parameters.drop(columns=['G_ID', 'STATUS'], inplace=True)
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
    if Parameter_value == "FlowLevel":
        # Get GID
        conn_20 = SQL_String
        Ratings = pd.read_sql_query(
            'select RatingNumber from tblFlowRatings WHERE G_ID = '+str(site_sql_id)+';', conn_20)
        Ratings.drop_duplicates(inplace=True)
        Ratings.sort_values('RatingNumber', inplace=True)
        # vlist.set_index('SITE_CODE', inplace=True)
        Ratings = Ratings['RatingNumber'].values.tolist()
        return [{'label': i, 'value': i} for i in Ratings], {'display': 'block'}
    else:
        return [{'label': "NONE", 'value': "NONE"}], {'display': 'none'}


# Pick Range, query existing data in SQL Database
@app.callback(
    # Output('output-container-date-picker-range', 'children'),
    Output('datatable-upload-container', 'data'),
    Output('datatable-upload-container', 'columns'),
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
        if startDate != '' and endDate != '':
            if parameter == "FlowLevel":
                # NEW CONN STRING
                conn_2 = SQL_String
                # QUERY Discharge
                df = pd.read_sql_query('select '+config[parameter]['datetime']+','+config[parameter]['data']+','+config[parameter]['corrected_data']+','+config[parameter]['discharge'] +
                                       ' from '+config[parameter]['table']+' WHERE G_ID = '+str(site_sql_id)+' AND '+config[parameter]['datetime']+' between ? and ?', conn_2, params=[str(startDate), str(endDate)])
                df.rename(columns={
                    df.columns[0]: "datetime",
                    df.columns[1]: "data",
                    df.columns[2]: "corrected_data",
                    df.columns[3]: "discharge",
                }, inplace=True)

            if parameter != "FlowLevel":
                # NEW CONN STRING
                conn_3 = SQL_String
                # QUERY non discharge
                df = pd.read_sql_query('select '+config[parameter]['datetime']+','+config[parameter]['data']+','+config[parameter]['corrected_data']+' from '+config[parameter]
                                       ['table']+' WHERE G_ID = '+str(site_sql_id)+' AND '+config[parameter]['datetime']+' between ? and ?', conn_3, params=[str(startDate), str(endDate)])
                df.rename(columns={
                    df.columns[0]: "datetime",
                    df.columns[1]: "data",
                    df.columns[2]: "corrected_data",
                }, inplace=True)
            # convert to date time and take out of utc
            df["datetime"] = pd.to_datetime(
                df["datetime"]) - timedelta(hours=7)
            # sort
            df.sort_values(by="datetime", inplace=True)
            # df2 = Baro_Query(df)
            df["datetime"] = pd.to_datetime(
                df["datetime"], format='%Y%m%d %H:M:S', errors='ignore')
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
        # return blank for a variety of situations
        else:
            return [{}], []
    if data_source == False:  # file upload
        if contents is not None:  # if there is a file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            # Assume that the user uploaded a CSV file
            # this assumes the file name ends in 'csv' or 'xls'
            if 'csv' in filename:
                df_csv = pd.read_csv(io.StringIO(decoded.decode('utf-8')), usecols=[int(
                    timestamp_column), int(data_column)], skiprows=int(header_rows), skipfooter=int(footer_rows))
                df_csv.rename(columns={
                    df_csv.columns[0]: "datetime",
                    df_csv.columns[1]: "data",
                }, inplace=True)
                df_csv["datetime"] = pd.to_datetime(
                    df_csv["datetime"], format='%Y%m%d %H:M:S', errors='ignore')

                return df_csv.to_dict('records'), [{"name": i, "id": i} for i in df_csv.columns]
            # Assume that the user uploaded an excel file
            if 'xls' in filename:
                df_xls = pd.read_excel(decoded, usecols=[int(timestamp_column), int(
                    data_column)], skiprows=int(header_rows), skipfooter=int(footer_rows))
                df_xls.rename(columns={
                    df_xls.columns[0]: "datetime",
                    df_xls.columns[1]: "data",
                }, inplace=True)
                df_xls["datetime"] = pd.to_datetime(
                    df_xls["datetime"], format='%Y%m%d %H:M:S', errors='ignore')
            if 'xlsx' in filename:
                df_xls = pd.read_excel(decoded, usecols=[int(timestamp_column), int(
                    data_column)], skiprows=int(header_rows), skipfooter=int(footer_rows))
                df_xls.rename(columns={
                    df_xls.columns[0]: "datetime",
                    df_xls.columns[1]: "data",
                }, inplace=True)
                df_xls["datetime"] = pd.to_datetime(
                    df_xls["datetime"], format='%Y%m%d %H:M:S', errors='ignore')
            # if these dont work try csv
            else:
                df_csv = pd.read_csv(io.StringIO(decoded.decode('utf-8')), usecols=[int(
                    timestamp_column), int(data_column)], skiprows=int(header_rows), skipfooter=int(footer_rows))
                df_csv.rename(columns={
                    df_csv.columns[0]: "datetime",
                    df_csv.columns[1]: "data",
                }, inplace=True)
                df_csv["datetime"] = pd.to_datetime(
                    df_csv["datetime"], format='%Y%m%d %H:M:S', errors='ignore')
                return df_csv.to_dict('records'), [{"name": i, "id": i} for i in df_csv.columns]
        if contents is None:  # nothing to upload
            return [{}], []


@app.callback(
    Output("Barometer", 'data'),
    Output("Barometer", "columns"),
    Output('Barometer', 'row_deletable'),
    Input('datatable-upload-container', 'data'),
    # Input('datatable-upload-container', 'columns'),
    Input(component_id='Barometer_Button', component_property='value'),
    Input(component_id='Available_Barometers', component_property='value'),
    Input(component_id='Select_Data_Source', component_property='value'),
    Input("Parameter", "value"))
def update_Barometer(rows, Barometer_Button, Available_Barometers, Select_Data_Source, parameter):
    df = pd.DataFrame(rows)
    if df.empty:
        return [{}], [], False
    else:
        # df['DateTime'] = pd.strftime(df['DateTime'], format= '%Y%m%d %H:M:S', errors='ignore')
        # ISO-8601 Standard has a T between the date and time
        if Barometer_Button == "Baro" and Select_Data_Source is False:  # data source false is file import
            search = Available_Sites.loc[Available_Sites["SITE_CODE"].isin(
                [Available_Barometers])]
            if search.empty:
                df['barometer'] = 0
                # since we are using a barometer and none selected no correction
                df['corrected_data'] = 0

                return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True
            else:
                B_ID_Lookup = search.iloc[0, 1]
                # THIS IS DUMB, ITS A PLACHHOULDER there needs to be a formula to convert wl feet
                unit_check = df['data'].mean()
                if unit_check < 30:
                    df['data'] = round((df['data']*68.9476), 3)

                if unit_check > 999:
                    df['data'] = df['data']

                conn_9 = SQL_String
                head_sql = df.head(1)
                head_sql.reset_index(inplace=True)
                head_sql = pd.DataFrame.to_string(head_sql, buf=None, columns=[
                                                  'datetime'], index=None, header=None)
                head_sql = pd.to_datetime(head_sql)
                head_sql = head_sql.to_pydatetime()
                head_sql = head_sql + timedelta(hours=7)
                head_sql = head_sql.strftime("%m/%d/%Y %H:%M")

                tail_sql = df.tail(1)
                tail_sql.reset_index(inplace=True)
                tail_sql = pd.DataFrame.to_string(tail_sql, buf=None, columns=[
                                                  'datetime'], index=None, header=None)
                tail_sql = pd.to_datetime(tail_sql)
                # convert pandas timestamp to python timestamp
                tail_sql = tail_sql.to_pydatetime()
                tail_sql = tail_sql + timedelta(hours=7)
                tail_sql = tail_sql.strftime("%m/%d/%Y %H:%M")
                # gData barometer does not have a corrected/raw
                # I am calling the "B_Value" table as it was corrected
                barometer_query = pd.read_sql_query('select '+config['barometer']["datetime"]+', '+config['barometer']["corrected_data"]+' from '+config['barometer']["table"]+' WHERE G_ID = '+str(
                    B_ID_Lookup)+' AND '+config['barometer']["datetime"]+' between ? and ?', conn_9, params=[head_sql, tail_sql])
                barometer_query = barometer_query.rename(
                    columns={config['barometer']["datetime"]: "datetime", config['barometer']["corrected_data"]: "barometer_data"})
                barometer_query["datetime"] = pd.to_datetime(
                    barometer_query["datetime"])
                barometer_query["datetime"] = pd.to_datetime(
                    barometer_query["datetime"] - timedelta(hours=7))
                df['datetime'] = pd.to_datetime(df['datetime'])
                barometer_query.set_index("datetime", inplace=True)
                barometer_query = barometer_query.resample(
                    '5T').interpolate(method='linear')
                barometer_query.reset_index(
                    level=None, drop=False, inplace=True)
                df = pd.merge(df,
                              barometer_query[['datetime', "barometer_data"]],
                              on=['datetime'])
                df['data'] = ((df['data']-df["barometer_data"]) * 0.0335).round(3)
                # Also a shotty conversion using a standard pressure
                df = df[['datetime', 'data']]
                return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True
        # If we arnt using a barometer this is just a passthrough
        else:
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True


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
    Output("Initial_Data_Correction", "row_deletable"),
    Input('Parameter', 'value'),
    Input("Barometer", "data"),
    Input("Barometer", "columns"),
    Input(component_id='site', component_property='value'),
    Input(component_id="site_sql_id", component_property="children"),
    Input('Ratings', 'value'),)
def get_observations(parameter_value, Barometer_rows, Barometer_columns, site, site_sql_id, Ratings_value):
    ''''Takes data in question and finds cooresponding observations
    returns data, with columns for observations does not trim or cut
    send to correct_data'''
    # observations_present is a flag that will be passed on later
    # q_observation_present is a flag for discharge that will be passed later
    data_check = pd.DataFrame(Barometer_rows)

    def get_observations():
        conn_9 = SQL_String
        field_observations = pd.read_sql_query('select '+config['observation']['site_sql_id']+', '+config['observation']['observation_id']+', '+config['observation']['datetime']+', '+config['observation']
                                               ['observation_stage']+', '+config['observation']['observation_number']+' from '+config['observation']['observation_table']+' WHERE '+config['observation']['site_sql_id']+' = '+str(site_sql_id)+';', conn_9)
        field_observations.rename(columns={
            field_observations.columns[0]: "site_sql_id",
            field_observations.columns[1]: "observation_id",
            field_observations.columns[2]: "datetime",
            field_observations.columns[3]: "observation_stage",
            field_observations.columns[4]: "observation_number",
        }, inplace=True)
        if field_observations.empty:
            observation_present = False
            # if there are field observations continue with observation processing
        else:
            field_observations["datetime"] = pd.to_datetime(
                field_observations["datetime"], format='%Y-%m-%d %H:M:S', errors='ignore')
            field_observations["datetime"] = field_observations["datetime"] - \
                timedelta(hours=7)
            field_observations.reset_index(drop=True, inplace=True)
            observation_present = True
        return field_observations, observation_present

    def get_parameter_observation(data, field_observations):
        # Get Field observations Stage Only
        conn_20 = SQL_String
        parameter_observation = pd.read_sql_query('select '+config['observation']['observation_id']+', '+config['observation']['observation_type']+', '+config['observation']
                                                  ['observation_value']+' from '+config['observation']['observation_value_table']+' WHERE '+config['observation']['site_sql_id']+' = '+str(site_sql_id)+';', conn_20)
        parameter_observation.rename(columns={
            parameter_observation.columns[0]: "observation_id",
            parameter_observation.columns[1]: "observation_type",
            parameter_observation.columns[2]: "observation_value",
        }, inplace=True)
        parameter_observation = parameter_observation[parameter_observation["observation_type"] == int(config[parameter_value]["observation_type"])]
        if parameter_observation.empty:
            df = finalize_non_discharge_observations(data, field_observations)
            df["parameter_observation"] = "nan"
            q_observation_present = False
            #df = data

        else:
            parameter_observation["observation_id"] = parameter_observation["observation_id"].astype(np.int64)
            parameter_observation.rename(
                columns={"observation_value": "parameter_observation"}, inplace=True)
            parameter_observation["parameter_observation"] = parameter_observation["parameter_observation"].astype(float)
            try:
                field_observations = pd.merge_asof(field_observations, parameter_observation.sort_values(
                    "observation_id"), on=["observation_id"])
                # I think this drop is where we are going wrong
                field_observations.dropna(inplace=True)
                df = pd.merge_asof(data, field_observations.sort_values(
                    'datetime'), on=['datetime'], tolerance=pd.Timedelta('15m'))
                q_observation_present = True
            except:
                q_observation_present = True
                df = data
        return df, q_observation_present

    def finalize_non_discharge_observations(data, field_observations):
        # force reformat data from Dash Datatable
        df = pd.merge_asof(data, field_observations.sort_values(
            'datetime'), on=['datetime'], tolerance=pd.Timedelta("15m"))
        return df

    def get_q_observations(data, field_observations):

        # Get Field observations Stage Only
        conn_19 = SQL_String
        q_observation = pd.read_sql_query('select '+config['observation']['observation_id']+', '+config['observation']['observation_type']+', '+config['observation']
                                          ['observation_value']+' from '+config['observation']['observation_value_table']+' WHERE '+config['observation']['site_sql_id']+' = '+str(site_sql_id)+';', conn_19)
        q_observation.rename(columns={
            q_observation.columns[0]: "observation_id",
            q_observation.columns[1]: "observation_type",
            q_observation.columns[2]: "observation_value",
        }, inplace=True)
        q_observation = q_observation[q_observation["observation_type"] == 2]
        if q_observation.empty:
            df = finalize_non_discharge_observations(data, field_observations)
            df["q_observation"] = "nan"
            q_observation_present = False

        else:
            q_observation["observation_id"] = q_observation["observation_id"].astype(np.int64)
            q_observation.rename(columns={"observation_value": "q_observation"}, inplace=True)
            q_observation["q_observation"] = q_observation["q_observation"].astype(float)
            try:
                field_observations = pd.merge_asof(field_observations, q_observation.sort_values(
                    "observation_id"), on=["observation_id"])
                field_observations.dropna(inplace=True)
                df = pd.merge_asof(data, field_observations.sort_values(
                    'datetime'), on=['datetime'], tolerance=pd.Timedelta('15m'))
                q_observation_present = True
            except:
                q_observation_present = True
                df = data
        return df, q_observation_present

    if data_check.empty:
        observation_present = False
        q_observation_present = False
        return [{}], [], False
    else:
        data = pd.DataFrame(Barometer_rows)
        from data_cleaning import fill_timeseries
        # fill time series also corrects time stamp
        data = fill_timeseries(data)
        interval = fill_timeseries.interval
        # fill doesnt transfer to here
        field_observations, observation_present = get_observations()
        if parameter_value == "FlowLevel" or parameter_value == "discharge":
            df, q_observation_present = get_q_observations(
                data, field_observations)
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True
        if parameter_value == "water_temperature":
            df, q_observation_present = get_parameter_observation(
                data, field_observations)
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True
        else:
            # fill doesnt transfer to here
            df = finalize_non_discharge_observations(data, field_observations)
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], True

@app.callback(
    # CORRECT FIELD data to FIELD OBSERVATIONS
    Output("Corrected_Data", "data"),
    Output("Corrected_Data", "columns"),
    Output("Corrected_Data", "row_deletable"),
    Input('select_data_level', 'value'),
    Input('site', 'value'),
    Input('site_sql_id', 'children'),
    Input('Ratings', 'value'),
    Input(component_id='Parameter', component_property='value'),
    Input("Initial_Data_Correction", "data"),
    Input("Initial_Data_Correction", "columns"),
    Input("Corrected_Data", "data"),
    State("Corrected_Data", "data"),
    State("Corrected_Data", "columns"),)
def correct_data(data_level, site_value, site_sql_id, Ratings_value, Parameter_value, Initial_Data_Correction_row, Initial_Data_Correction_column, row, Corrected_Data_row, Corrected_Data_column):
    '''Takes dataframe of data and observations from function: get_observations '''
    ''' THIS KIND OF WORKS AND WHENEVER YOU TRY TO MESS WITH IT YOU SCREW IT UP SO JUST LEAVE IT ALONE'''
    ''' IT NEEDS WORK BUT DO NOT TRY ANY FANCY OBJECTS FUNCTIONS ETC'''
    #df = pd.DataFrame(Initial_Data_Correction_row)
    df = pd.DataFrame(Initial_Data_Correction_row)
    # if there is no data to look at dont show data table
    # Input(component_id='Parameter', component_property='value'),
    data_name = 'corrected_data'
    # field observaions function returns the field observation (observation_stage)
    # and parameter_observation where applicable
    # you need the stage observation to get the parameter observation
    if "parameter_observation" in df.columns:
        observation = "parameter_observation"
    else:
        observation = "observation_stage"
    # on initial open we can select data vs corrected data
    # this is a bit hacky.  We are correcting off of the data column
    # but we can change the data in the data column on initial import

    def initial_data_level(df_raw):
        if data_level == "data":
            df_raw = df_raw
        elif data_level == "corrected_data":
            try:
                df_raw["data"] = df_raw["corrected_data"]
            except:
                df_raw = df_raw
        else:
            df_raw = df_raw
        return df_raw

    # initial dataframe re-format
    def initial_df_reformat(df_raw):
        df_raw['datetime'] = pd.to_datetime(
            df_raw['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
        df_raw['date'] = df_raw['datetime'].map(
            lambda x: dt.datetime.strftime(x, '%Y%m%d%H%M%S'))
        #df_raw['date'].replace('', np.nan, inplace=True)
        #df_raw = df_raw.dropna(subset=['data'], inplace=True)
        df_raw['data'] = df_raw["data"].astype(float, errors="ignore")
        try:
            df_raw["corrected_data"] = df_raw["corrected_data"].astype(float)
        except:
            df_raw["corrected_data"] = ''
        return df_raw
    # Calculates value

    def initial_update_value(df_reformat):
        try:
            df_raw[data_name] = df_raw[data_name].astype(float)
            df_raw['offset'] = df_raw[observation]-df_raw[data_name]
            df_raw['offset'].interpolate(
                method='linear', inplace=True, axis=0, limit_direction='both')
            df_raw[data_name] = df_raw[data_name]+df_raw['offset']
            df_raw[data_name] = df_raw[data_name].round(3)
        except:
            try:
                df_raw['offset'] = df_raw[observation]-df_raw["data"]
                df_raw['offset'].interpolate(
                    method='linear', inplace=True, axis=0, limit_direction='both')
                df_raw[data_name] = df_raw['data']+df_raw['offset']
                df_raw[data_name] = df_raw[data_name].round(3)
            except:
                df_raw['offset'] = 0
        return df_reformat

    # Calculates value
    def secondary_update_value(df_raw):
        df_raw["original_corrected_data"] = df_raw["corrected_data"].astype(
            float)
        df_raw[observation] = df_raw[observation].astype(float)
        df_raw[observation] = df_raw[observation].round(3)
        #df_corrected_data = update_value(df_raw)
        #df_corrected_data = df_corrected_data[["datetime", "data", data_name, "observation_stage"]]
        df_raw['offset'] = df_raw[observation] - df_raw["original_corrected_data"]
        df_raw['offset'].interpolate(method='linear', inplace=True, axis=0, limit_direction='both')
        df_raw["new_corrected_data"] = df_raw["original_corrected_data"] + df_raw['offset']
        df_raw["original_corrected_data"] = df_raw["original_corrected_data"].round(3)
        df_corrected_data = df_raw[["datetime", "data","new_corrected_data", "observation_stage"]]
        df_corrected_data.rename(columns={"new_corrected_data": "corrected_data"}, inplace=True)
        return df_raw
    # Full discharge calculation

    def full_discharge_calculation(df_q):
        # Calculate Discharge (Q) Offset
        df = df_q
        try:
            df['q_offset'] = df['q_observation']-df['corrected_data']
            df['q_offset'].interpolate(
                method='linear', inplace=True, axis=0, limit_direction='both')
            df["q_offset_stage"] = df['corrected_data']+df['q_offset']
            df["q_offset_stage"] = df['corrected_data'].round(3)
        except:
            df['q_offset'] = 0
            df["q_offset_stage"] = df['corrected_data'].round(3)
        # Calculate Rating Offset
        conn_21 = SQL_String
        Rating_Offsets = pd.read_sql_query(
            'select Offset, Rating_Number from tblFlowRating_Stats;', conn_21)
        Rating_Offsets['Rating_Number'] = Rating_Offsets['Rating_Number'].str.rstrip()
        Rating_Offset = Rating_Offsets[Rating_Offsets['Rating_Number']
                                       == Ratings_value].iloc[0, 0]
        Rating_Offset = Rating_Offset.astype(float)
        df['WaterLevel'] = df["q_offset_stage"]-Rating_Offset
        # Calculate Discharge from Offset
        conn_24 = SQL_String
        Rating_Points = pd.read_sql_query('select G_ID, RatingNumber, WaterLevel, Discharge, Marker, FlowRatings_id from tblFlowRatings WHERE G_ID = '+str(site_sql_id)+';', conn_24)
        Rating_Points = Rating_Points[Rating_Points['RatingNumber']== Ratings_value]
        df_q_calculation = pd.merge_asof(df.sort_values('WaterLevel'), Rating_Points.sort_values(
            'WaterLevel'), on='WaterLevel', allow_exact_matches=False, direction='nearest')
        df_q_calculation = df_q_calculation.sort_values(by="datetime")
        df_q_calculation['discharge'] = df_q_calculation['Discharge']
        # Trim dataframe
        #df_q = df_q_calculation[["datetime", "data", "corrected_data", "observation_stage",
                                 #"offset", "discharge", "q_observation", "q_offset", "discharge_rating"]]
        df_q = df_q_calculation
        return df_q

    # finalize discharge dataframe
    def finalize_discharge_dataframe(df_q):
        # Trim Data Frame
        df_q_final = df_q[["datetime", "data", data_name,
                           observation, "q_observation", "discharge"]]
        # Convert Unit Types
        df_q_final['data'] = df_q_final['data'].astype(float, errors='ignore')
        df_q_final['corrected_data'] = df_q_final['corrected_data'].astype(
            float, errors='ignore')
        df_q_final['observation_stage'] = df_q_final['observation_stage'].astype(
            float, errors='ignore')
        df_q_final['q_observation'] = df_q_final['q_observation'].astype(
            float, errors='ignore')
        df_q_final['discharge'] = df_q_final['discharge'].astype(
            float, errors='ignore')
        # Round
        df_q_final['data'] = df_q_final['data'].round(2)
        df_q_final['corrected_data'] = df_q_final['corrected_data'].round(2)
        df_q_final['observation_stage'] = df_q_final['observation_stage'].round(2)
        df_q_final['q_observation'] = df_q_final['q_observation'].round(2)
        df_q_final['discharge'] = df_q_final['discharge'].round(2)
        # convert datetime
        df_q_final['datetime'] = pd.to_datetime(
            df_q_final['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
        df_q = df_q_final
        return df_q_final

    # if there is no data return a blank dataframe
    if df.empty:
        return [], [], False
        # if there is data to look at read the datatable
    else:
        if Parameter_value != 'FlowLevel':
            dff = pd.DataFrame(row)
            if dff.empty:
                df_raw = pd.DataFrame(Initial_Data_Correction_row)
                # on initial open we can select data vs corrected data
                initial_data_level(df_raw)
                initial_df_reformat(df_raw)
                try:
                    #df_raw[data_name] = df_raw[data_name].astype(float)
                    df_raw[observation] = df_raw[observation].astype(float)
                    df_raw['offset'] = df_raw[observation] - df_raw['data']
                    df_raw['offset'].interpolate( method='linear', inplace=True, axis=0, limit_direction='both')
                    df_raw[data_name] = df_raw[data_name]+df_raw['offset']
                    df_raw[data_name] = df_raw[data_name].round(3)
                    df_raw['offset'] = df_raw['offset'].round(3)
                except:
                    try:
                        df_raw['offset'] = df_raw[observation] - df_raw["data"]
                        df_raw['offset'].interpolate(method='linear', inplace=True, axis=0, limit_direction='both')
                        df_raw[data_name] = df_raw['data']+df_raw['offset']
                        df_raw[data_name] = df_raw[data_name].round(3)
                        df_raw['offset'] = df_raw['offset'].round(3)
                    except:
                        df_raw['offset'] = 0
                df_corrected_data = df_raw[[
                    "datetime", "data", data_name, observation, "offset"]]
                df_corrected_data['datetime'] = pd.to_datetime(
                    df_corrected_data['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
                return df_corrected_data.to_dict('records'), [{"name": i, "id": i} for i in df_corrected_data.columns], True

            if not dff.empty:
                df_raw = pd.DataFrame(row)
                initial_df_reformat(df_raw)
                #df_raw["corrected_data"] = df_raw["corrected_data"].astype(float)
                # not quite sure this is conversion is needed
                df_raw[observation] = df_raw[observation].astype(float)
                df_raw[observation] = df_raw[observation].round(3)
                df_raw['offset'] = df_raw[observation]-df_raw['data']
                df_raw['offset'].interpolate(method='linear', inplace=True, axis=0, limit_direction='both')
                df_raw["corrected_data"] = df_raw["data"]+df_raw['offset']
                df_raw["corrected_data"] = df_raw["corrected_data"].round(3)
                df_raw['offset'] = df_raw['offset'].round(3)
                df_raw['corrected_data'] = df_raw["corrected_data"]
                df_corrected_data = df_raw[["datetime", "data", "corrected_data", observation, "offset"]]
                #df_corrected_data.rename(columns={"new_corrected_data": "corrected_data"}, inplace=True)
                df_corrected_data['datetime'] = pd.to_datetime(
                    df_corrected_data['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
                return df_corrected_data.to_dict('records'), [{"name": i, "id": i} for i in df_corrected_data.columns], True

        # Calculate Discharge
        if Parameter_value == 'FlowLevel':
            dff = pd.DataFrame(row)
            # Discharge Initial Load from field observations
            if dff.empty:
                # Load Data
                df_raw = pd.DataFrame(Initial_Data_Correction_row)
                # on initial open we can select data vs corrected data
                initial_data_level(df_raw)
                initial_df_reformat(df_raw)
                try:
                    df_raw[data_name] = df_raw[data_name].astype(float)
                    df_raw['offset'] = df_raw['observation_stage'] - df_raw['data']
                    df_raw['offset'].interpolate(
                        method='linear', inplace=True, axis=0, limit_direction='both')
                    df_raw[data_name] = df_raw["data"]+df_raw['offset']
                    df_raw[data_name] = df_raw[data_name].round(3)
                    df_raw['offset'] = df_raw['offset'].round(3)
                except:
                    try:
                        df_raw['offset'] = df_raw['observation_stage'] - \
                            df_raw["data"]
                        df_raw['offset'].interpolate(
                            method='linear', inplace=True, axis=0, limit_direction='both')
                        df_raw[data_name] = df_raw['data']+df_raw['offset']
                        df_raw[data_name] = df_raw[data_name].round(3)
                        df_raw['offset'] = df_raw['offset'].round(3)
                    except:
                        df_raw['offset'] = ""
                # Calculate Discharge
                if not 'observation_stage' in df_raw.columns:
                    df_raw['observation_stage'] = 0
                if not 'discharge' in df_raw.columns:
                    df_raw['discharge'] = 0
                
                if Ratings_value == 'NONE':  # If there is no discharge calculate a discharge of zero
                    #df_raw["q_offset"] = ""
                    #df_raw["discharge_rating"] = ""
                    df_q = df_raw
                    #df_q = df_raw[["datetime", "data", "corrected_data", "observation_stage", "offset", "discharge", "q_observation", "q_offset", "discharge_rating"]]
                else:  # Jf it is the first run and a rating is selected calculate discharge
                    # Run full discharge calculation but only if we have a rating to use
                    df_q = df_raw
                    df_q = full_discharge_calculation(df_q)
                    finalize_discharge_dataframe(df_q)
                    #df_q = df_q[["datetime", "data", "corrected_data", "observation_stage",
                    #             "offset", "discharge", "q_observation", "q_offset", "discharge_rating"]]
                    df_q = df_raw
                return df_q.to_dict('records'), [{"name": i, "id": i} for i in df_q.columns], True

            if not dff.empty:  # Discharge update
                # REad Data
                df_raw = pd.DataFrame(row)
                initial_df_reformat(df_raw)
                df_raw['q_observation'] = df_raw['q_observation'].astype(
                    float, errors="ignore")
                df_raw['observation_stage'] = df_raw['observation_stage'].astype(
                    float, errors="ignore")
                # calculate stage
                df_raw['offset'] = df_raw['observation_stage']-df_raw['data']
                df_raw['offset'].interpolate(
                    method='linear', inplace=True, axis=0, limit_direction='both')
                df_raw["corrected_data"] = df_raw["data"]+df_raw['offset']
                df_raw["corrected_data"] = df_raw["corrected_data"].round(3)
                df_raw['offset'] = df_raw['offset'].round(3)
                df_raw['corrected_data'] = df_raw["corrected_data"]
                # Calculate Discharge
                if Ratings_value == 'NONE':  # If there is no discharge calculate a discharge of zero
                    df_raw["q_offset"] = ""
                    df_raw["discharge_rating"] = ""
                    #df_q = df_raw[["datetime", "data", "corrected_data", "observation_stage",
                                  # "offset", "discharge", "q_observation", "q_offset", "discharge_rating"]]
                    df_q = df_raw
                else:
                    #df_q = df_raw[["datetime", "data", "corrected_data", "observation_stage",
                                  # "offset", "discharge", "q_observation", "q_offset", "discharge_rating"]]
                    df_q = df_raw
                    df_q = full_discharge_calculation(df_q)
                    finalize_discharge_dataframe(df_q)
                return df_q.to_dict('records'), [{"name": i, "id": i} for i in df_q.columns], True

# Display GRAPH
@app.callback(
    Output(component_id='datatable-upload-graph', component_property='style'),
    Input('datatable-upload-container', 'data'))
def hide_Graph(rows):
    df = pd.DataFrame(rows)
    if (df.empty or len(df.columns) < 1):
        return {'display': 'none'}
    return {'display': 'block'}

@app.callback(
    Output('datatable-upload-graph', 'figure'),
    Input('Corrected_Data', 'data'),
    Input('Parameter', 'value'),
    Input('site', 'value'),
    Input('site_sql_id', 'children'),
    Input('Ratings', 'value'),)
def display_graph(rows, parameter, site, site_sql_id, rating):
    ''' should be the same as update button'''
    df_raw = pd.DataFrame(rows)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    from cache_graph import graph
    from cache_graph import save_fig
    from cache_graph import format_cache_data
    if (df_raw.empty or len(df_raw.columns) < 1):
        return dash.no_update
    else:
        df, parameter, observation, end_time = format_cache_data(df_raw, parameter)
        fig = graph(df, site, parameter, observation)
        # update fig to display on screen, catch graph has its own pre-sets
        figure_height = 550
        figure_width = 1900
        fig.update_layout(height=figure_height, width=figure_width)
        return fig

@app.callback(
    dash.dependencies.Output('upload_data_children', 'children'),
    [dash.dependencies.Input('upload_data_button', 'n_clicks')],
    Input('Corrected_Data', 'data'),
    Input('Parameter', 'value'),
    Input('site_sql_id', 'children'),
    Input('site', 'value'),)
def run_upload_data(n_clicks, rows, parameter, site_sql_id, site):
    df = pd.DataFrame(rows)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    #today = pd.to_datetime("today")

    if 'upload_data_button' in changed_id:
        if (df.empty or len(df.columns) < 1):
            return dash.no_update
        else:
            from sql_upload import full_upload

            if parameter == "water_level" or parameter == "LakeLevel":
                parameter = "water_level"
                df = df[["datetime", "data", "corrected_data"]]
            if parameter == 'groundwater_level' or parameter == "Piezometer":
                parameter = "groundwater_level"
                df = df[["datetime", "data", "corrected_data"]]
            if parameter == 'water_temperature':
                df = df[["datetime", "data", "corrected_data"]]
            if parameter == "discharge" or parameter == "FlowLevel":
                parameter = "discharge"
                df = df[["datetime", "data", "corrected_data", "discharge"]]
            full_upload(df, parameter, site_sql_id, 7)
            result = "exported"

            return result
    else:
        return dash.no_update

@app.callback(
    dash.dependencies.Output('export_data_children', 'children'),
    [dash.dependencies.Input('export_data_button', 'n_clicks')],
    Input('Corrected_Data', 'data'),
    Input('Parameter', 'value'),
    Input('site_sql_id', 'children'),
    Input('site', 'value'),)
def run_export_data(n_clicks, rows, parameter, site_sql_id, site):
    ''' uses same function as update graph, this code is becomingly increasingly redundent '''
    df_raw = pd.DataFrame(rows)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    from cache_graph import graph
    from cache_graph import save_fig
    from cache_graph import format_cache_data
    if 'export_data_button' in changed_id:
        if (df_raw.empty or len(df_raw.columns) < 1):
            return dash.no_update
        else:
            df, parameter, observation, end_time = format_cache_data(df_raw, parameter)
            df_export = df.set_index('datetime')
            df_export.to_csv("W:/STS/hydro/GAUGE/Temp/Ian's Temp/" +
                str(site)+"_"+str(parameter)+"_"+str(end_time)+".csv")
            df_export.to_csv("C:/Users/ihiggins/OneDrive - King County/cache_upload/" +
                str(site)+"_"+str(parameter)+"_"+str(end_time)+".csv")

            fig = graph(df, site, parameter, observation)
            save_fig(fig, df, site, parameter)

            result = "uploaded"
            return result
            #return result
    else:
        return dash.no_update
        print("")


# You could also return a 404 "URL not found" page here
if __name__ == '__main__':
    app.run_server(port="8050",host='127.0.0.1',debug=True)
