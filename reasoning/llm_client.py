from dotenv import load_dotenv
import os
from groq import Groq
import json

load_dotenv() 
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

def run_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a senior software architect."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content

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
        llm_text = llm_text + "\nReturn ONLY valid JSON matching the schema exactly."
        result = run_llm(llm_text)  # your existing LLM call
        result = safe_parse(result)
        retries += 1

    return result
