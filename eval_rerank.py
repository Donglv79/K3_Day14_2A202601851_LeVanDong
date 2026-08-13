"""Reproduce the before/after reranking measurements for Exercise 3.5."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from template import RAGASEvaluator, rerank_by_overlap


ROOT = Path(__file__).resolve().parent
TRACE_IDS = ("E01", "E03", "E04", "M01", "A01")


def _load_records(path: Path, key: str) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get(key)
    if not isinstance(records, list):
        raise ValueError(f"{path.name} must contain a {key!r} list")
    return {record["id"]: record for record in records}


def evaluate() -> None:
    """Rerank saved retrieval traces without adding or removing any chunk."""

    golden = _load_records(ROOT / "golden_dataset.json", "qa_pairs")
    actual = _load_records(ROOT / "artifacts" / "actual_answers.json", "answers")
    evaluator = RAGASEvaluator()
    rows: list[tuple[str, float, float, float, float, bool]] = []

    for trace_id in TRACE_IDS:
        gold = golden[trace_id]
        trace = actual[trace_id]
        before = [context["text"] for context in trace["retrieved_contexts"]]
        after = rerank_by_overlap(before, gold["question"])

        # Counter compares the multiset, so duplicates would also be preserved.
        same_chunk_multiset = Counter(before) == Counter(after)
        if not same_chunk_multiset:
            raise AssertionError(f"{trace_id}: reranker changed the chunk multiset")

        recall_before = evaluator.evaluate_context_recall(
            before, gold["expected_answer"]
        )
        recall_after = evaluator.evaluate_context_recall(
            after, gold["expected_answer"]
        )
        if not math.isclose(recall_before, recall_after, abs_tol=1e-12):
            raise AssertionError(f"{trace_id}: union coverage changed")

        precision_before = evaluator.evaluate_context_precision(
            before, gold["expected_answer"]
        )
        precision_after = evaluator.evaluate_context_precision(
            after, gold["expected_answer"]
        )
        rows.append(
            (
                trace_id,
                recall_before,
                precision_before,
                recall_after,
                precision_after,
                same_chunk_multiset,
            )
        )

    print("| Trace | Recall before | Precision before | Recall after | Precision after | Same chunks |")
    print("|---|---:|---:|---:|---:|:---:|")
    for row in rows:
        trace_id, recall_before, precision_before, recall_after, precision_after, same = row
        print(
            f"| {trace_id} | {recall_before:.4f} | {precision_before:.4f} | "
            f"{recall_after:.4f} | {precision_after:.4f} | "
            f"{'yes' if same else 'no'} |"
        )

    count = len(rows)
    print(
        "\nAverage: "
        f"recall {sum(row[1] for row in rows) / count:.4f} -> "
        f"{sum(row[3] for row in rows) / count:.4f}; "
        f"precision {sum(row[2] for row in rows) / count:.4f} -> "
        f"{sum(row[4] for row in rows) / count:.4f}."
    )


if __name__ == "__main__":
    evaluate()
