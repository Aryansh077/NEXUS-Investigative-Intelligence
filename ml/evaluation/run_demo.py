"""Measure operational coverage for the synthetic anomaly baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.evaluation import evaluate_unsupervised_case


def evaluate(input_path: Path) -> dict[str, object]:
    frame = pd.read_csv(input_path)
    entities = sorted(set(frame["caller"].astype(str)) | set(frame["receiver"].astype(str)))
    relationships = frame.rename(
        columns={"caller": "source_id", "receiver": "target_id"}
    ).to_dict(orient="records")
    return evaluate_unsupervised_case(entities, relationships)


if __name__ == "__main__":
    result = evaluate(Path("data/synthetic/cdr/cdr_may.csv"))
    print(json.dumps(result, indent=2))