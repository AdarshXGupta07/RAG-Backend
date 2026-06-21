import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()
JINA_API_KEY=os.getenv("JINA_API_KEY")
JINA_MODEL = "jina-embeddings-v3"
def get_embedding(text:str)->List[float]:
    text=text.replace("/n","").strip()
    response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": JINA_MODEL,
            "task": "retrieval.passage",
            "input": [text]
        }
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]
def get_query_embedding(text: str) -> List[float]:
    """
    User query embed karte waqt use karo — task: retrieval.query
    """
    text = text.replace("\n", " ").strip()

    response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": JINA_MODEL,
            "task": "retrieval.query",
            "input": [text]
        }
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Multiple chunks ek API call mein — cost aur time dono bachta hai
    """
    cleaned = [t.replace("\n", " ").strip() for t in texts]

    response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": JINA_MODEL,
            "task": "retrieval.passage",
            "input": cleaned
        }
    )
    response.raise_for_status()

    data = response.json()["data"]
    return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]