import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.retrieval_service import search_similar_chunks

TENANT_ID = 7   # Using tenant with actual chunks (alpha_tenant)
TEST_QUERY = "What is CodeAlpha internship about?"  # Query related to the offer letter

db = SessionLocal()
results = search_similar_chunks(TEST_QUERY, TENANT_ID, db, top_k=3)
db.close()

print(f"\nQuery: {TEST_QUERY}\n")
print("=" * 60)

for i, r in enumerate(results, 1):
    print(f"\n[Result {i}] Score: {r['similarity_score']} | File: {r['filename']}")
    print(f"Chunk #{r['chunk_index']}")
    print("-" * 40)
    print(r['content'][:300])