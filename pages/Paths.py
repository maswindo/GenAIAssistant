import streamlit as st
from tools.Pathing import get_user_path
if 'logged_in' in st.session_state and st.session_state["logged_in"]:
    st.header("Paths")
    st.write(get_user_path())
    if st.button("Go to Job Listings"):
        st.switch_page("pages/JobListings.py")
else:
    st.write("You must be logged in to view this page.")