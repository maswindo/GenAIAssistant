import streamlit as st
from tools.Company.Company_Overview import generate_company_overview_data
from tools.Company.Company_Linkedin import generate_company_linkedin_data
from tools.Company.Glassdoor_Company_Reviews import generate_company_glassdoor_review_data
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
import certifi
from pymongo.server_api import ServerApi


# Load Font Awesome
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">',
    unsafe_allow_html=True
)


# Load environment variables
load_dotenv()

uri = os.environ.get('URI_FOR_Mongo')
tlsCAFile = certifi.where()
if not tlsCAFile:
    raise ValueError("tlsCAFile is not defined in the environment variables")
client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))

def get_company_linkedin_data(company_name: str):

    database_name = "499"
    collection_name = "Company_Linkedin"
    db = client[database_name]
    collection = db[collection_name]

    company_data = collection.find_one({"name": company_name})
    return company_data


def get_company_overview_data(company_name: str):
    
    # Select the database and collection
    database_name = "499"
    collection_name = "Company_Overview"
    db = client[database_name]
    collection = db[collection_name]

    company_data = collection.find_one({"company": company_name})

    print (company_data)
    return company_data

def get_company_glassdoor_review_data(company_name: str):

    # Select the database and collection
    database_name = "Company_Glassdoor_Reviews"
    collection_name = company_name
    db = client[database_name]
    collection = db[collection_name]

    # Retrieve all documents in the collection
    company_data = list(collection.find()) 

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
    

# ----------------------------------------------------Streamlit User Interface--------------------------------------------------


def load_company_data():
    company_name = st.session_state["company_name"]  # Access company_name from session state

    if company_name:
        print("hello I'm in company_name")
        if st.session_state["company_data"] is None:
            # Generate company data (formatted string)
            company_data = get_company_overview_data(company_name)
            if not company_data:
                company_data = generate_company_overview_data(company_name)
            st.session_state["company_data"] = company_data

        if st.session_state["linkedin_data"] is None:
            # Load LinkedIn data
            company_linkedin_data = get_company_linkedin_data(company_name)
            if not company_linkedin_data:
                company_linkedin_data = generate_company_linkedin_data(company_name)
            st.session_state["linkedin_data"] = company_linkedin_data

        if st.session_state["glassdoor_data"] is None:
            company_glassdoor_review_data = get_company_glassdoor_review_data(company_name)
            if not company_glassdoor_review_data:
                days = 90
                company_glassdoor_review_data = generate_company_glassdoor_review_data(company_name, days)
            st.session_state["glassdoor_data"] = company_glassdoor_review_data

    else:
        st.error("Please enter a valid company name.")


