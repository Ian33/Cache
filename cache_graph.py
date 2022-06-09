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
# add a note ####
# added a second note #
# a forth comment

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

import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots

### Set a bunch of parameters
# this is for the save figure
paper_width = 800
paper_height = 1500
# measurements for figure
horizontal_spacing_plots = 0.75
vertical_spacing_plots = 0.005
# figure font size
font_size = 10
font_type = "Arial"
# fig height of 400 was originally used
figure_height = 400
# figure width of 600 was originally used
figure_width = 600
legend_y_anchor = "top"
legend_x_anchor = "right"
# legend position y = 1 x=0.94 is top right of graph
legend_y_position = -.01 # higer number moves up
legend_x_position = 1 # lower number moves left
# legend viability
show_legend = True
# legend font size
legend_font_size = 4
subplot_1_line_width = 1
subplot_1_line_color = "grey"
subplot_2_line_width = 1
subplot_2_line_color = "blue"
fig_margin_left = 1
fig_margin_right = 1
fig_margin_top = 40
fig_margin_bottom = 60
x_axis_line_width = .25
y_axis_line_width = .25
# observation header
text_first_observation_x = 0.0
text_first_observation_y = -0.1 # higher number moves up, base (0) is bottom inside of graph line
text_last_observation_x = .7 # justified to left, 0.5 is halfway across paper
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
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
   
    if 'data' in df.columns:
        df['data'] = df['data'].astype(float, errors="ignore")
    if 'corrected_data' in df.columns:
        df['corrected_data'] = df['corrected_data'].astype(float, errors="ignore")
    if 'observation' in df.columns:
        df['observation'] = df['observation'].astype(float, errors="ignore")
    if 'observation_stage' in df.columns:
        df['observation_stage'] = df['observation_stage'].astype(float, errors="ignore")
    if 'parameter_observation' in df.columns:
        df['parameter_observation'] = df['parameter_observation'].astype(float, errors="ignore")
    if 'offset' in df.columns:
        df['offset'].astype(float, errors="ignore")
    if 'discharge' in df.columns:
        df['discharge'].astype(float, errors="ignore")
    if 'q_observation' in df.columns:
        df['q_observation'].astype(float, errors="ignore")
    if 'Discharge_Rating' in df.columns:
        df['Discharge_Rating'].astype(float, errors="ignore")
    if 'q_offset' in df.columns:
        df['q_offset'].astype(float, errors="ignore")
    
    return df

def observations(df, observation):
    # create observations dataframe
    # this copy makes it so you are not editing the original dataframe
    df_observations = df.copy()
    
    #df_observations.dropna(inplace=True)
    # this is a place holder as observationd do not get passed to program right now
    #  df_observations = pd.DataFrame({'': []})
    
    return df_observations

def titles(df, df_observations, site, parameter):
    start_time_minutes = df.head(1).iloc[0, df.columns.get_loc("datetime_string")]
    # get end time
    end_time_minutes = df.tail(1).iloc[0, df.columns.get_loc("datetime_string")]
    graph_title_a = "{0} {1} {2} {3}".format(site, parameter, start_time_minutes, end_time_minutes)
    table_title_a = "observations"
    return graph_title_a, table_title_a


def subplots(graph_title_a, table_title_a):
    today = pd.to_datetime('today')
    return make_subplots(rows=1, cols=1, subplot_titles=(
        f"created: {today}"),
        #specs=[[{"type": "xy", "secondary_y": True, "rowspan": 2}, {"type": "Table"}], [{}, {"type": "Table"}]],
            specs=[[{"type": "xy", "secondary_y": True}]],
            column_widths=[1],
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
            name=str("corrected_data"),
            ),
        row=1, col=1, secondary_y=False,)

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
def subplot_oobservation(df_observations, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df_observations['datetime'],
            y=df_observations['observation'],
            mode='markers',
            marker=dict(
                color='Black', size=6, opacity=.9),
            text='', name='observations'), row=1, col=1, secondary_y=False,)

def subplot_observation_stage(df_observations, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df_observations['datetime'],
            y=df_observations['observation_stage'],
            mode='markers',
            marker=dict(
                color='Black', size=6, opacity=.9),
            text='', name='observation_stage'), row=1, col=1, secondary_y=False,)

def subplot_parameter_observation(df_observations, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df_observations['datetime'],
            y=df_observations['parameter_observation'],
            mode='markers',
            marker=dict(
                color='Black', size=6, opacity=.9),
            text='', name='parameter_observation'), row=1, col=1, secondary_y=False,)

def subplot_q_observatio(df_observations, observation, fig):
    return fig.add_trace(
        go.Scatter(
            x=df_observations['datetime'],
            y=df_observations['q_observation'],
            mode='markers',
            marker=dict(
                color='grey', size=6, opacity=.9),
            text='', name='q_observation'), row=1, col=1, secondary_y=True,)
  

