from dotenv import load_dotenv
import os
from groq import Groq

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
