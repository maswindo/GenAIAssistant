import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os
from tools.JobPostProcessor import process_job_listing
from tools.ResumeProcessor import process_resume
from tools.ResumeProcessor import get_user_resume

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load variables
load_dotenv('../.env')
username = st.session_state.get('username')

#Page Title
st.title("Developer Dashboard")

#Functions

def process_jobs():
    for filename in os.listdir("Jobs"):
        if filename.endswith(".txt"):
            file_path = os.path.join("Jobs", filename)
            with open(file_path, 'r') as file:
                content = file.read()
                process_job_listing(content)

#Front End
st.subheader("Internal Analytics")


st.subheader("Resume Processor: Stores Active User's Resume to Database in JSON format")
if st.button("Process Resume"):
    if username:
        process_resume(get_user_resume(username))
        st.write("Process Complete")
    else:
        st.write("You must be logged in to perform this action")

st.subheader("Job Listings Processor: Stores Jobs to Database in JSON Format")
if st.button("Extract Job Details"):
    st.write("Extracts data from all .txt files in 'Jobs' folder located in source directory")
    process_jobs()
    st.write("Process Complete")

