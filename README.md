BEMA - The Interactive AI Model

We created BEMA using LLM, Langchain, and OpenAI. It is an interactive chatbot much like ChatGPT. It can also be used for the specific case of writing a resume based on a job link that the user provides. 

1. Install Python onto your system (3.12.6 reccommended and tested for).

2.  Clone the repository using git clone
   
3.  Create a .env file in the file directory with the repository that includes all your API keys.
The .env should have the following API calls:

OPENAI_API_KEY ([https://platform.openai.com/](https://platform.openai.com/docs/quickstart))

Sign Up/Login: Visit the OpenAI Platform and log in or create an account.

Navigate to API Keys: Click on your profile icon at the top-right corner and select "View API Keys."

Create a New Key: Click "Create new secret key" to generate a new API key.

Save the Key: Copy and securely store the key, as it won't be displayed again.

SERPAPI_API_KEY (https://serpapi.com/)

Sign Up/Login: Go to the SerpAPI website and create an account or log in.

Access API Key: Once logged in, your API key will be available in your account dashboard.

Save the Key: Copy and securely store the key for your .env file.

URI_FOR_Mongo (https://www.mongodb.com/cloud/atlas)

Sign Up/Login: Visit MongoDB Atlas and log in or create an account.

Create a Cluster: Follow the prompts to set up a new database cluster.

Obtain Connection String: After setting up, click "Connect" and choose "Connect your application" to get the connection URI.

Configure URI: Replace placeholders (e.g., <password>, <dbname>) with your database credentials.

TAVILY_API_KEY (https://tavily.com/)

Sign Up/Login: Visit the Tavily website and create an account or log in.

Access API Key: After logging in, navigate to the API section in your account to find your key.

Save the Key: Copy and securely store the key for your .env file.

PROXYCURL_API_KEY (https://nubela.co/proxycurl/)

Sign Up/Login: Go to the Proxycurl website and create an account or log in.

Access API Key: Once logged in, your API key will be displayed in your account dashboard.

Save the Key: Copy and securely store the key for your .env file.

BRIGHTDATA_API_KEY (https://brightdata.com/)

Sign Up/Login: Visit the Bright Data website and create an account or log in.

Access API Key: After logging in, navigate to the API section to find your key.

Save the Key: Copy and securely store the key for your .env file.

4. Create a python virtual environment in your system's terminal:
   
      Create a Python virtual environment for Windows
   
      `python -m venv venv`
       
      Create a Python virtual environment for Mac
   
      `python3 -m venv venv`
       
      Activating Virtual Environment in Python for Windows
   
      `venv\Scripts\activate`
       
      Activating Virtual environment in Python for Mac
   
      `source venv/bin/activate`

5. Once the virtual environment is activated go to the directory folder of the repository on your system.

      `cd YOURFILEPATH` for Windows
   
6. Afterwards, use pip to install all the requirements for the project.

      `pip install -r requirements.txt`
   
8.  Run the application by using the command below to start the project in your terminal:

      `streamlit run Login.py`

That should take you to this page where you can interact with our application.
<img width="1123" alt="image" src="https://github.com/Teccon1998/GenAIAssistant/assets/43446163/07388579-22e6-4c7c-b2d5-f016de5e4d4d">



Official Technology Stack:

`Front-End:`

Streamlit: Used to create the user interface of the application. It provides an intuitive way to build and deploy the front end of the AI-powered assistant as a web application.

`Back-end/AI:`

LangChain: A Python framework used for developing AI applications. It was employed to manage the interactions between the application and the various APIs, as well as to facilitate the decision-making process of the AI.

OpenAI LLM: Used as the main Large Language Model (LLM) for generating responses and processing user prompts. It provides the core AI capabilities for analyzing resumes and generating personalized feedback.

`Data Management:`

MongoDB: Used for database management, particularly for storing user data such as resumes and LinkedIn profiles. It ensures that data is securely stored and easily accessible for processing by the AI.

`Web Scraping and Data Retrieval:`

ProxyCurl API: A tool used to scrape data from LinkedIn profiles and job postings. This API allowed the AI to gather the necessary data to tailor resume suggestions accurately.

Tavily Search Engine: Implemented to enable the chatbot to perform general web searches and retrieve relevant information from the internet as part of the data enrichment process.

`Key Components:`

LangChain: Central framework connecting the AI model with external APIs.

OpenAI LLM: Provides the AI's natural language processing and response generation.

Streamlit: Facilitates the front-end user experience.

MongoDB: Handles secure storage and management of user data.

ProxyCurl API: Enables web scraping for LinkedIn data.

Tavily Search Engine: Assists in retrieving additional contextual data from the web.
