"""
pages/7_Leaderboard.py - Class Leaderboard for Arth Platform
Module 5: Reads leaderboard.csv at the top of the project and ranks all participant entries by return %.
Follows AGENTS.md, docs/house-style.md, and docs/finance-formulas.md.
"""

import os
import streamlit as st
import pandas as pd
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Class Leaderboard — Arth",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Fintech Aesthetic with Gold/Silver/Bronze Highlights)
st.markdown("""
<style>
    .main .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .page-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin-bottom: 0.35rem;
        letter-spacing: -0.03em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .page-title-badge {
        font-size: 0.8rem;
        font-weight: 700;
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24 !important;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .page-desc {
        font-size: 1.05rem;
        color: #94a3b8 !important;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* Podium / Top Rank Cards */
    .podium-card {
        background-color: #131b2e;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .podium-1 {
        border: 2px solid #fbbf24;
        background: linear-gradient(180deg, rgba(251, 191, 36, 0.08) 0%, #131b2e 100%);
    }
    .podium-2 {
        border: 2px solid #94a3b8;
        background: linear-gradient(180deg, rgba(148, 163, 184, 0.08) 0%, #131b2e 100%);
    }
    .podium-3 {
        border: 2px solid #d97706;
        background: linear-gradient(180deg, rgba(217, 119, 6, 0.08) 0%, #131b2e 100%);
    }
    .podium-rank {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .podium-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 0.35rem;
    }
    .podium-return {
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .podium-val {
        font-size: 0.85rem;
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
dl.render_html("""
<div class='page-title'>
    Class Leaderboard
    <span class='page-title-badge'>Rankings</span>
</div>
<div class='page-desc'>
    Live cohort performance rankings from <code>leaderboard.csv</code> at the top of the project.
    Ranked strictly by overall portfolio return percentage.
</div>
""")

# Load Leaderboard Data
df = dl.get_leaderboard_df()

if df.empty:
    st.info("ℹ️ No participants have shared scores to `leaderboard.csv` yet. Go to **Portfolio Analytics** or **Paper Trading** and click **'🚀 Share Result to Leaderboard'** to join the rankings!")
else:
    # Top 3 Podium Highlights
    p_cols = st.columns(min(3, len(df)))
    
    for idx in range(min(3, len(df))):
        row = df.iloc[idx]
        rank_num = idx + 1
        name = row["name"]
        ret = float(row["return_pct"])
        acct_val = float(row["account_value"])
        ret_color = "#34d399" if ret >= 0 else "#f87171"
        
        with p_cols[idx]:
            podium_style = f"podium-{rank_num}" if rank_num <= 3 else ""
            badge_icon = "🥇 1st Place" if rank_num == 1 else ("🥈 2nd Place" if rank_num == 2 else "🥉 3rd Place")
            dl.render_html(f"""
            <div class='podium-card {podium_style}'>
                <div class='podium-rank'>{badge_icon}</div>
                <div class='podium-name'>{name}</div>
                <div class='podium-return' style='color: {ret_color};'>{ret:+.2f}%</div>
                <div class='podium-val'>{dl.format_rupees(acct_val)}</div>
                <div style='font-size: 0.78rem; color: #64748b; margin-top: 0.4rem;'>Date: {row.get('date', 'N/A')}</div>
            </div>
            """)
            
    st.markdown("---")
    st.markdown("### Full Cohort Rankings")
    
    # Styled Table
    disp_df = df.copy()
    disp_df["account_value"] = disp_df["account_value"].apply(lambda v: dl.format_rupees(v))
    disp_df["return_pct"] = disp_df["return_pct"].apply(lambda v: f"{float(v):+.2f}%")
    disp_df = disp_df.rename(columns={
        "rank": "Rank",
        "name": "Trader Name",
        "date": "Date Submitted",
        "account_value": "Account Value",
        "return_pct": "Total Return (%)",
        "xirr_pct": "Annualized XIRR",
        "max_drawdown_pct": "Max Drawdown"
    })
    st.dataframe(disp_df, use_container_width=True, hide_index=True)
    
    # Export and Info
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Leaderboard CSV",
            data=csv_bytes,
            file_name="leaderboard.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_d2:
        st.caption("ℹ️ To merge records from other student computers, place their exported rows into `leaderboard.csv` at the project root (`c:\\Users\\abcom\\Desktop\\Arth\\leaderboard.csv`). The platform automatically aggregates and sorts by return.")

# Mandatory House Style Disclaimer Footer (Rule 7)
dl.render_footer()
