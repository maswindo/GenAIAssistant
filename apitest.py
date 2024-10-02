from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Check if the environment variable is loaded correctly
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key is missing. Ensure it's set in the .env file.")

# Instantiate the OpenAI client with the new API key
client = OpenAI(api_key=api_key)

# Test GPT-3.5 Turbo with a simple prompt
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "What is the capital of Japan?"}
    ],
    max_tokens=50
)

# Print the response
print(response.choices[0].message.content)
