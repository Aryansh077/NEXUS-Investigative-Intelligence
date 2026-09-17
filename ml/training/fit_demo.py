"""Fit an Isolation Forest artifact from the synthetic CDR demo dataset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.anomaly_detection import fit_isolation_forest
from ml.feature_engineering import build_entity_features


def train(input_path: Path, output_path: Path) -> dict[str, object]:
    frame = pd.read_csv(input_path)
    entity_ids = sorted(set(frame["caller"].astype(str)) | set(frame["receiver"].astype(str)))
    relationships = frame.rename(
        columns={"caller": "source_id", "receiver": "target_id"}
    ).to_dict(orient="records")
    features = build_entity_features(entity_ids, relationships)
    model, _, _ = fit_isolation_forest(features)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": model, "features": list(features.columns), "random_state": 42},
        output_path,
    )
    return {
        "model": "IsolationForest",
        "input": str(input_path),
        "output": str(output_path),
        "entity_count": len(entity_ids),
        "feature_columns": list(features.columns),
        "fit_type": "synthetic_runtime_baseline",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/synthetic/cdr/cdr_may.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ml/models/nexus_isolation_forest.joblib"),
    )
    args = parser.parse_args()
    print(json.dumps(train(args.input, args.output), indent=2))