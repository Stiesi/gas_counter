from fastapi import FastAPI


import gc_utils as gcu

app = FastAPI()
################################.   Schedule. ###############
@app.get("/heartbeat")
async def heartbeat():
    status = gcu.heartbeat()
    if status == 0:
        return {'message': 'OK'}
    else:
        return {'message': 'Error',
                'status': status}

@app.get("/savecounts")
async def save_counts(lookback:int=1000):
    resp = gcu.save_counts(lookback=lookback)
    return {'message': 'OK',
            'status': resp}


@app.post("/__space/v0/actions",tags=['schedule'],description='update counts from trigger')
async def events(event: dict):
#{
#  "event": {
#    "id": "cleanup",
#    "trigger": "schedule"
#  }
#}    
    # update all prices
    if event['event']['id']=='update_counts':
        ret = await gcu.save_counts()
    if event['event']['id']=='check_heartbeat':
        ret = await gcu.heartbeat()    
    if event['event']['id']=='update_daily':
        ret = await gcu.up_counts()
    return ret



#### ???? notwendig ??
@app.post("/check_trigger",tags=['trigger','schedule'],description='check if trigger database is up to date')
async def check_heartbeat():
    # check if trigger data is running
    # send message, if fails
    pass
    alarm=gcu.heartbeat()
#
    return {'message': alarm}

