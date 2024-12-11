from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

def check_credentials(username_from_client, password_from_client):
    # MongoDB URI without the tlsCAFile option
    uri = os.environ.get('URI_FOR_Mongo')

    # Create MongoClient object with tlsCAFile option
    #tlsCAFile=os.environ.get('tlsCAFile')
    tlsCAFile = certifi.where()
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))

    # Now you can use the 'client' object to interact with your MongoDB database
    # Select the database and collection
    database_name = "499"
    collection_name = "login_info"
    db = client[database_name]
    collection = db[collection_name]

    # Query for the specified username and password
    query = {"username": username_from_client, "password": password_from_client}
    result = collection.find_one(query)

    # Check if the result is not None (credentials exist)
    if result:
        # Store the username and first name in session state
        st.session_state["username"] = result["username"]
        st.session_state["first_name"] = result["firstName"]
        st.session_state['logged_in'] = True
        st.session_state['link'] = result.get('link', '')  
        st.success(f"Logged in as: {result['firstName']}")
        st.switch_page("pages/WelcomePage.py")
    else:
        st.error("Incorrect username or password!")

    # Close the MongoDB connection
    client.close()


st.title("Login")

with st.form("my_form", clear_on_submit=True):
    st.text("Username:")
    username = st.text_input("Enter Username")
    st.text("Password:")
    password = st.text_input("Enter Password", type="password")
    login = st.form_submit_button("Log In")
    if login:
        check_credentials(username, password)