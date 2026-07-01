import re

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 300):
    # Whitespace normalize
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text:
        return []

    # Sentence boundaries pe split
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Overlap: previous chunk ka last part carry forward
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = (overlap_text + " " + sentence).strip()

    if current_chunk:
        chunks.append(current_chunk.strip())

    # 50 char se chhote chunks filter karo (headers/noise)
    return [c for c in chunks if len(c) > 50]