from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
from dotenv import load_dotenv
import os
import certifi
import altair as alt
from geopy.geocoders import GoogleV3
import pandas as pd
from collections import Counter
import time
from geopy.exc import GeocoderTimedOut

# Init of Database and Session Variables
load_dotenv('../.env')
uri = os.environ.get('URI_FOR_Mongo')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
tlsCAFile = certifi.where()
client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
db = client['499']
collection_jobs = db['jobs']
collection_users = db['files_uploaded']

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

# Function to get coordinates from location string
def get_coordinates(location_str):
    try:
        location = geolocator.geocode(location_str)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        time.sleep(2)  # Retry after a short delay
        return get_coordinates(location_str)  # Recursive retry
    except Exception as e:
        print(f"Error geocoding {location_str}: {e}")
        return None, None

# Clean the location data to ensure consistency
coordinates = []
categories = []
for location_str, category in city_state_pairs:
    # Ensure the location_str is a string (not a list)
    location_str = str(location_str).strip()
    if location_str:  # Only proceed if the location is not empty
        lat, lng = get_coordinates(location_str)
        if lat and lng:
            coordinates.append((lat, lng))
            categories.append(category)

# If no coordinates were found, print a warning
if not coordinates:
    print("No coordinates were found. Check the location data.")

# Count frequency of each coordinate (latitude, longitude)
counter = Counter(zip(coordinates, categories))

# Create a DataFrame for Altair
df = pd.DataFrame(counter.items(), columns=['location', 'count'])

# Flatten the location column and split into lat and lng
df['location'] = df['location'].apply(lambda x: str(x[0][0]) + ', ' + str(x[0][1]) if isinstance(x[0], tuple) else str(x[0]))

# Extract latitude and longitude from the location column
df['lat'] = df['location'].apply(lambda x: x.split(',')[0] if isinstance(x, str) else None)
df['lng'] = df['location'].apply(lambda x: x.split(',')[1] if isinstance(x, str) else None)

# Add the category and frequency columns
df['category'] = df['location'].apply(lambda x: x.split(',')[2] if len(x.split(',')) > 2 else 'unknown')
df['frequency'] = df['count']

# Ensure consistent category values
df['category'] = df['category'].apply(lambda x: x if x in ['job', 'user'] else 'unknown')

# Load a geographical background (e.g., US states)
states = alt.topo_feature('https://raw.githubusercontent.com/vega/vega-datasets/master/data/us-10m.json', feature='states')

# Background layer with the states
background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).project('albersUsa').properties(
    width=600,
    height=400
)

# Points layer with your data
points = alt.Chart(df).mark_circle(size=60).encode(
    longitude='lng:Q',
    latitude='lat:Q',
    size='frequency:Q',
    color='category:N',  # Color points by category (job/user)
    tooltip=['lat', 'lng', 'frequency', 'category']
)

# Combine the background and points
map_chart = background + points

# Display the map with Streamlit
st.altair_chart(map_chart)
