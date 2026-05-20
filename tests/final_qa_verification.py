import os
import sys
from dotenv import load_dotenv

# Add phase_3 to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase_3")))

from qa_pipeline import QAPipeline

def run_tests():
    qa = QAPipeline()
    
    test_queries = [
        # 1. Fund Details
        ("What is the NAV and PE ratio of Nippon India Small Cap Fund?", "Fund Details (NAV/PE)"),
        ("What is the AUM, Expense Ratio, and Risk Level of Quant Small Cap Fund?", "Fund Details (AUM/Expense/Risk)"),
        
        # 2. Holdings
        ("What are the top 3 holdings of HDFC Mid Cap Fund, their sectors, and allocation percentages?", "Holdings"),
        
        # 3. Fund Managers and AMC
        ("Who is the fund manager of Nippon India Small Cap Fund and what is its AMC?", "Fund Manager & AMC"),
        
        # 4. Comparison
        ("Compare the 3-year returns and expense ratios between Nippon India Small Cap Fund and Quant Small Cap Fund.", "Comparison")
    ]
    
    print("="*80)
    print("                      GROWW AI BOT FINAL VERIFICATION")
    print("="*80)
    
    for query, category in test_queries:
        print(f"\n[Category: {category}]")
        print(f"Question: {query}")
        print("-" * 40)
        try:
            response = qa.ask(query)
            print(f"Answer:\n{response['result']}")
        except Exception as e:
            print(f"Error executing query: {e}")
        print("="*80)

if __name__ == "__main__":
    run_tests()
