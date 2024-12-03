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
else:
    st.warning("No resume found. Please upload one first.")
