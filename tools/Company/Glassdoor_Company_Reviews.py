import requests
import json
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from dotenv import load_dotenv
import time
from serpapi import GoogleSearch
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

# Load environment variables
load_dotenv()

BRIGHTDATA_API_KEY = os.getenv('BRIGHTDATA_API_KEY')
MONGO_URI = os.getenv('URI_FOR_Mongo')

if not BRIGHTDATA_API_KEY:
    raise ValueError("Bright Data API token is not set. Please set BRIGHTDATA_API_TOKEN in your environment.")
if not MONGO_URI:
    raise ValueError("MongoDB URI is not set. Please set MONGO_URI in your environment.")

# Bright Data API Constants
DATASET_TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"
HEADERS = {
    'Authorization': f'Bearer {BRIGHTDATA_API_KEY}',
    'Content-Type': 'application/json'
}

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), server_api=ServerApi('1'))

def get_company_glassdoor_review_data(glassdoor_url, days):
    """
    Triggers the data collection process for a given Glassdoor URL and days parameter.
    Returns the snapshot ID if the trigger is successful.
    """
    print(f"Triggering data collection for Glassdoor URL: {glassdoor_url}")

    payload = json.dumps([
        {
            "url": glassdoor_url,
            "days": days
        }
    ])
    params = {
        "dataset_id": "gd_l7j1po0921hbu0ri1z",
        "include_errors": "true"
    }

    response = requests.post(DATASET_TRIGGER_URL, headers=HEADERS, data=payload, params=params)

    if response.status_code == 200:
        # Extract the snapshot_id from the response
        snapshot_id = response.json().get('snapshot_id')
        if not snapshot_id:
            raise Exception("Snapshot ID not found in the response.")

        print(f"Snapshot ID: {snapshot_id}")
        return snapshot_id
    else:
        # Handle trigger failure
        raise Exception(f"Failed to trigger data collection. HTTP Status: {response.status_code}. Response: {response.text}")


def download_snapshot(snapshot_id):
    """
    Downloads the snapshot data for a given snapshot ID.
    Polls the API until the snapshot is ready and returns the JSON data.
    """
    snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

    while True:
        download_response = requests.get(snapshot_url, headers=HEADERS)

        if download_response.status_code == 200:
            try:
                # Parse the JSON response
                data = download_response.json()
                print(f"Successfully retrieved {len(data)} reviews.")
                return data
            except json.JSONDecodeError:
                raise Exception("Error decoding the JSON response from Bright Data API.")
        elif download_response.status_code == 202:
            # Snapshot not ready yet
            print("Snapshot is still processing. Waiting 10 seconds before retrying...")
            time.sleep(10)  # Wait for 10 seconds before polling again
        else:
            # Handle other HTTP errors
            raise Exception(f"Failed to download data. HTTP Status: {download_response.status_code}. Response: {download_response.text}")


def store_glassdoor_review_data(data, company_name):
    if not data:
        print("No data to store.")
        return

    db = client["Company_Glassdoor_Reviews"]
    collection = db[company_name]
    
    if isinstance(data, list):
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
    elif isinstance(data, dict):
        result = collection.insert_one(data)
        print(f"Inserted 1 record into MongoDB with ID: {result.inserted_id}.")
    else:
        print("Data format is not supported for MongoDB storage.")


def get_glassdoor_review_url(company_name):
    query_glassdoor = f"Glassdoor {company_name} company reviews"

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

    return glassdoor_url

def generate_company_glassdoor_review_data(company_name, days):
    glassdoor_url = get_glassdoor_review_url(company_name)
    print(glassdoor_url)
    snapshot_id = generate_company_glassdoor_review_data(glassdoor_url, days)
    data = download_snapshot(snapshot_id)
    print(data)
    store_glassdoor_review_data(data, company_name)
    return data


def get_top_reviews_for_filtered_results(company_name, job_title=None, location=None, years=None, status=None, count=5):
    """
    return: Dict with top Pro and Con reviews from filtered results.
    """
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
    db = client["Company_Glassdoor_Reviews"]
    collection = db[company_name]

    # Build the query based on filters
    query = {}
    if job_title:
        query["employee_job_title"] = {"$regex": job_title, "$options": "i"}  # Case-insensitive match
    if location:
        query["employee_location"] = {"$regex": location, "$options": "i"}  # Case-insensitive match
    if years:
        query["employee_length"] = {"$gte": years}  # Match years greater than or equal to the input
    if status:
        query["employee_status"] = {"$regex": status, "$options": "i"}  # Match current/past employee status

    # Retrieve and sort filtered results
    top_reviews = {
        "pros": list(collection.find({**query, "review_pros": {"$exists": True}})
                     .sort("count_helpful", -1)
                     .limit(count)),
        "cons": list(collection.find({**query, "review_cons": {"$exists": True}})
                     .sort("count_helpful", -1)
                     .limit(count))
    }
    client.close()

    return top_reviews



