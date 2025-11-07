from __future__ import annotations

from typing import List

from ..models import EvaluationContext, RiskFinding, RiskType, Severity
from ..rules_base import Rule


class PromptInjectionRule(Rule):
    """
    Detects common prompt-injection / jailbreak phrases in prompt or response.
    """

    id = "INJ-001"
    name = "Prompt Injection Heuristic Detector"
    description = "Flags instructions that try to override prior rules or bypass safety."

    def __init__(self):
        super().__init__()
        self.patterns = [
            "ignore previous instructions",
            "ignore all previous instructions",
            "disregard previous instructions",
            "forget all previous instructions",
            "bypass safety",
            "bypass all safety",
            "jailbreak",
            "you are now dan",
            "do anything now",
            "act as if you are not an ai",
            "pretend you are not an ai",
            "override your guidelines",
        ]

    def _scan_text(self, text: str, location: str) -> List[RiskFinding]:
        findings: List[RiskFinding] = []
        lower = text.lower()

        for pattern in self.patterns:
            if pattern in lower:
                findings.append(
                    RiskFinding(
                        risk_type=RiskType.SAFETY,
                        severity=Severity.HIGH,
                        rule_id=self.id,
                        rule_name=self.name,
                        message=(
                            f"Potential prompt injection phrase detected in {location}: "
                            f"'{pattern}'."
                        ),
                        metadata={"pattern": pattern, "location": location},
                    )
                )

        return findings

    def apply(self, ctx: EvaluationContext) -> List[RiskFinding]:
        findings: List[RiskFinding] = []
        findings.extend(self._scan_text(ctx.prompt, "prompt"))
        findings.extend(self._scan_text(ctx.response, "response"))
        return findings
