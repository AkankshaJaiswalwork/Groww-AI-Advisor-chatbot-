import json
from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
from langchain.schema import Document

# Assuming we have the MutualFund object from phase_1.models
# For typing without importing (to avoid cross-folder import issues in this snippet)
class DataChunker:
    """
    Responsible for converting structured mutual fund data into semantic chunks 
    with rich metadata to enable hybrid search and accurate retrieval.
    """
    
    @staticmethod
    def chunk_fund_data(fund_data: dict) -> List[Document]:
        """
        Converts a single fund's structured data into multiple Document objects.
        Instead of one massive document, we chunk logically by category:
        1. Overview & Performance
        2. Holdings & Sectors
        """
        documents = []
        fund_name = fund_data.get("fund_name", "Unknown Fund")
        fund_id = fund_data.get("fund_id", "unknown_id")
        category = fund_data.get("category", "Unknown Category")
        
        # --- Chunk 1: Overview and Performance ---
        overview_text = (
            f"Fund Name: {fund_name}\n"
            f"Category: {category}\n"
            f"AMC: {fund_data.get('amc', 'N/A')}\n"
            f"Fund Manager: {fund_data.get('fund_manager', 'N/A')}\n"
            f"AUM (Assets Under Management): ₹{fund_data.get('aum_cr', 'N/A')} Cr\n"
            f"Expense Ratio: {fund_data.get('expense_ratio', 'N/A')}%\n"
            f"Net Asset Value (NAV): ₹{fund_data.get('nav', 'N/A')}\n"
            f"PE Ratio (Price-to-Earnings): {fund_data.get('pe_ratio', 'N/A')}\n"
            f"Risk Level: {fund_data.get('risk_level', 'N/A')}\n\n"
            f"Returns Performance:\n"
            f"1 Year Return: {fund_data.get('returns_1y', 'N/A')}%\n"
            f"3 Year Return: {fund_data.get('returns_3y', 'N/A')}%\n"
            f"5 Year Return: {fund_data.get('returns_5y', 'N/A')}%\n"
        )
        
        doc_overview = Document(
            page_content=overview_text,
            metadata={
                "fund_id": fund_id,
                "fund_name": fund_name,
                "category": category,
                "nav": fund_data.get('nav', 0.0),
                "pe_ratio": fund_data.get('pe_ratio', 0.0),
                "chunk_type": "overview_performance"
            }
        )
        documents.append(doc_overview)
        
        # --- Chunk 2: Holdings & Sectors ---
        holdings = fund_data.get("holdings", [])
        if holdings:
            holdings_text = f"Portfolio Holdings for {fund_name} ({category}):\n"
            for h in holdings:
                holdings_text += f"- {h.get('company_name', 'N/A')} ({h.get('sector', 'N/A')}): {h.get('allocation_percentage', 'N/A')}%\n"
            
            doc_holdings = Document(
                page_content=holdings_text,
                metadata={
                    "fund_id": fund_id,
                    "fund_name": fund_name,
                    "category": category,
                    "chunk_type": "holdings"
                }
            )
            documents.append(doc_holdings)
            
        return documents

    @staticmethod
    def chunk_multiple_funds(funds_data: List[dict]) -> List[Document]:
        all_docs = []
        for fund in funds_data:
            all_docs.extend(DataChunker.chunk_fund_data(fund))
        return all_docs
