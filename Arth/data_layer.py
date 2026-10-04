"""
data_layer.py - Centralized Data Layer for Arth Personal Finance Platform
Implements:
- 15-minute caching for all network calls
- Daily snapshot persistence to snapshots/
- Automatic fallback to latest snapshot if offline / Yahoo unreachable
- SQLite persistence for user data (arth.db)
- House style formatting (Rupees, dates, percentages, plain English errors)
"""

import os
import time
import datetime
import sqlite3
import glob
import json
import requests
import numpy as np
import pandas as pd
import yfinance as yf

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
SNAPSHOTS_DIR = os.path.join(BASE_DIR, "snapshots")
DB_PATH = os.path.join(BASE_DIR, "arth.db")
NIFTY50_CSV_PATH = os.path.join(DATA_DIR, "nifty50-symbols.csv")
FD_RATES_CSV_PATH = os.path.join(DATA_DIR, "fd-rates.csv")

# Ensure snapshots folder exists
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

# Cache configuration (15 minutes = 900 seconds)
CACHE_TTL_SECONDS = 15 * 60

# In-memory cache structures: {cache_key: {"data": ..., "timestamp": float, "is_offline": bool, "source_label": str}}
_MEMORY_CACHE = {}

# Known standard indices metadata
INDICES_META = {
    "^NSEI": {"company_name": "Nifty 50", "sector": "Benchmark Index"},
    "^BSESN": {"company_name": "Sensex", "sector": "Benchmark Index"},
    "^NSEBANK": {"company_name": "Bank Nifty", "sector": "Sectoral Index"},
    "INR=X": {"company_name": "USD / INR", "sector": "Currency"},
    "GC=F": {"company_name": "Gold (USD/oz)", "sector": "Commodity"}
}


# ==============================================================================
# 1. House Style Formatters (Rule 1 & Rule 5)
# ==============================================================================

def format_rupees(val, narrative=False) -> str:
    """
    Format value in Indian Rupees according to docs/house-style.md:
    - Standard: Rs 12,34,567.89 (Indian digit grouping, two decimals)
    - Narrative: Rs 12.3 lakh, Rs 1.5 crore
    """
    if val is None or pd.isna(val):
        return "N/A"
    
    try:
        val = float(val)
    except (ValueError, TypeError):
        return "N/A"
    
    is_neg = val < 0
    abs_val = abs(val)
    sign = "-" if is_neg else ""
    
    if narrative:
        if abs_val >= 10_000_000:
            return f"{sign}Rs {abs_val / 10_000_000:.2f} crore"
        elif abs_val >= 100_000:
            return f"{sign}Rs {abs_val / 100_000:.2f} lakh"
    
    # Standard Indian digit grouping
    formatted_dec = f"{abs_val:.2f}"
    int_part, dec_part = formatted_dec.split(".")
    
    if len(int_part) <= 3:
        grouped = int_part
    else:
        last3 = int_part[-3:]
        remaining = int_part[:-3]
        chunks = []
        while len(remaining) > 2:
            chunks.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            chunks.insert(0, remaining)
        grouped = ",".join(chunks) + "," + last3
        
    return f"{sign}Rs {grouped}.{dec_part}"


def format_number(val, decimals=2) -> str:
    """Format plain number with Indian digit grouping and specified decimals."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        val = float(val)
    except (ValueError, TypeError):
        return "N/A"
    
    is_neg = val < 0
    abs_val = abs(val)
    sign = "-" if is_neg else ""
    
    formatted_dec = f"{abs_val:.{decimals}f}"
    if decimals > 0:
        int_part, dec_part = formatted_dec.split(".")
    else:
        int_part = formatted_dec
        dec_part = ""
        
    if len(int_part) <= 3:
        grouped = int_part
    else:
        last3 = int_part[-3:]
        remaining = int_part[:-3]
        chunks = []
        while len(remaining) > 2:
            chunks.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            chunks.insert(0, remaining)
        grouped = ",".join(chunks) + "," + last3
        
    return f"{sign}{grouped}" + (f".{dec_part}" if decimals > 0 else "")


def format_date(dt: datetime.datetime | datetime.date | str) -> str:
    """Format date strictly as '1 Oct 2026'."""
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except Exception:
            return dt
    if hasattr(dt, "day") and hasattr(dt, "year"):
        month_abbr = dt.strftime("%b")
        return f"{dt.day} {month_abbr} {dt.year}"
    return str(dt)


def format_timestamp(dt: datetime.datetime | None = None) -> str:
    """Format timestamp e.g. '1 Oct 2026 15:30 IST'."""
    if dt is None:
        dt = datetime.datetime.now()
    month_abbr = dt.strftime("%b")
    time_str = dt.strftime("%H:%M")
    return f"{dt.day} {month_abbr} {dt.year} {time_str} IST"


def format_percentage(val, show_sign=False) -> str:
    """Format percentage to two decimals: '12.34%' or '+12.34%'."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        val = float(val)
    except (ValueError, TypeError):
        return "N/A"
    sign = "+" if (show_sign and val > 0) else ""
    return f"{sign}{val:.2f}%"


def format_source_timestamp(is_offline: bool, offline_date: str = "", dt: datetime.datetime | None = None) -> str:
    """
    Format source indicator under tiles / tables.
    Online: 'Yahoo Finance, 1 Oct 2026 15:30 IST, delayed about 15 minutes'
    Offline: 'offline data from 1 Oct 2026'
    """
    if is_offline:
        date_label = offline_date if offline_date else format_date(datetime.date.today())
        return f"offline data from {date_label}"
    else:
        ts = format_timestamp(dt)
        return f"Yahoo Finance, {ts}, delayed about 15 minutes"


def render_html(html_str: str):
    """Renders raw HTML safely in Streamlit without triggering Markdown indented code block parsing."""
    import streamlit as st
    clean_lines = [line.strip() for line in html_str.strip().split("\n")]
    clean_str = "".join(clean_lines)
    st.markdown(clean_str, unsafe_allow_html=True)


def render_footer():
    """Renders mandatory educational disclaimer footer on every page (Rule 7)."""
    import streamlit as st
    st.markdown("---")
    render_html(
        "<div style='text-align: center; color: #94a3b8; font-size: 0.95rem; padding: 1.5rem 0; font-weight: 500; letter-spacing: 0.02em;'>"
        "Arth is a learning platform. Nothing here is investment advice."
        "</div>"
    )


# ==============================================================================
# 2. Database Layer (SQLite: arth.db)
# ==============================================================================

def get_db_connection():
    """Returns a SQLite connection to arth.db with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables in arth.db."""
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                ticker TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Prepopulate with 5 core Nifty 50 companies if empty
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM watchlist")
        count = cursor.fetchone()["cnt"]
        if count == 0:
            initial_items = [
                ("RELIANCE.NS", "Reliance Industries"),
                ("TCS.NS", "Tata Consultancy Services"),
                ("HDFCBANK.NS", "HDFC Bank"),
                ("INFY.NS", "Infosys"),
                ("ICICIBANK.NS", "ICICI Bank")
            ]
            conn.executemany(
                "INSERT INTO watchlist (ticker, company_name) VALUES (?, ?)",
                initial_items
            )
    conn.close()


def get_watchlist() -> list[dict]:
    """Returns list of items in watchlist."""
    init_db()
    conn = get_db_connection()
    cursor = conn.execute("SELECT ticker, company_name, added_at FROM watchlist ORDER BY added_at ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def add_to_watchlist(ticker: str, company_name: str = "") -> tuple[bool, str]:
    """Adds a ticker to watchlist. Returns (success, message)."""
    init_db()
    ticker = ticker.strip().upper()
    if not company_name:
        company_name = get_ticker_company_name(ticker)
        
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO watchlist (ticker, company_name) VALUES (?, ?)",
                (ticker, company_name)
            )
        return True, f"{company_name} ({ticker}) added to watchlist."
    except sqlite3.IntegrityError:
        return False, f"{ticker} is already in your watchlist."
    except Exception:
        return False, "Unable to save ticker to watchlist. Please try again."
    finally:
        conn.close()


def remove_from_watchlist(ticker: str) -> tuple[bool, str]:
    """Removes a ticker from watchlist. Returns (success, message)."""
    init_db()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
        return True, f"{ticker} removed from watchlist."
    except Exception:
        return False, "Unable to remove ticker. Please try again."
    finally:
        conn.close()


# ==============================================================================
# 3. Snapshot Management (snapshots/)
# ==============================================================================

def _get_today_snapshot_filename() -> str:
    """Returns filename for today's snapshot."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join(SNAPSHOTS_DIR, f"prices_{today_str}.csv")


def _save_quotes_to_snapshot(quotes_dict: dict[str, dict]):
    """
    Saves or updates daily quote records in snapshots/.
    Also maintains snapshots/latest_prices.csv for rapid offline loading.
    """
    if not quotes_dict:
        return
        
    records = []
    now_ts = datetime.datetime.now().isoformat()
    today_str = format_date(datetime.date.today())
    
    for ticker, q in quotes_dict.items():
        if q and q.get("price") is not None:
            records.append({
                "ticker": ticker,
                "price": q.get("price"),
                "previous_close": q.get("previous_close"),
                "change": q.get("change"),
                "pct_change": q.get("pct_change"),
                "company_name": q.get("company_name", ""),
                "sector": q.get("sector", ""),
                "date": today_str,
                "timestamp": now_ts
            })
            
    if not records:
        return
        
    new_df = pd.DataFrame(records)
    today_file = _get_today_snapshot_filename()
    latest_file = os.path.join(SNAPSHOTS_DIR, "latest_prices.csv")
    
    for target_path in [today_file, latest_file]:
        if os.path.exists(target_path):
            try:
                existing_df = pd.read_csv(target_path)
                combined = pd.concat([existing_df, new_df], ignore_index=True)
                combined = combined.drop_duplicates(subset=["ticker"], keep="last")
                combined.to_csv(target_path, index=False)
            except Exception:
                new_df.to_csv(target_path, index=False)
        else:
            new_df.to_csv(target_path, index=False)


def _load_latest_snapshot() -> tuple[dict[str, dict], str]:
    """
    Finds and loads the latest snapshot from snapshots/.
    Returns (quotes_dict, snapshot_date_str).
    """
    snapshot_files = glob.glob(os.path.join(SNAPSHOTS_DIR, "prices_*.csv"))
    latest_file = os.path.join(SNAPSHOTS_DIR, "latest_prices.csv")
    if os.path.exists(latest_file):
        snapshot_files.append(latest_file)
        
    if not snapshot_files:
        return {}, ""
        
    snapshot_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    target_file = snapshot_files[0]
    
    try:
        df = pd.read_csv(target_file)
        if df.empty or "ticker" not in df.columns:
            return {}, ""
        
        snapshot_date = df["date"].iloc[0] if "date" in df.columns and not df.empty else format_date(datetime.date.today())
        
        result = {}
        for _, row in df.iterrows():
            ticker = str(row["ticker"])
            result[ticker] = {
                "ticker": ticker,
                "price": float(row["price"]) if pd.notna(row.get("price")) else None,
                "previous_close": float(row["previous_close"]) if pd.notna(row.get("previous_close")) else None,
                "change": float(row["change"]) if pd.notna(row.get("change")) else 0.0,
                "pct_change": float(row["pct_change"]) if pd.notna(row.get("pct_change")) else 0.0,
                "company_name": str(row.get("company_name", ticker)) if pd.notna(row.get("company_name")) and str(row.get("company_name")) != "nan" else get_ticker_company_name(ticker),
                "sector": str(row.get("sector", "")) if pd.notna(row.get("sector")) and str(row.get("sector")) != "nan" else get_ticker_sector(ticker),
                "is_offline": True,
                "offline_date": str(snapshot_date)
            }
        return result, str(snapshot_date)
    except Exception:
        return {}, ""


def _save_history_snapshot(ticker: str, period: str, df: pd.DataFrame):
    """Saves daily historical data for a ticker and period to snapshots/."""
    if df is None or df.empty:
        return
    clean_ticker = ticker.replace("^", "").replace("=", "_").replace(".", "_")
    fname = os.path.join(SNAPSHOTS_DIR, f"history_{clean_ticker}_{period}.csv")
    try:
        df.to_csv(fname, index=True)
    except Exception:
        pass


def _load_history_snapshot(ticker: str, period: str) -> tuple[pd.DataFrame | None, str]:
    """Loads historical data from snapshot if available."""
    clean_ticker = ticker.replace("^", "").replace("=", "_").replace(".", "_")
    fname = os.path.join(SNAPSHOTS_DIR, f"history_{clean_ticker}_{period}.csv")
    if os.path.exists(fname):
        try:
            df = pd.read_csv(fname, index_col=0, parse_dates=True)
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(fname))
            snap_date = format_date(mod_time)
            return df, snap_date
        except Exception:
            return None, ""
    return None, ""


# ==============================================================================
# 4. Nifty 50 Symbols Reference & Metadata Helpers
# ==============================================================================

def get_nifty50_symbols() -> pd.DataFrame:
    """Reads data/nifty50-symbols.csv (Read-Only)."""
    if os.path.exists(NIFTY50_CSV_PATH):
        return pd.read_csv(NIFTY50_CSV_PATH)
    starter_path = os.path.join(BASE_DIR, "arth-starter", "data", "nifty50-symbols.csv")
    if os.path.exists(starter_path):
        return pd.read_csv(starter_path)
    return pd.DataFrame(columns=["symbol", "yahoo_ticker", "company", "sector"])


get_nifty50_metadata = get_nifty50_symbols


def get_ticker_company_name(ticker: str) -> str:
    """Returns human-friendly company name for any ticker."""
    if ticker in INDICES_META:
        return INDICES_META[ticker]["company_name"]
    df = get_nifty50_symbols()
    match = df[df["yahoo_ticker"] == ticker]
    if not match.empty:
        return match.iloc[0]["company"]
    # Check by symbol
    clean_sym = ticker.replace(".NS", "").replace(".BO", "")
    match_sym = df[df["symbol"] == clean_sym]
    if not match_sym.empty:
        return match_sym.iloc[0]["company"]
    return clean_sym


def get_ticker_sector(ticker: str) -> str:
    """Returns sector for any ticker."""
    if ticker in INDICES_META:
        return INDICES_META[ticker]["sector"]
    df = get_nifty50_symbols()
    match = df[df["yahoo_ticker"] == ticker]
    if not match.empty:
        return match.iloc[0]["sector"]
    clean_sym = ticker.replace(".NS", "").replace(".BO", "")
    match_sym = df[df["symbol"] == clean_sym]
    if not match_sym.empty:
        return match_sym.iloc[0]["sector"]
    return "Diversified"


# ==============================================================================
# 5. Core Data Layer Functions with 15-Minute Cache & Offline Fallback
# ==============================================================================

def _extract_ticker_sub_df(data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Robustly extracts OHLCV sub-dataframe for a ticker from yf.download result."""
    if data is None or data.empty:
        return pd.DataFrame()
        
    if isinstance(data.columns, pd.MultiIndex):
        level_0 = data.columns.levels[0]
        if ticker in level_0:
            return data[ticker].dropna(subset=["Close"])
        for lvl in level_0:
            if str(lvl).upper() == ticker.upper():
                return data[lvl].dropna(subset=["Close"])
        if "Close" in level_0 and ticker in data.columns.levels[1]:
            transposed = data.xs(ticker, axis=1, level=1)
            return transposed.dropna(subset=["Close"])
        return pd.DataFrame()
    else:
        if "Close" in data.columns:
            return data.dropna(subset=["Close"])
        return pd.DataFrame()


