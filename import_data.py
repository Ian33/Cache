import base64
import datetime as dt
from datetime import timedelta
from datetime import datetime
import io
import pyodbc
import configparser
import pickle 
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
from sqlalchemy import create_engine
import urllib

config = configparser.ConfigParser()
config.read('gdata_config.ini')

SQL_String = pyodbc.connect('Driver={'+config['sql_connection']['Driver']+'};'
                            'Server='+config['sql_connection']['Server']+';'
                            'Database=' +
                            config['sql_connection']['Database']+';'
                            'Trusted_Connection='+config['sql_connection']['Trusted_Connection']+';')

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

def sql_import(parameter, site_sql_id, start_date, end_date):
    if start_date != '' and end_date != '':
            start_date = pd.to_datetime(start_date).to_pydatetime()
            start_date = (start_date + timedelta(hours=(7))).strftime("%m/%d/%Y %H:%M")
            end_date = pd.to_datetime(end_date).to_pydatetime()
            end_date = (end_date + timedelta(hours=(7))).strftime("%m/%d/%Y %H:%M")
            if parameter == "FlowLevel" or parameter == "discharge":
              
                # QUERY Discharge
                select_statement = f"SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config[parameter]['datetime']}, 120)) as datetime, {config[parameter]['data']} as data, {config[parameter]['corrected_data']} as corrected_data, {config[parameter]['discharge']} as discharge, {config[parameter]['est']} as estimate "
            elif parameter == "barometer":
                # barometer (only has "data column")
                select_statement = f"SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config[parameter]['datetime']}, 120)) as datetime, {config[parameter]['corrected_data']} as corrected_data, {config[parameter]['est']} as estimate "
            
            else:
            
                select_statement = f"SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config[parameter]['datetime']}, 120)) as datetime, {config[parameter]['data']} as data, {config[parameter]['corrected_data']} as corrected_data, {config[parameter]['est']} as estimate  "
                
                # NEW CONN STRING
            with sql_engine.begin() as conn:
               
                df = pd.read_sql_query(f"{select_statement}"
                                    f"FROM {config[parameter]['table']} "
                                    F"WHERE G_ID = {str(site_sql_id)} "
                                    f"AND {config[parameter]['datetime']} BETWEEN ? and ? "
                                    f"ORDER BY {config[parameter]['datetime']} DESC", conn, params=[str(start_date), str(end_date)])
            # THIS ISNT THE COPY OF A Slice, datetime converted in sql statement
            #df["datetime"] = df["datetime"] - timedelta(hours=7)
                
    
    else:
            df = pd.DataFrame()
            
    return df

def sql_import_all_datetimes(parameter, site_sql_id):
        if parameter == "FlowLevel" or parameter == "discharge":
                # QUERY Discharge
                select_statement = f"SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config[parameter]['datetime']}, 120)) as datetime, {config[parameter]['data']} as data, {config[parameter]['corrected_data']} as corrected_data, {config[parameter]['discharge']} as discharge, {config[parameter]['est']} as estimate "
        elif parameter == "barometer":
                # barometer (only has "data column")
                select_statement = f"SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config[parameter]['datetime']}, 120)) as datetime, {config[parameter]['corrected_data']} as corrected_data, {config[parameter]['est']} as estimate "
            
        else:
            
                select_statement = f"SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config[parameter]['datetime']}, 120)) as datetime, {config[parameter]['data']} as data, {config[parameter]['corrected_data']} as corrected_data, {config[parameter]['est']} as estimate  "
                
                # NEW CONN STRING
        with sql_engine.begin() as conn:
            
                df = pd.read_sql_query(f"{select_statement}"
                                    f"FROM {config[parameter]['table']} "
                                    F"WHERE G_ID = {str(site_sql_id)} "
                                    f"ORDER BY {config[parameter]['datetime']} DESC", conn)
            # THIS ISNT THE COPY OF A Slice, datetime converted in sql statement
            #df["datetime"] = df["datetime"] - timedelta(hours=7)
        #else:
        #    df = pd.DataFrame()
            
        return df


