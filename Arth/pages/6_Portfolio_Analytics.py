"""
pages/6_Portfolio_Analytics.py - Portfolio Analytics & Risk Intelligence for Arth
Module 5 of 5: Asset & Sector Allocation Donuts, Whole-Account XIRR, Risk Metrics (Volatility, Drawdown, Beta),
Concentration Analysis, Printable Statement, CSV Exports, and Class Leaderboard.
Follows AGENTS.md, docs/house-style.md, and docs/finance-formulas.md.
"""

import streamlit as st
import pandas as pd
import datetime
import altair as alt
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Portfolio Analytics — Arth",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Calm, High-Contrast Dark Fintech Aesthetic & Clean One-Page Print Styling)
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
    
    /* Result and Stat Cards */
    .result-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
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
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc !important;
        line-height: 1.2;
    }
    .result-val-gain {
        color: #34d399 !important;
    }
    .result-val-danger {
        color: #f87171 !important;
    }
    .result-sub {
        font-size: 0.86rem;
        color: #94a3b8 !important;
        margin-top: 0.35rem;
        line-height: 1.4;
    }
    
    /* Section Headings */
    .section-hdr {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-top: 1.75rem;
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }
    
    /* Alert Cards */
    .alert-card-warning {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #fbbf24 !important;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .alert-card-success {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #34d399 !important;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Statement Printable Styling */
    .statement-box {
        background-color: #0f172a;
        border: 2px solid #334155;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        color: #f8fafc;
    }
    .statement-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #f8fafc !important;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }
    .statement-meta {
        font-size: 0.9rem;
        color: #94a3b8 !important;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 0.75rem;
    }
    .statement-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .statement-stat {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 0.85rem;
    }
    .statement-stat-lbl {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94a3b8 !important;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .statement-stat-val {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f8fafc !important;
    }
    
    /* Browser Print CSS (@media print) */
    @media print {
        header, footer, [data-testid="stSidebar"], .stButton, .no-print, [data-testid="stHeader"] {
            display: none !important;
        }
        @page {
            size: A4 portrait;
            margin: 10mm;
        }
        body, .main, .block-container {
            background-color: #ffffff !important;
            color: #000000 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .statement-box {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            border-radius: 0 !important;
            padding: 10mm !important;
            margin: 0 !important;
            box-shadow: none !important;
            page-break-inside: avoid;
        }
        .statement-title {
            color: #000000 !important;
        }
        .statement-meta {
            color: #333333 !important;
            border-bottom: 1px solid #666666 !important;
        }
        .statement-stat {
            background-color: #f8fafc !important;
            border: 1px solid #cccccc !important;
            color: #000000 !important;
        }
        .statement-stat-lbl {
            color: #555555 !important;
        }
        .statement-stat-val {
            color: #000000 !important;
        }
        table {
            color: #000000 !important;
            border-collapse: collapse !important;
        }
        th, td {
            border: 1px solid #cccccc !important;
            color: #000000 !important;
            padding: 4px 8px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database & State
dl.init_db()
dl.init_paper_trading_db()

# Page Header
dl.render_html("""
<div class='page-title'>
    Portfolio Analytics
    <span class='page-title-badge'>Module 5</span>
</div>
<div class='page-desc'>
    Read-only institutional risk and performance intelligence: asset & sector allocation donuts,
    whole-account XIRR, annualised volatility, maximum drawdown, market beta, portfolio concentration,
    printable statement, and the class leaderboard.
</div>
""")

# Fetch live paper trading data
account = dl.get_paper_account()
summary = dl.get_paper_holdings_summary()
trade_log = dl.get_paper_trade_log()
vs_nifty = dl.get_paper_vs_nifty()

cash_balance = summary["cash_balance"]
total_invested = summary["total_invested"]
total_current_value = summary["total_current_value"]
total_unrealised = summary["total_unrealised_pnl"]
total_account_value = summary["total_account_value"]
overall_return_pct = summary["overall_return_pct"]
holdings = summary["holdings"]
trader_name = account.get("display_name", "Student Trader")

# ==============================================================================
# Top Portfolio Overview Cards
# ==============================================================================
ret_cls = "result-val-gain" if overall_return_pct >= 0 else "result-val-danger"
unreal_cls = "result-val-gain" if total_unrealised >= 0 else "result-val-danger"

c1, c2, c3, c4 = st.columns(4)

with c1:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Total Account Value</div>
        <div class='result-val'>{dl.format_rupees(total_account_value)}</div>
        <div class='result-sub'>Starting Cash: {dl.format_rupees(1000000.0)}</div>
    </div>
    """)

with c2:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Overall Return</div>
        <div class='result-val {ret_cls}'>{overall_return_pct:+.2f}%</div>
        <div class='result-sub'>Net Profit: {dl.format_rupees(total_account_value - 1000000.0)}</div>
    </div>
    """)

with c3:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Available Cash</div>
        <div class='result-val'>{dl.format_rupees(cash_balance)}</div>
        <div class='result-sub'>{(cash_balance / total_account_value * 100.0 if total_account_value > 0 else 100.0):.1f}% of total portfolio</div>
    </div>
    """)

with c4:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Holdings Value</div>
        <div class='result-val'>{dl.format_rupees(total_current_value)}</div>
        <div class='result-sub'>Unrealised P&L: <span class='{unreal_cls}'>{dl.format_rupees(total_unrealised)}</span></div>
    </div>
    """)


# ==============================================================================
# Empty State Notice if No Trades
# ==============================================================================
if trade_log.empty:
    st.info("💡 You have not executed any trades yet. Showing initial allocation of Rs 10,00,000 cash. Execute simulated trades on the Paper Trading page to unlock active return tracking, XIRR, and risk intelligence.")


# ==============================================================================
# Section 1: Asset & Sector Allocation (Donut Charts)
# ==============================================================================
dl.render_html("<div class='section-hdr'>1. Asset & Sector Allocation</div>")
st.caption("Interactive distribution of your current account value by company and by industry sector, with virtual cash modeled as its own dedicated slice.")

alloc_data = dl.get_portfolio_allocation()
company_df = alloc_data["company_df"]
sector_df = alloc_data["sector_df"]

col_alloc_a, col_alloc_b = st.columns(2, gap="large")

with col_alloc_a:
    st.markdown("##### By Company")
    if not company_df.empty:
        # Altair Donut Chart
        chart_comp = alt.Chart(company_df).mark_arc(innerRadius=65, outerRadius=115).encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(
                field="label",
                type="nominal",
                scale=alt.Scale(scheme="category10"),
                legend=alt.Legend(title="", orient="bottom", labelColor="#cbd5e1", labelFontSize=11)
            ),
            tooltip=[
                alt.Tooltip(field="label", type="nominal", title="Asset / Company"),
                alt.Tooltip(field="value", type="quantitative", format=",.2f", title="Current Value (Rs)"),
                alt.Tooltip(field="percentage", type="quantitative", format=".2f", title="Portfolio Share (%)")
            ]
        ).properties(
            height=320,
            background="transparent"
        ).configure_view(strokeOpacity=0)
        st.altair_chart(chart_comp, use_container_width=True)
    else:
        st.info("No allocation data available.")

with col_alloc_b:
    st.markdown("##### By Sector")
    if not sector_df.empty:
        # Altair Donut Chart
        chart_sec = alt.Chart(sector_df).mark_arc(innerRadius=65, outerRadius=115).encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(
                field="sector",
                type="nominal",
                scale=alt.Scale(scheme="tableau10"),
                legend=alt.Legend(title="", orient="bottom", labelColor="#cbd5e1", labelFontSize=11)
            ),
            tooltip=[
                alt.Tooltip(field="sector", type="nominal", title="Industry Sector"),
                alt.Tooltip(field="value", type="quantitative", format=",.2f", title="Current Value (Rs)"),
                alt.Tooltip(field="percentage", type="quantitative", format=".2f", title="Portfolio Share (%)")
            ]
        ).properties(
            height=320,
            background="transparent"
        ).configure_view(strokeOpacity=0)
        st.altair_chart(chart_sec, use_container_width=True)
    else:
        st.info("No sector data available.")


# ==============================================================================
# Section 2: Whole-Account XIRR & Dated Cash Flows
# ==============================================================================
dl.render_html("<div class='section-hdr'>2. Whole-Account XIRR (Extended Internal Rate of Return)</div>")
st.caption("Exact annualized money-weighted return accounting for every trade cash outflow (buys), inflow (sells), and today's total portfolio valuation.")

xirr_res = dl.get_portfolio_xirr()
col_xirr_a, col_xirr_b = st.columns([1, 2], gap="medium")

with col_xirr_a:
    if xirr_res.get("has_xirr") and xirr_res.get("xirr_pct") is not None:
        x_val = xirr_res["xirr_pct"]
        x_cls = "result-val-gain" if x_val >= 0 else "result-val-danger"
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Whole-Account XIRR</div>
            <div class='result-val {x_cls}'>{x_val:+.2f}%</div>
            <div class='result-sub'>{xirr_res['message']}</div>
        </div>
        """)
    elif xirr_res.get("same_day"):
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Whole-Account XIRR</div>
            <div class='result-val {ret_cls}'>{xirr_res['return_pct']:+.2f}%*</div>
            <div class='result-sub'>*Same-day return. Annualised XIRR requires at least 1 calendar day between transactions.</div>
        </div>
        """)
    else:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Whole-Account XIRR</div>
            <div class='result-val'>insufficient history</div>
            <div class='result-sub'>{xirr_res.get('message', 'Execute trades across multiple days to compute annualised XIRR.')}</div>
        </div>
        """)

with col_xirr_b:
    st.markdown("""
    **Understanding Whole-Account XIRR:**
    Unlike simple point-to-point percentage gain, **XIRR (Extended Internal Rate of Return)** is a money-weighted annualized return metric.
    It discounts every specific cash event by the exact number of days elapsed from inception:
    - **Purchases (Buys)** are negative cash outflows (capital injected).
    - **Proceeds (Sells)** are positive cash inflows (capital extracted).
    - **Today's Total Account Value** is the terminal positive valuation.
    
    *Note on annualisation:* XIRR is an annualized rate. Shorter-term returns are projected over a full 365-day compounding basis, meaning that a small gain in a few weeks compounds to an annualized XIRR significantly higher than the simple percentage gain.
    """)

# Expandable Dated Cash Flow Ledger
cf_df = xirr_res.get("cash_flows_df", pd.DataFrame())
with st.expander("📋 View Dated Cash-Flow Ledger (Inputs plugged into XIRR solver)", expanded=False):
    if not cf_df.empty:
        display_cf = cf_df[["Date", "Type", "Description", "Direction", "Amount"]].copy()
        st.dataframe(display_cf, use_container_width=True, hide_index=True)
    else:
        st.caption("No cash flows recorded yet. Complete paper trades to populate the cash flow ledger.")

# Expandable "How this is calculated" for XIRR (Rule 1 & Rule 8)
with st.expander("ℹ️ How this is calculated — XIRR Formula", expanded=False):
    st.markdown("""
    **Mathematical Formula (from `docs/finance-formulas.md`):**
    
    $$\\text{NPV} = \\sum_{i=0}^{N} \\frac{\\text{CF}_i}{(1 + r)^{\\frac{d_i - d_0}{365.25}}} = 0$$
    
    Where:
    - $\\text{CF}_i$ = Dated cash flow amount (every Buy is negative, every Sell is positive, and current account value is positive).
    - $d_i$ = Date of cash flow $i$, where $d_0$ is the date of the first cash flow.
    - $r$ = Annualized Internal Rate of Return (XIRR), solved using Newton-Raphson iteration with bisection fallback.
    """)


# ==============================================================================
# Section 3: Risk Intelligence (Volatility, Drawdown, Beta)
# ==============================================================================
dl.render_html("<div class='section-hdr'>3. Portfolio Risk Intelligence</div>")
st.caption("Institutional risk metrics evaluated against daily portfolio valuations and benchmarked against Nifty 50 (^NSEI).")

risk_res = dl.get_portfolio_risk_metrics()

r_col1, r_col2, r_col3 = st.columns(3)

with r_col1:
    vol_val = risk_res.get("volatility_pct")
    if vol_val is not None:
        val_str = f"{vol_val:.2f}%"
    else:
        val_str = "insufficient history"
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Annualised Volatility</div>
        <div class='result-val'>{val_str}</div>
        <div class='result-sub'>Volatility measures how widely your daily portfolio value swings; higher numbers indicate larger price fluctuations.</div>
    </div>
    """)

