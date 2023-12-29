#Hannover-Ricklingen	2017	RR	54914	52.35	9.733	55	 	NI	01.01.1931	31.12.1984
from pydantic import BaseModel
#import streamlit as st
import urllib.request
import json
import os
from deta import Deta
from fastapi import FastAPI

# write credentials to env/env file (no quotes in value! for key = values)
import settings as _settings


app = FastAPI()



try:
    deta_key = os.environ.get('db_credentials',_settings.settings.db_credentials)
except:
    print('set Environment variable >>> db_credentials <<< to access key for Deta Space API')  

try:
    weather_key = os.environ.get('weather_key',_settings.settings.weather_key)
except:
    print('set Environment variable >>> weather_key <<< to access key for OpenWeather API')  


#deta_key = st.secrets['db_credentials']
mydeta = Deta(deta_key)
db = mydeta.Base("db_weather")

#weather_key = st.secrets['weather_key']

class BaseWeather(BaseModel):
    location: str    
    lat: float=0
    lon: float=0

    def __init__(self,**kwargs):
        super().__init__(**kwargs)        
        citylist = BaseWeather.getmycity(self.location)
        while self.lat==0 and self.lon==0:
            [print(enum,city) for enum,city in enumerate(citylist)]
            id = int(input('Enter id of city: [0]') or 0)
            print(f'using {citylist[id]}')
            lat,lon = BaseWeather.get_lat_lon(citylist,id=id)
            self.lat=lat
            self.lon=lon


    def getmycity(city_name,country_code='DE',state_code='',limit=10):
        GEOURL = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&limit={limit}&appid={weather_key}"
        contents = urllib.request.urlopen(GEOURL).read()
        data = json.loads(contents)
        return data

    def get_lat_lon(data,id=0):
        try:
            lat = data[id]['lat']
            lon = data[id]['lon']
        except:
            lat=0
            lon=0
        return lat,lon

    def get_weather(self,lat,lon):
        units = 'metric'
        WEATHERURL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={weather_key}"
        contents = urllib.request.urlopen(WEATHERURL).read()
        weather = json.loads(contents)
        return weather

    def create_weather_set(self):
        weather = self.get_weather(self.lat,self.lon)
        data = Weather.from_openweathermap(weather)
        data.update(self.model_dump())
        return Weather(**data)



class Weather(BaseWeather):
    key: str
    timestamp: int
    weather_gen : str   #= weather["weather"][0]["description"],
    weather_icon: str   # weather["weather"][0]["icon"],
    temperature : float #= weather["main"]["temp"],
    pressure: float     # = weather["main"]["pressure"],
    humidity : float    # = weather["main"]["humidity"],
    wind_speed : float  # = weather["wind"]["speed"],
    wind_dir : float    #   = weather["wind"]["deg"],
    clouds : float      #   = weather["clouds"]["all"],    





    def __repr__(self):
        tl  = [ f'Location    = {self.location}',
                f'Weather     = {self.weather_gen}',
                f'Weather icon= {self.weather_icon}',
                f'Temperature = {self.temperature}',
                f'pressure    = {self.pressure}',
                f'humidity    = {self.humidity}',
                f'wind.speed  = {self.wind_speed}',
                f'wind.dir    = {self.wind_dir}',
                f'clouds      = {self.clouds}',
                f'timestamp   = {self.timestamp}',]
        
        txt = '\\n'.join(tl)
        return txt
    
    
    def from_openweathermap(weather):
        # create an instance of weather data, based on location

        # key
        timestamp   = weather["dt"]
        # data set
        data =  dict(key=str(timestamp),
        location    =weather["name"],
        lat         =weather["coord"]["lat"],
        lon         =weather["coord"]["lon"],
        weather_gen = weather["weather"][0]["description"],
        weather_icon= weather["weather"][0]["icon"],
        temperature = weather["main"]["temp"],
        pressure    = weather["main"]["pressure"],
        humidity    = weather["main"]["humidity"],
        wind_speed  = weather["wind"]["speed"],
        wind_dir    = weather["wind"]["deg"],
        clouds      = weather["clouds"]["all"],
        timestamp   = timestamp,
        )
        return data
    
    def update(self):
        # update weather data in object
        weather = self.get_weather(self.lat,self.lon)
        data = Weather.from_openweathermap(weather)
        self.__dict__.update(**data)


    def put(self):
        # save object to database 
        db.put(self.model_dump())

    def push(self):
        # update and put
        self.update()
        self.put()

################################.   Schedule. ###############

@app.post("/__space/v0/actions",tags=['schedule'],description='update weather from scheduled action')
async def events(event: dict):
#{
#  "event": {
#    "id": "cleanup",
#    "trigger": "schedule"
#  }
#}    
    # update all prices
    if event['event']['id']=='update_prices':
        ret = await update_weather()
    return ret

@app.post("/update_weather",tags=['weather','schedule'],description='update weather from scheduled action')
async def update_weather():
    # update weather from symbols in db_prices, if date < today
    #today = datetime.datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).toordinal()
    
    
    data = db.fetch(limit=1).items[0] # get any data
    weather = Weather(**data)
    # get update and save
    weather.push()
    
        #lastdate = entry['lastdate']
        #if today > lastdate:
        #out = await update_symbol(entry['key'])
        #print(out)
    return {'updated weather timestamp': weather.timestamp}


if __name__=='__main__':
    import time
    limit=10
    #city_name = 'Hannover'
    city_name = 'Hemmingen'
    state_code=''
    country_code='DE'
    if 0:
        lat,lon = Weather.get_lat_lon(Weather.getmycity(city_name,state_code=state_code,country_code=country_code))
        weather = Weather.get_weather(lat,lon)
        print(weather)
        print(f'Weather     = {weather["weather"][0]["description"]}')
        print(f'Weather icon= {weather["weather"][0]["icon"]}')
        print(f'Temperature = {weather["main"]["temp"]}')
        print(f'pressure    = {weather["main"]["pressure"]}')
        print(f'humidity    = {weather["main"]["humidity"]}')
        print(f'wind.speed  = {weather["wind"]["speed"]}')
        print(f'wind.dir    = {weather["wind"]["deg"]}')
        print(f'clouds      = {weather["clouds"]["all"]}')
        print(f'timestamp   = {weather["dt"]}')
        data = Weather.from_openweathermap(weather)
        myweather = Weather(**data)
        print(myweather)
        while True:
            weather = Weather.get_weather(lat,lon)
            #put_weather(weather)
            data = Weather.from_openweathermap(weather)
            myweather = Weather(**data)
            myweather.put()
            print(f'Temperature = {weather["main"]["temp"]}')
            print(f'timestamp   = {weather["dt"]}')
            time.sleep(300)
    if 0:
        mycity = BaseWeather(location=city_name)
        myweather = mycity.create_weather_set()
        while True:
            
            time.sleep(300)        
            myweather.push()
            
            print(myweather)



