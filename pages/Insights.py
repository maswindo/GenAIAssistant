import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os
from tools.ResumeProcessor import process_resume
from tools.ResumeProcessor import get_user_resume

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load environment variables
load_dotenv('../.env')

#Page Title
st.title("Insights")

if st.button("Generate Insights"):
    process_resume(get_user_resume(st.session_state.get('username')))
