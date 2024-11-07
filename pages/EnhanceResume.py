# Your capstone code looks great! Here are some suggestions and updates to address your concerns.

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
from docx import Document  # To handle .docx files
from fpdf import FPDF  # To generate PDF output

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
        return response.content.strip()
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
        if file_data[:4] == b'\x50\x4b\x03\x04':  # Check if it's a .docx file
            return extract_text_from_docx(file_like)
        else:  # Assume PDF
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
        st.warning(f"Error extracting text from file: {e}")
        return None

#######################################################################################################
# FUNCTION TO EXTRACT TEXT FROM .DOCX FILES
#######################################################################################################

def extract_text_from_docx(file_like):
    try:
        document = Document(file_like)
        docx_text = "\n".join([para.text for para in document.paragraphs])
        return docx_text
    except Exception as e:
        st.warning(f"Error extracting DOCX: {e}")
        return None

######################################################################################################
# FUNCTION TO GENERATE PDF FROM TEXT
#######################################################################################################

def generate_pdf_from_text(text, filename="enhanced_resume.pdf"):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Split text into lines to avoid overflowing the PDF page
    for line in text.splitlines():
        if pdf.get_string_width(line) > 190:  # Check if the line is too long
            words = line.split()
            current_line = ""
            for word in words:
                if pdf.get_string_width(current_line + word + " ") < 190:
                    current_line += word + " "
                else:
                    pdf.cell(200, 10, txt=current_line, ln=True)
                    current_line = word + " "
            if current_line:
                pdf.cell(200, 10, txt=current_line, ln=True)
        else:
            pdf.cell(200, 10, txt=line, ln=True)

    # Save the PDF file
    pdf.output(filename, dest='F').encode('latin1', 'replace')  # Handle encoding errors

    return filename

#######################################################################################################
# FUNCTION TO GENERATE PDF OUTPUT FOR ENHANCED RESUME
#######################################################################################################

def generate_pdf_resume(text, output_filename="enhanced_resume.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    if not text.strip():
        pdf.cell(0, 10, "No content available to generate the resume.", ln=True)
    else:
        for line in text.split("\n"):
            if line.strip():
                if pdf.get_string_width(line) > pdf.w - 2 * pdf.l_margin:
                    # Split long lines into smaller chunks
                    words = line.split(" ")
                    current_line = ""
                    for word in words:
                        if pdf.get_string_width(current_line + word + " ") < pdf.w - 2 * pdf.l_margin:
                            current_line += word + " "
                        else:
                            pdf.multi_cell(0, 10, current_line.strip())
                            current_line = word + " "
                    if current_line:
                        pdf.multi_cell(0, 10, current_line.strip())
                else:
                    pdf.multi_cell(0, 10, line)
    pdf.output(output_filename)
    return output_filename

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
            prompt = f"Resume Text: {st.session_state['resume']}\n"
            if job_description.strip():
                prompt += f"Job Description: {job_description}\n"
            prompt += ("As an expert career coach, provide a detailed analysis highlighting:\n"
                       "1. The strengths of the resume.\n"
                       "2. Actionable steps to enhance the resume for better alignment.")
            detailed_summary = interact_with_gpt(prompt)
            st.session_state["detailed_summary"] = detailed_summary

    # Display suggested enhancements
    if "detailed_summary" in st.session_state:
        st.subheader("Suggested Enhancements:")
        st.text_area("", st.session_state["detailed_summary"], height=200, key="suggested_enhancements")

        # Step 2: Confirm if user wants to proceed with enhancements
        if "enhanced_resume" not in st.session_state:
            if st.button("Proceed with Enhancements"):
                prompt = f"Resume Text: {st.session_state['resume']}\n"
                if job_description.strip():
                    prompt += f"Job Description: {job_description}\n"
                prompt += ("Rewrite the resume with:\n"
                           "1. Bullet points in professional language, making them more quantifiable.\n"
                           "2. Highlighted skills, leadership roles, and gaps to bridge.")
                enhanced_resume = interact_with_gpt(prompt)
                st.session_state["enhanced_resume"] = enhanced_resume

    # Display enhanced resume
    if "enhanced_resume" in st.session_state:
        st.subheader("Enhanced Resume:")
        st.text_area("", st.session_state["enhanced_resume"], height=300, key="enhanced_resume")

        # Generate PDF option
        if st.button("Download Enhanced Resume as PDF"):
            pdf_filename = generate_pdf_resume(st.session_state["enhanced_resume"])
            with open(pdf_filename, "rb") as f:
                st.download_button(label="Download PDF", data=f, file_name=pdf_filename, mime="application/pdf")

        # Step 3: Provide additional suggestions for career improvement
        if "career_suggestions" not in st.session_state:
            if st.button("Get Career Improvement Suggestions"):
                prompt = (f"Enhanced Resume: {st.session_state['enhanced_resume']}\n"
                          "Provide suggestions for career growth, including skills to acquire.")
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
    # Save or process the uploaded resume as needed
    if file_type == "text/plain":
        new_resume = uploaded_file.read().decode("utf-8")
    else:
        new_resume = uploaded_file.read()