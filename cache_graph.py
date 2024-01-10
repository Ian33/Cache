# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 17:12:50 2022

@author: IHiggins
"""
import base64
import datetime as dt
from datetime import timedelta
from datetime import datetime
import io
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
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import find_peaks, find_peaks_cwt
import urllib
# add a note ####
# added a second note #
# a forth comment
from scipy import stats, interpolate
from sklearn.linear_model import LinearRegression
from scipy.interpolate import interp1d, UnivariateSpline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
# added a third note possibly in a branch?
import dash
from dash.dependencies import Input, Output, State
#import dash_core_components as dcc
from dash import dcc
from dash import html
#import dash_html_components as html
#import dash_table
from dash import dash_table
import pandas as pd

import dash_datetimepicker
import dash_daq as daq
import plotly.io as pio
pio.kaleido.scope.default_format = "svg"
import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots

### Set a bunch of parameters
# this is for the save figure
paper_width = 800
paper_height = 500
# measurements for figure
horizontal_spacing_plots = 0.75
vertical_spacing_plots = 0.005
# figure font size
font_size = 10
font_type = "Arial"
# fig height of 400 was originally used
figure_height = 800
# figure width of 600 was originally used
figure_width = 600
legend_y_anchor = "top"
legend_x_anchor = "right"
# legend position y = 1 x=0.94 is top right of graph
legend_y_position = -.08 # higer number moves up
legend_x_position = .5 # lower number moves left: "1" seems over justified on the right
# legend viability
show_legend = True
# legend font size
legend_font_size = 4
subplot_1_line_width = 1
subplot_1_line_color = "grey"
subplot_2_line_width = 1
subplot_2_line_color = "blue"
existing_data_line_color = "lightblue"
existing_data_line_width = 1


fig_margin_left = 1
fig_margin_right = 1
fig_margin_top = 40
fig_margin_bottom = 60
x_axis_line_width = .25
y_axis_line_width = .25
# observation header
text_first_observation_x = 0.0
text_first_observation_y = -0.12 # higher number moves up, base (0) is bottom inside of graph line
text_last_observation_x = .85 # justified to left, 0.5 is halfway across paper
text_last_observation_y = text_first_observation_y # higher number moves up, base (0) is bottom inside of graph line
# measuremnent
text_first_measurement_x = text_first_observation_x
text_first_measurement_y = text_first_observation_y -.035
text_last_measurement_x = text_last_observation_x
text_last_measurement_y = text_first_measurement_y
# instrument
text_first_instrument_x = text_first_observation_x
text_first_instrument_y = text_first_observation_y -.07
text_last_instrument_x = text_last_observation_x
text_last_instrument_y = text_first_instrument_y
# offset
text_first_offset_x = text_first_observation_x
text_first_offset_y = text_first_observation_y -.11
text_last_offset_x = text_last_observation_x
text_last_offset_y = text_first_offset_y

# statistics test
# color schemes
# https://plotly.com/python/discrete-color/
statistics_text_size = 6
statistics_opaq = .9
missing_data_size = 6
missing_data_color = "rgb(136, 136, 136)" # grey
missing_data_line_width = 1
estimate_color = "rgb(249, 123, 1144)"
estimate_size = 6
peaks_color = 'rgb(235, 180, 98)'
peaks_size = 6

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# a new comment
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Driver = 'SQL Server'
#Server = 'KCITSQLPRNRPX01'
#Database = 'gData'
#Trusted_Connection = 'yes'

config = configparser.ConfigParser()
config.read('gdata_config.ini')


def reformat(df):
    # reformat
    #df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
   
    from data_cleaning import reformat_data
    df = reformat_data(df)
    return df

#df['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))

def titles(df, site, parameter):
    #date_time_string_df = df['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))
    start_time_minutes = df.head(1).iloc[0, df.columns.get_loc("datetime")]
    # get end time
    end_time_minutes = df.tail(1).iloc[0, df.columns.get_loc("datetime")]
    if "RatingNumber" in df.columns:
        rating = str(df["RatingNumber"].iloc[4])
        rating = f" (rating: {rating})"
    else:
        rating = ""
    graph_title_a = "{0} {1} {2} {3} {4}".format(site, parameter, start_time_minutes, end_time_minutes, rating)
    table_title_a = "observations"
    return graph_title_a, table_title_a


def subplots(graph_title_a, table_title_a):
    today = pd.to_datetime('today')
    #return make_subplots(rows=2, cols=1, subplot_titles=(
    #    f"created: {today}"),
    return make_subplots(rows=3, cols=1,
        #specs=[[{"type": "xy", "secondary_y": True, "rowspan": 2}, {"type": "Table"}], [{}, {"type": "Table"}]],
            specs=[[{"type": "xy", "secondary_y": True}], [{"type": "xy", "secondary_y": True}], [{"type": "xy", "secondary_y": True}]],
            column_widths=[1],
            row_heights=[1, .2, .2],
            horizontal_spacing=horizontal_spacing_plots,
            vertical_spacing=vertical_spacing_plots)

# raw data
def subplot_1(df, fig):
    # if graphing discharge all water level/stage is on primary y
    # otherwise uncorrected wl is on secondary y
    if 'discharge' in df.columns:
        return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['data'],
                    line=dict(color=subplot_1_line_color, width=subplot_1_line_width),
                    name=str("raw data")
                    ),
            row=1, col=1, secondary_y=False,)
    else:
        return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['data'],
                    line=dict(color=subplot_1_line_color, width=subplot_1_line_width),
                    name=str("raw data")
                    ),
            row=1, col=1, secondary_y=True,)

# corrected data
def subplot_2(df, fig):
    return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['corrected_data'],
                    line=dict(color=subplot_2_line_color, width=subplot_2_line_width),
                    name=str("corrected_data"),),
                row=1, col=1, secondary_y=False,)

# show existing data
def existing_data(df, fig):
    return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['existing_data'],
                    line=dict(color=existing_data_line_color, width=existing_data_line_width),
                    name=str("existing_data"),),
                row=1, col=1, secondary_y=False,)

           
# these create the actual statistics supblots which are later modified with points
def subplot_3(df, fig):
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['corrected_data'],
            line=dict(color=subplot_2_line_color, width=0),
            name=str("corrected_data"),
            showlegend=False
            ),
        row=2, col=1, secondary_y=False)
# if you dont use 'corrected data' for the discharge line the data points will be off scuew
def subplot_4(df, fig):
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['corrected_data'],
            line=dict(color=subplot_2_line_color, width=0),
            name=str("discharge"),
            showlegend=False
            ),
        row=3, col=1, secondary_y=False)


# special discharge column, should really be a parameter column but alas
def subplot_discharge(df, fig):
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['discharge'],
            line=dict(color="red", width=subplot_2_line_width),
            name=str("discharge"),
            ),
        row=1, col=1, secondary_y=True,)

# observation sub plots
def subplot_observation(df, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['observation'],
            mode='markers',
            marker=dict(
                color='Black', size=6, opacity=.9),
            text='', name='observations', showlegend=False), row=1, col=1, secondary_y=False,)

def subplot_observation_stage(df, observation, fig):
    
    return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['observation_stage'],
                    mode='markers',
                    marker=dict(
                        color='Black', size=6, opacity=.9),
                    text='', name='observation_stage', showlegend=False), row=1, col=1, secondary_y=False,),

def subplot_observation_stage_statistics(df, observation, fig):
    # graph stage observation on main plot
    # graph observation stage on row 2
    # graph stage offset on row 2
    df_stats = df.copy()
    df_stats["y_position"] = df_stats['corrected_data'].mean()
    #stage_offset = df_stats.dropna(subset=['corrected_data']).copy()

    stage_offset = df_stats[['datetime', 'corrected_data', 'observation_stage', 'offset', 'y_position']].copy()
    
    df_missing = df_stats.loc[df['data'].isnull()]
    
    #peaks_df = df_stats['corrected_data']
    #peaks_stdev = df_stats['corrected_data'].std()
    
    #peaks = find_peaks(peaks_df)
    #peaks_prom, properties = find_peaks(stage_offset['corrected_data'], prominence=(peaks_stdev, None))

    #peaks_cwt = find_peaks_cwt(peaks_df)
    
    #tulupe = pd.DataFrame(properties)
    #tulupe_rb = pd.DataFrame(properties)
    #tulupe_rb = tulupe.drop_duplicates(['right_bases'])
    
    # drop "right base" from tulupe with lb as index
    #if "right_bases" in tulupe.columns:
    #    tulupe = tulupe.drop(columns=["right_bases"])
    #tulupe = tulupe.set_index(['left_bases'])
    # drop "left base" from tulupe with rb as index
    #if "left_bases" in tulupe_rb.columns:
    #    tulupe_rb = tulupe_rb.drop(columns=["left_bases"])
    #tulupe_rb = tulupe_rb.set_index(['right_bases'])
    
    #merged_df = df_stats.merge(tulupe, left_index=True, right_index="left_bases")
    #peaks_df = stage_offset.merge(tulupe_rb, left_index=True, right_index=True, how = "left").copy()
    #print("peaks")
    #print(peaks)
    #peaks_df = peaks_df.dropna(subset=['prominences'])
    #try:
    #    peaks_df = stage_offset.loc[stage_offset.corrected_data == [peaks]]
    #    print(peaks_df)
    #except:
    #    peaks_df = []
    stage_offset = stage_offset.dropna(subset=['observation_stage']).copy()
   # merged_df = peaks_df.merge(pd.DataFrame({'value_arr': arr}), left_index=True, right_index=True)

    #x = df['observation_stage']
    #peaks, _ = find_peaks(x)
    
    #df_stats.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/peaks.csv")
    #peaks.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/peaks.csv")
    # things rendered first will be under later things
    # so render missing data first
    return [fig.add_trace(
                go.Scatter(
                    x=df_missing['datetime'],
                    y=df_missing["y_position"],
                    mode="markers",
                    marker=dict(color=missing_data_color, size=missing_data_size, opacity=statistics_opaq),
                    showlegend=False), row=2, col=1, secondary_y=True),
            
        
            fig.add_trace(
                go.Scatter(
                    x=stage_offset['datetime'],
                    y=stage_offset["y_position"],
                    mode="markers+text",
                    marker=dict(color=subplot_2_line_color, size=statistics_text_size, opacity=statistics_opaq),
                    #mode="text",
                    text=stage_offset['observation_stage'], textposition="top center", name='observation_stage', showlegend=False), row=2, col=1, secondary_y=True),
                    
            fig.add_trace(
                go.Scatter(
                    x=stage_offset['datetime'],
                    y=stage_offset["y_position"],
                    mode="markers+text",
                    marker=dict(color=subplot_2_line_color, size=statistics_text_size, opacity=statistics_opaq),
                    #mode="text",
                    text=stage_offset['offset'], textposition="bottom center", name='observation_stage', showlegend=False), row=2, col=1, secondary_y=True),
            # peaks
            #fig.add_trace(
            #    go.Scatter(
            #        x=peaks_df['datetime'],
            #        y=peaks_df["y_position"],
            #        mode="markers+text",
            #        marker=dict(color=subplot_2_line_color, size=statistics_text_size, opacity=statistics_opaq),
            #        #mode="text",
            #        text=peaks_df['corrected_data'], textposition="bottom center", name='peak', showlegend=False), row=2, col=1, secondary_y=True), 
   
                    
    ]



def subplot_estimate(df, fig):
    df_estimate = df[df.estimate != 0]
    return fig.add_trace(
                go.Scatter(
                    x=df_estimate['datetime'],
                    y=df_estimate['corrected_data'],
                    mode='markers',
                    marker=dict(
                        color='red', size=1, opacity=.9),
                    name=str("estimate"), showlegend=False),
                row=1, col=1, secondary_y=False,)

def subplot_parameter_observation(df, observation, fig):
    
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['parameter_observation'],
            mode='markers',
            marker=dict(
                color='Black', size=6, opacity=.9),
            text='', name='parameter_observation', showlegend=False), row=1, col=1, secondary_y=False,)

def comparison_plot(df, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['comparison'],
            line=dict(color='rgb(152,78,163)', width=subplot_2_line_width),
            name=str("comparison"),
            ),
        row=1, col=1, secondary_y=True,)
        # true plots on data
        # false plots on corrected data

def subplot_q_observation(df, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['q_observation'],
            mode='markers',
            marker=dict(
                color='grey', size=6, opacity=.9),
            text='', name='q_observation', showlegend=False), row=1, col=1, secondary_y=True,)


# for statis subplot
# parameter statistics row 2


#def subplot_q_precent(df, fig):
#    q_offset = df.dropna(subset=['q_observation'])
#    q_offset = q_offset[['datetime', 'precent_q_change']]
#    q_offset["y_position"] = df['corrected_data'].mean()
#    return fig.add_trace(
#        go.Scatter(
#            x=q_offset['datetime'],
#            y=q_offset["y_position"],
#            mode="markers+text",
#            #marker=dict(
#            #    color='grey', size=6, opacity=.9),
#            text=q_offset['precent_q_change'], textposition="bottom center", name='q_precent', showlegend=False), row=3, col=1, secondary_y=True)

# discharge Statistics row 3
def subplot_q_offset(df, fig):
    q_offset = df.dropna(subset=['q_observation'])
    q_offset = q_offset[['datetime', 'q_offset']]
    q_offset["y_position"] = df['corrected_data'].mean()
    return fig.add_trace(
        go.Scatter(
            x=q_offset['datetime'],
            y=q_offset["y_position"],
            mode="markers+text",
            #marker=dict(
            #    color='grey', size=6, opacity=.9),
            text=q_offset['q_offset'], textposition="top center", name='q_offset', showlegend=False), row=3, col=1, secondary_y=True)

def subplot_q_precent(df, fig):
    q_offset = df.dropna(subset=['q_observation'])
    q_offset = q_offset[['datetime', 'precent_q_change', 'precent_q_change']]
    q_offset["y_position"] = df['corrected_data'].mean()
    return fig.add_trace(
        go.Scatter(
            x=q_offset['datetime'],
            y=q_offset["y_position"],
            mode="markers+text",
            #marker=dict(
            #    color='grey', size=6, opacity=.9),
            text=q_offset['precent_q_change'], textposition="bottom center", name='q_precent', showlegend=False), row=3, col=1, secondary_y=True)

        


def save_fig(fig, df, site, parameter):
    #scale = 1
    fig.update_layout(height=paper_height, width=paper_width)
    #fig.set_size_inches(11.69,8.27)
    end_date = df.tail(1).iloc[0, df.columns.get_loc("datetime")].date().strftime("%Y_%m_%d")
    #scale=1, width=1000, height=800
    # save as pdf
    #fig.update_layout(font_family="Serif", font_size=12)
    fig.write_image(file=r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site, parameter, end_date), format='pdf', engine="kaleido")
    # save as html
    #fig.write_html(r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\t {0}_{1}_{2}.html".format(site, parameter, end_date))

# run program
def graph(df, site, parameter, observation):
    # need to set graph here
    
    # this is probably redundent as cache should do this
    if (df.empty or len(df.columns) < 1):
        #return {'data': [{'x': [], 'y': [], 'type': 'line'}]}
        print("no_data")
    else:
        reformat(df)
        #df['datetime_string'] = df['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))

        
        graph_title_a, table_title_a = titles(df, site, parameter)
        # make graph
        fig = subplots(graph_title_a, table_title_a)
        subplot_1(df, fig)
        # corrected data
        subplot_2(df, fig)
        subplot_3(df, fig)
        if 'discharge' in df.columns:
            subplot_4(df, fig)
        if 'existing_data' in df.columns:
            existing_data(df, fig)
        # discharge column
        if 'discharge' in df.columns:
            subplot_discharge(df, fig)
            #fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
            fig.update_yaxes(title_text="discharge (cfs)", secondary_y=True)
            parameter = "water_level"
        
        # observation subplots
        if 'observation' in df.columns:
            subplot_observation(df, observation, fig)
        if 'observation_stage' in df.columns:
            subplot_observation_stage(df, observation, fig)
            subplot_observation_stage_statistics(df, observation, fig)
        if 'parameter_observation' in df.columns:
            subplot_parameter_observation(df, observation, fig)
        if 'q_observation' in df.columns:
            subplot_q_observation(df, observation, fig)
        if 'q_offset' in df.columns:
            subplot_q_offset(df, fig)
        if 'precent_q_change' in df.columns:
            subplot_q_precent(df, fig)
        if 'comparison' in df.columns:
            comparison_plot(df, observation, fig)
        if 'estimate' in df.columns:
            subplot_estimate(df, fig)
        
        

        # update figure
        fig.update_layout(height=figure_height, width=figure_width, title_text=graph_title_a)
        #fig.update_layout(title_text=graph_title_a)
        # add labels
        if parameter == "discharge" or parameter == "FlowLevel":
            fig.update_layout(yaxis_title=f"stage (feet)")
           
        else:
            fig.update_layout(yaxis_title=f"{parameter}")
           
        # ANNOTATE
        fig.update_layout(legend=dict(
            yanchor=legend_y_anchor,
            y=legend_y_position,
            xanchor=legend_x_anchor,
            x=legend_x_position,  # lower number is farther right
            orientation="h"
                 
        ))

     
        fig.update_layout(legend_font_size=legend_font_size)

        fig.update_xaxes(showline=True, linewidth=x_axis_line_width, linecolor='black', mirror=True, row=1, col=1)
        fig.update_xaxes(showline=False, linewidth=x_axis_line_width, linecolor='black', mirror=False, row=2, col=1)
        fig.update_xaxes(showline=True, linewidth=x_axis_line_width, linecolor='black', mirror=False, row=3, col=1)

        fig.update_yaxes(showline=True, linewidth=y_axis_line_width, linecolor='black', mirror=True, row=1, col=1)
        fig.update_yaxes(title_text="obs (offset)", showline=False, linewidth=y_axis_line_width, linecolor='black', mirror=False, row=2, col=1)
        fig.update_yaxes(title_text="Δq (Δ%)", showline=False, linewidth=y_axis_line_width, linecolor='black', mirror=False, row=3, col=1)

   


        fig.update_layout(font=dict(family = font_type, size = font_size,color="black"))

        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showticklabels=True, row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(showticklabels=False, row=3, col=1)

        fig.update_yaxes(showticklabels=True, row=1, col=1)
        fig.update_yaxes(showticklabels=False, row=2, col=1)
        fig.update_yaxes(showticklabels=False, row=3, col=1)
        fig.update_layout(
            margin=dict(l=fig_margin_left, r=fig_margin_right, t=fig_margin_top, b=fig_margin_bottom))
        return fig

def format_cache_data(df_raw, parameter):
    '''takes a raw df from cache, and does some pre-processing and adds settings'''
    '''returns df to cache, which sends df back to this program'''
    '''as this program is used in multiple parts of cache and is still in dev,
        this is a good workaround from having to copy and paste the dev code'''
    end_time = df_raw.tail(1)
    end_time['datetime'] = pd.to_datetime(
    end_time['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    end_time['datetime'] = end_time['datetime'].map(
        lambda x: dt.datetime.strftime(x, '%Y_%m_%d'))
    end_time = end_time.iloc[0, 0]

    df_raw['datetime'] = pd.to_datetime(
        df_raw['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    df_raw['datetime'] = df_raw['datetime'].map(
        lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))


    if parameter == "water_level" or parameter == "LakeLevel":
        observation = "observation_stage"
       # df_raw = df_raw[["datetime", "data", "corrected_data"]]
    elif parameter == "groundwater_level" or parameter == "Piezometer":
        observation = "observation_stage"
    elif parameter == 'water_temperature':
        observation = "parameter_observation"
    elif parameter == 'Conductivity' or 'conductivty':
        observation = "parameter_observation"
        #parameter = "Conductivity"

    elif parameter == "discharge" or parameter == "FlowLevel":
        #parameter = "discharge"
        df_raw = df_raw
        observation = "q_observation"
    return df_raw, parameter, observation, end_time


def graph_display(df_raw, site, Parameter_value, observation):
    from data_cleaning import reformat_data
    df_raw = reformat_data(df_raw)
    fig = graph(df_raw, site, Parameter_value, observation)
    figure_height = 600
    figure_width = 2000
    fig.update_layout(height=figure_height, width=figure_width)
    #'width': '10%', 'display': 'inline-block'
    return html.Div(dcc.Graph(figure = fig), style = {'width': '100%', 'display': 'inline-block'})

def rating_graph(field_observations, monitoring_peroid, rating_points, gzf, graph_axis_type, site, rating_curves, new_rating, observation_statistics):

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
    
    fig = make_subplots(rows=1, cols=1,
        #specs=[[{"type": "xy", "secondary_y": True, "rowspan": 2}, {"type": "Table"}], [{}, {"type": "Table"}]],
            #specs=[[{"type": "xy", "secondary_y": True}], [{"type": "xy", "secondary_y": True}]],
            
            column_widths=[1],
            row_heights=[.9],
            horizontal_spacing=horizontal_spacing_plots,
            vertical_spacing=vertical_spacing_plots)

    new_rating = new_rating.sort_values(by=['discharge']).copy()
    # display line issues
    new_rating_error = new_rating.copy()
    new_rating_error["error"] = 0
    for index, row in new_rating_error.iterrows():
        offset = row-1
        #print(f"offset {offset} row {row}")
        if row['discharge'] > offset['discharge']:
            row['error'] = 0
        else:
            row['error'] = 1
            
            print(f"error {row['discharge']} {offset['discharge']}")
    new_rating_error = new_rating_error.loc[new_rating_error['error'] == 1]
    print(new_rating_error)
    fig.add_trace(
        go.Scatter(
                y=new_rating['stage_offset'],
                x=new_rating['discharge'],
                line=dict(color='green',
                width=subplot_2_line_width),
                name='new rating',
                #mode='markers',
                #marker=dict(
                #color='green', size=6, opacity=.9),
                showlegend=False,),
            row=1, col=1, secondary_y=False,)
    def poly_fit_line(rating_points, fig):

        return fig.add_trace(
        go.Scatter(
            y=rating_points['observation_stage']-gzf,
            x=rating_points['poly_fit_line'],
            line=dict(color='rgb(152,78,163)', width=subplot_2_line_width),
            name='poly_fit_line', showlegend=False), row=1, col=1, secondary_y=False,)

    def linear_regression_line(rating_points, fig):

        return fig.add_trace(
        go.Scatter(
            y=rating_points['observation_stage']-gzf,
            x=rating_points['linear_regression_line'],
            line=dict(color='rgb(152,78,163)', width=subplot_2_line_width),
            name='line', showlegend=False), row=1, col=1, secondary_y=False,)

    def linear_regression_log(rating_points, fig):

        return fig.add_trace(
        go.Scatter(
            y=rating_points['observation_stage']-gzf,
            x=rating_points['linear_regression_log'],
            line=dict(color='rgb(152,78,163)', width=subplot_2_line_width),
            name='log', showlegend=False), row=1, col=1, secondary_y=False,)

    def linear_regression_log_gzf(rating_points, fig):

        return fig.add_trace(
        go.Scatter(
            y=rating_points['observation_stage']-gzf,
            x=rating_points['linear_regression_log_gzf'],
            line=dict(color='rgb(152,78,163)', width=subplot_2_line_width),
            name='log_gzf', showlegend=False), row=1, col=1, secondary_y=False,)
    

    def interpolate_line(rating_points, fig):
        rating_points_sort = rating_points.copy()
        rating_points_sort['observation_stage'] = rating_points_sort['observation_stage']-gzf
        rating_points_sort = rating_points.sort_values(by=['interpolate'])
        return fig.add_trace(
        go.Scatter(
                y=rating_points_sort['observation_stage']-gzf,
                x=rating_points_sort['interpolate'],
                line=dict(color='rgb(152,78,163)',
                width=subplot_2_line_width),
                name='interpolate_line',
                showlegend=False,),
            row=1, col=1, secondary_y=False,)
    # plotly x axis is horizontal (discharge)
    # plotly y axis is vertical (stage)
    def interpolate_error(rating_points, fig):
        rating_points_sort = rating_points.copy()
        rating_points_sort['observation_stage'] = rating_points_sort['observation_stage']-gzf
        rating_points_sort = rating_points.sort_values(by=['interpolate'])
        return [fig.add_trace(go.Scatter(
                    name='Upper Bound',
                    y=(rating_points_sort['observation_stage']-gzf)+((rating_points_sort['observation_stage']-gzf)*0.05),
                    x=rating_points_sort['interpolate']+(rating_points_sort['interpolate']*0.05),
                    mode='lines',
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    showlegend=False),row=1, col=1, secondary_y=False,),
                fig.add_trace(go.Scatter(
                    name='Lower Bound',
                    y=(rating_points_sort['observation_stage']-gzf)-((rating_points_sort['observation_stage']-gzf)*0.05),
                    x=rating_points_sort['interpolate']-(rating_points_sort['interpolate']*0.05),
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    mode='lines',
                    fillcolor='rgba(68, 68, 68, 0.3)',
                    fill='tonexty',
                    showlegend=False),row=1, col=1, secondary_y=False,)]


    if 'poly_fit_line' in rating_points.columns:
            poly_fit_line(rating_points, fig)
    if 'linear_regression_line' in rating_points.columns:
            linear_regression_line(rating_points, fig)       
    if 'interpolate' in rating_points.columns:
            interpolate_line(rating_points, fig)
            interpolate_error(rating_points, fig)
    if 'linear_regression_log' in rating_points.columns:
            linear_regression_log(rating_points, fig)
    if 'linear_regression_log_gzf' in rating_points.columns:
           linear_regression_log_gzf(rating_points, fig)
    
    fig.add_trace(
        go.Scatter(
            y=field_observations['observation_stage']-gzf,
            x=field_observations['discharge_observation'],
            mode='markers',
            marker=dict(
                color='grey', size=6, opacity=.9),
            text=field_observations['measurement_number'], name='field_observations', showlegend=False), row=1, col=1, secondary_y=False,)
    fig.add_trace(
        go.Scatter(
            y=monitoring_peroid['observation_stage']-gzf,
            x=monitoring_peroid['discharge_observation'],
            mode='markers',
            marker=dict(
                color='blue', size=6, opacity=.9),
            text=monitoring_peroid['measurement_number'], name='monitoring_peroid', showlegend=False), row=1, col=1, secondary_y=False,)
    fig.add_trace(
        go.Scatter(
            y=rating_points['observation_stage']-gzf,
            x=rating_points['discharge_observation'],
            mode='markers',
            marker=dict(
                color='green', size=6, opacity=.9),
            text=rating_points['measurement_number'], name='rating_points', showlegend=False), row=1, col=1, secondary_y=False,)
    from rating import rating_points_from_rating
    if rating_curves[0] != "0":
        for i in rating_curves:
                rating_number = str(i)
                rating_points, rating_offsets = rating_points_from_rating(site, rating_number)

                #sql_alchemy_connection = urllib.parse.quote_plus('DRIVER={'+driver+'}; SERVER='+server+'; DATABASE='+database+'; Trusted_Connection=yes;')
                #sql_engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % sql_alchemy_connection)
                #conn = sql_engine.raw_connection()

                #sql = f"select SITE_CODE as site_number, G_ID as site_sql_id from {config['parameters']['parameter_table']} WHERE STATUS = 'Active' AND FlowLevel = 'True'"
                #site_list = pd.read_sql_query(sql, conn)
                #conn.close()
                #conn = sql_engine.raw_connection()
                #site_sql_id = site_list.loc[site_list['site_number'] == site, 'site_sql_id'].item()
                #rating_points = pd.read_sql_query(f"SELECT WaterLevel as water_level_rating, CAST(Discharge AS float) as discharge_rating, RatingNumber "
                #                          f"FROM tblFlowRatings "
                #                          f"WHERE G_ID = '{str(site_sql_id)}' "
                #                          f"AND RatingNumber = '{i}' ;", conn)
                #conn.close()
                ## get rating offset
                #if i != 0:
                #    conn = sql_engine.raw_connection()
                #    rating_offsets = pd.read_sql_query(f"select Rating_Number from tblFlowRating_Stats WHERE Rating_Number = '{i}' GROUP BY Rating_Number ORDER BY Rating_Number DESC;", conn)
                #    #rating_offsets = rating_offsets['RatingNumber'].values.tolist()
                #    try:
                #        rating_offsets = rating_offsets.iloc[0, 0].astype(float)
                #    except:
                #        rating_offsets = 0 
                #    conn.close
                #else:
                 #   rating_offsets = 0
                rating_points = rating_points.sort_values(by=['water_level_rating'])
                fig.add_trace(
                    go.Scatter(
                        y=rating_points['water_level_rating'],
                        x=rating_points['discharge_rating'],
                        line=dict(color='grey', width=subplot_2_line_width),
                        name=f"{i}:{rating_offsets}", showlegend=False), row=1, col=1, secondary_y=False,)
    
    def observation_statistics_df(observation_statistics, fig):
        observation_statistics = observation_statistics.sort_values(by=['discharge_observation'])
        # filter out xero precent difference as these are probably rating points
        observation_statistics = observation_statistics.loc[abs(observation_statistics['precent_difference']) >= 6]
        return fig.add_trace(
        go.Scatter(
            y=observation_statistics['observation_stage']-gzf,
            x=observation_statistics['discharge_observation'],
            mode='markers',
            marker=dict(
                #color=observation_statistics['precent_difference'], size=6, opacity=.9),
                color='red', size=6, opacity=.9),
            text=observation_statistics['measurement_number'], name='stats', showlegend=False), row=1, col=1, secondary_y=False,)

    if 'precent_difference' in observation_statistics.columns:
           observation_statistics_df(observation_statistics, fig)
    fig.update_layout(legend_font_size=legend_font_size)
    # plotly x axis is horizontal (discharge)
    # plotly y axis is vertical (stage)
    #fig.update_xaxes(showline=False, linewidth=x_axis_line_width, linecolor='black', mirror=True, row=1, col=1)
    fig.update_xaxes(showline=True, linewidth=x_axis_line_width, linecolor='black', mirror=True, row=2, col=1)
    fig.update_yaxes(showline=True, linewidth=y_axis_line_width, linecolor='black', mirror=True, row=1, col=1)
    #fig.update_yaxes(showline=False, linewidth=y_axis_line_width, linecolor='black', mirror=True, row=2, col=1)
        
    fig.update_layout(font=dict(family = font_type, size = font_size,color="black"))

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    if "log" in graph_axis_type:
        graph_axis_type = 'log'
    else:
        graph_axis_type = 'linear'
    fig.update_yaxes(type=graph_axis_type)
    fig.update_xaxes(type=graph_axis_type)
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    fig.update_xaxes(showticklabels=True, row=1, col=1)
    #fig.update_xaxes(showticklabels=False, row=2, col=1)
    #fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=True, row=2, col=1)
    fig.update_layout(
        margin=dict(l=fig_margin_left, r=fig_margin_right, t=fig_margin_top, b=fig_margin_bottom))

    return html.Div(dcc.Graph(figure = fig), style = {'width': '100%', 'display': 'inline-block'})
