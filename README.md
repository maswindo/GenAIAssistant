## Installation 

1. First clone the repository using git clone
   cd GenAIAssistant

2. Create a python virtual environment:
   
      Create a Python virtual environment for Windows
   
      `python -m venv venv`
       
      Create a Python virtual environment for Mac
   
      `python3 -m venv venv`
       
      Activating Virtual Environment in Python for Windows
   
      `venv\Scripts\activate`
       
      Activating Virtual environment in Python for Mac
   
      `source venv/bin/activate`

4. Once the virtual environment is activated please run this in the terminal command line of the project

   `pip install -r requirements.txt`

5. Set Up Environmental variables

   create a .env file in the root directory

6. Finally run the command below to start the project:

   `streamlit run Home.py`

That should take you to this page where you can interact with our application.




## Mongo DB Setup 

1.	Sign in to MongoDB Atlas or set up a MongoDB instance locally.

2.	Create a new cluster in MongoDB Atlas or use an existing one.

3.	In the cluster settings:
	•	Whitelist your IP address to allow your application to connect.
	•	Create a database user with proper credentials for access.

4. Add your MongoDB connection string to the .env file in the root directory of the project

5. To find the tlsCAFile on your machine run the following:

import certifi
tlsCAFile = certifi.where()
print(tlsCAFile)

store this path in your .env file 