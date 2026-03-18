import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

YANDEX_CLOUD_MODEL = os.getenv("YANDEX_CLOUD_MODEL")
YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")


client = OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    project=YANDEX_CLOUD_FOLDER,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
)


SYSTEM_PROMPT = """
You are a professional dermatologist.

Recommend exactly 3 skincare products.

For each product include:
- product name
- price (in USD or RUB)

Return strictly in this format:

1. Product name — $price
2. Product name — $price
3. Product name — $price

No extra text.
"""


def build_prompt(user_query: str) -> str:
    return f"{SYSTEM_PROMPT}\n\nUser request:\n{user_query}"


def get_llm_response(user_query: str) -> str:

    prompt = build_prompt(user_query)

    response = client.responses.create(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        input=[{"role": "user", "content": prompt}],
    )

    return response.output_text