import streamlit as st
import requests
import uuid
import os
import json
import numpy as np
import pandas as pd

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Groww Mutual Fund Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to mimic Groww website style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit default header/deploy button and footer */
    [data-testid="stHeader"] {display: none !important;}
    footer {visibility: hidden !important;}
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
        color: #1e293b;
    }
    
    /* Header styling */
    .groww-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 4%;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 25px;
    }
    .groww-logo-section {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .groww-logo-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6 0%, #00d09c 100%);
    }
    .groww-logo-text {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .groww-nav {
        display: flex;
        gap: 30px;
        font-weight: 500;
        color: #64748b;
        font-size: 15px;
    }
    .groww-nav a {
        text-decoration: none;
        color: #64748b;
    }
    .groww-nav a.active {
        color: #00d09c;
        border-bottom: 2px solid #00d09c;
        padding-bottom: 4px;
    }
    .groww-search-bar {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 8px 16px;
        width: 250px;
        font-size: 14px;
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .groww-login-btn {
        background-color: #00d09c;
        color: white !important;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 20px;
        border-radius: 5px;
        border: none;
        text-decoration: none;
    }
    
    /* Fund details page elements */
    .fund-title {
        font-size: 28px;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 8px;
    }
    .tag-container {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
    }
    .fund-tag {
        background-color: #f1f5f9;
        color: #475569;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
    }
    
    /* Returns metrics */
    .returns-positive {
        font-size: 26px;
        font-weight: 700;
        color: #00d09c;
    }
    .returns-label {
        font-size: 13px;
        color: #64748b;
        margin-left: 5px;
    }
    .returns-daily-negative {
        font-size: 13px;
        font-weight: 500;
        color: #ef4444;
        margin-top: 2px;
    }
    
    /* Sidebar Card box */
    .invest-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
        text-align: center;
    }
    .invest-card-title {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
        margin-top: 15px;
        margin-bottom: 8px;
    }
    .invest-card-desc {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    .invest-btn {
        background-color: #00d09c;
        color: white;
        width: 100%;
        border-radius: 8px;
        padding: 12px;
        font-weight: 600;
        border: none;
        font-size: 15px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .invest-btn:hover {
        background-color: #00b386;
    }
    
    /* Chat layout enhancements */
    .stChatInputContainer {
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Render Top Header mimicking Groww
st.markdown("""
<div class="groww-header">
    <div class="groww-logo-section">
        <div class="groww-logo-circle"></div>
        <div class="groww-logo-text">Groww</div>
    </div>
    <div class="groww-nav">
        <a href="#">Explore</a>
        <a href="#" class="active">Mutual Funds</a>
        <a href="#">Stocks</a>
        <a href="#">F&O</a>
    </div>
    <div class="groww-search-bar">
        <span>🔍 Search Groww...</span>
        <span style="font-size: 11px; background: #e2e8f0; padding: 2px 6px; border-radius: 4px;">⌘K</span>
    </div>
    <a href="#" class="groww-login-btn">Login/Sign up</a>
</div>
""", unsafe_allow_html=True)

# Helper: Load local scraped mutual funds
def load_mutual_funds():
    funds = {}
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "phase_1", "data")
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith("_structured.json")]
        for file in files:
            with open(os.path.join(data_dir, file), "r") as f:
                data = json.load(f)
                funds[data["fund_id"]] = data
    return funds

funds_db = load_mutual_funds()

# Layout split: Left for Dashboard details (Graph, Stats), Right for chatbot and Call To Action
col_left, col_right = st.columns([0.65, 0.35], gap="large")

# Default fund selection
selected_fund_id = "nippon-india-small-cap-fund-direct-growth"
if not funds_db:
    # Fallback mock fund if no data has been scraped yet
    funds_db = {
        selected_fund_id: {
            "fund_id": selected_fund_id,
            "fund_name": "Nippon India Small Cap Fund Direct Growth",
            "category": "Equity",
            "aum_cr": 50000.0,
            "expense_ratio": 0.85,
            "nav": 191.45,
            "pe_ratio": 26.82,
            "returns_1y": 35.40,
            "returns_3y": 22.10,
            "returns_5y": 18.50,
            "risk_level": "Very High",
            "fund_manager": "John Doe",
            "amc": "Nippon",
            "holdings": [
                {"company_name": "Reliance Industries", "allocation_percentage": 8.5, "sector": "Energy"},
                {"company_name": "HDFC Bank", "allocation_percentage": 7.2, "sector": "Financials"}
            ]
        }
    }

with col_left:
    # Interactive fund switcher dropdown
    selected_fund_id = st.selectbox(
        "Select Mutual Fund to view Groww Dashboard:",
        options=list(funds_db.keys()),
        format_func=lambda x: funds_db[x]["fund_name"]
    )
    
    fund = funds_db[selected_fund_id]
    
    # 2. Render Fund Title and Tags
    st.markdown(f'<div class="fund-title">{fund["fund_name"]}</div>', unsafe_allow_html=True)
    
    risk_level = fund.get("risk_level", "Very High")
    category = fund.get("category", "Equity")
    sub_category = "Small Cap" if "small-cap" in fund["fund_id"] else ("mid-cap" in fund["fund_id"] and "Mid Cap" or "Flexi Cap")
    
    st.markdown(f"""
    <div class="tag-container">
        <span class="fund-tag">{category}</span>
        <span class="fund-tag">{sub_category}</span>
        <span class="fund-tag">{risk_level} Risk</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Render returns metrics
    returns_3y = fund.get("returns_3y", 23.46)
    st.markdown(f"""
    <div>
        <span class="returns-positive">+{returns_3y}%</span>
        <span class="returns-label">3Y annualised</span>
    </div>
    <div class="returns-daily-negative">-0.20% <span style="color: #64748b; font-weight: normal;">1D</span></div>
    """, unsafe_allow_html=True)
    
    st.write("") # spacing
    
    # 4. Generate & Plot Graph (matching Groww styling)
    # Generate random walk simulating the NAV returns
    np.random.seed(42)
    days = 180
    steps = np.random.normal(loc=0.001, scale=0.015, size=days)
    steps[0] = 100 # Initial index value
    nav_series = np.cumprod(1 + steps/100) * 100
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    chart_data = pd.DataFrame({"NAV": nav_series}, index=dates)
    
    # Plot using streamlit line chart (themed color matches groww green)
    st.line_chart(chart_data, y="NAV", color="#00d09c")
    
    # Pill selectors at bottom of chart
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 15px; margin-bottom: 25px;">
        <span style="border: 1px solid #cbd5e1; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: #475569;">1M</span>
        <span style="border: 1px solid #cbd5e1; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: #475569;">6M</span>
        <span style="border: 1px solid #cbd5e1; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: #475569;">1Y</span>
        <span style="border: 1px solid #00d09c; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: #00d09c; font-weight: 600; background: #e6fbf7;">3Y</span>
        <span style="border: 1px solid #cbd5e1; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: #475569;">5Y</span>
        <span style="border: 1px solid #cbd5e1; border-radius: 15px; padding: 4px 12px; font-size: 12px; cursor: pointer; color: #475569;">ALL</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Render key stats inside columns
    st.subheader("Fund Information")
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.metric(label="AUM", value=f"₹{fund.get('aum_cr', 'N/A')} Cr")
    with s_col2:
        st.metric(label="Expense Ratio", value=f"{fund.get('expense_ratio', 'N/A')}%")
    with s_col3:
        st.metric(label="Fund Manager", value=fund.get("fund_manager", "N/A"))
        
    st.write("") # spacing
    s_col4, s_col5, s_col6 = st.columns(3)
    with s_col4:
        st.metric(label="NAV (Net Asset Value)", value=f"₹{fund.get('nav', 'N/A')}")
    with s_col5:
        st.metric(label="PE Ratio (P/E)", value=f"{fund.get('pe_ratio', 'N/A')}")
    with s_col6:
        st.metric(label="AMC", value=fund.get("amc", "N/A"))

with col_right:
    # 5. Render Groww Invest Now Card on top of Sidebar
    st.markdown("""
    <div class="invest-card">
        <div style="font-size: 40px;">📊</div>
        <div class="invest-card-title">Looking to invest in mutual funds?</div>
        <div class="invest-card-desc">Explore diversified funds designed for every investor and start building wealth today.</div>
        <button class="invest-btn">Invest Now</button>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # 6. Streamlit Chat Advisor
    st.markdown("### 💬 Ask Groww AI Advisor")
    st.caption("Ask me anything about holdings, returns, expense ratios or risk details.")
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Input area (Form to prevent page reload jumping and handle enter key)
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            user_input = st.text_input("Ask a question...", label_visibility="collapsed", placeholder="E.g. What is the expense ratio?")
        with c2:
            submit = st.form_submit_button("Ask")
            
    if submit and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Call local FastAPI server
        answer = ""
        try:
            headers = {"Authorization": "Bearer supersecrettoken"}
            payload = {
                "query": user_input,
                "session_id": st.session_state.session_id
            }
            
            with st.spinner("Analyzing..."):
                response = requests.post("http://127.0.0.1:8000/chat", json=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No response content.")
                else:
                    answer = f"Error: Backend returned {response.status_code}."
        except requests.exceptions.ConnectionError:
            answer = "Error: Cannot connect to FastAPI server on port 8000."
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
    # Custom Chat History Container (Scrollable)
    chat_container = st.container(height=500)
    
    with chat_container:
        # Render messages from history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background-color: #f1f5f9; padding: 12px 16px; border-radius: 12px 12px 0 12px; margin-bottom: 12px; text-align: right; color: #334155; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-left: 15%;">
                  <strong style="color: #475569;">You</strong><br>
                  <span style="display: inline-block; margin-top: 4px;">{message["content"]}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #ffffff; border-left: 4px solid #00d09c; padding: 16px; border-radius: 4px 12px 12px 4px; margin-bottom: 20px; text-align: left; color: #0f172a; font-size: 14px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); margin-right: 10%;">
                  <strong style="color: #00d09c;">Groww AI</strong><br>
                  <div style="margin-top: 8px; line-height: 1.6;">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