# Function to generate summaries using LangChain LLM
def summarize_reviews(reviews, review_type):
    if not reviews:
        return f"No {review_type} reviews found for the selected filters."

    review_texts = [review[f"review_{review_type}"] for review in reviews]
    # Combine all reviews into a single text
    all_reviews = "\n".join(review_texts)

    # Use the LLM to generate a summary
    prompt = (
        f"Summarize the following {review_type} from employee reviews in 2-3 bullet points:\n\n{all_reviews}"
    )
    response = llm.predict(prompt)
    return response.strip()



def store_glassdoor_summarized_review_data(data, company_name):
    if not data:
        print("No data to store.")
        return
    
    data["company_name"] = company_name

    # Select the database and collection
    database_name = "499"
    collection_name = "Company_Reviews"
    db = client[database_name]
    collection = db[collection_name]
    
    if isinstance(data, list):
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
    elif isinstance(data, dict):
        result = collection.insert_one(data)
        print(f"Inserted 1 record into MongoDB with ID: {result.inserted_id}.")
    else:
        print("Data format is not supported for MongoDB storage.")




def generate_company_glassdoor_review_summary_data(reviews, company_name):

  # Limit the reviews to 100 to avoid token limits
    limited_reviews = reviews[:100]  # Adjust the number as needed
    prompt = f"""
    You are an AI assistant analyzing employee feedback from Glassdoor reviews for a company. Below are the raw reviews provided by employees:

    **Raw Reviews:**
    {limited_reviews}

    **Task:**
    1. Summarize the pros in a paragraph about 350 words, highlighting only the relevent specific information.
    2. Summarize the cons in a paragraph about 350 words, highlighting only the relevent specific information.
    3. Summarize the pros in a paragraph about 50 words, highlighting only the relevent specific information.
    4. Summarize the cons in a paragraph about 50 words, highlighting only the relevent specific information.
    5. Analyze the raw data provided and provide very specific trends or correlations found in the data. 
    - provide the output in concise bullet lists - provide about 5 key trends
    ex. “Most positive reviews come from interns,” or “Employees frequently mention work-life balance as a con.”
    I want the trends to be very specific correalation between role type or location or other factors such as number of years at company



    Make your summaries clear and concise and only include the specific important details. Be the most specific you can be in the summaries.

    Provide the output in this format:
    Pro Long Summary: [Your pro summary here]
    Con Long Summary: [Your con summary here]
    Pro Short Summary: [Your con summary here]
    Con Short Summary: [Your con summary here]
    Trends:
    - [Trend 1]
    - [Trend 2]
    - [Trend 3]
    - [Trend 4]
    - [Trend 5]
    
   
    """
    # Get response from LLM
    response = llm.predict(prompt)
    print(response)

    # Parse the response into structured output
    sections = {"pro_long_summary": None, "con_long_summary": None, 
                "pro_short_summary": None, "con_short_summary": None, "trends": []}
    current_section = None

    for line in response.split("\n"):
        line = line.strip()  # Remove extra spaces and newline characters
        
        # Identify the section headings with '**' markers
        if line.startswith("**Pro Long Summary:**"):
            current_section = "pro_long_summary"
            sections[current_section] = ""
        elif line.startswith("**Con Long Summary:**"):
            current_section = "con_long_summary"
            sections[current_section] = ""
        elif line.startswith("**Pro Short Summary:**"):
            current_section = "pro_short_summary"
            sections[current_section] = ""
        elif line.startswith("**Con Short Summary:**"):
            current_section = "con_short_summary"
            sections[current_section] = ""
        elif line.startswith("**Trends:**"):
            current_section = "trends"
        
        # Append content to the current section
        elif current_section in ["pro_long_summary", "con_long_summary", "pro_short_summary", "con_short_summary"]:
            sections[current_section] += (line + " ")  # Add a space between lines
        elif current_section == "trends" and line.startswith("-"):
            sections["trends"].append(line)

    # Final cleanup: Strip unnecessary whitespace from all text sections
    for key in ["pro_long_summary", "con_long_summary", "pro_short_summary", "con_short_summary"]:
        if sections[key]:
            sections[key] = sections[key].strip()

    print("Here is the Glassdoor review data:")
    print(sections)
    sections = store_glassdoor_summarized_review_data(sections, company_name)
    return sections
    
