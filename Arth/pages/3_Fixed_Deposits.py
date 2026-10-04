"""
pages/3_Fixed_Deposits.py - Fixed Deposits Module for Arth
Module 3 of 5: Bank FD Comparison, Quarterly Compounding Calculator, FD Laddering, and Inflation Erosion Analysis.
Follows AGENTS.md, docs/house-style.md, and docs/finance-formulas.md.
"""

import streamlit as st
import pandas as pd
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Fixed Deposits — Arth",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Fintech Theme)
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
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .asof-badge-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.75rem;
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
    }
    .asof-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0 !important;
    }
    .asof-date-pill {
        display: inline-block;
        background-color: rgba(56, 189, 248, 0.12);
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .dicgc-banner {
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 1.5rem;
        color: #a7f3d0 !important;
        font-size: 0.88rem;
        line-height: 1.4;
    }
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
    .ladder-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .ladder-tenure {
        font-size: 1rem;
        font-weight: 700;
        color: #38bdf8 !important;
    }
    .table-container {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #1e293b;
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

# Page Header
dl.render_html("""
<div class='page-title'>
    Fixed Deposits
    <span class='page-title-badge'>Module 3</span>
</div>
<div class='page-desc'>
    Compare benchmark bank FD rates across India, calculate quarterly compounding maturity with slab-based post-tax deductions, build an automated liquidity ladder, and evaluate real purchasing power against inflation.
</div>
""")

# Load FD Rates Data (Read-only from data/fd-rates.csv)
fd_df = dl.get_fd_rates_df()

if fd_df.empty:
    st.error("Fixed deposit rates data could not be loaded. Please ensure the reference dataset is present.")
    st.stop()

# Extract prominent as_of date
as_of_raw = fd_df["as_of"].iloc[0] if "as_of" in fd_df.columns else "2026-09-30"
try:
    as_of_formatted = dl.format_date(pd.to_datetime(as_of_raw))
except Exception:
    as_of_formatted = str(as_of_raw)

# Prominent As-Of Date Header & DICGC Guarantee Banner
dl.render_html(f"""
<div class='asof-badge-container'>
    <div class='asof-title'>
        🏦 Scheduled Commercial Banks & Post Office Deposit Rates
    </div>
    <div>
        <span class='asof-date-pill'>FD Rates as of {as_of_formatted}</span>
    </div>
</div>
<div class='dicgc-banner'>
    🛡️ <strong>DICGC Deposit Insurance:</strong> Deposits in each scheduled commercial bank (including small finance banks) are insured up to <strong>Rs 5,00,000</strong> per depositor across all branches for both principal and interest by the Deposit Insurance and Credit Guarantee Corporation (a wholly-owned subsidiary of RBI).
</div>
""")

# Four Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Rate Comparison Table",
    "🧮 Maturity & Tax Calculator",
    "🪜 FD Laddering Strategy",
    "🔥 FD vs Inflation (Real Returns)"
])