with r_col2:
    mdd_val = risk_res.get("max_drawdown_pct")
    p_date = risk_res.get("peak_date")
    t_date = risk_res.get("trough_date")
    if mdd_val is not None:
        if mdd_val > 0:
            mdd_str = f"-{mdd_val:.2f}%"
            date_sub = f"Peak: {dl.format_date(p_date)} • Trough: {dl.format_date(t_date)}"
        else:
            mdd_str = "0.00%"
            date_sub = f"Peak: {dl.format_date(p_date)} • No drawdown (flat or rising)"
    else:
        mdd_str = "0.00%"
        date_sub = "Requires historical checkpoints"
        
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Maximum Drawdown</div>
        <div class='result-val result-val-danger'>{mdd_str}</div>
        <div class='result-sub'>Maximum drawdown shows the steepest percentage drop your portfolio experienced from its highest peak to its lowest trough, indicating worst-case temporary decline.</div>
        <div style='font-size: 0.78rem; color: #64748b; margin-top: 0.25rem;'>{date_sub}</div>
    </div>
    """)

with r_col3:
    beta_val = risk_res.get("beta")
    if beta_val is not None:
        beta_str = f"{beta_val:.2f}"
    else:
        beta_str = "insufficient history"
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Beta vs Nifty 50 (^NSEI)</div>
        <div class='result-val'>{beta_str}</div>
        <div class='result-sub'>Beta measures your portfolio's sensitivity to market swings — a beta of 1.0 moves in tandem with Nifty 50, while below 1.0 means lower market sensitivity.</div>
    </div>
    """)

