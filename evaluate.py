"""Evaluate next-word suggestions with a deterministic held-out sentence split."""

import argparse
import json
import tempfile
from pathlib import Path

from predictor import NGramPredictor


def evaluate(corpus_path: Path) -> dict:
    lines = [line.strip() for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    train_lines = [line for index, line in enumerate(lines) if index % 5]
    test_lines = [line for index, line in enumerate(lines) if not index % 5]

    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8") as handle:
        handle.write("\n".join(train_lines))
        handle.flush()
        predictor = NGramPredictor(handle.name)

    top1 = 0
    top5 = 0
    evaluated = 0
    for sentence in test_lines:
        tokens = predictor.tokenize(sentence)
        if len(tokens) < 2:
            continue
        expected = tokens[-1]
        suggestions = predictor.predict(" ".join(tokens[:-1]), 5)
        evaluated += 1
        top1 += bool(suggestions and suggestions[0] == expected)
        top5 += expected in suggestions

    return {
        "training_sentences": len(train_lines),
        "held_out_sentences": evaluated,
        "top_1_accuracy": top1 / evaluated if evaluated else 0.0,
        "top_5_accuracy": top5 / evaluated if evaluated else 0.0,
        "note": "Small corpus diagnostic; not a general keyboard benchmark.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path(__file__).resolve().parent / "data" / "corpus.txt",
    )
    args = parser.parse_args()
    print(json.dumps(evaluate(args.corpus), indent=2))
