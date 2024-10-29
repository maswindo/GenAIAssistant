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

load_dotenv('../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Agent Prompts

triaging_system_prompt = """You are a Triaging Agent. Your role is to assess the user's query and route it to the relevant agents. The agents available are:
    - Resume Data Extraction Agent: Extracts data from a resume

    User the send_resume_to_agents tool to forward the user's resume to the relevant agents."""

extracting_system_prompt = (
    """You are a Job Data Extraction Agent. Your role is to extract job data using the following tools:
    - extract_data

    Please do not introduce any new information that is not present in the job data."""
)

triage_tools = [
    {
        "type": "function",
        "function": {
            "name": "send_job_to_agents",
            "description": "Sends the user query to relevant agents based on their capabilities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of agent names to send the query to."
                    },
                    "job": {
                        "type": "string",
                        "description": "The job to send."
                    }
                },
                "required": ["agents", "job"]
            }
        },
        "strict": True
    }
]
extraction_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_data",
            "description": "Extracts data from a job listing by creating a JSON object populated by arrays categorized by common resume fields, including, but not limited to: skills, education, Objective or Summary Statement, Contact Information, Work Experience,Certifications and Licenses,Projects,Volunteer Experience,Awards and Honors,Publications and Presentations,Professional Affiliations,Languages ",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The job listing to extract data from. Should be in a suitable format such as text."
                    }
                },
                "required": ["data"],
                "additionalProperties": False
            }
        },
        "strict": True
    }
]

def connect_to_mongo():
    uri = os.environ.get('URI_FOR_Mongo')
    tlsCAFile = certifi.where()
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    return client['499']

def save_job_details(extracted_data,job_id):
    db = connect_to_mongo()
    collection = db['jobs']
    # Define the filter, update, and additional options
    filter_query = {'job_id': job_id}  # Filter by job_id
    update_fields = {'$set': {'job_details': extracted_data}}  # Update resume fields
    options = {
        'upsert': True,  # Create a document if no match is found
    }

    # Update the document in MongoDB
    collection.update_one(filter_query, update_fields, **options)
