import requests
import json
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from dotenv import load_dotenv
import time
from dotenv import load_dotenv
from serpapi import GoogleSearch


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

    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
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
