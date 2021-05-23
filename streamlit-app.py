import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from tinydb import TinyDB

# Streamlit configuration
st.beta_set_page_config(layout="wide")
config = {'displayModeBar': False}

# Tool overview and color mapping
tools_and_color_map = {
    "Excel": "#1D6F42",
    "Google Chrome": "#DEE1E6", #"#666666",
    "Visual Studio Code": "#3FAAF2",
    "Jupyter Notebook": "#F37726",
    "PowerPoint": "#D04423",
    "Break": "#A5D38B",
    "Outlook": "#0072C6",
    "Power BI": "#F1C710",
    "Slack": "#ECB22E"
}

# Load data from db
db = TinyDB('timetracker-db.json')
df = pd.DataFrame(db.all())

# Datetime processing
df["datetime"] = pd.to_datetime(df["datetime"])
df["datetime_finish"] = df["datetime"] + pd.Timedelta(minutes=1)
df["date"] = df["datetime"].dt.date
max_date = df["datetime"].max()

# Function to extract keywords
def map_keywords(active_window, keywords):
    
    active_window = str(active_window)
    keyword_match = "Other"
    
    for k in keywords:
        if active_window.find(k) > 0:
            keyword_match = k

    if (len(active_window) == 0) or active_window == 'Windows-Standardsperrbildschirm':
        keyword_match = "Break"
        
    return keyword_match

# Extract keywords
df["keyword"] = df["active_window_name"].apply(map_keywords, keywords=tools_and_color_map.keys())

#st.subheader(f'Last data available {max_date}')
col1, _, _, _, col5 = st.beta_columns(5)
col1.title("Time tracker app")
date_selection = col5.date_input('')

# Filter by date
data = df[df["date"] == date_selection]

# Calculate tool changes (for Gantt chart)
data["tool_change"] = (df["keyword"] != df["keyword"].shift(1)).astype(int)
data["tool_change_counter"] = data["tool_change"].cumsum()

# Prepare data for Gantt chart
gantt_df = (data.groupby(["date","keyword","tool_change_counter"],as_index=False)
                .agg({"datetime": [np.min], "datetime_finish": [np.max]})
                )
gantt_df.columns = [col_name[0] for col_name in gantt_df.columns]
gantt_df = gantt_df.sort_values("datetime")

# Create two columns
col3, col4 = st.beta_columns(2)

# Pie Chart
fig = px.pie(df, values=[1]*len(data), names=df['keyword'], color=df['keyword'],
             color_discrete_map=tools_and_color_map)
fig.update_traces(hole=.6, hoverinfo="label+percent")
fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="right", x=0.75))
col3.subheader("Time per application")
col3.plotly_chart(fig, config=config)

# Gantt Chart
fig = px.timeline(gantt_df, x_start="datetime", x_end="datetime_finish", y="keyword", color="keyword",
                  color_discrete_map=tools_and_color_map
                 )
#fig.update_layout(showlegend=False, plot_bgcolor='rgb(256,256,256)') 
fig.update_layout(showlegend=False, template="plotly_white")
fig.update_yaxes(visible=True, showticklabels=True)
col4.subheader("Timeline")
col4.plotly_chart(fig, config=config)

