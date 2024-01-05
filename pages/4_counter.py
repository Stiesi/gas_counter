import streamlit as st
import os
# 
import site
dir = os.path.dirname(__file__)
basedir=dir.replace('pages','deta')
site.addsitedir(basedir)
import gc_utils as gcu
import gc_plots as gp
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def plot_count(dfg):
    '''
    plot counting history

    Parameters:
    ----------
    df  DataFrame
        history data of triggers

    Return:
    -------
    fig  object
        plotly figure
    '''


    layout = go.Layout(title='Gas Counter from Triggers over Time',
                    yaxis=dict(title='usage in m^3/h'),                    
                    yaxis2=dict(title='Counter in m^3',
                                overlaying='y',
                                side='right'),
                    xaxis=dict(title='time',
                                )
                                )
    colors=['grey','burlywood','wheat','red','green']
    fig = go.Figure(layout=layout)

    fig.add_traces(go.Bar(x=dfg.time, y = dfg['trigger'],
                            name="consumption",
                            yaxis='y1',
                            #line=dict(color=colors[0]),
                            )
                            )
    fig.add_traces(go.Scatter(x=df.time, y = df['counter'],
                            name='counter',
                            line=dict(color=colors[0]),
                            yaxis='y2',
                            ),
                            )
    return fig

def plot_count24(dfg):
    '''
    plot counting history

    Parameters:
    ----------
    df  DataFrame
        history data of triggers

    Return:
    -------
    fig  object
        plotly figure
    '''


    layout = go.Layout(title='Gas Counter from Triggers over Time',
                    yaxis=dict(title='usage in m^3/h'),                    
                    yaxis2=dict(title='Counter in m^3',
                                overlaying='y',
                                side='right'),
                    xaxis=dict(title='time',
                                )
                                )
    colors=['grey','burlywood','wheat','red','green']
    fig = go.Figure(layout=layout)

    fig.add_traces(go.Bar(x=dfg.time, y = dfg['trigger'],
                            name="consumption",
                            yaxis='y1',
                            #line=dict(color=colors[0]),
                            )
                            )
    fig.add_traces(go.Scatter(x=dfg.time, y = dfg['counter'],
                            name='counter',
                            line=dict(color=colors[0]),
                            yaxis='y2',
                            ),
                            )
    return fig


def generate_signal(signal=1, length=100):
    '''
    create a signals of events in time
    to test the ordering and plotting
    '''
    now = datetime.now()
    if signal==1:
        # linear distribution
        start = now-timedelta(days=1)
        tp = np.linspace(int(start.timestamp()),int(now.timestamp()),num=length)
        df =  pd.DataFrame(tp.astype(np.int64),columns=['timestamp'])
        df['trigger']=0.1

    return df


st.title('History Overview for Jens')

#h_resolution=st.selectbox('Sum Period in Hours',options=[1,4,8,24],index=0)
h_24 = st.toggle("Daily Sum",value=False)
if h_24:
    h_resolution=24
else:
    h_resolution=1

df = gcu.get_count_dev()
if df.empty:  
    df = generate_signal() # artifical signal
df['counter']=df.trigger.cumsum()
#df['time'] = pd.to_datetime(df.timestamp,unit='s',utc=True)
now = datetime.now()

start = now-timedelta(days=1)
df24 = df.loc[df.key>str(int(start.timestamp()))]
df24g = gcu.group_signal(df24,5,'min')
df24g['counter'] = df24g.trigger.cumsum()
st.plotly_chart(plot_count24(df24g))


dfg = gcu.group_signal(df,h_resolution)

st.plotly_chart(plot_count(dfg))
