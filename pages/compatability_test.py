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
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, openai_api_key=os.getenv('OPENAI_API_KEY'))

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
            # Set up prompt template for LLM with personalized context and experience calculation
            #TODO -
            prompt_template = PromptTemplate(
                input_variables=['resume', 'job_description'],
                template="""
                You are a job recruiter evaluating the candidate's compatibility with the role of the job title shown in
                the job description data. Your task is to assess how well the candidate’s skills, qualifications, and 
                experience align with the job requirements based on the provided resume and job description. Consider 
                the following factors for analyzing compatibility: level of relevant projects, years of experience, 
                listed skill set, and qualifications such as certificates, degrees, and education relevant to the job 
                posting. If you find the candidate missing requirements for the job posting, you are also experienced in
                providing assistance to help the candidate find resources to assist them to being qualified.

                Resume Data:
                {resume}

                Job Description Data:
                {job_description}

                Instructions:
                1. List the specific skills and qualifications from the resume that match the job requirements. For
                   non-technical skills, consider how their previous experience can be applied to those non-technical skill
                   requirements.
                2. Identify any missing skills, qualifications, or experience in the resume compared to the job description.
                3. Calculate the candidate's total experience in each relevant job listed, based on the start and end dates. 
                   Experience dates may be provided in various formats (e.g., "March 2015 – April 2019," "2017-2021," 
                   "July 2018 - Present"). Provide each job’s experience length in years and months, and then calculate 
                   the total relevant experience. Remember the current/present year is 2024.
                4. Provide a compatibility score between 0 and 100 based on the alignment of skills, qualifications, 
                   and experience. Weigh experience at 20% (if they have the required amount of experience or more, give
                   them the full points), qualifications at 20%, and listed skill set at 60%. Provide them the fraction
                   they earned from each category in your response (ex. Experience 15/20 Qualifications 15/20 Skills 60/60).
                   A score of 85 or above indicates a strong match.
                5. Highlight any areas where the candidate may improve to better match the job requirements. If the user
                   is lacking certain skills or requirements provide where the user can learn those skills, and include
                   direct links to the suggestions, this can include programming language courses, certification websites,
                   coding bootcamps, and more.
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
