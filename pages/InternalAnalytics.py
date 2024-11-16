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

###
#This class displays analytics for internal use and triggers for testing functions
###
#TODO Applicants Analytics - apply to job post from multiple applicant profiles then extract simple data points

# Initialize Database and Session Variables
load_dotenv('../.env',override=True)
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

st.header("Locations of Users and Job Listings")

# Query for city and state data from job postings or users
job_postings = collection_jobs.find({}, {'_id': 0, 'job_details.Location': 1})
users = collection_users.find({}, {'_id': 0, 'resume_fields.Contact Information.Location': 1})

# Combine the location data from job postings and users into one list
city_state_pairs = []
for posting in job_postings:
    location_str = posting.get('job_details', {}).get('Location', '')
    if location_str:
        city_state_pairs.append((location_str, 'job'))

for user in users:
    location_str = user.get('resume_fields', {}).get('Contact Information', {}).get('Location', '')
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
st.plotly_chart(fig)

st.header("Job Post Analytics")

job_postings_applicants = collection_jobs.find({}, {'_id': 1, 'applicants': 1, 'job_details.Job Title' : 1, 'job_details.Company Name' : 1, 'job_details.Location' : 1})

job_app_tuple = []
for posting in job_postings_applicants:
    job_title = posting.get('job_details', {}).get('Job Title', '')
    company_name = posting.get('job_details', {}).get('Company Name', '')
    location = posting.get('job_details', {}).get('Location', '')
    applicants = posting.get('applicants', '')

    if job_title and company_name and applicants and location:
        job_app_tuple.append((job_title, company_name, applicants, location))

with st.expander("Jobs with Applicants List", expanded=False):
    if job_app_tuple:
        for job_title, company_name, applicants, location in job_app_tuple:
            st.subheader(job_title)
            st.write(company_name)
            st.write(location)
            st.write(f'No. of Applicants: {len(applicants)}')
            st.write('Post Popularity: ')
            st.write('Applicants Qualifications: ')
            st.write('Applicants Demographics: ')
            st.write('Applicants Salary Expectations: ')
            st.write('Applicants Match Probability: ')
