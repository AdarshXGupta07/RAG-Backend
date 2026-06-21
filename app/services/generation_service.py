import os
from dotenv import load_dotenv
load_dotenv()  # ← PEHLI LINE honi chahiye, client se pehle

from groq import Groq
from typing import List, Dict

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def build_prompt(query: str, chunks: List[Dict]) -> str:
    """
    Chunks ko numbered sources mein format karo
    """
    context = ""
    for i, chunk in enumerate(chunks, 1):
        context += f"[Source {i}] (File: {chunk['filename']})\n"
        context += f"{chunk['content']}\n\n"

    prompt = f"""You are a helpful assistant. Answer the user's question using ONLY the provided sources below.

Rules:
- Answer only from the given sources
- Cite sources using [Source N] format inline
- If the answer is not in the sources, say "I don't have enough information in the provided documents to answer this."
- Do not make up information

Sources:
{context}

Question: {query}

Answer:"""

    return prompt


def generate_answer(query: str, chunks: List[Dict]) -> Dict:
    """
    Groq se answer generate karo with citations
    """
    if not chunks:
        return {
            "answer": "No relevant documents found for your query.",
            "citations": []
        }

    prompt = build_prompt(query, chunks)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based only on provided document sources."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,  # low temperature = factual, less creative
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    # Kaun se sources actually use hue answer mein
    used_citations = []
    for i, chunk in enumerate(chunks, 1):
        if f"[Source {i}]" in answer:
            used_citations.append({
                "source_number": i,
                "filename": chunk["filename"],
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "similarity_score": chunk["similarity_score"]
            })

    return {
        "answer": answer,
        "citations": used_citations
    }