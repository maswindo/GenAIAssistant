import json
import sys

import certifi
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI
from srsly import json_loads

load_dotenv('../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Agent Prompts

triaging_system_prompt = """You are a Triaging Agent. Your role is to assess the user's query and route it to the relevant agents. The agents available are:
    - Job Listing Data Extraction Agent: Extracts data from a job listing

    User the send_job_to_agents tool to forward the job listing to the relevant agents."""

extracting_system_prompt = (
    """You are a Job Listing Data Extraction Agent. Your role is to extract job listing data using the following tools:
    - extract_data

    Please do not introduce any new information that is not present in the job data."""
)

triage_tools = [
    {
        "type": "function",
        "function": {
            "name": "send_job_to_agents",
            "description": "Sends the user query to relevant agents based on their capabilities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "An array of agent names to send the query to."
                    },
                    "job_listing": {
                        "type": "string",
                        "description": "The job listing to send."
                    }
                },
                "required": ["agents", "job_listing"]
            }
        },
        "strict": True
    }
]
extraction_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_data",
            "description": "Job Title,Company Name,Location,Employment Type,Department,Job Summary,Responsibilities,Required Skills,Preferred Skills,Qualifications,Education Requirements,Experience Requirements,Certifications/Licenses,Physical Requirements,Working Hours,Salary Range,Benefits,Work Environment,Travel Requirements,Reporting Structure,Career Development Opportunities,Application Deadline,Application Process",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The job listing to extract data from. Should be in a suitable format such as text."
                    }
                },
                "required": ["data"],
                "additionalProperties": False
            }
        },
        "strict": True
    }
]

def connect_to_mongo():
    uri = os.environ.get('URI_FOR_Mongo')
    tlsCAFile = certifi.where()
    client = MongoClient(uri, tlsCAFile=tlsCAFile, server_api=ServerApi('1'))
    return client['499']

def save_job_details(extracted_data):
    db = connect_to_mongo()
    collection = db['jobs']
    new_job = {
        'job_details': extracted_data,
    }

    # Insert the new job document into the collection
    collection.insert_one(new_job)

# Main function to process job listing data
def process_job_listing(job_listing, conversation_messages=None):
    if conversation_messages is None:
        conversation_messages = []
    user_message = {"role": "user", "content": job_listing}
    conversation_messages.append(user_message)

    # Initialize the triaging process with the triaging prompt
    messages = [{"role": "system", "content": triaging_system_prompt}]
    messages.extend(conversation_messages)

    # Get response from the model, using triage tools for initial sorting
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        tools=triage_tools,
    )

    # Append tool calls for record-keeping and debugging
    conversation_messages.append([tool_call.function for tool_call in response.choices[0].message.tool_calls])

    # Process each tool call from the response
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name == 'send_job_to_agents':
            agents = json.loads(tool_call.function.arguments)['agents']
            job_listing = json.loads(tool_call.function.arguments)['job_listing']

            # Send the job listing to the appropriate agent(s) based on triage
            for agent in agents:
                if agent == "Job Listing Data Extraction Agent":
                    handle_data_extracting_agent(job_listing, conversation_messages)

    return conversation_messages


