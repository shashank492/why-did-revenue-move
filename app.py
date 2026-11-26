import streamlit as st
import pandas as pd
from analyst_tools import monthly, get_drivers, top_movers, new_vs_repeat
from ai_chat import new_chat, ask
from checker import check_numbers

st.title("Why Did Revenue Move?")

months = list(monthly.index)
new = st.selectbox("Pick a month", months[1:], index=10)
old = months[months.index(new) - 1]

if new == months[-1]:
    st.warning("This is the last month in the data and may be incomplete.")

r = get_drivers(old, new)
n, o = monthly.loc[new], monthly.loc[old]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"£{r['new_revenue']:,}", f"{r['pct_change']}%")
c2.metric("Customers", int(n["customers"]), int(n["customers"] - o["customers"]))
c3.metric("Orders / customer", round(n["orders_per_customer"], 2),
          round(n["orders_per_customer"] - o["orders_per_customer"], 2))
c4.metric("Avg order value", f"£{n['order_value']:.0f}",
          f"£{n['order_value'] - o['order_value']:.0f}")

st.subheader(f"What drove the £{r['change']:,} change vs {old}?")
names = {"customers": "Customers", "orders_per_customer": "Orders per customer", "order_value": "Order value"}
st.bar_chart(pd.Series(r["drivers"]).rename(index=names), horizontal=True)

st.subheader("Top country movers")
st.dataframe(pd.DataFrame(top_movers(old, new, "Country")))

st.subheader("Top product movers")
st.dataframe(pd.DataFrame(top_movers(old, new, "Description")))

st.subheader("New vs repeat customers")
st.dataframe(pd.DataFrame(new_vs_repeat(new)))

st.divider()
st.subheader("Ask the AI analyst")

if "chat" not in st.session_state:
    st.session_state.chat = new_chat()
    st.session_state.history = []


def show(role, text, calls=None):
    with st.chat_message(role):
        st.write(text)
        if role == "assistant" and calls is not None:
            total, bad = check_numbers(text, calls)
            if bad:
                st.warning("⚠️ Could not verify: " + ", ".join(f"{b:,.2f}".rstrip("0").rstrip(".") for b in bad))
            elif total:
                st.success(f"✅ Verified: all {total} numbers match the tool results")
        if calls:
            with st.expander("How I got this"):
                st.json(calls)


for m in st.session_state.history:
    show(**m)

question = st.chat_input("e.g. Why did revenue drop in January 2011?")
if question:
    show("user", question)
    with st.spinner("Analysing..."):
        try:
            answer, calls = ask(st.session_state.chat, question)
        except Exception as e:
            answer, calls = f"Sorry, the AI is not available right now. Please try again in a minute. ({str(e)[:120]})", None
    show("assistant", answer, calls)
    st.session_state.history.append(dict(role="user", text=question))
    st.session_state.history.append(dict(role="assistant", text=answer, calls=calls))
