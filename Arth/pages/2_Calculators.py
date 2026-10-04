"""
pages/2_Calculators.py - Financial Calculators Module for Arth
Module 2 of 5: Nine First-Principles Financial Calculators
Follows AGENTS.md, docs/house-style.md, and docs/finance-formulas.md.
"""

import streamlit as st
import pandas as pd
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Calculators — Arth",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Fintech Aesthetic matching Module 1)
st.markdown("""
<style>
    /* Global Container */
    .main .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Header typography */
    .page-title {
        font-size: 2.4rem;
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
        margin-bottom: 1.75rem;
        line-height: 1.5;
    }
    
    /* Result Cards */
    .result-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .result-label {
        font-size: 0.82rem;
        font-weight: 700;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.35rem;
    }
    .result-val {
        font-size: 1.75rem;
        font-weight: 800;
        color: #f8fafc !important;
        letter-spacing: -0.02em;
    }
    .result-val-highlight {
        font-size: 1.75rem;
        font-weight: 800;
        color: #38bdf8 !important;
        letter-spacing: -0.02em;
    }
    .result-val-gain {
        font-size: 1.75rem;
        font-weight: 800;
        color: #10b981 !important;
        letter-spacing: -0.02em;
    }
    .result-subtext {
        font-size: 0.85rem;
        color: #64748b !important;
        margin-top: 0.25rem;
    }
    
    /* Comparison Boxes */
    .comparison-box {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .comparison-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-bottom: 0.85rem;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 0.5rem;
    }
    
    /* Callout & Suggestion Banners */
    .calc-callout {
        background-color: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 10px;
        padding: 0.85rem 1.15rem;
        color: #e0f2fe !important;
        font-size: 0.95rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .calc-callout-success {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        padding: 0.85rem 1.15rem;
        color: #ecfdf5 !important;
        font-size: 0.95rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Table Styling */
    .calc-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .calc-table th {
        background-color: #0f172a;
        color: #94a3b8 !important;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.85rem 1rem;
        text-align: left;
        border-bottom: 1px solid #1e293b;
    }
    .calc-table th.num-col {
        text-align: right;
    }
    .calc-table td {
        padding: 0.8rem 1rem;
        font-size: 0.9rem;
        color: #f8fafc !important;
        border-bottom: 1px solid #1a2438;
    }
    .calc-table td.num-col {
        text-align: right;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .calc-table tr:last-child td {
        border-bottom: none;
    }
    .calc-table tr:hover td {
        background-color: #182239;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
dl.render_html("""
<div class='page-title'>
    Financial Calculators
    <span class='page-title-badge'>Module 2</span>
</div>
<div class='page-desc'>
    First-principles mathematical tools for Indian personal finance. Compounding models, debt amortization,
    retirement corpus, and Budget 2025 tax optimization.
</div>
""")

# Setup Tabs for the 9 Calculators
tabs = st.tabs([
    "💰 Budget (50/30/20)",
    "🏠 EMI & Loans",
    "📈 SIP Compounding",
    "🚀 Step-up SIP",
    "💼 Lump Sum",
    "🎯 Goal Planner",
    "📉 Inflation & Cash",
    "🏖️ Retirement Corpus",
    "⚖️ Tax Regime"
])


# ==============================================================================
# TAB 1: Budget Planner (50/30/20)
# ==============================================================================
with tabs[0]:
    st.markdown("### Budget Planner (50/30/20 Rule)")
    st.caption("Allocate your monthly take-home income into Needs, Wants, and Savings with flexible percentage overrides.")
    
    col_b1, col_b2 = st.columns([1, 1], gap="large")
    with col_b1:
        monthly_take_home = st.number_input(
            "Monthly Take-Home Pay (Rs)",
            min_value=0.0,
            value=100000.0,
            step=5000.0,
            key="budget_income"
        )
        needs_p = st.slider("Needs Percentage (%)", 0.0, 100.0, 50.0, 1.0, key="budget_needs_p")
        wants_p = st.slider("Wants Percentage (%)", 0.0, 100.0, 30.0, 1.0, key="budget_wants_p")
        savings_p = st.slider("Savings & Investment Percentage (%)", 0.0, 100.0, 20.0, 1.0, key="budget_savings_p")
        
        sum_p = needs_p + wants_p + savings_p
        if abs(sum_p - 100.0) > 0.01:
            st.info(f"Current allocation total: {sum_p:.1f}%. To balance your budget, ensure the three slices sum to 100%.")

    budget_res = dl.calc_budget_planner(monthly_take_home, needs_p, wants_p, savings_p)
    # Store suggested SIP in session state for Tool 3
    st.session_state["suggested_sip"] = budget_res["savings_amount"]

    with col_b2:
        res1, res2, res3 = st.columns(3)
        with res1:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Needs ({needs_p:.0f}%)</div>
                <div class='result-val'>{dl.format_rupees(budget_res['needs_amount'])}</div>
                <div class='result-subtext'>Rent, groceries, bills, EMIs</div>
            </div>
            """)
        with res2:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Wants ({wants_p:.0f}%)</div>
                <div class='result-val'>{dl.format_rupees(budget_res['wants_amount'])}</div>
                <div class='result-subtext'>Dining, travel, hobbies</div>
            </div>
            """)
        with res3:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Savings ({savings_p:.0f}%)</div>
                <div class='result-val-gain'>{dl.format_rupees(budget_res['savings_amount'])}</div>
                <div class='result-subtext'>SIPs, emergency fund, PPF</div>
            </div>
            """)

        # Segmented Split Bar
        bar_df = pd.DataFrame([{
            "Category": "Budget Split",
            "Needs": budget_res["needs_amount"],
            "Wants": budget_res["wants_amount"],
            "Savings": budget_res["savings_amount"]
        }])
        st.bar_chart(bar_df.set_index("Category"), horizontal=True, height=120)

        dl.render_html(f"""
        <div class='calc-callout-success'>
            💡 <b>Suggested Action</b>: Your monthly savings capacity is <b>{dl.format_rupees(budget_res['savings_amount'])}</b>.
            This amount has been automatically pre-filled into the <b>SIP Compounding</b> calculator (Tool 3).
        </div>
        """)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formula**:
        $$
        \text{Needs Amount} = \text{Monthly Income} \times \left(\frac{\text{Needs}\%}{100}\right)
        $$
        $$
        \text{Wants Amount} = \text{Monthly Income} \times \left(\frac{\text{Wants}\%}{100}\right)
        $$
        $$
        \text{Savings Amount} = \text{Monthly Income} \times \left(\frac{\text{Savings}\%}{100}\right)
        $$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Monthly Take-Home: {dl.format_rupees(monthly_take_home)}")
        st.write(f"- Needs: {dl.format_rupees(monthly_take_home)} × {needs_p:.2f}% = **{dl.format_rupees(budget_res['needs_amount'])}**")
        st.write(f"- Wants: {dl.format_rupees(monthly_take_home)} × {wants_p:.2f}% = **{dl.format_rupees(budget_res['wants_amount'])}**")
        st.write(f"- Savings: {dl.format_rupees(monthly_take_home)} × {savings_p:.2f}% = **{dl.format_rupees(budget_res['savings_amount'])}**")


