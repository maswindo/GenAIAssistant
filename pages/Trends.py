import streamlit as st
from tools.MacroAnalytics import get_salaries_map,get_salaries_args
from tools.Infer_User_Preferences import get_inferred_occupation,get_inferred_occupations
if 'logged_in' in st.session_state and st.session_state["logged_in"]:
    st.header('Trends')
    st.write(get_inferred_occupation())
    st.plotly_chart(get_salaries_map())
    #occupations = get_inferred_occupations()
    #figs = get_salaries_args(occupations)
    #st.write(occupations[0])
    #st.plotly_chart(figs[0])
    #st.write(occupations[1])
    #st.plotly_chart(figs[1])
    #st.write(occupations[2])
    #st.plotly_chart(figs[2])
else:
    st.write("You must be logged in to view trends.")