import pandas as pd
import numpy as np
from deta import Deta
import time
import datetime

import settings as _settings
import os

# write credentials to env/env file (no quotes in value! for key = values)
try:
    deta_key = os.environ.get('db_credentials',_settings.settings.db_credentials)
except:
    print('set Environment variable >>> db_credentials <<< to access deta data base')  
#dbkey = st.secrets['db_credentials']

deta = Deta(deta_key)

db = deta.Base("trigger") # continuously 8 h
db_count_dev = deta.Base("counter_dev")# from trigger , expires 1 Month
#db_count_m = deta.Base("counter_10min") #not used
#db_count_h = deta.Base("counter_1h") #not used
db_count = deta.Base("counter") # daily , update daily from 

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


def save_counts(lookback = 1000,angstep =100):
    # get count out of trigger and save count timepoints to database "db_count"
    df = get_counter_history(lookback=lookback)
    df,ixpeak,ix_relevant = create_peakfindings(df,angstep)
    if len(ix_relevant)<0:
        savedd = [dict(key=row.key) for index,row in df.loc[ix_relevant].iterrows()]
        resp = db_count_dev.put_many(savedd) # can save up to 25 items
    else: # do single puts
        resp = [db_count_dev.put(dict(key=row.key)) for index,row in df.loc[ix_relevant].iterrows()]
    #x=heartbeat()
    return resp

def group_signal(df,resolution,unit='H',groupby='trigger'):
    '''
    summarize counts to numbers

    unit 
    '''
    assert unit in ['min','H','D','W','M','Y']
    assert 'timestamp' in df.columns
    assert groupby in df.columns
    df['time'] = pd.to_datetime(df.timestamp,unit='s')
    dfg = (df.groupby([pd.Grouper(key='time', 
                                  #freq='W-MON',
                                  freq=f'{resolution}{unit}',
                                  ),])[groupby]
        .sum() 
        .reset_index())
    return dfg

def get_daily(start_date=None):
    # read counter_dev data with (unregular)
    #data = db_count.fetch()
    if start_date is None:
        data = db_count.fetch()
    else:
        data = db_count.fetch({'key?ge':start_date})
    df = pd.DataFrame.from_dict(data.items)    
    if not df.empty:
        df['timestamp']=pd.to_datetime(df.key.apply(int),unit='s',utc=True)
    return df
    

def timestamp_tokey(ts:datetime):
    return str(int(ts.value/1e9))


def update_daily(all=False):
    # signal as derived from trigger with unregular entries
    # get last existing entry in db daily
    lastday = db_count.fetch(limit=2,desc=True) # check??
    ### ACHTUNG Overlap kann Auswertung kaputt machen!!!
    # besser: ganze Tage ausschneiden: Anfangstag +1 bis letzter Tag -1 mit Gruppierung auswerten, 
    #         nur diese zufuegen, die sollten immer gleich sein, auch wenn sie ueberschreiben werden
    # only request new data
    if not all:
        try:
            df = get_count_dev(lastday.items[0].key) # sollte ab Vortag sein
        except:
            print('error in reading lastday from count_dev')
    if all:
        df = get_count_dev() # alle trigger
    minstamp = df.timestamp.min()
    #maxstamp = datetime.datetime(df.timestamp.max().day-1)
    df_cut = df.loc[df.timestamp>minstamp.replace(hour=23,minute=59,second=59)]
    # grouped to daily sums
    dfg = group_signal(df_cut,1,'D')
    dfg['key']=dfg.time.apply(timestamp_tokey)
    resp = [db_count.put(dict(key=row.key,usage=row.trigger)) for index,row in dfg.iterrows()]
    return resp



def heartbeat():
    # check if trigger is running by checking last timestamps
    now=datetime.datetime.now().timestamp()
    df = get_counter_history(lookback=120) # check last 120 s
    #  diff to latest datum
    lasttime = df['time'].max()
    delta = now - lasttime.timestamp()
    if delta > 30 : #after 30 secs
        return 1 # alarm
    else:
        return 0
    
def get_count_dev(trigger_step=0.1,start_date=None):
    # get trigger counts
    if start_date is None:
        data = db_count_dev.fetch()
    else:
        data = db_count_dev.fetch({'key?ge':start_date})

    df = pd.DataFrame.from_dict(data.items)
    
    #df['mag']=np.linalg.norm(df[['x','y','z']],axis=1)
    #df['ang']=np.arctan2(df['x'],df['y'])*180/np.pi
    df['timestamp']=pd.to_datetime(df.key.apply(int),unit='s',utc=True)
    df['trigger']=trigger_step
    return df


def update_pngs():
    '''
    Download figure ong files and show on streamlit page
    '''
    for file in ['countday_s.png','consumday_s.png','consumweek_s.png','consummonth_s.png','consumyear_s.png']:
        png = drive.get(f'/jens/{file}')
        with open(file,'wb') as fb:
            fb.write(png.read())
        png.close()


if __name__=='__main__':
    savd = save_counts()
    pass


