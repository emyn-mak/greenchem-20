from pathlib import Path

import joblib

from app.ml.features import build_features, vectorize
from app.ml.train_model import MODEL_PATH


class CompatibilityModel:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.artifact = None
        if model_path.exists():
            self.artifact = joblib.load(model_path)

    @property
    def is_available(self) -> bool:
        return self.artifact is not None

    def predict(self, solvent: dict, catalyst: dict, catalyst_role: str, environment: dict) -> dict[str, object]:
        if self.artifact is None:
            return {
                "available": False,
                "is_compatible": None,
                "model_signal": "No trained model found; rule-based compatibility only.",
            }

        features = build_features(solvent, catalyst, catalyst_role, environment.get("temperature"))
        model = self.artifact["model"]
        x = [vectorize(features)]
        prediction = int(model.predict(x)[0])
        probability = None
        if hasattr(model, "predict_proba"):
            classes = list(model.classes_)
            probabilities = model.predict_proba(x)[0]
            if 1 in classes:
                probability = float(probabilities[classes.index(1)])

        if probability is None:
            signal = "Prototype ML model predicted compatible." if prediction else "Prototype ML model predicted incompatible."
        elif prediction:
            signal = f"Prototype ML model predicted compatible with probability {probability:.2f}."
        else:
            signal = f"Prototype ML model predicted incompatible with probability {1 - probability:.2f}."

        return {
            "available": True,
            "is_compatible": bool(prediction),
            "probability_compatible": probability,
            "model_signal": signal,
            "training_rows": self.artifact.get("training_rows"),
            "label_source": self.artifact.get("label_source"),
        }
