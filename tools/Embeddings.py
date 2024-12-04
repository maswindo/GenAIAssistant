from openai import OpenAI
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv('../.env')
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

current_dir = Path(__file__).parent
occupations_file = current_dir / '..' / 'internal_database' / 'All_Occupations.csv'

if not occupations_file.exists():
    print("Occupations file not found! Required for accurate occupation name retrieval and generation.")

df = pd.read_csv(occupations_file)
documents = {}
for index, row in df.iterrows():
    # Combine columns to create a document
    document_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
    documents[f"Row_{index}"] = document_text

all_text = "\n".join([" | ".join([f"{col}: {row[col]}" for col in df.columns]) for _, row in df.iterrows()])
documents = {"csv_summary": all_text}

def get_embeddings(text):
    response = OpenAI.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response['data'][0]['embedding']

# Generate embeddings for each document
document_embeddings = {name: get_embeddings(content) for name, content in documents.items()}
