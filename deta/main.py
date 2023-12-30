from fastapi import FastAPI

# write credentials to env/env file (no quotes in value! for key = values)
import settings as _settings
import gc_utils as gcu

app = FastAPI()
################################.   Schedule. ###############

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
    if event['event']['id']=='check_hearbeat':
        ret = await gcu.heartbeat()    
    return ret



#### ???? notwendig ??
@app.post("/check_trigger",tags=['trigger','schedule'],description='check if trigger database is up to date')
async def check_heartbeat():
    # check if trigger data is running
    # send message, if fails
    pass
    alarm=0
#
    return {'message': alarm}

