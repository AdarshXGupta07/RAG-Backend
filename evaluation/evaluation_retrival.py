import sys, json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the correct retrieval function
from app.services.retrieval_service import retrieve_chunks
from app.database import SessionLocal

def evaluate(golden_set, tenant_id, k=5):
    db = SessionLocal()
    try:
        hits = []
        for item in golden_set:
            if item["expected_source_document"] == "NONE":
                continue  # ye sawaal generation test mein use honge, retrieval mein nahi

            results = retrieve_chunks(item["question"], tenant_id, db, top_k=k)
            retrieved_docs = [r["filename"] for r in results]  # results is a list of dicts

            hit = item["expected_source_document"] in retrieved_docs
            hits.append(1 if hit else 0)

        return round(sum(hits) / len(hits), 3) if hits else 0
    finally:
        db.close()

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    golden_set_path = script_dir / "golden_test_set.json"
    
    with open(golden_set_path) as f:
        golden_set = json.load(f)
    tenant_id = "7"  # Using tenant with existing chunks (alpha_tenant)
    print(f"recall@5: {evaluate(golden_set, tenant_id)}")