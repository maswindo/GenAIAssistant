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
    if st.button("Go Home"):
        st.switch_page("pages/WelcomePage.py")
    # Extract text from file
    resume_text = FileProcessor.extract_text(resume_data)
    st.text_area("Your Resume:", resume_text, height=200)

    st.subheader("Concise Suggestions")
    chat = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent_manager = AgentManager(chat)

    # Generate concise suggestions
    concise_suggestions = {
        "Clarity": agent_manager.clarity_agent(resume_text),
        "Impact": agent_manager.impact_agent(resume_text),
        "Visual Scan": agent_manager.visual_scan_agent(resume_text),
        "Branding": agent_manager.branding_agent(resume_text),  # Added Branding Agent
        "ATS Compatibility": agent_manager.ats_compatibility_agent(resume_text),  # Added ATS Agent
        "Quantification": agent_manager.quantification_agent(resume_text),  # Added Quantification Agent
        "Action Verbs": agent_manager.action_verb_agent(resume_text),  # Added Action Verb Agent
        "Achievements Highlight": agent_manager.achievements_highlight_agent(resume_text),  # Added Achievements Highlight Agent
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
    st.subheader("Need More Advanced Enhancements or Want to Tailor your Resume?")
    if st.button("Go to Advanced Enhancements"):
        st.switch_page("pages/Advanced_Enhancer.py")
else:
    st.warning("No resume found. Please upload one first.")
