import pandas as pd
import numpy as np
import streamlit as st
from deta import Deta
import time
import datetime
import plotly.graph_objects as go

from deta import Deta

dbkey = st.secrets['db_credentials']

deta = Deta(dbkey)

db = deta.Base("trigger")
db_count = deta.Base("counter_dev")
drive = deta.Drive('graphs')

def find_peaks(a):
    '''
    find peak and valley values in 1D-array a
    '''
    da = np.diff(a)
    dachange = da[:-1]*da[1:]
    ix_change = np.where(dachange<0)
    return ix_change[0]+1

def get_counter_history(lookback=600):
    '''

    Get Data of magnetic values from deta Base

    Parameters:
    -----------
    lookback int
        time in s to retrieve from  database
    angstep int
        step size to identify a rotation

    Return:
    -------
    df  DataFrame
        history data of magnetic field

    '''
    now = time.time()
    getfrom = str(int(now -lookback))
    data = db.fetch({'key?gt':getfrom})
    #print (data)

    df = pd.DataFrame.from_dict(data.items)
    #fig = px.line(df, x='x', y='y', color='variable')
    df['mag']=np.linalg.norm(df[['x','y','z']],axis=1)
    df['ang']=np.arctan2(df['x'],df['y'])*180/np.pi
    df['time']=pd.to_datetime(df.key.apply(int),unit='s',utc=True)
    return df
    

def create_peakfindings(df,angstep):
    '''
    Parameters:
    -----------
    df  DataFrame with history

    Return:
    -------
    df  DataFrame
        history data of magnetic field with peak findings
    ixpeak int
        index of any peak in signal
    ix_relevant  int
        index of identified rotations in history
    '''
    #df['angs'] = df.ang.rolling(window=average).mean() 
    # use only peaks
    ixpeak = find_peaks(df.ang.values)
    df['peaks']=df.ang.loc[ixpeak]

    df['diff']=df.peaks.dropna().diff().abs() # differences of two sequential peaks
    ix_relevant = df.loc[df['diff']>angstep].index # only peaks > threshold
    #df['step']=0
    #df.step.loc[ix_relevant]=100
    return df,ixpeak,ix_relevant


def plot_magneto(df,angstep):
    '''
    plot magnetic field history

    Parameters:
    ----------
    df  DataFrame
        history data of magnetic field

    Return:
    -------
    fig  object
        plotly figure
    '''

    df,ixpeak,ix_relevant = create_peakfindings(df,angstep)

    layout = go.Layout(title='Gas Counter Magnetic Components over Time',
                    yaxis=dict(title='Magnetic Field'),
                    yaxis2=dict(title='Angle',
                                overlaying='y',
                                side='right'))
    colors=['grey','burlywood','wheat','red','green']
    fig = go.Figure(layout=layout)

    fig.add_traces(go.Scatter(x=df.time, y = df['x'], mode = 'lines',
                            name='x',
                            line=dict(color=colors[0]),
                            )
                            )
    fig.add_traces(go.Scatter(x=df.time, y = df['y'], mode = 'lines', 
                            line=dict(color=colors[1]),
                            name='y',
                            ))
    fig.add_traces(go.Scatter(x=df.time, y = df['z'], mode = 'lines', 
                            line=dict(color=colors[2]),
                            name='z',
                            ))
    fig.add_traces(go.Scatter(x=df.time, y = df['mag'], mode = 'lines', 
                            name='mag',
                            line=dict(color=colors[3]),
                            ))
    fig.add_traces(go.Scatter(x=df.time, y = df['ang'], mode = 'lines', 
                            name='ang',
                            yaxis='y2',
                            line=dict(color=colors[4]),
                            ))

    fig.add_traces(go.Scatter(x=df.time.loc[ixpeak], y = df['ang'].loc[ixpeak], mode = 'markers', 
                            name='ang_peak',
                            yaxis='y2',
                            #line=dict(color=colors[2])
                            ))

    for ip in ix_relevant:
        fig.add_annotation(x=df.time.iloc[ip], y = df['ang'].iloc[ip],
                           yref='y2',
                           text="Step",
                           #yshift=10,
                           )

    # fig.add_traces(go.Bar(x=df.time.loc[ix], y = df['step'].loc[ix],# mode = 'lines', 
    #                         name='switch',
    #                         yaxis='y2',
    #                         marker_color='red',
    #                         width=5,
    #                         #line=dict(color=colors[2])
    #                         ))
    fig.add_annotation(
        xref="x domain",
        yref="y domain",
        x=0.7,
        y=-0.15,
        text=f"Number of Peaks Found: {len(ix_relevant)}",
        # If axref is exactly the same as xref, then the text's position is
        # absolute and specified in the same coordinates as xref.
        #axref="x domain",
        # The same is the case for yref and ayref, but here the coordinates are data
        # coordinates
        #ayref="y domain",
        #ax=0.5,
        #ay=1,
        showarrow=False,
        #arrowhead=2,
    )
    return fig

def plot_polar(df):
    '''
    plot magnetic field history

    Parameters:
    ----------
    df  DataFrame
        history data of magnetic field

    Return:
    -------
    fig  object
        plotly figure
    '''

    layout = go.Layout(title='Gas Counter Magnetic Components in Polar Coordinates')


    figpolar = go.Figure(layout=layout)
    figpolar.add_traces(go.Scatterpolar(r=df['mag'],theta=df['ang'],
                                name='Polar x-y',
                                mode='lines',
                                opacity=0.5))

    figpolar.add_traces(go.Scatterpolar(r=[0,df['mag'].iloc[-1]],
                                theta=[0,df['ang'].iloc[-1]],
                                name='Latest',
                                mode='lines+markers',                               
                                line_color='red',
                                marker_color='red'))
    return figpolar

def show_pngs():
    '''
    Download figure ong files and show on streamlit page
    '''
    for file in ['countday_s.png','consumday_s.png','consumweek_s.png','consummonth_s.png','consumyear_s.png']:
        png = drive.get(f'/jens/{file}')
        with open(file,'wb') as fb:
            fb.write(png.read())
        png.close()
        st.image(file,caption=file[:-6])

def save_counts(lookback = 1000,angstep =100):
    df = get_counter_history(lookback=lookback)
    df,ixpeak,ix_relevant = create_peakfindings(df,angstep)
    if len(ix_relevant)<25:
        savedd = [dict(key=row.key) for index,row in df.loc[ix_relevant].iterrows()]
        resp = db_count.put_many(savedd) # can save up to 25 items
    else: # do single puts
        resp = [db_count.put(dict(key=row.key)) for index,row in df.loc[ix_relevant].iterrows()]
    #x=heartbeat()
    return resp

def heartbeat():
    now=datetime.datetime.now().timestamp()
    df = get_counter_history(lookback=100) # check last 100 s
    #  diff to latest datum
    lasttime = df['time'].max()
    delta = now - lasttime.timestamp()
    if delta > 30 : #after 30 secs
        return 1 # alarm
    else:
        return 0



if __name__=='__main__':
    savd = save_counts()
    pass