def save_fig(fig, df, site, parameter):
    scale = 2
    end_date = df.tail(1).iloc[0, df.columns.get_loc("datetime")].date().strftime("%Y_%m_%d")
    #scale=1, width=1000, height=800
    # save as pdf
    fig.write_image(file=r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site, parameter, end_date), format='pdf',scale=scale)
    # save as html
    fig.write_html(r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\t {0}_{1}_{2}.html".format(site, parameter, end_date))

# run program
def graph(df, site, parameter, observation):
    # need to set graph here
    df = df

    # this is probably redundent as cache should do this
    if (df.empty or len(df.columns) < 1):
        #return {'data': [{'x': [], 'y': [], 'type': 'line'}]}
        print("no_data")
    else:
        reformat(df)
        df['datetime_string'] = df['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))
        df_observations = observations(df, observation)
        graph_title_a, table_title_a = titles(df, df_observations, site, parameter)
        # make graph
        fig = subplots(graph_title_a, table_title_a)
        subplot_1(df, fig)
        # corrected data
        subplot_2(df, fig)
        # discharge column
        if 'discharge' in df.columns:
            subplot_discharge(df, fig)
            #fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
            fig.update_yaxes(title_text="discharge (cfs)", secondary_y=True)
        
        # observation subplots
        if 'observation' in df_observations.columns:
            subplot_oobservation(df_observations, observation, fig)
        if 'observation_stage' in df_observations.columns:
            subplot_observation_stage(df_observations, observation, fig)
        if 'parameter_observation' in df_observations.columns:
            subplot_parameter_observation(df_observations, observation, fig)
        if 'q_observation' in df_observations.columns:
            subplot_q_observatio(df_observations, observation, fig)

        # add text
        fig.add_annotation(text=f"calculated {parameter}: {df['corrected_data'].iloc[0]}",
                  xref="paper", yref="paper",
                  x=text_first_measurement_x, y=text_first_measurement_y, showarrow=False)
        fig.add_annotation(text=f"raw {parameter}: {df['data'].iloc[0]}",
                  xref="paper", yref="paper",
                  x=text_first_instrument_x, y=text_first_instrument_y, showarrow=False)
        fig.add_annotation(text=f"offset: {(df['corrected_data'].iloc[0]-df['data'].iloc[0]).round(2)}",
                  xref="paper", yref="paper",
                  x=text_first_offset_x, y=text_first_offset_y, showarrow=False)
        fig.add_annotation(text=f"calculated {parameter}: {df['corrected_data'].iloc[-1]}",
                  xref="paper", yref="paper",
                  x=text_last_measurement_x, y=text_last_measurement_y, showarrow=False)
        fig.add_annotation(text=f"raw {parameter}: {df['data'].iloc[0]}",
                  xref="paper", yref="paper",
                  x=text_last_instrument_x, y=text_last_instrument_y, showarrow=False)
        fig.add_annotation(text=f"offset: {(df['corrected_data'].iloc[0]-df['data'].iloc[0]).round(2)}",
                  xref="paper", yref="paper",
                  x=text_last_offset_x, y=text_last_offset_y, showarrow=False)

        # update figure
        fig.update_layout(height=figure_height, width=figure_width, title_text=graph_title_a)
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
            x=legend_x_position  # lower number is farther right
        ))
        # set ledgend visability
        fig.update_layout(showlegend=show_legend)
        # set legend font
        fig.update_layout(legend_font_size=legend_font_size)
        fig.update_xaxes(showline=True, linewidth=x_axis_line_width, linecolor='black', mirror=True)
        fig.update_yaxes(showline=True, linewidth=y_axis_line_width, linecolor='black', mirror=True)
        # set text size and font
        # fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        fig.update_layout(font=dict(family = font_type, size = font_size,color="black"))
        
        
        '''
        # Set y-axes titles
            if parameter == 'FlowLevel':
                fig.update_yaxes(title_text="Water Level", secondary_y=False)
                fig.update_yaxes(title_text="Discharge", secondary_y=True,)
            if parameter != 'FlowLevel':
                fig.update_yaxes(title_text=str(parameter), secondary_y=False)
                fig.update_yaxes(title_text="", secondary_y=True)
        '''
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showticklabels=True)
        fig.update_yaxes(showticklabels=True)
        fig.update_layout(
            margin=dict(l=fig_margin_left, r=fig_margin_right, t=fig_margin_top, b=fig_margin_bottom))
        #fig.show(renderer="svg")
        #save_fig(fig, df, site, parameter)
        #fig.show()
        return fig

def format_cache_data(df_raw, parameter):
    '''takes a raw df from cache, and does some pre-processing and adds settings'''
    '''returns df to cache, which sends df back to this program'''
    '''as this program is used in multiple parts of cache and is still in dev,
        this is a good workaround from having to copy and paste the dev code'''
    end_time = df_raw.tail(1)
    end_time['datetime'] = pd.to_datetime(
    end_time['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    #end_time['datetime'] = pd.to_datetime(end_time['datetime'], format='%Y-%m-%d', errors='coerce', infer_datetime_format=True)
    end_time['datetime'] = end_time['datetime'].map(
        lambda x: dt.datetime.strftime(x, '%Y_%m_%d'))
    end_time = end_time.iloc[0, 0]

    df_raw['datetime'] = pd.to_datetime(
        df_raw['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    #end_time['datetime'] = pd.to_datetime(end_time['datetime'], format='%Y-%m-%d', errors='coerce', infer_datetime_format=True)
    df_raw['datetime'] = df_raw['datetime'].map(
        lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M:%S'))
        
    if parameter == "water_level" or parameter == "LakeLevel":
        parameter = "water_level"
        observation = "observation_stage"
        df_raw = df_raw[["datetime", "data", "corrected_data"]]
    if parameter == "groundwater_level" or parameter == "Piezometer":
        parameter = "groundwater_level"
        observation = "observation_stage"
        df_raw = df_raw[["datetime", "data", "corrected_data"]]
    if parameter == 'water_temperature':
        df_raw = df_raw[["datetime", "data", "corrected_data"]]
        observation = "parameter_observation"
    if parameter == "discharge" or parameter == "FlowLevel":
        parameter = "discharge"
        df_raw = df_raw[["datetime", "data", "corrected_data", "discharge", "observation_stage", "q_observation"]]
        observation = "q_observation"
    return df_raw, parameter, observation, end_time
        
    
#### to test 
df = pd.read_csv(r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\58A_discharge_2022_02_06.csv")
site = "58A"
parameter = "discharge"
observation = "q_observation"
fig = graph(df, site, parameter, observation)
save_fig(fig, df, site, parameter)