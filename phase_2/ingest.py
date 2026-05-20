import os
import json
import glob
from chunker import DataChunker
from vector_db import VectorStoreManager

def ingest_data():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_1", "data")
    structured_files = glob.glob(os.path.join(data_dir, "*_structured.json"))
    
    if not structured_files:
        print("No structured JSON data found. Please run the phase 1 scraper first.")
        return

    all_funds_data = []
    for file_path in structured_files:
        with open(file_path, "r") as f:
            fund_data = json.load(f)
            all_funds_data.append(fund_data)
            
    print(f"Loaded {len(all_funds_data)} funds. Chunking...")
    
    # 1. Chunking
    documents = DataChunker.chunk_multiple_funds(all_funds_data)
    print(f"Created {len(documents)} document chunks with metadata.")
    
    # 2. Embeddings & Vector DB
    db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    vsm = VectorStoreManager(persist_directory=db_path)
    
    # Initialize and index
    vsm.initialize_store(documents)
    print("Ingestion pipeline complete! Data is ready for semantic search.")

if __name__ == "__main__":
    ingest_data()
