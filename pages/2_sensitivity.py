import streamlit as st
import gc_utils as gcu
import time

st.title('Check Sensitivity of Step Detection')

col1,col2,col3=st.columns((4,2,1))
with col1:
    lookbacks=st.slider('time in min',min_value=1,max_value=100,value=20,step=1)
    lookback=lookbacks*60
with col2:
    angstep=st.slider('step detection, angle in deg',min_value=1,max_value=180,value=90,step=1)
#with col3:
#    average=st.slider('average smooting',min_value=1,max_value=20,value=5,step=1)

placeholder = st.empty()

while True:
    #time_int = int(time.time())
    #if time_int%20 < 7:
    df = gcu.get_counter_history(lookback=lookback,angstep=angstep)
    with placeholder.container():
        st.plotly_chart(gcu.plot_magneto(df,angstep))

        #st.markdown(f'Peaks found: {len(ix)}')
        st.plotly_chart(gcu.plot_polar(df))
    time.sleep(5.)
