import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class EmailResponder:
    def __init__(self):
        # Initialize embeddings & connect to persistent local Chroma DB
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.db = Chroma(
            persist_directory="./db", 
            embedding_function=self.embeddings
        )
        # Setup the LLM
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    def generate_suggested_reply(self, incoming_email: str) -> str:
        # 1. Retrieve the top 2 most semantically similar past emails (RAG)
        results = self.db.similarity_search_with_score(incoming_email, k=2)
        
        few_shots = ""
        for i, (doc, score) in enumerate(results):
            few_shots += f"Example {i+1}:\n"
            few_shots += f"Incoming: {doc.page_content}\n"
            few_shots += f"Your Past Reply: {doc.metadata['reply']}\n\n"
            
        # 2. System Prompt guiding the tone & context mapping
        system_prompt = (
            "You are an assistant drafting a professional email response on behalf of the user.\n"
            "Analyze the 'Past Examples' below to mirror the user's tone, formatting, and factual details "
            "as closely as possible. Only draft the reply itself. Do not include any meta-text or labels.\n\n"
            "--- START OF PAST EXAMPLES ---\n"
            "{few_shots}"
            "--- END OF PAST EXAMPLES ---"
        )
        
        user_prompt = "Incoming Email to respond to:\n{incoming_email}\n\nDraft Suggested Reply:"
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        # 3. Formulate chain & generate reply
        chain = prompt_template | self.llm
        response = chain.invoke({
            "few_shots": few_shots,
            "incoming_email": incoming_email
        })
        
        return response.content

# Quick test workflow execution
if __name__ == "__main__":
    responder = EmailResponder()
    
    # Simulated new incoming email
    test_email = "Hello! Do you have any demo options? I want to see the platform's layout before buying. Thanks!"
    
    print(f"\n--- INCOMING EMAIL ---\n{test_email}\n")
    
    reply = responder.generate_suggested_reply(test_email)
    
    print(f"--- GENERATED SUGGESTED REPLY ---\n{reply}\n")
