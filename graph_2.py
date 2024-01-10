import pandas as pd
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

import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots
import datetime as dt
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

import configparser
import plotly.io as pio
import os
import plotly.graph_objs as go
import numpy as np
from plotly.subplots import make_subplots

if not os.path.exists("images"):
    os.mkdir("images")

config = configparser.ConfigParser()
config.read('gdata_config.ini')
color_map = {
    'north_seidel_creek': r'rgb(0, 0, 255)',
    'south_seidel_creek': r'rgb(173, 216, 230)',
    'webster_creek': r'rgb(118, 78, 159)',

    'fisher_creek': r'rgb(221, 204, 119)',#r'rgb(255, 0, 0)',
    'weiss_creek': r'rgb(255, 192, 203)',
    'cherry_trib': r'rgb(255, 237, 111)',
    'judd_creek': r'rgb(237, 110, 90)',#r'rgb(220, 20, 60)',
    'tahlequah_creek': r'rgb(253, 180, 98)',
    'taylor_creek': r'rgb(255, 99, 71)',
    'data': r'rgba(102, 102, 102, 0.4)',
    'corrected_data': r'rgba(29, 105, 150, 0.6)',
    1: r'#72B7B2',
    2: r'#F8A19F',
    'mean_discharge' : r'#316395', # dark blue
    "min7q_rolling_helper" : r"#2DE9FF",
    'min7q' : r"#00B5F7",
    'water_temperature' : r"#D62728",
    'temperature' : r"#D62728",
    'mean_temperature' : r"#D62728",
    'max_temperature' : r'#AF0038',
    'min_temperature' : r"#FF9DA6",
    'raw_water_temperature' : r"#D62728", # mean water temperature
    'corrected_water_temperature' : r'#AF0038', # max water temperature

    'conductivity' : r"#FECB52",
    'mean_conductivity' : r"#FECB52",
    'max_conductivity' : r'#FEAA16',
    'min_conductivity' : r"#F7E1A0",

    'discharge' : r"rgba(82, 188, 163, 0.6)",
    'mean_discharge' : r"#00B5F7",
    'max_discharge' : r'#2E91E5',
    'min_discharge' : r"rgb(179, 225, 207)",

    "high_pulse" : r"#DC587D",
    "low_pulse" : r"#F7E1A0",
   

    'mean_conductivity' : r'#FEAF16',
    'low_flow_peroid_water_temperature' : r"#F8A19F",
    'low_flow_peroid_box' : r'rgba(99, 110, 250, 0.3)',
    'summer_season_box' : r'rgba(99, 110, 250, 0.3)',

    #"water_year_7q" : r"rgba(204, 204, 204, 0.1)",
    "water_year_7q" : r"rgba(127, 60, 141, 0.9)",
    "min_7d" :  r"rgba(222, 172, 242, 0.9)",
    
    "low_flow_peroid_7q" : r"rgba(204, 204, 204, 0.3)",
    "summer_season_7q" : r"rgba(204, 204, 204, 0.6)",

    "field_observation" : r"rgb(136, 136, 136)",
    # Add more mappings as needed
    #'north_seidel_creek': r'#EF553B',
    #'south_seidel_creek': r'#FFA15A',
    #'webster_creek': r'#EECA3B',
    #'cherry_trib': r'#636EFA',
    #'fisher_creek': r'#AB63FA',
    #'judd_creek': r'#19D3FA',
    #'tahlequah_creek': r'#7E7DCD',
   # 'taylor_creek': r'#00CC96',
    #'weiss_creek': r'#1CFFCE',
    1: r'#72B7B2',
    2: r'#F8A19F',
    # Add more mappings as needed
    }

# site code = site_sql_id
def parameter_graph(df, site_code, site_name, parameter):
    if parameter == "FlowLevel":
         parameter = "discharge"
    try:
        from data_cleaning import reformat_data
        df = reformat_data(df)
    except:
        pass
    # get site number?
     # replace _ with space
    #subplot_titles = [value.replace("_", " ") for value in df.index.unique()]
    subplot_titles = parameter
    number_of_rows = 1
    number_of_columns = 1
    title_font_size = 50
    annotation_font_size = 65 # subplot titels are hardcoded as annotations
    show_subplot_titles = False # supblot titles are hardcoded as annotations
    font_size = 20
    show_chart_title = True
    chart_title = f"{site_name} {(parameter.replace('_', ' '))} {dt.datetime.strftime(df['datetime'].min(), '%Y-%m-%d')} to {dt.datetime.strftime(df['datetime'].max(), '%Y-%m-%d')}"
    title_x = .5
    plot_background_color = 'rgba(0,0,0,0)' #'rgba(0,0,0,0)' clearn
    subplot_titles = subplot_titles if show_subplot_titles else None

    x_axis_line = True # True/False
    x_axis_line_width = 1
    x_axis_line_color = 'black' #black
    x_axis_mirror = True #True/False

    y_axis_line = True # True/False
    y_axis_line_width = 1
    y_axis_line_color = 'black' #black
    y_axis_mirror = True #True/False

    figure_autosize = True #True/False
    y_axis_auto_margin  = True #True/False
    horizontal_subplot_spacing = 0.00
    font = "Arial"
