# Installation 

1. Install Python onto your system (3.12.6 reccommended and tested for).

2.  Clone the repository using git clone

3. Create a python virtual environment in your system's terminal:
   
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

4. Once the virtual environment is activated go to the directory folder of the repository on your system. (if not already there)

      `cd YOURFILEPATH` 
      
5. Afterwards, use pip to install all the requirements for the project.

      `pip install -r requirements.txt`

6.  Create a .env file in the file directory with the repository that includes all your API keys.

## API Key Setup

**OPENAI_API_KEY:** [https://platform.openai.com/](https://platform.openai.com/docs/quickstart)

Free tier available, however to process sufficient amount of tokens free tier is insufficient. Requires upgrade to at least 1st tier.

- Sign Up/Login: Visit the OpenAI Platform and log in or create an account.
- Navigate to API Keys: Click on your profile icon at the top-right corner and select "View API Keys."
- Create a New Key: Click "Create new secret key" to generate a new API key.
- Save the Key: Copy and securely store the key, as it won't be displayed again.


**SERPAPI_API_KEY:** [https://serpapi.com/](https://serpapi.com/)

- Sign Up/Login: Visit the website and log in or create an account.
- Select "API Key" and copy paste the API key into .env file under SERPAPI_API_KEY.

**URI_FOR_Mongo:** [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

Sign Up/Login: Visit MongoDB Atlas and log in or create an account.

- Click on "New Project"
- Enter a Project Name and click "Next"
- Add team members email with "Project Owner" permission 
- Click "Create Project"

Create a Cluster: 

- After creating a project, click "Create" under "Create a cluster"
- Choose M0 and click "Create DEploymenet"
- To connect to Cluster0, save the Username and Password of database user. Click "Create Database User"
- Click "Choose a connection method" and choose "MongoDB for VS Code"
- Copy and paste the Connection String into the .env file for URI_FOR_Mongo

Configure URI: Replace placeholders (e.g., <password>, <dbname>) with your database credentials.

To obtain tlsCAFile path:

- Run the following code 

```
import certifi
print(certifi.where())

```

- Copy and paste this path into .env file under tlsCAFile

**BRIGHTDATA_API_KEY:** [https://brightdata.com/](https://brightdata.com/)

- Visit the website and create an account 
- After logging in choose "Web Scraper API"
- Search for "Glassdoor companies reviews - Collect by URL"
- Click "Start setting an API call" 
- Select JSON under "Trigger Data Collection API" and Download snapshop and JSON under "Delivery options"
- CLick "Get API token"
- Copy and paste this API token into .env file under BRIGHTDATA_API_KEY

**TAVILY_API_KEY:** [https://tavily.com/](https://tavily.com/)

Free tier allows 1000 credits

**PROXYCURL_API_KEY:** [https://nubela.co/proxycurl/](https://nubela.co/proxycurl/)

Small free trial avaiable. Can purchase credits starting at $10

**GOOGLE_API_KEY:** [https://developers.google.com/maps/documentation/geocoding/start](https://developers.google.com/maps/documentation/geocoding/start)

Activate the geocoding API and use that key after following all of the steps provided by google to make an account, billing, etc. It provides a generous free tier unlikely to reach a quota through development.

**CAREERONE_API_KEY and CAREERONE_USER_ID:** [https://www.careeronestop.org/Developers/WebAPI/web-api.aspx](https://www.careeronestop.org/Developers/WebAPI/web-api.aspx)

Fill out data request form to retrieve api key and user id. Completely free.
   
7.  Run the application by using the command below to start the project in your terminal:

      `streamlit run Home.py`

That should take you to this page where you can interact with our application.
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Home.jpg">



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

SERP API: Search Engine Results Pages API

Bright Data API: (formerly known as Luminati) for scraping Glassdoor Reviews

Google API: For geocoding coordinates for mapping data

CareerOne API: For retrieving data related to occupations

**MongoDB:**

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

**Notes:** Within collections files_uploaded there is a field called resume_fields. This is parsed by the AI and may be temperemental. The error checking for functions using this could be improved. Similarly, within Jobs is the job_details field and also temperemental to the way AI will parse data. If any issues occur for either, adjusting the associated prompt within their respective files to be more accurate will fix. However, cases of completely missing data from the original resume or job listing will require more thorough error checking.

Screenshots of application:

Welcome Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Welcome.jpg">


Login Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Login.jpg">


Register Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Register.jpg">


Advanced Enhancements Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Advanced_Enhancer.jpg">


Simple Enhancements Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Enhance_Resume.jpg">


Company Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Company.jpg">


Compatibility Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/compatability.jpg">


Paths Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Paths.jpg">


Job Listings Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/JobListings.jpg">


Developer Dashboard Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/DevDashboard.jpg">


Trends Page
<img width="1123" alt="image" src="https://github.com/maswindo/GenAIAssistant/blob/master/assets/Trends.jpg">







## References

1. OpenAI Platform: [https://platform.openai.com/](https://platform.openai.com/)
2. MongoDB Atlas Documentation: [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
3. Streamlit Documentation: [https://docs.streamlit.io/](https://docs.streamlit.io/)
4. LangChain Framework: [https://python.langchain.com/en/latest/](https://python.langchain.com/en/latest/)
5. SerpAPI Documentation: [https://serpapi.com/](https://serpapi.com/)
6. Tavily Search Engine API: [https://tavily.com/](https://tavily.com/)
7. ProxyCurl API for LinkedIn Data: [https://nubela.co/proxycurl/](https://nubela.co/proxycurl/)
8. Google Maps Geocoding API: [https://developers.google.com/maps/documentation/geocoding/start](https://developers.google.com/maps/documentation/geocoding/start)
9. CareerOneStop Web API: [https://www.careeronestop.org](https://www.careeronestop.org)
10. BrightData Web Scraper API: [https://brightdata.com/](https://brightdata.com/)
11. Python Virtual Environment: [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
12. MIT Sloan Report on AI-Boosted Resumes: [https://mitsloan.mit.edu/ideas-made-to-matter/job-seekers-ai-boosted-resumes-more-likely-to-be-hired](https://mitsloan.mit.edu/ideas-made-to-matter/job-seekers-ai-boosted-resumes-more-likely-to-be-hired)
13. McKinsey Report on AI Adoption: [https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
14. InsightGlobal Job Burnout Survey: [https://insightglobal.com/news/unemployment-job-hunt-burnout-survey/](https://insightglobal.com/news/unemployment-job-hunt-burnout-survey/)
15. OpenAI API Best Practices: [https://openai.com/blog/chatgpt-api-best-practices](https://openai.com/blog/chatgpt-api-best-practices)







## Frequently Asked Questions (FAQ)

### 1. How do I get the required API keys?
Refer to the **API Key Setup** section for step-by-step instructions on obtaining keys for OpenAI, MongoDB Atlas, SerpAPI, Tavily, ProxyCurl, and others.

---

### 2. I’m receiving API key errors. What should I do?
- Ensure that all API keys are correctly added to the `.env` file.
- Check for typos and ensure there are no spaces around the keys.
- Verify that the APIs are active and the quotas have not been exceeded.

---

### 3. The MongoDB database connection is failing. How can I resolve it?
- Double-check the **URI_FOR_Mongo** string in the `.env` file.
- Ensure that your IP address is whitelisted in the MongoDB Atlas settings.
- Verify that the database user credentials are correct.

---

### 4. What should I do if the Streamlit app won’t start?
- Ensure the virtual environment is activated before running the app:
  ```bash
  source venv/bin/activate  # Mac/Linux
  venv\Scripts\activate     # Windows
  ```
Run the following commands:
   ```bash
   pip install -r requirements.txt
   streamlit run Home.py
```
### 5. Where is user data stored?
- User data, resumes, and job-related information are securely stored in MongoDB Atlas collections. The main collections include:
   - **`files_uploaded`**: Stores resumes and uploaded files.
   - **`jobs`**: Contains job-related data retrieved via APIs.
   - **`insights`**: Stores analyzed trends and recommendations.

---

### 6. How can I update job listings data?
- Job data can be updated by running the functions in the **`JobPostProcessor.py`** script.
- Use the appropriate triggers for these functions in the **DevDashboard** page or as defined by the project structure.


## Potential Issues and Solutions

### 1. **API Rate Limits or Expired Keys**
- **Issue**: The application may fail to fetch data if API rate limits are exceeded or keys have expired.
- **Solution**:
  - Monitor API quotas via the respective dashboards.
  - Replace expired API keys in the `.env` file with new ones.
  - Optimize API calls to avoid hitting rate limits.

---

### 2. **Incomplete Data in Resumes or Job Listings**
- **Issue**: Missing fields like `resume_fields` or `job_details` can cause errors in data parsing.
- **Solution**:
  - Adjust the prompts in the respective files to improve parsing accuracy.
  - Add error-handling logic to skip or manage missing fields gracefully.

---

### 3. **MongoDB Database Connection Failure**
- **Issue**: The system fails to connect to the MongoDB database due to incorrect credentials or network issues.
- **Solution**:
  - Verify that the `URI_FOR_Mongo` string in the `.env` file is correct.
  - Ensure your IP address is whitelisted in the MongoDB Atlas settings.
  - Confirm that database user permissions are correctly configured.

---

### 4. **Application Performance Delays**
- **Issue**: API response times may cause delays, especially when processing a large number of requests.
- **Solution**:
  - Optimize API calls to minimize redundant requests.
  - Use batch processing for bulk data requests.
  - Reduce concurrent requests to external APIs where possible.

---

### 5. **Virtual Environment Not Activating**
- **Issue**: The virtual environment may fail to activate, preventing the application from running.
- **Solution**:
  - Recreate the virtual environment using the following command:
    ```bash
    python -m venv venv
    ```
  - Activate the virtual environment:
    - **Windows**:
      ```bash
      venv\Scripts\activate
      ```
    - **Mac/Linux**:
      ```bash
      source venv/bin/activate
      ```

---

### 6. **Streamlit App Crashes**
- **Issue**: The Streamlit app may crash due to missing dependencies or caching issues.
- **Solution**:
  - Reinstall required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
  - Clear Streamlit’s cache to resolve inconsistencies:
    ```bash
    streamlit cache clear
    ```
  - Verify installed libraries and their versions:
    ```bash
    pip freeze
    ```
  - Restart the virtual environment and rerun the app:
    ```bash
    streamlit run Home.py
    ```

---

### 7. **Data Not Appearing in UI**
- **Issue**: Resume fields, job listings, or insights data fail to appear in the Streamlit app.
- **Solution**:
  - Ensure the MongoDB database is connected and populated with data.
  - Verify that API responses return the expected data format.
  - Debug the pipeline scripts (e.g., `JobPostProcessor.py`) for errors.

---

### 8. **API Key Exposure**
- **Issue**: Exposing sensitive API keys in the source code poses a security risk.
- **Solution**:
  - Store API keys securely in a `.env` file and use environment variable libraries like `python-dotenv`.
  - Avoid hardcoding API keys into scripts or publicly accessible files.