if risk_res.get("status") == "insufficient_history":
    st.info(f"ℹ️ {risk_res.get('message', 'Daily history has fewer points than required. Risk metrics will automatically compute as your trading history grows.')}")

# Expandable "How this is calculated" for Risk Metrics (Rule 1 & Rule 8)
with st.expander("ℹ️ How this is calculated — Risk Formulas", expanded=False):
    st.markdown("""
    **Formulas implemented directly from `docs/finance-formulas.md`:**
    
    1. **Annualised Volatility**:
       $$\\sigma_{\\text{annual}} = \\text{std}(R_{\\text{daily}}) \\times \\sqrt{252}$$
       Where $R_{\\text{daily}} = \\frac{V_t - V_{t-1}}{V_{t-1}}$ represents daily percentage returns across trading sessions.
       
    2. **Maximum Drawdown**:
       $$\\text{MDD} = \\max_{t} \\left( \\frac{\\max_{s \\le t} V_s - V_t}{\\max_{s \\le t} V_s} \\right) \\times 100\\%$$
       Measures the largest observed loss from a peak to a trough of a portfolio, before a new peak is attained.
       
    3. **Beta against Nifty 50**:
       $$\\beta = \\frac{\\text{Cov}(R_{\\text{portfolio}}, R_{\\text{Nifty}})}{\\text{Var}(R_{\\text{Nifty}})}$$
       Evaluates systematic co-movement between your account returns and benchmark index returns.
    """)


