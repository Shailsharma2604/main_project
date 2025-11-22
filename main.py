import streamlit as st
import subprocess
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Finance Analytics Hub",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .project-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    .project-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .project-desc {
        color: #7f8c8d;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .feature-list {
        list-style: none;
        padding: 0;
        margin-bottom: 1.5rem;
    }
    .feature-item {
        padding: 0.5rem 0;
        color: #34495e;
        font-size: 0.95rem;
    }
    .feature-item:before {
        content: "✓ ";
        color: #27ae60;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    h1 {
        color: white !important;
        text-align: center;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .subtitle {
        color: #ecf0f1;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    .footer {
        text-align: center;
        color: white;
        margin-top: 3rem;
        padding: 2rem;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 💰 Finance Analytics Hub")
st.markdown("<p class='subtitle'>Choose your financial analysis tool</p>", unsafe_allow_html=True)

# Project paths
MUTUAL_FUND_APP_PATH = r"C:\Users\shail\Downloads\main_project\MutualFunds-Allocation-Planner-main\MutualFunds-Allocation-Planner-main\streamlit_app.py"
CRYPTO_ANALYSIS_APP_PATH = r"C:\Users\shail\Downloads\main_project\example-app-crypto-dashboard-main\app.py"

# Create two columns for the project cards
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
        <div class='project-card'>
            <div class='project-title'>📈 Mutual Fund Analyzer</div>
            <div class='project-desc'>
                Comprehensive mutual fund portfolio planning and analysis tool
            </div>
            <ul class='feature-list'>
                <li class='feature-item'>Portfolio Allocation Optimizer</li>
                <li class='feature-item'>Risk Assessment Tools</li>
                <li class='feature-item'>Performance Analytics</li>
                <li class='feature-item'>Investment Recommendations</li>
                <li class='feature-item'>Historical Data Analysis</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Launch Mutual Fund Analyzer", key="mutual_fund"):
        if os.path.exists(MUTUAL_FUND_APP_PATH):
            st.success("✅ Launching Mutual Fund Analyzer...")
            st.balloons()
            subprocess.Popen(["streamlit", "run", MUTUAL_FUND_APP_PATH])
            st.info("📌 The app will open in a new browser tab")
        else:
            st.error("❌ File not found. Please check the path.")

with col2:
    st.markdown("""
        <div class='project-card'>
            <div class='project-title'>₿ Crypto Analytics Dashboard</div>
            <div class='project-desc'>
                Advanced cryptocurrency market analysis and insights platform
            </div>
            <ul class='feature-list'>
                <li class='feature-item'>Real-time Price Tracking</li>
                <li class='feature-item'>Market Trend Analysis</li>
                <li class='feature-item'>Technical Indicators</li>
                <li class='feature-item'>Portfolio Monitoring</li>
                <li class='feature-item'>Multi-Currency Support</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Launch Crypto Analytics", key="crypto"):
        if os.path.exists(CRYPTO_ANALYSIS_APP_PATH):
            st.success("✅ Launching Crypto Analytics Dashboard...")
            st.balloons()
            subprocess.Popen(["streamlit", "run", CRYPTO_ANALYSIS_APP_PATH])
            st.info("📌 The app will open in a new browser tab")
        else:
            st.error("❌ File not found. Please check the path.")

# Footer
st.markdown("---")
st.markdown(f"""
    <div class='footer'>
        <p>🕐 Current Time: {datetime.now().strftime('%B %d, %Y - %I:%M %p')}</p>
        <p>💡 Tip: Each project runs independently in a separate browser tab</p>
        <p>⚡ Built with Streamlit | Finance Analytics Hub</p>
    </div>
""", unsafe_allow_html=True)