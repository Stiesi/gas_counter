#Hannover-Ricklingen	2017	RR	54914	52.35	9.733	55	 	NI	01.01.1931	31.12.1984
from pydantic import BaseModel
import streamlit as st
import urllib.request
import json
from deta import Deta

deta_key = st.secrets['db_credentials']
mydeta = Deta(deta_key)
db = mydeta.Base("db_weather")

weather_key = st.secrets['weather_key']

class Weather(BaseModel):
    key: str
    location: str
    lat: float
    lon: float
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
    
    def put(self):
        db.put(self.model_dump())




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

    def get_weather(lat,lon):
        units = 'metric'
        WEATHERURL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={units}&appid={weather_key}"
        contents = urllib.request.urlopen(WEATHERURL).read()
        weather = json.loads(contents)
        return weather


""" def put_weather(weather):
    timestamp   = weather["dt"]

    data =  dict(key=str(timestamp),
                 
        weather_gen = weather["weather"][0]["description"],
        weather_icon= weather["weather"][0]["icon"],
        temperature = weather["main"]["temp"],
        pressure    = weather["main"]["pressure"],
        humidity    = weather["main"]["humidity"],
        wind_speed  = weather["wind"]["speed"],
        wind_dir    = weather["wind"]["deg"],
        clouds      = weather["clouds"]["all"],
    )
    
    #data = {**data,**datum}
    #r=requests.post(url = url, data = data, header = datum, params=PARAMS)
    #r=requests.put(url = url, data = data, headers=datum)
    #try:‚
    r=db.put(data)
    #except:
    #    r=None
    return r
 """


if __name__=='__main__':
    import time
    limit=10
    #city_name = 'Hannover'
    city_name = 'Hemmingen'
    state_code=''
    country_code='DE'
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




