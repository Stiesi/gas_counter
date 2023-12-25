import time
import deta
import hmc5883l_jj as hmc

base_name="counter"
collection_id ='gas_recorder'
#url = f"https://database.deta.sh/v1/{collection_id}/{base_name}"
#detakey = "tNc9YQjG_WxQyAy9BXn95guCqPveZJwLsxbg2FrJW"
deta_key = "a07vrepk2zd_1mzeU3kyeWbr8Qtf8WAx9UM5A2y7E9Kx"

#datum = {'X-API-Key':deta_key,'Content-Type': 'application/json'}
#auth = f'X-API-Key : {deta_key}'

from deta import Deta


def copy_png(drive):
    try:
        drive.put('/jens/consumday_s.png',path='/tmp/consumday_s.png')
        drive.put('/jens/consumweek_s.png',path='/tmp/consumweek_s.png')
        drive.put('/jens/consummonth_s.png',path='/tmp/consummonth_s.png')
        drive.put('/jens/consumyear_s.png',path='/tmp/consumyear_s.png')
        drive.put('/jens/countday_s.png',path='/tmp/countday_s.png')
    except:
        print('error copying files to deta')
#deta_key = os.environ.get('eurex_base',_settings.settings.eurex_base)

# Connect to Deta Base with your Data Key
deta = Deta(deta_key)

db = deta.Base("counter")
drive = deta.Drive("graphs")


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
    
