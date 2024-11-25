from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
from dotenv import load_dotenv
import os
import certifi
import plotly.express as px
from geopy.geocoders import GoogleV3
import pandas as pd
import time
from geopy.exc import GeocoderTimedOut
import itertools
from collections import Counter

###
#This class displays analytics for internal use and triggers for testing functions
###

# Initialize Database and Session Variables
load_dotenv('../.env', override=True)
uri = os.environ.get('URI_FOR_Mongo')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
MAPBOX_API_KEY = os.environ.get('MAP_KEY')

if not MAPBOX_API_KEY:
    st.error("Mapbox API key is missing. Please check your environment variables.")
    st.stop()

if not uri or not GOOGLE_API_KEY:
    st.error("Environment variables are missing. Please check the .env file.")
    st.stop()

tlsCAFile = certifi.where()


# MongoDB connection with error handling
try:
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    db = client['499']
    collection_jobs = db['jobs']
    collection_users = db['files_uploaded']
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

#Analytics Functions
"""
What factors would result in a competitive rating? 
What makes something competitive?
Number of people vs number of openings
Quality of competitors
What effect does competition have on success probability?
Decreases success probability
Success probability built from a large number of variables per user
Competitive aspect per job listing therefore determines all users compete with each other
From the perspective of a single user:
Applicants with lower compatibility effect success odds less than applicant with higher or similar compatibility
Number of applicants, depending on distribution, effect user's competitive ranking like so.
Note: Requires integration with job_compatibility functionality
"""
def get_post_competition_distribution():
    #Returns a bar graph representing the distribution of applicants according to their competitive ranking for a job listing
    return None

def calculate_competitive_ranking():
    #Calculates a users competitive ranking
    return None

#Post popularity compares number of applicants to a job listing to all other no. of applicants in a job listing within a specified timeframe
def get_post_popularity():
    return None

# Query for city and state data from job postings or users
jobs_cursor = collection_jobs.find({}, {'_id': 0, 'job_details.Location': 1})
users_cursor = collection_users.find({}, {'_id': 0, 'resume_fields.Contact Information.Location': 1})

@st.cache_data(ttl=3600)
def getJobLocationsList():
    return list(jobs_cursor)

@st.cache_data(ttl=3600)
def getUserLocationsList():
    return list(users_cursor)

job_locations = getJobLocationsList()
user_locations = getUserLocationsList()
# Combine the location data from job postings and users into one list
city_state_pairs = []
for job_location in job_locations:
    location_str = job_location.get('job_details', {}).get('Location', '')
    if location_str:
        city_state_pairs.append((location_str, 'job'))

for user_location in user_locations:
    location_str = user_location.get('resume_fields', {}).get('Contact Information', {}).get('Location', '')
    if location_str:
        city_state_pairs.append((location_str, 'user'))

# Initialize the geolocator (GoogleV3)
geolocator = GoogleV3(api_key=GOOGLE_API_KEY)

# Function to get coordinates from location string with retries
@st.cache_data
def geocode_location(location_str):
    try:
        location = geolocator.geocode(location_str)
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        time.sleep(2)  # Retry after a short delay
        return geocode_location(location_str)  # Recursive retry
    except Exception as e:
        print(f"Error geocoding {location_str}: {e}")
        return None, None

# Clean and geocode locations
coordinates = []
categories = []
for location_str, category in city_state_pairs:
    location_str = str(location_str).strip()
    if location_str:
        lat, lng = geocode_location(location_str)
        if lat and lng:
            coordinates.append((lat, lng))
            categories.append(category)

# If no coordinates were found, warn the user
if not coordinates:
    st.warning("No valid coordinates were found. Check the location data.")

# Create DataFrame with location and category
df = pd.DataFrame({
    'lat': [lat for (lat, lng) in coordinates],
    'lng': [lng for (lat, lng) in coordinates],
    'category': categories,
})
df['frequency'] = df.groupby(['lat', 'lng', 'category']).transform('size')

# Visualization using Plotly

# Create the scatter mapbox chart
fig = px.scatter_mapbox(df, lat="lat", lon="lng", color="category",
                        size="frequency", hover_name="category", hover_data=["lat", "lng", "frequency"],
                        color_discrete_map={"job": "red", "user": "blue"},
                        title="User and Job Locations",
                        mapbox_style="carto-positron",  # You can use different Mapbox styles
                        zoom=3)

# Set the mapbox access token for the chart
fig.update_layout(mapbox_accesstoken=MAPBOX_API_KEY)

# Show the map
def getLocationMap():
    return fig

#Job Post Analytics
applicants_cursor = collection_jobs.find({}, {'_id': 1, 'applicants': 1, 'job_details.Job Title' : 1, 'job_details.Company Name' : 1, 'job_details.Location' : 1})

@st.cache_data(ttl=3600)
def getApplicantList():
    return list(applicants_cursor)

job_posts_applicants = getApplicantList()

#Retrieves all jobs with applicants
@st.cache_data(ttl=3600)
def getJobAppTuple():
    job_app_tuple = []
    for post in job_posts_applicants:
        job_title = post.get('job_details', {}).get('Job Title', '')
        company_name = post.get('job_details', {}).get('Company Name', '')
        location = post.get('job_details', {}).get('Location', '')
        applicants = post.get('applicants', '')

        if job_title and company_name and applicants and location:
            job_app_tuple.append((job_title, company_name, applicants, location))

    return job_app_tuple

#Gathers cursor to applicants with relevant data, creates lists of specified data, finds the mode of each field
@st.cache_data(ttl=3600)
def get_applicant_modes(applicants):
    user_ids = [item['user_id'] for item in applicants]
    applicant_data = collection_users.find({'username': {'$in': user_ids}}, {'resume_fields.Education': 1,'resume_fields.Contact Information.Location':1,'resume_fields.Work Experience.Position':1,'resume_fields.Skills':1})
    locations_list = []
    skills = [{}]
    positions = []
    degrees = []
    for applicant in applicant_data:
        locations_list.append(applicant.get('resume_fields', {}).get('Contact Information', {}).get('Location',''))
        skills.append(applicant.get('resume_fields', {}).get('Skills', {}))
        for work_experience in applicant.get('resume_fields', {}).get('Work Experience', []):
            positions.append(work_experience.get('Position',''))
        for education in applicant.get('resume_fields', {}).get('Education', []):
            degrees.append(education.get('Degree',''))

    skills_list = list(itertools.chain.from_iterable(
        [value for item in skills for value in (item.values() if isinstance(item, dict) else [item])]))
    degree_counter = Counter(degrees)
    location_counter = Counter(locations_list)
    skills_counter = Counter(skills_list)
    positions_counter = Counter(positions)
    largest_degree_freq = max(degree_counter.values())
    largest_loc_freq = max(location_counter.values())
    largest_skill_freq = max(skills_counter.values())
    largest_pos_freq = max(positions_counter.values())
    degree_mode = [key for key, value in degree_counter.items() if value == largest_degree_freq]
    location_mode = [key for key, value in location_counter.items() if value == largest_loc_freq]
    skill_mode = [key for key, value in skills_counter.items() if value == largest_skill_freq]
    pos_mode = [key for key, value in positions_counter.items() if value == largest_pos_freq]
    applicant_modes = [location_mode,skill_mode,pos_mode,degree_mode]
    return applicant_modes

job_app_tuple = getJobAppTuple()
#Displays job post data
def getJobPostAnalytics():
    return job_app_tuple


