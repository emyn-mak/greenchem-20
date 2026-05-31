from app.llm import LLMCompatibilityModel
from app.ml.model import CompatibilityModel


class GreenChemModel:
    def __init__(self) -> None:
        self.compatibility_model = CompatibilityModel()
        self.llm_model = LLMCompatibilityModel()

    @property
    def is_available(self) -> bool:
        return self.compatibility_model.is_available or self.llm_model.is_available

    def predict(self, current_solvent: dict, candidate_solvent: dict, catalyst: dict, catalyst_role: str, environment: dict) -> dict[str, object]:
        trained_result = self.compatibility_model.predict(candidate_solvent, catalyst, catalyst_role, environment)
        if trained_result["available"]:
            return trained_result

        llm_result = self.llm_model.predict(current_solvent, candidate_solvent, catalyst, catalyst_role, environment)
        if llm_result["available"]:
            llm_result["model_signal"] = (
                "LLM fallback used because no trained compatibility model artifact was found. "
                + llm_result["model_signal"]
            )
        return llm_result
