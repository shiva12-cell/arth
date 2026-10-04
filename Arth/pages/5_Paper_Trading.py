"""
pages/5_Paper_Trading.py - Paper Trading Module for Arth
Module 4 of 5: Virtual Equity Simulator, Transparent Order Cost Modeling, Portfolio Accounting & Reconciliation, and Benchmark Comparison vs Nifty 50.
Follows AGENTS.md, docs/house-style.md, and docs/finance-formulas.md.
"""

import streamlit as st
import pandas as pd
import datetime
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Paper Trading — Arth",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Fintech Aesthetic matching Modules 1-3)
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
    
    /* Top Account Bar */
    .account-bar {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }
    .market-pill-open {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .market-pill-closed {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b !important;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
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
    
    /* Order Preview Box */
    .order-preview-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.15rem;
        margin: 1rem 0;
    }
    .order-preview-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
    .order-preview-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.4rem;
        font-size: 0.92rem;
        color: #cbd5e1;
    }
    .order-preview-net {
        display: flex;
        justify-content: space-between;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid #334155;
        font-size: 1.05rem;
        font-weight: 800;
        color: #f8fafc;
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
        margin-bottom: 0.5rem;
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

# Ensure Database is Initialized
dl.init_paper_trading_db()

# Page Title & Header
dl.render_html("""
<div class='page-title'>
    Paper Trading
    <span class='page-title-badge'>Module 4</span>
</div>
<div class='page-desc'>
    Simulate equity trading on the National Stock Exchange without real money. Executions are simulated against the latest market prices (delayed about 15 minutes), with transparent transaction costs and automated portfolio accounting.
</div>
""")

# Market Status Check
is_market_open, market_note, now_ist = dl.is_nse_market_open()
market_pill = f"<span class='market-pill-open'>🟢 Market Open (9:15 – 15:30 IST)</span>" if is_market_open else f"<span class='market-pill-closed'>🟡 Market Closed — Orders filled at last close</span>"

# Account Details & Metrics
acct = dl.get_paper_account()
summary = dl.get_paper_holdings_summary()

# Top Account Banner & Reset Action
top_c1, top_c2 = st.columns([3, 1])
with top_c1:
    dl.render_html(f"""
    <div style='display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;'>
        <div style='font-size: 1.25rem; font-weight: 800; color: #f8fafc;'>
            Trader Account: <span style='color: #38bdf8;'>{acct['display_name']}</span>
        </div>
        <div>{market_pill}</div>
    </div>
    """)
with top_c2:
    with st.popover("⚙️ Account Options"):
        new_name_val = st.text_input("Change Display Name", value=acct["display_name"])
        if st.button("Save Name", key="btn_save_name"):
            if new_name_val.strip():
                dl.set_paper_account_name(new_name_val)
                st.success("Name updated successfully.")
                st.rerun()
                
        st.write("---")
        st.write("⚠️ **Reset Account**")
        st.caption("Clears all holdings, wipes the trade history, and resets virtual cash to Rs 10,00,000.00.")
        confirm_reset = st.checkbox("Yes, confirm reset", key="chk_confirm_reset")
        if st.button("Reset Everything to Rs 10 Lakh", type="primary", disabled=not confirm_reset):
            dl.reset_paper_account()
            st.success("Account reset successfully. Your cash balance is restored to Rs 10,00,000.00.")
            st.rerun()

# Four Hero Metrics (Cash, Holdings Value, Account Value, Overall Return)
m1, m2, m3, m4 = st.columns(4)
with m1:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Available Cash</div>
        <div class='result-val'>{dl.format_rupees(summary['cash_balance'])}</div>
        <div class='result-subtext'>Unallocated liquid capital</div>
    </div>
    """)
with m2:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Holdings Valuation</div>
        <div class='result-val'>{dl.format_rupees(summary['total_current_value'])}</div>
        <div class='result-subtext'>Invested: {dl.format_rupees(summary['total_invested'])}</div>
    </div>
    """)
