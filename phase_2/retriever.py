import sys
import os
from vector_db import VectorStoreManager

# A simple retrieval test script
def test_retrieval(query: str):
    db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    if not os.path.exists(db_path):
        print("ChromaDB not found! Please run ingest.py first.")
        return
        
    vsm = VectorStoreManager(persist_directory=db_path)
    
    print(f"\n--- SEMANTIC SEARCH ---")
    print(f"Query: '{query}'\n")
    
    # Simple semantic search
    results = vsm.hybrid_search(query=query, k=3)
    
    for i, res in enumerate(results, 1):
        print(f"Result {i} (Fund: {res.metadata.get('fund_name')} | Type: {res.metadata.get('chunk_type')}):")
        print(f"{res.page_content[:200]}...")
        print("-" * 40)
        
    print(f"\n--- HYBRID SEARCH (Filtered by Small Cap) ---")
    print(f"Query: '{query}' + Filter: category='Small Cap Fund'\n")
    
    filtered_results = vsm.hybrid_search(
        query=query, 
        filter_metadata={"category": "Small Cap Fund"},
        k=2
    )
    
    for i, res in enumerate(filtered_results, 1):
        print(f"Result {i} (Fund: {res.metadata.get('fund_name')}):")
        print(f"{res.page_content[:200]}...")
        print("-" * 40)

if __name__ == "__main__":
    test_query = "What are the top holdings for Nippon?"
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    test_retrieval(test_query)
