import streamlit as st
import json
from tools.ResumeProcessor import process_resume, get_user_resume  # Resume processing
from tools.JobPostProcessor import process_job_listing  # Job description processing
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import pdfplumber
import pytesseract
import io

# Initialize OpenAI LLM for compatibility scoring
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5, openai_api_key=os.getenv('OPENAI_API_KEY'))

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

# Fetch resume from MongoDB using `ResumeProcessor` logic
resume_data = get_user_resume(username)

if resume_data:
    # Process the resume to extract structured JSON data
    #structured_resume = process_resume(resume_data)

    #Process the resume to text
    resume_text = process_resume_data(resume_data)

    # Display the user's resume data in text format
    st.subheader("Processed Resume Data:")
    st.text_area("Resume Content", resume_text, height=400)

    # Allow user to input a LinkedIn job URL for comparison
    job_url = st.text_input("Paste the LinkedIn job URL here:")

    if job_url and st.button("Analyze Compatibility"):
        structured_resume = process_resume(resume_data)
        # Fetch and process the job description
        job_data = process_job_listing(job_url)  # Get structured data from JobPostProcessor

        # Verify job description retrieval
        if not job_data:
            st.write("The job description could not be retrieved. Please check the job URL.")
        else:
            # Display structured job data
            #st.subheader("Processed Job Description Data:")
            #st.json(job_data)  # Display as JSON for clarity
            # Prepare structured input for compatibility analysis
            combined_input = {
                "resume": structured_resume,
                "job_description": job_data
            }

            # Set up prompt template for LLM
            prompt_template = PromptTemplate(
                input_variables=['resume', 'job_description'],
                template="""
                Given the structured resume and job description below, analyze the user's compatibility for the role.

                Resume Data:
                {resume}

                Job Description Data:
                {job_description}

                Instructions:
                1. List the specific skills from the resume that match the job requirements.
                2. Identify any missing skills, qualifications, or experience in the resume compared to the job description.
                3. Provide a compatibility score between 0 and 100 based on the alignment of skills, qualifications, and experience.
                4. Highlight any areas where the candidate may improve to better match the job requirements.
                """
            )

            # Run the LLM with structured input data
            chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)
            result = chain.invoke(combined_input)  # Use `combined_input` as it now matches the template

            # Display the compatibility score and details
            st.write("Compatibility Analysis Result:")
            st.write(result.get('text'))
else:
    st.write("No resume found for the given username.")
