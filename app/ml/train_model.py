import csv
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from app.ml.dataset import DATA_PATH, write_training_csv
from app.ml.features import feature_columns


MODEL_PATH = Path(__file__).with_name("greenchem_model.joblib")


def train_model() -> dict[str, object]:
    csv_path = write_training_csv(DATA_PATH)
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    columns = feature_columns()
    x = [[float(row[column]) for column in columns] for row in rows]
    y = [int(row["is_compatible"]) for row in rows]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    artifact = {
        "model": model,
        "feature_columns": columns,
        "training_rows": len(rows),
        "accuracy": accuracy,
        "label_source": "curated_rule_bootstrap",
    }
    joblib.dump(artifact, MODEL_PATH)

    return {
        "model_path": str(MODEL_PATH),
        "training_data_path": str(csv_path),
        "training_rows": len(rows),
        "accuracy": round(float(accuracy), 3),
        "classification_report": classification_report(y_test, predictions, zero_division=0),
    }


if __name__ == "__main__":
    result = train_model()
    for key, value in result.items():
        print(f"{key}: {value}")