def get_batch_quotes(tickers: list[str]) -> tuple[dict[str, dict], bool, str]:
    """
    Fetches batch quotes for a list of tickers.
    - Uses 15-minute in-memory cache
    - Performs ONE batch call via yfinance
    - Enriches with company and sector metadata
    - Writes snapshot to snapshots/
    - Falls back to snapshots/ if internet fails or offline
    Returns:
        (quotes_dict, is_offline, source_label)
    """
    if not tickers:
        return {}, False, ""
        
    cache_key = "batch_" + ",".join(sorted(tickers))
    now = time.time()
    
    # Check 15-minute cache
    if cache_key in _MEMORY_CACHE:
        cached = _MEMORY_CACHE[cache_key]
        if (now - cached["timestamp"]) < CACHE_TTL_SECONDS:
            return cached["data"], cached["is_offline"], cached["source_label"]

    quotes = {}
    is_offline = False
    source_label = ""
    offline_date = ""

    # Check for forced offline mode (for simulation/testing)
    force_offline = os.environ.get("ARTH_FORCE_OFFLINE") == "1"

    if not force_offline:
        try:
            # ONE batch call for all tickers
            data = yf.download(tickers, period="5d", group_by="ticker", progress=False, timeout=12)
            
            if data is None or data.empty:
                raise ConnectionError("No data received from Yahoo Finance")
                
            for ticker in tickers:
                try:
                    sub = _extract_ticker_sub_df(data, ticker)
                    if not sub.empty:
                        last_price = float(sub["Close"].iloc[-1])
                        prev_close = float(sub["Close"].iloc[-2]) if len(sub) > 1 else last_price
                        change = last_price - prev_close
                        pct_change = (change / prev_close * 100.0) if prev_close != 0 else 0.0
                        
                        company_name = get_ticker_company_name(ticker)
                        sector = get_ticker_sector(ticker)
                        
                        quotes[ticker] = {
                            "ticker": ticker,
                            "price": last_price,
                            "previous_close": prev_close,
                            "change": change,
                            "pct_change": pct_change,
                            "company_name": company_name,
                            "sector": sector,
                            "is_offline": False,
                            "offline_date": ""
                        }
                    else:
                        quotes[ticker] = None
                except Exception:
                    quotes[ticker] = None
                    
            valid_quotes = {k: v for k, v in quotes.items() if v is not None}
            if valid_quotes:
                _save_quotes_to_snapshot(valid_quotes)
                source_label = format_source_timestamp(is_offline=False)
                _MEMORY_CACHE[cache_key] = {
                    "data": quotes,
                    "timestamp": now,
                    "is_offline": False,
                    "source_label": source_label
                }
                return quotes, False, source_label
            else:
                raise ConnectionError("Empty quote results")
                
        except Exception:
            is_offline = True
    else:
        is_offline = True

    # Fallback to snapshots/
    snapshot_quotes, snapshot_date = _load_latest_snapshot()
    offline_date = snapshot_date
    source_label = format_source_timestamp(is_offline=True, offline_date=offline_date)
    
    for ticker in tickers:
        if ticker in snapshot_quotes:
            q = snapshot_quotes[ticker]
            if not q.get("company_name") or q.get("company_name") == "nan":
                q["company_name"] = get_ticker_company_name(ticker)
            if not q.get("sector") or q.get("sector") == "nan":
                q["sector"] = get_ticker_sector(ticker)
            quotes[ticker] = q
        else:
            quotes[ticker] = None
            
    _MEMORY_CACHE[cache_key] = {
        "data": quotes,
        "timestamp": now,
        "is_offline": True,
        "source_label": source_label
    }
    return quotes, is_offline, source_label


def get_latest_price(ticker: str) -> tuple[dict | None, bool, str]:
    """
    Fetches latest price for a single ticker.
    Returns (quote_dict, is_offline, source_label).
    """
    batch_res, is_offline, source_label = get_batch_quotes([ticker])
    quote = batch_res.get(ticker)
    return quote, is_offline, source_label


def get_daily_history(ticker: str, period: str = "1mo") -> tuple[pd.DataFrame | None, dict, bool, str]:
    """
    Fetches daily price history for a ticker and period ('1mo', '6mo', '1y', '5y').
    - Caches for 15 minutes
    - Writes snapshot
    - Falls back to snapshot if offline
    Returns:
        (dataframe, stats_dict, is_offline, source_label)
        stats_dict contains: high, low, period_pct_change, start_price, end_price
    """
    cache_key = f"hist_{ticker}_{period}"
    now = time.time()
    
    if cache_key in _MEMORY_CACHE:
        cached = _MEMORY_CACHE[cache_key]
        if (now - cached["timestamp"]) < CACHE_TTL_SECONDS:
            return cached["df"], cached["stats"], cached["is_offline"], cached["source_label"]
            
    is_offline = False
    stats = {"high": None, "low": None, "period_pct_change": None, "start_price": None, "end_price": None}
    
    force_offline = os.environ.get("ARTH_FORCE_OFFLINE") == "1"
    
    if not force_offline:
        try:
            tkr = yf.Ticker(ticker)
            df = tkr.history(period=period)
            
            if df is None or df.empty or "Close" not in df.columns:
                raise ConnectionError(f"No history for {ticker}")
                
            df = df[["Close"]].dropna()
            if df.empty:
                raise ConnectionError("Empty close prices")
                
            high = float(df["Close"].max())
            low = float(df["Close"].min())
            start_price = float(df["Close"].iloc[0])
            end_price = float(df["Close"].iloc[-1])
            pct_change = ((end_price - start_price) / start_price * 100.0) if start_price != 0 else 0.0
            
            stats = {
                "high": high,
                "low": low,
                "period_pct_change": pct_change,
                "start_price": start_price,
                "end_price": end_price
            }
            
            _save_history_snapshot(ticker, period, df)
            source_label = format_source_timestamp(is_offline=False)
            
            _MEMORY_CACHE[cache_key] = {
                "df": df,
                "stats": stats,
                "is_offline": False,
                "source_label": source_label,
                "timestamp": now
            }
            return df, stats, False, source_label
            
        except Exception:
            is_offline = True
    else:
        is_offline = True

    # Fallback to history snapshot
    df, snap_date = _load_history_snapshot(ticker, period)
    if df is not None and not df.empty and "Close" in df.columns:
        high = float(df["Close"].max())
        low = float(df["Close"].min())
        start_price = float(df["Close"].iloc[0])
        end_price = float(df["Close"].iloc[-1])
        pct_change = ((end_price - start_price) / start_price * 100.0) if start_price != 0 else 0.0
        stats = {
            "high": high,
            "low": low,
            "period_pct_change": pct_change,
            "start_price": start_price,
            "end_price": end_price
        }
        source_label = format_source_timestamp(is_offline=True, offline_date=snap_date)
        _MEMORY_CACHE[cache_key] = {
            "df": df,
            "stats": stats,
            "is_offline": True,
            "source_label": source_label,
            "timestamp": now
        }
        return df, stats, True, source_label
    else:
        return None, stats, True, "offline data from unavailable snapshot"


# ==============================================================================
# 6. Financial Calculators (Rule 1 & docs/finance-formulas.md)
# ==============================================================================

TAX_SLABS_CSV_PATH = os.path.join(DATA_DIR, "tax-slabs.csv")


def calc_budget_planner(income: float, needs_pct: float = 50.0, wants_pct: float = 30.0, savings_pct: float = 20.0) -> dict:
    """
    Budget planner (50/30/20 rule with custom overrides).
    Needs = income * (needs_pct / 100)
    Wants = income * (wants_pct / 100)
    Savings = income * (savings_pct / 100)
    """
    income = max(0.0, float(income))
    needs_amount = income * (needs_pct / 100.0)
    wants_amount = income * (wants_pct / 100.0)
    savings_amount = income * (savings_pct / 100.0)
    pct_sum = needs_pct + wants_pct + savings_pct
    
    return {
        "income": income,
        "needs_pct": needs_pct,
        "wants_pct": wants_pct,
        "savings_pct": savings_pct,
        "pct_sum": pct_sum,
        "needs_amount": needs_amount,
        "wants_amount": wants_amount,
        "savings_amount": savings_amount
    }


