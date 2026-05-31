from app.compatibility import check_acid_base_compatibility, catalyst_supports_role, validation_from_notes
from app.knowledge import find_catalyst, find_solvent, replacement_records, solvent_facts
from app.model_placeholder import GreenChemModel
from app.parser import parse_formula_text
from app.schemas import AnalyzeResponse, empty_environment_dict


REALITY_MESSAGE = "These are predictions based on literature and chemical rules. Wet lab validation required."


class GreenChemRecommender:
    def __init__(self):
        self.compatibility_model = GreenChemModel()

    def analyze(self, formula_text: str) -> AnalyzeResponse:
        if "is this real" in formula_text.lower():
            return AnalyzeResponse.model_validate(
                {
                    "detected_input": parse_formula_text(formula_text),
                    "current_formula": {},
                    "alternatives_found": 0,
                    "alternatives": [],
                    "validation_status": "Experimental required",
                    "status": "Information",
                    "message": REALITY_MESSAGE,
                    "human_validation_required": True,
                }
            )

        detected = parse_formula_text(formula_text)
        environment = detected["environment"]
        current_solvent = find_solvent(environment.get("solvent"))
        catalyst = find_catalyst(environment.get("catalyst"))
        catalyst_role = environment.get("catalyst_role")

        current_formula = {
            "solvent": solvent_facts(current_solvent),
            "catalyst_formula": catalyst.get("formula") if catalyst else environment.get("catalyst"),
            "catalyst_role": catalyst_role,
            "hazard_summary": hazard_summary(current_solvent, catalyst),
            "compatibility_warnings": [],
        }

        if current_solvent is None:
            return insufficient_data_response(
                detected,
                current_formula,
                "Current solvent is unknown or absent from the local knowledge base; no alternative proposed.",
            )

        if catalyst is None or not environment.get("catalyst"):
            return insufficient_data_response(
                detected,
                current_formula,
                "Catalyst formula is null or unknown; no alternative proposed.",
            )

        if not catalyst_role or not catalyst_supports_role(catalyst, catalyst_role):
            return insufficient_data_response(
                detected,
                current_formula,
                "Catalyst role is missing or not supported by the local catalyst lookup table; no alternative proposed.",
            )

        alternatives = []
        for record in replacement_records(current_solvent):
            candidate = find_solvent(record["to_solvent"])
            if candidate is None:
                continue

            compatible, notes = check_acid_base_compatibility(catalyst, catalyst_role, candidate, environment)
            if not compatible:
                continue

            ml_result = self.compatibility_model.predict(current_solvent, candidate, catalyst, catalyst_role, environment)
            if ml_result.get("available"):
                notes.append(str(ml_result["model_signal"]))
                if ml_result.get("is_compatible") is False:
                    continue
            else:
                notes.append(str(ml_result["model_signal"]))

            validation_status = validation_from_notes(record["status"], notes)
            alternatives.append(
                {
                    "rank": 0,
                    "replacement_solvent": solvent_facts(candidate),
                    "formula": replace_solvent_lines(detected["compounds"], current_solvent, candidate),
                    "environment": {**empty_environment_dict(), **environment, "solvent": candidate["name"]},
                    "compatibility_notes": notes,
                    "qualitative_benefits": qualitative_benefits(current_solvent, candidate),
                    "evidence": [
                        {
                            "source": "Local solvent knowledge base",
                            "statement": record["note"],
                        },
                        {
                            "source": "Internal acid/base compatibility rules",
                            "statement": "Candidate passed deterministic compatibility checks; this is not experimental proof.",
                        },
                        {
                            "source": "Prototype ML compatibility classifier",
                            "statement": model_evidence_statement(ml_result),
                        },
                    ],
                    "status": record["status"],
                    "validation_status": validation_status,
                }
            )

        alternatives = sorted(alternatives, key=alternative_sort_key)
        for index, alternative in enumerate(alternatives, start=1):
            alternative["rank"] = index

        if not alternatives:
            return AnalyzeResponse.model_validate(
                {
                    "detected_input": detected,
                    "current_formula": current_formula,
                    "alternatives_found": 0,
                    "alternatives": [],
                    "validation_status": "Experimental required",
                    "status": "No compatible alternative found",
                    "message": "No candidate passed the local knowledge-base and compatibility filters. Wet lab validation required.",
                    "human_validation_required": True,
                }
            )

        return AnalyzeResponse.model_validate(
            {
                "detected_input": detected,
                "current_formula": current_formula,
                "alternatives_found": len(alternatives),
                "alternatives": alternatives,
                "validation_status": response_validation_status(alternatives),
                "status": "Alternatives found",
                "message": REALITY_MESSAGE,
                "human_validation_required": True,
            }
        )


