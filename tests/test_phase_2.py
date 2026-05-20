import os
import sys
import pytest
from langchain.schema import Document

# Add phase_2 and phase_1 to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_1"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_2"))

from chunker import DataChunker
from vector_db import VectorStoreManager

@pytest.fixture
def sample_fund_data():
    return {
        "fund_id": "test-fund",
        "fund_name": "Test Growth Fund",
        "category": "Equity",
        "amc": "Test AMC",
        "aum_cr": 1000.0,
        "expense_ratio": 0.5,
        "risk_level": "Moderate",
        "returns_1y": 15.0,
        "returns_3y": 12.0,
        "returns_5y": 10.0,
        "holdings": [
            {"company_name": "Reliance", "allocation_percentage": 10.0, "sector": "Energy"},
            {"company_name": "HDFC", "allocation_percentage": 5.0, "sector": "Finance"}
        ]
    }

def test_data_chunker(sample_fund_data):
    docs = DataChunker.chunk_fund_data(sample_fund_data)
    
    assert len(docs) == 2
    assert isinstance(docs[0], Document)
    assert docs[0].metadata["fund_id"] == "test-fund"
    assert docs[0].metadata["chunk_type"] == "overview_performance"
    assert docs[1].metadata["chunk_type"] == "holdings"
    assert "Reliance" in docs[1].page_content

def test_vector_store_indexing_and_retrieval(sample_fund_data, tmp_path):
    docs = DataChunker.chunk_fund_data(sample_fund_data)
    
    # Use a temporary directory for ChromaDB to keep tests clean
    persist_dir = str(tmp_path / "chroma_test_db")
    vsm = VectorStoreManager(persist_directory=persist_dir)
    
    # Test indexing
    store = vsm.initialize_store(documents=docs)
    assert store is not None
    
    # Test semantic search
    results = vsm.hybrid_search(query="what are the holdings?", k=1)
    assert len(results) == 1
    assert results[0].metadata["fund_id"] == "test-fund"
    assert results[0].metadata["chunk_type"] == "holdings"
