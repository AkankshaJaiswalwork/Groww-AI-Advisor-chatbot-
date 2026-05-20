import sys
import os
import json
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class QAPipeline:
    def __init__(self):
        # Use Groq Llama 3
        self.llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.1)
        
        # Load the scraped data directly to bypass the vector DB for now
        self.context_data = ""
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase_1", "data"))
        
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith("_structured.json")]
            for file in files:
                with open(os.path.join(data_dir, file), "r") as f:
                    data = json.load(f)
                    self.context_data += f"\nFund: {data.get('fund_name')}\n"
                    self.context_data += json.dumps(data, indent=2)
                    self.context_data += "\n---\n"
        
        print(f"Loaded context from {len(files)} files.")

        # Define the prompt
        template = """You are an expert AI Financial Advisor specializing in Groww Mutual Funds.
Your job is to answer the user's questions based on the provided context.

Context: {context}

User Question: {question}

Strict Rules:
1. Only use facts mentioned in the context. Do not make up any numbers, percentages, or holdings.
2. If the answer cannot be found in the context, say "I cannot find this information in the scraped data."
3. DO NOT ask the user for any personal details (like name, email, phone, investment amount, etc.).
4. Keep your answer concise and professional.

Answer:"""
        self.prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    def ask(self, query: str) -> dict:
        # Format the prompt
        formatted_prompt = self.prompt.format(context=self.context_data, question=query)
        
        # Call the LLM
        response = self.llm.invoke(formatted_prompt)
        
        return {
            "result": response.content,
            "source_documents": []
        }