def display_company_data():
            
    company_data = st.session_state["company_data"]
    company_linkedin_data = st.session_state["linkedin_data"]
    company_name = st.session_state["company_name"]  

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

    # Glassdoor Reviews Section
    st.write("#### Glassdoor Reviews")

    db = client["Company_Glassdoor_Reviews"]
    collection = db[company_name]

    # Fetch distinct values for filters
    job_titles = collection.distinct("employee_job_title")
    locations = collection.distinct("employee_location")
    years_at_company = collection.distinct("employee_length")
    statuses = collection.distinct("employee_status")

    # Initialize session state for filters and reviews
    if "filtered_reviews" not in st.session_state:
        st.session_state["filtered_reviews"] = None

    with st.form(key="glassdoor_filters_form"):
        st.write("### Glassdoor Filters")
        
        # User inputs for filters
        job_title = st.selectbox("Filter by Job Title", ["All"] + sorted(job_titles))
        location = st.selectbox("Filter by Location", ["All"] + sorted(locations))
        years = st.selectbox("Filter by Minimum Years at Company", ["All"] + sorted(years_at_company))
        status = st.selectbox("Filter by Employee Status", ["All"] + sorted(statuses))
        count = st.slider("Number of Top Reviews", min_value=1, max_value=10, value=5)

        # Submit button for the form
        submitted = st.form_submit_button("Get Reviews")

    # Process the form submission
    if submitted:
        # Build query based on selected filters
        query = {}
        if job_title != "All":
            query["employee_job_title"] = {"$regex": job_title, "$options": "i"}
        if location != "All":
            query["employee_location"] = {"$regex": location, "$options": "i"}
        if years != "All":
            query["employee_length"] = {"$gte": int(years)}
        if status != "All":
            query["employee_status"] = {"$regex": status, "$options": "i"}

        # Fetch filtered top reviews
        filtered_reviews = {
            "pros": list(collection.find({**query, "review_pros": {"$exists": True}})
                        .sort("count_helpful", -1)
                        .limit(count)),
            "cons": list(collection.find({**query, "review_cons": {"$exists": True}})
                        .sort("count_helpful", -1)
                        .limit(count))
        }

        # Store the filtered reviews in session state
        st.session_state["filtered_reviews"] = filtered_reviews

        # Display reviews only if they exist in session state
        if st.session_state["filtered_reviews"]:
            filtered_reviews = st.session_state["filtered_reviews"]

            # Display Top Pro Reviews
            st.subheader("Top Pro Reviews")
            if filtered_reviews["pros"]:
                # Create columns for horizontal layout
                col1, col2, col3 = st.columns(3)  # Adjust the number of columns as needed
                columns = [col1, col2, col3]  # List to cycle through columns

                for idx, review in enumerate(filtered_reviews["pros"]):
                    with columns[idx % len(columns)]:  # Cycle through columns
                        st.write(f"**Pros:** {review.get('review_pros')}")
                        st.write(f"**Job Title:** {review.get('employee_job_title')}")
                        st.write(f"**Location:** {review.get('employee_location')}")
                        st.write(f"**Helpful Count:** {review.get('count_helpful', 0)}")
                        st.write("---")
            else:
                st.write("No Pro reviews found for the selected filters.")

            # Display Top Con Reviews
            st.subheader("Top Con Reviews")
            if filtered_reviews["cons"]:

                # Create columns for horizontal layout
                col1, col2, col3 = st.columns(3)  # Adjust the number of columns as needed
                columns = [col1, col2, col3]  # List to cycle through columns

                for idx, review in enumerate(filtered_reviews["cons"]):
                    with columns[idx % len(columns)]:  # Cycle through columns
                        st.write(f"**Cons:** {review.get('review_cons')}")
                        st.write(f"**Job Title:** {review.get('employee_job_title')}")
                        st.write(f"**Location:** {review.get('employee_location')}")
                        st.write(f"**Helpful Count:** {review.get('count_helpful', 0)}")
                        st.write("---")
            else:
                st.write("No Con reviews found for the selected filters.")

    
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


# Ensure the session state keys exist
if "current_company_name" not in st.session_state:
    st.session_state["current_company_name"] = ""

if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""

if "company_data" not in st.session_state:
    st.session_state["company_data"] = None

if "linkedin_data" not in st.session_state:
    st.session_state["linkedin_data"] = None

if "glassdoor_data" not in st.session_state:
    st.session_state["glassdoor_data"] = None

# Function to handle company name change
def handle_company_name_change():
    current_name = st.session_state["current_company_name"]
    # Do nothing if the input field is empty
    if current_name.strip() == "":
        print("Search bar is cleared; no action taken.")
        return  # Exit early, keeping everything as it is

    # Check if the company name has changed
    if st.session_state["company_name"] != current_name:
        print("Company name changed")
        # Clear session state for company-specific data
        st.session_state.update({
            "company_data": None,
            "linkedin_data": None,
            "glassdoor_data": None,
        })
        # Update the company name and load data
        st.session_state["company_name"] = current_name
        print(f"Loading data for {current_name}")
        load_company_data()
        print("Loaded company data")

# Text input for company name (kept at the top)
st.text_input(
    "Enter a Company Name",
    key="current_company_name",  
    on_change = handle_company_name_change  # Trigger when the value changes
)


if st.session_state["company_data"]:
    display_company_data()