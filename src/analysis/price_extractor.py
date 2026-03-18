import re


def extract_prices(text: str) -> list:

    if not text:
        return []

    prices = re.findall(r"\$\s*(\d+(?:\.\d+)?)", text)

    return [float(p) for p in prices]