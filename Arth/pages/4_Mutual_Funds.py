"""
pages/4_Mutual_Funds.py - Mutual Funds Analytics & Research Module for Arth
Module 3 of 5: NAV History, 1Y/3Y/5Y CAGR, 3-Year Rolling Returns, SIP Back-Testing with XIRR, and Rebased Scheme Comparison.
Follows AGENTS.md, docs/house-style.md, and docs/finance-formulas.md.
"""

import streamlit as st
import pandas as pd
import datetime
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Mutual Funds — Arth",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Fintech Aesthetic)
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
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .page-desc {
        font-size: 1.05rem;
        color: #94a3b8 !important;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }
    
    /* Mandatory Risk Caution Banner */
    .mf-caution-banner {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 10px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.5rem;
        color: #fde68a !important;
        font-size: 0.92rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    /* Result and Stat Cards */
    .result-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.15rem 1.15rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .result-label {
        font-size: 0.82rem;
        font-weight: 700;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }
    .result-val {
        font-size: 1.65rem;
        font-weight: 800;
        color: #f8fafc !important;
        letter-spacing: -0.02em;
    }
    .result-val-highlight {
        font-size: 1.65rem;
        font-weight: 800;
        color: #38bdf8 !important;
        letter-spacing: -0.02em;
    }
    .result-val-gain {
        font-size: 1.65rem;
        font-weight: 800;
        color: #10b981 !important;
        letter-spacing: -0.02em;
    }
    .result-val-danger {
        font-size: 1.65rem;
        font-weight: 800;
        color: #f43f5e !important;
        letter-spacing: -0.02em;
    }
    .result-subtext {
        font-size: 0.82rem;
        color: #64748b !important;
        margin-top: 0.25rem;
    }
    
    /* Scheme Meta Header Card */
    .scheme-meta-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }
    .scheme-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin-bottom: 0.4rem;
    }
    .scheme-tags-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.85rem;
    }
    .scheme-tag {
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        background-color: #1e293b;
        color: #94a3b8 !important;
        border: 1px solid #334155;
    }
    .scheme-tag-cyan {
        background-color: rgba(56, 189, 248, 0.12);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .info-callout {
        background-color: #131b2e;
        border-left: 4px solid #38bdf8;
        border-radius: 0 8px 8px 0;
        padding: 0.85rem 1.15rem;
        margin: 1rem 0;
        color: #cbd5e1 !important;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .source-timestamp {
        font-size: 0.78rem;
        color: #64748b !important;
        margin-top: 0.35rem;
        margin-bottom: 1rem;
    }
    .offline-badge {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b !important;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .footer-disclaimer {
        text-align: center;
        padding: 2.5rem 1rem 1rem 1rem;
        color: #64748b !important;
        font-size: 0.88rem;
        border-top: 1px solid #1e293b;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Page Title & Header
dl.render_html("""
<div class='page-title'>
    Mutual Funds
    <span class='page-title-badge'>Module 3</span>
</div>
<div class='page-desc'>
    Explore Indian mutual fund schemes via live AMFI NAV history, analyze 1Y, 3Y, and 5Y compound returns, inspect rolling consistency without entry-date bias, simulate monthly SIP wealth compounding with exact numerical XIRR, and compare fund performance head-to-head.
</div>
""")

# Mandatory Risk Caution (Item 10)
dl.render_html("""
<div class='mf-caution-banner'>
    ⚠️ <strong>Important Educational Note:</strong> Past returns do not predict future returns, and direct plans have lower expense ratios than regular plans.
</div>
""")


# ==============================================================================
# SCHEME SEARCH & SELECTION (Cached & Offline-Safe)
# ==============================================================================

# Search Bar with Suggestions
col_search, col_spacer = st.columns([3, 1])
with col_search:
    search_query = st.text_input(
        "Search Mutual Fund Scheme by Name",
        value="Parag Parikh Flexi Cap",
        placeholder="Type fund name (e.g., Parag Parikh, Nifty 50, HDFC, SBI, ICICI Prudential)...",
        help="Searches open-ended Indian mutual funds via the free api.mfapi.in service. Results are cached for 15 minutes."
    )

search_res = dl.search_mutual_funds(search_query)

if search_res.get("error"):
    st.warning(search_res["error"])

matching_funds = search_res.get("data", [])
if not matching_funds:
    # Helpful fallback default
    st.info("No schemes found matching that search term. Showing default popular schemes below.")
    matching_funds = [
        {"schemeCode": 122639, "schemeName": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth"},
        {"schemeCode": 120716, "schemeName": "UTI Nifty 50 Index Fund - Direct Plan - Growth"},
        {"schemeCode": 119551, "schemeName": "Tata Digital India Fund - Direct Plan - Growth"},
        {"schemeCode": 125354, "schemeName": "Mirae Asset Large Cap Fund - Direct Plan - Growth"}
    ]

# Scheme Selectbox
scheme_map = {f"{item['schemeName']} (Code: {item['schemeCode']})": item["schemeCode"] for item in matching_funds}
selected_scheme_label = st.selectbox(
    "Select Scheme",
    list(scheme_map.keys()),
    index=0,
    help="Select the exact scheme to view historical performance and run back-tests."
)
selected_code = scheme_map[selected_scheme_label]

# Fetch Fund Details (15-min cached, offline fallback)
fund_details = dl.get_mutual_fund_details(selected_code)

if fund_details.get("error") and (fund_details.get("df") is None or fund_details["df"].empty):
    st.error(fund_details["error"])
    dl.render_html("""
    <div class='footer-disclaimer'>
        Arth is a learning platform. Nothing here is investment advice.
    </div>
    """)
    st.stop()

meta = fund_details.get("meta", {})
nav_df = fund_details.get("df", pd.DataFrame())
is_offline = fund_details.get("is_offline", False)
source_label = fund_details.get("source_label", "api.mfapi.in")
latest_nav = fund_details.get("latest_nav")
latest_date = fund_details.get("latest_date")

# Format date and nav
latest_nav_formatted = f"Rs {latest_nav:.4f}" if latest_nav is not None else "N/A"
latest_date_formatted = dl.format_date(latest_date) if latest_date is not None else "N/A"

scheme_name = meta.get("scheme_name", selected_scheme_label)
fund_house = meta.get("fund_house", "Mutual Fund")
scheme_type = meta.get("scheme_type", "Open Ended")
scheme_cat = meta.get("scheme_category", "Equity")

# Render Scheme Meta Header Card
source_badge = f"<span class='offline-badge'>{source_label}</span>" if is_offline else f"<span class='source-timestamp'>{source_label}</span>"
dl.render_html(f"""
<div class='scheme-meta-card'>
    <div class='scheme-tags-row'>
        <span class='scheme-tag scheme-tag-cyan'>{fund_house}</span>
        <span class='scheme-tag'>{scheme_type}</span>
        <span class='scheme-tag'>{scheme_cat}</span>
        <span class='scheme-tag'>Code: {selected_code}</span>
    </div>
    <div class='scheme-title'>{scheme_name}</div>
    <div style='display: flex; gap: 1.5rem; align-items: baseline; margin-top: 0.5rem;'>
        <div>
            <span style='font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;'>Latest NAV:</span>
            <span style='font-size: 1.45rem; font-weight: 800; color: #38bdf8; margin-left: 0.35rem;'>{latest_nav_formatted}</span>
        </div>
        <div>
            <span style='font-size: 0.85rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;'>NAV Date:</span>
            <span style='font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-left: 0.35rem;'>{latest_date_formatted}</span>
        </div>
    </div>
    <div style='margin-top: 0.5rem;'>{source_badge}</div>
</div>
""")


# ==============================================================================
# TABS: 1. NAV History, 2. CAGRs & Rolling Returns, 3. SIP Backtest, 4. Compare Funds
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 NAV History & Chart",
    "🔄 CAGR & 3Y Rolling Returns",
    "💰 SIP Wealth Back-Test",
    "⚖️ Compare Two Funds"
])


# ==============================================================================
# TAB 1: NAV History Chart
# ==============================================================================
with tab1:
    st.subheader("Historical NAV Progression")
    st.caption("Inspect the historical Net Asset Value (NAV) of the scheme over multiple time horizons.")
    
    if not nav_df.empty:
        # Period Selector Buttons
        p_col1, p_col2 = st.columns([2, 1])
        with p_col1:
            period_choice = st.radio(
                "Select Time Period",
                ["1 Year", "3 Years", "5 Years", "Max (Since Inception)"],
                index=1,
                horizontal=True
            )
            
        period_days_map = {
            "1 Year": 365,
            "3 Years": 365 * 3,
            "5 Years": 365 * 5,
            "Max (Since Inception)": None
        }
        
        days_limit = period_days_map[period_choice]
        if days_limit is not None:
            cutoff = latest_date - pd.Timedelta(days=days_limit)
            chart_df = nav_df[nav_df["date"] >= cutoff].copy()
        else:
            chart_df = nav_df.copy()
            
        if not chart_df.empty:
            period_high = chart_df["nav"].max()
            period_low = chart_df["nav"].min()
            start_p_nav = chart_df.iloc[0]["nav"]
            end_p_nav = chart_df.iloc[-1]["nav"]
            period_pct = ((end_p_nav - start_p_nav) / start_p_nav) * 100.0 if start_p_nav > 0 else 0.0
            
            # Period Stats Row
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Period High</div>
                    <div class='result-val'>Rs {period_high:.4f}</div>
                    <div class='result-subtext'>Peak NAV in selected horizon</div>
                </div>
                """)
            with sc2:
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Period Low</div>
                    <div class='result-val'>Rs {period_low:.4f}</div>
                    <div class='result-subtext'>Trough NAV in selected horizon</div>
                </div>
                """)
            with sc3:
                arrow = "▲ " if period_pct > 0 else ("▼ " if period_pct < 0 else "")
                val_cls = "result-val-gain" if period_pct > 0 else "result-val-danger"
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Period Absolute Return</div>
                    <div class='{val_cls}'>{arrow}{dl.format_percentage(period_pct, show_sign=True)}</div>
                    <div class='result-subtext'>From {dl.format_date(chart_df.iloc[0]['date'])} to {dl.format_date(chart_df.iloc[-1]['date'])}</div>
                </div>
                """)
                
            # NAV Chart (Keep DatetimeIndex for proper chronological sorting)
            chart_plot = chart_df.copy().set_index("date")
            st.line_chart(chart_plot["nav"], use_container_width=True)
            st.caption(f"Showing {len(chart_df)} daily NAV observations. Source: {source_label}.")
        else:
            st.info("Insufficient historical NAV data for the selected period.")
    else:
        st.warning("No NAV historical records available for this scheme.")


# ==============================================================================
# TAB 2: CAGRs & 3-Year Rolling Returns
# ==============================================================================
with tab2:
    st.subheader("Point-to-Point CAGR & 3-Year Rolling Consistency")
    st.caption("Point-to-point CAGRs measure return between two static calendar dates. Rolling returns measure return across every possible 3-year holding window.")
    
    # 1. Point-to-point CAGRs
    cagrs = dl.calc_fund_cagrs(nav_df)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        c1y = cagrs.get("1y")
        if c1y:
            pct_val = c1y["cagr_pct"]
            val_cls = "result-val-gain" if pct_val > 0 else "result-val-danger"
            sign = "▲ " if pct_val > 0 else "▼ "
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>1-Year CAGR</div>
                <div class='{val_cls}'>{sign}{dl.format_percentage(pct_val, show_sign=True)}</div>
                <div class='result-subtext'>From Rs {c1y['start_nav']:.2f} ({dl.format_date(c1y['start_date'])})</div>
            </div>
            """)
        else:
            dl.render_html("""
            <div class='result-card'>
                <div class='result-label'>1-Year CAGR</div>
                <div class='result-val'>N/A</div>
                <div class='result-subtext'>Fund has < 1 year history</div>
            </div>
            """)
            
    with c2:
        c3y = cagrs.get("3y")
        if c3y:
            pct_val = c3y["cagr_pct"]
            val_cls = "result-val-gain" if pct_val > 0 else "result-val-danger"
            sign = "▲ " if pct_val > 0 else "▼ "
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>3-Year CAGR</div>
                <div class='{val_cls}'>{sign}{dl.format_percentage(pct_val, show_sign=True)}</div>
                <div class='result-subtext'>From Rs {c3y['start_nav']:.2f} ({dl.format_date(c3y['start_date'])})</div>
            </div>
            """)
        else:
            dl.render_html("""
            <div class='result-card'>
                <div class='result-label'>3-Year CAGR</div>
                <div class='result-val'>N/A</div>
                <div class='result-subtext'>Fund has < 3 years history</div>
            </div>
            """)
            
    with c3:
        c5y = cagrs.get("5y")
        if c5y:
            pct_val = c5y["cagr_pct"]
            val_cls = "result-val-gain" if pct_val > 0 else "result-val-danger"
            sign = "▲ " if pct_val > 0 else "▼ "
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>5-Year CAGR</div>
                <div class='{val_cls}'>{sign}{dl.format_percentage(pct_val, show_sign=True)}</div>
                <div class='result-subtext'>From Rs {c5y['start_nav']:.2f} ({dl.format_date(c5y['start_date'])})</div>
            </div>
            """)
        else:
            dl.render_html("""
            <div class='result-card'>
                <div class='result-label'>5-Year CAGR</div>
                <div class='result-val'>N/A</div>
                <div class='result-subtext'>Fund has < 5 years history</div>
            </div>
            """)
            
    # 2. 3-Year Rolling Returns (Item 7 Requirement)
    st.write("---")
    st.write("#### 3-Year Rolling Returns (Monthly Stepped)")
    
    # Explanatory Sentence on Screen (Strict Requirement)
    dl.render_html("""
    <div class='info-callout'>
        <strong>What are rolling returns?</strong> Rolling returns measure the CAGR of an investment across every possible holding window (here, 3 years), eliminating point-to-point entry bias and revealing the true consistency of returns.
    </div>
    """)
    
    rolling_res = dl.calc_rolling_returns(nav_df, window_years=3)
    rolling_df = rolling_res.get("df", pd.DataFrame())
    
    if not rolling_df.empty:
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            best_win = rolling_res["best"]
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Best 3-Year Window</div>
                <div class='result-val-gain'>▲ {dl.format_percentage(best_win['cagr_pct'])}</div>
                <div class='result-subtext'>Ended {dl.format_date(best_win['date'])}</div>
            </div>
            """)
        with r2:
            worst_win = rolling_res["worst"]
            val_c = "result-val-danger" if worst_win['cagr_pct'] < 0 else "result-val"
            sign_w = "▼ " if worst_win['cagr_pct'] < 0 else "▲ "
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Worst 3-Year Window</div>
                <div class='{val_c}'>{sign_w}{dl.format_percentage(worst_win['cagr_pct'])}</div>
                <div class='result-subtext'>Ended {dl.format_date(worst_win['date'])}</div>
            </div>
            """)
        with r3:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Median 3-Year CAGR</div>
                <div class='result-val-highlight'>{dl.format_percentage(rolling_res['median_pct'])}</div>
                <div class='result-subtext'>Average: {dl.format_percentage(rolling_res['average_pct'])}</div>
            </div>
            """)
        with r4:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Profitable Windows</div>
                <div class='result-val-gain'>{dl.format_percentage(rolling_res['positive_windows_pct'])}</div>
                <div class='result-subtext'>{rolling_res['total_windows']} 3-year windows tested</div>
            </div>
            """)
            
        # Rolling Returns Line Chart (Keep DatetimeIndex for chronological ordering)
        chart_rolling = rolling_df.copy().set_index("date")
        st.line_chart(chart_rolling["cagr_pct"], use_container_width=True)
        st.caption("Chart shows the 3-year annualized return (CAGR %) realized by an investor exiting on that month's date.")
    else:
        st.info("This fund requires at least 3 years of continuous NAV history to compute 3-year rolling returns.")
        
    with st.expander("How this is calculated"):
        st.markdown(f"""
**CAGR Formula** (from `docs/finance-formulas.md`):
$$\\text{{CAGR}} = \\left(\\frac{{\\text{{End NAV}}}}{{\\text{{Start NAV}}}}\\right)^{{1 / \\text{{years}}}} - 1$$

**Rolling Returns Computation:**
- For each month from (Fund Start Date + 3 Years) to Latest Date:
  - Take the NAV at the end of the window ($NAV_{{t}}$).
  - Take the NAV exactly 3 years prior ($NAV_{{t - 3\\text{{y}}}}$).
  - Calculate Window CAGR: $\\left(\\frac{{NAV_t}}{{NAV_{{t-3\\text{{y}}}}}}\\right)^{{1/3}} - 1$.
- **Median Window:** The exact 50th percentile of all overlapping 3-year holding periods.
        """)


