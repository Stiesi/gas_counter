import streamlit as st
import os
# 
import site
dir = os.path.dirname(__file__)
basedir=dir.replace('pages','deta')
site.addsitedir(basedir)
from detadb import gc_utils as gcu
import gc_plots as gp

st.title('History Overview for Jens')
gcu.update_pngs()
gp.show_pngs()