# ==============================================================================
# TAB 2: EMI & Loan Amortization
# ==============================================================================
with tabs[1]:
    st.markdown("### EMI (Equated Monthly Installment)")
    st.caption("Calculate monthly debt servicing, total interest burden, and loan amortization over time.")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        loan_amount = st.number_input("Loan Amount (Rs)", min_value=0.0, value=5000000.0, step=100000.0, key="emi_loan")
    with col_e2:
        loan_rate = st.slider("Annual Interest Rate (%)", 1.0, 20.0, 8.50, 0.05, key="emi_rate")
    with col_e3:
        loan_tenure = st.slider("Loan Tenure (Years)", 1, 30, 20, 1, key="emi_tenure")

    emi_res = dl.calc_emi(loan_amount, loan_rate, loan_tenure)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Monthly EMI</div>
            <div class='result-val-highlight'>{dl.format_rupees(emi_res['emi'])}</div>
            <div class='result-subtext'>{loan_tenure * 12} monthly installments</div>
        </div>
        """)
    with m2:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Total Interest Payable</div>
            <div class='result-val'>{dl.format_rupees(emi_res['total_interest'])}</div>
            <div class='result-subtext'>{(emi_res['total_interest'] / loan_amount * 100.0) if loan_amount > 0 else 0:.1f}% of principal</div>
        </div>
        """)
    with m3:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Total Amount Paid</div>
            <div class='result-val'>{dl.format_rupees(emi_res['total_paid'])}</div>
            <div class='result-subtext'>Principal + Interest</div>
        </div>
        """)

    st.markdown("##### Outstanding Principal Balance Over Time")
    if not emi_res["schedule_df"].empty:
        chart_df = emi_res["schedule_df"][["Month", "Ending Balance"]].set_index("Month")
        st.line_chart(chart_df, use_container_width=True)

    st.markdown("##### First 12 Months Amortization Schedule")
    if not emi_res["first_12_months_df"].empty:
        t_html = "<table class='calc-table'><thead><tr><th>Month</th><th class='num-col'>Beginning Balance</th><th class='num-col'>EMI</th><th class='num-col'>Principal Paid</th><th class='num-col'>Interest Paid</th><th class='num-col'>Ending Balance</th></tr></thead><tbody>"
        for _, r in emi_res["first_12_months_df"].iterrows():
            t_html += f"<tr><td>Month {int(r['Month'])}</td><td class='num-col'>{dl.format_rupees(r['Beginning Balance'])}</td><td class='num-col'>{dl.format_rupees(r['EMI'])}</td><td class='num-col'>{dl.format_rupees(r['Principal Paid'])}</td><td class='num-col'>{dl.format_rupees(r['Interest Paid'])}</td><td class='num-col'>{dl.format_rupees(r['Ending Balance'])}</td></tr>"
        t_html += "</tbody></table>"
        dl.render_html(t_html)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formula** (from `docs/finance-formulas.md`):
        $$
        \text{EMI} = \frac{P \times i \times (1+i)^n}{(1+i)^n - 1}
        $$
        where:
        - $P$ = Loan principal amount
        - $r$ = Annual interest rate as a decimal
        - $i = \frac{r}{12}$ = Monthly interest rate
        - $n$ = Total duration in months ($Tenure \times 12$)
        - $\text{Total Paid} = \text{EMI} \times n$
        - $\text{Total Interest} = \text{Total Paid} - P$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Principal ($P$): {dl.format_rupees(loan_amount)}")
        st.write(f"- Annual Rate ($r$): {loan_rate:.2f}% $\\rightarrow$ Monthly rate ($i$): {loan_rate/100/12:.6f}")
        st.write(f"- Tenure ($n$): {loan_tenure} years $\\rightarrow$ {loan_tenure*12} months")
        st.write(f"- Monthly EMI = **{dl.format_rupees(emi_res['emi'])}**")
        st.write(f"- Total Paid = {dl.format_rupees(emi_res['emi'])} × {loan_tenure*12} = **{dl.format_rupees(emi_res['total_paid'])}**")
        st.write(f"- Total Interest = {dl.format_rupees(emi_res['total_paid'])} - {dl.format_rupees(loan_amount)} = **{dl.format_rupees(emi_res['total_interest'])}**")


# ==============================================================================
# TAB 3: SIP (Systematic Investment Plan)
# ==============================================================================
with tabs[2]:
    st.markdown("### SIP (Systematic Investment Plan)")
    st.caption("Model wealth creation through disciplined monthly rupee compounding invested at the start of each month.")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    default_sip_val = float(st.session_state.get("suggested_sip", 10000.0))
    if default_sip_val <= 0:
        default_sip_val = 10000.0
        
    with col_s1:
        sip_amount = st.number_input("Monthly SIP Amount (Rs)", min_value=100.0, value=default_sip_val, step=1000.0, key="sip_amount")
    with col_s2:
        sip_return = st.slider("Expected Annual Return (%)", 1.0, 30.0, 12.00, 0.25, key="sip_return")
    with col_s3:
        sip_tenure = st.slider("Investment Period (Years)", 1, 40, 15, 1, key="sip_tenure")

    sip_res = dl.calc_sip(sip_amount, sip_return, sip_tenure)
    
    s1, s2, s3 = st.columns(3)
    with s1:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Total Amount Invested</div>
            <div class='result-val'>{dl.format_rupees(sip_res['invested_amount'])}</div>
            <div class='result-subtext'>{sip_tenure * 12} monthly contributions</div>
        </div>
        """)
    with s2:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Estimated Final Value</div>
            <div class='result-val-highlight'>{dl.format_rupees(sip_res['final_value'])}</div>
            <div class='result-subtext'>Compounded at {sip_return:.2f}% p.a.</div>
        </div>
        """)
    with s3:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Estimated Wealth Gained</div>
            <div class='result-val-gain'>+{dl.format_rupees(sip_res['wealth_gained'])}</div>
            <div class='result-subtext'>{(sip_res['wealth_gained'] / sip_res['invested_amount'] * 100.0) if sip_res['invested_amount'] > 0 else 0:.1f}% net profit</div>
        </div>
        """)

    st.markdown("##### Portfolio Value Growth Over Time")
    chart_sip = sip_res["yearly_df"].set_index("Year")
    st.line_chart(chart_sip, use_container_width=True)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formula** (from `docs/finance-formulas.md`):
        $$
        \text{SIP Future Value} = A \times \left[\frac{(1+i)^n - 1}{i}\right] \times (1+i)
        $$
        where:
        - $A$ = Monthly investment amount (invested at start of each month)
        - $r$ = Annual return rate as decimal
        - $i = \frac{r}{12}$ = Monthly interest rate
        - $n$ = Number of monthly contributions ($\text{Years} \times 12$)
        - $\text{Wealth Gained} = \text{Future Value} - (A \times n)$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Monthly installment ($A$): {dl.format_rupees(sip_amount)}")
        st.write(f"- Monthly return ($i$): {sip_return:.2f}% / 12 = {sip_return/100/12:.6f}")
        st.write(f"- Installments ($n$): {sip_tenure} × 12 = {sip_tenure*12} months")
        st.write(f"- Total Invested = {dl.format_rupees(sip_amount)} × {sip_tenure*12} = **{dl.format_rupees(sip_res['invested_amount'])}**")
        st.write(f"- Final Value = **{dl.format_rupees(sip_res['final_value'])}**")
        st.write(f"- Wealth Gained = **{dl.format_rupees(sip_res['wealth_gained'])}**")


