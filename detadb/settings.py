from typing import Union

from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict
import os
# 
class Settings(BaseSettings):
    # to work on Deta: path of .env not found
    model_config = SettingsConfigDict(env_file=os.path.join('env','env'), env_file_encoding='utf-8')
    #api_key: Union[str,None] = Field(default=None,alias='my_api_key')      
    db_credentials : Union[str,None] = Field(default=None)#,alias='eurex_api_key')  
    weather_key : Union[str,None] = Field(default=None)#,alias='deta_api_key')  
    user_manager : Union[str,None] = Field(default=None)#,alias='deta_api_key for users')  

settings=Settings()#_env_file='secrets.env' , _env_file_encoding='utf-8')
print('env-file',os.path.abspath("env"))
print('path',os.path.curdir)