# Create subplots
    fig = make_subplots(rows=number_of_rows, cols=number_of_columns, subplot_titles=subplot_titles, specs=[[{"secondary_y": True}] * number_of_columns] * number_of_rows, horizontal_spacing = horizontal_subplot_spacing)
    fig.update_layout(title_x=title_x)
    fig.update_layout(plot_bgcolor=plot_background_color)
    fig.update_xaxes(showline=x_axis_line, linewidth=x_axis_line_width, linecolor=x_axis_line_color, mirror=x_axis_mirror)
    fig.update_yaxes(automargin=y_axis_auto_margin)
    fig.update_layout(autosize = figure_autosize)
    fig.update_yaxes(showline=y_axis_line, linewidth=y_axis_line_width, linecolor=y_axis_line_color, mirror=y_axis_mirror)
    #fig3.update_layout(autosize=False,width=x,height=y) # this is to set a figure height using pixles
    #fig3.update_layout(autosize=False,width=80, height=80) # 80% of the available widthheight=0.8,  # 80% of the available height)
   
    # x is horizontal, y is veertical   The 'y' property is a number and may be specified as: - An int or float in the interval [-2, 3]
    legend_orientation =  "h" #h or v
    legend_x = 0.3
    legend_y = -0.1
    
    show_legend = True #True/False
    fig.update_layout(legend=dict(orientation=legend_orientation, x=legend_x, y=legend_y), showlegend=show_legend)

    margin_l = 0
    margin_r = 0
    margin_b = 0
    
    fig.update_layout(margin=dict(l=margin_l, r=margin_r, t=title_font_size+60, b=margin_b))  # Adjust the margin as neededautosize=False,
    fig.update_layout(font=dict(size=font_size))  # Set the desired text size)

    fig.update_annotations(font_size=annotation_font_size) # subplot titles are hardcoded as an annotation
    
    show_chart_title = True
    if show_chart_title == True:
        fig.update_layout(title_text=f"{chart_title}", title_font=dict(size=title_font_size))
       

    # font 
     # font 
    fig.update_layout(font_family=font, title_font_family=font,)
    #fig.update_yaxes(title_font_family=font, secondary = False)
    #fig.update_yaxes(title_font_family=font, Secondary = True)
    fig.update_xaxes(title_font_family=font)
        
        # multi site
        #fig3 = make_subplots(rows=df.index.nunique(), cols=1, subplot_titles=df.index.unique(), specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]])
        # single site
       
    row_count = 1

       
        ### Water temperature
        #for i in df.index.unique():
       
        #fig.update_yaxes(range=[0,1], row=row_count, col=1, secondary_y=True)
    fig.update_yaxes(title_text=f"{parameter.replace('_', ' ')} ({config[parameter]['unit']})", row=row_count, col=1, secondary_y=False, )
    fig.update_yaxes(showticklabels=False, row=row_count, col=1, secondary_y=True)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, secondary_y=False)
    fig.update_yaxes(showgrid=False, secondary_y=True)
            
            #fig3.add_trace(go.Scatter(
            #    x=df.loc[(df.index == i), "datetime"],
            #    y=df.loc[(df.index == i), "conductivity_daily_mean"],
            #    line=dict(color = color_map.get("mean_conductivity", 'black'), width = 1),
            #    name="conductivity_mean",showlegend=True,),row=row_count, col=1, secondary_y=False),
                ## summer flow box
            #fig.add_trace(go.Scatter(x=df.loc[(df.index == i), "datetime"], y = df.loc[(df.index == i), "summer_season"],
            #    fill = 'tonexty', fillcolor = color_map.get('summer_season_box', 'black'),
            #    line_shape = 'hv', line_color = 'rgba(0,0,0,0)', name="summer low-flow (June-September)",
            #    showlegend = False),row=row_count, col=1, secondary_y=True, )
            ## low flow peroid box
            #fig3.add_trace(go.Scatter(x=df.loc[(df.index == i), "datetime"], y = df.loc[(df.index == i), "low_flow_peroid"],
            #    fill = 'tonexty', fillcolor = color_map.get('low_flow_peroid_box', 'black'),
            #    line_shape = 'hv', line_color = 'rgba(0,0,0,0)',
            #    showlegend = False),row=row_count, col=1, secondary_y=True)
            
    fig.add_trace(go.Scatter(
                x=df.loc[:, "datetime"],
                y=df.loc[:, f"data"],
                line=dict(color=color_map.get(f"data", 'black'), width = 1),
                name=f"raw_{parameter}",showlegend=True,),row=row_count, col=1, secondary_y=False),
        
            
    if f"corrected_data" in df.columns:
            if df.corrected_data.mean() > df.data.mean()+10: # if there is a large difference, plot on secondary axis (discharge wont have a large difference)
                secondary = True
            else:
                 secondary = False
            fig.add_trace(go.Scatter(
                x=df.loc[:, "datetime"],
                y=df.loc[:, f"corrected_data"],
                line=dict(color=color_map.get(f"corrected_data", 'black'), width = 2),
                name=f"corrected_{parameter}",showlegend=True,),row=row_count, col=1, secondary_y=secondary),
        
    # special graph
    if f"{parameter}" in df.columns:
            if parameter == "discharge": # set primary axis to "stage (feet)"
                fig.update_yaxes(title_text=f"stage (wl feet)", row=row_count, col=1, secondary_y=False, )
            else:
                 fig.update_yaxes(title_text=f"{parameter.replace('_', ' ')} ({config[parameter]['unit']})", row=row_count, col=1, secondary_y=False, )
            fig.update_yaxes(title_text=f"{parameter.replace('_', ' ')} ({config[parameter]['unit']})", row=row_count, col=1, showticklabels=True, secondary_y=True, )
            #fig.update_yaxes(showgrid=False, showticklabels=False, row=row_count, col=1, secondary_y=True)
            fig.add_trace(go.Scatter(
                x=df.loc[:, "datetime"],
                y=df.loc[:, f"{parameter}"],
                line=dict(color=color_map.get(f"{parameter}", 'black'), width = 2),
                name=f"{parameter}",showlegend=True,),row=row_count, col=1, secondary_y=True),
        

    def annotations(obs):
            row_count = 1
            annotation_x = 0.05 # allows offset for when year is displatyed on axis
            annotation_y = -.08
              # annotation 
            obs_df = df.dropna(subset=[f"{obs}"])
            if obs_df.shape[0] > 0:
                # first observation
                fig.add_annotation(text=f"{obs_df['datetime'].iloc[0].strftime('%Y-%m-%d %H:%M')}",
                        xref="x domain", yref="y domain",
                        x=annotation_x, y=annotation_y, showarrow=False, row=row_count, col=1, secondary_y=False,)
                fig.add_annotation(text=f"obs: {obs_df[f'{obs}'].iloc[0]}",
                        xref="x domain", yref="y domain",
                        x=annotation_x, y=annotation_y-.02, showarrow=False, row=row_count, col=1, secondary_y=False,)
                fig.add_annotation(text=f"inst: {round(obs_df[f'data'].iloc[0], 2)}",
                        xref="x domain", yref="y domain",
                        x=annotation_x, y=annotation_y-.04, showarrow=False, row=row_count, col=1, secondary_y=False,)
                fig.add_annotation(text=f"offset: {round(obs_df[f'offset'].iloc[0], 2)}",
                        xref="x domain", yref="y domain",
                        x=annotation_x, y=annotation_y-.06, showarrow=False, row=row_count, col=1, secondary_y=False,)
                # last observation
                
                fig.add_annotation(text=f"{obs_df['datetime'].iloc[-1].strftime('%Y-%m-%d %H:%M')}",
                        xref="x domain", yref="y domain",
                        x=annotation_x+0.9, y=annotation_y, showarrow=False, row=row_count, col=1, secondary_y=False,)
                fig.add_annotation(text=f"obs: {obs_df[f'{obs}'].iloc[-1]}",
                        xref="x domain", yref="y domain",
                        x=annotation_x+0.9, y=annotation_y-.02, showarrow=False, row=row_count, col=1, secondary_y=False,)
                fig.add_annotation(text=f"inst: {round(obs_df[f'data'].iloc[-1], 2)}",
                        xref="x domain", yref="y domain",
                        x=annotation_x+0.9, y=annotation_y-.04, showarrow=False, row=row_count, col=1, secondary_y=False,)
                fig.add_annotation(text=f"offset: {round(obs_df[f'offset'].iloc[-1], 2)}",
                        xref="x domain", yref="y domain",
                    x=annotation_x+0.9, y=annotation_y-.06, showarrow=False, row=row_count, col=1, secondary_y=False,)
                
                # shift
                fig.add_annotation(text=f"session shift: {round((obs_df[f'offset'].iloc[-1] - obs_df[f'offset'].iloc[0]),2)}",
                    xref="x domain", yref="y domain",
                    x=.5, y=legend_y+.02, showarrow=False, row=row_count, col=1, secondary_y=False,)
        
    if "field_observations" in df.columns or "observations" in df.columns or "observation" in df.columns or "observation_stage" in df.columns:
            if "field_observations" in df.columns:
                obs = "field_observations"
            if "observations" in df.columns:
                obs = "observations"
            if "observation" in df.columns:
                obs = "observation"
            if "observation_stage" in df.columns:
                obs = "observation_stage"
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df[f'{obs}'],
            mode='markers',
            marker=dict(
                color=color_map.get(f"field_observation", 'black'), size=12, opacity=.9),
            text='', name=f"{obs}", showlegend=True), row=row_count, col=1, secondary_y=secondary,)
            annotations(obs)
    row_count = row_count+1
    
    return fig

