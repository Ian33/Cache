import gradio as gr

import pandas as pd
#import datase#ts
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO#
import configparser
config = configparser.ConfigParser()
config.read('gdata_config.ini')


parameter = "discharge"
site_sql_id = 1679
start_date = "01/01/2022 11:15"
end_date = "03/01/2022 12:00"
from import_data import sql_import
df = sql_import(parameter, site_sql_id, start_date, end_date)
print(df)
#def greet(name):

#    return "Hello " + name + "!"

#demo = gr.Interface(fn=greet, inputs="text", outputs="text")

def plot(df):
  plt.scatter(df.datetime, df.discharge)
  plt.savefig("scatter.png")
  #df['failure'].value_counts().plot(kind='bar')
  #plt.savefig("bar.png")
  #sns.heatmap(df.select_dtypes(include="number").corr())
 # plt.savefig("corr.png")
  plots = ["scatter.png"]
  return plots

inputs = [gr.Dataframe(label="Supersoaker Production Data")]
outputs = [gr.Gallery(label="Profiling Dashboard", columns=(1,3))]

app = gr.Interface(plot, inputs=inputs, outputs=outputs, examples=[df.head(100)], title="Supersoaker Failures Analysis Dashboard").launch()
    
if __name__ == "__main__":
    app.launch(show_api=False)   