# ==============================================================================
# TAB 4: Step-up SIP
# ==============================================================================
with tabs[3]:
    st.markdown("### Step-up SIP (Top-up Systematic Investment Plan)")
    st.caption("Increase your SIP contribution each year in tandem with salary increments. Shown side by side with a plain SIP.")
    
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    with col_st1:
        step_base = st.number_input("Starting Monthly SIP (Rs)", min_value=100.0, value=10000.0, step=1000.0, key="step_base")
    with col_st2:
        step_ret = st.slider("Expected Annual Return (%)", 1.0, 30.0, 12.00, 0.25, key="step_ret")
    with col_st3:
        step_tenure = st.slider("Tenure (Years)", 1, 40, 15, 1, key="step_tenure")
    with col_st4:
        step_up_p = st.slider("Annual Step-up Rate (%)", 1.0, 25.0, 10.00, 1.0, key="step_up_p")

    step_res = dl.calc_step_up_sip(step_base, step_ret, step_tenure, step_up_p)
    plain_info = step_res["plain_sip"]

    col_side_left, col_side_right = st.columns(2, gap="large")
    with col_side_left:
        dl.render_html(f"""
        <div class='comparison-box'>
            <div class='comparison-title'>Plain SIP (Constant Amount)</div>
            <div style='margin-bottom: 0.75rem;'>
                <div class='result-label'>Total Invested</div>
                <div style='font-size: 1.35rem; font-weight: 700; color: #f8fafc;'>{dl.format_rupees(plain_info['invested_amount'])}</div>
            </div>
            <div style='margin-bottom: 0.75rem;'>
                <div class='result-label'>Final Value</div>
                <div style='font-size: 1.35rem; font-weight: 800; color: #38bdf8;'>{dl.format_rupees(plain_info['final_value'])}</div>
            </div>
            <div>
                <div class='result-label'>Wealth Gained</div>
                <div style='font-size: 1.35rem; font-weight: 700; color: #10b981;'>+{dl.format_rupees(plain_info['wealth_gained'])}</div>
            </div>
        </div>
        """)
        
    with col_side_right:
        dl.render_html(f"""
        <div class='comparison-box' style='border-color: rgba(56, 189, 248, 0.4);'>
            <div class='comparison-title' style='color: #38bdf8;'>Step-up SIP (+{step_up_p:.0f}% Annually)</div>
            <div style='margin-bottom: 0.75rem;'>
                <div class='result-label'>Total Invested</div>
                <div style='font-size: 1.35rem; font-weight: 700; color: #f8fafc;'>{dl.format_rupees(step_res['invested_amount'])}</div>
            </div>
            <div style='margin-bottom: 0.75rem;'>
                <div class='result-label'>Final Value</div>
                <div style='font-size: 1.35rem; font-weight: 800; color: #38bdf8;'>{dl.format_rupees(step_res['final_value'])}</div>
            </div>
            <div>
                <div class='result-label'>Wealth Gained</div>
                <div style='font-size: 1.35rem; font-weight: 700; color: #10b981;'>+{dl.format_rupees(step_res['wealth_gained'])}</div>
            </div>
        </div>
        """)

    dl.render_html(f"""
    <div class='calc-callout-success'>
        🚀 <b>Step-up Difference</b>: Stepping up your contributions by {step_up_p:.1f}% each year creates an extra 
        <b>{dl.format_rupees(step_res['diff_wealth'])}</b> in final wealth compared to a fixed SIP, on an additional investment of 
        {dl.format_rupees(step_res['diff_invested'])}.
    </div>
    """)

    st.markdown("##### Plain SIP vs Step-up SIP Wealth Progression")
    chart_step_df = step_res["yearly_df"][["Year", "Plain SIP Value", "Step-up SIP Value"]].set_index("Year")
    st.line_chart(chart_step_df, use_container_width=True)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formula** (from `docs/finance-formulas.md`):
        $$
        \text{Total FV} = \sum_{m=1}^{n} \left[ C_m \times (1+i)^{n - m + 1} \right]
        $$
        where:
        - $C_m = A \times (1+s)^{\lfloor (m-1)/12 \rfloor}$ is the installment amount in month $m$
        - $A$ = Initial monthly installment
        - $s$ = Annual step-up percentage as decimal
        - $i = \frac{r}{12}$ = Monthly compounding interest rate
        - Each month's deposit compounds until the end of month $n$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Base Monthly SIP ($A$): {dl.format_rupees(step_base)}")
        st.write(f"- Annual Step-up ($s$): {step_up_p:.2f}%")
        st.write(f"- Expected Return ($r$): {step_ret:.2f}% p.a. over {step_tenure} years")
        st.write(f"- Step-up SIP Final Value = **{dl.format_rupees(step_res['final_value'])}**")
        st.write(f"- Plain SIP Final Value = **{dl.format_rupees(plain_info['final_value'])}**")
        st.write(f"- Additional Wealth Created = **{dl.format_rupees(step_res['diff_wealth'])}**")


