import json
from functools import lru_cache
from pathlib import Path
from typing import Any


KB_PATH = Path(__file__).with_name("knowledge_base.json")


@lru_cache
def load_knowledge_base() -> dict[str, Any]:
    with KB_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def all_solvents() -> list[dict[str, Any]]:
    return load_knowledge_base()["solvents"]


def all_catalysts() -> list[dict[str, Any]]:
    return load_knowledge_base()["catalysts"]


def reported_replacements() -> list[dict[str, Any]]:
    return load_knowledge_base()["reported_replacements"]


def normalize_key(value: str | None) -> str:
    return (value or "").strip().lower()


def find_solvent(value: str | None) -> dict[str, Any] | None:
    key = normalize_key(value)
    if not key:
        return None

    for solvent in all_solvents():
        names = [solvent["name"], solvent.get("formula"), *solvent.get("aliases", [])]
        if key in {normalize_key(name) for name in names if name}:
            return solvent
    return None


def find_catalyst(value: str | None) -> dict[str, Any] | None:
    key = normalize_key(value)
    if not key:
        return None

    for catalyst in all_catalysts():
        names = [catalyst["formula"], catalyst["name"]]
        if key in {normalize_key(name) for name in names if name}:
            return catalyst
    return None


def solvent_facts(solvent: dict[str, Any] | None) -> dict[str, Any] | None:
    if solvent is None:
        return None
    return {
        "name": solvent["name"],
        "formula": solvent.get("formula"),
        "ghs_codes": solvent.get("ghs_codes", []),
        "boiling_point_c": solvent.get("boiling_point_c"),
        "chem21_color": solvent.get("chem21_color", "unknown"),
    }


def replacement_records(current_solvent: dict[str, Any]) -> list[dict[str, Any]]:
    current_name = current_solvent["name"]
    records = [
        item
        for item in reported_replacements()
        if normalize_key(item["from_solvent"]) == normalize_key(current_name)
    ]

    if records:
        return records

    greener = []
    current_color = current_solvent.get("chem21_color")
    for solvent in all_solvents():
        if solvent["name"] == current_name:
            continue
        if solvent.get("chem21_color") == "green" or current_color == "red":
            greener.append(
                {
                    "from_solvent": current_name,
                    "to_solvent": solvent["name"],
                    "status": "Requires experiment",
                    "validation_status": "Experimental required",
                    "note": "Generated from internal solvent guide color ranking; no reaction-specific literature match in the local knowledge base.",
                }
            )
    return greener[:5]
