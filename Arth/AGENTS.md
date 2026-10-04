# AGENTS.md — Standing Rules for Arth Development

All agents and contributors working on Arth must strictly adhere to the following standing rules across all tasks.

---

### Rule 1: Reference Documentation & Formulas
- Read `docs/house-style.md` and `docs/finance-formulas.md` before any task and follow them exactly.
- Every financial calculator must implement the exact mathematical formula defined in `finance-formulas.md`.
- Every calculator must display its formula on-screen in an expandable section titled: **"How this is calculated"**.

---

### Rule 2: Immutability of Reference Data and Docs
- **Never edit, move, or delete** any files or subdirectories inside `data/` or `docs/`.
- Treat these folders strictly as **read-only**.

---

### Rule 3: Single Streamlit Application Architecture
- The platform consists of a single Streamlit application in this folder:
  - `app.py` (entry point / Home)
  - `pages/` (multi-page application directory)
  - `arth.db` (single SQLite database file)
  - A small centralized data layer module that every page uses.
- **Strict Boundaries**:
  - No additional framework.
  - No user accounts or login flows.
  - No payment gateways.
  - No external services beyond:
    - Yahoo Finance (`yfinance`)
    - `api.mfapi.in` (Mutual fund NAVs)

---

### Rule 4: Data Fetching, Caching & Offline Fallbacks
- Every number fetched from the internet must be **cached for 15 minutes**.
- Every fetched figure must visibly state its source and timestamp on screen (e.g., `"Yahoo Finance, 1 Oct 2026 15:30 IST, delayed"`).
- A daily snapshot of every fetched price must be saved to `snapshots/`.
- If an internet source fails or is unreachable, the system must automatically fall back to the latest snapshot in `snapshots/` and display a visible note:
  `"offline data from <date>"`.

---

### Rule 5: Formatting & Localization Standards
- **Rupees**: Formatted with Indian digit grouping and two decimal places (e.g., `Rs 12,34,567.89`). Use Lakh and Crore in narrative text (e.g., `Rs 12.3 lakh`).
- **Dates**: Format strictly as `1 Oct 2026`. Financial years written as `FY 2026-27`.
- **Percentages**: Format to two decimal places (e.g., `12.34%`).

---

### Rule 6: Error Handling & User Experience
- **Never display** raw JSON, code snippets, stack traces, or technical error logs on screen.
- User-facing error messages must consist of **one plain sentence and a suggestion**.

---

### Rule 7: Mandatory Educational Disclosure
- Every screen and page must conclude with the exact footer line:
  > `"Arth is a learning platform. Nothing here is investment advice."`

---

### Rule 8: Cumulative Extension Rule
- When a later prompt extends the platform, **never remove or break** what an earlier prompt built; extend it.
