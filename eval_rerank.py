import json
from template import rerank_by_overlap
from evaluate_answers import calculate_context_recall, calculate_context_precision

def evaluate():
    with open("golden_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print("--- Reranking Evaluation (Exercise 3.5) ---")
    traces = dataset[:5]
    for trace in traces:
        expected = trace["expected_answer"]
        query = trace["question"]
        
        relevant_contexts = [c["text"] for c in trace["contexts"]]
        noise1 = "The cafeteria is open from 8am to 8pm."
        noise2 = "Parking permits are required for all students."
        initial_contexts = [noise1, noise2] + relevant_contexts
        
        recall_before = calculate_context_recall(expected, initial_contexts)
        precision_before = calculate_context_precision(expected, initial_contexts)
        
        reranked_contexts = rerank_by_overlap(initial_contexts, query)
        recall_after = calculate_context_recall(expected, reranked_contexts)
        precision_after = calculate_context_precision(expected, reranked_contexts)
        
        print(f"ID: {trace['id']}")
        print(f"  Before: Recall={recall_before:.2f}, Precision={precision_before:.2f}")
        print(f"  After : Recall={recall_after:.2f}, Precision={precision_after:.2f}")
        print()

if __name__ == "__main__":
    evaluate()
