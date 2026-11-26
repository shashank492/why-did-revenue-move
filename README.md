<img width="1395" height="722" alt="Screenshot 2026-11-26 110025" src="https://github.com/user-attachments/assets/9a9ed089-d47c-4b79-b475-215c094e704b" />
# Why Did Revenue Move?

An AI analyst that explains **why** revenue changed between months, and **checks its own numbers**.

**Live app:** [https://why-did-revenue-move-djyswkuhmthrqzug75vn2z.streamlit.app/]  |  **Demo video (2 min):** [PASTE VIDEO LINK]

[Dashboard]("C:\Users\shash\OneDrive\Pictures\Screenshots\Screenshot 2026-11-26 105952.png")

## The business problem
Managers see "revenue went up £133K" and ask the same follow-up: *why, and what should we do?*
Revenue = customers × orders per customer × average order value, and each driver needs a different action:

| Driver | Business lever |
|---|---|
| Customers | Marketing and acquisition |
| Orders per customer | Retention and loyalty |
| Average order value | Pricing and product mix |

This app splits any monthly change into those three drivers, shows which countries and products moved most, and lets a manager ask follow-up questions in plain English.

## Example finding (Oct to Nov 2010)
Revenue rose **£133,348 (+12.9%)**. More customers added £77,886 and more orders per customer added £134,079, while a lower average order value took away £78,617. The UK made up £102,110 of the growth, and repeat customers brought about 87% of November revenue. Growth came from buying frequency and traffic, not bigger baskets, which also fits the holiday season.

## How the AI is used safely
- **The AI never calculates.** It only picks one of 4 tested SQL/Python functions, and the code returns the numbers.
- **Every answer is audited.** A checker compares each number in the AI's answer with the function results. Match gives a green *Verified* badge, a mismatch gives a warning.
- **Traceable.** A "How I got this" panel shows the exact function calls and results.
- **Handles wrong assumptions.** Asked "why did revenue drop in Nov 2011?", it replies that revenue actually rose.
- **Handles outages.** If one AI model is overloaded, the app tries backup models.

[Verified answer](<img width="1395" height="722" alt="Screenshot 2026-11-26 110025" src="https://github.com/user-attachments/assets/9a9ed089-d47c-4b79-b475-215c094e704b" />)
[Checker warning]("C:\Users\shash\OneDrive\Pictures\Screenshots\Screenshot 2026-11-26 110131.png")

## Tech stack
Python, pandas, DuckDB (SQL), Streamlit, Google Gemini API (function calling).

## Data and cleaning decisions
Source: UCI Machine Learning Repository, *Online Retail II* (UK online gift retailer, Dec 2009 to Dec 2011). Please check the licence on the UCI page.
1,067,371 raw rows became 779,425 clean rows.

| Issue | Decision | Why |
|---|---|---|
| Cancelled invoices (start with "C") | Removed | Report sales revenue |
| Zero or negative quantity or price | Removed | Returns, adjustments, test rows |
| Blank customer ID (about 23% of rows) | Removed | The 3-driver split needs customers |
| Duplicate rows | Removed | Avoid double counting |
| Non-product lines (manual, postage, fees) | Excluded from product rankings | They are not products |

## Limitations (known)
- "Revenue" means sales from identified customers, excluding cancellations.
- "New customer" means first purchase in this dataset, so early months overstate new customers.
- Dec 2011 is a partial month and is flagged in the app.
- Totals use unrounded revenue, so they can differ by £1 from displayed figures.
- The checker catches wrong or invented numbers, not wrong reasoning.
- If a backup AI model answers, it does not remember earlier questions.
- Built for a portfolio demo, not for many simultaneous users.

## Run locally
```
pip install -r requirements.txt
set GEMINI_API_KEY=your-key
python -m streamlit run app.py
```
