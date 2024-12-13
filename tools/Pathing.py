from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
# Load environment variables
load_dotenv('../.env')
openai = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def connect_to_mongo():
    uri = os.environ.get('URI_FOR_Mongo')
    tlsCAFile = certifi.where()
    db = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    return db['499']

st.cache_data(ttl=3600)
def getJobs():
    db = connect_to_mongo()
    collection = db['jobs']
    return list(collection.find())

def getResumeData(username):
    db = connect_to_mongo()
    collection = db['files_uploaded']
    user_data = collection.find({'username': username}, {'_id': 0, 'resume_fields': 1})
    return list(user_data)

@st.cache_data(ttl=3600)
def get_user_path():
    username = st.session_state.get('username')
    resume = getResumeData(username)
    jobs = getJobs()
    prompt = (
        f"Based on this JSON structured resume: {resume} Provide two career paths this person should take."
        f"Structure the response in a way that communicates the pathing reasonably and legibly."
        f"Select from this list of job listings that best fit the career paths you've decided are optimal: {jobs} and list them in the relevant career path under the title Jobs Available Now."
    )
    behaviour = (
        "You are a career advisor tasked with outlining the possible paths available to a person given the unique information provided in their resume data"
        "Your goal is to provide precise information that details steps they could take in their career path along with relevant metrics, explanations, and requirements for each step along with a time evaluation of each step and sub-step."
        "All of your information must critically look at each piece of data in their resume and make suggestion related to that data and draw conclusions based on it such as location, experience etc."
        "Use all information available and knowledge available such as macroeconomic data, labor data, etc. to provide suggestion are explanations that would be of benefit to the user."
        "Structure it formatted and title it as so: 'Consider {overarching occupation} Path'"
    )
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": behaviour}
        ]
    )

    # Extract the assistant's reply
    occupation_data = response.choices[0].message.content.strip()

    return occupation_data
