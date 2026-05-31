import re
from typing import Any


def parse_temperature_c(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"[-+]?\d+(\.\d+)?", value)
    if not match:
        return None
    return float(match.group(0))


def catalyst_supports_role(catalyst: dict[str, Any], role: str | None) -> bool:
    if not role:
        return False
    normalized_role = role.strip().lower()
    return normalized_role in {item.lower() for item in catalyst.get("roles", [])}


def check_acid_base_compatibility(
    catalyst: dict[str, Any],
    catalyst_role: str,
    solvent: dict[str, Any],
    environment: dict[str, Any],
) -> tuple[bool, list[str]]:
    notes: list[str] = []
    role = catalyst_role.lower()
    solvent_incompatibilities = set(solvent.get("known_incompatibilities", []))
    catalyst_incompatibilities = set(catalyst.get("known_incompatibilities", []))
    temperature_c = parse_temperature_c(environment.get("temperature"))
    heated = temperature_c is not None and temperature_c >= 50

    if role in {"acid_catalyst", "strong_acid"}:
        if "strong_acid" in solvent_incompatibilities:
            return False, [f"{solvent['name']} is flagged as incompatible with strong acid in the local knowledge base."]

        if (
            solvent["name"] == "Ethanol"
            and heated
            and "alcohol_heat_dehydration" in catalyst_incompatibilities
        ):
            return False, ["Ethanol + H2SO4 + heat can promote ether/dehydration side reactions."]

        if "strong_acid_hydrolysis" in solvent_incompatibilities:
            notes.append(f"{solvent['name']} may hydrolyze under strong acid; mark as uncertain unless literature supports this case.")

    if role in {"base_catalyst", "strong_base", "weak_base"}:
        if "strong_base" in solvent_incompatibilities:
            return False, [f"{solvent['name']} is flagged as incompatible with strong base in the local knowledge base."]

        if "ester_hydrolysis" in catalyst_incompatibilities and solvent["name"] == "Ethyl acetate":
            return False, ["Ethyl acetate can undergo base-promoted hydrolysis with strong base catalysts."]

        if "strong_base_hydrolysis" in solvent_incompatibilities:
            notes.append(f"{solvent['name']} has base-hydrolysis risk; experimental validation is required.")

    if not notes:
        notes.append(f"{solvent['name']} passed the local acid/base compatibility screen for {catalyst['formula']} as {catalyst_role}.")

    return True, notes


def validation_from_notes(default_status: str, notes: list[str]) -> str:
    if any("uncertain" in note.lower() or "experimental" in note.lower() for note in notes):
        return "Predicted (uncertain)"
    if default_status == "Literature reported":
        return "Published"
    if default_status == "Theoretically compatible":
        return "Predicted (compatible)"
    return "Experimental required"
