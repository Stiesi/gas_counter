import time
import hmc5883l_jj as hmc
import math
import os
import streamlit as st

import settings as _settings

base_name="counter" # TODO rename to trigger!!
collection_id ='gas_recorder'

try:
    deta_key = os.environ.get('db_credentials',_settings.settings.db_credentials)
except:
    print('set Environment variable >>> db_credentials <<< to access key for Deta Space API')  

#deta_key = st.secrets['db_credentials']


from deta import Deta

class MagnetField:
    x: float=0
    y: float=0
    z: float=0

    def amplitude(self):
        return (math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z))
    def angle(self):
        return math.atan2(self.y,self.x) * 180 /math.pi
class Trigger:
    counter:float=0.
    magnet_position:int=1
    


def copy_png(drive):
    try:
        drive.put('/jens/consumday_s.png',path='/tmp/consumday_s.png')
        drive.put('/jens/consumweek_s.png',path='/tmp/consumweek_s.png')
        drive.put('/jens/consummonth_s.png',path='/tmp/consummonth_s.png')
        drive.put('/jens/consumyear_s.png',path='/tmp/consumyear_s.png')
        drive.put('/jens/countday_s.png',path='/tmp/countday_s.png')
    except:
        print('error copying files to deta')

# Connect to Deta Base with your Data Key
mydeta = Deta(deta_key)

db = mydeta.Base(base_name)
drive = mydeta.Drive("graphs")


#base = deta.Base()


try:
    compass = hmc.hmc5883l(gauss = 4.7, declination = (-2,5))
except:
    compass = hmc.hmc_dummy()

while True:
    
    x,y,z,ic = compass.safeaxes()

    now = time.localtime()
    nowstr=time.strftime('%d.%m - %H:%M',now)
    print(nowstr,x,y,z,ic)
    time_int = int(time.time())
    if time_int%20 < 7:
        copy_png(drive)
        print('files uploaded')
    timestamp = str(time_int)
    data =  dict(key=timestamp,x=x,y=y,z=z,ic=ic)
    #data = {**data,**datum}
    start=time.time()
    #r=requests.post(url = url, data = data, header = datum, params=PARAMS)
    #r=requests.put(url = url, data = data, headers=datum)
    if 0: # for debug
        r=db.put(data,expire_in=86400)
    else:
        r=None
    timeused=time.time()-start
    #print(r.content)
    if r is None:
        print(r)
    time.sleep(5.)
    
