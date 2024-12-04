import streamlit as st
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os
import certifi
from tools.JobPostProcessor import process_job_listing
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from tools.ResumeProcessor import process_resume
from tools.ResumeProcessor import get_user_resume
#from tools.ProxyCurlCompany import companies_linkedin_batch
from tools.InternalAnalytics import get_applicant_modes, getJobPostAnalytics, getLocationMap

# Load variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
load_dotenv('../.env')
username = st.session_state.get('username')
# Initialize Database and Session Variables
load_dotenv('../.env',override=True)
uri = os.environ.get('URI_FOR_Mongo')
if not uri:
    st.error("Missing Environment Variables, check .env file.")
    st.stop()

tlsCAFile = certifi.where()
try:
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    db = client['499']
    collection_users = db['files_uploaded']
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


#Page Title
st.title("Developer Dashboard - Internal Use Only")

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

#Function 1: Active User Resume Processing
st.subheader("Resume Processor: Stores Active User's Resume to Database in JSON format")
if st.button("Process Resume"):
    if username:
        process_resume(get_user_resume(username),username)
        st.write("Process Complete")
    else:
        st.write("You must be logged in to perform this action")

#Function 2: Batch Database User Resume Processing
st.subheader("Process All Un-Processed User Resumes in Database")
if st.button("Process All Users"):
    users = collection_users.find({
        "resume_fields": {"$exists": False}
        },
        {
            '_id': 0, 'username': 1
        }
    )
    for user in users:
        process_resume(get_user_resume(user['username']),user['username'])

#Function 3: Batch Local Job Listing Processing
st.subheader("Job Listings Processor: Stores Jobs to Database in JSON Format")
if st.button("Extract Job Details"):
    st.write("Extracts data from all .txt files in 'Jobs' folder located in source directory")
    process_jobs()
    st.write("Process Complete")

#Function 4:Batch Company LinkedIn Gathering
#st.subheader("Batch Company LinkedIn Gathering from Jobs Database")
#st.write("Works but Requires ProxyCurl Credits")
#if(st.button("Get Companies LinkedIn Data")):
#    companies_linkedin_batch()

#Function 5: Map of Users and Job Listings
st.plotly_chart(getLocationMap())
#Function 6:Job Post Applicant Analytics
job_app_tuple = getJobPostAnalytics()
with st.expander("Jobs with Applicants List", expanded=False):
    if job_app_tuple:
        for job_title, company_name, applicants, location in job_app_tuple:
            applicant_modes = get_applicant_modes(applicants)
            st.subheader(job_title)
            st.write(company_name)
            st.write(location)
            st.write(f'No. of Applicants: {len(applicants)}')
            st.write('Post Popularity: ')
            st.write('Applicants Profile')
            st.write(f'Most common skill: {applicant_modes[1]}')
            st.write(f'Most common degree: {applicant_modes[3]}')
            st.write(f'Most common location: {applicant_modes[0]}')
            st.write(f'Most common previous occupation: {applicant_modes[2]}')
            st.write('---')