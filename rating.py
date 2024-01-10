import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
from scipy import stats, interpolate
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d, UnivariateSpline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
import configparser
import pyodbc
import configparser
import pyodbc
import configparser
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import configparser
import sys
import os
from datetime import datetime
from datetime import timedelta
import urllib

config = configparser.ConfigParser()
config.read('gdata_config.ini')

host_name = "KCITSQLPRNRPX01"
db_name = "gData"
server = "KCITSQLPRNRPX01"
#10.82.12.39
driver = "SQL Server"
database = "gData"


comparison_sites = configparser.ConfigParser()
comparison_sites.read('gdata_config.ini')

#Driver = config['sql_connection']['Driver']
#Server = config['sql_connection']['Server']
#Database = config['sql_connection']['Database']
#Trusted_Connection = config['sql_connection']['Trusted_Connection']
SQL_String = pyodbc.connect('Driver={'+config['sql_connection']['Driver']+'};'
                            'Server='+config['sql_connection']['Server']+';'
                            'Database=' +
                            config['sql_connection']['Database']+';'
                            'Trusted_Connection='+config['sql_connection']['Trusted_Connection']+';')
### for gdata ratinf creating
def rating_calculator(Ratings_value, site_sql_id):
            
            # get rating points 
            conn_9 = SQL_String
            rating_points = pd.read_sql_query(f"SELECT WaterLevel as water_level_rating, CAST(Discharge AS float) as discharge_rating, RatingNumber "
                                            f"FROM tblFlowRatings "
                                            f"WHERE G_ID = '{str(site_sql_id)}' "
                                            f"AND RatingNumber = '{Ratings_value}' ;", conn_9)
            conn_9.close
            rating_points = rating_points.dropna()
            rating_points.sort_values(by=['water_level_rating'], inplace = True)
            interpolate_discharge = interpolate.interp1d(((rating_points['water_level_rating']).to_numpy()), rating_points['discharge_rating'].to_numpy(), bounds_error = False)
            interpolate_stage = interpolate.interp1d(rating_points['discharge_rating'].to_numpy(), ((rating_points['water_level_rating']).to_numpy()), bounds_error = False)
            # Calculate Rating Offset

            conn_10 = SQL_String
            gzf = pd.read_sql_query(f"SELECT Offset as gzf "
                                            f"FROM tblFlowRating_Stats "
                                            f"WHERE Rating_Number = '{Ratings_value}';", conn_10)
            conn_10.close
            

            gzf = gzf.iloc[0, 0].astype(float)
            rating_calculation_status = Ratings_value
            print("RATING CALCULATED")
            return rating_calculation_status, interpolate_discharge, interpolate_stage, gzf

def rating_points_from_rating(site, rating_value):
    sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection=yes;')
    sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)
    conn = sql_engine.raw_connection()

    sql = f"select SITE_CODE as site_number, G_ID as site_sql_id from {config['parameters']['parameter_table']} WHERE STATUS = 'Active' AND FlowLevel = 'True'"
    site_list = pd.read_sql_query(sql, conn)
    conn.close()
    conn = sql_engine.raw_connection()
    site_sql_id = site_list.loc[site_list['site_number'] == site, 'site_sql_id'].item()
    rating_points = pd.read_sql_query(f"SELECT WaterLevel as water_level_rating, CAST(Discharge AS float) as discharge_rating, RatingNumber "
                                          f"FROM tblFlowRatings "
                                          f"WHERE G_ID = '{str(site_sql_id)}' "
                                          f"AND RatingNumber = '{rating_value}' ;", conn)
    conn.close()
                # get rating offset
    if rating_value != 0:
        conn = sql_engine.raw_connection()
        rating_offsets = pd.read_sql_query(f"select Rating_Number from tblFlowRating_Stats WHERE Rating_Number = '{rating_value}' GROUP BY Rating_Number ORDER BY Rating_Number DESC;", conn)
                    #rating_offsets = rating_offsets['RatingNumber'].values.tolist()
        try:
            rating_offsets = rating_offsets.iloc[0, 0].astype(float)
        except:
            rating_offsets = 0 
            conn.close
    else:
            rating_offsets = 0
            rating_points = rating_points.sort_values(by=['water_level_rating'])
                #fig.add_trace(
                    #go.Scatter(
                    #    y=rating_points['water_level_rating'],
                    #    x=rating_points['discharge_rating'],
                    #    line=dict(color='grey', width=subplot_2_line_width),
                    #    name=f"{i}:{rating_offsets}", showlegend=False), row=1, col=1, secondary_y=False,)
    return rating_points, rating_offsets