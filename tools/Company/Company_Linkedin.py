import requests
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from serpapi import GoogleSearch



load_dotenv()
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

api_key = os.environ.get("PROXYCURL_API_KEY")

def fetch_company_data(linkedin_url):
    headers = {'Authorization': 'Bearer ' + api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/company'  # Company endpoint
    params = {
        'url': linkedin_url,
        'categories': 'include',
        'funding_data': 'include',
        'exit_data': 'include',
        'acquisitions': 'include',
        'extra': 'include',
        'use_cache': 'if-present',
        'fallback_to_cache': 'on-error',
    }

    response = requests.get(api_endpoint, params=params, headers=headers)
    print(response.status_code)

    if response.status_code == 200:
        company_data = response.json()
        print("Company Data:", company_data)

        # Fetch the profile picture URL
        profile_pic_url = company_data.get("profile_pic_url")
        
        if profile_pic_url:
            # Define the local path for saving the profile picture
            image_filename = f"{company_data['name'].replace(' ', '_')}_profile.jpg"
            image_path = os.path.join("cached_images", image_filename)
            os.makedirs("cached_images", exist_ok=True)  # Create directory if it doesn't exist
            
            # Download and save the profile picture
            img_response = requests.get(profile_pic_url)
            if img_response.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(img_response.content)
                print(f"Profile picture saved as {image_path}")
                
                # Add the local image path to the company data
                company_data["local_profile_pic_path"] = image_path
            else:
                print("Failed to download profile picture.")
                company_data["local_profile_pic_path"] = None
        else:
            print("No profile picture URL found.")
            company_data["local_profile_pic_path"] = None

        return company_data


def store_proxy_company(data):

    # MongoDB setup
    uri = os.environ.get('URI_FOR_Mongo')  # Load MongoDB URI from the environment
    tlsCAFile = certifi.where()
    if not tlsCAFile:
        raise ValueError("tlsCAFile is not defined in the environment variables")
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))

    # Select the database and collection
    database_name = "499"
    collection_name = "Company_Linkedin"
    db = client[database_name]
    collection = db[collection_name]
    print (data)
    # Insert data into MongoDB
    result = collection.insert_one(data)
    print("Data inserted with ID:", result.inserted_id)
    client.close()


def get_linkedin_company_url(company_name):
    query_linkedin = f"LinkedIn {company_name} company page"

    # Configure GoogleSearch parameters
    search_params = {
        "engine": "google",
        "q": query_linkedin,
        "api_key": SERP_API_KEY, 
    }

    # Run the search for LinkedIn
    search = GoogleSearch(search_params)
    results = search.get_dict()
    linkedin_url = None
    for result in results.get("organic_results", []):
        if "linkedin.com/company" in result.get("link", ""):
            linkedin_url = result["link"]
            break

    return linkedin_url


def generate_company_linkedin_data(company_name: str):
    company_linkedin_url = get_linkedin_company_url(company_name)
    print("Company Linkedin URL:", company_linkedin_url)
    company_linkedin_data = fetch_company_data(company_linkedin_url)
    store_proxy_company(company_linkedin_data)
    return company_linkedin_data