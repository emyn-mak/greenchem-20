import re
from typing import Any

from app.knowledge import find_solvent
from app.schemas import empty_environment_dict


KNOWN_FORMULAS = {
    "h2o": "H2O",
    "water": "H2O",
    "acetone": "C3H6O",
    "ethanol": "C2H6O",
    "ethyl acetate": "C4H8O2",
    "h2so4": "H2SO4",
    "sulfuric acid": "H2SO4",
    "hcl": "HCl",
    "naoh": "NaOH",
    "k2co3": "K2CO3",
}

ENVIRONMENT_ALIASES = {
    "temperature": "temperature",
    "temp": "temperature",
    "time": "time",
    "light": "light",
    "humidity": "humidity",
    "pressure": "pressure",
    "stirring": "stirring",
    "ph": "ph",
    "atmosphere": "atmosphere",
    "solvent": "solvent",
    "catalyst": "catalyst",
    "catalyst formula": "catalyst",
    "catalyst role": "catalyst_role",
    "role": "catalyst_role",
    "concentration": "concentration",
    "wavelength": "wavelength",
    "voltage": "voltage",
    "current": "current",
    "flow_rate": "flow_rate",
    "flow rate": "flow_rate",
}


def parse_formula_text(formula_text: str) -> dict[str, Any]:
    environment = empty_environment_dict()
    compounds: list[dict[str, str | None]] = []

    for raw_line in formula_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" in line:
            key, value = [part.strip() for part in line.split(":", 1)]
            field = ENVIRONMENT_ALIASES.get(key.lower())
            if field:
                environment[field] = normalize_value(value)
            continue

        compound = parse_compound_line(line)
        if compound:
            compounds.append(compound)

    infer_solvent_from_compounds(environment, compounds)
    infer_catalyst_from_compounds(environment, compounds)
    return {"compounds": compounds, "environment": environment}


def parse_compound_line(line: str) -> dict[str, str | None] | None:
    match = re.match(r"^([\d.]+)\s*([A-Za-z/%]+)?\s+(.+)$", line)
    if not match:
        return None

    quantity, unit, raw_name = match.groups()
    name = raw_name.strip()
    formula = formula_for(name)
    role = None
    if "catalyst" in name.lower():
        role = "catalyst"

    return {
        "quantity": quantity,
        "unit": unit,
        "name": friendly_name(name),
        "formula": formula,
        "role": role,
    }


def normalize_value(value: str) -> str | None:
    cleaned = value.strip()
    if cleaned.lower() in {"", "null", "none", "unknown"}:
        return None
    return cleaned


def friendly_name(value: str) -> str:
    key = value.strip().lower()
    names = {
        "h2o": "Water",
        "h2so4": "Sulfuric acid",
        "hcl": "Hydrochloric acid",
        "naoh": "Sodium hydroxide",
        "k2co3": "Potassium carbonate",
    }
    solvent = find_solvent(value)
    if solvent:
        return solvent["name"]
    return names.get(key, value)


def formula_for(value: str) -> str | None:
    key = value.strip().lower()
    solvent = find_solvent(value)
    if solvent:
        return solvent.get("formula")
    if key in KNOWN_FORMULAS:
        return KNOWN_FORMULAS[key]
    return value if re.search(r"\d", value) else None


def infer_solvent_from_compounds(environment: dict[str, Any], compounds: list[dict[str, Any]]) -> None:
    if environment.get("solvent"):
        return

    for compound in compounds:
        if find_solvent(compound.get("name")) or find_solvent(compound.get("formula")):
            if compound.get("name") != "Water":
                environment["solvent"] = compound.get("name")
                return


def infer_catalyst_from_compounds(environment: dict[str, Any], compounds: list[dict[str, Any]]) -> None:
    if environment.get("catalyst"):
        return

    for compound in compounds:
        name = (compound.get("name") or "").lower()
        if "catalyst" in name and compound.get("formula"):
            environment["catalyst"] = compound["formula"]
            return
