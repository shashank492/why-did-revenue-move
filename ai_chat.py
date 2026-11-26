from google import genai
from google.genai import types
from analyst_tools import monthly, get_drivers, top_movers, new_vs_repeat

client = genai.Client(http_options=types.HttpOptions(
    timeout=30000,
    retry_options=types.HttpRetryOptions(attempts=2),
))
MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.6-flash"]
calls = []                       # log of every function the AI used

RULES = """You are a business analyst assistant for an online gift store.
Data covers 2009-12 to 2011-12 (months are written YYYY-MM).
Use ONLY numbers returned by the tools. Never calculate, estimate or guess numbers.
Questions about one month compare it with the previous month.
Call only the tools needed to answer the question.
Write numbers in full like £133,348. Never use K or M abbreviations and never round.
If the question assumes something the numbers contradict, say so politely.
If the tools cannot answer, say so. Write short plain English, money in pounds."""


def run(name, fn, *months, **kw):
    if any(m not in monthly.index for m in months):
        result = {"error": "Month not in data. Data covers 2009-12 to 2011-12."}
    else:
        result = fn(*months, **kw)
    calls.append({"function": name, "inputs": months, "result": result})
    return result


def revenue_drivers(old_month: str, new_month: str) -> dict:
    """Why revenue changed between two months (YYYY-MM): total change and the share from customers, orders per customer and order value."""
    return run("revenue_drivers", get_drivers, old_month, new_month)


def country_movers(old_month: str, new_month: str) -> list:
    """Countries with the biggest revenue change between two months (YYYY-MM)."""
    return run("country_movers", top_movers, old_month, new_month, by="Country")


def product_movers(old_month: str, new_month: str) -> list:
    """Products with the biggest revenue change between two months (YYYY-MM)."""
    return run("product_movers", top_movers, old_month, new_month, by="Description")


def new_vs_repeat_customers(month: str) -> list:
    """Customers and revenue from new vs repeat customers in one month (YYYY-MM)."""
    return run("new_vs_repeat_customers", new_vs_repeat, month)


def new_chat(model=None):
    return client.chats.create(
        model=model or MODELS[0],
        config=types.GenerateContentConfig(
            system_instruction=RULES,
            tools=[revenue_drivers, country_movers, product_movers, new_vs_repeat_customers],
        ),
    )


def ask(chat, question):
    calls.clear()
    try:
        response = chat.send_message(question)
    except Exception:
        for model in MODELS[1:]:          # first model failed, try the backups
            try:
                calls.clear()
                response = new_chat(model).send_message(question)
                break
            except Exception:
                continue
        else:
            raise                         # all models failed, show the error
    return response.text, list(calls)
