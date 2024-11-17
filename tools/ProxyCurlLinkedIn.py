import os
import requests
from dotenv import load_dotenv

import json  # Import json for better handling of json data
from serpapi import GoogleSearch

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")


# Function to get LinkedIn profile URLs based on person's name and company name
def get_linkedin_url(person_name, company_name):
    # Create a search query that includes both the person's name and company
    query_linkedin = f"{person_name} {company_name} LinkedIn profile"

    # Configure GoogleSearch parameters
    search_params = {
        "engine": "google",
        "q": query_linkedin,
        "api_key": SERP_API_KEY,  # Replace with your actual SerpAPI key
    }

    # Run the search for LinkedIn
    search = GoogleSearch(search_params)
    results = search.get_dict()

    # Extract LinkedIn profile URL
    for result in results.get("organic_results", []):
        if "linkedin.com/in" in result.get("link", ""):
            print(result["link"])
            return result["link"]  # Directly return the LinkedIn URL if found

    # Return None if no LinkedIn profile URL was found
    return None


def scrapelinkedinprofile(linkedin_profile_url: str, mock: bool = False):
    """Scrape information from LinkedIn profiles, manually scrape the information from the LinkedIn profile."""

    if mock:
        # Use a mocked URL for testing
        linkedin_profile_url = "https://gist.githubusercontent.com/emarco177/0d6a3f93dd06634d95e46a2782ed7490/raw/78233eb934aa9850b689471a604465b188e761a0/eden-marco.json"
        response = requests.get(linkedin_profile_url, timeout=10)
    else:
        # Real API endpoint
        api_endpoint = "https://nubela.co/proxycurl/api/v2/linkedin"
        header_dic = {"Authorization": f'Bearer {os.environ.get("PROXYCURL_API_KEY")}'}
        response = requests.get(api_endpoint, params={"url": linkedin_profile_url, "skills": "include"},
                                headers=header_dic)

    # Convert response to JSON
    data = response.json()

    # Clean up data to remove empty values and specific keys
    clean_data = {k: v for k, v in data.items() if
                  v not in ([], "", None) and k not in ["people_also_viewed", "certifications"]}

    # Handling nested dictionaries in 'groups', if present
    if clean_data.get("groups"):
        for group_dict in clean_data["groups"]:
            group_dict.pop("profile_pic_url", "None")  # Use pop with None as default to avoid KeyError

    # Convert cleaned data back to JSON for output
    json_data = json.dumps(clean_data, indent=4)  # Convert dictionary to JSON string with pretty print

    print(json_data)

    return (clean_data)


def get_leadership_team_info(company_name: str, team_members: list):
    """Fetch LinkedIn profile picture, headline, LinkedIn URL, and summary for each team member."""
    team_info = []

    for member in team_members:

        company = company_name
        name = member.get("name", "Name not found")
        description = member.get("description", "Description not found")
        # linkedin_url = member.get("linkedin_url")
        linkedin_url = get_linkedin_url(name, company)

        if linkedin_url:
            # Fetch LinkedIn profile data
            profile_data = scrapelinkedinprofile(linkedin_url)
            if profile_data:
                # Construct LinkedIn URL using 'public_identifier'
                linkedin_profile_url = f"https://www.linkedin.com/in/{profile_data.get('public_identifier')}"

                team_member_info = {
                    "name": profile_data.get("full_name", name),
                    "profile_pic_url": profile_data.get("profile_pic_url", "None"),
                    "description": description,
                    "linkedin_url": linkedin_profile_url,
                }
                team_info.append(team_member_info)


            else:
                print(f"Could not fetch profile data for {name} at {linkedin_url}")
        else:
            print(f"LinkedIn URL not available for {name}")

    print(team_info)
    return team_info