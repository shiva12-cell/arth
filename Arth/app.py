"""
app.py - Home Page of Arth Personal Finance Platform
Module 1 of 5 Foundation
"""

import streamlit as st
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Arth — Personal Finance Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Calm, High-Contrast, Professional Financial Dashboard
st.markdown("""
<style>
    /* Main container adjustments */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Hero Title styling - High contrast for dark mode */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin-bottom: 0.4rem;
        letter-spacing: -0.03em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .hero-title-accent {
        color: #38bdf8 !important;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8 !important;
        line-height: 1.65;
        margin-bottom: 2.5rem;
        max-width: 850px;
    }
    
    /* Section Headings */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 1.25rem;
        letter-spacing: -0.02em;
    }
    
    /* Module Cards - Terminal / Bloomberg / Modern Fintech Dark Style */
    .module-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .module-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12);
    }
    
    .module-badge-active {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.35);
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        margin-bottom: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .module-badge-upcoming {
        display: inline-block;
        background-color: #1e293b;
        color: #94a3b8 !important;
        border: 1px solid #334155;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        margin-bottom: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    .module-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    .module-desc {
        font-size: 0.95rem;
        color: #cbd5e1 !important;
        line-height: 1.55;
        margin-bottom: 1.25rem;
    }
    
    .module-status-note {
        color: #64748b !important;
        font-size: 0.85rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database
dl.init_db()

# Header & Introduction
dl.render_html("<div class='hero-title'>Arth <span class='hero-title-accent'>•</span></div>")
dl.render_html(
    "<div class='hero-subtitle'>"
    "Arth is a personal finance learning platform built from first principles for Indian investors. "
    "It brings together live market intelligence, portfolio tracking, long-term wealth projections, "
    "tax planning, and risk analysis into a unified, transparent space — without hidden jargon or "
    "proprietary black boxes."
    "</div>"
)

dl.render_html(
    "<div style='background-color: rgba(56, 189, 248, 0.08); border-left: 3px solid #38bdf8; "
    "padding: 0.6rem 1rem; border-radius: 4px; margin-bottom: 2rem; color: #94a3b8; font-size: 0.95rem;'>"
    "The public copy is a demo whose paper-trading account resets from time to time."
    "</div>"
)

dl.render_html("<div class='section-title'>Modules</div>")

col1, col2 = st.columns(2, gap="medium")

with col1:
    # Module 1 (Active)
    dl.render_html("""
    <div class='module-card'>
        <span class='module-badge-active'>Active • Module 1</span>
        <div class='module-title'>Market Pulse</div>
        <div class='module-desc'>
            Live benchmark indices, currency rates, gold prices, top Nifty 50 gainers & losers,
            sector heat strips, interactive price charts, and a persistent custom watchlist.
        </div>
    </div>
    """)
    if st.button("Open Market Pulse →", key="btn_pulse", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Market_Pulse.py")

    # Module 3 (Active: Fixed Deposits & Mutual Funds)
    dl.render_html("""
    <div class='module-card' style='margin-top: 1.5rem;'>
        <span class='module-badge-active'>Active • Module 3</span>
        <div class='module-title'>Fixed Deposits & Mutual Funds</div>
        <div class='module-desc'>
            Bank FD comparison with slab-rate post-tax returns, automated FD laddering, real return inflation erosion, live AMFI mutual fund explorer, 1Y/3Y/5Y CAGRs, 3Y rolling returns, SIP back-testing with XIRR, and side-by-side fund comparison.
        </div>
    </div>
    """)
    col_m3_a, col_m3_b = st.columns(2)
    with col_m3_a:
        if st.button("Open Fixed Deposits →", key="btn_fd", use_container_width=True, type="primary"):
            st.switch_page("pages/3_Fixed_Deposits.py")
    with col_m3_b:
        if st.button("Open Mutual Funds →", key="btn_mf", use_container_width=True, type="primary"):
            st.switch_page("pages/4_Mutual_Funds.py")

    # Module 5 (Active: Portfolio Analytics & Leaderboard)
    dl.render_html("""
    <div class='module-card' style='margin-top: 1.5rem;'>
        <span class='module-badge-active'>Active • Module 5</span>
        <div class='module-title'>Portfolio Analytics & Leaderboard</div>
        <div class='module-desc'>
            Asset and sector allocation donuts, whole-account XIRR with dated cash-flow ledger, institutional risk metrics (annualised volatility, maximum drawdown with peak/trough dates, beta vs Nifty 50), concentration warnings, printable statement, CSV data exports, and cohort leaderboard.
        </div>
    </div>
    """)
    col_m5_a, col_m5_b = st.columns(2)
    with col_m5_a:
        if st.button("Open Portfolio Analytics →", key="btn_port_analytics", use_container_width=True, type="primary"):
            st.switch_page("pages/6_Portfolio_Analytics.py")
    with col_m5_b:
        if st.button("Open Leaderboard →", key="btn_leaderboard", use_container_width=True):
            st.switch_page("pages/7_Leaderboard.py")

with col2:
    # Module 2 (Active)
    dl.render_html("""
    <div class='module-card'>
        <span class='module-badge-active'>Active • Module 2</span>
        <div class='module-title'>Financial Calculators</div>
        <div class='module-desc'>
            Nine essential tools: 50/30/20 budget planner, EMI amortization, SIP compounding, step-up SIP,
            lump sum, goal planner, inflation analysis, retirement corpus, and Budget 2025 tax comparison.
        </div>
    </div>
    """)
    if st.button("Open Calculators →", key="btn_calcs", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Calculators.py")

    # Module 4 (Active: Paper Trading)
    dl.render_html("""
    <div class='module-card' style='margin-top: 1.5rem;'>
        <span class='module-badge-active'>Active • Module 4</span>
        <div class='module-title'>Paper Trading</div>
        <div class='module-desc'>
            Virtual equity simulator with Rs 10,00,000 starting cash, live delayed execution, transparent brokerage and STT cost modeling, average-cost portfolio accounting, and automated benchmark comparison versus Nifty 50.
        </div>
    </div>
    """)
    if st.button("Open Paper Trading →", key="btn_paper_trading", use_container_width=True, type="primary"):
        st.switch_page("pages/5_Paper_Trading.py")

# Mandatory House Style Disclaimer Footer (Rule 7)
dl.render_footer()
