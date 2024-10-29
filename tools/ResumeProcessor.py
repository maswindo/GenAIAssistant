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

#Agent Prompts

triaging_system_prompt = """You are a Triaging Agent. Your role is to assess the user's query and route it to the relevant agents. The agents available are:
    - Resume Data Extraction Agent: Extracts data from a resume

    User the send_resume_to_agents tool to forward the user's resume to the relevant agents."""

extracting_system_prompt = (
    """You are a Resume Data Extraction Agent. Your role is to extract resume data using the following tools:
    - extract_data
    
    Please do not introduce any new information that is not present in the user's resume."""
)

triage_tools = [
    {
        "type": "function",
        "function": {
            "name": "send_resume_to_agents",
            "description": "Sends the user query to relevant agents based on their capabilities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of agent names to send the query to."
                    },
                    "resume": {
                        "type": "string",
                        "description": "The user resume to send."
                    }
                },
                "required": ["agents", "resume"]
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
            "description": "Extracts data from a resume by creating lists categorized by common resume fields, including, but not limited to: skills, education, Objective or Summary Statement, Contact Information, Work Experience,Certifications and Licenses,Projects,Volunteer Experience,Awards and Honors,Publications and Presentations,Professional Affiliations,Languages ",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The resume to extract data from. Should be in a suitable format such as text."
                    }
                },
                "required": ["data"],
                "additionalProperties": False
            }
        },
        "strict": True
    }
]
def resume_to_text(uploaded_file):
    pdf_data = uploaded_file
    with fitz.open(stream=pdf_data, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

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

# Main function to process resume data
def process_resume(resume,conversation_messages=[]):
    resume_data = resume_to_text(resume)
    user_message = {"role": "user", "content": resume_data}
    conversation_messages.append(user_message)

    # Initialize the triaging process with the triaging prompt
    messages = [{"role": "system", "content": triaging_system_prompt}]
    messages.extend(conversation_messages)

    # Get response from the model, using triage tools for initial sorting
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        tools=triage_tools,
    )

    # Append tool calls for record-keeping and debugging
    conversation_messages.append([tool_call.function for tool_call in response.choices[0].message.tool_calls])

    # Process each tool call from the response
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == 'send_resume_to_agents':
            agents = json.loads(tool_call.function.arguments)['agents']
            resume = json.loads(tool_call.function.arguments)['resume']

            # Send the resume to the appropriate agent(s) based on triage
            for agent in agents:
                if agent == "Resume Data Extraction Agent":
                    handle_data_extracting_agent(resume, conversation_messages)

    return conversation_messages


def extract_data(resume_data):
    prompt = (
        f"Extract structured data from the following resume text:\n\n{resume_data}\n\n"
        "Format the extracted information as a JSON object."
        "Categorize the extracted information into lists. You can create custom categories based on the content of the resume. "
        "Please do not introduce new information or categories not found in the provided resume."
        "Please do not relate or make inference upon the relationship of data unless it for the purpose to categorize them"
        "Please ensure that all relevant details are captured. Aim for comprehensive extraction and feel free to introduce new categories as needed."
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
        "  'Skills': ['string'],\n"
        "  'Certifications': [{{'Name': 'string', 'Year': 'string'}}],\n"
        "  'Projects': [{{'Name': 'string', 'Description': 'string'}}],\n"
        "  'Languages': ['string']\n"
        "}}\n\n"
        "If any categories are not applicable, simply omit them."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt, "type": "json_object"}
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


def execute_tool(tool_calls, messages):
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        try:
            tool_arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            print("Error parsing tool arguments")
            continue

        # Check for the specific tool and call the associated function
        if tool_name == 'extract_data':
            try:
                # Call extract_data to get structured JSON output
                extracted_data = extract_data(tool_arguments['data'])

                # Send extracted data to MongoDB
                save_resume_to_mongo(extracted_data)

                # Append extracted data to the messages list for reference
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({"extracted_data": extracted_data})
                })
            except Exception as e:
                print("Error in extract_data:", e)
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({"error": "Extraction failed", "details": str(e)})
                })

def handle_data_extracting_agent(resume, conversation_messages):
    # Initialize messages with the triaging prompt
    messages = [{"role": "system", "content": extracting_system_prompt}]
    messages.append({"role": "user", "content": resume})

    # Generate a response from the triaging system
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or whatever model you're using
        messages=messages,
        temperature=0,
        tools=extraction_tools  # Use the tools defined for triaging
    )

    # Append all function calls to the conversation_messages
    conversation_messages.append([tool_call.function for tool_call in response.choices[0].message.tool_calls])

    # Execute tools using execute_tool function
    execute_tool(response.choices[0].message.tool_calls, conversation_messages)

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