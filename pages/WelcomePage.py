import streamlit as st


st.set_page_config(page_title="Welcome", layout="wide")


# Check if user is logged in
if "first_name" in st.session_state:
    st.title(f"Welcome {st.session_state['first_name']}!")
else:
    st.switch_page("Home.py")

if st.button("Company/Company Job"):
        st.switch_page("pages/Company.py")

if st.button("Chatbot"):
    st.switch_page("pages/Chatbot.py")

if st.button("Resume Enchancement"):
    st.switch_page("pages/EnchanceResume.py")

if st.button("Job Compatibility"):
    st.switch_page("pages/JobCompatibility.py")

if st.button("Personalized Recommendations"):
    st.switch_page("pages/JobCompatibility.py")

