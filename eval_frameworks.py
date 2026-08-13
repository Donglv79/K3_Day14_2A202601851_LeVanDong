"""Compare RAGAS and DeepEval on identical saved inputs for Exercise 3.4.

The comparison uses each framework's native Exact Match metric. It is fully
deterministic, makes no network request, and consumes no LLM/API quota.
"""

from __future__ import annotations

import json
import os
from importlib.metadata import version
from pathlib import Path

# Disable DeepEval telemetry before importing the package. This experiment is
# intended to be local and deterministic.
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

from deepeval.metrics import ExactMatchMetric as DeepEvalExactMatch  # noqa: E402
from deepeval.test_case import LLMTestCase  # noqa: E402
from ragas.metrics.collections import ExactMatch as RagasExactMatch  # noqa: E402


ROOT = Path(__file__).resolve().parent


def _load_inputs() -> list[dict[str, str]]:
    golden = json.loads((ROOT / "golden_dataset.json").read_text(encoding="utf-8"))
    actual = json.loads(
        (ROOT / "artifacts" / "actual_answers.json").read_text(encoding="utf-8")
    )
    if golden.get("corpus_id") != actual.get("corpus_id"):
        raise ValueError("Golden and actual artifacts use different corpus IDs")

    actual_by_id = {record["id"]: record for record in actual["answers"]}
    inputs: list[dict[str, str]] = []
    for gold in golden["qa_pairs"]:
        generated = actual_by_id.get(gold["id"])
        if generated is None:
            raise ValueError(f"Missing actual answer for {gold['id']}")
        inputs.append(
            {
                "id": gold["id"],
                "question": gold["question"],
                "actual": generated["actual_answer"],
                "expected": gold["expected_answer"],
            }
        )
    return inputs


def evaluate() -> None:
    inputs = _load_inputs()
    ragas_metric = RagasExactMatch()
    deepeval_metric = DeepEvalExactMatch()
    rows: list[tuple[str, float, float]] = []

    for item in inputs:
        ragas_result = ragas_metric.score(
            response=item["actual"], reference=item["expected"]
        )
        test_case = LLMTestCase(
            input=item["question"],
            actual_output=item["actual"],
            expected_output=item["expected"],
        )
        deepeval_score = float(deepeval_metric.measure(test_case))
        rows.append((item["id"], float(ragas_result.value), deepeval_score))

    disagreements = sum(ragas != deep for _, ragas, deep in rows)
    ragas_matches = sum(ragas for _, ragas, _ in rows)
    deepeval_matches = sum(deep for _, _, deep in rows)
    total = len(rows)

    print(f"RAGAS version: {version('ragas')}")
    print(f"DeepEval version: {version('deepeval')}")
    print(f"Same input cases: {total}")
    print("| Trace | RAGAS ExactMatch | DeepEval ExactMatch |")
    print("|---|---:|---:|")
    for trace_id, ragas_score, deepeval_score in rows:
        print(f"| {trace_id} | {ragas_score:.0f} | {deepeval_score:.0f} |")
    print(
        f"\nRAGAS: {ragas_matches:.0f}/{total} ({ragas_matches / total:.2%}); "
        f"DeepEval: {deepeval_matches:.0f}/{total} ({deepeval_matches / total:.2%}); "
        f"disagreements: {disagreements}."
    )


if __name__ == "__main__":
    evaluate()
