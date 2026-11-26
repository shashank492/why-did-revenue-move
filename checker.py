import re


def flatten(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from flatten(v)
    elif isinstance(x, (list, tuple)):
        for v in x:
            yield from flatten(v)
    elif isinstance(x, str):
        for n in re.findall(r"\d+(?:\.\d+)?", x):
            yield float(n)
    elif isinstance(x, (int, float)):
        yield abs(float(x))


def check_numbers(answer, calls):
    text = re.sub(r"\b(19|20)\d{2}(-\d{2})?\b", "", answer)
    said = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*\.?\d*", text)]
    said = [n for n in said if n >= 10]
    known = {round(v, 1) for v in flatten(calls)}
    unverified = sorted({n for n in said if round(n, 1) not in known})
    return len(said), unverified
