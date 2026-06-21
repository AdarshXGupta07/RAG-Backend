import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from evaluation.evaluation_retrival import evaluate
from evaluation.llm_judge import judge_answer
import requests

API_URL = "http://localhost:8000/query"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1LCJ0ZW5hbnRfaWQiOjgsImV4cCI6MTc4MjA1NDY5MH0.ZMpIm6zEgk1CSPEnbXQ5_U0A5z2UCyZa_QvqRigpSTs"
TENANT_ID = 8 # Using tenant with existing chunks

def get_answer(question):
    r = requests.post(API_URL,
                       headers={"Authorization": f"Bearer {TOKEN}"},
                       json={"question": question})
    print("STATUS:", r.status_code)
    print("BODY:", r.json())
    return r.json()["answer"]
if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    golden_set_path = script_dir / "golden_test_set.json"
    
    with open(golden_set_path) as f:
        golden_set = json.load(f)

    recall_score = evaluate(golden_set, TENANT_ID)

    faithfulness_scores, correctness_scores = [], []
    no_answer_correct = 0
    no_answer_total = 0

    for item in golden_set:
        try:
            answer = get_answer(item["question"])

            if item["expected_source_document"] == "NONE":
                no_answer_total += 1
                NO_ANSWER_SIGNALS = ["don't know", "not mention", "no information", 
                       "doesn't mention", "do not", "i don't have", 
                       "nahin", "nahi hai", "koi jaankari nahi", "pata nahi"]

                if any(signal in answer.lower() for signal in NO_ANSWER_SIGNALS):
                    no_answer_correct += 1

            score = judge_answer(item["question"], item["expected_answer"], answer)
            faithfulness_scores.append(score["faithfulness"])
            correctness_scores.append(score["correctness"])
        except Exception as e:
            print(f"Error processing question: {item['question']}")
            print(f"Error: {e}")
            continue

    print(f"recall@5: {recall_score}")
    if faithfulness_scores:
        print(f"avg faithfulness: {sum(faithfulness_scores)/len(faithfulness_scores)}/5")
    if correctness_scores:
        print(f"avg correctness: {sum(correctness_scores)/len(correctness_scores)}/5")
    if no_answer_total > 0:
        print(f"hallucination check passed: {no_answer_correct}/{no_answer_total}")