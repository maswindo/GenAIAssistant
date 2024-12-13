import streamlit as st
from tools.MacroAnalytics import get_salaries_map, get_salaries_args, get_occupation_statistics
from tools.Infer_User_Preferences import get_inferred_occupation,get_inferred_occupations

if 'logged_in' in st.session_state and st.session_state["logged_in"]:
    st.header('Trends')
    inferred_occupation = get_inferred_occupation()
    st.write(f"We've inferred your best occupation fit to be: {inferred_occupation}")
    st.plotly_chart(get_salaries_map(inferred_occupation))
    #occupations = get_inferred_occupations()
    #figs = get_salaries_args(occupations)
    #st.write(occupations[0])
    #st.plotly_chart(figs[0])
    #st.write(occupations[1])
    #st.plotly_chart(figs[1])
    #st.write(occupations[2])
    #st.plotly_chart(figs[2])
    st.write(get_occupation_statistics(inferred_occupation))
    if st.button("Go to Paths"):
        st.switch_page("pages/Paths.py")
else:
    st.write("You must be logged in to view trends.")