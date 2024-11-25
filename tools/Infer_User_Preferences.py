import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from tools.ResumeProcessor import get_user_resume,resume_to_text, get_resume_type
load_dotenv('../.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
if not OPENAI_API_KEY:
    st.error("Environment variables are missing. Please check the .env file.")
    st.stop()



def get_inferred_occupation():
    resume_data = get_user_resume(st.session_state.get('username'))
    resume_type = get_resume_type(st.session_state.get('username'))
    resume_text = resume_to_text(resume_data,resume_type)
    prompt = (
        f"Analyze the following user resume:\n\n{resume_text}\n\n"
        "From the provided resume data, determine the most appropriate occupation name that matches the user's skills, experience, and qualifications."
        "The occupation title must align strictly with official SOC (Standard Occupational Classification), O*NET, or OES/OEWS (Occupational Employment Statistics/Occupational Employment and Wage Statistics) codes and titles."
        "Provide only the occupation title as a string output, without additional text, explanations, or formatting."
        "Do not include inferred information beyond what is explicitly mentioned in the resume unless necessary for aligning with SOC, O*NET, or OES/OEWS occupation titles."
        "Ensure the chosen title accurately represents the user's professional profile and adheres to the standardized classification."
        "The title must be in plurals as per the exact string in the official documentation"
        "The title must be a single occupation, not a comma seperated value"
    )
    behaviour = (
        "You are an occupation inference agent tasked with matching user resume data to SOC, O*NET, or OES/OEWS occupation codes and titles. "
        "Your goal is to provide a precise and standardized occupation name based solely on the resume content."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": behaviour}
        ]
    )

    # Extract the assistant's reply
    occupation_name = response.choices[0].message.content.strip()

    return occupation_name


@st.cache_data(ttl=3600)
def get_inferred_occupations():
    resume_data = get_user_resume(st.session_state.get('username'))
    resume_type = get_resume_type(st.session_state.get('username'))
    resume_text = resume_to_text(resume_data, resume_type)

    prompt = (
        f"Analyze the following user resume:\n\n{resume_text}\n\n"
        "From the provided resume data, determine the most appropriate occupation name that matches the user's skills, experience, and qualifications."
        "The occupation title must align strictly with official SOC (Standard Occupational Classification), O*NET, or OES/OEWS (Occupational Employment Statistics/Occupational Employment and Wage Statistics) codes and titles."
        "Provide a list of the top three occupations most related to the first occupation title, in order of relevance."
        "Each occupation title must be a single occupation, in plural form, matching official classification titles."
        "Return only the occupation titles as a list of strings, with no extra text, explanations, or formatting."
    )

    behaviour = (
        "You are an occupation inference agent tasked with matching user resume data to SOC, O*NET, or OES/OEWS occupation codes and titles. "
        "Your goal is to provide a precise and standardized occupation name based solely on the resume content."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": behaviour}
        ]
    )

    # Extract the assistant's reply
    occupations = response.choices[0].message.content.strip()

    # If the response contains multiple occupations, split by line and clean up
    occupations_list = [occupation.strip() for occupation in occupations.split("\n") if occupation.strip()]

    # Ensure it's a list of exactly three occupations
    return occupations_list[:3]  # Return only the top 3 occupations


