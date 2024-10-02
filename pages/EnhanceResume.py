import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load environment variables
load_dotenv()

# Title of the resume enhancement page
st.title("Enhance Your Resume with GPT-3.5 Turbo")

# Option 1: User uploads a new resume
uploaded_file = st.file_uploader("Upload your resume (as a .txt or .pdf):")

# Function to enhance the resume and provide a detailed summary of changes
def enhance_resume_with_gpt35_turbo(resume_text, job_description=None):
    # Prepare the prompt with or without the job description
    if job_description:
        prompt = (f"Here is a resume:\n\n{resume_text}\n\n"
                  f"Based on this job description:\n\n{job_description}\n\n"
                  "Please enhance the resume to make it more aligned with the job description, "
                  "and provide a detailed summary of what changes were made and why.")
    else:
        prompt = (f"Here is a resume:\n\n{resume_text}\n\n"
                  "Please enhance the resume and provide a detailed summary of what changes were made and why.")

    # Call the GPT model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert career coach and professional resume writer. Your task "
                                          "is to refine resumes based on the user's provided experience"
                                          "and job description while maintaining complete honesty and integrity. "
                                          "Ensure that you don't create or invent new experiences or projects."
                                          "Your focus is on improving clarity, readability, and professionalism by "
                                          "enhancing the language, formatting, and the way achievements are "
                                          "highlighted."
                                          "When optimizing resumes for a specific job description, prioritize "
                                          "highlighting relevant skills and experiences the user already possesses, "
                                          "but never fabricate them."
                                          "Additionally, if you identify any gaps in the user's experience that may "
                                          "be important for the job, suggest potential projects they could work on to "
                                          "fill those gaps in a separate suggestion section."},
            {"role": "user", "content": prompt}
        ]
    )

    # Try to extract the detailed summary and the enhanced resume from the response
    response_text = response.choices[0].message.content

    # Check if "Enhanced Resume:" exists in the response, and split accordingly
    if "Enhanced Resume:" in response_text:
        detailed_summary, enhanced_resume = response_text.split("Enhanced Resume:", 1)
        detailed_summary = detailed_summary.strip()
        enhanced_resume = enhanced_resume.strip()
    else:
        # Handle cases where the expected format is not found
        detailed_summary = response_text.strip()
        enhanced_resume = "Unable to extract enhanced resume from the response."

    return detailed_summary, enhanced_resume

if uploaded_file:
    # Check the file type and read the resume
    file_type = uploaded_file.type
    if file_type == "text/plain":  # Handle .txt file
        resume_text = uploaded_file.getvalue().decode("utf-8")
    elif file_type == "application/pdf":  # Handle .pdf file
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        resume_text = ""
        for page in pdf_reader.pages:
            resume_text += page.extract_text()

    # Optionally, user provides a job description
    job_description = st.text_area("Optional: Paste a job description to tailor the resume enhancements:")

    st.subheader("Uploaded Resume:")
    st.text(resume_text)

    # When the user clicks the "Enhance Resume" button
    if st.button("Enhance Resume"):
        detailed_summary, enhanced_resume = enhance_resume_with_gpt35_turbo(resume_text, job_description)

        st.subheader("Enhancement Summary:")
        st.text(detailed_summary)

        st.subheader("Enhanced Resume:")
        st.text(enhanced_resume)

else:
    st.info("Please upload a resume to get started.")
