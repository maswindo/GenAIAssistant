import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import certifi
from pymongo.server_api import ServerApi
import secrets  # To generate unique keys
import pdfplumber
import pytesseract
from PIL import Image
import io
from langchain.schema import HumanMessage, SystemMessage

#######################################################################################################
# LOAD ENVIRONMENT VARIABLES AND SETUP OPENAI CLIENT
#######################################################################################################

load_dotenv()

# Set up OpenAI API key with error handling
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    st.error("Missing OpenAI API key. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Initialize GPT-4 Turbo model
chat = ChatOpenAI(model="gpt-4-turbo", temperature=0)

#######################################################################################################
# USER AUTHENTICATION AND GET USERNAME
#######################################################################################################

# Retrieve username from session state if user is logged in
if 'username' in st.session_state and st.session_state['username']:
    username = st.session_state['username']
else:
    st.error("You must be logged in to access this page.")
    st.stop()

#######################################################################################################
# TITLE AND USER INTERFACE FOR RESUME ENHANCEMENT PAGE
#######################################################################################################

# Title of the resume enhancement page
st.title("Enhance Your Resume with GPT-4 Turbo")

#######################################################################################################
# DATABASE CONNECTION FUNCTIONS
#######################################################################################################

# MongoDB setup to retrieve user data
def get_user_resume_from_db(username):
    # Connect to MongoDB
    uri = os.getenv('URI_FOR_Mongo')
    with MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1')) as client:
        db = client['499']
        collection = db['files_uploaded']

        # Query for the user's resume based on username
        user = collection.find_one({'username': username})
        if user and 'data' in user:
            return user['data']  # Assuming the data is stored as binary
    return None

#######################################################################################################
# FUNCTION TO INTERACT WITH GPT-4 TURBO
#######################################################################################################

def interact_with_gpt(prompt):
    try:
        # Create the messages list using Langchain's message classes
        messages = [
            SystemMessage(content="You are an expert career coach and professional resume writer."),
            HumanMessage(content=prompt)
        ]

        # Call the ChatOpenAI model
        response = chat(messages)

        # Extract and return the generated response content
        return response.content
    except Exception as e:
        st.error(f"Error interacting with GPT-4 Turbo: {e}")
        return ""

#######################################################################################################
# FUNCTION TO PROCESS RESUME DATA
#######################################################################################################

def process_resume_data(resume_data):
    """Process and extract text from binary resume data."""
    if isinstance(resume_data, bytes):
        return extract_text_from_file(resume_data)
    else:
        # Directly return if it's already text
        return resume_data

#######################################################################################################
# UTILITY FUNCTION TO EXTRACT TEXT FROM FILE
#######################################################################################################

def extract_text_from_file(file_data):
    try:
        # Convert binary data to a file-like object
        file_like = io.BytesIO(file_data)
        # Assuming PDF, handle it with pdfplumber and OCR if needed
        with pdfplumber.open(file_like) as pdf:
            resume_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    resume_text += page_text + "\n"
                else:
                    # Attempt OCR for non-readable text
                    image = page.to_image()
                    pil_image = image.original
                    ocr_text = pytesseract.image_to_string(pil_image)
                    if ocr_text:
                        resume_text += ocr_text + "\n"
        return resume_text
    except Exception as e:
        st.warning(f"Error extracting PDF: {e}")
        return None

#######################################################################################################
# RETRIEVE AND DISPLAY USER RESUME
#######################################################################################################

# Fetch resume from the database if not already in session state
if "resume" not in st.session_state or not st.session_state["resume"]:
    stored_resume = get_user_resume_from_db(username)
    if stored_resume:
        st.write("Debug: Resume found in database.")
        # Use centralized processing function to parse resume data
        resume_text = process_resume_data(stored_resume)
        st.session_state["resume"] = resume_text if resume_text else ""
    else:
        st.write("Debug: No resume found in database.")

# Ensure the resume in session state is in a readable format (process it if needed)
if "resume" in st.session_state and isinstance(st.session_state["resume"], bytes):
    st.session_state["resume"] = process_resume_data(st.session_state["resume"])

# Display the resume if available
if st.session_state.get("resume") and st.session_state["resume"].strip():
    st.subheader("Here is Your Current Resume:")
    st.text_area("", st.session_state["resume"], height=300)

    # Allow user to add a job description to tailor the enhancement
    job_description = st.text_area("Add a Job Description (optional):", "", height=150)

    # Step 1: Provide an initial summary of suggested changes
    if "detailed_summary" not in st.session_state:
        if st.button("Analyze Resume for Suggested Enhancements"):
            prompt = (f"Here is a resume:\n\n{st.session_state['resume']}\n\n"
                      f"Job Description:\n\n{job_description}\n\n"
                      f"Please provide a summary of the improvements you would suggest to enhance this resume, and why those changes would be beneficial.")
            detailed_summary = interact_with_gpt(prompt)
            st.session_state["detailed_summary"] = detailed_summary

    # Display suggested enhancements
    if "detailed_summary" in st.session_state:
        st.subheader("Suggested Enhancements:")
        st.text_area("", st.session_state["detailed_summary"], height=200, key="suggested_enhancements")

        # Step 2: Confirm if user wants to proceed with enhancements
        if "enhanced_resume" not in st.session_state:
            if st.button("Proceed with Enhancements"):
                prompt = (f"Here is a resume:\n\n{st.session_state['resume']}\n\n"
                          f"Job Description:\n\n{job_description}\n\n"
                          f"Please enhance the resume to make it more aligned with professional standards, and provide a detailed summary of what changes were made and why.")
                enhanced_resume = interact_with_gpt(prompt)
                st.session_state["enhanced_resume"] = enhanced_resume

    # Display enhanced resume
    if "enhanced_resume" in st.session_state:
        st.subheader("Enhanced Resume:")
        st.text_area("", st.session_state["enhanced_resume"], height=300, key="enhanced_resume")

        # Step 3: Provide additional suggestions for career improvement
        if "career_suggestions" not in st.session_state:
            if st.button("Get Career Improvement Suggestions"):
                prompt = (f"Based on the enhanced resume:\n\n{st.session_state['enhanced_resume']}\n\n"
                          f"Please provide additional suggestions for skills, projects, or experiences that could further improve this user's career prospects, including an 'X-Factor' that could help them stand out among top-level candidates.")
                career_suggestions = interact_with_gpt(prompt)
                st.session_state["career_suggestions"] = career_suggestions

    # Display career improvement suggestions
    if "career_suggestions" in st.session_state:
        st.subheader("Career Improvement Suggestions (Including X-Factor):")
        st.text_area("", st.session_state["career_suggestions"], height=200, key="career_suggestions")
else:
    st.warning("No resume found for the user. Please upload a resume first.")

#######################################################################################################
# UPLOAD AND DISPLAY NEW RESUME
#######################################################################################################

st.subheader("Upload a New Resume:")
uploaded_file = st.file_uploader("Upload your resume (as a .txt, .pdf, or .docx):", type=["txt", "pdf", "docx"])

if uploaded_file:
    # Check the file type and read the resume
    file_type = uploaded_file.type
    resume_text = ""
    if file_type == "text/plain":
        resume_text = uploaded_file.getvalue().decode("utf-8")
    elif file_type == "application/pdf":  # Handle .pdf file
        resume_text = ""
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        resume_text += page_text + "\n"
                    else:
                        # Attempt OCR for non-readable text
                        image = page.to_image()
                        pil_image = image.original
                        ocr_text = pytesseract.image_to_string(pil_image)
                        if ocr_text:
                            resume_text += ocr_text + "\n"
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {e}")
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  # Handle .docx file
        from docx import Document
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            if para.text:
                resume_text += para.text + "\n"

    # Store the resume text in the session state and display it
    st.session_state["resume"] = resume_text if resume_text else ""

    st.subheader("Uploaded Resume:")
    st.text_area("", resume_text)