# ==============================================================================
# Section 4: Single-Stock Concentration Analysis
# ==============================================================================
dl.render_html("<div class='section-hdr'>4. Single-Stock Concentration Analysis</div>")
st.caption("Monitors single-company exposure to prevent capital vulnerability. Single stock allocations above 25% trigger an active concentration alert.")

conc_res = dl.get_portfolio_concentration()
largest_name = conc_res["largest_name"]
largest_ticker = conc_res["largest_ticker"]
largest_weight = conc_res["largest_weight_pct"]
is_above_25 = conc_res["is_above_25"]
conc_note = conc_res["note"]

col_conc_a, col_conc_b = st.columns([1, 2], gap="medium")

with col_conc_a:
    w_cls = "result-val-danger" if is_above_25 else "result-val-gain"
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Largest Position Weight</div>
        <div class='result-val {w_cls}'>{largest_weight:.2f}%</div>
        <div class='result-sub'>{largest_name} ({largest_ticker})</div>
    </div>
    """)

with col_conc_b:
    if is_above_25:
        dl.render_html(f"""
        <div class='alert-card-warning'>
            <span>⚠️</span>
            <div><strong>Concentration Alert:</strong> {conc_note}</div>
        </div>
        """)
    else:
        dl.render_html(f"""
        <div class='alert-card-success'>
            <span>🛡️</span>
            <div><strong>Healthy Diversification:</strong> {conc_note}</div>
        </div>
        """)
    st.progress(min(1.0, max(0.0, largest_weight / 100.0)))


# ==============================================================================
# Section 5: Printable Statement (One-Page Browser Print)
# ==============================================================================
dl.render_html("<div class='section-hdr'>5. Printable Portfolio Statement</div>")
st.caption("A clean, formal, one-page financial audit statement ready for direct browser printing or saving as a PDF.")

# Compute statement data
recon = dl.get_paper_reconciliation()
tot_realised = recon["total_realised_pnl"]
tot_costs = recon["total_costs"]
today_str = dl.format_date(datetime.date.today())

# Versus Nifty status
vs_txt = ""
if vs_nifty.get("has_trades"):
    if vs_nifty.get("is_portfolio_ahead"):
        vs_txt = f"Ahead of Nifty 50 by {dl.format_rupees(vs_nifty['ahead_amount'])}"
    else:
        vs_txt = f"Trailing Nifty 50 by {dl.format_rupees(vs_nifty['ahead_amount'])}"
else:
    vs_txt = "Benchmark tracking begins with your first trade"

# Print Trigger Button
col_pr_btn, _ = st.columns([1, 3])
with col_pr_btn:
    if st.button("🖨️ Print Statement / Save PDF", use_container_width=True, type="primary"):
        st.components.v1.html("""
        <script>
            window.parent.focus();
            window.parent.print();
        </script>
        """, height=0)

# Printable Statement HTML Card
holdings_table_rows = ""
if holdings:
    for h in holdings:
        pnl_sign = "+" if h["unrealised_pnl"] >= 0 else ""
        holdings_table_rows += f"""
        <tr>
            <td style='padding: 6px 10px; border-bottom: 1px solid #1e293b;'>{h['company_name']} ({h['ticker']})</td>
            <td style='padding: 6px 10px; border-bottom: 1px solid #1e293b; text-align: right;'>{h['quantity']}</td>
            <td style='padding: 6px 10px; border-bottom: 1px solid #1e293b; text-align: right;'>{dl.format_rupees(h['avg_buy_price'])}</td>
            <td style='padding: 6px 10px; border-bottom: 1px solid #1e293b; text-align: right;'>{dl.format_rupees(h['last_price'])}</td>
            <td style='padding: 6px 10px; border-bottom: 1px solid #1e293b; text-align: right;'>{dl.format_rupees(h['current_value'])}</td>
            <td style='padding: 6px 10px; border-bottom: 1px solid #1e293b; text-align: right;'>{pnl_sign}{dl.format_rupees(h['unrealised_pnl'])} ({pnl_sign}{h['unrealised_pnl_pct']:.2f}%)</td>
        </tr>
        """
else:
    holdings_table_rows = """
    <tr>
        <td colspan='6' style='padding: 10px; text-align: center; color: #94a3b8;'>No equity positions held. Account is 100% in cash.</td>
    </tr>
    """

xirr_display_str = f"{x_val:+.2f}%" if (xirr_res.get("has_xirr") and xirr_res.get("xirr_pct") is not None) else ("Same day" if xirr_res.get("same_day") else "insufficient history")
vol_display_str = f"{vol_val:.2f}%" if vol_val is not None else "insufficient history"
mdd_display_str = f"-{mdd_val:.2f}%" if (mdd_val is not None and mdd_val > 0) else "0.00%"
beta_display_str = f"{beta_val:.2f}" if beta_val is not None else "insufficient history"

dl.render_html(f"""
<div class='statement-box'>
    <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;'>
        <div>
            <div class='statement-title'>Arth Portfolio Statement</div>
            <div class='statement-meta'>Trader: <strong>{trader_name}</strong> • Date: <strong>{today_str}</strong> • Base Currency: <strong>INR (Rs)</strong></div>
        </div>
        <div style='text-align: right; color: #94a3b8; font-size: 0.82rem;'>
            Official Simulation Report<br>
            arth.db Local Ledger
        </div>
    </div>
    
    <div class='statement-grid'>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Account Valuation</div>
            <div class='statement-stat-val'>{dl.format_rupees(total_account_value)}</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Cash Balance</div>
            <div class='statement-stat-val'>{dl.format_rupees(cash_balance)}</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Realised P&L</div>
            <div class='statement-stat-val'>{dl.format_rupees(tot_realised)}</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Unrealised P&L</div>
            <div class='statement-stat-val'>{dl.format_rupees(total_unrealised)}</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Total Costs Paid</div>
            <div class='statement-stat-val'>{dl.format_rupees(tot_costs)}</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Overall Return</div>
            <div class='statement-stat-val'>{overall_return_pct:+.2f}%</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Whole-Account XIRR</div>
            <div class='statement-stat-val'>{xirr_display_str}</div>
        </div>
        <div class='statement-stat'>
            <div class='statement-stat-lbl'>Versus Nifty 50</div>
            <div class='statement-stat-val' style='font-size: 0.92rem;'>{vs_txt}</div>
        </div>
    </div>
    
    <div style='margin-bottom: 1.5rem;'>
        <div style='font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.04em;'>Risk Intelligence</div>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;'>
            <div class='statement-stat'>
                <div class='statement-stat-lbl'>Annualised Volatility</div>
                <div class='statement-stat-val'>{vol_display_str}</div>
            </div>
            <div class='statement-stat'>
                <div class='statement-stat-lbl'>Maximum Drawdown</div>
                <div class='statement-stat-val'>{mdd_display_str}</div>
            </div>
            <div class='statement-stat'>
                <div class='statement-stat-lbl'>Beta vs ^NSEI</div>
                <div class='statement-stat-val'>{beta_display_str}</div>
            </div>
        </div>
    </div>
    
    <div>
        <div style='font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.04em;'>Holdings Portfolio</div>
        <table style='width: 100%; border-collapse: collapse; font-size: 0.88rem;'>
            <thead>
                <tr style='background-color: #1e293b; color: #94a3b8; text-transform: uppercase; font-size: 0.76rem; letter-spacing: 0.05em;'>
                    <th style='padding: 8px 10px; text-align: left;'>Company / Ticker</th>
                    <th style='padding: 8px 10px; text-align: right;'>Quantity</th>
                    <th style='padding: 8px 10px; text-align: right;'>Avg Buy Price</th>
                    <th style='padding: 8px 10px; text-align: right;'>Current Price</th>
                    <th style='padding: 8px 10px; text-align: right;'>Invested Value</th>
                    <th style='padding: 8px 10px; text-align: right;'>Unrealised P&L</th>
                </tr>
            </thead>
            <tbody>
                {holdings_table_rows}
            </tbody>
        </table>
    </div>
    
    <div style='margin-top: 1.75rem; padding-top: 0.75rem; border-top: 1px solid #1e293b; text-align: center; color: #64748b; font-size: 0.82rem;'>
        Arth is a learning platform. Nothing here is investment advice.
    </div>
