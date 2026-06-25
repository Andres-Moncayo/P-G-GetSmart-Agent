from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml
from jinja2 import Environment, BaseLoader

from app.core.config import OPENSPEC_SYNTHESIS_YAML


class PromptLoader:
    """Loads system prompt and user template from the OpenSpec synthesis contract."""

    def __init__(self, yaml_path: Path | None = None) -> None:
        self.yaml_path = yaml_path or OPENSPEC_SYNTHESIS_YAML
        self._contract: Dict[str, Any] | None = None

    def load_contract(self) -> Dict[str, Any]:
        if self._contract is None:
            with open(self.yaml_path, encoding="utf-8") as handle:
                self._contract = yaml.safe_load(handle)
        return self._contract

    def get_system_prompt(self) -> str:
        contract = self.load_contract()
        return contract["system_prompt"].strip()

    def get_user_prompt_template(self) -> str:
        contract = self.load_contract()
        return contract["user_prompt_template"].strip()

    def get_model_config(self) -> Dict[str, Any]:
        contract = self.load_contract()
        return contract.get("model", {})

    def render_user_prompt(self, context: Dict[str, Any]) -> str:
        env = Environment(loader=BaseLoader())

        def to_json(value: Any) -> str:
            return json.dumps(value, indent=2, ensure_ascii=False, default=str)

        env.filters["tojson"] = to_json
        template = env.from_string(self.get_user_prompt_template())
        return template.render(**context)

    def get_workflow_steps(self) -> list[str]:
        contract = self.load_contract()
        workflow = contract.get("agent", {}).get("workflow", [])
        return [step["id"] for step in workflow]
