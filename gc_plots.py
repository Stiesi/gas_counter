import streamlit as st
import plotly.graph_objects as go



def plot_magneto(df,ixpeak,ix_relevant):
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

    #df,ixpeak,ix_relevant = create_peakfindings(df,angstep)

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
    show files on streamlit page
    '''
    for file in ['countday_s.png','consumday_s.png','consumweek_s.png','consummonth_s.png','consumyear_s.png']:
        st.image(file,caption=file[:-6])