def cache_graph_export(df, site_code, site_name, parameter):
    fig = parameter_graph(df, site_code, site_name, parameter)
    #if "field_observations" in df.columns:
        #annotations()
    paper_width = 2300
    paper_height = 1300

    # Update layout with fixed dimensions
    #fig.update_layout(autosize=True, width=paper_width, height = paper_height)

    # Use write_image to export the figure with fixed dimensions
    image_path = f"images/{site_name}_{parameter}_graph.jpeg"
    pio.write_image(fig, image_path, width=paper_width, height = paper_height)
    # update for display
    figure_height = 1000
#      figure width of 600 was originally used
    figure_width = 2300
    fig.update_layout(autosize=True, width=figure_width, height = figure_height)
    return html.Div(dcc.Graph(figure = fig), style = {'width': '100%', 'display': 'inline-block'})

def save_fig(df, site_code, site_name, parameter):
    # end date
    fig = parameter_graph(df, site_code, site_name, parameter)
    #start_date = df.head(1).iloc[0, df.columns.get_loc("datetime")].date().strftime("%Y_%m_%d")
    end_date = df.tail(1).iloc[0, df.columns.get_loc("datetime")].date().strftime("%Y_%m_%d")

    # end_date = dt.datetime.strftime(df['datetime'].max(), '%Y-%m-%d')
    paper_width = 2300
    paper_height = 1300
    fig.update_layout(autosize=True, width=paper_width, height = paper_height)
    file_path = r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site_name, parameter, end_date)

    # Use plotly.io.write_image to export the figure as a PDF
    pio.write_image(fig, file_path, format='pdf')
    # Update layout with fixed dimensions
    #fig.update_layout(autosize=True, width=paper_width, height = paper_height)

    # Use write_image to export the figure with fixed dimensions
    #image_path = f"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{site_name}_{parameter}_{end_date}.jpeg"
    #image_path = r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\t {0}_{1}_{2}.pdf".format(site_name, parameter, end_date)
    #image_path = f"images\{site_name}_{parameter}_{end_date}.jpeg"
    #os.makedirs(directory, exist_ok=True)

    #pio.write_image(fig, image_path, width=paper_width, height=paper_height)
    #fig.write_image(file=r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site_name, parameter, end_date), format='pdf', engine="kaleido")
    #fig.write_image(file=r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site, parameter, end_date), format='pdf', engine="kaleido")
    #scale = 1
    
    #fig.set_size_inches(11.69,8.27)
    
    #scale=1, width=1000, height=800
    # save as pdf
    #fig.update_layout(font_family="Serif", font_size=12)
    #fig.write_image(file=r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\{0}_{1}_{2}.pdf".format(site_name, parameter, end_date), format='pdf', engine="kaleido")
    # save as html
    #fig.write_html(r"W:\STS\hydro\GAUGE\Temp\Ian's Temp\t {0}_{1}_{2}.html".format(site, parameter, end_date))