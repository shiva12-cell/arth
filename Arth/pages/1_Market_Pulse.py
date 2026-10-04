"""
pages/1_Market_Pulse.py - Market Pulse Module for Arth
Module 1: Market Intelligence, Benchmark Indices, Sector Heat Strip, Charts & Watchlist
Designed with professional financial dark-mode color theory and high accessibility contrast.
"""

import streamlit as st
import pandas as pd
import datetime
import data_layer as dl

# Page Configuration
st.set_page_config(
    page_title="Market Pulse — Arth",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Professional Fintech Dark Palette (TradingView / Bloomberg / Zerodha inspired)
st.markdown("""
<style>
    /* Global Container */
    .main .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Header typography - Crisp and high contrast */
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
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.45rem;
        font-weight: 700;
        color: #f8fafc !important;
        margin-top: 2.25rem;
        margin-bottom: 0.85rem;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-header-bar {
        width: 4px;
        height: 1.25rem;
        background-color: #38bdf8;
        border-radius: 2px;
        display: inline-block;
    }
    
    /* Benchmark Metric Cards */
    .metric-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.35rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.12);
    }
    
    .metric-name {
        font-size: 0.82rem;
        font-weight: 700;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.45rem;
    }
    .metric-val {
        font-size: 1.85rem;
        font-weight: 800;
        color: #f8fafc !important;
        margin-bottom: 0.45rem;
        letter-spacing: -0.02em;
    }
    
    /* Financial indicator colors */
    .metric-change-pos {
        font-size: 0.95rem;
        font-weight: 700;
        color: #10b981 !important;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }
    .metric-change-neg {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f43f5e !important;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }
    .metric-change-neutral {
        font-size: 0.95rem;
        font-weight: 600;
        color: #94a3b8 !important;
    }
    
    /* Timestamp / Source badge */
    .source-timestamp {
        font-size: 0.86rem;
        color: #64748b !important;
        margin-top: 0.35rem;
        margin-bottom: 1.75rem;
        font-style: italic;
    }
    .offline-badge {
        display: inline-block;
        background-color: rgba(244, 63, 94, 0.15);
        color: #fb7185 !important;
        font-weight: 700;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        border: 1px solid rgba(244, 63, 94, 0.35);
        font-style: normal;
    }
    
    /* Financial Tables */
    .fin-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .fin-table th {
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
    .fin-table th.num-col {
        text-align: right;
    }
    .fin-table td {
        padding: 0.85rem 1rem;
        font-size: 0.92rem;
        color: #f8fafc !important;
        border-bottom: 1px solid #1a2438;
    }
    .fin-table td.num-col {
        text-align: right;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .fin-table tr:last-child td {
        border-bottom: none;
    }
    .fin-table tr:hover td {
        background-color: #182239;
    }
    .sector-subtext {
        color: #64748b !important;
        font-size: 0.8rem;
        display: block;
        margin-top: 0.1rem;
    }
    
    /* Table badges */
    .table-badge-pos {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-weight: 700;
    }
    .table-badge-neg {
        display: inline-block;
        background-color: rgba(244, 63, 94, 0.15);
        color: #fb7185 !important;
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        font-weight: 700;
    }
    
    /* Sector Chips */
    .sector-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 0.85rem;
        border-radius: 8px;
        font-size: 0.86rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .sector-chip:hover {
        transform: translateY(-1px);
    }
    .chip-pos {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34d399 !important;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .chip-neg {
        background-color: rgba(244, 63, 94, 0.12);
        color: #fb7185 !important;
        border: 1px solid rgba(244, 63, 94, 0.35);
    }
    .chip-neutral {
        background-color: #1e293b;
        color: #94a3b8 !important;
        border: 1px solid #334155;
    }
    
    /* Chart Summary Stats Box */
    .chart-stat-box {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chart-stat-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .chart-stat-val {
        font-size: 1.45rem;
        font-weight: 700;
        color: #f8fafc !important;
    }
    
    /* Watchlist Asset Card */
    .wl-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .wl-card:hover {
        border-color: #38bdf8;
        transform: translateY(-1px);
    }
    .wl-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc !important;
    }
    .wl-ticker {
        font-size: 0.8rem;
        color: #64748b !important;
        font-family: monospace;
    }
    .wl-price {
        font-size: 1.25rem;
        font-weight: 800;
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
dl.render_html("""
<div class='page-title'>
    Market Pulse
    <span class='page-title-badge'>Module 1</span>
</div>
<div class='page-desc'>
    Live benchmark indices, currency exchange, precious metals, constituent market breadth, and sector momentum.
</div>
""")


# ==============================================================================
# SECTION 1: Key Benchmark Tiles
# ==============================================================================

INDEX_TICKERS = ["^NSEI", "^BSESN", "^NSEBANK", "INR=X", "GC=F"]
index_quotes, indices_offline, index_source = dl.get_batch_quotes(INDEX_TICKERS)

def render_metric_tile(title, price_str, change_str, pct_str, is_pos, is_neg):
    change_class = "metric-change-pos" if is_pos else ("metric-change-neg" if is_neg else "metric-change-neutral")
    symbol_sign = "+" if is_pos else ""
    arrow = "▲ " if is_pos else ("▼ " if is_neg else "")
    dl.render_html(f"""
    <div class='metric-card'>
        <div class='metric-name'>{title}</div>
        <div class='metric-val'>{price_str}</div>
        <div class='{change_class}'>{arrow}{symbol_sign}{change_str} ({symbol_sign}{pct_str})</div>
    </div>
    """)

col1, col2, col3 = st.columns(3)

# 1. Nifty 50
nifty = index_quotes.get("^NSEI")
with col1:
    if nifty and nifty.get("price") is not None:
        p = dl.format_number(nifty["price"], decimals=2)
        chg = dl.format_number(nifty["change"], decimals=2)
        pct = dl.format_percentage(nifty["pct_change"])
        render_metric_tile("Nifty 50", p, chg, pct, nifty["change"] > 0, nifty["change"] < 0)
    else:
        render_metric_tile("Nifty 50", "N/A", "0.00", "0.00%", False, False)

# 2. Sensex
sensex = index_quotes.get("^BSESN")
with col2:
    if sensex and sensex.get("price") is not None:
        p = dl.format_number(sensex["price"], decimals=2)
        chg = dl.format_number(sensex["change"], decimals=2)
        pct = dl.format_percentage(sensex["pct_change"])
        render_metric_tile("Sensex", p, chg, pct, sensex["change"] > 0, sensex["change"] < 0)
    else:
        render_metric_tile("Sensex", "N/A", "0.00", "0.00%", False, False)

# 3. Bank Nifty
banknifty = index_quotes.get("^NSEBANK")
with col3:
    if banknifty and banknifty.get("price") is not None:
        p = dl.format_number(banknifty["price"], decimals=2)
        chg = dl.format_number(banknifty["change"], decimals=2)
        pct = dl.format_percentage(banknifty["pct_change"])
        render_metric_tile("Bank Nifty", p, chg, pct, banknifty["change"] > 0, banknifty["change"] < 0)
    else:
        render_metric_tile("Bank Nifty", "N/A", "0.00", "0.00%", False, False)

col4, col5, col6 = st.columns(3)

# 4. USD / INR
usdinr = index_quotes.get("INR=X")
with col4:
    if usdinr and usdinr.get("price") is not None:
        p = dl.format_rupees(usdinr["price"])
        chg = dl.format_rupees(usdinr["change"])
        pct = dl.format_percentage(usdinr["pct_change"])
        render_metric_tile("USD / INR", p, chg, pct, usdinr["change"] > 0, usdinr["change"] < 0)
    else:
        render_metric_tile("USD / INR", "N/A", "0.00", "0.00%", False, False)

# 5. Gold (USD / oz)
gold = index_quotes.get("GC=F")
with col5:
    if gold and gold.get("price") is not None:
        p = f"${dl.format_number(gold['price'], decimals=2)} / oz"
        chg = f"${dl.format_number(gold['change'], decimals=2)}"
        pct = dl.format_percentage(gold["pct_change"])
        render_metric_tile("Gold (USD / oz)", p, chg, pct, gold["change"] > 0, gold["change"] < 0)
    else:
        render_metric_tile("Gold (USD / oz)", "N/A", "0.00", "0.00%", False, False)

# 6. Gold (INR / 10g)
# Conversion: 1 troy ounce = 31.1035 grams
with col6:
    if gold and gold.get("price") and usdinr and usdinr.get("price"):
        gold_usd = gold["price"]
        prev_gold_usd = gold["previous_close"]
        rate_usd_inr = usdinr["price"]
        prev_rate_usd_inr = usdinr["previous_close"]
        
        gold_inr_10g = (gold_usd / 31.1035) * rate_usd_inr * 10.0
        prev_gold_inr_10g = (prev_gold_usd / 31.1035) * prev_rate_usd_inr * 10.0
        chg_gold_inr = gold_inr_10g - prev_gold_inr_10g
        pct_gold_inr = (chg_gold_inr / prev_gold_inr_10g * 100.0) if prev_gold_inr_10g != 0 else 0.0
        
        p = f"{dl.format_rupees(gold_inr_10g)} / 10g"
        chg = dl.format_rupees(chg_gold_inr)
        pct = dl.format_percentage(pct_gold_inr)
        render_metric_tile("Gold (INR / 10g)", p, chg, pct, chg_gold_inr > 0, chg_gold_inr < 0)
    else:
        render_metric_tile("Gold (INR / 10g)", "N/A", "0.00", "0.00%", False, False)

# Source and timestamp under tiles
if indices_offline:
    dl.render_html(f"<div class='source-timestamp'><span class='offline-badge'>{index_source}</span></div>")
else:
    dl.render_html(f"<div class='source-timestamp'>{index_source}</div>")


# ==============================================================================
# SECTION 2: Top Gainers & Top Losers of the Day (Nifty 50)
# ==============================================================================

dl.render_html("""
<div class='section-header'>
    <span class='section-header-bar'></span>
    Top Gainers and Losers
</div>
""")

symbols_df = dl.get_nifty50_symbols()
nifty_tickers = symbols_df["yahoo_ticker"].tolist()
nifty_quotes, nifty_offline, nifty_source = dl.get_batch_quotes(nifty_tickers)

nifty_records = []
for _, row in symbols_df.iterrows():
    tkr = row["yahoo_ticker"]
    q = nifty_quotes.get(tkr)
    if q and q.get("price") is not None:
        nifty_records.append({
            "ticker": tkr,
            "company": row["company"],
            "sector": row["sector"],
            "price_val": q["price"],
            "change_val": q["change"],
            "pct_val": q["pct_change"],
            "price": dl.format_rupees(q["price"]),
            "pct_change": dl.format_percentage(q["pct_change"], show_sign=True)
        })

if nifty_records:
    df_nifty = pd.DataFrame(nifty_records)
    gainers_df = df_nifty.sort_values(by="pct_val", ascending=False).head(5)
    losers_df = df_nifty.sort_values(by="pct_val", ascending=True).head(5)
    
    col_g, col_l = st.columns(2, gap="large")
    
    with col_g:
        dl.render_html("<div style='font-size: 1.1rem; font-weight: 700; color: #10b981; margin-bottom: 0.6rem;'>▲ Top 5 Gainers</div>")
        rows_g = ""
        for _, row in gainers_df.iterrows():
            rows_g += f"<tr><td><b>{row['company']}</b><span class='sector-subtext'>{row['sector']}</span></td><td class='num-col'>{row['price']}</td><td class='num-col'><span class='table-badge-pos'>{row['pct_change']}</span></td></tr>"
        table_g_html = f"<table class='fin-table'><thead><tr><th>Company</th><th class='num-col'>Last Price</th><th class='num-col'>% Change</th></tr></thead><tbody>{rows_g}</tbody></table>"
        dl.render_html(table_g_html)
        
    with col_l:
        dl.render_html("<div style='font-size: 1.1rem; font-weight: 700; color: #f43f5e; margin-bottom: 0.6rem;'>▼ Top 5 Losers</div>")
        rows_l = ""
        for _, row in losers_df.iterrows():
            rows_l += f"<tr><td><b>{row['company']}</b><span class='sector-subtext'>{row['sector']}</span></td><td class='num-col'>{row['price']}</td><td class='num-col'><span class='table-badge-neg'>{row['pct_change']}</span></td></tr>"
        table_l_html = f"<table class='fin-table'><thead><tr><th>Company</th><th class='num-col'>Last Price</th><th class='num-col'>% Change</th></tr></thead><tbody>{rows_l}</tbody></table>"
        dl.render_html(table_l_html)
else:
    st.info("Market data is currently being fetched. Please refresh in a moment.")


# ==============================================================================
# SECTION 3: Sector Heat Strip
# ==============================================================================

dl.render_html("""
<div class='section-header'>
    <span class='section-header-bar'></span>
    Sector Heat Strip
</div>
""")
st.caption("Average percentage change per sector across all 50 constituent companies, ordered from most negative to most positive.")

if nifty_records:
    sector_summary = df_nifty.groupby("sector")["pct_val"].mean().reset_index()
    sector_summary = sector_summary.sort_values(by="pct_val", ascending=True)
    
    chips_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.75rem; margin-top: 0.5rem;'>"
    for _, row in sector_summary.iterrows():
        sec = row["sector"]
        avg_pct = row["pct_val"]
        pct_label = dl.format_percentage(avg_pct, show_sign=True)
        if avg_pct > 0.05:
            chip_class = "chip-pos"
            arrow = "▲ "
        elif avg_pct < -0.05:
            chip_class = "chip-neg"
            arrow = "▼ "
        else:
            chip_class = "chip-neutral"
            arrow = ""
        chips_html += f"<span class='sector-chip {chip_class}'>{sec} &nbsp; <b>{arrow}{pct_label}</b></span>"
    chips_html += "</div>"
    dl.render_html(chips_html)


# ==============================================================================
# SECTION 4: Interactive Historical Chart
# ==============================================================================

dl.render_html("""
<div class='section-header'>
    <span class='section-header-bar'></span>
    Historical Price Chart
</div>
""")

chart_options = {
    "Nifty 50 (^NSEI)": "^NSEI",
    "Sensex (^BSESN)": "^BSESN",
    "Bank Nifty (^NSEBANK)": "^NSEBANK",
    "USD / INR (INR=X)": "INR=X",
    "Gold (USD/oz) (GC=F)": "GC=F"
}
for _, row in symbols_df.iterrows():
    chart_options[f"{row['company']} ({row['yahoo_ticker']})"] = row["yahoo_ticker"]

chart_col1, chart_col2 = st.columns([3, 2])
with chart_col1:
    selected_label = st.selectbox("Select Benchmark or Company", list(chart_options.keys()), index=0)
    selected_ticker = chart_options[selected_label]

with chart_col2:
    period_map = {
        "1 month": "1mo",
        "6 months": "6mo",
        "1 year": "1y",
        "5 years": "5y"
    }
    selected_period_label = st.selectbox("Select Time Horizon", list(period_map.keys()), index=0)
    selected_period = period_map[selected_period_label]

hist_df, stats, hist_offline, hist_source = dl.get_daily_history(selected_ticker, selected_period)

if hist_df is not None and not hist_df.empty:
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    
    is_currency_or_idx = selected_ticker in ["^NSEI", "^BSESN", "^NSEBANK"]
    is_gold_usd = selected_ticker == "GC=F"
    is_usdinr = selected_ticker == "INR=X"
    
    def format_stat_val(v):
        if is_currency_or_idx:
            return dl.format_number(v, decimals=2)
        elif is_gold_usd:
            return f"${dl.format_number(v, decimals=2)}"
        else:
            return dl.format_rupees(v)
            
    with stat_col1:
        dl.render_html(f"""
        <div class='chart-stat-box'>
            <div class='chart-stat-label'>Period High</div>
            <div class='chart-stat-val'>{format_stat_val(stats['high'])}</div>
        </div>
        """)
        
    with stat_col2:
        dl.render_html(f"""
        <div class='chart-stat-box'>
            <div class='chart-stat-label'>Period Low</div>
            <div class='chart-stat-val'>{format_stat_val(stats['low'])}</div>
        </div>
        """)
        
    with stat_col3:
        p_pct = stats["period_pct_change"]
        pct_color = "#10b981" if p_pct > 0 else ("#f43f5e" if p_pct < 0 else "#94a3b8")
        arrow = "▲ " if p_pct > 0 else ("▼ " if p_pct < 0 else "")
        dl.render_html(f"""
        <div class='chart-stat-box'>
            <div class='chart-stat-label'>Period Change</div>
            <div class='chart-stat-val' style='color: {pct_color} !important;'>{arrow}{dl.format_percentage(p_pct, show_sign=True)}</div>
        </div>
        """)
        
    chart_data = hist_df.copy()
    st.line_chart(chart_data["Close"], use_container_width=True)
    
    if hist_offline:
        dl.render_html(f"<div class='source-timestamp'><span class='offline-badge'>{hist_source}</span></div>")
    else:
        dl.render_html(f"<div class='source-timestamp'>{hist_source}</div>")
else:
    st.warning("Historical price data could not be retrieved at this moment. Please try selecting a different period or check back shortly.")


# ==============================================================================
# SECTION 5: Watchlist (Stored in SQLite)
# ==============================================================================

dl.render_html("""
<div class='section-header'>
    <span class='section-header-bar'></span>
    My Watchlist
</div>
""")
st.caption("Add any Nifty 50 constituent or type any NSE symbol. Your watchlist is preserved in SQLite.")

watch_col1, watch_col2 = st.columns([3, 1], gap="medium")

with watch_col1:
    add_mode = st.radio("Add to Watchlist:", ["Select from Nifty 50", "Type NSE Ticker"], horizontal=True)
    
    if add_mode == "Select from Nifty 50":
        nifty_add_options = {f"{r['company']} ({r['symbol']})": (r['yahoo_ticker'], r['company']) for _, r in symbols_df.iterrows()}
        selected_add_item = st.selectbox("Choose company", list(nifty_add_options.keys()))
        selected_add_ticker, selected_add_company = nifty_add_options[selected_add_item]
        if st.button("Add to Watchlist", key="btn_add_nifty", type="secondary"):
            ok, msg = dl.add_to_watchlist(selected_add_ticker, selected_add_company)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)
    else:
        typed_ticker = st.text_input("Enter NSE Ticker Symbol (e.g. TATAMOTORS, ITC, SBIN):", placeholder="e.g. TATAMOTORS")
        if st.button("Validate & Add Ticker", key="btn_add_custom", type="secondary"):
            if typed_ticker.strip():
                clean_sym = typed_ticker.strip().upper()
                test_ticker = clean_sym if clean_sym.endswith(".NS") or clean_sym.startswith("^") or "=" in clean_sym else f"{clean_sym}.NS"
                
                with st.spinner("Validating ticker on Yahoo Finance..."):
                    q, _, _ = dl.get_latest_price(test_ticker)
                    
                if q and q.get("price") is not None:
                    cname = dl.get_ticker_company_name(test_ticker)
                    ok, msg = dl.add_to_watchlist(test_ticker, cname)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.warning(msg)
                else:
                    st.error("That ticker was not found on Yahoo Finance. Please check the symbol and try again.")
            else:
                st.warning("Please enter a valid ticker symbol.")

current_watchlist = dl.get_watchlist()

if current_watchlist:
    wl_tickers = [item["ticker"] for item in current_watchlist]
    wl_quotes, wl_offline, wl_source = dl.get_batch_quotes(wl_tickers)
    
    dl.render_html("<div style='font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-top: 1rem; margin-bottom: 0.75rem;'>Tracked Assets</div>")
    
    for item in current_watchlist:
        tkr = item["ticker"]
        cname = item["company_name"]
        q = wl_quotes.get(tkr)
        
        card_col1, card_col2, card_col3, card_col4, card_col5 = st.columns([3, 2, 2, 1, 1])
        
        with card_col1:
            dl.render_html(f"<div class='wl-name'>{cname}</div><div class='wl-ticker'>{tkr}</div>")
            
        with card_col2:
            if q and q.get("price") is not None:
                p_str = dl.format_rupees(q["price"]) if not (tkr.startswith("^") or "=" in tkr) else dl.format_number(q["price"])
                dl.render_html(f"<div class='wl-price'>{p_str}</div>")
            else:
                dl.render_html("<div class='wl-price' style='color: #64748b;'>—</div>")
                
        with card_col3:
            if q and q.get("change") is not None:
                is_pos = q["change"] > 0
                is_neg = q["change"] < 0
                col_style = "#10b981" if is_pos else ("#f43f5e" if is_neg else "#94a3b8")
                arrow = "▲ " if is_pos else ("▼ " if is_neg else "")
                sign = "+" if is_pos else ""
                chg_str = dl.format_rupees(q["change"]) if not (tkr.startswith("^") or "=" in tkr) else dl.format_number(q["change"])
                pct_str = dl.format_percentage(q["pct_change"])
                dl.render_html(f"<div style='color: {col_style}; font-weight: 700; font-size: 1.05rem; padding-top: 0.2rem;'>{arrow}{sign}{chg_str} ({sign}{pct_str})</div>")
            else:
                dl.render_html("<div style='color: #64748b; font-size: 1.05rem;'>—</div>")
                
        with card_col4:
            is_tradable = not (tkr.startswith("^") or "=" in tkr)
            if is_tradable:
                if st.button("Trade", key=f"trade_{tkr}", type="primary"):
                    st.session_state["trade_ticker"] = tkr
                    st.switch_page("pages/5_Paper_Trading.py")

        with card_col5:
            if st.button("Remove", key=f"del_{tkr}"):
                dl.remove_from_watchlist(tkr)
                st.rerun()
                
        dl.render_html("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #1e293b;'>")
        
    if wl_offline:
        dl.render_html(f"<div class='source-timestamp'><span class='offline-badge'>{wl_source}</span></div>")
    else:
        dl.render_html(f"<div class='source-timestamp'>{wl_source}</div>")
else:
    st.info("Your watchlist is currently empty. Add a stock from the options above.")


# ==============================================================================
# Mandatory House Style Disclaimer Footer (Rule 7)
# ==============================================================================
dl.render_footer()
