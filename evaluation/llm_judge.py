import requests, json, os
from dotenv import load_dotenv

load_dotenv()

def judge_answer(question, expected_answer, generated_answer):
    prompt = f"""Question: {question}
Reference answer: {expected_answer}
Generated answer: {generated_answer}

Score 1-5 each: faithfulness (no made-up facts beyond reference), correctness (matches reference meaning).
Respond ONLY as JSON: {{"faithfulness": int, "correctness": int}}"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
        json={"model": "llama-3.3-70b-versatile",
              "messages": [{"role": "user", "content": prompt}],
              "temperature": 0}
    )
    text = response.json()["choices"][0]["message"]["content"]
    cleaned = text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned)