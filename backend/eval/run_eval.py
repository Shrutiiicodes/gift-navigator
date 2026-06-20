"""Evaluation harness for the free-text classifier.

Runs the expert-validated golden set through the classifier and reports:
  * overall accuracy
  * accuracy broken down by resolution PATH (keyword / fallback / llm) - so the
    cheap deterministic path and the escalation path are measured separately
  * accuracy broken down by case DIFFICULTY (easy / hard)
  * a confusion matrix
  * the low-confidence / escalation rate

Usage (from backend/):
    python -m eval.run_eval            # human-readable report
    python -m eval.run_eval --json     # machine-readable, for charts
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import classifier, rules_engine  # noqa: E402

CASES_PATH = Path(__file__).parent / "golden_cases.json"


def _acc(bucket: dict) -> float:
    return round(bucket["correct"] / bucket["total"], 4) if bucket["total"] else 0.0


def run() -> dict:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    ids = rules_engine.list_entity_ids()

    correct = 0
    by_method: dict[str, dict] = defaultdict(lambda: {"correct": 0, "total": 0})
    by_difficulty: dict[str, dict] = defaultdict(lambda: {"correct": 0, "total": 0})
    confusion: dict[str, dict[str, int]] = {a: {b: 0 for b in ids} for a in ids}
    failures = []

    for case in cases:
        result = classifier.classify(case["text"])
        predicted = result["entity_id"]
        expected = case["expected"]
        method = result["method"]
        difficulty = case.get("difficulty", "unspecified")
        is_correct = predicted == expected

        by_method[method]["total"] += 1
        by_difficulty[difficulty]["total"] += 1
        confusion[expected][predicted] += 1
        if is_correct:
            correct += 1
            by_method[method]["correct"] += 1
            by_difficulty[difficulty]["correct"] += 1
        else:
            failures.append(
                {
                    "text": case["text"],
                    "expected": expected,
                    "predicted": predicted,
                    "method": method,
                    "difficulty": difficulty,
                    "confidence": result["confidence"],
                }
            )

    total = len(cases)
    escalated = sum(
        v["total"] for k, v in by_method.items() if k in ("fallback", "llm")
    )

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "by_method": {
            m: {**b, "accuracy": _acc(b)} for m, b in by_method.items()
        },
        "by_difficulty": {
            d: {**b, "accuracy": _acc(b)} for d, b in by_difficulty.items()
        },
        "escalation_rate": round(escalated / total, 4) if total else 0.0,
        "confusion": confusion,
        "failures": failures,
        "entity_ids": ids,
        "llm_enabled": classifier.os.environ.get("ANTHROPIC_API_KEY") is not None,
    }


def _print_confusion(confusion: dict, ids: list) -> None:
    width = max(len(i) for i in ids) + 2
    print("\nConfusion matrix (rows = expected, cols = predicted):")
    print(" " * width + "".join(f"{i:>{width}}" for i in ids))
    for exp in ids:
        print(
            f"{exp:<{width}}"
            + "".join(f"{confusion[exp][pred]:>{width}}" for pred in ids)
        )


def _print_bucket(title: str, buckets: dict) -> None:
    print(f"\n{title}:")
    for name, b in sorted(buckets.items()):
        print(f"  {name:<10} {b['correct']:>3}/{b['total']:<3}  {b['accuracy']*100:5.1f}%")


def main() -> None:
    report = run()
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
        return

    print("=" * 60)
    print("  GIFT Navigator - classifier evaluation")
    print("=" * 60)
    print(f"Cases:           {report['total']}")
    print(f"Correct:         {report['correct']}")
    print(f"Overall accuracy:{report['accuracy']*100:6.1f}%")
    print(f"Escalation rate: {report['escalation_rate']*100:6.1f}%  "
          f"(LLM fallback {'ENABLED' if report['llm_enabled'] else 'disabled'})")

    _print_bucket("Accuracy by resolution path", report["by_method"])
    _print_bucket("Accuracy by difficulty", report["by_difficulty"])
    _print_confusion(report["confusion"], report["entity_ids"])

    if report["failures"]:
        print(f"\nMisclassifications ({len(report['failures'])}):")
        for f in report["failures"]:
            print(
                f"  [{f['expected']} -> {f['predicted']}] "
                f"({f['difficulty']}, {f['method']}, conf {f['confidence']}): {f['text']}"
            )
    else:
        print("\nNo misclassifications on the golden set.")
    print()


if __name__ == "__main__":
    main()
