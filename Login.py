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
        st.session_state["username"] = username
        st.session_state['link'] = result['link']
        st.success(f"Logged in as: {username}")
        st.switch_page("pages/chatbot.py")
    else:
        st.error("Incorrect username or password!")

    # Close the MongoDB connection
    client.close()


st.title("Login")
st.sidebar.page_link("Login.py", label="Log In")
st.sidebar.page_link("pages/Register.py", label="Register")

with st.form("my_form", clear_on_submit=True):
    st.text("Username:")
    username = st.text_input("Enter Username")
    st.text("Password:")
    password = st.text_input("Enter Password", type="password")
    login = st.form_submit_button("Log In")
    if login:
        check_credentials(username, password)