with m3:
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Total Account Value</div>
        <div class='result-val-highlight'>{dl.format_rupees(summary['total_account_value'])}</div>
        <div class='result-subtext'>Cash + Holdings Market Value</div>
    </div>
    """)
with m4:
    ret_pct = summary["overall_return_pct"]
    val_cls = "result-val-gain" if ret_pct >= 0 else "result-val-danger"
    arrow = "▲ " if ret_pct >= 0 else "▼ "
    sign = "+" if ret_pct >= 0 else ""
    net_pnl = summary["total_account_value"] - 1000000.0
    dl.render_html(f"""
    <div class='result-card'>
        <div class='result-label'>Overall Return</div>
        <div class='{val_cls}'>{arrow}{sign}{dl.format_percentage(ret_pct)}</div>
        <div class='result-subtext'>{sign}{dl.format_rupees(net_pnl)} on Rs 10 lakh</div>
    </div>
    """)


# ==============================================================================
# MAIN TABS: 1. Trading Desk, 2. Holdings, 3. Trade Log, 4. Versus Nifty 50
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🖥️ Trading Desk",
    "💼 Holdings & Valuation",
    "📜 Trade Log & Audit",
    "📊 Versus Nifty 50"
])


# ==============================================================================
# TAB 1: Trading Desk
# ==============================================================================
with tab1:
    st.subheader("Order Execution Desk")
    st.caption("Place buy or sell orders at the latest market price with full cost transparency.")
    
    # Load Nifty 50 symbols for quick picker
    nifty_df = dl.get_nifty50_symbols()
    
    desk_c1, desk_c2 = st.columns([1.1, 1.2], gap="large")
    
    with desk_c1:
        st.write("##### 1. Select Asset")
        
        # Check if pre-selected via Watchlist Trade button
        preselected_ticker = st.session_state.get("trade_ticker", "INFY.NS")
        
        asset_mode = st.radio("Asset Selection Mode", ["Pick from Nifty 50", "Type NSE Ticker"], horizontal=True)
        
        if asset_mode == "Pick from Nifty 50":
            nifty_options = {f"{r['company']} ({r['symbol']})": (r['yahoo_ticker'], r['company']) for _, r in nifty_df.iterrows()}
            
            # Find default index
            default_idx = 0
            for idx, (lbl, (t_sym, _)) in enumerate(nifty_options.items()):
                if t_sym == preselected_ticker:
                    default_idx = idx
                    break
                    
            selected_desk_label = st.selectbox("Choose Company", list(nifty_options.keys()), index=default_idx)
            chosen_ticker, chosen_company = nifty_options[selected_desk_label]
        else:
            custom_sym_input = st.text_input("Enter NSE Symbol (e.g. INFY, TCS, RELIANCE)", value="INFY")
            clean_s = custom_sym_input.strip().upper()
            chosen_ticker = clean_s if clean_s.endswith(".NS") or clean_s.startswith("^") else f"{clean_s}.NS"
            chosen_company = dl.get_ticker_company_name(chosen_ticker)
            
        # Fetch Live Quote for the chosen asset
        quote_data, is_q_offline, q_source = dl.get_latest_price(chosen_ticker)
        
        if not quote_data or quote_data.get("price") is None:
            st.error("That ticker was not found on Yahoo Finance. Please check the symbol and try again.")
            st.stop()
            
        last_price = float(quote_data["price"])
        day_chg = float(quote_data["change"]) if quote_data.get("change") is not None else 0.0
        day_pct = float(quote_data["pct_change"]) if quote_data.get("pct_change") is not None else 0.0
        
        # Display Quote Tile
        is_pos = day_chg >= 0
        col_c = "#10b981" if is_pos else "#f43f5e"
        arrow = "▲ " if is_pos else "▼ "
        sign = "+" if is_pos else ""
        
        dl.render_html(f"""
        <div style='background-color: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 1rem; margin-top: 0.5rem;'>
            <div style='font-size: 1.15rem; font-weight: 800; color: #f8fafc;'>{chosen_company}</div>
            <div style='font-size: 0.85rem; color: #94a3b8; font-weight: 600;'>{chosen_ticker}</div>
            <div style='display: flex; align-items: baseline; gap: 0.75rem; margin-top: 0.5rem;'>
                <span style='font-size: 1.7rem; font-weight: 800; color: #38bdf8;'>{dl.format_rupees(last_price)}</span>
                <span style='font-size: 1rem; font-weight: 700; color: {col_c};'>{arrow}{sign}{dl.format_rupees(day_chg)} ({sign}{dl.format_percentage(day_pct)})</span>
            </div>
            <div class='source-timestamp'>{q_source}</div>
        </div>
        """)
        
        # 6-Month Chart
        st.write("##### 6-Month Historical Price Chart")
        hist_df, _, _, _ = dl.get_daily_history(chosen_ticker, "6mo")
        if hist_df is not None and not hist_df.empty:
            chart_hist = hist_df.copy()
            st.line_chart(chart_hist["Close"], use_container_width=True)
        else:
            st.caption("Historical chart unavailable for this symbol.")

    with desk_c2:
        st.write("##### 2. Order Specification")
        
        # Check user's current holding for this ticker
        current_holding = next((h for h in summary["holdings"] if h["ticker"] == chosen_ticker), None)
        held_qty = current_holding["quantity"] if current_holding else 0
        held_avg = current_holding["avg_buy_price"] if current_holding else 0.0
        
        if held_qty > 0:
            st.info(f"You currently hold **{held_qty} shares** of {chosen_company} at an average price of **{dl.format_rupees(held_avg)}**.")
        else:
            st.caption(f"You do not hold any shares of {chosen_company}.")
            
        trade_action = st.radio("Action", ["BUY", "SELL"], horizontal=True)
        
        order_qty = st.number_input(
            "Quantity (Number of Shares)",
            min_value=1,
            max_value=1000000,
            value=10,
            step=1,
            format="%d"
        )
        
        # Cost Calculations
        costs = dl.calc_trade_costs(last_price, order_qty)
        t_val = costs["trade_value"]
        brok = costs["brokerage"]
        stt_val = costs["stt"]
        tot_costs = costs["total_costs"]
        
        if trade_action == "BUY":
            net_cash_impact = -(t_val + tot_costs)
            net_label = "Cash Required (Debit)"
        else:
            net_cash_impact = t_val - tot_costs
            net_label = "Cash Proceeds (Credit)"
            
        # Order Preview Card
        dl.render_html(f"""
        <div class='order-preview-card'>
            <div class='order-preview-title'>Order Cost & Cash Preview ({trade_action})</div>
            <div class='order-preview-row'>
                <span>Execution Price:</span>
                <span style='font-weight: 700;'>{dl.format_rupees(last_price)}</span>
            </div>
            <div class='order-preview-row'>
                <span>Quantity:</span>
                <span style='font-weight: 700;'>{order_qty:,} shares</span>
            </div>
            <div class='order-preview-row'>
                <span>Gross Trade Value:</span>
                <span style='font-weight: 700;'>{dl.format_rupees(t_val)}</span>
            </div>
            <div class='order-preview-row'>
                <span>Brokerage (Rs 20 or 0.03%, whichever is lower):</span>
                <span style='color: #94a3b8;'>{dl.format_rupees(brok)}</span>
            </div>
            <div class='order-preview-row'>
                <span>Securities Transaction Tax (STT 0.1%):</span>
                <span style='color: #94a3b8;'>{dl.format_rupees(stt_val)}</span>
            </div>
            <div class='order-preview-row' style='font-weight: 600;'>
                <span>Total Transaction Costs:</span>
                <span style='color: #f43f5e;'>{dl.format_rupees(tot_costs)}</span>
            </div>
            <div class='order-preview-net'>
                <span>{net_label}:</span>
                <span style='color: #38bdf8;'>{dl.format_rupees(abs(net_cash_impact))}</span>
            </div>
        </div>
        """)
        
        # Timing Note
        if not is_market_open:
            st.warning("market closed - filled at last close")
            
        # Educational Cost Note (Formulas Requirement)
        st.caption("Ignoring exchange transaction charges, SEBI turnover fees, stamp duty, and GST for simplicity.")
        
        # Confirm Button
        btn_label = f"Confirm {trade_action} Order ({dl.format_rupees(abs(net_cash_impact))})"
        if st.button(btn_label, type="primary", use_container_width=True):
            success, msg, _ = dl.execute_paper_trade(
                ticker=chosen_ticker,
                company_name=chosen_company,
                trade_type=trade_action,
                quantity=order_qty,
                price=last_price
            )
            if success:
                st.success(msg)
                # Clear session state trade ticker
                if "trade_ticker" in st.session_state:
                    del st.session_state["trade_ticker"]
                st.rerun()
            else:
                st.error(msg)


# ==============================================================================
# TAB 2: Holdings & Portfolio Valuation
# ==============================================================================
with tab2:
    st.subheader("Holdings & Portfolio Accounting")
    st.caption("Inspect open positions, average buy prices, unrealised market profit or loss, and the mathematical accounting reconciliation.")
    
    holdings = summary["holdings"]
    
    if holdings:
        h_table_rows = []
        for h in holdings:
            pnl_amt = h["unrealised_pnl"]
            pnl_pct = h["unrealised_pnl_pct"]
            sign = "+" if pnl_amt >= 0 else ""
            
            h_table_rows.append({
                "Company": h["company_name"],
                "Symbol": h["ticker"],
                "Quantity": f"{h['quantity']:,}",
                "Avg Buy Price": dl.format_rupees(h["avg_buy_price"]),
                "Last Price": dl.format_rupees(h["last_price"]),
                "Invested Value": dl.format_rupees(h["invested_value"]),
                "Current Value": dl.format_rupees(h["current_value"]),
                "Profit or loss": f"{sign}{dl.format_rupees(pnl_amt)} ({sign}{dl.format_percentage(pnl_pct)})"
            })
            
        st.dataframe(pd.DataFrame(h_table_rows), use_container_width=True, hide_index=True)
        
        # Portfolio Summary Strip
        tot_c1, tot_c2, tot_c3 = st.columns(3)
        with tot_c1:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Total Capital Invested</div>
                <div class='result-val'>{dl.format_rupees(summary['total_invested'])}</div>
                <div class='result-subtext'>Across {len(holdings)} positions</div>
            </div>
            """)
        with tot_c2:
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Current Holdings Value</div>
                <div class='result-val-highlight'>{dl.format_rupees(summary['total_current_value'])}</div>
                <div class='result-subtext'>At delayed market prices</div>
            </div>
            """)
        with tot_c3:
            u_pnl = summary["total_unrealised_pnl"]
            u_pct = (u_pnl / summary["total_invested"] * 100.0) if summary["total_invested"] > 0 else 0.0
            u_cls = "result-val-gain" if u_pnl >= 0 else "result-val-danger"
            arrow = "▲ " if u_pnl >= 0 else "▼ "
            sign = "+" if u_pnl >= 0 else ""
            dl.render_html(f"""
            <div class='result-card'>
                <div class='result-label'>Total Unrealised P&L</div>
                <div class='{u_cls}'>{arrow}{sign}{dl.format_rupees(u_pnl)}</div>
                <div class='result-subtext'>{sign}{dl.format_percentage(u_pct)} on invested capital</div>
            </div>
            """)
    else:
        st.info("You currently hold no open stock positions. Head over to the Trading Desk tab to make your first trade.")
        
    # Non-Negotiable Arithmetic Reconciliation Box
    st.write("---")
    st.write("#### Arithmetic Portfolio Reconciliation")
    st.caption("Strict mathematical check ensuring your account balance agrees with every rupee of realised gains, unrealised valuation, and trading fees.")
    
    rec = dl.get_paper_reconciliation()
    
    rec_c1, rec_c2 = st.columns(2)
    with rec_c1:
        dl.render_html(f"""
        <div style='background-color: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 1.15rem;'>
            <div style='font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;'>
                Balance Sheet Method
            </div>
            <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.35rem;'>
                Cash Balance: <strong>{dl.format_rupees(rec['cash_balance'])}</strong>
            </div>
            <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.35rem;'>
                + Holdings Value: <strong>{dl.format_rupees(rec['current_value'])}</strong>
            </div>
            <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.35rem;'>
                − Starting Capital: <strong>{dl.format_rupees(rec['starting_cash'])}</strong>
            </div>
            <hr style='border: none; border-top: 1px solid #334155; margin: 0.5rem 0;'>
            <div style='font-size: 1.15rem; font-weight: 800; color: #f8fafc;'>
                Net Change: {dl.format_rupees(rec['net_profit'])}
            </div>
        </div>
        """)
        
    with rec_c2:
        dl.render_html(f"""
        <div style='background-color: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 1.15rem;'>
            <div style='font-size: 0.85rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;'>
                P&L Accounting Method
            </div>
            <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.35rem;'>
                Realised Profit / Loss: <strong>{dl.format_rupees(rec['total_realised_pnl'])}</strong>
            </div>
            <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.35rem;'>
                + Unrealised Profit / Loss: <strong>{dl.format_rupees(rec['total_unrealised_pnl'])}</strong>
            </div>
            <div style='font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.35rem;'>
                − Total Costs (Brokerage + STT): <strong>{dl.format_rupees(rec['total_costs'])}</strong>
            </div>
            <hr style='border: none; border-top: 1px solid #334155; margin: 0.5rem 0;'>
            <div style='font-size: 1.15rem; font-weight: 800; color: #f8fafc;'>
                Reconciled Sum: {dl.format_rupees(rec['reconciled_sum'])}
            </div>
        </div>
        """)
        
    if rec["is_balanced"]:
        dl.render_html(f"""
        <div style='background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 0.75rem 1rem; margin-top: 1rem; color: #a7f3d0; font-size: 0.92rem; font-weight: 600;'>
            ✅ <strong>Account Fully Reconciled:</strong> Balance Sheet method agrees exactly with the P&L accounting equation to the rupee (Discrepancy: {dl.format_rupees(rec['difference'])}).
        </div>
        """)
    else:
        st.error(f"Reconciliation discrepancy detected: {dl.format_rupees(rec['difference'])}.")


# ==============================================================================
# TAB 3: Trade Log & Audit Trail
# ==============================================================================
with tab3:
    st.subheader("Trade Audit Trail & Ledger")
    st.caption("Immutable record of every buy and sell order executed in your account, including complete fee breakdowns and realised profit or loss.")
    
    trades_df = dl.get_paper_trade_log()
    
    if not trades_df.empty:
        # Download Button
        csv_data = trades_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Trade Log to CSV",
            data=csv_data,
            file_name=f"arth_paper_trade_log_{datetime.date.today().isoformat()}.csv",
            mime="text/csv",
            type="secondary"
        )
        
        # Display formatted trade log table
        log_view = trades_df.copy()
        log_view["Date & Time"] = log_view["timestamp"].apply(lambda t: dl.format_timestamp(pd.to_datetime(t)))
        log_view["Action"] = log_view["trade_type"]
        log_view["Asset"] = log_view["company_name"] + " (" + log_view["ticker"] + ")"
        log_view["Quantity"] = log_view["quantity"].apply(lambda q: f"{q:,}")
        log_view["Price"] = log_view["price"].apply(lambda p: dl.format_rupees(p))
        log_view["Value"] = log_view["trade_value"].apply(lambda v: dl.format_rupees(v))
        log_view["Brokerage"] = log_view["brokerage"].apply(lambda b: dl.format_rupees(b))
        log_view["STT"] = log_view["stt"].apply(lambda s: dl.format_rupees(s))
        log_view["Total Costs"] = log_view["total_costs"].apply(lambda c: dl.format_rupees(c))
        log_view["Net Cash Effect"] = log_view["net_cash_flow"].apply(lambda n: dl.format_rupees(n))
        log_view["Realised P&L"] = log_view.apply(lambda r: dl.format_rupees(r["realised_pnl"]) if r["trade_type"] == "SELL" else "—", axis=1)
        log_view["Execution Note"] = log_view["market_status_note"]
        
        show_cols = [
            "Date & Time", "Action", "Asset", "Quantity", "Price", "Value",
            "Brokerage", "STT", "Total Costs", "Net Cash Effect", "Realised P&L", "Execution Note"
        ]
        
        st.dataframe(log_view[show_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No trades have been recorded yet. Use the Trading Desk tab to execute your first order.")


# ==============================================================================
# TAB 4: Versus Nifty 50 Benchmark
# ==============================================================================
with tab4:
    st.subheader("Performance Versus Nifty 50 Index")
    st.caption("Compare your active portfolio account value since your first trade against an identical Rs 10,00,000 lump sum invested in the Nifty 50 (^NSEI) on the same starting date.")
    
    vs_data = dl.get_paper_vs_nifty()
    
    if vs_data.get("has_trades"):
        f_date = vs_data["first_trade_date"]
        port_val = vs_data["current_acct_val"]
        nifty_val = vs_data["current_nifty_val"]
        ahead_amt = vs_data["ahead_amount"]
        is_ahead = vs_data["is_portfolio_ahead"]
        
        # State which is ahead and by how many rupees!
        if is_ahead:
            dl.render_html(f"""
            <div style='background-color: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem;'>
                <div style='font-size: 1.2rem; font-weight: 800; color: #34d399;'>
                    🏆 Your portfolio is ahead of Nifty 50 by {dl.format_rupees(ahead_amt)}!
                </div>
                <div style='font-size: 0.9rem; color: #cbd5e1; margin-top: 0.35rem;'>
                    Since your first trade on <strong>{dl.format_date(f_date)}</strong>, your total portfolio value has reached <strong>{dl.format_rupees(port_val)}</strong> compared to <strong>{dl.format_rupees(nifty_val)}</strong> for the Nifty 50 benchmark.
                </div>
            </div>
            """)
        else:
            dl.render_html(f"""
            <div style='background-color: rgba(244, 63, 94, 0.12); border: 1px solid rgba(244, 63, 94, 0.35); border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem;'>
                <div style='font-size: 1.2rem; font-weight: 800; color: #fb7185;'>
                    📉 Nifty 50 is ahead of your portfolio by {dl.format_rupees(ahead_amt)}.
                </div>
                <div style='font-size: 0.9rem; color: #cbd5e1; margin-top: 0.35rem;'>
                    Since your first trade on <strong>{dl.format_date(f_date)}</strong>, Nifty 50 benchmark value has reached <strong>{dl.format_rupees(nifty_val)}</strong> compared to <strong>{dl.format_rupees(port_val)}</strong> for your active portfolio.
                </div>
            </div>
            """)
            
        chart_vs = vs_data.get("chart_df", pd.DataFrame())
        if not chart_vs.empty:
            st.write("#### Total Account Value vs Nifty 50 Benchmark")
            st.line_chart(chart_vs, use_container_width=True)
            st.caption(f"Chart tracks daily valuation since inception date {dl.format_date(f_date)}. Both portfolios initiated with Rs 10,00,000.00 capital.")
    else:
        st.info("No trades executed yet. Complete at least one paper trade to activate your benchmark tracking versus the Nifty 50.")


# Mandatory Educational Disclosure (Rule 7)
dl.render_html("""
<div class='footer-disclaimer'>
    Arth is a learning platform. Nothing here is investment advice.
</div>
""")
