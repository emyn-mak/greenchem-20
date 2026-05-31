import csv
from pathlib import Path

from app.compatibility import check_acid_base_compatibility
from app.knowledge import all_catalysts, all_solvents
from app.ml.features import build_features, feature_columns


DATA_PATH = Path(__file__).with_name("training_data.csv")
TEMPERATURES = [0, 25, 40, 60, 90, 120]


def generate_rows() -> list[dict[str, str | int | float]]:
    rows: list[dict[str, str | int | float]] = []
    for solvent in all_solvents():
        for catalyst in all_catalysts():
            for role in catalyst.get("roles", []):
                for temperature in TEMPERATURES:
                    environment = {"temperature": f"{temperature}C"}
                    compatible, notes = check_acid_base_compatibility(catalyst, role, solvent, environment)
                    features = build_features(solvent, catalyst, role, temperature)
                    rows.append(
                        {
                            "solvent": solvent["name"],
                            "catalyst_formula": catalyst["formula"],
                            "catalyst_role": role,
                            "temperature_c": temperature,
                            "is_compatible": int(compatible),
                            "label_source": "curated_rule_bootstrap",
                            "label_reason": " ".join(notes),
                            **features,
                        }
                    )
    return rows


def write_training_csv(path: Path = DATA_PATH) -> Path:
    rows = generate_rows()
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "solvent",
        "catalyst_formula",
        "catalyst_role",
        "temperature_c",
        "is_compatible",
        "label_source",
        "label_reason",
        *feature_columns(),
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return path
