# Overview of Contributions

 - Resume parsing
 - Job listing parsing
 - Job application and listing page
 - Internal analytics
 - Developer dashboard
 - MacroAnalytics (Planned)
 - Merged most of Shreya's Branch
 - Insights Page
 - Paths 
.
## Resume Parser - tools/ResumeProcessor.py
**APIs Added**
None
**Libraries Added:**
python-docx~=1.1.2
*Used for parsing Docx Files*
**Location of Trigger**
DevDashboard Page
**Use Case**
Parses active logged in user
**Design**
Uses OpenAI GPT API to parse user's resume and stores data in JSON format to user-associated doc in MongoDB database
**Plans**
Will modify to process all users stored in database automatically in backend
**Notes**
None

## Job Listing Parser - tools/JobPostProcessor.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
DevDashboard Page
**Use Case**
Parses all job listings stored.
Currently parses all .txt files from a folder named Jobs in root directory.
**Design**
Uses OpenAI GPT API to parse user's resume and stores data in JSON format to user-associated doc in MongoDB database
**Plans**
Will modify to process all jobs stored in database automatically in backend
**Notes**
Job Listing sourcing is not finalized. 
Need to find an API that is available and scalable. 
Datasets may be used temporarily but are not convenient for a dynamic system.

## Job Listing and Application Page - pages/JobListing.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
JobListings Page
**Use Case**
Lists all jobs in our database and allows user to apply to them
**Design**
Queries database and lists jobs. Users limited to apply once.
**Plans**
Job listings should have a success/compatibility score. Clicking apply should lead to page with more information about the job and the scoring analytics. Must connect to rest of team's projects.
**Notes**
Currently used for testing job listing applicant statistical analyses


## Internal Analytics - tools/InternalAnalytics.py
**APIs Added**
Mapbox (Requires Key, Freemium - Likely will not reach paid threshold for testing)
*For Map Graphics*
GoogleV3 (Requires Key, Freemium - Likely will not reach paid threshold for testing)
*For Location Name-Coordinate conversions*
**Libraries Added:**
Plotly
*For analytic graphing and plotting*
Pandas
*For data structuring and formatting*
Geopy
*For Location Name_Coordinate conversions*
**Location of Trigger**
JobListings Page
**Use Case**
Forms basis for backend analytics tools
**Design**
Displays location of users and job listings currently stored in MongoDB database on an interactive world map.
Displays a job listing's applicants analytics.
**Plans**
Must establish more analytics that can be easily derived to allow the multi-agent system to produce more accurate results.
**Notes**
Every analytics process avaiable is essentially a tool that the multi-agent system can utilize in its calculations. The more data we can derive from the less likeliness of hallucinations, bad math, and weak confidence in analyses.
Should prioritize univariate analytics

## DevDashboard - pages/DevDasboard.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
DevDashboard
**Use Case**
Page for developers to test backend or WIP functions
**Design**
Buttons trigger function calls
**Plans**
Will merge internal analytics into this page 
**Notes**
None

## tools/MacroAnalytics (WIP) - MacroAnalytics.py
**APIs Added**
CareerOne,Google
**Libraries Added:**
Plotly,Pandas,Geopy,GoogleV3
**Location of Trigger**
MacroAnalytics
**Use Case**
Perform statistical analysis or provide the tools for AI to do so to derive meaningful insights from external uncontrolled and dynamic data. Data and insights will be relevant to the user.
**Design**
A mix of hard coded analytic algorithms to derive insights, data sourcing from API's, and tools for AI to derive statistical analyses of its own.
**Plans**
Could provide more detailed information, requires more connections to good data sources/APIs
**Notes**
None

## Insights - pages/Insights.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
None
**Use Case**
Displays/provides the most optimal actionable suggestions, information and analytics to user. Provides user with the most sensible next steps forward in the employment process including current optimal probabilities of actions and future actionable planning. 
I.E
A skill that could be valuable to attain given location, field, experience, market, etc.
A job listing that has a high probability of being compatible while also being optimal for user in the context of all user info obtained as of yet
A location that will likely be optimal if relocated
**Design**
Will use macroanalytics and a combination of all data in the system to derive insights using multi-agent system
**Plans**
Will create
**Notes**
Currently only planning and hypothesis

## Trends - pages/Trends.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
Trends page
**Use Case**
Display trends relevent to user about related occupation and important information contextually about it to provide user with an understanding the career
**Design**
Calls for inferred user optimal occupation based on user data and provides statistics and maps using several libraries
**Plans**
Would be useful to have the option to select from multiple different optimal occupations to view data
**Notes**
None

## pages/Paths.py and tools/Pathing.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
Paths page
**Use Case**
Display optimal career paths based on user data and suggests relevant jobs in database
**Design**
Simple prompt with necessary active user data and current database
**Plans**
Front-End should display info in a more intuitive way. Mapping career prospects should read left to right in some sort of graphic display that draws attention to information in an intuitive way.
**Notes**
None

## tools/Infer_User_Preferences.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
Trends Page
**Use Case**
Infer data/conclusions about the user based on user data
**Design**
Simple prompt with necessary active user data and current database
**Plans**
Could be expanded to infer many other things. Should be developed to become its own multi-agent node
**Notes**
None

## tools/Embeddings.py
**APIs Added**
None
**Libraries Added:**
None
**Location of Trigger**
Trends(planned)
**Use Case**
Incorporate internal static data that the AI must use for recall to perform accurate function calling
**Design**
Generic OpenAI embeddings procedure
**Plans**
Needs to be developed
**Notes**
Example: CareerOne requires specific titles for functions to retrieve data correctly, therefore a static list of data provided by them needs to be recalled by the AI for no-fault use.
Should contain all initializations required for teh internal database to be connected to the AI model.

## Bug Fixes and Modifications

 - Removed Unnecessary duplicate side bar in Login.py
 - Original process_resume call returned a string conversion of a resume pdf, rename appropriately to resume_to_text - process_resume now parses and stores resume data to MongoDB
 - Various bug fixes or reformatting
 - Due to my Macbook Model(16in 2019 - Intel Chip), my base python interpreter is a lower version. Had to install latest python versions via homebrew

# Platform Plans

 - Implement multi-agent system
 - Redesign frontend for at-scale user oriented functionality
 - Security and privacy features
 - Original system design was a chatbot, we are transitioning towards a fully autonomous and hands-free system

## Metrics to Judge Operability (Tentative)

 - Time to Employment
 - Compatibility-Employment Ratio
 - Token-Employment Ratio

## Multi-Agent System Design Plans
RAG based design necessary.
System should build context from external sources, internal sources, and synthetic/meta sources.
Could be reasonable to build a temporary("synthetic") database of the calculations and analyses the system performs during tasking to operate consistently and accurately.
Structure should abstractly imitate that of a well-developed company.
Reasoning: LLM's and AI mimic that of a human, so it is reasonable to model a multi-agent or multi-AI system to that of a company
Due to the contextual nature of companies and organizations, a more abstract approach would likely be more economical and productive.
Paraphrased quote that comes to mind: "We wanted to fly like birds the birds did, and the best way to do that was not by building wings that flapped"

## Viable APIs
-Will likely incorporate CareerOne API. It is a governments provided API by the Department of Labor that grants access to federally funded and public information with the intention that the data will be used to further develop the labor market. Has several datasets of interest that could be valuable, and currently the only known firsthand free source of job listings

## Theoretical Works for Reference
Personality-Job Fit Theory
Employee Value Proposition (EVP)

## Privacy
Possible privacy breach through OpenAI resume parsing. Proposal for zero knowledge proof authentication and closed system/cryptographically secure data manipulation