def get_observations_join(parameter, site_sql_id, startDate, endDate):
        added_time_window = 12 # you want to pull in observations from before and after the start of the record as the observation could be taken 1 minute before start of record
        # convert to datetime
        #startDate = pd.to_datetime(startDate)
        #endDate = pd.to_datetime(endDate)

        # convert start/end date to utc time
        #startDate = startDate + timedelta(hours=(7))
        #endDate = endDate + timedelta(hours=(7))

        # add data window
        #startDate = startDate - timedelta(hours=(added_time_window))
        #endDate = endDate + timedelta(hours=(added_time_window))

        # convert to string
        #startDate = startDate.strftime("%m/%d/%Y %H:%M")
        #endDate = endDate.strftime("%m/%d/%Y %H:%M")
        if parameter == "water_level" or parameter == "LakeLevel" or parameter == "groundwater_level" or parameter == "piezometer" or parameter == "Piezometer": # no parameter value to join with
              with sql_engine.begin() as conn: 
                     #observations = pd.read_sql_query(f"""   SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config['observation']['datetime']}, 120)) as datetime, {config['observation']['observation_stage']} as observation_stage, Comments as comments
                     #                               FROM tblFieldVisitInfo 
                     #                               WHERE tblFieldVisitInfo.G_ID = {site_sql_id} AND tblFieldVisitInfo.Date_Time BETWEEN ? AND ?;""", conn, params=[str(startDate), str(endDate)])   
                     observations = pd.read_sql_query(f"""   SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config['observation']['datetime']}, 120)) as datetime, {config['observation']['observation_stage']} as observation_stage, Comments as comments
                                                    FROM tblFieldVisitInfo 
                                                    WHERE tblFieldVisitInfo.G_ID = {site_sql_id};""", conn)    
        else:
                with sql_engine.begin() as conn:                                      
                #observations = pd.read_sql_query(f"""  SELECT Measurement_Number,                                                  Date_Time AS date,                                                                         Stage_Feet,                                                         tblFieldData.Parameter_Value, Comments FROM tblFieldVisitInfo INNER JOIN tblFieldData ON (tblFieldVisitInfo.FieldVisit_ID = tblFieldData.FieldVisit_ID) WHERE tblFieldVisitInfo.G_ID = {site_sql_id} AND tblFieldVisitInfo.Date_Time BETWEEN ? AND ? AND tblFieldData.Parameter = 2;""", conn, params=[str(startDate), str(endDate)])
                #observations = pd.read_sql_query(f"""   SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config['observation']['datetime']}, 120)) as datetime, {config['observation']['observation_number']} as observation_number, {config['observation']['observation_stage']} as observation_stage, tblFieldData.Parameter_Value as parameter_observation, Comments as comments
                #                                        FROM tblFieldVisitInfo INNER JOIN tblFieldData ON (tblFieldVisitInfo.FieldVisit_ID = tblFieldData.FieldVisit_ID) 
                #                                        WHERE tblFieldVisitInfo.G_ID = {site_sql_id} AND tblFieldVisitInfo.Date_Time BETWEEN ? AND ? AND tblFieldData.Parameter = {config[parameter_value]['observation_type']};""", conn, params=[str(startDate), str(endDate)])
                        observations = pd.read_sql_query(f"""   SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config['observation']['datetime']}, 120)) as datetime, {config['observation']['observation_number']} as observation_number, {config['observation']['observation_stage']} as observation_stage, tblFieldData.Parameter_Value as parameter_observation, Comments as comments
                                                        FROM tblFieldVisitInfo INNER JOIN tblFieldData ON (tblFieldVisitInfo.FieldVisit_ID = tblFieldData.FieldVisit_ID) 
                                                        WHERE tblFieldVisitInfo.G_ID = {site_sql_id} AND tblFieldData.Parameter = {config[parameter]['observation_type']};""", conn)
                if observations.empty: # if there are no parameter observations ie a waterlevel site
                        with sql_engine.begin() as conn: 
                        #observations = pd.read_sql_query(f"""   SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config['observation']['datetime']}, 120)) as datetime, {config['observation']['observation_stage']} as observation_stage, Comments as comments
                        #                               FROM tblFieldVisitInfo 
                        #                               WHERE tblFieldVisitInfo.G_ID = {site_sql_id} AND tblFieldVisitInfo.Date_Time BETWEEN ? AND ?;""", conn, params=[str(startDate), str(endDate)])   
                                observations = pd.read_sql_query(f"""   SELECT DATEADD(HOUR, -7, CONVERT(DATETIME, {config['observation']['datetime']}, 120)) as datetime, {config['observation']['observation_stage']} as observation_stage, Comments as comments
                                                        FROM tblFieldVisitInfo 
                                                        WHERE tblFieldVisitInfo.G_ID = {site_sql_id};""", conn)    
        return observations
