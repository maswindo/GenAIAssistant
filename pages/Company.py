import streamlit as st
from tools.CompanyDataGenerator import generate_company_data
from tools.ProxyCurlLinkedIn import get_leadership_team_info
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
import certifi
from pymongo.server_api import ServerApi

import plotly.graph_objects as go
import pandas as pd

import time


st.markdown(
    """
    <style>
    

    </style>
    """,
    unsafe_allow_html=True
)
# Load Font Awesome
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">',
    unsafe_allow_html=True
)


# Load environment variables
def get_company_linkedin_data(company_name: str):
    load_dotenv()
    uri = os.environ.get('URI_FOR_Mongo')
    tlsCAFile = certifi.where()
    if not tlsCAFile:
        raise ValueError("tlsCAFile is not defined in the environment variables")
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))

    # Select the database and collection
    database_name = "499"
    collection_name = "Company_Linkedin"
    db = client[database_name]
    collection = db[collection_name]

    company_data = collection.find_one({"name": company_name})
    client.close()
    return company_data


def get_company_data(company_name: str):
    load_dotenv()
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

    company_data = collection.find_one({"company": company_name})
    client.close()

    print (company_data)
    return company_data

def format_company_type(company_type_raw):
    company_type_mapping = {
        "EDUCATIONAL": "Educational Institution",
        "GOVERNMENT_AGENCY": "Government Agency",
        "NON_PROFIT": "Nonprofit",
        "PARTNERSHIP": "Partnership",
        "PRIVATELY_HELD": "Privately Held",
        "PUBLIC_COMPANY": "Public Company",
        "SELF_EMPLOYED": "Self-Employed",
        "SELF_OWNED": "Sole Proprietorship"
    }
    # Return the mapped value or format the raw type if not found
    return company_type_mapping.get(company_type_raw, company_type_raw.replace('_', ' ').title())

def format_company_size(company_size):
    if isinstance(company_size, list) and len(company_size) == 2:
        lower_bound = company_size[0]
        upper_bound = company_size[1]
        
        # If upper bound is None, display as "10,001+ employees"
        if upper_bound is None:
            return f"{lower_bound:,}+ employees"
        else:
            return f"{lower_bound:,} - {upper_bound:,} employees"
    return "Size not available"
    

# ------------------------------------------------Streamlit User Interface-----------------------------------------



