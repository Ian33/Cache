# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 14:29:39 2021

@author: IHiggins
"""
from datetime import date
import base64
import pyodbc
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from datetime import timedelta
import dash_datetimepicker

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

Driver = 'SQL Server'
Server = 'NRDOSQLPrX01'
Database = 'gData'
Trusted_Connection = 'yes'
SQL_String = pyodbc.connect('Driver={'+Driver+'};'
                      'Server='+Server+';'
                      'Database='+Database+';'
                      'Trusted_Connection='+Trusted_Connection+';')

Discharge_Table = 'tblDIschargeGauging'
Discharge_Table_Raw = 'D_Value'
Discharge_DateTime = 'D_TimeDate'
# Get site list
# Query SQL every sql query will need its own CONN
conn_1 = SQL_String
Available_Sites = pd.read_sql_query('select SITE_CODE, G_ID, FLOWLEVEL, STATUS from tblGaugeLLID;',conn_1)
Available_Sites = Available_Sites[Available_Sites['STATUS']=='Active']
# this will need to change when there is more then just flowlevel
Available_Sites = Available_Sites[Available_Sites['FLOWLEVEL']== True]
Available_Sites.sort_values('SITE_CODE', inplace=True)
vlist = Available_Sites['SITE_CODE'].values.tolist()

app.layout = html.Div([
    dcc.Dropdown(
                id='Site',
                options=[{'label': i, 'value': i} for i in vlist],
                value='0'),
    
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
    # we are assuming a time in PDT
    dash_datetimepicker.DashDatetimepicker(id='selectrange', startDate='', endDate=''),
    
    #dcc.DatePickerRange(
    #    id='my-date-picker-range',
    #    #min_date_allowed=date(1995, 8, 5),
    #    #max_date_allowed=date(2017, 9, 19),
    #    initial_visible_month=date(2020, 8, 5),
    #    end_date=date(2021, 8, 25)
    #),
    #
    html.Div(id='output-container-date-picker-range'),
    dcc.Graph(id='datatable-upload-graph'),
    dash_table.DataTable(id='datatable-upload-container',editable=True)
    
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')),usecols=[0,1])
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded),usecols=[0,1])

# Pick Range, query existing data in SQL Database
@app.callback(
    #Output('output-container-date-picker-range', 'children'),
    Output('datatable-upload-container', 'data'),
    Output('datatable-upload-container', 'columns'),
    Input('selectrange', 'startDate'),
    Input('selectrange', 'endDate'),
    Input(component_id='Site', component_property='value'),
    Input('datatable-upload', 'contents'),
    State('datatable-upload', 'filename'))
def update_daterange(startDate, endDate, value, contents, filename):
    if contents is None:
        if startDate != '' and endDate != '':
            # take assumed PDT and convert to UTC (7 hours)
            startDate = pd.to_datetime(startDate) + timedelta(hours=7)
            endDate = pd.to_datetime(endDate) + timedelta(hours=7)
            startDate = startDate.strftime("%Y/%m/%d %H:%M:%S")
            endDate = endDate.strftime("%Y/%m/%d %H:%M:%S")
            
            # Get SQL Site Number From Site Name 31q Site Name =233 SQL Number
            search = Available_Sites.loc[Available_Sites['SITE_CODE'].isin([value])]
            G_ID_Lookup = search.iloc[0,1]
            # NEW CONN STRING
            conn_2 = SQL_String
            #QUERY Discharge
            df = pd.read_sql_query('select '+Discharge_DateTime+','+Discharge_Table_Raw+' from '+Discharge_Table+' WHERE G_ID = '+str(G_ID_Lookup)+' AND '+Discharge_DateTime+' between ? and ?',conn_2, params=[str(startDate), str(endDate)])
            # convert to date time and take out of utc
            df[Discharge_DateTime] = pd.to_datetime(df[Discharge_DateTime]) - timedelta(hours=7)
            # sort
            df.sort_values(by=Discharge_DateTime, inplace=True)
            return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]           
    if contents is not None:
        df = parse_contents(contents, filename)
        return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]\
    # return blank for a variety of situations
    if contents is None and startDate == '' and endDate == '':
        return [{}], []
    if contents is None and startDate != '' and endDate == '':
        return [{}], []
    if contents is None and startDate == '' and endDate != '':
        return [{}], []
    

@app.callback(Output('datatable-upload-graph', 'figure'),
              Input('datatable-upload-container', 'data'))
def display_graph(rows):
    df = pd.DataFrame(rows)

    if (df.empty or len(df.columns) < 1):
        return {
            'data': [{
                'x': [],
                'y': [],
                'type': 'line'
            }]
        }
    return {
        'data': [{
            'x': df[df.columns[0]],
            'y': df[df.columns[1]],
            'type': 'line'
        }]
    }


if __name__ == '__main__':
    app.run_server(debug=True)