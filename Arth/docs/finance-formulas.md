# Finance formulas the platform must use (for the agent and for the student)

All rates are annual unless stated. r = annual rate as a decimal. n = number of periods.

- EMI = P * i * (1+i)^n / ((1+i)^n - 1), where i = r/12 and n = months.
- SIP future value (monthly, invested at the start of each month) = A * ((1+i)^n - 1) / i * (1+i).
- Step-up SIP: the monthly amount rises by s% every 12 months; sum each month's contribution compounded to the end.
- Lump sum future value = P * (1+r)^t.
- Inflation-adjusted (real) value = nominal / (1+inflation)^t.
- Retirement corpus at retirement = annual expense in the first retirement year * (1 - (1+g)^-N) / g, where g = (1+post-retirement return)/(1+inflation) - 1 and N = years in retirement.
- FD maturity with quarterly compounding = P * (1 + r/4)^(4*years). Interest is taxable at slab rate; TDS applies above the threshold.
- CAGR = (End / Start)^(1/years) - 1.
- XIRR: the rate that makes the net present value of dated cash flows zero (use a numeric solver).
- Volatility (annualised) = standard deviation of daily returns * sqrt(252).
- Max drawdown = largest peak-to-trough fall in portfolio value, as a percentage of the peak.
- Beta = covariance(portfolio daily returns, Nifty 50 daily returns) / variance(Nifty 50 daily returns).
- Brokerage simulation for paper trading: Rs 20 or 0.03% per order, whichever is lower (discount-broker style); STT 0.1% on delivery buy and sell; ignore exchange charges and GST for simplicity, and say so on screen.
