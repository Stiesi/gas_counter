import streamlit as st
import gc_utils as gcu
import time

st.title('Check Sensitivity of Step Detection')

col1,col2,col3=st.columns((4,2,1))
with col1:
    lookbackm=st.slider('time in min',min_value=1,max_value=100,value=20,step=1)
    lookback=lookbackm*60
with col2:
    angstep=st.slider('step detection, angle in deg',min_value=1,max_value=180,value=90,step=1)
#with col3:
#    average=st.slider('average smooting',min_value=1,max_value=20,value=5,step=1)

save = st.button('Save triggers to counters')
if save:
    resp = gcu.save_counts(lookback=lookback,angstep=angstep)
    st.write(resp)


placeholder = st.empty()

while True:
    #time_int = int(time.time())
    #if time_int%20 < 7:
    df = gcu.get_counter_history(lookback=lookback)
    with placeholder.container():
        # cola,colb=st.columns((1,1))
        # with colb:
        #     pass
        # with cola:
        #     check = gcu.heartbeat() # yields problems with deta (too many requests??)
        #     #check=0
        #     if check==1:
        #         st.error('Trigger not Running')
        #     else:
        #         st.markdown(':green[Triggers are Running]')
        st.plotly_chart(gcu.plot_magneto(df,angstep))

        #st.markdown(f'Peaks found: {len(ix)}')
        st.plotly_chart(gcu.plot_polar(df))
    time.sleep(5.)
