import streamlit as st
import json
from tools.ProxyCurlLinkedIn import scrapelinkedinprofile
from tools.ProxyCurlJob import scrape_job
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# Initialize OpenAI LLM for compatibility scoring
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, openai_api_key=os.getenv('OPENAI_API_KEY'))

# Streamlit UI for Compatibility Analysis
st.title("LLM-based Job Compatibility Analysis")

# Get LinkedIn profile link from session state
if 'link' not in st.session_state:
    st.write("Please set your LinkedIn profile link first.")
else:
    linkedin_url = st.session_state['link']
    job_url = st.text_input("Paste the LinkedIn job URL here:")

    if st.button("Analyze Compatibility"):
        # Fetch LinkedIn data
        linkedin_data = scrapelinkedinprofile(linkedin_url)

        if linkedin_data:
            # Fetch job description data
            job_data = scrape_job(job_url)
            job_description = job_data.get('description', "")

            # Combine data for LLM input
            combined_input = f"""
            LinkedIn Profile:
            {json.dumps(linkedin_data, indent=2)}

            Job Description:
            {job_description}

            Instructions:
            Based on the LinkedIn profile and job description, determine the user's compatibility for the role.
            Provide a compatibility score from 0 to 100, considering skills, experience, and qualifications.
            """

            # Set up the prompt template for the LLM
            prompt_template = PromptTemplate(
                input_variables=['information'],
                template="""
                Given the LinkedIn profile data and job description below, analyze the user's compatibility for the role.
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
            st.write("Unable to retrieve LinkedIn data.")