# ==============================================================================
# TAB 1: Rate Comparison Table
# ==============================================================================
with tab1:
    st.subheader("Bank Interest Rate Comparison")
    st.caption("Filter by deposit tenure, bank classification, or toggle senior citizen preferential rates.")
    
    fcol1, fcol2, fcol3 = st.columns([1.5, 1.5, 1])
    with fcol1:
        tenure_filter_opts = {
            "All Tenures": None,
            "12 Months (1 Year)": 12,
            "24 Months (2 Years)": 24,
            "36 Months (3 Years)": 36,
            "60 Months (5 Years)": 60
        }
        sel_tenure_label = st.selectbox("Filter Tenure", list(tenure_filter_opts.keys()), index=0)
        sel_tenure_val = tenure_filter_opts[sel_tenure_label]
        
    with fcol2:
        bank_types = ["All Types"] + sorted(list(fd_df["type"].unique()))
        sel_bank_type = st.selectbox("Filter Bank Type", bank_types, index=0)
        
    with fcol3:
        st.write("")
        st.write("")
        is_senior = st.toggle("Senior Citizen", value=False, help="Senior citizens (age 60+) typically receive an additional 0.50% interest.")

    # Filter DataFrame
    filtered_df = fd_df.copy()
    if sel_tenure_val is not None:
        filtered_df = filtered_df[filtered_df["tenure_months"] == sel_tenure_val]
    if sel_bank_type != "All Types":
        filtered_df = filtered_df[filtered_df["type"] == sel_bank_type]
        
    # Sort according to toggle
    sort_col = "rate_senior_pct" if is_senior else "rate_general_pct"
    filtered_df = filtered_df.sort_values(sort_col, ascending=False).reset_index(drop=True)
    
    # Highlight Best Rates Tiles
    bcol1, bcol2, bcol3, bcol4 = st.columns(4)
    with bcol1:
        top_rate = filtered_df.iloc[0][sort_col] if not filtered_df.empty else 0.0
        top_bank = filtered_df.iloc[0]["bank"] if not filtered_df.empty else "N/A"
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Top Selected Rate</div>
            <div class='result-val-highlight'>{dl.format_percentage(top_rate)}</div>
            <div class='result-subtext'>{top_bank}</div>
        </div>
        """)
    with bcol2:
        df_1y = fd_df[fd_df["tenure_months"] == 12].sort_values(sort_col, ascending=False)
        r_1y = df_1y.iloc[0][sort_col] if not df_1y.empty else 0.0
        b_1y = df_1y.iloc[0]["bank"] if not df_1y.empty else "N/A"
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Best 1-Year Rate</div>
            <div class='result-val-gain'>{dl.format_percentage(r_1y)}</div>
            <div class='result-subtext'>{b_1y}</div>
        </div>
        """)
    with bcol3:
        df_3y = fd_df[fd_df["tenure_months"] == 36].sort_values(sort_col, ascending=False)
        r_3y = df_3y.iloc[0][sort_col] if not df_3y.empty else 0.0
        b_3y = df_3y.iloc[0]["bank"] if not df_3y.empty else "N/A"
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Best 3-Year Rate</div>
            <div class='result-val-gain'>{dl.format_percentage(r_3y)}</div>
            <div class='result-subtext'>{b_3y}</div>
        </div>
        """)
    with bcol4:
        df_5y = fd_df[fd_df["tenure_months"] == 60].sort_values(sort_col, ascending=False)
        r_5y = df_5y.iloc[0][sort_col] if not df_5y.empty else 0.0
        b_5y = df_5y.iloc[0]["bank"] if not df_5y.empty else "N/A"
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Best 5-Year Rate</div>
            <div class='result-val-gain'>{dl.format_percentage(r_5y)}</div>
            <div class='result-subtext'>{b_5y}</div>
        </div>
        """)
        
    # Format display table
    display_df = filtered_df.copy()
    display_df["Tenure"] = display_df["tenure_months"].apply(lambda m: f"{m // 12} Year{'s' if m > 12 else ''} ({m}m)")
    display_df["General Rate"] = display_df["rate_general_pct"].apply(lambda r: dl.format_percentage(r))
    display_df["Senior Citizen Rate"] = display_df["rate_senior_pct"].apply(lambda r: dl.format_percentage(r))
    
    cols_to_show = ["bank", "type", "Tenure", "General Rate", "Senior Citizen Rate", "source_note"]
    renames = {
        "bank": "Institution / Bank",
        "type": "Classification",
        "source_note": "Source Reference"
    }
    
    st.dataframe(
        display_df[cols_to_show].rename(columns=renames),
        use_container_width=True,
        hide_index=True
    )
    
    dl.render_html(f"<div style='color: #64748b; font-size: 0.82rem; margin-top: 0.5rem;'>Data benchmark as of {as_of_formatted}. Rates apply to domestic term deposits under Rs 3 crore with quarterly compounding.</div>")


