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
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

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

#df_check = pd.read_csv("W:/STS/hydro/GAUGE/Temp/Ian's Temp/cahce_check/graph.csv", index_col=0)
    # df = pd.DataFrame(rows)
observation = "observation_stage"
#site = "Test"
#parameter = "discharge"
def graph(df, site, parameter, observation):
    def reformat(df):
        # reformat
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
        if 'data' in df.columns:
            df['data'] = df['data'].astype(float, errors="ignore")
        if 'corrected_data' in df.columns:
            df['corrected_data'] = df['corrected_data'].astype(float, errors="ignore")
        if 'observation' in df.columns:
            df['observation'] = df['observation'].astype(float, errors="ignore")
        if 'parameter_observation' in df.columns:
            df['parameter_observation'] = df['parameter_observation'].astype(float, errors="ignore")
        if 'offset' in df.columns:
            df['offset'].astype(float, errors="ignore")
        if 'discharge' in df.columns:
            df['discharge'].astype(float, errors="ignore")
        if 'q_observation' in df.columns:
            df['q_observation'].astype(float, errors="ignore")
        return df
    
    def observations(df, observation):
        # create observations dataframe
        # this copy makes it so you are not editing the original dataframe
        df_observations = df.copy()
        df_observations.dropna(inplace=True)
        return df_observations
    
    def titles(df, df_observations, site, parameter):
        start_time_minutes = df.head(1).iloc[0, df.columns.get_loc("datetime_string")]
        # get end time
        end_time_minutes = df.tail(1).iloc[0, df.columns.get_loc("datetime_string")]
        graph_title_a = "{0} {1} {2} {3}".format(site, parameter, start_time_minutes, end_time_minutes)
        table_title_a = "observations"
        return graph_title_a, table_title_a
    
    def subplots(graph_title_a, table_title_a):
        return make_subplots(rows=1, cols=1, subplot_titles=(
                            str(graph_title_a),
                            str(table_title_a)),
                    #specs=[[{"type": "xy", "secondary_y": True, "rowspan": 2}, {"type": "Table"}], [{}, {"type": "Table"}]],
                    specs=[[{"type": "xy", "secondary_y": True}]],
                    column_widths=[1],
                    horizontal_spacing=horizontal_spacing_plots,
                    vertical_spacing=vertical_spacing_plots)
    def subplot_1(df):
        return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['data'],
                    line=dict(color=subplot_1_line_color, width=subplot_1_line_width),
                    name=str("raw data")
                    ),
                row=1, col=1, secondary_y=True,)
    # corrected discharge
    def subplot_2(df):
        return fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['corrected_data'],
                    line=dict(color=subplot_2_line_color, width=subplot_2_line_width),
                    name=str("corrected_data"),
                    ),
                row=1, col=1, secondary_y=False,)
    def subplot_3(df_observations):
        return fig.add_trace(
                go.Scatter(
                    x=df_observations['datetime'],
                    y=df_observations[observation],
                    mode='markers',
                    marker=dict(
                        color='Black', size=6, opacity=.9),
                    text='', name='Observations'), row=1, col=1, secondary_y=False,)
    def save_fig(fig, df, site, parameter):
        #start_date = df.head(1).iloc[0, df.columns.get_loc("datetime")].date()
        # get end time
        #df.map(lambda x: dt.datetime.strftime(x, '%Y_%m_%d')).
        scale = 2
        paper_width = 400
        paper_height = 600
        end_date = df.tail(1).iloc[0, df.columns.get_loc("datetime")].date().strftime("%Y_%m_%d")
        #scale=1, width=1000, height=800
        # save as pdf
        fig.write_image(file=r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site, parameter, end_date), format='pdf',scale=scale)
        # save as html
        fig.write_html(r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\t {0}_{1}_{2}.html".format(site, parameter, end_date))
    df_check = df
    if (df_check.empty or len(df_check.columns) < 1):
        #return {'data': [{'x': [], 'y': [], 'type': 'line'}]}
        print("no_data")
    else:
        #df = pd.read_csv("W:/STS/hydro/GAUGE/Temp/Ian's Temp/cahce_check/graph.csv", index_col=0)
        # set observation to use, either observation_stage or parameter_observation
        if "parameter_observation" in df.columns:
            observation = "parameter_observation"
        else:
            observation = "observation_stage"
        reformat(df)
        df['datetime_string'] = df['datetime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))
        df_observations = observations(df, observation)
        graph_title_a, table_title_a = titles(df, df_observations, site, parameter)
    
        print("dataframe")
        print(df.head(5))
        print("observations dataframe")
        print(df_observations.head(5))
        # measurements for figure
        horizontal_spacing_plots = 0.75
        vertical_spacing_plots = 0.005
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
        legend_font_size = 7
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
        # make graph
        fig = subplots(graph_title_a, table_title_a)
        subplot_1(df)
        # corrected data
        subplot_2(df)
        subplot_3(df_observations)
        # add text
        '''
        fig.add_annotation(text="First Observation:",
                      xref="paper", yref="paper",
                      x=text_first_observation_x, y=text_first_observation_y, showarrow=False)
        '''
        fig.add_annotation(text=f"calculated {parameter}: {df['corrected_data'].iloc[0]}",
                      xref="paper", yref="paper",
                      x=text_first_measurement_x, y=text_first_measurement_y, showarrow=False)
        fig.add_annotation(text=f"raw {parameter}: {df['data'].iloc[0]}",
                      xref="paper", yref="paper",
                      x=text_first_instrument_x, y=text_first_instrument_y, showarrow=False)
        fig.add_annotation(text=f"offset: {(df['corrected_data'].iloc[0]-df['data'].iloc[0]).round(2)}",
                      xref="paper", yref="paper",
                      x=text_first_offset_x, y=text_first_offset_y, showarrow=False)
        '''
        fig.add_annotation(text="Last Observation:",
                      xref="paper", yref="paper",
                      x=text_last_observation_x, y=text_last_observation_y, showarrow=False)
        '''
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
        save_fig(fig, df, site, parameter)
        #fig.show()
'''


        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['data'],
                line=dict(color='Grey', width=1),
                name=str("Raw Data")
                ),
            row=1, col=1, secondary_y=False,)
    
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df[data_name],
            line=dict(color='Blue', width=2),
            name=str("corrected data")), row=1, col=1, secondary_y=True,)
    
        fig.add_trace(go.Scatter(
            x=df['datetime'],
            y=df['observation'],
            mode='markers',
            marker=dict(
                color='Black', size=6, opacity=.9),
            text='', name='Observations'), row=1, col=1, secondary_y=True,)
        # Display field ovservation information
        fig.append_trace(
            go.Table(
                header=dict(
                    values=["datetime", "instrument", "observation", "offset"],
                    font=dict(size=10),
                    align="left",
                    ),
                columnwidth=[40, 20, 20, 20],
                cells=dict(
                    # values=[df_observations[k].tolist() for k in df_observations.columns[1:]],
                    values=[df_observations['datetime_string'],
                            df_observations['data'],
                            df_observations["observation"],
                            df_observations["offset"]],
                    align="left")
            ),
            row=1, col=2)
    
        if parameter == 'FlowLevel':
            df = pd.DataFrame(rows)
            #try:
            df_q_observations = df.dropna(subset=["q_observation"]).copy()
            #except:
                #df_q_observations = pd.DataFrame({'': []})
            if df_q_observations.empty:
                df_q_observations['datetime_string'] = ""
                df_q_observations['q_observation'] = ""
                df_q_observations["Discharge_Rating"] = ""
                df_q_observations["q_offset"] = ""
                df_q_observations['datetime'] = ""
            elif rating == "NONE" and df_q_observations.empty:
                df_q_observations["Discharge_Rating"] = ""
                df_q_observations["q_offset"] = ""
                df_q_observations['datetime_string'] = ""
                df_q_observations['datetime'] = ""
    
            else:
                df_q_observations['datetime_string'] = pd.to_datetime(df_q_observations['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
                df_q_observations['datetime_string'] = df_q_observations['datetime_string'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))
                df_q_observations['discharge'] = df_q_observations['discharge'].astype(float, errors='ignore')
                df_q_observations.to_csv(r"W:\STS\hydro\GAUGE\Temp\Data\\SITE.csv")
                # pd.to_datetime(df_q_observations['DateTime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
                # df_q_observations['DateTime'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))
                conn_30 = SQL_String
                Rating_Offsets = pd.read_sql_query('select Offset, Rating_Number from tblFlowRating_Stats;', conn_30)
                Rating_Offsets['Rating_Number'] = Rating_Offsets['Rating_Number'].str.rstrip()
                try:
                    Rating_Offset = Rating_Offsets[Rating_Offsets['Rating_Number'] == rating].iloc[0, 0]
                
                    Rating_Offset = Rating_Offset.astype(float)
                    df_q_observations['WaterLevel'] = df["observation_stage"]-Rating_Offset
                    # Calculate Discharge from Offset
                    conn_31 = SQL_String
                    Rating_Points = pd.read_sql_query('select G_ID, RatingNumber, WaterLevel, Discharge, Marker, FlowRatings_id from tblFlowRatings WHERE G_ID = '+str(site_sql_id)+';', conn_31)
                    Rating_Points = Rating_Points[Rating_Points['RatingNumber'] == rating]
                    Rating_Points.rename(columns={"Discharge": "Discharge_Rating"}, inplace=True)
                    df_q_observations = pd.merge_asof(df_q_observations.sort_values('WaterLevel'), Rating_Points.sort_values('WaterLevel'), on='WaterLevel', allow_exact_matches=False, direction='nearest')
                    df_q_observations = df_q_observations.sort_values(by="datetime")
                
                    #df_observations.rename(columns={"Discharge_y": "Discharge_Calculated"}, inplace=True)
                    df_q_observations['q_offset'] = df_q_observations['q_observation']-df_q_observations['Discharge_Rating']
    
                    df_q_observations['Rating'] = str(rating)
                #df_q_observationss['DT_STRING'] = pd.to_datetime(df_q_observations['DateTime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
                # df_observations['DT_STRING'] = df_observations['DT_STRING'].map(lambda x: dt.datetime.strftime(x, '%Y-%m-%d %H:%M'))
                #df_observations = df_observations[['DT_STRING', "DischargeQ_", "Observation", "Offset"]]
                
                except:
                    df_q_observations.rename(columns={"discharge": "Discharge_Rating"}, inplace=True)
                    df_q_observations['q_observation'] = ""
                    df_q_observations["q_offset"] = ""
                    
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df["discharge"],
                line=dict(color='Red', width=2),
                name=str("discharge")), row=1, col=1, secondary_y=True,)
            fig.add_trace(go.Scatter(
                x=df_q_observations['datetime'],
                y=df_q_observations['q_observation'],
                mode='markers',
                marker=dict(
                    color='Pink', size=6, opacity=.9),
                text='', name='q Observations'), row=1, col=1, secondary_y=True,)
            # Display discharge ovservation information
            fig.append_trace(
                go.Table(
                    header=dict(
                        values=["datetime", "Q Measured", "Q Record", "Offset"],
                        font=dict(size=10),
                        align="left",
                        ),
                    columnwidth=[40, 15, 15, 15, 15],
                    cells=dict(
                        # values=[df_observations[k].tolist() for k in df_observations.columns[1:]],
                        values=[df_q_observations['datetime_string'],
                                df_q_observations['q_observation'],
                                df_q_observations["Discharge_Rating"],
                                df_q_observations["q_offset"]],
                        align="left")
                ),
                row=2, col=2)
    
    
        # ANNOTATE
        fig.update_layout(legend=dict(
            yanchor="bottom",
            y=.04,
            xanchor="right",
            x=.8  # lower number is farther right
        ))
        fig.update_xaxes(showline=True, linewidth=.05, linecolor='black', mirror=True)
        fig.update_yaxes(showline=True, linewidth=.05, linecolor='black', mirror=True)
    
    
        # Set y-axes titles
        if parameter == 'FlowLevel':
            fig.update_yaxes(title_text="Water Level", secondary_y=False)
            fig.update_yaxes(title_text="Discharge", secondary_y=True,)
        if parameter != 'FlowLevel':
            fig.update_yaxes(title_text=str(parameter), secondary_y=False)
            fig.update_yaxes(title_text="", secondary_y=True)
    
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)
        fig.update_xaxes(showticklabels=True)
        fig.update_yaxes(showticklabels=True)
        fig.update_layout(
            margin=dict(l=1, r=1, t=20, b=1)
            )
        return fig
'''