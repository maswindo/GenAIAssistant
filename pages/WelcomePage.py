import streamlit as st


st.set_page_config(page_title="Welcome", layout="wide")


# Check if user is logged in
if "first_name" in st.session_state:
    st.title(f"Welcome, {st.session_state['first_name']}!")
else:
    st.switch_page("Home.py")

# Search for a company
search_query = st.text_input("Search for a company", placeholder="Enter company name...")

if st.button("Search"):
    if search_query:
        # Store the search query in session state to access on Company page
        st.session_state["search_query"] = search_query
        st.session_state["company_data"] = None  # Reset previous company data
        # Redirect to the Company page
        st.switch_page("pages/Company.py")
    else:
        st.error("Please enter a company name.")

if st.button("Chatbot"):
    st.switch_page("pages/Chatbot.py")