def calc_emi(principal: float, annual_rate_pct: float, tenure_years: float) -> dict:
    """
    Exact formula from docs/finance-formulas.md:
    EMI = P * i * (1+i)^n / ((1+i)^n - 1), where i = r/12 and n = months.
    """
    P = max(0.0, float(principal))
    r = max(0.0, float(annual_rate_pct)) / 100.0
    n = max(1, int(round(tenure_years * 12)))
    i = r / 12.0
    
    if P == 0:
        return {"emi": 0.0, "total_paid": 0.0, "total_interest": 0.0, "schedule_df": pd.DataFrame(), "first_12_months_df": pd.DataFrame()}
        
    if i == 0:
        emi = P / n
    else:
        emi = P * i * ((1.0 + i) ** n) / (((1.0 + i) ** n) - 1.0)
        
    total_paid = emi * n
    total_interest = total_paid - P
    
    # Amortization schedule
    balance = P
    records = []
    for m in range(1, n + 1):
        interest_m = balance * i
        principal_m = emi - interest_m
        if principal_m > balance:
            principal_m = balance
            emi_m = principal_m + interest_m
        else:
            emi_m = emi
        end_balance = max(0.0, balance - principal_m)
        records.append({
            "Month": m,
            "Beginning Balance": balance,
            "EMI": emi_m,
            "Principal Paid": principal_m,
            "Interest Paid": interest_m,
            "Ending Balance": end_balance
        })
        balance = end_balance
        
    schedule_df = pd.DataFrame(records)
    first_12_df = schedule_df.head(12).copy()
    
    return {
        "P": P,
        "r": r,
        "i": i,
        "n": n,
        "emi": emi,
        "total_paid": total_paid,
        "total_interest": total_interest,
        "schedule_df": schedule_df,
        "first_12_months_df": first_12_df
    }


def calc_sip(monthly_amount: float, annual_return_pct: float, tenure_years: float) -> dict:
    """
    Exact formula from docs/finance-formulas.md:
    SIP future value (monthly, invested at the start of each month) = A * ((1+i)^n - 1) / i * (1+i).
    where i = r/12 and n = months.
    """
    A = max(0.0, float(monthly_amount))
    r = max(0.0, float(annual_return_pct)) / 100.0
    t = max(1, int(round(tenure_years)))
    n = t * 12
    i = r / 12.0
    
    invested_amount = A * n
    
    if i == 0:
        final_value = invested_amount
    else:
        final_value = A * (((1.0 + i) ** n - 1.0) / i) * (1.0 + i)
        
    wealth_gained = max(0.0, final_value - invested_amount)
    
    # Yearly breakdown for chart
    yearly_records = []
    for y in range(1, t + 1):
        ny = y * 12
        inv_y = A * ny
        if i == 0:
            val_y = inv_y
        else:
            val_y = A * (((1.0 + i) ** ny - 1.0) / i) * (1.0 + i)
        yearly_records.append({
            "Year": y,
            "Invested Amount": inv_y,
            "Portfolio Value": val_y
        })
    yearly_df = pd.DataFrame(yearly_records)
    
    return {
        "A": A,
        "r": r,
        "i": i,
        "n": n,
        "tenure_years": t,
        "invested_amount": invested_amount,
        "final_value": final_value,
        "wealth_gained": wealth_gained,
        "yearly_df": yearly_df
    }


