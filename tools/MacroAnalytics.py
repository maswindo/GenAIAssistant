import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv('../.env')
user_id = os.getenv('CAREERONE_USER_ID')
api_key = os.getenv('CAREERONE_API_KEY')

#TODO AI generate related occupations to search database with, run getLocalSalary on all occupations, local companies with these occupations, connect to corp page
#TODO Create Internal Analytics Functionality
"""
Problem Outline

Service:
Provide user with important information and actionable plans that, when completed, will likely improve the probability of them achieving an optimal employment outcome

Required Data:
A lot of data. 
Local, National, Global.
Economic, Labor, Location, Market
User Data

Example Statistics:
Salaries for occupation x has changed
Competitiveness for occupation x has changed
Location x has experienced growth in field y
Time to employment for field/occupation x has decreased in area y
If working at company x, location y is the optimal place to live
Skill demand in location x, field y has changed
Growth in industry x has changed in location y
Cost of living/salary in field/occupation x is y
Skill x prevalence has changed in field y
etc.

Example Directives:
Learn skill x
Move to residence x
Change salary expectations to x
Apply to occupation x
Follow career path x
Plan for economical situation xyz
Discover company x
Expect conditions x
Attend conference x
Read article x
etc.

System Requirements:
Operates passively
Continuously Gathers Data
Performs analyses dynamically
Determines confidence of analyses
Determines informational priority
Dynamically chooses relevant data
Dynamically chooses relevant tools
Dynamically chooses relevant agents

Questions:

Q: Where/how does this process begin?
A: When the user creates an account
Q: What happens when the user creates an account?
A: All of their data is sent to the AI agents

Q: What always exists in the system?
A: Data from external resources, Tools to gather data from external resources
Q: What happens if data externally and internally conflict?
A: Internal data is updated to reflect external data changes
Q: What happens if external data sources conflict on the supposed same information?
A: A weighted average based on reputability, data post date, internal analyses of trends

Q: How many agents are there?
A:
Q: What limitations determine that an agent should be implemented?
A: Complex Decision Making
Q: What determines if a decision is complex?
A: 
    1. Large number of variables and diversity of type of variables (e.g., quantitative vs. qualitative, measurable vs. abstract) 
    2. Interdependency among variables
    3. Uncertainty and Unpredictability
    4. Conflicting objectives
    5. Coordination between stakeholders
    6. Dynamic context
    7. Long term impacts and feedback loops
    8. Ambiguity and Subjectivity
    9. Resource Constraints
    10. Adaptive or Real-Time Decision Making
Q: What decisions need to be made?
A: 
Q: How do i know if these decision conditions exist?
A: This is a complex question
ChatGPT Response from question, missing last 3 because i ran out of tokens:
1. Too Many Variables
Identify: List all factors you think affect the decision. If the list feels unmanageable, you’re likely dealing with too many.
Solution: Prioritize the top 3–5 most influential factors and focus on them first.
2. Interdependencies Among Variables
Identify: Check if changing one factor seems to impact others (e.g., changing cost affects quality). Ask, “If I adjust this, does it change anything else?”
Solution: Map out or make notes of these connections. Focus on pairs that seem tightly connected and consider them together.
3. Uncertainty or Missing Information
Identify: Look for questions you can’t confidently answer about the situation. If there are many unknowns, uncertainty is high.
Solution: Make simple “best-case” and “worst-case” assumptions. Proceed with caution or gather more data if possible.
4. Conflicting Goals
Identify: List all objectives you’re trying to achieve. If two or more seem to oppose each other (e.g., low cost vs. high quality), there’s a conflict.
Solution: Rank objectives by importance and decide which ones you’re willing to compromise on.
5. Multiple Stakeholders
Identify: Count the number of people/groups whose input or buy-in you need. More than a few indicates complex coordination.
Solution: Identify common ground or shared goals first. Prioritize decisions that align with most stakeholders’ interests.
6. Changing Conditions
Identify: Think about how stable the environment is. If it’s frequently changing or unpredictable, this applies.
Solution: Make a flexible plan that can be adjusted easily. Schedule regular check-ins to revisit the decision.
7. Long-Term Implications
Identify: Ask if the effects of the decision extend far into the future or affect future decisions.
Solution: Weigh the pros and cons of short-term vs. long-term benefits, favoring long-term if stability is essential.

Q: Does this^ mean i need to create an agent to evaluate complexity?
A: Yes
Q: Does this imply the first step in dynamically created agents?
A: Yes
Q: How do I avoid this?
A: Answer all complex questions that are outside the scope of the project
Q: What is the first question the system need to answer?
A: What is the best possible outcome for the user?
Q: How do i determine this?
A: Inference or allow user to set goals
Q: How do i determine this with inference?
A: For actual - see whats available, for ideal - calculate whats possible
1. Take all user data and determine the occupations they would best fit
2. Determine if these jobs are available locally
3. If none available find occupations with the next highest relevance and repeat
4. If none are available expand search radius
5.
Create an ideal outcome to measure actual outcomes to!!

Define the Ideal in Quantifiable Terms:
Specify all metrics, benchmarks, or criteria associated with the ideal outcome. The clearer and more measurable these are, the easier it will be to gauge actual performance.
Map Key Characteristics:
Describe the conditions that would need to exist for the ideal to be achieved. These could include factors like resource availability, time constraints, technical capabilities, and external conditions.
Visualize Success Across All Stages:
Map out the ideal process from start to finish, identifying what optimal progress looks like at each stage. This will help you assess deviations and maintain a closer alignment between actual progress and the ideal.
Anticipate Variations and Tolerances:
Establish acceptable ranges around the ideal outcome that would still signify successful outcomes. This helps to create flexibility when moving from the ideal to practical implementation, giving a clearer path to follow.
                                                                                
Example Ideal: (assumes a target job exists)
1. Preparation Stage 
Industry Familiarity Score: 90%+ coverage of industry knowledge
Skill Readiness Score: 100% of required skills and certifications met
Resume Quality Score: 90% alignment with job requirements
2. Application Stage
Relevance Score: 90%+ skills match for selected positions
Application Accuracy Rate: 100% correct and tailored submissions
Application Tracking Completion Rate: 100% of applications tracked with status updates
3. Interview Process
Interview Invitation Rate: 50%+ of applications result in interviews
Interview Readiness Score: 95% completion of preparation tasks
Interview Success Rate: 70%+ progression to next interview stage
4. Offer Stage
Offer Match Score: 90%+ alignment with desired salary, benefits, and expectations
Job Satisfaction Prediction Score: 85%+ satisfaction prediction based on criteria
Offer Acceptance Rate: 100% acceptance of the best-matching offer
5. Onboarding and Retention Stage
Onboarding Completion Rate: 100% of tasks completed within 30 days
Engagement Score: High engagement with 90%+ goal achievement
Retention Rate: 100% retention at 6, 12, and 24 months

Assumptions:
User has no preferences (giving the user what they want vs giving whats best for them)

Step 1:
Create ideal employment process
Step 2: 
Take analysis of current situation
    a. Calculate alignment to ideal
        Calculate Employee-Value Proposition (to compare short commutes and low wage vs long commutes and high wages, if priorities unspecified)
    b. Calculate probabilities of job process stages
    c. Compare job listings based on probability of success and value to user
Step 3:
Deliver info related to highly probable and highly valuable outcomes


Ideal Metrics:
Pre-Prep

Self determination theory
Company fit:
Employee Value Proposition (EVP)
Quantitative

Salary
Bonuses
Stock options
Health insurance
Retirement plans
Paid time off (PTO)
Gym memberships
Company vacations
Training

Qualitative

Career growth,
Leadership quality
Role alignment
Trust and collaboration
Team relationships
Company culture
Low pay (but comparable to industry)
Rapid career growth
Strong reputation globally
Strong commitment to social justice.
Hard-charging environment but striving to improve well-being and flexibility
:

Information Gathering Processes:
Targeted
Exploratory
Predictive
Q: How do I utilize these?
A: 

"""
"""
1.  Take resume_fields and other information if available
2.  Take job details and company details
3.  Take compatibility and resume scores
4.  Take macro data
5.  Assess how trends will affect user
"""
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
#Find salary data for keyword(occupation) and location given
def getLocalSalary(keyword, location):
    import requests

    # Define the base URL and parameters
    base_url = "https://api.careeronestop.org/v1/comparesalaries/{userId}/wage"
    enable_metadata = "false"  # Set to "false" to exclude metadata if desired

    # Format the full URL with user ID
    url = base_url.format(userId=user_id)

    # Set the parameters
    params = {
        "keyword": keyword,
        "location": location,
        "enableMetaData": enable_metadata
    }

    # Set the headers for authentication and content type
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract wages
        state_wages = data.get('OccupationDetail', {}).get('Wages', {}).get('StateWagesList', [])
        annual_wages = [wage for wage in state_wages if wage.get('RateType') == "Annual"]

        if annual_wages:
            wage_data = annual_wages[0]  # Pick the first matching wage entry
            print("Occupation Title:", data['OccupationDetail']['OccupationTitle'])
            print("Rate Type:", wage_data['RateType'])
            print("Median Annual Salary:", wage_data['Median'])
            print("State:", wage_data['AreaName'])
        else:
            print("No annual wage data available for this location.")
    else:
        # Handle errors
        print(f"Error: {response.status_code} - {response.text}")


uri = os.environ.get('URI_FOR_Mongo')
tlsCAFile = certifi.where()
client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
db = client['499']

def getJobSalariesByState():
    for state in us_states:
        getLocalSalary("Software Developers",state)

getJobSalariesByState()
"""
collection_user_data = db['files_uploaded']
user_cursor = collection_user_data.find_one({'username': username},)
user_data = list(user_cursor.get('resume_fields', {}))"""




