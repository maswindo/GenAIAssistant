import streamlit as st
from tools.MacroAnalytics import getJobSalariesByState
from tools.Infer_User_Preferences import get_inferred_occupation
if 'logged_in' in st.session_state and st.session_state["logged_in"]:
    st.header('Trends')
    st.write(get_inferred_occupation())
    st.plotly_chart(getJobSalariesByState())

else:
    st.write("You must be logged in to view trends.")