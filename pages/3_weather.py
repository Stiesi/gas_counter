import streamlit as st
#import gc_utils as gcu
import pandas as pd
from meteostat import Point, Daily
from datetime import datetime,timedelta

import plotly.graph_objects as go


def plot_weather(weather):
    #temp = go.Trace(go.Scatter(x=weather.index,y=weather.tavg,name='Temperature'))
    layout = go.Layout(title='Temperatures over Time',
                    yaxis=dict(title='Average Temperature of the week'),
                    xaxis=dict(title='Date'),
                    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(x=weather.index,y=weather.tmin,name='Temperature min'))
    fig.add_trace(go.Scatter(x=weather.index,y=weather.tavg,name='Temperature'))
    fig.add_trace(go.Scatter(x=weather.index,y=weather.tmax,name='Temperature max'))

    df = weather
    df['date'] = pd.to_datetime(df.index)
    df = (df.groupby([pd.Grouper(key='date', freq='W-MON')])['tavg']
        .mean()        
        .reset_index())
    fig.add_trace(go.Bar(x=df.date-timedelta(days=4),y=df.tavg,name='Temp week avg'))

    return fig




st.title('History Weather for Jens')
#gcu.show_pngs()
start = datetime(2023, 1, 1)
end = datetime(2023, 12, 31)

home = Point(52.3212, 9.7455, 52 )
data = Daily(home,start,end)
weather=data.fetch()


st.plotly_chart(plot_weather(weather))
