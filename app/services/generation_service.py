import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from typing import List, Dict

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(query: str, chunks: List[Dict]) -> str:
    context = ""
    for i, chunk in enumerate(chunks, 1):
        context += f"[Source {i}] (File: {chunk['filename']})\n"
        context += f"{chunk['content']}\n\n"

    prompt = f"""You are an expert document analysis assistant working for a company.
Answer the user's question using ONLY the provided sources below.

Rules:
- Give a DETAILED, COMPREHENSIVE answer — minimum 3-4 paragraphs for complex questions
- Use bullet points, numbered lists, or headings where it improves clarity
- Cite sources inline using [Source N] format
- Explain technical concepts thoroughly — do not give one-liner answers
- If the answer spans multiple sources, synthesize them into a coherent response
- If the answer is not in the sources, say "I don't have enough information in the provided documents to answer this."
- Never make up information not present in the sources

Sources:
{context}

Question: {query}

Provide a thorough, well-structured answer:"""

    return prompt


def generate_answer(query: str, chunks: List[Dict]) -> Dict:
    if not chunks:
        return {
            "answer": "No relevant documents found for your query. Please upload relevant documents first.",
            "citations": []
        }

    prompt = build_prompt(query, chunks)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert document analysis AI assistant for a company platform. "
                    "You provide detailed, structured, and accurate answers based strictly on provided document sources. "
                    "Your answers should be thorough and professional — never give vague or one-line responses."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,   # 0.1 → 0.3: thoda flexible, better phrasing
        max_tokens=2048,   # 1000 → 2048: detailed answers ke liye
        top_p=0.9
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