# ==============================================================================
# TAB 3: SIP Wealth Back-Tester
# ==============================================================================
with tab3:
    st.subheader("Systematic Investment Plan (SIP) Back-Tester")
    st.caption("Simulate investing a fixed monthly sum on the first available trading day of each month, and compute exact annualized compound returns (XIRR).")
    
    bcol1, bcol2 = st.columns([1, 1.2], gap="large")
    
    with bcol1:
        sip_amount_input = st.number_input(
            "Monthly SIP Installment",
            min_value=500,
            max_value=1000000,
            value=5000,
            step=500,
            format="%d",
            help="Default is Rs 5,000 invested at the beginning of each calendar month."
        )
        st.caption(f"Monthly investment: **{dl.format_rupees(sip_amount_input)}**")
        
        # Inception date boundary
        earliest_dt = nav_df["date"].min().date() if not nav_df.empty else datetime.date(2021, 1, 1)
        default_start = max(earliest_dt, datetime.date(2021, 1, 1))
        
        sip_start_date = st.date_input(
            "SIP Start Date",
            value=default_start,
            min_value=earliest_dt,
            max_value=datetime.date.today(),
            help="Default benchmark start date is 1 Jan 2021."
        )
        st.caption(f"Simulation starts from: **{dl.format_date(sip_start_date)}**")
        
    sip_res = dl.backtest_sip(nav_df, sip_amount_input, sip_start_date.isoformat())
    
    if sip_res and sip_res.get("installments_count", 0) > 0:
        with bcol2:
            scol1, scol2 = st.columns(2)
            with scol1:
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Total Amount Invested</div>
                    <div class='result-val'>{dl.format_rupees(sip_res['total_invested'])}</div>
                    <div class='result-subtext'>{sip_res['installments_count']} monthly installments</div>
                </div>
                """)
            with scol2:
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Current Portfolio Value</div>
                    <div class='result-val-highlight'>{dl.format_rupees(sip_res['current_value'])}</div>
                    <div class='result-subtext'>Holding {sip_res['total_units']:.4f} units @ Rs {sip_res['latest_nav']:.2f}</div>
                </div>
                """)
                
            scol3, scol4 = st.columns(2)
            with scol3:
                gain_val = sip_res["absolute_gain"]
                val_cls = "result-val-gain" if gain_val >= 0 else "result-val-danger"
                arrow = "▲ " if gain_val >= 0 else "▼ "
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Absolute Profit / Loss</div>
                    <div class='{val_cls}'>{arrow}{dl.format_rupees(gain_val)}</div>
                    <div class='result-subtext'>Absolute return: {dl.format_percentage(sip_res['absolute_gain_pct'], show_sign=True)}</div>
                </div>
                """)
            with scol4:
                xirr_val = sip_res["xirr_pct"]
                x_cls = "result-val-gain" if xirr_val >= 0 else "result-val-danger"
                x_arrow = "▲ " if xirr_val >= 0 else "▼ "
                dl.render_html(f"""
                <div class='result-card'>
                    <div class='result-label'>Annualized Return (XIRR)</div>
                    <div class='{x_cls}'>{x_arrow}{dl.format_percentage(xirr_val, show_sign=True)}</div>
                    <div class='result-subtext'>True internal rate of return</div>
                </div>
                """)
                
        # SIP Progression Chart (Invested vs Portfolio Value)
        traj_df = sip_res.get("trajectory_df", pd.DataFrame())
        if not traj_df.empty:
            st.write("#### Portfolio Growth: Cumulative Invested vs Valuation")
            chart_sip = traj_df[["date", "invested_amount", "portfolio_value"]].copy().set_index("date")
            chart_sip.columns = ["Total Invested", "Portfolio Value"]
            st.line_chart(chart_sip, use_container_width=True)
            
            # Installments Sample Table
            with st.expander("View SIP Installments Ledger"):
                table_view = traj_df.copy()
                table_view["Date"] = table_view["date"].apply(lambda d: dl.format_date(d))
                table_view["NAV"] = table_view["nav"].apply(lambda n: f"Rs {n:.4f}")
                table_view["Units Added"] = table_view["units_bought"].apply(lambda u: f"{u:.4f}")
                table_view["Total Units"] = table_view["cumulative_units"].apply(lambda u: f"{u:.4f}")
                table_view["Invested"] = table_view["invested_amount"].apply(lambda a: dl.format_rupees(a))
                table_view["Valuation"] = table_view["portfolio_value"].apply(lambda v: dl.format_rupees(v))
                
                cols = ["Date", "NAV", "Units Added", "Total Units", "Invested", "Valuation"]
                st.dataframe(table_view[cols], use_container_width=True, hide_index=True)
                
        with st.expander("How this is calculated"):
            st.markdown(f"""