# ==============================================================================
# TAB 2: FD Maturity & Tax Calculator
# ==============================================================================
with tab2:
    st.subheader("Quarterly Compounding & Tax Calculator")
    st.caption("Calculate maturity value with standard quarterly compounding, and see how much tax is deducted at your slab.")
    
    ccol1, ccol2 = st.columns([1, 1.2], gap="large")
    
    with ccol1:
        principal_input = st.number_input(
            "Deposit Amount (Principal)",
            min_value=1000,
            max_value=100000000,
            value=100000,
            step=10000,
            format="%d",
            help="The lump sum amount you wish to deposit in the fixed deposit."
        )
        st.caption(f"Principal formatted: **{dl.format_rupees(principal_input)}**")
        
        mode = st.radio("Choose Rate Input Method", ["Pick from Benchmark Rates", "Custom Tenure & Rate"], horizontal=True)
        
        if mode == "Pick from Benchmark Rates":
            # Build picker list
            rate_col = "rate_senior_pct" if is_senior else "rate_general_pct"
            bank_options = []
            for _, r in fd_df.iterrows():
                yrs = r["tenure_months"] // 12
                lbl = f"{r['bank']} — {yrs}Y ({r['tenure_months']}m) @ {r[rate_col]:.2f}%"
                bank_options.append((lbl, r["rate_general_pct"], r["rate_senior_pct"], r["tenure_months"], r["bank"]))
                
            selected_option_lbl = st.selectbox("Select Bank & Tenure", [opt[0] for opt in bank_options], index=0)
            chosen_opt = next(opt for opt in bank_options if opt[0] == selected_option_lbl)
            rate_to_use = chosen_opt[2] if is_senior else chosen_opt[1]
            tenure_months_to_use = chosen_opt[3]
            bank_name_to_use = chosen_opt[4]
        else:
            custom_years = st.slider("Deposit Tenure (Years)", min_value=1, max_value=10, value=3, step=1)
            tenure_months_to_use = custom_years * 12
            rate_to_use = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=15.0, value=7.0, step=0.05, format="%.2f")
            bank_name_to_use = "Custom Deposit"
            
        tax_bracket_choice = st.selectbox(
            "Your Income Tax Slab Rate",
            options=[
                "0% (Tax-exempt / Form 15G or 15H)",
                "5% Slab (Effective 5.20% with cess)",
                "20% Slab (Effective 20.80% with cess)",
                "30% Slab (Effective 31.20% with cess)"
            ],
            index=3,
            help="FD interest is added to your total income and taxed at your applicable slab rate plus 4% health & education cess."
        )
        tax_bracket_map = {
            "0% (Tax-exempt / Form 15G or 15H)": 0.0,
            "5% Slab (Effective 5.20% with cess)": 5.0,
            "20% Slab (Effective 20.80% with cess)": 20.0,
            "30% Slab (Effective 31.20% with cess)": 30.0
        }
        chosen_slab_pct = tax_bracket_map[tax_bracket_choice]
        
    calc_res = dl.calc_fd_maturity(principal_input, rate_to_use, tenure_months_to_use, chosen_slab_pct)
    
    with ccol2:
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Maturity Amount (Pre-Tax)</div>
                <div class='result-val-highlight'>{dl.format_rupees(calc_res['maturity_amount'])}</div>
                <div class='result-subtext'>At {dl.format_percentage(rate_to_use)} for {calc_res['tenure_years']:.1f} yr(s)</div>
            </div>
            """)
        with rcol2:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Total Interest Earned</div>
                <div class='result-val-gain'>{dl.format_rupees(calc_res['total_interest'])}</div>
                <div class='result-subtext'>Effective APY: {dl.format_percentage(calc_res['effective_yield_pct'])}</div>
            </div>
            """)
            
        rcol3, rcol4 = st.columns(2)
        with rcol3:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Post-Tax Interest</div>
                <div class='result-val'>{dl.format_rupees(calc_res['post_tax_interest'])}</div>
                <div class='result-subtext'>Tax paid: {dl.format_rupees(calc_res['tax_amount'])} ({calc_res['effective_tax_rate_pct']:.2f}%)</div>
            </div>
            """)
        with rcol4:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Post-Tax Maturity</div>
                <div class='result-val'>{dl.format_rupees(calc_res['post_tax_maturity'])}</div>
                <div class='result-subtext'>Real post-tax yield: {dl.format_percentage(calc_res['post_tax_yield_pct'])}</div>
            </div>
            """)
            
        # Educational Tax & TDS Notice
        dl.render_html("""
        <div class='info-callout'>
            <strong>Tax & TDS Rules (Section 194A):</strong><br>
            • FD interest is not tax-free. It is added to your income under 'Income from Other Sources' and taxed at your applicable slab rate.<br>
            • Banks deduct <strong>10% TDS</strong> if total bank interest exceeds <strong>Rs 40,000</strong> per year (<strong>Rs 50,000</strong> for senior citizens). If PAN is not provided, TDS is 20%.<br>
            • If your total income is below the taxable threshold, submit <strong>Form 15G</strong> (or <strong>Form 15H</strong> for senior citizens) at the start of the financial year to avoid TDS.
        </div>
        """)
        
    with st.expander("How this is calculated"):
        st.markdown(f"""
**Mathematical Formula** (from `docs/finance-formulas.md`):
$$\\text{{FD Maturity with quarterly compounding}} = P \\times \\left(1 + \\frac{{r}}{{4}}\\right)^{{4 \\times \\text{{years}}}}$$
$$\\text{{Interest Earned}} = A - P$$
$$\\text{{Effective Tax Rate}} = \\text{{Slab Rate}} \\times 1.04$$
$$\\text{{Post-Tax Interest}} = \\text{{Interest}} \\times (1 - \\text{{Effective Tax Rate}})$$

**Plugging in the numbers:**
- Principal ($P$): `{dl.format_rupees(calc_res['principal'])}`
- Annual Interest Rate ($r$): `{rate_to_use:.2f}%` = `{rate_to_use/100:.4f}`
- Tenure ($t$): `{calc_res['tenure_years']:.2f}` years (`{calc_res['tenure_months']}` months)
- Compounding periods per year: `4` (Quarterly)
- Total compounding periods: `{int(4 * calc_res['tenure_years'])}`
- Maturity Calculation: `{calc_res['principal']:,.2f} * (1 + {rate_to_use/100:.4f} / 4)^({4 * calc_res['tenure_years']:.1f})` = **`{dl.format_rupees(calc_res['maturity_amount'])}`**
- Total Interest: `{dl.format_rupees(calc_res['maturity_amount'])} - {dl.format_rupees(calc_res['principal'])}` = **`{dl.format_rupees(calc_res['total_interest'])}`**
- Tax Slab: `{calc_res['tax_bracket_pct']:.0f}%` + 4% Cess = `{calc_res['effective_tax_rate_pct']:.2f}%`
- Tax Deducted: `{dl.format_rupees(calc_res['tax_amount'])}`
- Post-Tax Interest: **`{dl.format_rupees(calc_res['post_tax_interest'])}`**
        """)


