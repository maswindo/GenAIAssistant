import fitz
import streamlit as st
import json
import certifi
import os
from dotenv import load_dotenv, find_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit import session_state
from openai import OpenAI
from docx import Document
from io import BytesIO

###
#This class processes the currently logged in user's resume, parses and uploads it in JSON format to mongodb
###
load_dotenv('../.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.error("Environment variables are missing. Please check the .env file.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)


def resume_to_text(uploaded_file, file_type):
    text = ""

    if file_type == 'pdf':
        # For PDF files, use PyMuPDF (fitz)
        with fitz.open(stream=uploaded_file, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()

    elif file_type == 'vnd.openxmlformats-officedocument.wordprocessingml.document':
        # For DOCX files, wrap the bytes in BytesIO to simulate a file-like object
        file_stream = BytesIO(uploaded_file)
        doc = Document(file_stream)

        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

def connect_to_mongo():
    uri = os.environ.get('URI_FOR_Mongo')
    tlsCAFile = certifi.where()
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    return client['499']

def save_resume_to_mongo(extracted_data,username):
    db = connect_to_mongo()
    collection = db['files_uploaded']
    # Define the filter, update, and additional options
    filter_query = {'username': username}  # Filter by username
    update_fields = {'$set': {'resume_fields': extracted_data}}  # Update resume fields
    options = {
        'upsert': True,  # Create a document if no match is found
    }

    # Update the document in MongoDB
    collection.update_one(filter_query, update_fields, **options)
    client.close()

def extract_data(resume_data):
    prompt = (
        f"Extract structured data from the following resume text:\n\n{resume_data}\n\n"
        "Format the extracted information as a JSON object."
        "Categorize the extracted information into lists. You can create custom categories based on the content of the resume. "
        "Please do not introduce new information or categories not found in the provided resume."
        "Please do not relate or make inference upon the relationship of data unless it for the purpose to categorize them."
        "Please ensure that all relevant details are captured. Aim for comprehensive extraction and feel free to introduce new categories as needed."
        "Any lists generated should be formatted as an array in JSON, within whatever array or category they would normally appear."
        "Output the JSON object directly without using backticks or the 'json' label."
        "Be sure to include as lists, but not limited to: skills, hard skills, soft skills, subcategories of skills based on field|area|topic|position|etc., education, Objective or Summary Statement, Contact Information, Work Experience,Certifications and Licenses,Projects,Volunteer Experience,Awards and Honors,Publications and Presentations,Professional Affiliations,Languages, Extra-Curricular,Additional Information, Personal Projects, References,Patents, Portfolio, Professional Development and Training "
        "Here's an example format, but feel free to add new fields if necessary:\n\n"
        "{{\n"
        "  'Contact Information': {{\n"
        "      'Name': 'string',\n"
        "      'Email': 'string',\n"
        "      'Phone': 'string'\n"
        "  }},\n"
        "  'Education': [\n"
        "      {{'Degree': 'string', 'Institution': 'string', 'Year': 'string'}},\n"
        "  ],\n"
        "  'Work Experience': [\n"
        "      {{'Position': 'string', 'Company': 'string', 'Dates': 'string', 'Responsibilities': ['string']}}\n"
        "  ],\n"
        "  'Skills': [\n"
        "      {{'Hard Skills': ['string'], 'Soft Skills': ['string']\n"
        "  'Certifications': [{{'Name': 'string', 'Year': 'string'}}],\n"
        "  'Projects': [{{'Name': 'string', 'Description': 'string'}}],\n"
        "  'Languages': ['string']\n"
        "}}\n\n"
        "If any categories are not applicable, simply omit them."
    )
    behaviour = (
        "You are a resume extraction agent. Your job is to extract all the information from the resume. "
        "Do not introduce any new data or information that is not already provided in the resume."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt, "type": "json_object"},
            {"role": "system", "content": behaviour}
        ]
    )

    # Parse the assistant's reply as JSON
    extracted_data = response.choices[0].message.content

    # Attempt to convert the response into a JSON object
    try:
        json_data = json.loads(extracted_data)
    except json.JSONDecodeError:
        # If JSON decoding fails, return the raw text to inspect or handle further
        json_data = {"error": "Failed to parse JSON", "data": extracted_data}

    return json_data

def process_resume(resume_data,username):
        file_type = get_resume_type(username)
        type, subtype = file_type.split('/')
        resume = resume_to_text(resume_data,subtype)
        extracted_data = extract_data(resume)
        # Send extracted data to MongoDB
        save_resume_to_mongo(extracted_data,username)

def display_resume(uploaded_file):
    pdf_data = uploaded_file
    with fitz.open(stream=pdf_data, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    st.text_area("Resume Content", value=text)

@st.cache_resource(ttl=3600)
def connect_to_mongo():
    uri = os.getenv('URI_FOR_Mongo')
    return MongoClient(uri, server_api=ServerApi('1'))

@st.cache_data(ttl=3600)
def get_user_resume(username):
    client = connect_to_mongo()
    db = client['499']
    collection = db['files_uploaded']
    user = collection.find_one({'username': username})
    if user and 'data' in user:
        return user['data']
    return None

def get_resume_type(username):
    client = connect_to_mongo()
    db = client['499']
    collection = db['files_uploaded']
    user = collection.find_one({'username': username})
    if user and 'file_type' in user:
        return user['file_type']
    return None
