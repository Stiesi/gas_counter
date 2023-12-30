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
    fig.add_trace(go.Scatter(x=weather.index,y=weather.tmin,name='Temperature min',opacity=0.2))
    fig.add_trace(go.Scatter(x=weather.index,y=weather.tavg,name='Temperature',opacity=0.2))
    fig.add_trace(go.Scatter(x=weather.index,y=weather.tmax,name='Temperature max',opacity=0.2))

    df = weather
    df['date'] = pd.to_datetime(df.index)
    df = (df.groupby([pd.Grouper(key='date', freq='W-MON')])['tavg']
        .mean()        
        .reset_index())
    fig.add_trace(go.Bar(x=df.date-timedelta(days=4),y=df.tavg,name='Temp week avg'))

    return fig


def get_datetime(date):
    return datetime.combine(date,datetime.min.time())


st.title('History Weather for Jens')
#gcu.show_pngs()
col1,col2 =st.columns((1,1))
with col1:
    start = st.date_input('Start',datetime.today()-timedelta(days=365),format="DD.MM.YYYY")
with col2:
    end = st.date_input('End',"today",format="DD.MM.YYYY")

#start = datetime(2023, 1, 1)
#end = datetime(2023, 12, 31)

home = Point(52.3212, 9.7455, 52 )
data = Daily(home,get_datetime(start),get_datetime(end)) # needs datetime type
weather=data.fetch()


st.plotly_chart(plot_weather(weather))