def extract_data(job_data):
    prompt = (
        f"Extract structured data from the following job listing text:\n\n{job_data}\n\n"
        "Format the extracted information as a JSON object.\n"
        "Categorize the extracted information into lists. You can create custom categories based on the content of the job listing.\n "
        "Please do not introduce new information or categories not found in the provided job listing.\n"
        "Please do not relate or make inference upon the relationship of data unless it is for the purpose of categorizing them\n"
        "Please ensure that all relevant details are captured. Aim for comprehensive extraction and feel free to introduce new categories as needed.\n"
        "Any lists generated should be formatted as an array in JSON, within whatever array or category they would normally appear.\n"
        "Be sure to include as lists, but not limited to: Job Title,Company Name,Location,Employment Type,Department,Job Summary,Responsibilities,Required Skills,Preferred Skills,Qualifications,Education Requirements,Experience Requirements,Certifications/Licenses,Physical Requirements,Working Hours,Salary Range,Benefits,Work Environment,Travel Requirements,Reporting Structure,Career Development Opportunities,Application Deadline,Application Process\n"
        "If the job listing is unformatted, or has no labeled sections, or has is unconventionally written, still try try to extract the fields as best possible contextually."
        "Output the JSON object directly without using backticks or the 'json' label."
        "Here's an example format, but feel free to add new fields if necessary:\n\n"
        "{\n"
        "  'Job Title': 'string',\n"
        "  'Company Name': 'string',\n"
        "  'Location': 'string',\n"
        "  'Employment Type': 'string',\n"
        "  'Department': 'string',\n"
        "  'Job Summary': 'string',\n"
        "  'Responsibilities': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Required Skills': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Preferred Skills': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Qualifications': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Education Requirements': [\n"
        "      {\n"
        "          'Degree': 'string',\n"
        "          'Field': 'string',\n"
        "          'Preferred Institution': 'string'\n"
        "      }\n"
        "  ],\n"
        "  'Experience Requirements': [\n"
        "      {\n"
        "          'Years': 'integer',\n"
        "          'Field': 'string'\n"
        "      }\n"
        "  ],\n"
        "  'Certifications/Licenses': [\n"
        "      {\n"
        "          'Certification': 'string',\n"
        "          'Authority': 'string',\n"
        "          'Year': 'integer'\n"
        "      }\n"
        "  ],\n"
        "  'Physical Requirements': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Working Hours': 'string',\n"
        "  'Salary Range': {\n"
        "      'Minimum': 'decimal',\n"
        "      'Maximum': 'decimal',\n"
        "      'Currency': 'string'\n"
        "  },\n"
        "  'Benefits': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Work Environment': 'string',\n"
        "  'Travel Requirements': 'string',\n"
        "  'Reporting Structure': {\n"
        "      'Reports To': 'string',\n"
        "      'Team Size': 'integer'\n"
        "  },\n"
        "  'Career Development Opportunities': [\n"
        "      'string'\n"
        "  ],\n"
        "  'Application Deadline': 'string',\n"
        "  'Application Process': [\n"
        "      'string'\n"
        "  ]\n"
        "}\n\n"
        "If any categories are not applicable, simply omit them."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt, "type": "json_object"}
        ]
    )

    # Parse the assistant's reply as JSON
    extracted_data = response.choices[0].message.content
    print(repr(extracted_data))
    # Attempt to convert the response into a JSON object
    try:
        json_data = json.loads(extracted_data)
    except json.JSONDecodeError as e:
        # If JSON decoding fails, return the raw text to inspect or handle further
        print(f"JSON decode error: {e}")
        json_data = {"error": "Failed to parse JSON", "data": extracted_data}
        sys.exit(1)

    return json_data


def execute_tool(tool_calls, messages):
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        try:
            tool_arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            print("Error parsing tool arguments")
            continue

        # Check for the specific tool and call the associated function
        if tool_name == 'extract_data':
            try:
                # Call extract_data to get structured JSON output
                extracted_data = extract_data(tool_arguments['data'])

                # Send extracted data to MongoDB
                save_job_details(extracted_data)

                # Append extracted data to the messages list for reference
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({"extracted_data": extracted_data})
                })
            except Exception as e:
                print("Error in extract_data:", e)
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({"error": "Extraction failed", "details": str(e)})
                })

def handle_data_extracting_agent(job_listing, conversation_messages):
    # Initialize messages with the triaging prompt
    messages = [{"role": "system", "content": extracting_system_prompt}]
    messages.append({"role": "user", "content": job_listing})

    # Generate a response from the triaging system
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or whatever model you're using
        messages=messages,
        temperature=0,
        tools=extraction_tools  # Use the tools defined for triaging
    )

    # Append all function calls to the conversation_messages
    conversation_messages.append([tool_call.function for tool_call in response.choices[0].message.tool_calls])

    # Execute tools using execute_tool function
    execute_tool(response.choices[0].message.tool_calls, conversation_messages)

