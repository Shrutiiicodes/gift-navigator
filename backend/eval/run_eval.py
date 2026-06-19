"""Evaluation harness for the free-text classifier.

Runs the expert-validated golden set through the classifier and prints an
accuracy figure plus a confusion matrix. This is the artefact that answers
"how do you know your recommendations are right?" in the dissertation.

Usage (from backend/):  python -m eval.run_eval
Add --json to emit machine-readable results for charts.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

# Allow running as `python -m eval.run_eval` from the backend dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import classifier, rules_engine  # noqa: E402

CASES_PATH = Path(__file__).parent / "golden_cases.json"


def run() -> dict:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    ids = rules_engine.list_entity_ids()

    correct = 0
    by_method: dict[str, int] = defaultdict(int)
    confusion: dict[str, dict[str, int]] = {a: {b: 0 for b in ids} for a in ids}
    failures = []

    for case in cases:
        result = classifier.classify(case["text"])
        predicted = result["entity_id"]
        expected = case["expected"]
        by_method[result["method"]] += 1
        confusion[expected][predicted] += 1
        if predicted == expected:
            correct += 1
        else:
            failures.append(
                {
                    "text": case["text"],
                    "expected": expected,
                    "predicted": predicted,
                    "confidence": result["confidence"],
                }
            )

    total = len(cases)
    accuracy = correct / total if total else 0.0
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "by_method": dict(by_method),
        "confusion": confusion,
        "failures": failures,
        "entity_ids": ids,
    }


def _print_confusion(confusion: dict, ids: list) -> None:
    width = max(len(i) for i in ids) + 2
    header = " " * width + "".join(f"{i:>{width}}" for i in ids)
    print("\nConfusion matrix (rows = expected, cols = predicted):")
    print(header)
    for exp in ids:
        row = f"{exp:<{width}}" + "".join(
            f"{confusion[exp][pred]:>{width}}" for pred in ids
        )
        print(row)


def main() -> None:
    report = run()
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
        return

    print("=" * 56)
    print("  GIFT Navigator - classifier evaluation")
    print("=" * 56)
    print(f"Cases:     {report['total']}")
    print(f"Correct:   {report['correct']}")
    print(f"Accuracy:  {report['accuracy'] * 100:.1f}%")
    print(f"Methods:   {report['by_method']}")

    _print_confusion(report["confusion"], report["entity_ids"])

    if report["failures"]:
        print(f"\nMisclassifications ({len(report['failures'])}):")
        for f in report["failures"]:
            print(
                f"  [{f['expected']} -> {f['predicted']}] "
                f"(conf {f['confidence']}): {f['text']}"
            )
    else:
        print("\nNo misclassifications on the golden set.")
    print()


if __name__ == "__main__":
    main()