# ==============================================================================
# TAB 5: Lump Sum Investment
# ==============================================================================
with tabs[4]:
    st.markdown("### Lump Sum Investment")
    st.caption("Calculate compound growth for a single one-time capital deployment over a chosen time horizon.")
    
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        lump_p = st.number_input("One-Time Investment Amount (Rs)", min_value=100.0, value=500000.0, step=25000.0, key="lump_p")
    with col_l2:
        lump_r = st.slider("Expected Annual Return (%)", 1.0, 30.0, 12.00, 0.25, key="lump_r")
    with col_l3:
        lump_t = st.slider("Time Period (Years)", 1, 40, 10, 1, key="lump_t")

    lump_res = dl.calc_lump_sum(lump_p, lump_r, lump_t)

    lu1, lu2, lu3 = st.columns(3)
    with lu1:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Initial Principal</div>
            <div class='result-val'>{dl.format_rupees(lump_p)}</div>
            <div class='result-subtext'>Single upfront investment</div>
        </div>
        """)
    with lu2:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Final Value</div>
            <div class='result-val-highlight'>{dl.format_rupees(lump_res['final_value'])}</div>
            <div class='result-subtext'>Compounded over {lump_t} years</div>
        </div>
        """)
    with lu3:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Wealth Gained</div>
            <div class='result-val-gain'>+{dl.format_rupees(lump_res['wealth_gained'])}</div>
            <div class='result-subtext'>{(lump_res['wealth_gained'] / lump_p * 100.0) if lump_p > 0 else 0:.1f}% net return</div>
        </div>
        """)

    st.markdown("##### Year-by-Year Growth Table")
    if not lump_res["yearly_df"].empty:
        table_html = "<table class='calc-table'><thead><tr><th>Year</th><th class='num-col'>Beginning Value</th><th class='num-col'>Returns Earned</th><th class='num-col'>Ending Value</th></tr></thead><tbody>"
        for _, row in lump_res["yearly_df"].iterrows():
            table_html += f"<tr><td>Year {int(row['Year'])}</td><td class='num-col'>{dl.format_rupees(row['Beginning Value'])}</td><td class='num-col'>{dl.format_rupees(row['Returns Earned'])}</td><td class='num-col'>{dl.format_rupees(row['Ending Value'])}</td></tr>"
        table_html += "</tbody></table>"
        dl.render_html(table_html)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formula** (from `docs/finance-formulas.md`):
        $$
        \text{Lump Sum Future Value} = P \times (1 + r)^t
        $$
        where:
        - $P$ = Principal invested upfront
        - $r$ = Expected annual return rate as decimal
        - $t$ = Duration in years
        - $\text{Wealth Gained} = \text{Future Value} - P$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Principal ($P$): {dl.format_rupees(lump_p)}")
        st.write(f"- Annual return ($r$): {lump_r:.2f}% $\\rightarrow$ {lump_r/100:.4f}")
        st.write(f"- Period ($t$): {lump_t} years")
        st.write(f"- Final Value = {dl.format_rupees(lump_p)} × (1 + {lump_r/100:.4f})^{lump_t} = **{dl.format_rupees(lump_res['final_value'])}**")
        st.write(f"- Total Wealth Gained = **{dl.format_rupees(lump_res['wealth_gained'])}**")


# ==============================================================================
# TAB 6: Goal Planner
# ==============================================================================
with tabs[5]:
    st.markdown("### Goal Planner (Target Amount & Inflation Adjuster)")
    st.caption("Determine the monthly SIP required to reach a specific financial goal, accounting for the erosion of inflation.")
    
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        goal_target = st.number_input("Target Amount Today (Rs)", min_value=10000.0, value=5000000.0, step=100000.0, key="goal_target")
    with col_g2:
        goal_years = st.slider("Years to Goal", 1, 35, 10, 1, key="goal_years")
    with col_g3:
        goal_return = st.slider("Expected Return (%)", 1.0, 25.0, 12.00, 0.25, key="goal_return")
    with col_g4:
        goal_inflation = st.slider("Inflation Rate (%)", 0.0, 15.0, 6.00, 0.25, key="goal_inflation")

    goal_res = dl.calc_goal_planner(goal_target, goal_years, goal_return, goal_inflation)

    col_g_nom, col_g_real = st.columns(2, gap="large")
    with col_g_nom:
        dl.render_html(f"""
        <div class='comparison-box'>
            <div class='comparison-title'>Unadjusted Target (Ignoring Inflation)</div>
            <div style='margin-bottom: 0.75rem;'>
                <div class='result-label'>Target Amount</div>
                <div style='font-size: 1.45rem; font-weight: 700; color: #f8fafc;'>{dl.format_rupees(goal_target)}</div>
            </div>
            <div>
                <div class='result-label'>Monthly SIP Needed</div>
                <div style='font-size: 1.65rem; font-weight: 800; color: #38bdf8;'>{dl.format_rupees(goal_res['sip_without_inflation'])}</div>
                <div class='result-subtext'>At {goal_return:.2f}% p.a.</div>
            </div>
        </div>
        """)
        
    with col_g_real:
        dl.render_html(f"""
        <div class='comparison-box' style='border-color: rgba(244, 63, 94, 0.4);'>
            <div class='comparison-title' style='color: #fb7185;'>Real Target (With {goal_inflation:.2f}% Inflation)</div>
            <div style='margin-bottom: 0.75rem;'>
                <div class='result-label'>Inflated Cost at Year {goal_years}</div>
                <div style='font-size: 1.45rem; font-weight: 700; color: #f8fafc;'>{dl.format_rupees(goal_res['target_inflated'])}</div>
            </div>
            <div>
                <div class='result-label'>Realistic Monthly SIP Needed</div>
                <div style='font-size: 1.65rem; font-weight: 800; color: #f43f5e;'>{dl.format_rupees(goal_res['sip_with_inflation'])}</div>
                <div class='result-subtext'>To preserve purchasing power</div>
            </div>
        </div>
        """)

    dl.render_html(f"""
    <div class='calc-callout'>
        ⚠️ <b>Inflation Impact</b>: In {goal_years} years, what costs {dl.format_rupees(goal_target)} today will require 
        <b>{dl.format_rupees(goal_res['target_inflated'])}</b>. You will need an extra 
        <b>{dl.format_rupees(goal_res['diff_sip'])}</b> every month to hit your real target.
    </div>
    """)

    st.markdown("##### Goal Accumulation Trajectory")
    chart_goal_df = goal_res["yearly_df"].set_index("Year")
    st.line_chart(chart_goal_df, use_container_width=True)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formula** (from `docs/finance-formulas.md`):
        $$
        \text{Target}_{\text{inflated}} = \text{Target} \times (1 + \text{inflation})^t
        $$
        $$
        \text{Monthly SIP Needed} = \frac{\text{Target}}{\left[\frac{(1+i)^n - 1}{i}\right] \times (1+i)}
        $$
        where $i = \frac{r}{12}$ and $n = t \times 12$.
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Target today: {dl.format_rupees(goal_target)}")
        st.write(f"- Inflated Target at {goal_years} yrs ({goal_inflation:.2f}% inflation) = **{dl.format_rupees(goal_res['target_inflated'])}**")
        st.write(f"- SIP without inflation = **{dl.format_rupees(goal_res['sip_without_inflation'])} / month**")
        st.write(f"- Real SIP required with inflation = **{dl.format_rupees(goal_res['sip_with_inflation'])} / month**")


# ==============================================================================
# TAB 7: Inflation & Purchasing Power
# ==============================================================================
with tabs[6]:
    st.markdown("### Inflation & Purchasing Power")
    st.caption("See what goods will cost in the future, and what your liquid cash will actually be worth over time.")
    
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        inf_amount = st.number_input("Amount Today (Rs)", min_value=100.0, value=1000000.0, step=50000.0, key="inf_amount")
    with col_i2:
        inf_rate = st.slider("Annual Inflation Rate (%)", 1.0, 15.0, 6.00, 0.25, key="inf_rate")
    with col_i3:
        inf_tenure = st.slider("Time Horizon (Years)", 1, 40, 15, 1, key="inf_tenure")

    inf_res = dl.calc_inflation(inf_amount, inf_rate, inf_tenure)

    i1, i2 = st.columns(2)
    with i1:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>What it will cost then (Future Cost)</div>
            <div class='result-val' style='color: #f43f5e;'>{dl.format_rupees(inf_res['future_cost'])}</div>
            <div class='result-subtext'>To purchase goods costing {dl.format_rupees(inf_amount)} today</div>
        </div>
        """)
    with i2:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>What today's cash will be worth then (Purchasing Power)</div>
            <div class='result-val' style='color: #fbbf24;'>{dl.format_rupees(inf_res['purchasing_power'])}</div>
            <div class='result-subtext'>Purchasing power erosion of uninvested cash</div>
        </div>
        """)

    st.markdown("##### The Two Sides of Inflation")
    chart_inf_df = inf_res["yearly_df"].set_index("Year")
    st.line_chart(chart_inf_df, use_container_width=True)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formulas** (from `docs/finance-formulas.md`):
        $$
        \text{Future Cost} = P \times (1 + \text{inflation})^t
        $$
        $$
        \text{Inflation-Adjusted Real Value} = \frac{P}{(1 + \text{inflation})^t}
        $$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Initial Amount ($P$): {dl.format_rupees(inf_amount)}")
        st.write(f"- Annual Inflation: {inf_rate:.2f}% over {inf_tenure} years")
        st.write(f"- Future Cost = {dl.format_rupees(inf_amount)} × (1 + {inf_rate/100:.4f})^{inf_tenure} = **{dl.format_rupees(inf_res['future_cost'])}**")
        st.write(f"- Purchasing Power = {dl.format_rupees(inf_amount)} / (1 + {inf_rate/100:.4f})^{inf_tenure} = **{dl.format_rupees(inf_res['purchasing_power'])}**")


# ==============================================================================
# TAB 8: Retirement Corpus
# ==============================================================================
with tabs[7]:
    st.markdown("### Retirement Corpus & Independence Planner")
    st.caption("Calculate the exact nest egg required at retirement using the real-return growing annuity formula, plus the monthly SIP to achieve it.")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        current_age = st.slider("Current Age", 18, 65, 30, key="ret_cur_age")
        monthly_exp = st.number_input("Monthly Expenses Today (Rs)", min_value=1000.0, value=50000.0, step=5000.0, key="ret_exp")
    with col_r2:
        ret_age = st.slider("Planned Retirement Age", current_age + 1, 75, 60, key="ret_ret_age")
        inf_ret = st.slider("Expected Inflation Rate (%)", 2.0, 12.0, 6.00, 0.25, key="ret_inf")
    with col_r3:
        life_exp = st.slider("Life Expectancy Age", ret_age + 1, 100, 85, key="ret_life_exp")
        ret_pre = st.slider("Pre-Retirement Return (%)", 4.0, 20.0, 12.00, 0.25, key="ret_pre")
        ret_post = st.slider("Post-Retirement Return (%)", 2.0, 15.0, 8.00, 0.25, key="ret_post")

    ret_res = dl.calc_retirement_corpus(current_age, ret_age, life_exp, monthly_exp, inf_ret, ret_pre, ret_post)

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Monthly Expense at Retirement</div>
            <div class='result-val'>{dl.format_rupees(ret_res['monthly_expense_at_ret'])}</div>
            <div class='result-subtext'>At age {ret_age} ({ret_res['years_to_retirement']} yrs of inflation)</div>
        </div>
        """)
    with rc2:
        corpus_narrative = dl.format_rupees(ret_res['corpus_needed'], narrative=True)
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Target Retirement Corpus</div>
            <div class='result-val-highlight'>{corpus_narrative}</div>
            <div class='result-subtext'>{dl.format_rupees(ret_res['corpus_needed'])}</div>
        </div>
        """)
    with rc3:
        dl.render_html(f"""
        <div class='result-card'>
            <div class='result-label'>Monthly SIP Needed from Today</div>
            <div class='result-val-gain'>{dl.format_rupees(ret_res['monthly_sip_needed'])}</div>
            <div class='result-subtext'>Assuming {ret_pre:.2f}% annual equity return</div>
        </div>
        """)

    st.markdown("##### Wealth Accumulation & Decumulation Lifecycle")
    chart_ret_df = ret_res["projection_df"].set_index("Age")[["Corpus Balance"]]
    st.line_chart(chart_ret_df, use_container_width=True)

    with st.expander("How this is calculated"):
        st.markdown(r"""
        **Mathematical Formulas** (from `docs/finance-formulas.md`):
        $$
        \text{First Year Retirement Expense} = \text{Monthly Expense} \times (1 + \text{inflation})^t \times 12
        $$
        $$
        \text{Retirement Corpus} = \text{Annual Expense Year 1} \times \left[\frac{1 - (1+g)^{-N}}{g}\right]
        $$
        where:
        - $g = \frac{1 + \text{post-retirement return}}{1 + \text{inflation}} - 1$ = Real post-retirement rate of return
        - $t = \text{Retirement Age} - \text{Current Age}$ = Years to retirement
        - $N = \text{Life Expectancy} - \text{Retirement Age}$ = Years in retirement
        - $\text{Monthly SIP Needed} = \frac{\text{Corpus}}{\left[\frac{(1+i)^n - 1}{i}\right] \times (1+i)}$ with $i = \frac{\text{Pre-retirement return}}{12}$
        """)
        st.write(f"**Numbers plugged in**:")
        st.write(f"- Years to retirement ($t$): {ret_res['years_to_retirement']} years | Years in retirement ($N$): {ret_res['years_in_retirement']} years")
        st.write(f"- First year annual expense at age {ret_age}: **{dl.format_rupees(ret_res['annual_expense_first_year'])}**")
        st.write(f"- Real rate of return ($g$): (1 + {ret_post/100:.4f}) / (1 + {inf_ret/100:.4f}) - 1 = **{ret_res['real_return_g']*100:.2f}%**")
        st.write(f"- Required Corpus at age {ret_age} = **{dl.format_rupees(ret_res['corpus_needed'])}** ({corpus_narrative})")
        st.write(f"- Monthly SIP Needed from today = **{dl.format_rupees(ret_res['monthly_sip_needed'])}**")


# ==============================================================================
# TAB 9: Tax Regime Comparison (Budget 2025 / FY 2025-26)
# ==============================================================================
with tabs[8]:
    st.markdown("### Tax Regime Comparison (New vs Old Regime)")
    
    # Slabs info from CSV
    tax_temp = dl.calc_tax_comparison(1500000)
    st.caption(f"Accurately dynamically computes tax liability according to slab rates, deductions, 87A rebate, and 4% cess. **Financial Year: {tax_temp['fy_label']} (from data/tax-slabs.csv)**.")

    col_t1, col_t2 = st.columns([1, 1], gap="large")
    with col_t1:
        st.markdown("##### Income & Deductions Input")
        t_gross = st.number_input("Gross Annual Salary (Rs)", min_value=0.0, value=1500000.0, step=50000.0, key="tax_gross")
        t_80c = st.number_input("Section 80C Investments (PPF, ELSS, EPF, etc.) [Max Rs 1.5L]", min_value=0.0, max_value=150000.0, value=150000.0, step=10000.0, key="tax_80c")
        t_80d = st.number_input("Section 80D Health Insurance Premium (Rs)", min_value=0.0, value=25000.0, step=5000.0, key="tax_80d")
        t_hra = st.number_input("HRA Exemption Claimed (Rs)", min_value=0.0, value=120000.0, step=10000.0, key="tax_hra")
        t_home = st.number_input("Home Loan Interest u/s 24(b) (Rs) [Max Rs 2.0L]", min_value=0.0, max_value=200000.0, value=150000.0, step=10000.0, key="tax_home")

    tax_res = dl.calc_tax_comparison(t_gross, t_80c, t_80d, t_hra, t_home)
    old = tax_res["old_regime"]
    new = tax_res["new_regime"]

    with col_t2:
        # Verdict Callout
        if tax_res["better_regime"] == "New Regime":
            dl.render_html(f"""
            <div class='calc-callout-success'>
                🏆 <b>Recommendation: New Tax Regime is cheaper!</b><br>
                You save <b>{dl.format_rupees(tax_res['savings'])}</b> in taxes by opting for the New Regime.
            </div>
            """)
        elif tax_res["better_regime"] == "Old Regime":
            dl.render_html(f"""
            <div class='calc-callout-success'>
                🏆 <b>Recommendation: Old Tax Regime is cheaper!</b><br>
                You save <b>{dl.format_rupees(tax_res['savings'])}</b> in taxes by claiming your deductions under the Old Regime.
            </div>
            """)
        else:
            dl.render_html("""
            <div class='calc-callout'>
                ⚖️ <b>Both Tax Regimes yield identical tax liability.</b>
            </div>
            """)

        col_box_new, col_box_old = st.columns(2)
        with col_box_new:
            dl.render_html(f"""
            <div class='comparison-box' style='{"border-color: #10b981;" if tax_res["better_regime"]=="New Regime" else ""}'>
                <div class='comparison-title' style='color: #38bdf8;'>New Regime</div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Standard Deduction</div>
                    <div style='color: #f8fafc; font-weight: 600;'>{dl.format_rupees(new['standard_deduction'])}</div>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Taxable Income</div>
                    <div style='color: #f8fafc; font-weight: 600;'>{dl.format_rupees(new['taxable_income'])}</div>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Slab Tax</div>
                    <div style='color: #f8fafc;'>{dl.format_rupees(new['slab_tax'])}</div>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Rebate 87A</div>
                    <div style='color: #10b981;'>-{dl.format_rupees(new['rebate_87a'])}</div>
                </div>
                <div style='margin-bottom: 0.75rem;'>
                    <div class='result-label'>4% Cess</div>
                    <div style='color: #f8fafc;'>{dl.format_rupees(new['cess'])}</div>
                </div>
                <div style='border-top: 1px solid #1e293b; padding-top: 0.5rem;'>
                    <div class='result-label'>Total Tax Payable</div>
                    <div style='font-size: 1.45rem; font-weight: 800; color: #f8fafc;'>{dl.format_rupees(new['total_tax'])}</div>
                </div>
            </div>
            """)

        with col_box_old:
            dl.render_html(f"""
            <div class='comparison-box' style='{"border-color: #10b981;" if tax_res["better_regime"]=="Old Regime" else ""}'>
                <div class='comparison-title' style='color: #fbbf24;'>Old Regime</div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Total Deductions</div>
                    <div style='color: #f8fafc; font-weight: 600;'>{dl.format_rupees(old['total_deductions'])}</div>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Taxable Income</div>
                    <div style='color: #f8fafc; font-weight: 600;'>{dl.format_rupees(old['taxable_income'])}</div>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Slab Tax</div>
                    <div style='color: #f8fafc;'>{dl.format_rupees(old['slab_tax'])}</div>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <div class='result-label'>Rebate 87A</div>
                    <div style='color: #10b981;'>-{dl.format_rupees(old['rebate_87a'])}</div>
                </div>
                <div style='margin-bottom: 0.75rem;'>
                    <div class='result-label'>4% Cess</div>
                    <div style='color: #f8fafc;'>{dl.format_rupees(old['cess'])}</div>
                </div>
                <div style='border-top: 1px solid #1e293b; padding-top: 0.5rem;'>
                    <div class='result-label'>Total Tax Payable</div>
                    <div style='font-size: 1.45rem; font-weight: 800; color: #f8fafc;'>{dl.format_rupees(old['total_tax'])}</div>
                </div>
            </div>
            """)

    with st.expander("How this is calculated"):
        st.markdown(f"""
        **Tax Rules & Slabs Reference**:
        - Source file: `data/tax-slabs.csv` ({tax_res['fy_label']})
        - **New Regime**:
          - Standard deduction: **Rs 75,000.00**
          - Slabs: 0-4L (0%), 4-8L (5%), 8-12L (10%), 12-16L (15%), 16-20L (20%), 20-24L (25%), Above 24L (30%).
          - Rebate u/s 87A: If taxable income $\\le$ Rs 12,00,000, full tax rebate is applied making tax nil.
        - **Old Regime**:
          - Standard deduction: **Rs 50,000.00**
          - Allowed deductions claimed: 80C ({dl.format_rupees(t_80c)}), 80D ({dl.format_rupees(t_80d)}), HRA ({dl.format_rupees(t_hra)}), Home Loan Interest ({dl.format_rupees(t_home)}).
          - Slabs: 0-2.5L (0%), 2.5-5L (5%), 5-10L (20%), Above 10L (30%).
          - Rebate u/s 87A: If taxable income $\\le$ Rs 5,00,000, rebate up to Rs 12,500 is applied.
        - **Health & Education Cess**: Strictly 4% added to net tax payable under both regimes.
        """)
        st.write(f"**Step-by-Step Numbers**:")
        st.write(f"- Gross Salary: {dl.format_rupees(t_gross)}")
        st.write(f"- New Regime Taxable = {dl.format_rupees(t_gross)} - Rs 75,000 = **{dl.format_rupees(new['taxable_income'])}** $\\rightarrow$ Final Tax = **{dl.format_rupees(new['total_tax'])}**")
        st.write(f"- Old Regime Taxable = {dl.format_rupees(t_gross)} - {dl.format_rupees(old['total_deductions'])} = **{dl.format_rupees(old['taxable_income'])}** $\\rightarrow$ Final Tax = **{dl.format_rupees(old['total_tax'])}**")
        st.write(f"- Net Difference: **{dl.format_rupees(tax_res['savings'])}** in favor of {tax_res['better_regime']}")


# ==============================================================================
# Mandatory House Style Disclaimer Footer (Rule 7)
# ==============================================================================
dl.render_footer()
