from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / "data" / "detections_log.csv"
LOG_COLUMNS = ["timestamp", "confidence", "severity", "latitude", "longitude"]


def append_detection_log(
    confidence: float,
    severity: str,
    latitude: float,
    longitude: float,
) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "confidence": float(confidence),
        "severity": severity,
        "latitude": float(latitude),
        "longitude": float(longitude),
    }
    columns = LOG_COLUMNS
    if LOG_PATH.exists():
        existing_columns = pd.read_csv(LOG_PATH, nrows=0).columns.tolist()
        columns = existing_columns if existing_columns else LOG_COLUMNS

    frame = pd.DataFrame([{column: row.get(column, "") for column in columns}], columns=columns)
    frame.to_csv(LOG_PATH, mode="a", index=False, header=not LOG_PATH.exists())


def log_detection(file_name: str, metrics) -> None:
    pothole_count = int(_get(metrics, "pothole_count", 0))
    if pothole_count <= 0:
        return

    append_detection_log(
        confidence=_get(metrics, "average_confidence", 0.0),
        severity=_get(metrics, "severity_label", "Low"),
        latitude=_get(metrics, "latitude", 24.7136),
        longitude=_get(metrics, "longitude", 46.6753),
    )


def _get(metrics, key: str, default):
    if isinstance(metrics, dict):
        return metrics.get(key, default)
    return getattr(metrics, key, default)
