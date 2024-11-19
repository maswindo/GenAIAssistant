import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
import certifi
from pymongo.server_api import ServerApi
from langchain.schema import HumanMessage, SystemMessage
import io
from docx import Document
import pdfplumber
import pytesseract
from PIL import Image

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

st.title("Enhance Your Resume with Specialized Agents")

#######################################################################################################
# DATABASE CONNECTION FUNCTIONS
#######################################################################################################

def get_user_resume_from_db(username):
    uri = os.getenv('URI_FOR_Mongo')
    with MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1')) as client:
        db = client['499']
        collection = db['files_uploaded']
        user = collection.find_one({'username': username})
        if user and 'data' in user:
            return user['data']
    return None

#######################################################################################################
# UTILITY FUNCTIONS
#######################################################################################################

def extract_text_from_file(file_data):
    try:
        file_like = io.BytesIO(file_data)
        if file_data[:4] == b'\x50\x4b\x03\x04':
            return extract_text_from_docx(file_like)
        else:
            with pdfplumber.open(file_like) as pdf:
                resume_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        resume_text += page_text + "\n"
                    else:
                        image = page.to_image()
                        pil_image = image.original
                        ocr_text = pytesseract.image_to_string(pil_image)
                        if ocr_text:
                            resume_text += ocr_text + "\n"
                return resume_text
    except Exception as e:
        st.warning(f"Error extracting text from file: {e}")
        return None

def extract_text_from_docx(file_like):
    try:
        document = Document(file_like)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        st.warning(f"Error extracting DOCX: {e}")
        return None

#######################################################################################################
# AGENT FUNCTIONS FOR RESUME ENHANCEMENT
#######################################################################################################

def interact_with_agent(agent_prompt):
    try:
        messages = [
            SystemMessage(content=agent_prompt['system']),
            HumanMessage(content=agent_prompt['user'])
        ]
        response = chat(messages)
        return response.content.strip()
    except Exception as e:
        st.error(f"Error interacting with GPT-4 Turbo: {e}")
        return ""