# ==============================================================================
# TAB 3: FD Laddering Strategy
# ==============================================================================
with tab3:
    st.subheader("Automated FD Laddering Strategy")
    st.caption("Split your capital equally across 1, 2, 3, and 5-year tenures at the best available rates to maintain steady liquidity while eliminating interest rate lock-in risk.")
    
    lcol1, lcol2 = st.columns([1, 1.2], gap="large")
    
    with lcol1:
        ladder_amount_input = st.number_input(
            "Total Capital to Ladder",
            min_value=40000,
            max_value=100000000,
            value=400000,
            step=40000,
            format="%d",
            help="Total amount split equally into 4 buckets (25% each) across 1Y, 2Y, 3Y, and 5Y tenures."
        )
        st.caption(f"Each tranche receives: **{dl.format_rupees(ladder_amount_input / 4)}** (25%)")
        
        ladder_senior = st.toggle("Apply Senior Citizen Rates for Ladder", value=is_senior)
        
        ladder_bank_type = st.selectbox(
            "Restrict Ladder to Bank Type",
            ["All"] + sorted(list(fd_df["type"].unique())),
            index=0
        )
        
    ladder_data = dl.calc_fd_ladder(ladder_amount_input, is_senior=ladder_senior, bank_type_filter=ladder_bank_type)
    
    with lcol2:
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Ladder Blended Rate</div>
                <div class='result-val-highlight'>{dl.format_percentage(ladder_data['blended_rate_pct'])}</div>
                <div class='result-subtext'>Weighted average interest rate</div>
            </div>
            """)
        with mcol2:
            single_5y = ladder_data["single_5y"]
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Single 5-Year FD Rate</div>
                <div class='result-val'>{dl.format_percentage(single_5y['rate_pct'])}</div>
                <div class='result-subtext'>{single_5y['bank']}</div>
            </div>
            """)
            
        mcol3, mcol4 = st.columns(2)
        with mcol3:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Total Ladder Maturity</div>
                <div class='result-val-gain'>{dl.format_rupees(ladder_data['ladder_maturity_total'])}</div>
                <div class='result-subtext'>Interest: {dl.format_rupees(ladder_data['ladder_interest_total'])}</div>
            </div>
            """)
        with mcol4:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Single 5-Year Maturity</div>
                <div class='result-val'>{dl.format_rupees(single_5y['maturity_amount'])}</div>
                <div class='result-subtext'>Interest: {dl.format_rupees(single_5y['interest'])}</div>
            </div>
            """)
            
    # Tranche Breakdown
    st.write("#### Ladder Tranche Schedule")
    tranche_rows = []
    for b in ladder_data["buckets"]:
        tranche_rows.append({
            "Maturity Timeline": f"End of Year {b['tenure_years']}",
            "Tenure": f"{b['tenure_years']} Year{'s' if b['tenure_years'] > 1 else ''} ({b['tenure_months']}m)",
            "Bank Institution": b["bank"],
            "Category": b["bank_type"],
            "Annual Rate": dl.format_percentage(b["rate_pct"]),
            "Principal Invested": dl.format_rupees(b["principal"]),
            "Interest Earned": dl.format_rupees(b["interest"]),
            "Maturity Payout": dl.format_rupees(b["maturity_amount"])
        })
    st.dataframe(pd.DataFrame(tranche_rows), use_container_width=True, hide_index=True)
    
    # Maturity Timeline Chart
    chart_df = pd.DataFrame({
        "Timeline": [f"Year {b['tenure_years']}" for b in ladder_data["buckets"]],
        "Principal": [b["principal"] for b in ladder_data["buckets"]],
        "Interest": [b["interest"] for b in ladder_data["buckets"]],
        "Total Payout": [b["maturity_amount"] for b in ladder_data["buckets"]]
    }).set_index("Timeline")
    
    st.write("#### Maturity Payout Timeline")
    st.bar_chart(chart_df[["Principal", "Interest"]], use_container_width=True)
    
    # Strategic Educational Insight
    dl.render_html("""
    <div class='info-callout'>
        <strong>Why Use an FD Ladder?</strong><br>
        1. <strong>Predictable Liquidity:</strong> Exactly 25% of your total capital matures at regular intervals (Year 1, Year 2, Year 3, and Year 5), giving you access to cash without incurring premature withdrawal penalties.<br>
        2. <strong>Reinvestment Power:</strong> When Year 1 matures, you roll it forward into a new 5-year FD at the prevailing peak rate. Over time, your entire portfolio earns long-term 5-year rates while 20-25% matures every single year.<br>
        3. <strong>Hedging Interest Rate Cycles:</strong> If interest rates rise, you have fresh liquidity maturing soon to capture higher yields. If rates drop, your 3-year and 5-year tranches remain safely locked in at high returns.
    </div>
    """)
    
    with st.expander("How this is calculated"):
        st.markdown(f"""
**Laddering Mathematics:**
- Total Investment: `{dl.format_rupees(ladder_data['total_amount'])}`
- Tranche Size: `{dl.format_rupees(ladder_data['total_amount'] / 4.0)}` each
- Each tranche uses quarterly compounding: $A_k = P_k \\times (1 + r_k/4)^{{4 \\times t_k}}$
- **Blended Rate:** Weighted average rate = $\\frac{{r_1 + r_2 + r_3 + r_5}}{{4}} = \\frac{{{ladder_data['buckets'][0]['rate_pct']:.2f} + {ladder_data['buckets'][1]['rate_pct']:.2f} + {ladder_data['buckets'][2]['rate_pct']:.2f} + {ladder_data['buckets'][3]['rate_pct']:.2f}}}{{4}} =$ **`{ladder_data['blended_rate_pct']:.2f}%`**
- Total Ladder Maturity Payout: **`{dl.format_rupees(ladder_data['ladder_maturity_total'])}`**
- Single 5-Year FD at `{single_5y['rate_pct']:.2f}%`: **`{dl.format_rupees(single_5y['maturity_amount'])}`**
        """)