def calc_step_up_sip(monthly_amount: float, annual_return_pct: float, tenure_years: float, step_up_pct: float) -> dict:
    """
    Exact formula from docs/finance-formulas.md:
    Step-up SIP: the monthly amount rises by s% every 12 months; sum each month's contribution compounded to the end.
    """
    A = max(0.0, float(monthly_amount))
    r = max(0.0, float(annual_return_pct)) / 100.0
    t = max(1, int(round(tenure_years)))
    s = max(0.0, float(step_up_pct)) / 100.0
    n = t * 12
    i = r / 12.0
    
    # Calculate plain SIP for side-by-side comparison
    plain_res = calc_sip(monthly_amount, annual_return_pct, tenure_years)
    
    # Calculate step-up month by month
    invested_step = 0.0
    fv_step = 0.0
    
    # Also track yearly points
    yearly_records = []
    current_invested = 0.0
    
    # Precompute running value for each year
    for y in range(1, t + 1):
        ny = y * 12
        inv_y = 0.0
        val_y = 0.0
        for m in range(1, ny + 1):
            c_m = A * ((1.0 + s) ** ((m - 1) // 12))
            inv_y += c_m
            val_y += c_m * ((1.0 + i) ** (ny - m + 1))
        # Plain SIP at year y
        inv_plain = A * ny
        val_plain = A * (((1.0 + i) ** ny - 1.0) / i) * (1.0 + i) if i > 0 else inv_plain
        yearly_records.append({
            "Year": y,
            "Plain SIP Value": val_plain,
            "Step-up SIP Value": val_y,
            "Plain Invested": inv_plain,
            "Step-up Invested": inv_y
        })
        
    invested_step = yearly_records[-1]["Step-up Invested"]
    fv_step = yearly_records[-1]["Step-up SIP Value"]
    wealth_gained_step = max(0.0, fv_step - invested_step)
    
    diff_wealth = fv_step - plain_res["final_value"]
    diff_invested = invested_step - plain_res["invested_amount"]
    
    yearly_df = pd.DataFrame(yearly_records)
    
    return {
        "A": A,
        "r": r,
        "i": i,
        "n": n,
        "s": s,
        "tenure_years": t,
        "plain_sip": plain_res,
        "invested_amount": invested_step,
        "final_value": fv_step,
        "wealth_gained": wealth_gained_step,
        "diff_wealth": diff_wealth,
        "diff_invested": diff_invested,
        "yearly_df": yearly_df
    }


def calc_lump_sum(principal: float, annual_return_pct: float, tenure_years: float) -> dict:
    """
    Exact formula from docs/finance-formulas.md:
    Lump sum future value = P * (1+r)^t.
    """
    P = max(0.0, float(principal))
    r = max(0.0, float(annual_return_pct)) / 100.0
    t = max(1, int(round(tenure_years)))
    
    final_value = P * ((1.0 + r) ** t)
    wealth_gained = max(0.0, final_value - P)
    
    # Year-by-year table and growth curve
    records = []
    for y in range(1, t + 1):
        beginning = P * ((1.0 + r) ** (y - 1))
        returns = beginning * r
        ending = P * ((1.0 + r) ** y)
        records.append({
            "Year": y,
            "Beginning Value": beginning,
            "Returns Earned": returns,
            "Ending Value": ending
        })
    yearly_df = pd.DataFrame(records)
    
    return {
        "P": P,
        "r": r,
        "t": t,
        "final_value": final_value,
        "wealth_gained": wealth_gained,
        "yearly_df": yearly_df
    }


def calc_goal_planner(target_today: float, tenure_years: float, annual_return_pct: float, inflation_pct: float) -> dict:
    """
    Goal planner:
    - Target nominal = target_today
    - Target inflated (real target) = target_today * (1+inflation)^t
    - SIP needed = FV / (((1+i)^n - 1) / i * (1+i))
    """
    target = max(0.0, float(target_today))
    t = max(1, int(round(tenure_years)))
    r = max(0.0, float(annual_return_pct)) / 100.0
    inf = max(0.0, float(inflation_pct)) / 100.0
    n = t * 12
    i = r / 12.0
    
    # Target inflated
    target_inflated = target * ((1.0 + inf) ** t)
    
    # SIP factor = ((1+i)^n - 1) / i * (1+i)
    if i == 0:
        factor = float(n)
    else:
        factor = (((1.0 + i) ** n - 1.0) / i) * (1.0 + i)
        
    sip_without_inflation = (target / factor) if factor > 0 else 0.0
    sip_with_inflation = (target_inflated / factor) if factor > 0 else 0.0
    
    diff_sip = sip_with_inflation - sip_without_inflation
    diff_target = target_inflated - target
    
    # Trajectory chart data
    yearly_records = []
    for y in range(1, t + 1):
        ny = y * 12
        if i == 0:
            fy = float(ny)
        else:
            fy = (((1.0 + i) ** ny - 1.0) / i) * (1.0 + i)
        yearly_records.append({
            "Year": y,
            "Target (Inflated)": target * ((1.0 + inf) ** y),
            "Accumulation (With Inflation SIP)": sip_with_inflation * fy,
            "Accumulation (Without Inflation SIP)": sip_without_inflation * fy
        })
    yearly_df = pd.DataFrame(yearly_records)
    
    return {
        "target_today": target,
        "target_inflated": target_inflated,
        "sip_without_inflation": sip_without_inflation,
        "sip_with_inflation": sip_with_inflation,
        "diff_sip": diff_sip,
        "diff_target": diff_target,
        "tenure_years": t,
        "annual_return_pct": annual_return_pct,
        "inflation_pct": inflation_pct,
        "factor": factor,
        "yearly_df": yearly_df
    }


def calc_inflation(amount_today: float, inflation_pct: float, tenure_years: float) -> dict:
    """
    Exact formulas from docs/finance-formulas.md:
    - What it will cost then: Future cost = nominal * (1+inflation)^t
    - What today's money will be worth then: Real value = nominal / (1+inflation)^t
    """
    P = max(0.0, float(amount_today))
    inf = max(0.0, float(inflation_pct)) / 100.0
    t = max(1, int(round(tenure_years)))
    
    future_cost = P * ((1.0 + inf) ** t)
    purchasing_power = P / ((1.0 + inf) ** t)
    
    yearly_records = []
    for y in range(0, t + 1):
        yearly_records.append({
            "Year": y,
            "Future Cost of Today's Goods": P * ((1.0 + inf) ** y),
            "Purchasing Power of Cash": P / ((1.0 + inf) ** y)
        })
    yearly_df = pd.DataFrame(yearly_records)
    
    return {
        "P": P,
        "inflation_pct": inflation_pct,
        "inf": inf,
        "t": t,
        "future_cost": future_cost,
        "purchasing_power": purchasing_power,
        "yearly_df": yearly_df
    }


def calc_retirement_corpus(current_age: int, retirement_age: int, life_expectancy: int,
                           monthly_expense_today: float, inflation_pct: float,
                           pre_ret_return_pct: float, post_ret_return_pct: float) -> dict:
    """
    Exact formula from docs/finance-formulas.md:
    Retirement corpus at retirement = annual expense in the first retirement year * (1 - (1+g)^-N) / g,
    where g = (1+post-retirement return)/(1+inflation) - 1 and N = years in retirement.
    """
    age_curr = int(current_age)
    age_ret = int(retirement_age)
    age_life = int(life_expectancy)
    
    t = max(1, age_ret - age_curr)  # Years to retirement
    N = max(1, age_life - age_ret)  # Years in retirement
    
    exp_today = max(0.0, float(monthly_expense_today))
    inf = max(0.0, float(inflation_pct)) / 100.0
    r_pre = max(0.0, float(pre_ret_return_pct)) / 100.0
    r_post = max(0.0, float(post_ret_return_pct)) / 100.0
    
    # Monthly expense in first retirement year
    monthly_expense_at_ret = exp_today * ((1.0 + inf) ** t)
    annual_expense_first_year = monthly_expense_at_ret * 12.0
    
    # Real rate of return g
    g = (1.0 + r_post) / (1.0 + inf) - 1.0
    
    if abs(g) < 1e-7:
        corpus = annual_expense_first_year * N
    else:
        corpus = annual_expense_first_year * (1.0 - ((1.0 + g) ** (-N))) / g
        
    # Monthly SIP required from today
    i_pre = r_pre / 12.0
    n_pre = t * 12
    if i_pre == 0:
        sip_needed = corpus / n_pre if n_pre > 0 else 0.0
    else:
        factor = (((1.0 + i_pre) ** n_pre - 1.0) / i_pre) * (1.0 + i_pre)
        sip_needed = corpus / factor if factor > 0 else 0.0
        
    # Progression projection (Accumulation to Decumulation)
    records = []
    # Accumulation
    for y in range(0, t + 1):
        age = age_curr + y
        ny = y * 12
        if i_pre == 0:
            val = sip_needed * ny
        else:
            val = sip_needed * (((1.0 + i_pre) ** ny - 1.0) / i_pre) * (1.0 + i_pre) if ny > 0 else 0.0
        records.append({
            "Age": age,
            "Phase": "Accumulation",
            "Corpus Balance": min(corpus, val)
        })
    # Decumulation
    balance = corpus
    for yr in range(1, N + 1):
        age = age_ret + yr
        expense_yr = annual_expense_first_year * ((1.0 + inf) ** (yr - 1))
        balance = max(0.0, (balance - expense_yr) * (1.0 + r_post))
        records.append({
            "Age": age,
            "Phase": "Decumulation",
            "Corpus Balance": balance
        })
    projection_df = pd.DataFrame(records)
    
    return {
        "current_age": age_curr,
        "retirement_age": age_ret,
        "life_expectancy": age_life,
        "years_to_retirement": t,
        "years_in_retirement": N,
        "monthly_expense_today": exp_today,
        "monthly_expense_at_ret": monthly_expense_at_ret,
        "annual_expense_first_year": annual_expense_first_year,
        "real_return_g": g,
        "corpus_needed": corpus,
        "monthly_sip_needed": sip_needed,
        "inflation_pct": inflation_pct,
        "pre_ret_return_pct": pre_ret_return_pct,
        "post_ret_return_pct": post_ret_return_pct,
        "projection_df": projection_df
    }


def calc_tax_comparison(gross_salary: float, inv_80c: float = 0.0, prem_80d: float = 0.0,
                        hra_exemption: float = 0.0, home_loan_interest: float = 0.0) -> dict:
    """
    Tax regime comparison reading directly from data/tax-slabs.csv (do not hard-code slabs).
    Applies standard deduction, slab rates, rebate under 87A and cess for both regimes.
    """
    gross = max(0.0, float(gross_salary))
    inv_80c = min(max(0.0, float(inv_80c)), 150000.0)  # Capped at 1.5L
    prem_80d = max(0.0, float(prem_80d))
    hra_exemption = max(0.0, float(hra_exemption))
    home_loan_interest = min(max(0.0, float(home_loan_interest)), 200000.0)  # Capped at 2L for self-occupied
    
    slabs_df = pd.read_csv(TAX_SLABS_CSV_PATH)
    
    # Financial Year label from note
    new_regime_note = slabs_df[slabs_df["regime"] == "new"].iloc[0]["note"]
    import re
    match = re.search(r"FY\s*\d{4}-\d{2}", str(new_regime_note))
    fy_label = match.group(0) if match else "FY 2025-26"
                
    # Cess rate
    cess_rows = slabs_df[slabs_df["regime"] == "cess"]
    cess_pct = float(cess_rows.iloc[0]["rate_pct"]) if not cess_rows.empty else 4.0
    cess_multiplier = cess_pct / 100.0
    
    # Slabs calculation helper
    def compute_slab_tax(income, regime_type):
        rows = slabs_df[slabs_df["regime"] == regime_type]
        slab_details = []
        total_tax = 0.0
        for _, r in rows.iterrows():
            s_from = float(r["slab_from"])
            s_to = float(r["slab_to"])
            rate = float(r["rate_pct"]) / 100.0
            if income > s_from:
                taxable_chunk = min(income, s_to) - s_from
                chunk_tax = taxable_chunk * rate
                total_tax += chunk_tax
                slab_details.append({
                    "slab": f"Rs {int(s_from):,} - {('Above' if s_to > 99999999 else 'Rs ' + str(int(s_to)))}",
                    "rate": f"{int(r['rate_pct'])}%",
                    "taxable_amount": taxable_chunk,
                    "tax": chunk_tax
                })
        return total_tax, slab_details
        
    # --- 1. NEW REGIME (Budget 2025 / FY 2025-26) ---
    std_deduction_new = 75000.0
    taxable_income_new = max(0.0, gross - std_deduction_new)
    tax_new_gross, slab_details_new = compute_slab_tax(taxable_income_new, "new")
    
    # Rebate 87A for New Regime (nil up to 12,00,000 taxable income)
    if taxable_income_new <= 1200000.0:
        rebate_87a_new = tax_new_gross
        tax_new_net = 0.0
    else:
        rebate_87a_new = 0.0
        tax_new_net = tax_new_gross
        
    cess_new = tax_new_net * cess_multiplier
    total_tax_new = tax_new_net + cess_new
    
    # --- 2. OLD REGIME ---
    std_deduction_old = 50000.0
    total_deductions_old = std_deduction_old + inv_80c + prem_80d + hra_exemption + home_loan_interest
    taxable_income_old = max(0.0, gross - total_deductions_old)
    tax_old_gross, slab_details_old = compute_slab_tax(taxable_income_old, "old")
    
    # Rebate 87A for Old Regime (up to 5,00,000 taxable income, max 12,500)
    if taxable_income_old <= 500000.0:
        rebate_87a_old = min(tax_old_gross, 12500.0)
        tax_old_net = max(0.0, tax_old_gross - rebate_87a_old)
    else:
        rebate_87a_old = 0.0
        tax_old_net = tax_old_gross
        
    cess_old = tax_old_net * cess_multiplier
    total_tax_old = tax_old_net + cess_old
    
    # Comparison
    diff = abs(total_tax_new - total_tax_old)
    if total_tax_new < total_tax_old:
        better_regime = "New Regime"
        savings = total_tax_old - total_tax_new
    elif total_tax_old < total_tax_new:
        better_regime = "Old Regime"
        savings = total_tax_new - total_tax_old
    else:
        better_regime = "Equal"
        savings = 0.0
        
    return {
        "fy_label": fy_label,
        "gross_salary": gross,
        "new_regime": {
            "standard_deduction": std_deduction_new,
            "taxable_income": taxable_income_new,
            "slab_tax": tax_new_gross,
            "rebate_87a": rebate_87a_new,
            "tax_after_rebate": tax_new_net,
            "cess": cess_new,
            "total_tax": total_tax_new,
            "slab_details": slab_details_new
        },
        "old_regime": {
            "standard_deduction": std_deduction_old,
            "inv_80c": inv_80c,
            "prem_80d": prem_80d,
            "hra_exemption": hra_exemption,
            "home_loan_interest": home_loan_interest,
            "total_deductions": total_deductions_old,
            "taxable_income": taxable_income_old,
            "slab_tax": tax_old_gross,
            "rebate_87a": rebate_87a_old,
            "tax_after_rebate": tax_old_net,
            "cess": cess_old,
            "total_tax": total_tax_old,
            "slab_details": slab_details_old
        },
        "better_regime": better_regime,
        "savings": savings
    }


# ==============================================================================
# 5. Fixed Deposit Functions (Module 3)
# ==============================================================================

def get_fd_rates_df() -> pd.DataFrame:
    """
    Reads data/fd-rates.csv (read-only reference table).
    Returns DataFrame with columns:
    [bank, type, tenure_months, rate_general_pct, rate_senior_pct, as_of, source_note]
    """
    if not os.path.exists(FD_RATES_CSV_PATH):
        return pd.DataFrame()
    return pd.read_csv(FD_RATES_CSV_PATH)


def calc_fd_maturity(principal: float, rate_pct: float, tenure_months: int, tax_bracket_pct: float = 0.0) -> dict:
    """
    Exact formula from docs/finance-formulas.md:
    FD maturity with quarterly compounding = P * (1 + r/4)^(4 * years)
    where r = annual rate as a decimal, years = tenure_months / 12.0.
    
    Interest is taxable at slab rate; TDS applies above threshold (Sec 194A).
    Effective tax includes 4% Health & Education cess: tax_bracket * 1.04.
    Post-tax interest = interest * (1 - effective_tax_rate).
    """
    principal = float(principal)
    rate_pct = float(rate_pct)
    tenure_months = int(tenure_months)
    tax_bracket_pct = float(tax_bracket_pct)
    
    years = tenure_months / 12.0
    r = rate_pct / 100.0
    
    # Quarterly compounding
    # A = P * (1 + r/4)^(4*years)
    maturity_amount = principal * ((1.0 + r / 4.0) ** (4.0 * years))
    total_interest = maturity_amount - principal
    
    # Tax computation
    # 4% Health & Education cess on tax bracket
    effective_tax_rate = (tax_bracket_pct / 100.0) * 1.04
    tax_amount = total_interest * effective_tax_rate
    post_tax_interest = total_interest - tax_amount
    post_tax_maturity = principal + post_tax_interest
    
    # Annualized effective yield (APY)
    effective_yield_pct = (((maturity_amount / principal) ** (1.0 / years)) - 1.0) * 100.0 if years > 0 else rate_pct
    post_tax_yield_pct = (((post_tax_maturity / principal) ** (1.0 / years)) - 1.0) * 100.0 if years > 0 else rate_pct
    
    return {
        "principal": principal,
        "rate_pct": rate_pct,
        "tenure_months": tenure_months,
        "tenure_years": years,
        "tax_bracket_pct": tax_bracket_pct,
        "effective_tax_rate_pct": effective_tax_rate * 100.0,
        "maturity_amount": maturity_amount,
        "total_interest": total_interest,
        "tax_amount": tax_amount,
        "post_tax_interest": post_tax_interest,
        "post_tax_maturity": post_tax_maturity,
        "effective_yield_pct": effective_yield_pct,
        "post_tax_yield_pct": post_tax_yield_pct
    }


def calc_fd_ladder(total_amount: float, is_senior: bool = False, bank_type_filter: str = "All") -> dict:
    """
    FD Laddering:
    Splits total_amount equally into 1, 2, 3 and 5-year FDs at the best available rate
    for each tenure from data/fd-rates.csv.
    Compares to a single 5-year FD at the best 5-year rate.
    """
    df = get_fd_rates_df()
    if df.empty:
        return {}
    
    if bank_type_filter != "All":
        df_filtered = df[df["type"].str.lower() == bank_type_filter.lower()]
        if df_filtered.empty:
            df_filtered = df
    else:
        df_filtered = df
        
    rate_col = "rate_senior_pct" if is_senior else "rate_general_pct"
    
    tenures = [12, 24, 36, 60]
    bucket_amount = total_amount / 4.0
    buckets = []
    
    for t_m in tenures:
        sub = df_filtered[df_filtered["tenure_months"] == t_m]
        if sub.empty:
            sub = df[df["tenure_months"] == t_m]
        
        best_row = sub.sort_values(rate_col, ascending=False).iloc[0]
        best_rate = float(best_row[rate_col])
        bank_name = best_row["bank"]
        bank_type = best_row["type"]
        
        calc = calc_fd_maturity(bucket_amount, best_rate, t_m)
        buckets.append({
            "tenure_months": t_m,
            "tenure_years": t_m // 12,
            "bank": bank_name,
            "bank_type": bank_type,
            "rate_pct": best_rate,
            "principal": bucket_amount,
            "maturity_amount": calc["maturity_amount"],
            "interest": calc["total_interest"]
        })
        
    ladder_maturity_total = sum(b["maturity_amount"] for b in buckets)
    ladder_interest_total = sum(b["interest"] for b in buckets)
    blended_rate = sum(b["rate_pct"] for b in buckets) / 4.0
    
    # Single 5-year FD comparison
    sub_5y = df_filtered[df_filtered["tenure_months"] == 60]
    if sub_5y.empty:
        sub_5y = df[df["tenure_months"] == 60]
    best_5y_row = sub_5y.sort_values(rate_col, ascending=False).iloc[0]
    best_5y_rate = float(best_5y_row[rate_col])
    best_5y_bank = best_5y_row["bank"]
    
    single_5y_calc = calc_fd_maturity(total_amount, best_5y_rate, 60)
    
    return {
        "total_amount": total_amount,
        "is_senior": is_senior,
        "buckets": buckets,
        "ladder_maturity_total": ladder_maturity_total,
        "ladder_interest_total": ladder_interest_total,
        "blended_rate_pct": blended_rate,
        "single_5y": {
            "bank": best_5y_bank,
            "rate_pct": best_5y_rate,
            "maturity_amount": single_5y_calc["maturity_amount"],
            "interest": single_5y_calc["total_interest"]
        },
        "interest_diff": ladder_interest_total - single_5y_calc["total_interest"]
    }


def calc_fd_real_return(rate_pct: float, tax_bracket_pct: float, inflation_pct: float) -> dict:
    """
    Fisher equation for real return after tax:
    post_tax_rate = rate * (1 - (tax_bracket * 1.04))
    real_return = (1 + post_tax_rate) / (1 + inflation) - 1
    """
    r_nom = float(rate_pct) / 100.0
    t_eff = (float(tax_bracket_pct) / 100.0) * 1.04
    r_post = r_nom * (1.0 - t_eff)
    inf = float(inflation_pct) / 100.0
    
    r_real = ((1.0 + r_post) / (1.0 + inf)) - 1.0
    
    return {
        "nominal_rate_pct": rate_pct,
        "tax_bracket_pct": tax_bracket_pct,
        "effective_tax_pct": t_eff * 100.0,
        "post_tax_rate_pct": r_post * 100.0,
        "inflation_pct": inflation_pct,
        "real_return_pct": r_real * 100.0,
        "is_negative": r_real < 0.0
    }


# ==============================================================================
# 6. Mutual Fund Data & Functions (Module 3)
# ==============================================================================

def search_mutual_funds(query: str) -> dict:
    """
    Searches mutual fund schemes via https://api.mfapi.in/mf/search?q=<query>.
    Caches results for 15 minutes.
    Falls back to local search snapshot if offline.
    """
    q_clean = query.strip()
    if not q_clean:
        return {"data": [], "is_offline": False, "source_label": "api.mfapi.in", "error": None}
        
    cache_key = f"mf_search_{q_clean.lower()}"
    now_ts = time.time()
    
    if cache_key in _MEMORY_CACHE:
        entry = _MEMORY_CACHE[cache_key]
        if now_ts - entry["timestamp"] < CACHE_TTL_SECONDS:
            return entry["data"]
            
    snapshot_pattern = os.path.join(SNAPSHOTS_DIR, f"mf_search_{q_clean.lower()[:20]}_*.json")
    
    url = f"https://api.mfapi.in/mf/search?q={requests.utils.quote(q_clean)}"
    try:
        resp = requests.get(url, timeout=7)
        if resp.status_code == 200:
            results = resp.json()
            source_lbl = format_source_timestamp("api.mfapi.in", datetime.datetime.now())
            res_dict = {
                "data": results,
                "is_offline": False,
                "source_label": source_lbl,
                "error": None
            }
            _MEMORY_CACHE[cache_key] = {"data": res_dict, "timestamp": now_ts}
            
            # Save snapshot
            snap_file = os.path.join(SNAPSHOTS_DIR, f"mf_search_{q_clean.lower()[:20]}_{datetime.date.today().isoformat()}.json")
            try:
                with open(snap_file, "w", encoding="utf-8") as f:
                    json.dump(results, f)
            except Exception:
                pass
                
            return res_dict
    except Exception:
        pass
        
    # Offline fallback
    matches = glob.glob(snapshot_pattern)
    if matches:
        latest_snap = max(matches, key=os.path.getmtime)
        try:
            with open(latest_snap, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(latest_snap))
            offline_lbl = f"offline data from {format_date(file_mtime)}"
            res_dict = {
                "data": cached_data,
                "is_offline": True,
                "source_label": offline_lbl,
                "error": None
            }
            _MEMORY_CACHE[cache_key] = {"data": res_dict, "timestamp": now_ts}
            return res_dict
        except Exception:
            pass
            
    return {
        "data": [],
        "is_offline": True,
        "source_label": "offline",
        "error": "Unable to connect to the mutual fund data service. Please check your internet connection or try again shortly."
    }


def get_mutual_fund_details(scheme_code: int) -> dict:
    """
    Fetches full scheme details and historical NAVs from https://api.mfapi.in/mf/<scheme_code>.
    Caches for 15 minutes.
    Saves snapshot CSV to snapshots/mf_<scheme_code>_<date>.csv.
    Falls back to snapshot if offline.
    """
    code_str = str(scheme_code).strip()
    cache_key = f"mf_details_{code_str}"
    now_ts = time.time()
    
    if cache_key in _MEMORY_CACHE:
        entry = _MEMORY_CACHE[cache_key]
        if now_ts - entry["timestamp"] < CACHE_TTL_SECONDS:
            return entry["data"]
            
    snapshot_pattern = os.path.join(SNAPSHOTS_DIR, f"mf_{code_str}_*.csv")
    meta_pattern = os.path.join(SNAPSHOTS_DIR, f"mf_{code_str}_meta.json")
    
    url = f"https://api.mfapi.in/mf/{code_str}"
    try:
        resp = requests.get(url, timeout=9)
        if resp.status_code == 200:
            payload = resp.json()
            meta = payload.get("meta", {})
            raw_data = payload.get("data", [])
            
            if raw_data:
                df = pd.DataFrame(raw_data)
                df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
                df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
                df = df.dropna().sort_values("date").reset_index(drop=True)
                
                source_lbl = format_source_timestamp("api.mfapi.in", datetime.datetime.now())
                res_dict = {
                    "scheme_code": scheme_code,
                    "meta": meta,
                    "df": df,
                    "latest_nav": df.iloc[-1]["nav"] if not df.empty else None,
                    "latest_date": df.iloc[-1]["date"] if not df.empty else None,
                    "is_offline": False,
                    "source_label": source_lbl,
                    "error": None
                }
                _MEMORY_CACHE[cache_key] = {"data": res_dict, "timestamp": now_ts}
                
                # Save snapshot CSV and metadata
                today_str = datetime.date.today().isoformat()
                snap_csv = os.path.join(SNAPSHOTS_DIR, f"mf_{code_str}_{today_str}.csv")
                try:
                    df.to_csv(snap_csv, index=False)
                    with open(meta_pattern, "w", encoding="utf-8") as f:
                        json.dump(meta, f)
                except Exception:
                    pass
                    
                return res_dict
    except Exception:
        pass
        
    # Offline fallback
    matches = glob.glob(snapshot_pattern)
    if matches:
        latest_snap = max(matches, key=os.path.getmtime)
        try:
            df = pd.read_csv(latest_snap)
            df["date"] = pd.to_datetime(df["date"])
            df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
            df = df.dropna().sort_values("date").reset_index(drop=True)
            
            meta = {}
            if os.path.exists(meta_pattern):
                with open(meta_pattern, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    
            file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(latest_snap))
            offline_lbl = f"offline data from {format_date(file_mtime)}"
            
            res_dict = {
                "scheme_code": scheme_code,
                "meta": meta,
                "df": df,
                "latest_nav": df.iloc[-1]["nav"] if not df.empty else None,
                "latest_date": df.iloc[-1]["date"] if not df.empty else None,
                "is_offline": True,
                "source_label": offline_lbl,
                "error": None
            }
            _MEMORY_CACHE[cache_key] = {"data": res_dict, "timestamp": now_ts}
            return res_dict
        except Exception:
            pass
            
    return {
        "scheme_code": scheme_code,
        "meta": {},
        "df": pd.DataFrame(),
        "latest_nav": None,
        "latest_date": None,
        "is_offline": True,
        "source_label": "offline",
        "error": "Unable to connect to the mutual fund data service. Please check your internet connection or try again shortly."
    }


def calc_fund_cagrs(df: pd.DataFrame) -> dict:
    """
    Computes 1-year, 3-year, and 5-year CAGR from NAV history according to docs/finance-formulas.md:
    CAGR = (End / Start)^(1 / years) - 1
    """
    if df is None or df.empty or len(df) < 2:
        return {"1y": None, "3y": None, "5y": None}
        
    latest_row = df.iloc[-1]
    latest_date = latest_row["date"]
    latest_nav = latest_row["nav"]
    
    results = {}
    for yrs in [1, 3, 5]:
        target_date = latest_date - pd.DateOffset(years=yrs)
        sub = df[df["date"] <= target_date]
        if not sub.empty:
            start_row = sub.iloc[-1]
            days = (latest_date - start_row["date"]).days
            years_float = days / 365.25
            if years_float >= (yrs * 0.9):
                cagr = ((latest_nav / start_row["nav"]) ** (1.0 / years_float)) - 1.0
                results[f"{yrs}y"] = {
                    "cagr_pct": cagr * 100.0,
                    "start_date": start_row["date"],
                    "start_nav": start_row["nav"],
                    "end_date": latest_date,
                    "end_nav": latest_nav,
                    "years": years_float
                }
            else:
                results[f"{yrs}y"] = None
        else:
            results[f"{yrs}y"] = None
            
    return results


def calc_rolling_returns(df: pd.DataFrame, window_years: int = 3) -> dict:
    """
    Calculates 3-year rolling returns (CAGR of every 3-year window, stepped monthly).
    Returns rolling time series DataFrame and summary statistics (best, worst, median, average).
    """
    if df is None or df.empty:
        return {"df": pd.DataFrame(), "best": None, "worst": None, "median": None, "average": None}
        
    min_date = df["date"].min() + pd.DateOffset(years=window_years)
    max_date = df["date"].max()
    
    if min_date > max_date:
        return {"df": pd.DataFrame(), "best": None, "worst": None, "median": None, "average": None, "insufficient_history": True}
        
    eval_dates = pd.date_range(start=min_date, end=max_date, freq="MS")
    records = []
    
    for d in eval_dates:
        sub_end = df[df["date"] <= d]
        if sub_end.empty:
            continue
        end_row = sub_end.iloc[-1]
        
        target_start = end_row["date"] - pd.DateOffset(years=window_years)
        sub_start = df[df["date"] <= target_start]
        if sub_start.empty:
            continue
        start_row = sub_start.iloc[-1]
        
        yrs = (end_row["date"] - start_row["date"]).days / 365.25
        if yrs < (window_years * 0.9):
            continue
            
        cagr = ((end_row["nav"] / start_row["nav"]) ** (1.0 / yrs)) - 1.0
        records.append({
            "date": end_row["date"],
            "cagr_pct": cagr * 100.0,
            "start_nav": start_row["nav"],
            "end_nav": end_row["nav"]
        })
        
    rdf = pd.DataFrame(records)
    if rdf.empty:
        return {"df": pd.DataFrame(), "best": None, "worst": None, "median": None, "average": None}
        
    best_idx = rdf["cagr_pct"].idxmax()
    worst_idx = rdf["cagr_pct"].idxmin()
    
    best_row = rdf.loc[best_idx]
    worst_row = rdf.loc[worst_idx]
    median_val = float(rdf["cagr_pct"].median())
    avg_val = float(rdf["cagr_pct"].mean())
    positive_pct = float((rdf["cagr_pct"] > 0).mean() * 100.0)
    
    return {
        "df": rdf,
        "best": {"date": best_row["date"], "cagr_pct": float(best_row["cagr_pct"])},
        "worst": {"date": worst_row["date"], "cagr_pct": float(worst_row["cagr_pct"])},
        "median_pct": median_val,
        "average_pct": avg_val,
        "positive_windows_pct": positive_pct,
        "total_windows": len(rdf)
    }


def solve_xirr(cash_flows: list, dates: list, guess: float = 0.1, max_iter: int = 100, tol: float = 1e-6) -> float:
    """
    Solves for XIRR according to docs/finance-formulas.md:
    The rate that makes the net present value of dated cash flows zero (numeric solver).
    Uses Newton-Raphson with bisection fallback.
    """
    if len(cash_flows) < 2 or len(cash_flows) != len(dates):
        return 0.0
        
    d0 = dates[0]
    years = np.array([(d - d0).days / 365.25 for d in dates], dtype=float)
    cfs = np.array(cash_flows, dtype=float)
    
    # Check if there is both positive and negative cash flows
    if not (np.any(cfs > 0) and np.any(cfs < 0)):
        return 0.0
        
    r = guess
    for _ in range(max_iter):
        denom = (1.0 + r) ** years
        f = np.sum(cfs / denom)
        f_prime = np.sum(-cfs * years / ((1.0 + r) ** (years + 1.0)))
        if abs(f_prime) < 1e-12:
            break
        r_new = r - f / f_prime
        if abs(r_new - r) < tol:
            return float(r_new)
        r = r_new
        if r < -0.99:
            r = -0.99
            
    # Bisection fallback
    low, high = -0.99, 10.0
    for _ in range(100):
        mid = (low + high) / 2.0
        val = np.sum(cfs / ((1.0 + mid) ** years))
        if abs(val) < tol:
            return float(mid)
        val_low = np.sum(cfs / ((1.0 + low) ** years))
        if val * val_low < 0:
            high = mid
        else:
            low = mid
            
    return float(r)


def backtest_sip(df: pd.DataFrame, monthly_amount: float = 5000.0, start_date_str: str = "2021-01-01") -> dict:
    """
    SIP Back-test:
    Buys units on each month's first available trading day.
    Returns units held, invested amount, current value, absolute gain, gain %, and XIRR.
    Also returns month-by-month trajectory DataFrame for charting.
    """
    if df is None or df.empty:
        return {}
        
    start_date = pd.to_datetime(start_date_str)
    df_sip = df[df["date"] >= start_date].copy()
    if df_sip.empty:
        return {}
        
    latest_row = df_sip.iloc[-1]
    latest_date = latest_row["date"]
    latest_nav = float(latest_row["nav"])
    
    # First trading day of each month
    df_sip["year_month"] = df_sip["date"].dt.to_period("M")
    sip_entries = df_sip.groupby("year_month").first().reset_index()
    
    units_held = 0.0
    total_invested = 0.0
    cash_flows = []
    cf_dates = []
    trajectory = []
    
    for _, row in sip_entries.iterrows():
        nav = float(row["nav"])
        d = row["date"]
        units = monthly_amount / nav
        units_held += units
        total_invested += monthly_amount
        
        cash_flows.append(-monthly_amount)
        cf_dates.append(d.date())
        
        trajectory.append({
            "date": d,
            "nav": nav,
            "units_bought": units,
            "cumulative_units": units_held,
            "invested_amount": total_invested,
            "portfolio_value": units_held * nav
        })
        
    current_value = units_held * latest_nav
    abs_gain = current_value - total_invested
    abs_gain_pct = (abs_gain / total_invested * 100.0) if total_invested > 0 else 0.0
    
    # Terminal cash flow for XIRR
    xirr_cfs = list(cash_flows) + [current_value]
    xirr_dates = list(cf_dates) + [latest_date.date()]
    xirr_rate = solve_xirr(xirr_cfs, xirr_dates)
    
    traj_df = pd.DataFrame(trajectory)
    
    return {
        "monthly_amount": monthly_amount,
        "start_date": start_date,
        "latest_date": latest_date,
        "latest_nav": latest_nav,
        "installments_count": len(sip_entries),
        "total_units": units_held,
        "total_invested": total_invested,
        "current_value": current_value,
        "absolute_gain": abs_gain,
        "absolute_gain_pct": abs_gain_pct,
        "xirr_pct": xirr_rate * 100.0,
        "trajectory_df": traj_df
    }


def compare_funds(df1: pd.DataFrame, df2: pd.DataFrame, label1: str = "Fund 1", label2: str = "Fund 2") -> dict:
    """
    Rebases both NAV series to 100 on their common start date.
    Returns merged DataFrame with rebased values and CAGR comparison.
    """
    if df1 is None or df1.empty or df2 is None or df2.empty:
        return {}
        
    start1 = df1["date"].min()
    start2 = df2["date"].min()
    common_start = max(start1, start2)
    
    sub1 = df1[df1["date"] >= common_start].copy().sort_values("date")
    sub2 = df2[df2["date"] >= common_start].copy().sort_values("date")
    
    if sub1.empty or sub2.empty:
        return {}
        
    base_nav1 = sub1.iloc[0]["nav"]
    base_nav2 = sub2.iloc[0]["nav"]
    
    sub1["rebased_1"] = (sub1["nav"] / base_nav1) * 100.0
    sub2["rebased_2"] = (sub2["nav"] / base_nav2) * 100.0
    
    # Merge on date
    merged = pd.merge(sub1[["date", "rebased_1", "nav"]].rename(columns={"nav": "nav_1"}),
                      sub2[["date", "rebased_2", "nav"]].rename(columns={"nav": "nav_2"}),
                      on="date", how="outer").sort_values("date").reset_index(drop=True)
    merged["rebased_1"] = merged["rebased_1"].ffill()
    merged["rebased_2"] = merged["rebased_2"].ffill()
    merged = merged.dropna()
    
    cagrs1 = calc_fund_cagrs(df1)
    cagrs2 = calc_fund_cagrs(df2)
    
    return {
        "common_start_date": common_start,
        "merged_df": merged,
        "label1": label1,
        "label2": label2,
        "cagrs1": cagrs1,
        "cagrs2": cagrs2
    }


# ==============================================================================
# 7. Paper Trading Module (Module 4)
# ==============================================================================

def init_paper_trading_db():
    """Initializes SQLite tables for paper trading account, holdings, and trade log."""
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_account (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                display_name TEXT NOT NULL,
                cash_balance REAL NOT NULL DEFAULT 1000000.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_holdings (
                ticker TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_buy_price REAL NOT NULL,
                invested_value REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ticker TEXT NOT NULL,
                company_name TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                trade_value REAL NOT NULL,
                brokerage REAL NOT NULL,
                stt REAL NOT NULL,
                total_costs REAL NOT NULL,
                net_cash_flow REAL NOT NULL,
                realised_pnl REAL DEFAULT 0.0,
                market_status_note TEXT
            )
        """)
        # Ensure default account row exists
        row = conn.execute("SELECT * FROM paper_account WHERE id = 1").fetchone()
        if not row:
            conn.execute(
                "INSERT INTO paper_account (id, display_name, cash_balance) VALUES (1, ?, 1000000.0)",
                ("Trader",)
            )
    conn.close()


def get_paper_account() -> dict:
    """Returns current paper account details."""
    init_paper_trading_db()
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM paper_account WHERE id = 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"id": 1, "display_name": "Trader", "cash_balance": 1000000.0}


def set_paper_account_name(display_name: str) -> bool:
    """Updates the user's paper trading display name."""
    init_paper_trading_db()
    name_clean = display_name.strip()
    if not name_clean:
        return False
    conn = get_db_connection()
    with conn:
        conn.execute(
            "UPDATE paper_account SET display_name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (name_clean,)
        )
    conn.close()
    return True


def reset_paper_account() -> bool:
    """
    Resets account back to starting cash Rs 10,00,000,
    clearing all holdings and trade history.
    """
    init_paper_trading_db()
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE paper_account SET cash_balance = 1000000.0, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
        conn.execute("DELETE FROM paper_holdings")
        conn.execute("DELETE FROM paper_trades")
    conn.close()
    return True


def is_nse_market_open() -> tuple[bool, str, datetime.datetime]:
    """
    Checks if NSE is open in IST:
    Monday to Friday, 09:15 to 15:30 IST.
    Returns (is_open, note, current_ist).
    """
    tz_ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    now_ist = datetime.datetime.now(tz_ist)
    
    is_weekday = 0 <= now_ist.weekday() <= 4
    time_now = now_ist.time()
    market_open = datetime.time(9, 15)
    market_close = datetime.time(15, 30)
    
    is_open = is_weekday and (market_open <= time_now <= market_close)
    if is_open:
        note = "market open - live simulated fill"
    else:
        note = "market closed - filled at last close"
    return is_open, note, now_ist


def calc_trade_costs(price: float, quantity: int) -> dict:
    """
    Exact formulas from docs/finance-formulas.md:
    - Brokerage: Rs 20 or 0.03% per order, whichever is lower.
    - STT: 0.1% on delivery buy and sell.
    - Exchange charges and GST ignored for simplicity.
    """
    trade_value = round(float(price) * int(quantity), 2)
    brokerage = round(min(20.0, 0.0003 * trade_value), 2)
    stt = round(0.001 * trade_value, 2)
    total_costs = round(brokerage + stt, 2)
    return {
        "trade_value": trade_value,
        "brokerage": brokerage,
        "stt": stt,
        "total_costs": total_costs
    }


def execute_paper_trade(ticker: str, company_name: str, trade_type: str, quantity: int, price: float) -> tuple[bool, str, dict]:
    """
    Executes a BUY or SELL paper trade in SQLite:
    - Verifies cash availability for BUY
    - Verifies held quantity for SELL
    - Computes average-cost basis and realised P&L
    - Updates cash_balance, paper_holdings, and logs trade to paper_trades.
    """
    init_paper_trading_db()
    trade_type = trade_type.upper().strip()
    if trade_type not in ["BUY", "SELL"]:
        return False, "Invalid trade action. Only Buy or Sell is allowed.", {}
    if quantity <= 0:
        return False, "Quantity must be greater than zero.", {}
    if price <= 0:
        return False, "Invalid price for execution.", {}
        
    costs = calc_trade_costs(price, quantity)
    trade_value = costs["trade_value"]
    total_costs = costs["total_costs"]
    
    conn = get_db_connection()
    try:
        with conn:
            # Check Account Cash
            acct_row = conn.execute("SELECT cash_balance FROM paper_account WHERE id = 1").fetchone()
            cash_balance = acct_row["cash_balance"] if acct_row else 1000000.0
            
            # Check Holding
            hold_row = conn.execute("SELECT * FROM paper_holdings WHERE ticker = ?", (ticker,)).fetchone()
            held_qty = hold_row["quantity"] if hold_row else 0
            held_avg_price = hold_row["avg_buy_price"] if hold_row else 0.0
            held_invested = hold_row["invested_value"] if hold_row else 0.0
            
            _, market_note, _ = is_nse_market_open()
            
            if trade_type == "BUY":
                net_cash_flow = -(trade_value + total_costs)
                if cash_balance < (trade_value + total_costs):
                    return False, f"Insufficient cash balance. Required: {format_rupees(trade_value + total_costs)}, Available: {format_rupees(cash_balance)}.", {}
                    
                new_cash = cash_balance + net_cash_flow
                new_qty = held_qty + quantity
                new_invested = held_invested + trade_value
                new_avg_price = new_invested / new_qty
                
                # Update account
                conn.execute(
                    "UPDATE paper_account SET cash_balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
                    (new_cash,)
                )
                
                # Update holding
                if hold_row:
                    conn.execute("""
                        UPDATE paper_holdings 
                        SET quantity = ?, avg_buy_price = ?, invested_value = ?, company_name = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE ticker = ?
                    """, (new_qty, new_avg_price, new_invested, company_name, ticker))
                else:
                    conn.execute("""
                        INSERT INTO paper_holdings (ticker, company_name, quantity, avg_buy_price, invested_value)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ticker, company_name, new_qty, new_avg_price, new_invested))
                    
                # Log trade
                cursor = conn.execute("""
                    INSERT INTO paper_trades (
                        ticker, company_name, trade_type, quantity, price, trade_value,
                        brokerage, stt, total_costs, net_cash_flow, realised_pnl, market_status_note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, ?)
                """, (ticker, company_name, "BUY", quantity, price, trade_value,
                      costs["brokerage"], costs["stt"], total_costs, net_cash_flow, market_note))
                trade_id = cursor.lastrowid
                
                trade_info = {
                    "id": trade_id,
                    "trade_type": "BUY",
                    "ticker": ticker,
                    "quantity": quantity,
                    "price": price,
                    "trade_value": trade_value,
                    "costs": total_costs,
                    "net_cash_flow": net_cash_flow,
                    "realised_pnl": 0.0,
                    "market_note": market_note
                }
                return True, f"Bought {quantity} shares of {company_name} at {format_rupees(price)}.", trade_info
                
            elif trade_type == "SELL":
                if held_qty < quantity:
                    return False, f"You cannot sell more shares than you currently hold. Held: {held_qty}, Attempted to sell: {quantity}.", {}
                    
                net_cash_flow = trade_value - total_costs
                realised_pnl = quantity * (price - held_avg_price)
                
                new_cash = cash_balance + net_cash_flow
                new_qty = held_qty - quantity
                
                # Update account
                conn.execute(
                    "UPDATE paper_account SET cash_balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
                    (new_cash,)
                )
                
                # Update holding
                if new_qty == 0:
                    conn.execute("DELETE FROM paper_holdings WHERE ticker = ?", (ticker,))
                else:
                    new_invested = new_qty * held_avg_price
                    conn.execute("""
                        UPDATE paper_holdings 
                        SET quantity = ?, invested_value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE ticker = ?
                    """, (new_qty, new_invested, ticker))
                    
                # Log trade
                cursor = conn.execute("""
                    INSERT INTO paper_trades (
                        ticker, company_name, trade_type, quantity, price, trade_value,
                        brokerage, stt, total_costs, net_cash_flow, realised_pnl, market_status_note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (ticker, company_name, "SELL", quantity, price, trade_value,
                      costs["brokerage"], costs["stt"], total_costs, net_cash_flow, realised_pnl, market_note))
                trade_id = cursor.lastrowid
                
                trade_info = {
                    "id": trade_id,
                    "trade_type": "SELL",
                    "ticker": ticker,
                    "quantity": quantity,
                    "price": price,
                    "trade_value": trade_value,
                    "costs": total_costs,
                    "net_cash_flow": net_cash_flow,
                    "realised_pnl": realised_pnl,
                    "market_note": market_note
                }
                return True, f"Sold {quantity} shares of {company_name} at {format_rupees(price)}. Realised profit or loss: {format_rupees(realised_pnl)}.", trade_info
    finally:
        conn.close()


def get_paper_holdings_summary() -> dict:
    """
    Returns full holdings details with current prices, valuations, unrealised P&L,
    cash balance, total account value, and overall return %.
    """
    init_paper_trading_db()
    acct = get_paper_account()
    cash_balance = acct["cash_balance"]
    
    conn = get_db_connection()
    holdings_rows = conn.execute("SELECT * FROM paper_holdings ORDER BY invested_value DESC").fetchall()
    conn.close()
    
    if not holdings_rows:
        return {
            "cash_balance": cash_balance,
            "holdings": [],
            "total_invested": 0.0,
            "total_current_value": 0.0,
            "total_unrealised_pnl": 0.0,
            "total_account_value": cash_balance,
            "overall_return_pct": ((cash_balance - 1000000.0) / 1000000.0) * 100.0
        }
        
    tickers = [r["ticker"] for r in holdings_rows]
    quotes, _, _ = get_batch_quotes(tickers)
    
    holdings_list = []
    total_invested = 0.0
    total_current_value = 0.0
    
    for r in holdings_rows:
        tkr = r["ticker"]
        qty = r["quantity"]
        avg_price = r["avg_buy_price"]
        invested = r["invested_value"]
        
        q = quotes.get(tkr, {})
        last_price = q.get("price") if q and q.get("price") is not None else avg_price
        curr_val = qty * last_price
        unrealised = curr_val - invested
        unrealised_pct = (unrealised / invested * 100.0) if invested > 0 else 0.0
        
        total_invested += invested
        total_current_value += curr_val
        
        holdings_list.append({
            "ticker": tkr,
            "company_name": r["company_name"],
            "quantity": qty,
            "avg_buy_price": avg_price,
            "last_price": last_price,
            "invested_value": invested,
            "current_value": curr_val,
            "unrealised_pnl": unrealised,
            "unrealised_pnl_pct": unrealised_pct
        })
        
    total_unrealised = total_current_value - total_invested
    total_account_val = cash_balance + total_current_value
    overall_return_pct = ((total_account_val - 1000000.0) / 1000000.0) * 100.0
    
    return {
        "cash_balance": cash_balance,
        "holdings": holdings_list,
        "total_invested": total_invested,
        "total_current_value": total_current_value,
        "total_unrealised_pnl": total_unrealised,
        "total_account_value": total_account_val,
        "overall_return_pct": overall_return_pct
    }


def get_paper_trade_log() -> pd.DataFrame:
    """Returns trade history as a DataFrame with totals."""
    init_paper_trading_db()
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM paper_trades ORDER BY id DESC", conn)
    conn.close()
    return df


def get_paper_reconciliation() -> dict:
    """
    Verifies the non-negotiable arithmetic identity:
    cash + current value of holdings - Rs 10,00,000 == realised P&L + unrealised P&L - total costs
    """
    summary = get_paper_holdings_summary()
    trade_log = get_paper_trade_log()
    
    cash = summary["cash_balance"]
    current_value = summary["total_current_value"]
    account_value = summary["total_account_value"]
    net_profit = account_value - 1000000.0
    
    total_realised = float(trade_log["realised_pnl"].sum()) if not trade_log.empty else 0.0
    total_costs = float(trade_log["total_costs"].sum()) if not trade_log.empty else 0.0
    total_unrealised = summary["total_unrealised_pnl"]
    
    reconciled_sum = total_realised + total_unrealised - total_costs
    difference = abs(net_profit - reconciled_sum)
    is_balanced = difference < 0.01
    
    return {
        "cash_balance": cash,
        "current_value": current_value,
        "starting_cash": 1000000.0,
        "net_profit": net_profit,
        "total_realised_pnl": total_realised,
        "total_unrealised_pnl": total_unrealised,
        "total_costs": total_costs,
        "reconciled_sum": reconciled_sum,
        "difference": difference,
        "is_balanced": is_balanced
    }


def get_paper_vs_nifty() -> dict:
    """
    Computes comparative performance:
    Recomputes daily total account value since first trade date D0,
    benchmarked against Rs 10,00,000 invested in Nifty 50 (^NSEI) on D0.
    """
    trade_log = get_paper_trade_log()
    if trade_log.empty:
        return {"has_trades": False}
        
    first_trade_ts = pd.to_datetime(trade_log["timestamp"].min())
    first_trade_date = first_trade_ts.date()
    
    nifty_df, _, _, _ = get_daily_history("^NSEI", "1y")
    if nifty_df is None or nifty_df.empty:
        nifty_df, _, _, _ = get_daily_history("^NSEI", "5y")
        
    summary = get_paper_holdings_summary()
    current_acct_val = summary["total_account_value"]
    
    if nifty_df is None or nifty_df.empty:
        return {
            "has_trades": True,
            "first_trade_date": first_trade_date,
            "chart_df": pd.DataFrame(),
            "current_acct_val": current_acct_val,
            "current_nifty_val": 1000000.0,
            "ahead_amount": current_acct_val - 1000000.0,
            "is_portfolio_ahead": current_acct_val >= 1000000.0
        }
        
    nifty_sub = nifty_df[nifty_df.index.date >= first_trade_date].copy()
    if nifty_sub.empty:
        nifty_sub = nifty_df.iloc[-1:].copy()
        
    n0 = float(nifty_sub.iloc[0]["Close"])
    nifty_units = 1000000.0 / n0 if n0 > 0 else 1.0
    
    dates = []
    portfolio_vals = []
    nifty_vals = []
    
    trades_asc = trade_log.sort_values("id").to_dict("records")
    
    # Pre-fetch historical prices for distinct held tickers
    unique_tickers = list(trade_log["ticker"].unique())
    hist_prices = {}
    for tk in unique_tickers:
        h_df, _, _, _ = get_daily_history(tk, "1y")
        if h_df is not None and not h_df.empty:
            hist_prices[tk] = {idx.date(): float(c) for idx, c in zip(h_df.index, h_df["Close"])}
        else:
            hist_prices[tk] = {}
            
    last_trade_prices = {t["ticker"]: float(t["price"]) for t in trades_asc}
    
    for idx_date, row in nifty_sub.iterrows():
        d = idx_date.date()
        n_val = float(row["Close"]) * nifty_units
        
        sub_trades = [t for t in trades_asc if pd.to_datetime(t["timestamp"]).date() <= d]
        c_bal = 1000000.0 + sum(t["net_cash_flow"] for t in sub_trades)
        
        h_dict = {}
        for t in sub_trades:
            tk = t["ticker"]
            if t["trade_type"] == "BUY":
                h_dict[tk] = h_dict.get(tk, 0) + t["quantity"]
            else:
                h_dict[tk] = h_dict.get(tk, 0) - t["quantity"]
                
        if d == nifty_sub.index[-1].date():
            port_val = current_acct_val
        else:
            holdings_val_on_d = 0.0
            for tk, qty in h_dict.items():
                if qty > 0:
                    p_on_d = hist_prices.get(tk, {}).get(d)
                    if p_on_d is None:
                        prior_dates = [dt for dt in hist_prices.get(tk, {}) if dt <= d]
                        if prior_dates:
                            p_on_d = hist_prices[tk][max(prior_dates)]
                        else:
                            p_on_d = last_trade_prices.get(tk, 0.0)
                    holdings_val_on_d += qty * p_on_d
            port_val = c_bal + holdings_val_on_d
            
        dates.append(pd.to_datetime(d))
        portfolio_vals.append(port_val)
        nifty_vals.append(n_val)
        
    chart_df = pd.DataFrame({
        "date": dates,
        "My Portfolio": portfolio_vals,
        "Nifty 50 (Rs 10 Lakh Invested)": nifty_vals
    }).set_index("date")
    
    current_nifty_val = nifty_vals[-1] if nifty_vals else 1000000.0
    ahead_amount = current_acct_val - current_nifty_val
    is_portfolio_ahead = ahead_amount >= 0.0
    
    return {
        "has_trades": True,
        "first_trade_date": first_trade_date,
        "chart_df": chart_df,
        "current_acct_val": current_acct_val,
        "current_nifty_val": current_nifty_val,
        "ahead_amount": abs(ahead_amount),
        "is_portfolio_ahead": is_portfolio_ahead
    }


# ==============================================================================
# 9. Module 5: Portfolio Analytics & Risk Metrics
# ==============================================================================

LEADERBOARD_CSV_PATH = os.path.join(BASE_DIR, "leaderboard.csv")

def get_ticker_sector_map() -> dict:
    """
    Loads sector mapping from data/nifty50-symbols.csv (read-only).
    Returns mapping from symbol / ticker to sector.
    """
    sector_map = {}
    if os.path.exists(NIFTY50_CSV_PATH):
        try:
            df = pd.read_csv(NIFTY50_CSV_PATH)
            for _, row in df.iterrows():
                sec = str(row.get("sector", "Other")).strip()
                sym = str(row.get("symbol", "")).strip().upper()
                ytick = str(row.get("yahoo_ticker", "")).strip().upper()
                if sym:
                    sector_map[sym] = sec
                if ytick:
                    sector_map[ytick] = sec
        except Exception:
            pass
    return sector_map


def get_portfolio_allocation() -> dict:
    """
    Returns asset and sector allocation breakdowns:
    1. By Company: Cash slice + each holding current value
    2. By Sector: Cash slice + holdings grouped by sector ('Other' if not in symbols file)
    """
    summary = get_paper_holdings_summary()
    cash_bal = max(0.0, float(summary["cash_balance"]))
    total_val = float(summary["total_account_value"])
    if total_val <= 0:
        total_val = 1000000.0

    sector_map = get_ticker_sector_map()
    
    # 1. Company breakdown
    company_data = []
    # Cash slice
    cash_pct = (cash_bal / total_val) * 100.0
    company_data.append({
        "label": "Cash",
        "ticker": "CASH",
        "value": cash_bal,
        "percentage": cash_pct,
        "is_cash": True
    })
    
    # Holdings slices
    for h in summary["holdings"]:
        curr_val = max(0.0, float(h["current_value"]))
        pct = (curr_val / total_val) * 100.0
        company_data.append({
            "label": h["company_name"],
            "ticker": h["ticker"],
            "value": curr_val,
            "percentage": pct,
            "is_cash": False
        })
        
    company_df = pd.DataFrame(company_data)
    
    # 2. Sector breakdown
    sector_totals = {"Cash": cash_bal}
    for h in summary["holdings"]:
        curr_val = max(0.0, float(h["current_value"]))
        clean_tk = str(h["ticker"]).upper().replace(".NS", "").replace(".BO", "")
        sector = sector_map.get(clean_tk, sector_map.get(str(h["ticker"]).upper(), "Other"))
        sector_totals[sector] = sector_totals.get(sector, 0.0) + curr_val
        
    sector_data = []
    for sec, val in sector_totals.items():
        pct = (val / total_val) * 100.0
        sector_data.append({
            "sector": sec,
            "value": val,
            "percentage": pct,
            "is_cash": (sec == "Cash")
        })
    sector_df = pd.DataFrame(sector_data)
    
    return {
        "company_df": company_df,
        "sector_df": sector_df,
        "total_account_value": total_val,
        "cash_balance": cash_bal,
        "holdings_count": len(summary["holdings"])
    }


def get_portfolio_xirr() -> dict:
    """
    Computes XIRR of the whole account according to docs/finance-formulas.md:
    Cash flows:
    - Every BUY trade: negative outflow (-abs(net_cash_flow))
    - Every SELL trade: positive inflow (+abs(net_cash_flow))
    - Today's account value: positive terminal value (+total_account_value)
    
    Displays dated cash-flow table and numeric solver result.
    If fewer than 1 trade or trades all occurred today, returns informative explanation.
    """
    trade_log = get_paper_trade_log()
    summary = get_paper_holdings_summary()
    today_dt = datetime.date.today()
    total_val = float(summary["total_account_value"])
    
    if trade_log.empty:
        return {
            "has_xirr": False,
            "xirr_pct": None,
            "message": "No trades executed yet. XIRR will be calculated once you execute your first trade and hold account value.",
            "cash_flows_df": pd.DataFrame()
        }
        
    # Sort chronological
    trades_asc = trade_log.sort_values("id", ascending=True)
    
    cf_dates = []
    cf_amounts = []
    display_rows = []
    
    for _, t in trades_asc.iterrows():
        t_date = pd.to_datetime(t["timestamp"]).date()
        is_buy = (t["trade_type"] == "BUY")
        amt = -abs(float(t["net_cash_flow"])) if is_buy else abs(float(t["net_cash_flow"]))
        
        cf_dates.append(t_date)
        cf_amounts.append(amt)
        display_rows.append({
            "Date": format_date(t_date),
            "raw_date": t_date,
            "Type": "Buy Stock" if is_buy else "Sell Stock",
            "Description": f"{t['trade_type']} {t['quantity']} {t['ticker']} @ {format_rupees(t['price'])}",
            "Cash Flow": amt,
            "Amount": format_rupees(abs(amt)),
            "Direction": "Outflow (-)" if is_buy else "Inflow (+)"
        })
        
    # Terminal cash flow: today's account value
    cf_dates.append(today_dt)
    cf_amounts.append(total_val)
    display_rows.append({
        "Date": format_date(today_dt),
        "raw_date": today_dt,
        "Type": "Current Portfolio Value",
        "Description": "Total Account Valuation (Cash + Holdings)",
        "Cash Flow": total_val,
        "Amount": format_rupees(total_val),
        "Direction": "Terminal Valuation (+)"
    })
    
    cash_flows_df = pd.DataFrame(display_rows)
    
    # Check elapsed time:
    min_date = min(cf_dates)
    max_date = max(cf_dates)
    days_elapsed = (max_date - min_date).days
    
    if days_elapsed == 0:
        # All cash flows on same day -> annualised XIRR cannot be computed
        overall_ret = float(summary["overall_return_pct"])
        return {
            "has_xirr": False,
            "xirr_pct": None,
            "message": f"All trades were executed today ({format_date(min_date)}). Annualised XIRR requires at least 1 day between cash flows. Your same-day account return is {overall_ret:+.2f}%.",
            "cash_flows_df": cash_flows_df,
            "same_day": True,
            "return_pct": overall_ret
        }
        
    try:
        xirr_rate = solve_xirr(cf_amounts, cf_dates)
        xirr_pct = xirr_rate * 100.0
        # Sanity check bounded
        if np.isnan(xirr_pct) or np.isinf(xirr_pct) or abs(xirr_pct) > 10000.0:
            return {
                "has_xirr": False,
                "xirr_pct": None,
                "message": "Numeric solver could not determine a stable XIRR for the current cash flow pattern.",
                "cash_flows_df": cash_flows_df
            }
        return {
            "has_xirr": True,
            "xirr_pct": xirr_pct,
            "message": f"Annualised XIRR is {xirr_pct:+.2f}%.",
            "cash_flows_df": cash_flows_df
        }
    except Exception as e:
        return {
            "has_xirr": False,
            "xirr_pct": None,
            "message": f"Unable to calculate XIRR: {str(e)}",
            "cash_flows_df": cash_flows_df
        }


def get_portfolio_risk_metrics() -> dict:
    """
    Computes portfolio risk metrics using daily account values from Module 4 'versus Nifty' series:
    1. Annualised Volatility = standard deviation of daily returns * sqrt(252)
    2. Maximum Drawdown = largest peak-to-trough fall in portfolio value (%), with peak and trough dates
    3. Beta = covariance(portfolio daily returns, Nifty 50 daily returns) / variance(Nifty 50 daily returns)
    """
    vs_res = get_paper_vs_nifty()
    if not vs_res.get("has_trades"):
        return {
            "status": "empty",
            "message": "No trade history available yet to calculate risk metrics.",
            "volatility_pct": None,
            "max_drawdown_pct": None,
            "peak_date": None,
            "trough_date": None,
            "beta": None,
            "data_points": 0
        }
        
    chart_df = vs_res.get("chart_df")
    if chart_df is None or chart_df.empty:
        return {
            "status": "insufficient_history",
            "message": "Insufficient daily history: At least two trading days of portfolio valuations are required.",
            "volatility_pct": None,
            "max_drawdown_pct": None,
            "peak_date": None,
            "trough_date": None,
            "beta": None,
            "data_points": 0
        }
        
    # Series of portfolio values and nifty values
    p_vals = chart_df["My Portfolio"].values.astype(float)
    n_vals = chart_df["Nifty 50 (Rs 10 Lakh Invested)"].values.astype(float)
    dates = list(chart_df.index)
    
    n_points = len(p_vals)
    
    # 1. Max Drawdown
    if n_points >= 1:
        running_peak = p_vals[0]
        peak_idx = 0
        max_dd = 0.0
        best_peak_idx = 0
        best_trough_idx = 0
        
        for i in range(len(p_vals)):
            val = p_vals[i]
            if val > running_peak:
                running_peak = val
                peak_idx = i
            dd = ((running_peak - val) / running_peak) * 100.0 if running_peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
                best_peak_idx = peak_idx
                best_trough_idx = i
                
        peak_date = dates[best_peak_idx] if best_peak_idx < len(dates) else dates[0]
        trough_date = dates[best_trough_idx] if best_trough_idx < len(dates) else dates[0]
        max_drawdown_pct = max_dd
    else:
        max_drawdown_pct = None
        peak_date = None
        trough_date = None
        
    # 2. Daily returns for Volatility and Beta
    if n_points < 2:
        return {
            "status": "insufficient_history",
            "message": "Insufficient history: Only 1 daily valuation checkpoint is available. Volatility and Beta require at least two daily points.",
            "volatility_pct": None,
            "max_drawdown_pct": max_drawdown_pct,
            "peak_date": peak_date,
            "trough_date": trough_date,
            "beta": None,
            "data_points": n_points
        }
        
    # Calculate daily returns
    p_returns = np.diff(p_vals) / p_vals[:-1]
    n_returns = np.diff(n_vals) / n_vals[:-1]
    
    # Volatility = std(R) * sqrt(252)
    p_std = float(np.std(p_returns, ddof=1)) if len(p_returns) > 1 else float(np.std(p_returns))
    volatility_pct = float(p_std * np.sqrt(252) * 100.0)
    
    # Beta = cov(R_p, R_n) / var(R_n)
    n_var = float(np.var(n_returns, ddof=1)) if len(n_returns) > 1 else float(np.var(n_returns))
    if n_var > 1e-12:
        if len(p_returns) > 1:
            cov = float(np.cov(p_returns, n_returns)[0, 1])
        else:
            cov = float((p_returns[0] - np.mean(p_returns)) * (n_returns[0] - np.mean(n_returns)))
        beta = float(cov / n_var)
    else:
        beta = 1.0 if volatility_pct > 0 else 0.0
        
    return {
        "status": "ok",
        "message": f"Calculated from {n_points} daily valuation checkpoints.",
        "volatility_pct": volatility_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "peak_date": peak_date,
        "trough_date": trough_date,
        "beta": beta,
        "data_points": n_points
    }


def get_portfolio_concentration() -> dict:
    """
    Computes single-holding concentration:
    - Largest holding as % of total account
    - Flag if any single company is above 25%
    """
    summary = get_paper_holdings_summary()
    total_val = float(summary["total_account_value"])
    holdings = summary["holdings"]
    
    if not holdings or total_val <= 0:
        return {
            "has_holdings": False,
            "largest_name": "Cash",
            "largest_ticker": "CASH",
            "largest_value": float(summary["cash_balance"]),
            "largest_weight_pct": 100.0,
            "is_above_25": False,
            "note": "Your portfolio is currently 100.00% cash with no individual stock exposure."
        }
        
    largest = max(holdings, key=lambda h: float(h["current_value"]))
    weight = (float(largest["current_value"]) / total_val) * 100.0
    is_above = weight > 25.0
    
    if is_above:
        note = f"Concentration alert: {largest['company_name']} ({largest['ticker']}) represents {weight:.2f}% of your total portfolio, exceeding the 25.00% safety threshold."
    else:
        note = f"Healthy diversification: Your largest equity position is {largest['company_name']} ({largest['ticker']}) at {weight:.2f}% of your total account, safely within the 25.00% concentration threshold."
        
    return {
        "has_holdings": True,
        "largest_name": largest["company_name"],
        "largest_ticker": largest["ticker"],
        "largest_value": float(largest["current_value"]),
        "largest_weight_pct": weight,
        "is_above_25": is_above,
        "note": note
    }


def share_to_leaderboard(name: str | None = None, date_str: str | None = None) -> tuple[bool, str]:
    """
    Writes one row to leaderboard.csv at the top of the project:
    name,date,account_value,return_pct,xirr_pct,max_drawdown_pct
    """
    try:
        acct = get_paper_account()
        trader_name = name.strip() if name and name.strip() else acct.get("display_name", "Student Trader")
        # Strip quotes and commas from name
        trader_name = trader_name.replace('"', '').replace(',', ' ')
        summary = get_paper_holdings_summary()
        account_val = float(summary["total_account_value"])
        return_pct = float(summary["overall_return_pct"])
        
        # XIRR
        xirr_res = get_portfolio_xirr()
        if xirr_res.get("has_xirr") and xirr_res.get("xirr_pct") is not None:
            xirr_str = f"{xirr_res['xirr_pct']:.2f}%"
        elif xirr_res.get("same_day"):
            xirr_str = f"{xirr_res['return_pct']:.2f}% (same day)"
        else:
            xirr_str = "insufficient history"
            
        # Risk / Max Drawdown
        risk_res = get_portfolio_risk_metrics()
        mdd_num = risk_res.get("max_drawdown_pct")
        if mdd_num is not None and mdd_num > 0:
            mdd_str = f"-{mdd_num:.2f}%"
        else:
            mdd_str = "0.00%"
            
        if not date_str:
            date_str = format_date(datetime.date.today())
            
        # Write to leaderboard.csv at the top of the project
        file_exists = os.path.exists(LEADERBOARD_CSV_PATH)
        with open(LEADERBOARD_CSV_PATH, "a", encoding="utf-8") as f:
            if not file_exists or os.path.getsize(LEADERBOARD_CSV_PATH) == 0:
                f.write("name,date,account_value,return_pct,xirr_pct,max_drawdown_pct\n")
            f.write(f'"{trader_name}",{date_str},{account_val:.2f},{return_pct:.2f},"{xirr_str}","{mdd_str}"\n')
            
        return True, f"Successfully recorded score for {trader_name} to leaderboard.csv."
    except Exception as e:
        return False, f"Could not share score to leaderboard: {str(e)}"


def get_leaderboard_df() -> pd.DataFrame:
    """
    Reads leaderboard.csv from the project root and ranks by return_pct descending.
    """
    if not os.path.exists(LEADERBOARD_CSV_PATH) or os.path.getsize(LEADERBOARD_CSV_PATH) == 0:
        return pd.DataFrame(columns=["rank", "name", "date", "account_value", "return_pct", "xirr_pct", "max_drawdown_pct"])
        
    try:
        df = pd.read_csv(LEADERBOARD_CSV_PATH)
        if "return_pct" in df.columns:
            # Clean numeric
            df["return_num"] = pd.to_numeric(df["return_pct"], errors="coerce").fillna(0.0)
            df = df.sort_values("return_num", ascending=False).reset_index(drop=True)
            df["rank"] = df.index + 1
            df = df.drop(columns=["return_num"])
            # Order columns
            cols = ["rank", "name", "date", "account_value", "return_pct", "xirr_pct", "max_drawdown_pct"]
            existing_cols = [c for c in cols if c in df.columns]
            return df[existing_cols]
        return df
    except Exception:
        return pd.DataFrame(columns=["rank", "name", "date", "account_value", "return_pct", "xirr_pct", "max_drawdown_pct"])


