from app.compatibility import parse_temperature_c


GHS_FEATURE_CODES = ["H225", "H301", "H302", "H311", "H312", "H315", "H319", "H331", "H332", "H336", "H370"]
COLOR_RANK = {"green": 0, "yellow": 1, "red": 2, "unknown": 3}


def build_features(solvent: dict, catalyst: dict, catalyst_role: str, temperature: str | float | None) -> dict[str, float]:
    temperature_c = temperature if isinstance(temperature, (int, float)) else parse_temperature_c(temperature)
    solvent_ghs = set(solvent.get("ghs_codes", []))
    catalyst_roles = {role.lower() for role in catalyst.get("roles", [])}
    solvent_incompatibilities = solvent.get("known_incompatibilities", [])
    catalyst_incompatibilities = catalyst.get("known_incompatibilities", [])

    features = {
        "boiling_point_c": float(solvent.get("boiling_point_c") or 0),
        "temperature_c": float(temperature_c or 25),
        "chem21_rank": float(COLOR_RANK.get(solvent.get("chem21_color", "unknown"), 3)),
        "solvent_ghs_count": float(len(solvent_ghs)),
        "solvent_incompatibility_count": float(len(solvent_incompatibilities)),
        "catalyst_incompatibility_count": float(len(catalyst_incompatibilities)),
        "is_acid_role": float(catalyst_role in {"acid_catalyst", "strong_acid"}),
        "is_base_role": float(catalyst_role in {"base_catalyst", "strong_base", "weak_base"}),
        "catalyst_supports_role": float(catalyst_role.lower() in catalyst_roles),
        "is_heated": float((temperature_c or 25) >= 50),
    }

    for code in GHS_FEATURE_CODES:
        features[f"has_{code}"] = float(code in solvent_ghs)

    return features


def feature_columns() -> list[str]:
    base = [
        "boiling_point_c",
        "temperature_c",
        "chem21_rank",
        "solvent_ghs_count",
        "solvent_incompatibility_count",
        "catalyst_incompatibility_count",
        "is_acid_role",
        "is_base_role",
        "catalyst_supports_role",
        "is_heated",
    ]
    return base + [f"has_{code}" for code in GHS_FEATURE_CODES]


def vectorize(features: dict[str, float]) -> list[float]:
    return [features[column] for column in feature_columns()]
