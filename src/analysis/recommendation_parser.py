import re


def extract_products(text: str) -> list:

    if not text:
        return []

    lines = text.split("\n")
    products = []

    for line in lines:
        line = re.sub(r"^\d+\.\s*", "", line)

        parts = line.split("—")

        if len(parts) >= 1:
            product = parts[0].strip()
            if product:
                products.append(product)

    return products