</div>
""")


# ==============================================================================
# Section 6: CSV Data Downloads
# ==============================================================================
dl.render_html("<div class='section-hdr'>6. Export Portfolio Records</div>")
st.caption("Generate instant CSV backups of your current equity holdings and complete chronological trade execution log.")

col_exp_a, col_exp_b = st.columns(2)

with col_exp_a:
    if holdings:
        h_export_df = pd.DataFrame(holdings)
    else:
        h_export_df = pd.DataFrame(columns=["ticker", "company_name", "quantity", "avg_buy_price", "last_price", "invested_value", "current_value", "unrealised_pnl", "unrealised_pnl_pct"])
    h_csv = h_export_df.to_csv(index=False).encode("utf-8-sig")
    
    st.download_button(
        label="📥 Download Holdings (CSV)",
        data=h_csv,
        file_name=f"arth_holdings_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp_b:
    t_csv = trade_log.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Download Full Trade Log (CSV)",
        data=t_csv,
        file_name=f"arth_trade_log_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==============================================================================
# Section 7: Class Leaderboard Integration
# ==============================================================================
dl.render_html("<div class='section-hdr'>7. Class Leaderboard</div>")
st.caption("Share your trading performance metrics with your cohort. Appends one row to leaderboard.csv at the top of the project.")

col_share_a, col_share_b = st.columns([1, 2], gap="medium")

with col_share_a:
    st.markdown("##### Share Your Score")
    share_name = st.text_input("Trader Display Name", value=trader_name, key="share_trader_name")
    
    if st.button("🚀 Share Result to Leaderboard", use_container_width=True, type="primary"):
        ok, msg = dl.share_to_leaderboard(share_name)
        if ok:
            st.success(f"✅ {msg}")
            st.rerun()
        else:
            st.error(msg)

with col_share_b:
    st.markdown("##### Current Rankings")
    leaderboard_df = dl.get_leaderboard_df()
    
    if not leaderboard_df.empty:
        # Display styled leaderboard
        disp_lb = leaderboard_df.copy()
        # Format currency & numbers
        disp_lb["account_value"] = disp_lb["account_value"].apply(lambda v: dl.format_rupees(v))
        disp_lb["return_pct"] = disp_lb["return_pct"].apply(lambda v: f"{float(v):+.2f}%")
        disp_lb = disp_lb.rename(columns={
            "rank": "Rank",
            "name": "Trader",
            "date": "Date",
            "account_value": "Account Value",
            "return_pct": "Return (%)",
            "xirr_pct": "XIRR",
            "max_drawdown_pct": "Max Drawdown"
        })
        st.dataframe(disp_lb, use_container_width=True, hide_index=True)
    else:
        st.info("No scores shared yet. Click 'Share Result to Leaderboard' to record your performance in leaderboard.csv!")

st.caption("ℹ️ Note for instructors and students: Scores are recorded in `leaderboard.csv` at the project root (`c:\\Users\\abcom\\Desktop\\Arth\\leaderboard.csv`). The class can combine these individual CSV files by hand into a unified leaderboard.")


# Mandatory House Style Disclaimer Footer (Rule 7)
dl.render_footer()
