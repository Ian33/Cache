import gradio as gr
from vega_datasets import data

#cars = data.cars()
#iris = data.iris()

# # Or generate your own fake data

import pandas as pd
import random


parameter = "discharge"
site_sql_id = 1679
start_date = "01/01/2022 11:15"
end_date = "03/01/2022 12:00"
from import_data import sql_import
cars_data = sql_import(parameter, site_sql_id, start_date, end_date)
iris_data = sql_import(parameter, site_sql_id, start_date, end_date)
import gradio as gr
from vega_datasets import data

stocks = data.stocks()
gapminder = data.gapminder()
gapminder = gapminder.loc[
    gapminder.country.isin(["Argentina", "Australia", "Afghanistan"])
]
climate = data.climate()
print("climate")
print(climate.dtypes)
seattle_weather = data.seattle_weather()



import pandas as pd
import random
#
flow_site = sql_import(parameter, site_sql_id, start_date, end_date)
print('flowsite')
print(flow_site.dtypes)
def line_plot_fn(dataset):
    if dataset == "flow_site":
        return gr.LinePlot(
            flow_site,
            x="datetime",
            y="discharge",
            y_lim=[0, 500],
            title="Climate",
            tooltip=["datetime", "discharge"],
            height=300,
            width=500,
        )
    elif dataset == "climate":
        return gr.LinePlot(
            climate,
            x="DATE",
            y="HLY-TEMP-NORMAL",
            y_lim=[250, 500],
            title="Climate",
            tooltip=["DATE", "HLY-TEMP-NORMAL"],
            height=300,
            width=500,
        )
    elif dataset == "seattle_weather":
        return gr.LinePlot(
            seattle_weather,
            x="date",
            y="temp_min",
            tooltip=["weather", "date"],
            overlay_point=True,
            title="Seattle Weather",
            height=300,
            width=500,
        )
    elif dataset == "gapminder":
        return gr.LinePlot(
            gapminder,
            x="year",
            y="life_expect",
            color="country",
            title="Life expectancy for countries",
            stroke_dash="cluster",
            x_lim=[1950, 2010],
            tooltip=["country", "life_expect"],
            stroke_dash_legend_title="Country Cluster",
            height=300,
            width=500,
        )


with gr.Blocks() as line_plot:
    with gr.Row():
        with gr.Column():
            dataset = gr.Dropdown(
                choices=["flow_site", "climate", "seattle_weather", "gapminder"],
                value="stocks",
            )
        with gr.Column():
            plot = gr.LinePlot()
    dataset.change(line_plot_fn, inputs=dataset, outputs=plot)
    line_plot.load(fn=line_plot_fn, inputs=dataset, outputs=plot)


if __name__ == "__main__":
    line_plot.launch()

