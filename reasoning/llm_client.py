from dotenv import load_dotenv
import os
import json
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def run_llm(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a senior software architect.",
            temperature=0.2,
        ),
    )

    return response.text


def safe_parse(json_text: str) -> dict | None:
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None


def parse_with_retry(llm_text: str, max_retries: int = 1) -> dict:
    result = safe_parse(llm_text)
    retries = 0

    while result is None and retries < max_retries:
        # Append instruction to force valid JSON
        llm_text = (
            llm_text
            + "\nReturn ONLY valid JSON matching the schema exactly."
        )

        result = run_llm(llm_text)
        result = safe_parse(result)
        retries += 1

    return result