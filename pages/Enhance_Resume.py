import streamlit as st
from resume_enhancer.database_manager import DatabaseManager
from resume_enhancer.file_processor import FileProcessor
from resume_enhancer.agent_manager import AgentManager
from langchain_openai import ChatOpenAI
from resume_enhancer import *
import os

# Ensure user is logged in
if 'username' not in st.session_state:
    st.error("You must log in first!")
    st.stop()

st.title("Simple Enhancements")

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

    st.subheader("Concise Suggestions")
    chat = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    agent_manager = AgentManager(chat)

    # Generate concise suggestions
    concise_suggestions = {
        "Clarity": agent_manager.clarity_agent(resume_text),
        "Impact": agent_manager.impact_agent(resume_text),
        "Visual Scan": agent_manager.visual_scan_agent(resume_text),
    }

    # Display suggestions
    for agent_name, suggestion in concise_suggestions.items():
        st.markdown(f"### **{agent_name}**")
        st.markdown(f"- **Suggestion:** {suggestion}")
        st.markdown(
            f"*Tip:* If you feel this aspect of your resume needs more improvement, "
            f"consider exploring advanced enhancements for detailed suggestions."
        )

    # Navigation to advanced enhancements
    st.subheader("Need More Advanced Enhancements?")
    if st.button("Go to Advanced Enhancements"):
        st.switch_page("pages/Advanced_Enhancer.py")
else:
    st.warning("No resume found. Please upload one first.")