def load_company_data():
    company_name = st.session_state["company_name"]  # Access company_name from session state
    if company_name:
        # Generate company data (formatted string)
        company_data = get_company_data(company_name)

        if not company_data:
            company_data = generate_company_data(company_name)
        company_linkedin_data = get_company_linkedin_data(company_name)
        if not company_linkedin_data:
            st.write("Company linked in data not found")
            st.stop()

        # Display the retrieved or scraped data
        if company_data:

            col1, col2 = st.columns(2)
            with col1:

                
                local_profile_pic_path = company_linkedin_data.get("local_profile_pic_path")
                if local_profile_pic_path:
                    st.image(local_profile_pic_path, width=150)

                
                

            with col2:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Industry**: {company_linkedin_data.get('industry', 'N/A')}")

                    company_type_raw = company_linkedin_data.get('company_type', 'N/A')
                    company_type = format_company_type(company_type_raw)
                    st.write(f"**Company Type:** {company_type}")
                    st.write(f"**Founded Year**: {company_linkedin_data.get('founded_year', 'N/A')}")
                with col2:
                    company_size = company_linkedin_data.get('company_size', 'N/A')
                    formatted_company_size = format_company_size(company_size)
                    st.markdown(f"<p style='font-size: 16px;'><i class='fas fa-users'></i> {formatted_company_size}</p>", unsafe_allow_html=True)

                    hq = company_linkedin_data.get("hq", {})
                    if hq:
                        location_text = f"{hq.get('city', '')}, {hq.get('state', '')}, {hq.get('country', '')}"
                        st.markdown(f"<p style='font-size: 16px;'><i class='fas fa-map-marker-alt'></i> {location_text}</p>", unsafe_allow_html=True)
                    website = company_linkedin_data.get('website', '')

                    # Format the website text to show without hyperlink styling
                    if website:
                        st.markdown(
                            f"<p style='font-size: 16px;'><i class='fas fa-globe'></i> {website}</p>",
                            unsafe_allow_html=True
                        )

            col1, col2, col3 = st.columns(3)

            with col1:
                # Display the company title
                st.title(company_data.get('company_name', company_name))
            
            with col3:
                st.text_input(
                    "", 
                    placeholder="Type Company Job"
                )

            
            col1, col2, col3 = st.columns(3)
          

            
            with col1:
                st.markdown("#### Overview")
                st.write(company_data.get('overview', 'Overview not available'))
            with col2:
                st.write(f"#### Mission")
                st.write(company_data.get('mission', 'Mission and values not available'))
            with col3:
                st.write(f"#### Culture")
                st.write(company_data.get('culture', 'Culture information not available'))
                
            
            
            st.write(f"#### Company Values")            
            # Get the values from company data
            values = company_data.get('values', [])
            if values:
            # Create 5 columns
                cols = st.columns(5)
                # Distribute values across the columns
                for idx, value in enumerate(values):
                    col = cols[idx % 5]  # Select the column based on index
                    col.write(value)  # Write the value in the appropriate column
            else:
                st.write("Values not available.")


            
            # Specialties Section
            st.write(f"#### Specialties") 
            # Sample specialties data (replace this with your actual data from MongoDB)
            specialties = company_linkedin_data.get("specialities", [])

            if specialties:
                for specialty in specialties:
                    st.write(specialty)
            else:
                st.write("No specialties available.")


                
            st.write(f"#### Leadership") 
            leadership_info = company_data["leadership"]
            if leadership_info:
            # Create columns based on the number of leadership members
                columns = st.columns(len(leadership_info))

                 # Loop through each leadership member with an integer index
                for i, member in enumerate(leadership_info):
                     with columns[i]:  # Use `i` as the index for `columns`
                        st.markdown(f"**{member['name']}**")
                        st.write(member["description"])
                         # Display the LinkedIn profile link with the icon
                        # Display the LinkedIn icon as a link without additional text
                        st.markdown(
                            f'''
                            <a href="{member["linkedin_url"]}" target="_blank" style="text-decoration: none;">
                                <i class="fab fa-linkedin" style="
                                    font-size: 24px; 
                                    color: #ffffff; 
                                    background-color: #000000; 
                                    padding: 10px; 
                                    border-radius: 4px;">
                                </i>
                            </a>
                            ''',
                            unsafe_allow_html=True
                        )
    
            else:
                st.write("Leadership information not available.")



            # Affiliated Companies
            st.write(f"#### Affiliated Companies")

            affiliated_companies = company_linkedin_data.get("affiliated_companies", [])
            if affiliated_companies:
                for company in (affiliated_companies):
                        name = company.get("name", "N/A")
                        industry = company.get("industry", "Industry not available")
                        st.markdown(f"**{name}**")
                        st.write(industry)
            else:
                st.write("No affiliated companies available.")

            # News and Updates Section
            st.write(f"#### News and Updates")
            updates = company_linkedin_data.get("updates", [])
            updates_with_images = [update for update in updates if update.get("image")]
            if updates:
                    # Display the top 3 updates in three columns
                    cols = st.columns(3)
                    for i in range(3):
                        if i < len(updates_with_images):  # Ensure there are enough updates with images
                            update = updates_with_images[i]
                            # Extract the update details
                            text = update.get('text', 'No update text available')
                            posted_on = update.get('posted_on', {})
                            date_str = f"{posted_on.get('day', 'N/A')}/{posted_on.get('month', 'N/A')}/{posted_on.get('year', 'N/A')}"
                            image_url = update.get('image')

                            # Display each update in its respective column
                            with cols[i]:
                                st.image(image_url, width=300)  # Adjust width as desired
                                st.write(f"**{text}**")
                                st.write(f"Date: {date_str}")
            else:
                st.write("No recent updates available.")

        else:
            st.write("Unable to retrieve company data.")
    else:
        st.error("Please enter a valid company name.")
        
# Place the search bar at the top of the page
col1, col2, col3 = st.columns(3)
with col1:
    st.text_input(
        "", 
        key="company_name", 
        on_change=lambda: st.session_state.update({"load_data": True}),  # Flag to load data on Enter
        placeholder="Type Company Name"
    )

# Only call load_company_data if the search bar has been triggered
if st.session_state.get("load_data") and st.session_state.get("company_name"):
    st.session_state["load_data"] = False  # Reset the flag after loading data
    load_company_data()

