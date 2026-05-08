from datetime import datetime
from pathlib import Path

import pandas as pd
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "MODELS" / "best.pt"
DATA_YAML_PATH = PROJECT_ROOT / "data.yaml"
EVALUATION_METRICS_PATH = PROJECT_ROOT / "data" / "evaluation_metrics.csv"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def compute_model_evaluation() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")
    if not DATA_YAML_PATH.exists():
        raise FileNotFoundError(f"data.yaml not found at: {DATA_YAML_PATH}")

    config = _load_data_yaml(DATA_YAML_PATH)
    image_paths = _resolve_validation_images(config, DATA_YAML_PATH)
    if not image_paths:
        raise FileNotFoundError("No validation images found from data.yaml.")

    model = YOLO(str(MODEL_PATH))
    tp = tn = fp = fn = 0

    for image_path in image_paths:
        has_label = _has_positive_label(image_path)
        results = model.predict(source=str(image_path), verbose=False)
        has_prediction = len(results[0].boxes) > 0

        if has_label and has_prediction:
            tp += 1
        elif not has_label and not has_prediction:
            tn += 1
        elif not has_label and has_prediction:
            fp += 1
        else:
            fn += 1

    accuracy = _safe_divide(tp + tn, tp + tn + fp + fn)
    precision = _safe_divide(tp, tp + fp)
    recall = _safe_divide(tp, tp + fn)
    f1 = _safe_divide(2 * precision * recall, precision + recall)

    metrics = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "total_images": len(image_paths),
        "model_path": str(MODEL_PATH),
        "data_yaml": str(DATA_YAML_PATH),
    }
    EVALUATION_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(EVALUATION_METRICS_PATH, index=False)
    return metrics


def load_evaluation_metrics() -> dict | None:
    if not EVALUATION_METRICS_PATH.exists():
        return None

    df = pd.read_csv(EVALUATION_METRICS_PATH)
    if df.empty:
        return None
    return df.iloc[-1].to_dict()


def _load_data_yaml(path: Path) -> dict:
    try:
        import yaml

        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to read data.yaml.") from exc

    if "val" not in config:
        raise ValueError("data.yaml must include a val path.")
    return config


def _resolve_validation_images(config: dict, yaml_path: Path) -> list[Path]:
    dataset_root = _resolve_path(config.get("path", yaml_path.parent), yaml_path.parent)
    val_entries = config["val"] if isinstance(config["val"], list) else [config["val"]]
    image_paths: list[Path] = []

    for entry in val_entries:
        val_path = _resolve_path(entry, dataset_root)
        if val_path.is_file() and val_path.suffix.lower() == ".txt":
            image_paths.extend(_read_image_list(val_path, dataset_root))
        elif val_path.is_file() and val_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_paths.append(val_path)
        elif val_path.is_dir():
            image_paths.extend(
                path for path in val_path.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS
            )

    return sorted(set(path.resolve() for path in image_paths))


def _resolve_path(value, base: Path) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return (base / path).resolve()


def _read_image_list(list_path: Path, dataset_root: Path) -> list[Path]:
    images = []
    for line in list_path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item:
            continue
        image_path = _resolve_path(item, dataset_root)
        if image_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(image_path)
    return images


def _has_positive_label(image_path: Path) -> bool:
    label_path = _label_path_for_image(image_path)
    if not label_path.exists():
        return False

    return any(line.strip() for line in label_path.read_text(encoding="utf-8").splitlines())


def _label_path_for_image(image_path: Path) -> Path:
    parts = list(image_path.parts)
    if "images" in parts:
        index = len(parts) - 1 - parts[::-1].index("images")
        parts[index] = "labels"
        return Path(*parts).with_suffix(".txt")
    return image_path.with_suffix(".txt")


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
