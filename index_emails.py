import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

load_dotenv()

def index_historical_emails():
    # Load raw data
    with open("data/past_emails.json", "r") as f:
        emails = json.load(f)
        
    documents = []
    for item in emails:
        # We index based on the "incoming" text, storing the correct "reply" in metadata
        doc = Document(
            page_content=item["incoming"],
            metadata={"reply": item["reply"]}
        )
        documents.append(doc)
        
    print(f"Vectorizing {len(documents)} emails...")
    
    # Generate vector database locally
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma.from_documents(
        documents, 
        embeddings, 
        persist_directory="./db"
    )
    
    print("Database built and saved to './db' successfully.")

if __name__ == "__main__":
    index_historical_emails()