# ==============================================================================
# TAB 4: FD versus Inflation (Real Returns)
# ==============================================================================
with tab4:
    st.subheader("FD versus Inflation — The Real Return Reality")
    st.caption("Evaluate how income taxes and consumer inflation systematically erode the real purchasing power of fixed deposits.")
    
    icol1, icol2 = st.columns([1, 1.2], gap="large")
    
    with icol1:
        inf_slider = st.slider(
            "Expected Annual Inflation Rate (%)",
            min_value=2.0,
            max_value=10.0,
            value=6.0,
            step=0.25,
            format="%.2f%%",
            help="Long-term average Indian CPI inflation typically hovers between 5% and 6.5%."
        )
        
        inf_tax_choice = st.selectbox(
            "Your Applicable Tax Slab",
            options=[
                "0% (Tax-exempt)",
                "5% Slab (Effective 5.20%)",
                "20% Slab (Effective 20.80%)",
                "30% Slab (Effective 31.20%)"
            ],
            index=3,
            help="Slab rate plus 4% health and education cess."
        )
        inf_tax_map = {
            "0% (Tax-exempt)": 0.0,
            "5% Slab (Effective 5.20%)": 5.0,
            "20% Slab (Effective 20.80%)": 20.0,
            "30% Slab (Effective 31.20%)": 30.0
        }
        inf_tax_val = inf_tax_map[inf_tax_choice]
        
        test_rate = st.slider("Select Benchmark FD Rate to Test", min_value=4.0, max_value=9.5, value=6.50, step=0.25, format="%.2f%%")
        
    example_real = dl.calc_fd_real_return(test_rate, inf_tax_val, inf_slider)
    
    with icol2:
        m1, m2 = st.columns(2)
        with m1:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Nominal FD Rate</div>
                <div class='result-val'>{dl.format_percentage(test_rate)}</div>
                <div class='result-subtext'>Before tax deduction</div>
            </div>
            """)
        with m2:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Post-Tax Return</div>
                <div class='result-val'>{dl.format_percentage(example_real['post_tax_rate_pct'])}</div>
                <div class='result-subtext'>Effective tax: {example_real['effective_tax_pct']:.2f}%</div>
            </div>
            """)
            
        m3, m4 = st.columns(2)
        with m3:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Inflation Rate</div>
                <div class='result-val'>{dl.format_percentage(inf_slider)}</div>
                <div class='result-subtext'>Annual cost-of-living rise</div>
            </div>
            """)
        with m4:
            is_neg = example_real["is_negative"]
            val_cls = "result-val-danger" if is_neg else "result-val-gain"
            sign = "▼ " if is_neg else "▲ "
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Real Return (Purchasing Power)</div>
                <div class='{val_cls}'>{sign}{dl.format_percentage(example_real['real_return_pct'])}</div>
                <div class='result-subtext'>{'Losing real purchasing power' if is_neg else 'Beating inflation'}</div>
            </div>
            """)
            
    # Educational Focus Banner
    if example_real["is_negative"]:
        dl.render_html(f"""
        <div style='background-color: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.35); border-radius: 10px; padding: 1rem 1.25rem; margin: 1rem 0; color: #fecdd3;'>
            ⚠️ <strong>Wealth Erosion Alert:</strong> At a <strong>{test_rate:.2f}%</strong> FD rate in the <strong>{inf_tax_val:.0f}%</strong> tax slab, your post-tax return is only <strong>{example_real['post_tax_rate_pct']:.2f}%</strong>. Because inflation is <strong>{inf_slider:.2f}%</strong>, your real return is <strong>{example_real['real_return_pct']:.2f}%</strong>. For every year this money sits in the FD, its purchasing power shrinks.
        </div>
        """)
    else:
        dl.render_html(f"""
        <div style='background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 1rem 1.25rem; margin: 1rem 0; color: #a7f3d0;'>
            ✅ <strong>Positive Real Return:</strong> Your post-tax return of <strong>{example_real['post_tax_rate_pct']:.2f}%</strong> is higher than inflation (<strong>{inf_slider:.2f}%</strong>), providing a real purchasing power gain of <strong>+{example_real['real_return_pct']:.2f}%</strong> per year.
        </div>
        """)
        
    # Table of Real Returns Across All Banks in Dataset
    st.write(f"#### Real Returns Across Bank FDs at {inf_tax_val:.0f}% Tax Slab & {inf_slider:.2f}% Inflation")
    
    real_rows = []
    for _, r in fd_df.iterrows():
        rate_val = r["rate_senior_pct"] if is_senior else r["rate_general_pct"]
        calc_out = dl.calc_fd_real_return(rate_val, inf_tax_val, inf_slider)
        real_rows.append({
            "Bank": r["bank"],
            "Classification": r["type"],
            "Tenure": f"{r['tenure_months'] // 12}Y ({r['tenure_months']}m)",
            "Nominal Rate": dl.format_percentage(rate_val),
            "Post-Tax Rate": dl.format_percentage(calc_out["post_tax_rate_pct"]),
            "Inflation": dl.format_percentage(inf_slider),
            "Real Return": f"{calc_out['real_return_pct']:+.2f}%",
            "Real Outcome": "Erodes wealth" if calc_out["is_negative"] else "Beats inflation"
        })
    st.dataframe(pd.DataFrame(real_rows), use_container_width=True, hide_index=True)
    
    with st.expander("How this is calculated"):
        st.markdown(f"""
**The Fisher Equation for Exact Real Return** (from `docs/finance-formulas.md`):
$$\\text{{Post-tax Rate}} = r \\times \\left(1 - \\text{{Slab Rate}} \\times 1.04\\right)$$
$$\\text{{Real Return}} = \\frac{{1 + \\text{{Post-tax Rate}}}}{{1 + \\text{{Inflation Rate}}}} - 1$$

**Plugging in the numbers:**
- Nominal FD Rate ($r$): `{test_rate:.2f}%` = `{test_rate/100:.4f}`
- Slab Rate: `{inf_tax_val:.0f}%` (Effective Tax = `{example_real['effective_tax_pct']:.2f}%`)
- Post-tax Rate: `{test_rate/100:.4f} * (1 - {example_real['effective_tax_pct']/100:.4f})` = **`{example_real['post_tax_rate_pct']:.2f}%`** (`{example_real['post_tax_rate_pct']/100:.5f}`)
- Inflation Rate: `{inf_slider:.2f}%` = `{inf_slider/100:.4f}`
- Exact Real Return: $\\frac{{1 + {example_real['post_tax_rate_pct']/100:.5f}}}{{1 + {inf_slider/100:.4f}}} - 1$ = **`{example_real['real_return_pct']:.2f}%`**
        """)


# Mandatory Educational Disclosure (Rule 7)
dl.render_html("""
<div class='footer-disclaimer'>
    Arth is a learning platform. Nothing here is investment advice.
</div>
""")