# Clarity Agent
def clarity_agent(resume_text):
    prompt = {
        'system': "You are an expert recruiter with a focus on enhancing resume clarity. Scan through the resume and focus on improving readability, structure, and organization without adding or fabricating any information. Provide a summary of the changes made and offer suggestions for improving clarity, including substitution examples to illustrate improvements.",
        'user': f"Enhance the clarity of the following resume text to make it more readable and structured for a recruiter:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Impact Agent
def impact_agent(resume_text):
    prompt = {
        'system': "You are an expert in enhancing resume impact by emphasizing achievements and quantifiable results. Focus on identifying key accomplishments and ensuring that each achievement is clearly quantified where possible, without fabricating any information. Provide specific changes, but don't just enhance the whole resume your focus is only the impact. Provide a summary of the changes made and offer suggestions for improving impact, including substitution examples to illustrate improvements.",
        'user': f"Enhance the impact of the following resume text by emphasizing achievements and quantifiable results where applicable. Do not fabricate information:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Experience Prioritization Agent
def experience_prioritization_agent(resume_text):
    prompt = {
        'system': "You are an expert in prioritizing resume job experiences to highlight the most relevant information for recruiters. Focus on reorganizing the content so that the most impactful and relevant experiences are placed prominently, improving the overall impression within a short scan. xProvide a summary of the changes made and offer suggestions for improving experience prioritization, including substitution examples to illustrate improvements.",
        'user': f"Reorganize the job experiences in the following resume text to prioritize the most relevant and impactful experiences for the target job:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Skills Matching Agent
def skills_matching_agent(resume_text, job_description=None):
    user_prompt = "Enhance the skills section of the following resume text to make it more impactful and relevant. Do not create or fabricate any skills that are not already present in the resume. Provide a summary of the changes made and offer suggestions for improving matching skills, including substitution examples to illustrate improvements."
    if job_description:
        user_prompt += f" Use the following job description for context: {job_description}"
    prompt = {
        'system': "You are an expert in improving resume skills presentation. Focus on making existing skills stand out by aligning them closely with the job requirements and presenting them in a more compelling manner. Provide a summary of the changes made and offer suggestions for improving matching skills, including substitution examples to illustrate improvements.",
        'user': user_prompt + f"\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Visual Scan Agent
def visual_scan_agent(resume_text):
    prompt = {
        'system': "You are an expert in optimizing resumes for quick visual scans by recruiters. Ensure that key details like job titles, company names, dates, and major achievements are highlighted to stand out during a brief review. Do not alter the core content or fabricate information. Do not enhance the entire resume, just go over visual aspects of the resume and talk about how the user can make specific parts of their resume better visually. Provide a summary of the changes made and offer suggestions for improving the visuals of the users resume, including substitution examples to illustrate improvements.",
        'user': f"Optimize the following resume text for a quick visual scan by a recruiter:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# ATS Compatibility Agent
def ats_compatibility_agent(resume_text):
    prompt = {
        'system': "You are an expert recruiter specializing in optimizing resumes for Applicant Tracking Systems (ATS). Scan through the resume and provide specific recommendations for improving keyword usage, formatting, and structure to ensure compatibility with ATS. Do not fabricate information or make unrelated changes. Provide a summary of the changes made and offer suggestions for improving ats compatibility, including substitution examples to illustrate improvements.",
        'user': f"Review the following resume and make precise changes to ensure it is optimized for ATS, including keyword usage, formatting, and structure. Do not fabricate information:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Tailoring Agent
def tailoring_agent(resume_text, job_description=None):
    user_prompt = "Tailor the following resume text to align with a specific job description without fabricating any information. Focus on adjusting the wording and emphasis to match the job requirements closely. Provide a summary of the changes made and offer suggestions for improving the resume to fit the tailored job, including substitution examples to illustrate improvements."
    if job_description:
        user_prompt += f" Use the following job description for context: {job_description}"
    prompt = {
        'system': "You are an expert in tailoring resumes to match specific job descriptions. Ensure that the resume content is adjusted to align with the needs and language of the target job while maintaining the integrity of the original information. Provide a summary of the changes made and offer suggestions for improving tailoring, including substitution examples to illustrate improvements.",
        'user': user_prompt + f"\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Branding Agent
def branding_agent(resume_text):
    prompt = {
        'system': "You are an expert in enhancing a candidate's professional branding on their resume. Focus on improving the professional summary, emphasizing unique strengths, and ensuring that the candidate's personal brand is communicated effectively and consistently throughout the resume. Provide a summary of the changes made and offer suggestions for improving the users brand, including substitution examples to illustrate improvements. Help the user establish their brand.",
        'user': f"Review the following resume text and enhance the personal branding by improving the summary and emphasizing unique strengths:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

# Consistency Agent
def consistency_agent(resume_text):
    prompt = {
        'system': "You are an expert in ensuring consistency across resume details, such as date formats, alignment, punctuation, and general tone. Identify and correct any inconsistencies to present a polished and professional resume. Provide a summary of the changes made and offer suggestions for improving consistency, including substitution examples to illustrate improvements.",
        'user': f"Ensure consistency in the following resume text, including date formats, alignment, punctuation, and tone:\nResume Text: {resume_text}"
    }
    return interact_with_agent(prompt)

#######################################################################################################
# RETRIEVE AND DISPLAY USER RESUME
#######################################################################################################

stored_resume = get_user_resume_from_db(username)
if stored_resume:
    st.write("Debug: Resume found in database.")
    resume_text = extract_text_from_file(stored_resume)
    st.subheader("Your Current Resume:")
    st.text_area("", resume_text, height=300)
else:
    st.warning("No resume found for the user. Please upload a resume first.")
    resume_text = None

#######################################################################################################
# AGENT INTERACTION SECTION
#######################################################################################################

job_description = st.text_area("Add Job Description (optional):", "", height=100)

# Pre-create text areas for agent outputs
if "clarity_suggestions" not in st.session_state:
    st.session_state["clarity_suggestions"] = ""
if "impact_suggestions" not in st.session_state:
    st.session_state["impact_suggestions"] = ""
if "experience_prioritization_suggestions" not in st.session_state:
    st.session_state["experience_prioritization_suggestions"] = ""
if "skills_matching_suggestions" not in st.session_state:
    st.session_state["skills_matching_suggestions"] = ""
if "visual_scan_suggestions" not in st.session_state:
    st.session_state["visual_scan_suggestions"] = ""
if "ats_optimization_suggestions" not in st.session_state:
    st.session_state["ats_optimization_suggestions"] = ""
if "tailoring_suggestions" not in st.session_state:
    st.session_state["tailoring_suggestions"] = ""
if "branding_suggestions" not in st.session_state:
    st.session_state["branding_suggestions"] = ""
if "consistency_suggestions" not in st.session_state:
    st.session_state["consistency_suggestions"] = ""

if resume_text:
    st.subheader("Clarity Enhancement Agent")
    if st.button("Enhance Clarity"):
        st.session_state["clarity_suggestions"] = clarity_agent(resume_text)
    st.text_area("Clarity Enhancement Suggestions:", st.session_state["clarity_suggestions"], height=150)

    st.subheader("Impact Enhancement Agent")
    if st.button("Enhance Impact"):
        st.session_state["impact_suggestions"] = impact_agent(resume_text)
    st.text_area("Impact Enhancement Suggestions:", st.session_state["impact_suggestions"], height=150)

    st.subheader("Experience Prioritization Agent")
    if st.button("Prioritize Job Experience"):
        st.session_state["experience_prioritization_suggestions"] = experience_prioritization_agent(resume_text)
    st.text_area("Experience Prioritization Suggestions:", st.session_state["experience_prioritization_suggestions"], height=150)

    st.subheader("Skills Matching Agent")
    if st.button("Enhance Skills"):
        st.session_state["skills_matching_suggestions"] = skills_matching_agent(resume_text, job_description)
    st.text_area("Skills Matching Suggestions:", st.session_state["skills_matching_suggestions"], height=150)

    st.subheader("Visual Scan Enhancement Agent")
    if st.button("Optimize for Visual Scan"):
        st.session_state["visual_scan_suggestions"] = visual_scan_agent(resume_text)
    st.text_area("Visual Scan Suggestions:", st.session_state["visual_scan_suggestions"], height=150)

    st.subheader("ATS Compatibility Agent")
    if st.button("Optimize for ATS"):
        st.session_state["ats_optimization_suggestions"] = ats_compatibility_agent(resume_text)
    st.text_area("ATS Optimization Suggestions:", st.session_state["ats_optimization_suggestions"], height=150)

    st.subheader("Tailoring Agent")
    if st.button("Tailor Resume"):
        st.session_state["tailoring_suggestions"] = tailoring_agent(resume_text, job_description)
    st.text_area("Tailoring Suggestions:", st.session_state["tailoring_suggestions"], height=150)

    st.subheader("Branding Enhancement Agent")
    if st.button("Enhance Branding"):
        st.session_state["branding_suggestions"] = branding_agent(resume_text)
    st.text_area("Branding Enhancement Suggestions:", st.session_state["branding_suggestions"], height=150)

    st.subheader("Consistency Agent")
    if st.button("Ensure Consistency"):
        st.session_state["consistency_suggestions"] = consistency_agent(resume_text)
    st.text_area("Consistency Suggestions:", st.session_state["consistency_suggestions"], height=150)

#######################################################################################################
# GENERATE ENHANCED RESUME BASED ON ALL SUGGESTIONS
#######################################################################################################

if st.button("Generate Enhanced Resume"):
    combined_suggestions = (
        f"Clarity Suggestions:\n{st.session_state['clarity_suggestions']}\n\n"
        f"Impact Enhancement Suggestions:\n{st.session_state['impact_suggestions']}\n\n"
        f"Experience Prioritization Suggestions:\n{st.session_state['experience_prioritization_suggestions']}\n\n"
        f"Skills Matching Suggestions:\n{st.session_state['skills_matching_suggestions']}\n\n"
        f"Visual Scan Suggestions:\n{st.session_state['visual_scan_suggestions']}\n\n"
        f"ATS Optimization Suggestions:\n{st.session_state['ats_optimization_suggestions']}\n\n"
        f"Tailoring Suggestions:\n{st.session_state['tailoring_suggestions']}\n\n"
        f"Branding Suggestions:\n{st.session_state['branding_suggestions']}\n\n"
        f"Consistency Suggestions:\n{st.session_state['consistency_suggestions']}\n"
    )

    # Create enhanced resume based on all suggestions
    enhanced_resume_prompt = {
        'system': "You are an expert resume writer. Do not fabricate any information or add details that are not already present in the suggestions or original resume.",
        'user': f"Using the following suggestions, generate an enhanced version of the user's resume:\n\n{combined_suggestions}\n\nOriginal Resume:\n{resume_text}"
    }
    enhanced_resume = interact_with_agent(enhanced_resume_prompt)

    st.subheader("Enhanced Resume Template:")
    st.text_area("", enhanced_resume, height=300)

#######################################################################################################
# UPLOAD AND DISPLAY NEW RESUME
#######################################################################################################

st.subheader("Upload a New Resume:")
uploaded_file = st.file_uploader("Upload your resume (as a .txt, .pdf, or .docx):", type=["txt", "pdf", "docx"])
if uploaded_file:
    file_type = uploaded_file.type
    if file_type == "text/plain":
        new_resume = uploaded_file.read().decode("utf-8")
    else:
        new_resume = extract_text_from_file(uploaded_file.read())
    resume_text = new_resume if new_resume else resume_text
    st.session_state["resume_text"] = resume_text
    st.text_area("", resume_text, height=300)
    st.write("Debug: Resume uploaded successfully.")
