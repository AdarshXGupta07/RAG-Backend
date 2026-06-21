import sys
import os

# project root add karna (so app imports work)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.chunk import Chunk
from app.services.embedding_service import get_embeddings_batch

BATCH_SIZE = 50


def embed_all_chunks():
    db = SessionLocal()

    try:
        # 1. sirf un chunks ko uthao jinke embeddings missing hain
        unembedded_chunks = (
            db.query(Chunk)
            .filter(Chunk.embedding == None)
            .all()
        )

        print(f"Found {len(unembedded_chunks)} chunks without embeddings")

        # 2. batching start
        for i in range(0, len(unembedded_chunks), BATCH_SIZE):

            batch = unembedded_chunks[i:i + BATCH_SIZE]
            texts = [chunk.content for chunk in batch]

            print(f"Embedding batch {i // BATCH_SIZE + 1}...")

            # 3. embeddings generate (API call)
            embeddings = get_embeddings_batch(texts)

            # 4. mapping chunk → embedding
            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding

            # 5. save to DB
            db.commit()

            print(f"✓ Committed {len(batch)} embeddings")

        print("Done! All chunks embedded.")

    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    embed_all_chunks()