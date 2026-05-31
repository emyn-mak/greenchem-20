import json
import urllib.error
import urllib.request
from typing import Any

from app.config import get_settings


class LLMCompatibilityModel:
    def __init__(self) -> None:
        settings = get_settings()
        self.use_mock = settings.use_mock_llm
        self.provider = settings.llm_provider
        self.api_key = settings.openai_api_key
        self.api_base = settings.openai_api_base or "https://api.openai.com/v1"
        self.api_version = settings.openai_api_version
        self.model = settings.openai_model or "gpt-4o-mini"

    @property
    def is_available(self) -> bool:
        if self.use_mock and self.provider == "mock":
            return True
        return bool(self.api_key)

    def predict(self, current_solvent: dict, candidate_solvent: dict, catalyst: dict, catalyst_role: str, environment: dict) -> dict[str, object]:
        if not self.is_available:
            return {
                "available": False,
                "is_compatible": None,
                "model_signal": "No LLM API key configured; rule-based compatibility only.",
            }

        if self.use_mock and self.provider == "mock":
            return self.predict_mock(current_solvent, candidate_solvent, catalyst, catalyst_role, environment)

        prompt = self.build_prompt(current_solvent, candidate_solvent, catalyst, catalyst_role, environment)
        try:
            response_text = self.call_openai_chat(prompt)
        except Exception as error:
            return {
                "available": False,
                "is_compatible": None,
                "model_signal": f"LLM compatibility fallback failed: {error}",
            }

        parsed = self.parse_response(response_text)
        return {
            "available": True,
            "is_compatible": parsed.get("compatible"),
            "probability_compatible": parsed.get("confidence"),
            "model_signal": parsed.get("reason") or response_text,
            "llm_response": response_text,
        }

    def predict_mock(self, current_solvent: dict, candidate_solvent: dict, catalyst: dict, catalyst_role: str, environment: dict) -> dict[str, object]:
        candidate_color = candidate_solvent.get("chem21_color")
        current_color = current_solvent.get("chem21_color")
        color_compatibility = {
            ("green", "green"): True,
            ("green", "yellow"): True,
            ("yellow", "green"): True,
            ("yellow", "yellow"): True,
            ("red", "green"): False,
            ("red", "yellow"): False,
            ("red", "red"): False,
        }
        
        compatible = color_compatibility.get((current_color, candidate_color), True)
        confidence = 0.85 if compatible else 0.75
        reason = (
            f"Mock LLM: {candidate_solvent.get('name')} ({candidate_color}) is "
            f"{'compatible' if compatible else 'incompatible'} with {current_solvent.get('name')} "
            f"({current_color}) for {catalyst_role}."
        )

        return {
            "available": True,
            "is_compatible": compatible,
            "probability_compatible": confidence,
            "model_signal": reason,
            "llm_response": reason,
        }

    def build_prompt(
        self,
        current_solvent: dict,
        candidate_solvent: dict,
        catalyst: dict,
        catalyst_role: str,
        environment: dict,
    ) -> str:
        environment_lines = "\n".join(f"- {key}: {value}" for key, value in environment.items() if value)
        return (
            "You are a chemistry assistant. Answer only in valid JSON with keys: compatible (true or false), "
            "confidence (0.0-1.0), and reason (brief explanation).\n\n"
            "Current solvent:\n"
            f"- name: {current_solvent.get('name')}\n"
            f"- chem21_color: {current_solvent.get('chem21_color')}\n"
            f"- ghs_codes: {current_solvent.get('ghs_codes')}\n"
            f"- boiling_point_c: {current_solvent.get('boiling_point_c')}\n\n"
            "Candidate solvent:\n"
            f"- name: {candidate_solvent.get('name')}\n"
            f"- chem21_color: {candidate_solvent.get('chem21_color')}\n"
            f"- ghs_codes: {candidate_solvent.get('ghs_codes')}\n"
            f"- boiling_point_c: {candidate_solvent.get('boiling_point_c')}\n\n"
            "Catalyst:\n"
            f"- formula: {catalyst.get('formula') if catalyst else environment.get('catalyst')}\n"
            f"- role: {catalyst_role}\n\n"
            "Environment:\n"
            f"{environment_lines}\n\n"
            "Is the candidate solvent compatible with the catalyst and reaction environment?"
        )

    def call_openai_chat(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a technical chemistry assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 300,
        }

        url = self.build_api_url()
        headers = self.build_headers()
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8")
            payload = json.loads(body)
            return payload["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"LLM request failed: {exc.code} {exc.reason}")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM request failed: {exc.reason}")

    def build_api_url(self) -> str:
        if "openai.azure.com" in self.api_base:
            api_version_param = f"?api-version={self.api_version or '2023-05-15'}"
            return f"{self.api_base}/openai/deployments/{self.model}/chat/completions{api_version_param}"
        return f"{self.api_base.rstrip('/')}/chat/completions"

    def build_headers(self) -> dict[str, str]:
        if "openai.azure.com" in self.api_base:
            return {
                "Content-Type": "application/json",
                "api-key": self.api_key,
            }
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def parse_response(self, response_text: str) -> dict[str, Any]:
        try:
            candidate = json.loads(response_text)
            return {
                "compatible": bool(candidate.get("compatible")),
                "confidence": float(candidate.get("confidence", 0.0)) if candidate.get("confidence") is not None else None,
                "reason": candidate.get("reason"),
            }
        except Exception:
            compatible = "true" in response_text.lower()
            return {
                "compatible": compatible,
                "confidence": None,
                "reason": response_text,
            }
