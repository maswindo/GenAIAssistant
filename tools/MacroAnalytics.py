import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import requests
import pandas as pd
import plotly.express as px
from geopy.geocoders import GoogleV3
import streamlit as st
from tools.Infer_User_Preferences import get_inferred_occupation
from openai import OpenAI

# Load environment variables
load_dotenv('../.env')
user_id = os.getenv('CAREERONE_USER_ID')
api_key = os.getenv('CAREERONE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

openai = OpenAI(api_key=openai_api_key)
uri = os.environ.get('URI_FOR_Mongo')
tlsCAFile = certifi.where()
client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
db = client['499']
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

if not uri or not GOOGLE_API_KEY:
    st.error("Environment variables are missing. Please check the .env file.")
    st.stop()

# Initialize the geolocator (GoogleV3)
geolocator = GoogleV3(api_key=GOOGLE_API_KEY)

us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming"
]
# Dictionary mapping state names to abbreviations
state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}
# Function to convert state names to abbreviations
def convert_state_names_to_abbr(state_names):
    return [state_abbreviations.get(state, state) for state in state_names]

# Find salary data for keyword(occupation) and location given
def get_local_salary(keyword, location):
    base_url = "https://api.careeronestop.org/v1/comparesalaries/{userId}/wage"
    enable_metadata = "false"
    url = base_url.format(userId=user_id)

    # Set the parameters
    params = {
        "keyword": keyword,
        "location": location,
        "enableMetaData": enable_metadata
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        state_wages = data.get('OccupationDetail', {}).get('Wages', {}).get('StateWagesList', [])
        annual_wages = [wage for wage in state_wages if wage.get('RateType') == "Annual"]
        if annual_wages:
            wage_data = annual_wages[0]  # Pick the first matching wage entry
            return wage_data
        else:
            print("No annual wage data available for this location.")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_occupation_skills():
    keyword = get_inferred_occupation()
    location = "New York"
    base_url = "https://api.careeronestop.org/v1/occupation/{userId}/{keyword}/{location}"
    enable_metadata = "false"

    url = base_url.format(userId=user_id)

    # Set the parameters
    params = {
        "location": location,
        "keyword": keyword,
        "enableMetaData": enable_metadata
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Choropleth map function
@st.cache_data(ttl=3600)
def get_salary_map(wage_data,occupation):
    median_salary = []
    states = []

    # Collect data from wage_data
    for wage in wage_data:
        median_salary.append(float(wage['Median']))  # Ensure the median salary is a float
        states.append(wage['AreaName'])

    # Convert state names to abbreviations
    states_abrv = convert_state_names_to_abbr(states)

    # Create DataFrame with location and category
    df = pd.DataFrame({
        'State': states,
        'Median Salary': median_salary
    })

    # Ensure that 'Median Salary' is a numeric column for proper gradient rendering
    df['Median Salary'] = pd.to_numeric(df['Median Salary'], errors='coerce')

    # Create choropleth map
    fig = px.choropleth(
        df,
        locations=states_abrv,
        locationmode='USA-states',
        color='Median Salary',
        hover_name="State",
        hover_data={"State": False, "Median Salary": True},
        scope = "usa",
        title=f"Salaries By State - {occupation}",
        color_continuous_scale="RdYlGn",  # Green to Red color scale
        range_color=[df['Median Salary'].min(),  df['Median Salary'].max()]
    )
    fig.update_layout(
        geo=dict(
            center=dict(lat=37.0902, lon=-95.7129),  # Center of the USA (approx. lat/lon)
            projection_type="albers usa",
            projection_scale=1,
            showcoastlines=True,
            coastlinecolor="black",
            showland=True,
            landcolor="black"
        ),
        title={
            'text': f"Salaries By State - {occupation}",
            'x': 0.4,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top',
            'font': {
                'size': 24,
                'color': 'white'
            }
        },
        margin={"r": 0, "t": 100, "l": 0, "b": 0},
    )
    return fig

# Function to get job salaries by state
@st.cache_data(ttl=3600)
def get_salaries_map(occupation):
    wage_data = []
    for state in us_states:
        wage_data.append(get_local_salary(occupation, state))  # Get wage data for each state
    return get_salary_map(wage_data,occupation)  # Return the choropleth map

# Choropleth map function, for parsing multiple occupations, returns a tuple
@st.cache_data(ttl=3600)
def get_salary_maps(wage_data):
    # Initialize empty lists for the three figures
    figs = []

    # Loop through each occupation and create a figure
    for occupation, data in wage_data.items():
        median_salary = []
        states = []

        # Collect data for the specific occupation
        for wage in data:
            median_salary.append(float(wage['Median']))  # Ensure the median salary is a float
            states.append(wage['AreaName'])

        # Convert state names to abbreviations
        states_abrv = convert_state_names_to_abbr(states)

        # Create DataFrame with location and category for the current occupation
        df = pd.DataFrame({
            'State': states,
            'Median Salary': median_salary
        })

        # Ensure that 'Median Salary' is a numeric column for proper gradient rendering
        df['Median Salary'] = pd.to_numeric(df['Median Salary'], errors='coerce')

        # Create choropleth map for the current occupation (fig1, fig2, or fig3)
        fig = px.choropleth(
            df,
            locations=states_abrv,
            locationmode='USA-states',
            color='Median Salary',
            hover_name="State",
            hover_data={"State": False, "Median Salary": True},
            scope="usa",
            title=f"Salaries By State - {occupation}",
            color_continuous_scale="RdYlGn",  # Green to Red color scale
            range_color=[df['Median Salary'].min(), df['Median Salary'].max()]
        )
        fig.update_layout(
            geo=dict(
                center=dict(lat=37.0902, lon=-95.7129),  # Center of the USA (approx. lat/lon)
                projection_type="albers usa",
                projection_scale=1,
                showcoastlines=True,
                coastlinecolor="black",
                showland=True,
                landcolor="black"
            ),
            title={
                'text': f"Salaries By State - {occupation}",
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.98,
                'yanchor': 'top',
                'font': {'size': 24, 'color': 'black'}
            },
            margin={"r": 0, "t": 200, "l": 0, "b": 0},
        )

        # Append the generated figure to the list
        figs.append(fig)

    # Return the three figures as a tuple
    return tuple(figs[:3])

@st.cache_data(ttl=3600)
def get_salaries_args(occupations):
    wage_data = {}
    for occupation in occupations:
        occupation_wage_data = []
        for state in us_states:
            occupation_wage_data.append(get_local_salary(occupation, state))  # Get wage data for each state

        wage_data[occupation] = occupation_wage_data

    return get_salary_maps(wage_data)  # Return the choropleth map

@st.cache_data(ttl=3600)
def get_occupation_statistics(occupation,location='New York'):
    prompt = (
        f"Please provide important statistics about the occupation of {occupation}. Present the information in a structured format, including the following sections:"
        "Job Outlook: Projected growth rate over the next [X] years."
        f"Average Salary: The median salary for the occupation in {location}."
        f"Employment Numbers: Total number of people employed in this occupation in {location}."
        "Educational Requirements: Typical level of education required for the occupation."
        "Job Duties: Common responsibilities and tasks associated with the occupation."
        "Work Environment: Typical work conditions, including hours, location, and work settings."
        "Key Skills: Essential skills needed for the job."
        f"Industry Demand: Industries in which the occupation is in high demand in {location}."
        "Please provide relevant data, including citations from reputable sources where applicable."
    )
    behaviour = (
        "You are an occupation data analyst tasked with outputting accurate data that is concise and easy to read while also being impactful to a person who's prospective occupation is given "
        "Your goal is to provide precise information about the occupation and statistics regarding it in the current labor market locally, nationally, and globally."
    )
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": behaviour}
        ]
    )

    # Extract the assistant's reply
    occupation_data = response.choices[0].message.content.strip()

    return occupation_data
