1. Install Python onto your system (3.12.6 reccommended and tested for).

2.  Clone the repository using git clone
   
3.  Create a .env file in the file directory with the repository that includes all your API keys.
For All:
Sign Up/Login: Visit the OpenAI Platform and log in or create an account.

Navigate to API Keys: Click on your profile icon at the top-right corner and select "View API Keys."

Create a New Key: Click "Create new secret key" to generate a new API key.

Save the Key: Copy and securely store the key, as it won't be displayed again.
The .env should have the following API keys:

OPENAI_API_KEY ([https://platform.openai.com/](https://platform.openai.com/docs/quickstart))

Free tier available, however to process sufficient amount of tokens free tier is insufficient. Requires upgrade to at least 1st tier.

SERPAPI_API_KEY (https://serpapi.com/)

Free tier available, 100 searches per month

URI_FOR_Mongo (https://www.mongodb.com/cloud/atlas)

Sign Up/Login: Visit MongoDB Atlas and log in or create an account.

Create a Cluster: Follow the prompts to set up a new database cluster.

Obtain Connection String: After setting up, click "Connect" and choose "Connect your application" to get the connection URI.

Configure URI: Replace placeholders (e.g., <password>, <dbname>) with your database credentials.

TAVILY_API_KEY (https://tavily.com/)

Free tier allows 1000 credits

PROXYCURL_API_KEY (https://nubela.co/proxycurl/)

Small free trial avaiable. Can purchase credits starting at $10

BRIGHTDATA_API_KEY (https://brightdata.com/)

Small free trial avaiable. Can purchase credits starting at $10

GOOGLE_API_KEY (https://developers.google.com/maps/documentation/geocoding/start)

Activate the geocoding API and use that key after following all of the steps provided by google to make an account, billing, etc. It provides a generous free tier unlikely to reach a quota through development.

CAREERONE_API_KEY and CAREERONE_USER_ID (https://www.careeronestop.org/Developers/WebAPI/web-api.aspx)

Fill out data request form to retrieve api key and user id. Completely free.


4. Create a python virtual environment in your system's terminal:
   
      Create a Python virtual environment for Windows
   
      `python -m venv venv`
       
      Create a Python virtual environment for Mac

      (example uses python3.11, likely will need homebrew so as not to use Mac's default python 3.9.7, preferable for flexibility without having to manually change python version in PATH)

      `/usr/local/bin/python3.11 -m venv venv`
         alternatively, to find that exact path of your python version:
         import certifi
         print(certifi.where())

      Activating Virtual Environment in Python for Windows
   
      `venv\Scripts\activate`
       
      Activating Virtual environment in Python for Mac
   
      `source venv/bin/activate`

6. Once the virtual environment is activated go to the directory folder of the repository on your system. (if not already there)

      `cd YOURFILEPATH` for Windows
      
7. Afterwards, use pip to install all the requirements for the project.

      `pip install -r requirements.txt`
   
8.  Run the application by using the command below to start the project in your terminal:

      `streamlit run Home.py`

That should take you to this page where you can interact with our application.
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/assets/Home.pdf">



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

LangChain: Central framework connecting the AI model with external APIs and creating acyclic multi-agent systems

OpenAI LLM: Provides the AI's natural language processing and response generation.

Streamlit: Facilitates the front-end user experience. (Primarily used for data science and lightweight web applications, a more comprehensive framework for front-end should probably be used)

MongoDB: Handles secure storage and management of user data.

ProxyCurl API: Enables web scraping for LinkedIn data.

Tavily Search Engine: AI focused contextual web data retrieval.

Google API: For geocoding coordinates for mapping data

CareerOne API: For retrieving data related to occupations

**MongoDB Set Up:**

Number of Databases: 2
Number of Collections: 9
Service Name
`Cluster0`
Database Names
`499`
`Company_Glassdoor_Reviews`

Collections - All are populated by running application, no manual data entry needed (im pretty sure) except for jobs. Jobs data is updated by running the functions in JobPostProcessor.py, triggers to run are found in DevDashboard page, and it only parses .txt files (copied and pasted job descriptions) that are in a folder called Jobs within the main directory of the project) 
Within `499`:
- Company_Linkedin   (scraped and formatted linkedin data)
- Company_Overview   (scraped and formatted tavily data)
- Company_Reviews   (scraped and formatted glassdoor data)
- files_uploaded   (user data)
- jobs               (job listing data)
- login_info         (credentials)

Within `Compay_Glassdoor_Reviews`:
- Meta (info scraped for Meta)
- Netflix (info scraped for Netflix)
- Nvidia
- etc.

Triggers:
Currently we've set up a timestamp trigger that adds a field to documents for the times they are created and modified. Must be set up for each collection individually on actions Update Document and Insert Document.

exports = async function(changeEvent) {
  const docId = changeEvent.documentKey._id;
  const serviceName = "Cluster0";
  const database = "499";
  const collection = context.services.get(serviceName).db(database).collection(changeEvent.ns.coll);

  try {
    if (changeEvent.operationType === "insert") {
      console.log(`Setting timestamps for newly inserted document with _id: ${docId}`);
      // Update the new document with `createdAt` and `lastModified` timestamps
      await collection.updateOne(
        { "_id": docId },
        { 
          $set: { 
            createdAt: new Date(),       // Set creation timestamp
            lastModified: new Date()     // Set initial modification timestamp
          }
        }
      );
    } else if (changeEvent.operationType === "update" || changeEvent.operationType === "replace") {
      console.log(`Updating document with _id: ${docId}`);
      // Update the `lastModified` timestamp on update or replace operations
      await collection.updateOne(
        { "_id": docId },
        { 
          $set: { lastModified: new Date() } // Only update lastModified timestamp
        }
      );
    }
  } catch(err) {
    console.log("Error performing MongoDB write operation:", err.message);
  }
};

Notes:
within collections files_uploaded there is a field called resume_fields. This is parsed by the AI and may be temperemental. The error checking for functions using this could be improved.
Similarly, within Jobs is the job_details field and also temperemental to the way AI will parse data. If any issues occur for either, adjusting the associated prompt within their respective files to be more accurate will fix. However, cases of completely missing data from the original resume or job listing will require more thorough error checking.
