from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import certifi
import os
from langchain.schema import SystemMessage, HumanMessage
from docx import Document
import pdfplumber
import io


load_dotenv()

# Database connection
def load_resume_from_db(username):
    uri = os.getenv('URI_FOR_Mongo')
    if not uri:
        raise ValueError("MongoDB URI not set. Please set 'URI_FOR_Mongo' in the environment variables.")

    with MongoClient(uri, tlsCAFile=certifi.where()) as client:
        db = client['499']
        collection = db['files_uploaded']
        user = collection.find_one({'username': username})
        if user and 'data' in user:
            return user['data']
    return None

# Text extraction
def extract_text_from_file(file_data):
    try:
        file_like = io.BytesIO(file_data)
        # Check if file is a DOCX
        if file_data[:4] == b'\x50\x4b\x03\x04':  # DOCX magic number
            document = Document(file_like)
            return "\n".join([para.text for para in document.paragraphs])
        # Otherwise, assume it's a PDF
        else:
            with pdfplumber.open(file_like) as pdf:
                resume_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        resume_text += page_text + "\n"
                return resume_text
    except Exception as e:
        return None

# Run agents

def run_agent(agent_name, resume_text, concise):
    # Define agent prompts for concise/detailed feedback
    agents = {
        "Clarity": {
            "system": "You are an expert in enhancing resume clarity.",
            "user": f"Analyze this resume text for clarity improvements: {resume_text}"
        },
        "Impact": {
            "system": "You are an expert in enhancing the impact of resumes.",
            "user": f"Enhance the impact of this resume text by emphasizing achievements: {resume_text}"
        },
        # Add other agents as needed
        "Visual Scan": { ... },
        "ATS Compatibility": { ... },
        "Tailoring": { ... },
        "Branding": { ... }
    }
    if agent_name not in agents:
        return f"Agent '{agent_name}' not found."

    prompt = agents[agent_name]
    chat = ChatOpenAI(model="gpt-4-turbo")
    messages = [
        SystemMessage(content=prompt['system']),
        HumanMessage(content=prompt['user'])
    ]

    try:
        response = chat(messages)
        return response.content.strip()
    except Exception as e:
        return f"Error from agent '{agent_name}': {e}"


def run_all_agents(resume_text, concise):
    agent_names = [
        "Clarity", "Impact", "Experience Prioritization", "Skills Matching",
        "Visual Scan", "ATS Compatibility", "Tailoring", "Branding"
    ]
    results = {}
    for agent_name in agent_names:
        results[agent_name] = run_agent(agent_name, resume_text, concise)
    return results
