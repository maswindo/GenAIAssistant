import streamlit as st
from tools.ProxyCurlJob import scrape_job  # Still using job scraping
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from pymongo import MongoClient
import certifi
from pymongo.server_api import ServerApi
import pdfplumber
import pytesseract
import io

# Initialize OpenAI LLM for compatibility scoring
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=os.getenv('OPENAI_API_KEY'))

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
# FUNCTION TO PROCESS RESUME DATA INTO TEXT
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
# RESUME-BASED JOB COMPATIBILITY ANALYSIS
#######################################################################################################

# Fetch resume from MongoDB using `EnhanceResume` logic
resume_data = get_user_resume_from_db(username)

if resume_data:
    # Process the resume to extract text
    resume_text = process_resume_data(resume_data)

    # Display the user's resume
    st.subheader("Here is Your Uploaded Resume:")
    st.text_area("Resume Content", resume_text, height=300)

    # Allow user to input a LinkedIn job URL for comparison
    job_url = st.text_input("Paste the LinkedIn job URL here:")

    if job_url and st.button("Analyze Compatibility"):
        # Fetch job description data
        job_data = scrape_job(job_url)
        job_description = job_data.get('description', "")

        # Combine resume and job description data for LLM input
        combined_input = f"""
        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Instructions:
        Analyze the resume and job description for compatibility. Specifically:
        - Match the skills listed in the resume against the skills required in the job description.
        - Compare the level of experience and qualifications in the resume against the job's requirements.
        - Provide a compatibility score between 0 and 100, where 0 means no match and 100 means a perfect match.
        - Additionally, explain which skills or qualifications match and where the gaps are.
        """
        # Set up the prompt template for the LLM
        prompt_template = PromptTemplate(
            input_variables=['information'],
            template="""
            Given the resume and job description below, analyze the user's compatibility for the role.
            Provide a score between 0 and 100 based on how well the user's skills, qualifications, and experience align with the job requirements.
            {information}
            """
        )

        # Create the chain and run the LLM
        chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)
        result = chain.invoke({"information": combined_input})

        # Display the compatibility score and details
        st.write("Compatibility Analysis Result:")
        st.write(result.get('text'))  # This should contain the compatibility score and relevant details
else:
    st.write("No resume found for the given username.")
