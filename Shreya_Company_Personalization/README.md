# Company-Specific and Job-Specific Pages for Career Guidance

### What I've Worked On:
- **UI Enhancements**:
  - Added a **Home Page** with options to log in or register.
  - Created a **Welcome Page** for users after they log in successfully. Displays a personalized greeting once the user is logged in.
  - **Company Page** (Work in Progress):
  - Users will be able to search for a company and view mission, values, headquarters, and employee information.
  - **Job Page** (Work in Progress):
  - Users will be able to search for a job and view relevant information like requirements, skills, and interview questions and view networking opportunities.

## `.streamlit/config.toml` File


The `.streamlit/config.toml` file is used to configure the appearance and layout of the Streamlit app. This file allows you to customize things like the app's title, favicon, and layout options.

Example content of `.streamlit/config.toml`:

[theme]
base = "light"
primarycolor = "black"
backgroundColor = "white"


[client]
showSidebarNavigation = false


## Task Objective

### The task involves:

	1.	Retrieving past interview questions from Glassdoor based on company name and job title.
	2.	Using LinkedIn to fetch referrals of people currently working in a specific job role at the company.
	3.	Integrating these retrievals into a multi-agent workflow that combines data retrieval, user profile evaluation, and personalized feedback.


## Key Features

### Search Company Information: Users can search for a company and see a detailed summary that includes:
	• Mission and values
	• Headquarters location 
	• CEO Information: Display the CEO of the company with a biography and links to their LinkedIn profile.


### Job-Specific Page: Users can type in a job title (e.g., Software Engineer at Google) and see:
	• Box to enter job description (provided by the user)
	• Job requirements, skills, and benefits
	• Resume Enhancement: Users can upload their resume, which will be analyzed and optimized to fit the job description and company values.
	• Interview Preparation: A section that provides commonly asked interview questions at the company and for the specific job role.
	• Networking with Employees: Users can view a list of current employees in similar roles, with links to their LinkedIn profiles for networking opportunities.
	• Other personalized recommendations when applying. 


## Multi-Agent Workflow

LangChain’s multi-agent framework, where each agent has a specific task:

	1.	Data Retrieval Agent: Fetches data from Glassdoor and LinkedIn using APIs.
	2.	User Profile Agent: Extracts user data (e.g., education, career objectives) from MongoDB.
	3.	Evaluation Agent: Compares user data with company-specific data and provides personalized feedback.


## Task Division

	•	Glassdoor Retrieval: Will be implemented in tavily_lookup_tool.py. This component is responsible for retrieving past interview questions. (May consider Beautiful Soup)
	•	LinkedIn Referrals: Implemented in ProxyCurlLinkedIn.py, which uses ProxyCurl to fetch referral information from LinkedIn.

## Use Cases

### Use Case 1: Glassdoor Interview Questions Retrieval

A user applies for a position at Google and wants to prepare for the interview. The system retrieves relevant past interview questions from Glassdoor based on the job title and company name.

### Use Case 2: LinkedIn Network Retrieval

A user seeks referrels opportunities for a Software Engineer position at Facebook. The system retrieves LinkedIn profiles of people currently working at Facebook in similar job roles for networking.

### Use Case 3: Job Skills Matching and Improvement Suggestions

A user searches for a Data Scientist position at Amazon. The system retrieves the job requirements and skills needed for the role as well as company insights and compares them with the user’s profile (resume, skills, and experience). It then provides suggestions for improving the user’s qualifications for that specific company. 

### Use Case 4: Insights into Company Culture and Values

A user is interested in working for IBM and wants to know more about the company’s culture and values. The system retrieves and displays detailed information about IBM's mission and core values based on publicly available data and reviews from Glassdoor, helping the user determine if it aligns with their career aspirations.


