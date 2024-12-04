import os
import certifi
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain.agents import load_tools
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from tools.ProxyCurlLinkedIn import get_leadership_team_info

load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# use SERPAPI
def search_google_top_results(query: str):
    tools = load_tools(["serpapi"], api_key=os.getenv('SERPAPI_API_KEY'))
    serpapi_tool = tools[0]

    # Run the query through SerpAPI
    results = serpapi_tool.run(query)
    #print for testing 
    print("Here are the results")
    print (results)
    return results

def extract_data_with_regex(response):
    try:
        # Extract Overview
        overview_match = re.search(r'"Overview":\s*"(.*?)"', response)
        overview = overview_match.group(1) if overview_match else "Overview not found."

        # Extract Mission
        mission_match = re.search(r'"Mission":\s*"(.*?)"', response)
        mission = mission_match.group(1) if mission_match else "Mission not found."

        # Extract Company Culture
        culture_match = re.search(r'"Company Culture":\s*"(.*?)"', response)
        culture = culture_match.group(1) if culture_match else "Culture not found."

        # Extract Values (Top 5 Company Values)
        values_match = re.search(r'"Top 5 Company Values":\s*\[(.*?)\]', response, re.DOTALL)
        if values_match:
            # Match the inner list content
            values_raw = values_match.group(1)
            # Extract individual values from the list
            values = re.findall(r'"(.*?)"', values_raw)
        else:
            values = []

        # Extract Leadership
        leadership_match = re.search(r'"Leadership":\s*\[(.*?)\]', response, re.DOTALL)
        if leadership_match:
            leadership_raw = leadership_match.group(1)
            leadership = re.findall(r'"Name":\s*"(.*?)".*?"Description":\s*"(.*?)"', leadership_raw, re.DOTALL)
            leadership = [{"name": name, "description": description} for name, description in leadership]
        else:
            leadership = []

        # Return extracted data
        return {
            "overview": overview,
            "mission": mission,
            "culture": culture,
            "values": values,
            "leadership": leadership,
        }

    except Exception as e:
        print(f"Error extracting data: {e}")
        return {"error": str(e)}
  

# Function to extract data for the company using different queries
def extract_and_scrape_company_overview_data(company_name: str):
    data = {}

    # Different search queries for different sections
    overview_query = f"{company_name} company overview"
    mission_query = f"{company_name} company mission"
    culture_query = f"{company_name} company culture"
    values_query = f"{company_name} company core values"
    leadership_query = f"{company_name} top 3 leadership team"

    # Search and scrape for each section
    overview_results = search_google_top_results(overview_query)
    mission_results = search_google_top_results(mission_query)
    culture_results = search_google_top_results(culture_query)
    values_results = search_google_top_results(values_query)
    leadership_results = search_google_top_results(leadership_query)


    # Prepare the data dictionary to send to the LLM
    data['overview'] = overview_results
    data['mission'] = mission_results
    data['culture'] = culture_results
    data['values'] = values_results
    data['leadership'] = leadership_results 

    # Format the data using the LLM to generate a summary of each section 
    formatted_data = format_company_data_with_llm(company_name, data)
    formatted_data["serp_overview"] = overview_results 
    formatted_data["serp_mission"] = mission_results
    formatted_data["serp_culture"] = culture_results 
    formatted_data["serp_values"] = values_results 
    formatted_data["serp_leadership"] = leadership_results 
    return formatted_data

# LLM Integration to format the scraped data into concise summaries
def format_company_data_with_llm(company_name: str, data: dict):

# prompt template to ask LLM to summarize each section using the scraped data
    prompt_template = PromptTemplate(
        input_variables=["company_name", "overview", "mission", "culture", "values", "leadership"],
        template="""
        Please provide a concise and well-structured summary for the following information about {company_name}:

        Overview (summarize this information under 60 words):
        {overview}

        Mission (summarize this information under 60 words):
        {mission}

        Company Culture (summarize this information under 60 words):
        {culture}

        Only list Top 5 Company Values (summarize this information and list the top 5:
        {values}

        Leadership (Based on the information provided below, list the leadership team of {company_name})
        Give only the top 3 people and for each provide the Name and Description (title of member at company)
        {leadership}

        Ensure that the summaries are clear, concise, and capture the overall key points. 
        I want the response in a JSON format
        """
    )

    # Setup the LLMChain
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    # Run the LLM with the scraped data
    formatted_response = chain.run({
        "company_name": company_name,
        "overview": data.get('overview', "Overview not found."),
        "mission": data.get('mission', "Mission and values not found."),
        "culture": data.get('culture', "Culture information not available."),
        "values": "\n".join(data.get('values', [])),
        "leadership": "\n".join(data.get('leadership', []))
    })

    # Print the formatted response with a message
    print("\nHere is the formatted response from the LLM:\n")
    print(formatted_response)

    extracted_data = extract_data_with_regex(formatted_response)
    extracted_data["company"] = company_name
    # Print the formatted response with a message
    print("\nHere is the formatted response with regex:\n")
    print(extracted_data)

    # Enrich leadership team data if necessary
    enriched_leadership_data = get_leadership_team_info(company_name, extracted_data["leadership"])
    extracted_data["leadership"] = enriched_leadership_data

    #add serapi results to dataset



    return extracted_data




# MongoDB Storage Function to store the data
def store_company_overview_data(formatted_response):

    uri = os.environ.get('URI_FOR_Mongo')  # Load MongoDB URI from the environment
    #tlsCAFile = os.getenv('tlsCAFile')  # Load tlsCAFile from the environment
    tlsCAFile = certifi.where()
    # Check if tlsCAFile is loaded correctly
    if not tlsCAFile:
        raise ValueError("tlsCAFile is not defined in the environment variables")
    # Create MongoClient object with tlsCAFile
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))

    # Select the database and collection
    database_name = "499"
    collection_name = "Company_Overview"
    db = client[database_name]
    collection = db[collection_name]
    
    # Insert data into MongoDB
    result = collection.insert_one(formatted_response)
    print("Data inserted with ID:", result.inserted_id)
    client.close()


# function to generate, scrape, format, and store company data
def generate_company_overview_data(company_name: str):
    company_data = extract_and_scrape_company_overview_data(company_name)
    store_company_overview_data(company_data)
    return company_data




       

