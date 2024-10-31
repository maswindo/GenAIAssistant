import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os

from tools.JobPostProcessor import process_job_listing
from tools.ResumeProcessor import process_resume
from tools.ResumeProcessor import get_user_resume

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load environment variables
load_dotenv('../.env')

#Page Title
st.title("Insights")

folder_name = "Jobs"

def process_jobs():
    for filename in os.listdir(folder_name):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_name, filename)
            with open(file_path, 'r') as file:
                content = file.read()
                process_job_listing(content)

if st.button("Generate Insights"):
    process_resume(get_user_resume(st.session_state.get('username')))

if st.button("Extract Job Details"):
   process_jobs()


