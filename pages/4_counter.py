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


    layout = go.Layout(title='Gas Consumption',
                    yaxis=dict(title='usage in m^3/d'),                    
                    #yaxis2=dict(title='Counter in m^3',
                    #            overlaying='y',
                    #            side='right'),
                    xaxis=dict(title='time',
                                )
                                )
    colors=['grey','burlywood','wheat','red','green']
    fig = go.Figure(layout=layout)

    fig.add_traces(go.Bar(x=dfg.time, y = dfg['usage'],
                            text=dfg['usage'],
                            name="consumption",
                            yaxis='y1',
                            texttemplate='%{text:.1f}', textposition='outside',
                            #line=dict(color=colors[0]),
                            )
                            )
    #fig.add_traces(go.Scatter(x=df.time, y = df['counter'],
    #                        name='counter',
    #                        line=dict(color=colors[0]),
    #                        yaxis='y2',
    #                        ),
    #                        )
    #fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
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


    layout = go.Layout(title='Triggers last 24 h',
                    yaxis=dict(title='usage in m^3/h'),                    
                    yaxis2=dict(title='Counter in m^3',
                                overlaying='y',
                                side='right'),
                    xaxis=dict(title='time',
                                )
                                )
    colors=['grey','burlywood','wheat','red','green']
    fig = go.Figure(layout=layout)

    fig.add_traces(go.Bar(x=dfg.time, y = dfg['usage'],
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
    #fig.add_annotation(text=f'total usage:{dfg.iloc[-1].counter -dfg.iloc[0].counter:.1f} m^3/24h',
    #                   xref="x domain",
    #            yref="y domain",
    #            x=0.7,
    #            y=.95,
    #            showarrow=False,
    #            )
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

df = gcu.get_count_dev()
if df.empty:  
    df = generate_signal() # artifical signal
df['counter']=df.trigger.cumsum()
df['time'] = pd.to_datetime(df.timestamp,unit='s',utc=True)
# 3600 s at 0.1 m^3 per consequtive steps
df['usage'] = (360/df.time.diff().dt.total_seconds()).rolling(window=5).mean()
now = datetime.now()

start = now-timedelta(days=1)
df24 = df.loc[df.key>str(int(start.timestamp()))]
df24g = gcu.group_signal(df24,60,'min')
df24g['counter'] = df24g.trigger.cumsum()
df24g['usage'] = (360/df.time.diff().dt.total_seconds())#.rolling(window=3).mean()

col1,col2,col3 = st.columns((1,1,1))
with col1:
    h_w = st.toggle("per hour",value=False)
with col2:
    st.markdown(f'Counter:   {df.iloc[-1].counter:.1f}')
with col3:    
    st.markdown(f'last 24h:  {df24.iloc[-1].counter -df24.iloc[0].counter:.1f}')

if h_w:
    df24=df24g

st.plotly_chart(plot_count24(df24))

col11,col22=st.columns((1,4))
with col11:
    unitname = st.radio('Sum',index=0,options=['Day','Week','Month','Year'])
    h_w_resolution=1
    unit=dict(Day='D',Week='W',Month='M',Year='Y')[unitname]
    dfh = gcu.get_daily()
    dfg = gcu.group_signal(dfh,h_w_resolution,unit=unit,groupby='usage')
with col22:
    st.plotly_chart(plot_count(dfg))

update=st.button('update daily')
if update:
    resp = gcu.update_daily(all=True)
    st.write(resp)