def insufficient_data_response(
    detected: dict,
    current_formula: dict,
    message: str,
) -> AnalyzeResponse:
    return AnalyzeResponse.model_validate(
        {
            "detected_input": detected,
            "current_formula": current_formula,
            "alternatives_found": 0,
            "alternatives": [],
            "validation_status": "Experimental required",
            "status": "Insufficient data",
            "message": message,
            "human_validation_required": True,
        }
    )


def hazard_summary(current_solvent: dict | None, catalyst: dict | None) -> list[str]:
    summary = []
    if current_solvent:
        summary.append(
            f"Solvent {current_solvent['name']}: GHS {format_codes(current_solvent.get('ghs_codes'))}; "
            f"CHEM21 {current_solvent.get('chem21_color', 'unknown')}; "
            f"boiling point {current_solvent.get('boiling_point_c')}C."
        )
    if catalyst:
        summary.append(f"Catalyst {catalyst['formula']}: GHS {format_codes(catalyst.get('ghs_codes'))}.")
    return summary


def qualitative_benefits(current_solvent: dict, candidate: dict) -> list[str]:
    benefits = [
        f"Solvent guide comparison: {candidate['name']} is {candidate.get('chem21_color')} vs {current_solvent['name']} is {current_solvent.get('chem21_color')}.",
        f"GHS comparison: {candidate['name']} {format_codes(candidate.get('ghs_codes'))} vs {current_solvent['name']} {format_codes(current_solvent.get('ghs_codes'))}.",
    ]

    current_bp = current_solvent.get("boiling_point_c")
    candidate_bp = candidate.get("boiling_point_c")
    if current_bp is not None and candidate_bp is not None:
        if candidate_bp > current_bp:
            benefits.append(f"Higher boiling point ({candidate_bp}C vs {current_bp}C) may reduce volatility but can require more energy for removal.")
        elif candidate_bp < current_bp:
            benefits.append(f"Lower boiling point ({candidate_bp}C vs {current_bp}C) may simplify removal but can increase volatility risk.")
        else:
            benefits.append(f"Similar boiling point ({candidate_bp}C vs {current_bp}C).")
    return benefits


def replace_solvent_lines(compounds: list[dict], current_solvent: dict, candidate: dict) -> list[str]:
    lines = []
    replaced = False
    for compound in compounds:
        name = compound.get("name")
        if name == current_solvent["name"]:
            name = candidate["name"]
            replaced = True
        lines.append(" ".join(part for part in [compound.get("quantity"), compound.get("unit"), name] if part))

    if not replaced:
        lines.append(f"Replace solvent: {current_solvent['name']} -> {candidate['name']}")
    return lines


def format_codes(codes: list[str] | None) -> str:
    return ", ".join(codes or ["no GHS code in local KB"])


def alternative_sort_key(alternative: dict) -> tuple[int, int, float]:
    color_rank = {"green": 0, "yellow": 1, "red": 2, "unknown": 3}
    validation_rank = {
        "Published": 0,
        "Predicted (compatible)": 1,
        "Predicted (uncertain)": 2,
        "Experimental required": 3,
    }
    solvent = alternative["replacement_solvent"]
    return (
        validation_rank.get(alternative["validation_status"], 3),
        color_rank.get(solvent["chem21_color"], 3),
        solvent["boiling_point_c"] or 999,
    )


def response_validation_status(alternatives: list[dict]) -> str:
    statuses = {alternative["validation_status"] for alternative in alternatives}
    if statuses == {"Published"}:
        return "Published"
    if "Predicted (uncertain)" in statuses:
        return "Predicted (uncertain)"
    if "Experimental required" in statuses:
        return "Experimental required"
    return "Predicted (compatible)"


def model_evidence_statement(ml_result: dict) -> str:
    if not ml_result.get("available"):
        return "No trained model artifact found; recommendation used rule-based compatibility only."
    return (
        f"{ml_result['model_signal']} Model trained on {ml_result.get('training_rows')} "
        f"curated rule-bootstrap rows; this is not experimental validation."
    )
