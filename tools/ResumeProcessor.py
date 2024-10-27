import fitz
import streamlit as st
import spacy
import certifi
import os
import io
import nltk;
import subprocess
from pyresparser import ResumeParser
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from streamlit import session_state

load_dotenv('../.env')

# Function to initialize spaCy
def initialize_spacy():
    model_name = "en_core_web_sm"
    try:
        nlp = spacy.load(model_name)
    except OSError:
        print(f"{model_name} not found. Installing...")
        subprocess.call(['python', '-m', 'spacy', 'download', model_name])
        nlp = spacy.load(model_name)
    return nlp


# Function to initialize NLTK
def initialize_nltk():
    # Check for NLTK stopwords
    try:
        nltk.data.find('corpora/stopwords.zip')
    except LookupError:
        nltk.download('stopwords')

    # Check for NLTK words dataset
    try:
        nltk.data.find('corpora/words.zip')
    except LookupError:
        nltk.download('words')

def connect_to_mongo():
    uri = os.environ.get('URI_FOR_Mongo')
    tlsCAFile = certifi.where()
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    return client['499']

def save_resume_to_mongo(extracted_data):
    db = connect_to_mongo()
    collection = db['files_uploaded']
    username = st.session_state.get('username')
    # Define the filter, update, and additional options
    filter_query = {'username': username}  # Filter by username
    update_fields = {'$set': {'resume_fields': extracted_data}}  # Update resume fields
    options = {
        'upsert': True,  # Create a document if no match is found
    }

    # Update the document in MongoDB
    collection.update_one(filter_query, update_fields, **options)

def extract_data(pdf_data,nlp):
    temp_resume_path = "temp_resume.pdf"
    with open(temp_resume_path, "wb") as f:
        f.write(pdf_data)  # Save the file temporarily for PyResparser

    data = ResumeParser("temp_resume.pdf").get_extracted_data()
    save_resume_to_mongo(data)
    os.remove(temp_resume_path)

def process_resume(uploaded_file):
    nlp = initialize_spacy()
    initialize_nltk()
    pdf_data = uploaded_file
    extract_data(pdf_data,nlp)


def display_resume(uploaded_file):
    pdf_data = uploaded_file
    with fitz.open(stream=pdf_data, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    st.text_area("Resume Content", value=text)

def get_user_resume(username):
    uri = os.getenv('URI_FOR_Mongo')
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['499']
    collection = db['files_uploaded']
    user = collection.find_one({'username': username})
    if user and 'data' in user:
        return user['data']
    return None