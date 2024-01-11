import streamlit as st
from detadb import gc_utils as gcu

st.title('Gas Counter ')
st.write('By Magnetic Field Measurement on local Raspberrypi')

import hmac


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here
#st.write("Here goes your normal Streamlit app...")
#st.button("Click me")
st.markdown('Welcome')
time_since_last_entry=gcu.health_daily()

if time_since_last_entry> 24*60*60:
    st.warning(f'daily update not updated since {int(time_since_last_entry)/24*60*60} days')
else:
    st.info('Daily update OK')



time_since_last_entry,laststamp=gcu.health_counter()
if time_since_last_entry> 200:
    st.warning(f'Trigger last update {laststamp}')
else:
    st.info('Trigger count OK')

if gcu.heartbeat():
    st.warning('Streamer is not running')
else:
    st.info('Streamer OK')

