import streamlit as st


st.set_page_config(page_title="Welcome", layout="wide")


# Check if user is logged in
if "first_name" in st.session_state:
    st.title(f"Welcome {st.session_state['first_name']}!")
else:
    st.switch_page("Home.py")


#if st.button("Chatbot"):
#    st.switch_page("pages/chatbot.py")

if st.button("Advanced Enchancer"):
    st.switch_page("pages/Advanced_Enhancer.py")

if st.button("Company"):
        st.switch_page("pages/Company.py")

if st.button("Compatibility Test"):
    st.switch_page("pages/compatability_test.py")

if st.button("Compatibility"):
    st.switch_page("pages/compatability.py")

if st.button("Enchance_Resume"):
    st.switch_page("pages/Enhance_Resume.py")

#if st.button("EnchanceResume"):
#    st.switch_page("pages/EnhanceResume.py")

if st.button("Find a Job"):
    st.switch_page("pages/JobListings.py")



