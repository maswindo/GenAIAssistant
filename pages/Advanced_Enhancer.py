import streamlit as st
from resume_enhancer.database_manager import DatabaseManager
from resume_enhancer.file_processor import FileProcessor
from langchain_openai import ChatOpenAI
from resume_enhancer.agent_manager import AgentManager
import os
from resume_enhancer import *


# Ensure user is logged in
if 'username' not in st.session_state:
    st.error("You must log in first!")
    st.stop()

st.title("Advanced Enhancements")

# Initialize components
username = st.session_state['username']
db_manager = DatabaseManager(
    db_uri=os.getenv('URI_FOR_Mongo'),
    database_name='499',
    collection_name='files_uploaded'
)
resume_data = db_manager.get_resume(username)

if resume_data:
    if st.button("Go Home"):
        st.switch_page("pages/WelcomePage.py")
    # Extract text from file
    resume_text = FileProcessor.extract_text(resume_data)
    st.text_area("Your Resume:", resume_text, height=200)

    st.subheader("Detailed Enhancements by Agent")
    chat = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    agent_manager = AgentManager(chat)

    # Buttons for each agent
    if st.button("Clarity Enhancements"):
        with st.expander("Clarity Suggestions"):
            clarity_feedback = agent_manager.advanced_clarity_agent(resume_text)
            st.markdown("### **Clarity Suggestions**")
            st.write(clarity_feedback)

    if st.button("Impact Enhancements"):
        with st.expander("Impact Suggestions"):
            impact_feedback = agent_manager.advanced_impact_agent(resume_text)
            st.markdown("### **Impact Suggestions**")
            st.write(impact_feedback)

    if st.button("Visual Scan Improvements"):
        with st.expander("Visual Scan Suggestions"):
            visual_feedback = agent_manager.advanced_visual_scan_agent(resume_text)
            st.markdown("### **Visual Scan Suggestions**")
            st.write(visual_feedback)

    if st.button("Branding Enhancements"):
        with st.expander("Branding Suggestions"):
            branding_feedback = agent_manager.advanced_branding_agent(resume_text)
            st.markdown("### **Branding Suggestions**")
            st.write(branding_feedback)

    if st.button("ATS Compatibility Enhancements"):
        with st.expander("ATS Compatibility Suggestions"):
            ats_feedback = agent_manager.advanced_ats_compatibility_agent(resume_text)
            st.markdown("### **ATS Compatibility Suggestions**")
            st.write(ats_feedback)

    if st.button("Quantification Enhancements"):
        with st.expander("Quantification Suggestions"):
            quantification_feedback = agent_manager.advanced_quantification_agent(resume_text)
            st.markdown("### **Quantification Suggestions**")
            st.write(quantification_feedback)

    if st.button("Action Verb Enhancements"):
        with st.expander("Action Verb Suggestions"):
            action_verb_feedback = agent_manager.advanced_action_verb_agent(resume_text)
            st.markdown("### **Action Verb Suggestions**")
            st.write(action_verb_feedback)

    if st.button("Achievements Highlight Enhancements"):
        with st.expander("Achievements Highlight Suggestions"):
            achievements_feedback = agent_manager.advanced_achievements_highlight_agent(resume_text)
            st.markdown("### **Achievements Highlight Suggestions**")
            st.write(achievements_feedback)


    # Tailoring Enhancements Section
    st.subheader("Tailoring Enhancements")

    # Text input field for the job description
    job_description = st.text_area("Paste the Job Description:", placeholder="Enter the job description here...", height=150)

    # Button to trigger the tailoring agent
    if st.button("Run Tailoring Agent"):
        if job_description.strip():  # Check if the user has entered a job description
            with st.expander("Tailoring Suggestions"):
                tailoring_feedback = agent_manager.tailoring_agent(resume_text, job_description)
                st.markdown("### **Tailoring Suggestions**")
                st.write(tailoring_feedback)
        else:
            st.error("Please provide a job description before running the Tailoring Agent.")

else:
    st.warning("No resume found. Please upload one first.")
