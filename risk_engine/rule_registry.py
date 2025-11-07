import importlib
import yaml
from pathlib import Path
from typing import Any, Dict, List

from .rules_base import Rule


class RuleRegistry:
    """
    Loads rule definitions from YAML and instantiates rule classes dynamically.
    """

    def __init__(self, config_path: str = "config/policies.yaml"):
        self.config_path = Path(config_path)
        self.rules: List[Rule] = []
        self.policy_meta: Dict[str, Any] = {}

    def load(self) -> List[Rule]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Policy config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        self.policy_meta = config.get("policy", {})

        for rule_conf in config.get("rules", []):
            if not rule_conf.get("enabled", True):
                continue

            module_name = rule_conf["module"]
            class_name = rule_conf["class"]
            params = rule_conf.get("params", {})

            module = importlib.import_module(module_name)
            rule_cls = getattr(module, class_name)
            rule_obj = rule_cls(**params)
            self.rules.append(rule_obj)

        return self.rules

    def get_rules(self) -> List[Rule]:
        return self.rules
