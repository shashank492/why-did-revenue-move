import duckdb
import numpy as np

con = duckdb.connect()
con.sql("CREATE TABLE sales AS SELECT * FROM 'sales_clean.parquet'")

monthly = con.sql("""
SELECT Month,
       COUNT(DISTINCT CustomerID) AS customers,
       COUNT(DISTINCT Invoice)    AS orders,
       SUM(Revenue)               AS revenue
FROM sales GROUP BY Month ORDER BY Month
""").df().set_index("Month")
monthly["orders_per_customer"] = monthly["orders"] / monthly["customers"]
monthly["order_value"] = monthly["revenue"] / monthly["orders"]


def get_drivers(old, new):
    a, b = monthly.loc[old], monthly.loc[new]
    change = b["revenue"] - a["revenue"]
    total = np.log(b["revenue"] / a["revenue"])
    drivers = {}
    for d in ["customers", "orders_per_customer", "order_value"]:
        drivers[d] = round(change * np.log(b[d] / a[d]) / total)
    return {"old": old, "new": new,
            "old_revenue": round(a["revenue"]), "new_revenue": round(b["revenue"]),
            "change": round(change),
            "pct_change": round(change / a["revenue"] * 100, 1),
            "drivers": drivers}


def top_movers(old, new, by="Country", n=3):
    assert by in ("Country", "Description")
    skip = ("AND StockCode NOT IN ('M','POST','DOT','C2','BANK CHARGES','AMAZONFEE','CRUK')"
            if by == "Description" else "")
    df = con.sql(f"""
    SELECT {by} AS name,
           ROUND(SUM(CASE WHEN Month = '{old}' THEN Revenue ELSE 0 END)) AS old_revenue,
           ROUND(SUM(CASE WHEN Month = '{new}' THEN Revenue ELSE 0 END)) AS new_revenue
    FROM sales WHERE Month IN ('{old}', '{new}') {skip}
    GROUP BY {by}
    """).df()
    df["change"] = df["new_revenue"] - df["old_revenue"]
    df = df.reindex(df["change"].abs().sort_values(ascending=False).index)
    return df.head(n).to_dict("records")


def new_vs_repeat(month):
    return con.sql(f"""
    WITH first AS (SELECT CustomerID, MIN(Month) AS first_month
                   FROM sales GROUP BY CustomerID)
    SELECT CASE WHEN first.first_month = '{month}' THEN 'new' ELSE 'repeat' END AS type,
           COUNT(DISTINCT sales.CustomerID) AS customers,
           ROUND(SUM(sales.Revenue)) AS revenue
    FROM sales JOIN first USING (CustomerID)
    WHERE sales.Month = '{month}'
    GROUP BY type
    """).df().to_dict("records")