**XIRR Mathematical Formulation** (from `docs/finance-formulas.md`):
$$\\sum_{{j=1}}^{{n}} \\frac{{C_j}}{{(1 + R)^{{(t_j - t_0)/365.25}}}} = 0$$

**Parameters & Cash Flow Schedule:**
- Each monthly SIP installment is an outflow: $C_j = -\\text{{{dl.format_rupees(sip_res['monthly_amount'])}}}$ on date $t_j$.
- The final terminal valuation is an inflow: $C_n = +\\text{{{dl.format_rupees(sip_res['current_value'])}}}$ on latest date {dl.format_date(sip_res['latest_date'])}.
- Total Installments: `{sip_res['installments_count']}` months.
- Solved using the Newton-Raphson numeric root-finding algorithm.
- **Resulting XIRR:** **`{sip_res['xirr_pct']:.2f}%`** per annum.
            """)
    else:
        st.warning("No SIP installments could be simulated for the chosen date range. Please select an earlier start date.")


# ==============================================================================
# TAB 4: Compare Two Funds (Rebased to 100 on Common Start Date)
# ==============================================================================
with tab4:
    st.subheader("Head-to-Head Scheme Comparison")
    st.caption("Rebase two mutual fund NAV series to 100 on their common inception date to compare relative wealth generation on a single normalized chart.")
    
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        st.write("##### Primary Scheme (Fund 1)")
        fund1_code = selected_code
        fund1_name = scheme_name
        st.markdown(f"**{fund1_name}** (`{fund1_code}`)")
        
    with comp_col2:
        st.write("##### Secondary Scheme (Fund 2)")
        comp_search = st.text_input("Search Second Fund", value="UTI Nifty 50 Index", key="comp_fund_search")
        comp_search_res = dl.search_mutual_funds(comp_search)
        comp_matches = comp_search_res.get("data", [])
        if not comp_matches:
            comp_matches = [
                {"schemeCode": 120716, "schemeName": "UTI Nifty 50 Index Fund - Direct Plan - Growth"},
                {"schemeCode": 119551, "schemeName": "Tata Digital India Fund - Direct Plan - Growth"},
                {"schemeCode": 125354, "schemeName": "Mirae Asset Large Cap Fund - Direct Plan - Growth"}
            ]
        comp_scheme_map = {f"{item['schemeName']} (Code: {item['schemeCode']})": item["schemeCode"] for item in comp_matches}
        selected_comp_label = st.selectbox("Select Benchmark / Peer Scheme", list(comp_scheme_map.keys()), index=0)
        fund2_code = comp_scheme_map[selected_comp_label]
        
    # Fetch details for Fund 2
    fund2_details = dl.get_mutual_fund_details(fund2_code)
    nav_df2 = fund2_details.get("df", pd.DataFrame())
    fund2_name = fund2_details.get("meta", {}).get("scheme_name", selected_comp_label)
    
    if not nav_df.empty and not nav_df2.empty:
        comp_res = dl.compare_funds(nav_df, nav_df2, label1=fund1_name, label2=fund2_name)
        
        if comp_res and not comp_res.get("merged_df", pd.DataFrame()).empty:
            merged_df = comp_res["merged_df"]
            c_start = comp_res["common_start_date"]
            
            dl.render_html(f"""
            <div style='background-color: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 0.75rem 1.25rem; margin-bottom: 1rem; color: #94a3b8; font-size: 0.88rem;'>
                📅 <strong>Common Comparison Inception:</strong> Both funds normalized to base value <strong>100.00</strong> starting on <strong>{dl.format_date(c_start)}</strong> ({len(merged_df)} daily observations).
            </div>
            """)
            
            # Side-by-side CAGR comparison metrics
            cagrs1 = comp_res["cagrs1"]
            cagrs2 = comp_res["cagrs2"]
            
            def get_cagr_str(c_dict, key):
                if c_dict and c_dict.get(key):
                    return dl.format_percentage(c_dict[key]["cagr_pct"], show_sign=True)
                return "N/A"
                
            comp_table_rows = [
                {
                    "Metric / Characteristic": "Scheme Name",
                    "Fund 1": fund1_name,
                    "Fund 2": fund2_name
                },
                {
                    "Metric / Characteristic": "Fund House",
                    "Fund 1": meta.get("fund_house", "N/A"),
                    "Fund 2": fund2_details.get("meta", {}).get("fund_house", "N/A")
                },
                {
                    "Metric / Characteristic": "Category",
                    "Fund 1": meta.get("scheme_category", "N/A"),
                    "Fund 2": fund2_details.get("meta", {}).get("scheme_category", "N/A")
                },
                {
                    "Metric / Characteristic": "Latest NAV",
                    "Fund 1": f"Rs {fund_details.get('latest_nav', 0.0):.4f}",
                    "Fund 2": f"Rs {fund2_details.get('latest_nav', 0.0):.4f}"
                },
                {
                    "Metric / Characteristic": "1-Year CAGR",
                    "Fund 1": get_cagr_str(cagrs1, "1y"),
                    "Fund 2": get_cagr_str(cagrs2, "1y")
                },
                {
                    "Metric / Characteristic": "3-Year CAGR",
                    "Fund 1": get_cagr_str(cagrs1, "3y"),
                    "Fund 2": get_cagr_str(cagrs2, "3y")
                },
                {
                    "Metric / Characteristic": "5-Year CAGR",
                    "Fund 1": get_cagr_str(cagrs1, "5y"),
                    "Fund 2": get_cagr_str(cagrs2, "5y")
                }
            ]
            
            st.dataframe(pd.DataFrame(comp_table_rows), use_container_width=True, hide_index=True)
            
            # Rebased Line Chart (Keep DatetimeIndex for chronological ordering)
            plot_rebased = merged_df[["date", "rebased_1", "rebased_2"]].copy().set_index("date")
            plot_rebased.columns = [f"Fund 1: {fund1_name[:30]}...", f"Fund 2: {fund2_name[:30]}..."]
            st.line_chart(plot_rebased, use_container_width=True)
            
            with st.expander("How this is calculated"):
                st.markdown(f"""
**Rebasing Formula:**
$$\\text{{Rebased NAV}}_i(t) = \\frac{{\\text{{NAV}}_i(t)}}{{\\text{{NAV}}_i(t_0)}} \\times 100$$
Where $t_0$ is the latest mutual start date: **{dl.format_date(c_start)}**.
This levels the playing field so a hypothetical Rs 100 invested on day one in each scheme can be tracked directly over time regardless of differing nominal unit prices.
                """)
        else:
            st.warning("Could not find overlapping dates between the two schemes.")
    else:
        st.warning("Historical data missing for one or both schemes.")


# Mandatory Educational Disclosure (Rule 7)
dl.render_html("""
<div class='footer-disclaimer'>
    Arth is a learning platform. Nothing here is investment advice.
</div>
""")
