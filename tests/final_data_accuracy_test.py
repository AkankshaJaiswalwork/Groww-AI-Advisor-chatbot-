import os
import json
import math

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "phase_1", "data"))

def test_data_accuracy():
    funds = [
        "nippon-india-small-cap-fund-direct-growth",
        "quant-small-cap-fund-direct-plan-growth",
        "hdfc-mid-cap-opportunities-fund-direct-growth"
    ]
    
    print("=" * 100)
    print("                    GROWW SCRAPER DATA ACCURACY VERIFICATION REPORT")
    print("=" * 100)
    
    all_passed = True
    
    for slug in funds:
        raw_path = os.path.join(DATA_DIR, f"{slug}_raw.json")
        structured_path = os.path.join(DATA_DIR, f"{slug}_structured.json")
        
        if not os.path.exists(raw_path):
            print(f"[-] Raw file missing for {slug}")
            all_passed = False
            continue
            
        if not os.path.exists(structured_path):
            print(f"[-] Structured file missing for {slug}")
            all_passed = False
            continue
            
        with open(raw_path, "r") as f:
            raw_data = json.load(f)
            
        with open(structured_path, "r") as f:
            struct_data = json.load(f)
            
        # Extract from raw data (duplicating scraping logic for verification)
        props = raw_data.get('props', {})
        page_props = props.get('pageProps', {})
        mf_data = page_props.get('mfServerSideData', {})
        
        raw_name = mf_data.get('fund_name') or mf_data.get('scheme_name')
        raw_aum = mf_data.get('aum')
        raw_expense = mf_data.get('expense_ratio')
        
        # Returns
        returns_list = mf_data.get('return_stats', [])
        raw_1y, raw_3y, raw_5y = None, None, None
        if returns_list and isinstance(returns_list, list):
            stats_0 = returns_list[0]
            raw_1y = stats_0.get('return1y')
            raw_3y = stats_0.get('return3y')
            raw_5y = stats_0.get('return5y')
                
        raw_nav = mf_data.get('nav')
        raw_holdings = mf_data.get('holdings', [])
        
        raw_managers = ", ".join([m.get('person_name', 'Unknown') for m in mf_data.get('fund_manager_details', []) if m.get('person_name')])
        
        raw_amc_node = mf_data.get('amc', {})
        raw_amc = raw_amc_node.get('name') if isinstance(raw_amc_node, dict) else str(raw_amc_node)
        
        print(f"\n[Fund: {slug.upper()}]")
        print("-" * 100)
        print(f"{'Field':<25} | {'Raw HTML/JSON Value':<35} | {'Structured DB Value':<35} | {'Result':<10}")
        print("-" * 100)
        
        def check_field(field_name, raw_val, struct_val, is_float=False):
            nonlocal all_passed
            status = "PASS"
            
            if raw_val is None:
                # Raw value could be missing from server-side data, verify if structured fell back correctly
                if struct_val is not None:
                    status = "OK (Fallback)"
            elif is_float:
                try:
                    if not math.isclose(float(raw_val), float(struct_val), rel_tol=1e-5):
                        status = f"FAIL (Diff: {float(raw_val)} vs {float(struct_val)})"
                        all_passed = False
                except (ValueError, TypeError):
                    status = "FAIL (Type)"
                    all_passed = False
            else:
                if str(raw_val).strip().lower() not in str(struct_val).strip().lower() and str(struct_val).strip().lower() not in str(raw_val).strip().lower():
                    status = "FAIL"
                    all_passed = False
                    
            print(f"{field_name:<25} | {str(raw_val):<35} | {str(struct_val):<35} | {status:<10}")
            
        check_field("Fund Name", raw_name, struct_data.get("fund_name"))
        check_field("AUM (Cr)", raw_aum, struct_data.get("aum_cr"), is_float=True)
        check_field("Expense Ratio (%)", raw_expense, struct_data.get("expense_ratio"), is_float=True)
        check_field("1Y Returns (%)", raw_1y, struct_data.get("returns_1y"), is_float=True)
        check_field("3Y Returns (%)", raw_3y, struct_data.get("returns_3y"), is_float=True)
        check_field("5Y Returns (%)", raw_5y, struct_data.get("returns_5y"), is_float=True)
        check_field("NAV (Net Asset Value)", raw_nav, struct_data.get("nav"), is_float=True)
        
        # Verify first holding
        if raw_holdings and struct_data.get("holdings"):
            raw_first_name = raw_holdings[0].get("company_name")
            raw_first_alloc = raw_holdings[0].get("corpus_per")
            
            struct_first_name = struct_data.get("holdings")[0].get("company_name")
            struct_first_alloc = struct_data.get("holdings")[0].get("allocation_percentage")
            
            check_field("Top Holding Co Name", raw_first_name, struct_first_name)
            check_field("Top Holding Allocation", raw_first_alloc, struct_first_alloc, is_float=True)
            
        check_field("Fund Manager", raw_managers, struct_data.get("fund_manager"))
        check_field("AMC Name", raw_amc, struct_data.get("amc"))
        
    print("=" * 100)
    if all_passed:
        print(">>> OVERALL ACCURACY TEST RESULT: 100% CORRECT & ALIGNED <<<")
    else:
        print(">>> OVERALL ACCURACY TEST RESULT: FAILED (Some mismatches detected) <<<")
    print("=" * 100)

if __name__ == "__main__":
    test_data_accuracy()
