from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
from dotenv import load_dotenv
import os
import certifi

###
#This class lists all jobs in mongodb database
###
# Init of Database and Session Variables
load_dotenv('../.env')
uri = os.environ.get('URI_FOR_Mongo')
tlsCAFile = certifi.where()
client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
db = client['499']
collection = db['jobs']
job_postings = collection.find({})
user_id = st.session_state.get('username')

# Front End
st.title('Job Listings')

if job_postings:
    # Add a search bar
    search_query = st.text_input("Search for a job title", "")

    # Filter the job postings based on the search query
    filtered_jobs = []
    for job in job_postings:
        job_details = job.get("job_details", {})
        job_title = job_details.get("Job Title", "").lower()

        # Check if the search query matches the job title
        if search_query.lower() in job_title:
            filtered_jobs.append(job)

    # Display each filtered job posting
    if filtered_jobs:
        for job in filtered_jobs:
            job_details = job.get("job_details", {})
            job_title = job_details.get("Job Title", "No Job Title Available")
            company_name = job_details.get("Company Name", "No Company Name Available")
            location = job_details.get("Location", "No Location Available")
            employment_type = job_details.get("Employment Type", "No Employment Type Available")
            summary = job_details.get("Job Summary", "No Summary Available")

            # Check if Multiple Employment types
            if isinstance(employment_type, list):
                employment_type = ', '.join(employment_type)

            st.header(job_title)
            st.subheader(company_name)
            st.write(f"**Location:** {location}")
            st.write(f"**Employment Type:** {employment_type}")
            st.write(f"**Summary:** {summary}")

            if st.button("Apply Here", key=f"apply_button_{job['_id']}"):
                if user_id == "Anonymous" or not user_id:
                    st.write("You must login to perform this action")
                else:
                    filter_query = {
                        '_id': job["_id"]
                    }
                    update = {
                        "$addToSet": {
                            "applicants": user_id
                        }
                    }
                    collection.update_one(filter_query, update)
                    st.write("Applied")

            st.write("---")
    else:
        st.write("No job postings match your search query.")
else:
    st.write("No job postings available.")
