import os
import certifi
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain.agents import load_tools
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from serpapi import GoogleSearch
import re
from tools.ProxyCurlLinkedIn import get_leadership_team_info


load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

llm = chat = ChatOpenAI(model="gpt-4", temperature=0)

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
  

# Function to extract data for the company using different queries
def extract_and_scrape_company_data(company_name: str):
    data = {}

    # Different search queries for different sections
    overview_query = f"{company_name} company overview"
    mission_query = f"{company_name} company mission"
    culture_query = f"{company_name} company culture"
    values_query = f"{company_name} company core values"
    leadership_query = f"{company_name} top leadership team"

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
    return formatted_data

# LLM Integration to format the scraped data into concise summaries
def format_company_data_with_llm(company_name: str, data: dict):

    # prompt template to ask LLM to summarize each section using the scraped data
    prompt_template = PromptTemplate(
        input_variables=["company_name", "overview", "mission", "culture", "values", "leadership"],
        template="""
        Please provide a concise and well-structured summary for the following information about {company_name}:
        
        Overview (summarize this information under 40 words):
        {overview}

        Mission (summarize this information under 40 words):
        {mission}

        Company Culture (summarize this information under 40 words):
        {culture}

        Only list Top 5 Company Values (summarize this information and list the top 5(1., 2., 3., 4., 5.)):
        {values}

        Leadership (Based on the information provided below, list the leadership team of {company_name})
        Give only the top 3 people and for each provide the Name and Description (title of member at company)
        {leadership}

        here is a format example
        1.
        Name: name
        Description: the title of member at company
       
        2.
        Name: 
        Description: 
        
        
        3.
        Name: 
        Description: 
  


        
        Ensure that the summaries are clear, concise, and capture the overall key points.
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
    
    print (formatted_response)
    # Function to parse formatted response
    # Use regex to extract sections from the formatted response
    
    overview_match = re.search(r"Overview:\n(.*?)\nMission:", formatted_response, re.DOTALL)
    mission_match = re.search(r"Mission:\n(.*?)\nCompany Culture:", formatted_response, re.DOTALL)
    culture_match = re.search(r"Company Culture:\n(.*?)\nTop 5 Company Values:", formatted_response, re.DOTALL)
    values_match = re.search(r"Top 5 Company Values:\n(.*?)(?:\nLeadership|$)", formatted_response, re.DOTALL)
    leadership_match = re.findall(r"\d+\.\s+Name:\s*(.*?)\n\s*Description:\s*(.*?)\n\s*", formatted_response, re.DOTALL)



    # Clean up and format the extracted sections
    data = {
        "company": company_name,
        "overview": overview_match.group(1).strip() if overview_match else "Overview not found.",
        "mission": mission_match.group(1).strip() if mission_match else "Mission not found.",
        "culture": culture_match.group(1).strip() if culture_match else "Culture not found.",
        "values": [v.strip() for v in values_match.group(1).split('\n') if v.strip()] if values_match else [],
        "leadership": [
        {"name": name.strip(), "description": description.strip() }
        for name, description in leadership_match
    ]


    }

    enriched_leadership_data = get_leadership_team_info(company_name, data["leadership"])
    data["leadership"] = enriched_leadership_data

    print (data)  
    return data
      
    

# MongoDB Storage Function to store the data
def store_company_data(formatted_response):

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


def get_review_urls(company_name):
    query_glassdoor = f"Glassdoor {company_name} company reviews"
    query_indeed = f"Indeed {company_name} company reviews"

    # Configure GoogleSearch parameters
    search_params = {
        "engine": "google",
        "q": query_glassdoor,
        "api_key": SERP_API_KEY,
    }

    # Run the search for Glassdoor
    search = GoogleSearch(search_params)
    results = search.get_dict()
    glassdoor_url = None
    for result in results.get("organic_results", []):
        if "glassdoor" in result.get("link", ""):
            glassdoor_url = result["link"]
            break

    # Update search parameters for Indeed
    search_params["q"] = query_indeed
    search = GoogleSearch(search_params)
    results = search.get_dict()
    indeed_url = None
    for result in results.get("organic_results", []):
        if "indeed" in result.get("link", ""):
            indeed_url = result["link"]
            break

    return glassdoor_url, indeed_url


from serpapi import GoogleSearch





 
# Main function to generate, scrape, format, and store company data
def generate_company_data(company_name: str):
    company_data = extract_and_scrape_company_data(company_name)
    store_company_data(company_data)

    glassdoor_url, indeed_url = get_review_urls(company_name)
    print("Glassdoor URL:", glassdoor_url)
    print("Indeed URL:", indeed_url)

    return company_data