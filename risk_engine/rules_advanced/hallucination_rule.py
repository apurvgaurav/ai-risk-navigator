from typing import List, Dict, Optional
import re

from risk_engine.models import EvaluationContext, RiskFinding, RiskType, Severity
from risk_engine.rules_base import Rule


class HallucinationRule(Rule):
    """
    Naive hallucination check for 'What is the capital of X?' style questions.

    It only supports a small, explicit map of countries to capitals. If the prompt
    clearly asks for a capital we know, and the response does NOT mention the
    expected capital, we flag it as a hallucination risk.

    This is intentionally narrow and deterministic: it's a demo of how to plug
    factual checks into the engine, not a general QA system.
    """

    # Follow the same pattern as LatencySpikeRule / ToxicKeywordRule
    id = "HALL-001"
    name = "Naive Capital Hallucination Check"
    description = "Flags potential hallucinations for simple 'capital of X' questions."

    def __init__(self, capitals: Optional[Dict[str, List[str]]] = None) -> None:
        super().__init__()

        # Very small, explicit knowledge base
        # keys are lower-cased; values are lists of acceptable capital tokens
        self.capitals: Dict[str, List[str]] = capitals or {
            "france": ["paris"],
            "germany": ["berlin"],
            "italy": ["rome"],
            "spain": ["madrid"],
            "united kingdom": ["london"],
            "uk": ["london"],
            "india": ["new delhi", "delhi"],
            # United States variants
            "united states": ["washington", "washington dc", "washington d.c."],
            "united states of america": [
                "washington",
                "washington dc",
                "washington d.c.",
            ],
            "usa": ["washington", "washington dc", "washington d.c."],
            "us": ["washington", "washington dc", "washington d.c."],
        }

    def _extract_country(self, text: str) -> Optional[str]:
        """
        Look for patterns like 'capital of X' in the prompt.
        Returns a normalized country name or None.
        """
        lowered = text.lower()
        match = re.search(r"capital of\s+([a-z\s]+)\??", lowered)
        if not match:
            return None

        country = match.group(1).strip()
        # remove leading 'the ' if present (e.g. "the united states")
        if country.startswith("the "):
            country = country[4:]

        return country

    def apply(self, ctx: EvaluationContext) -> List[RiskFinding]:
        findings: List[RiskFinding] = []

        if not ctx.prompt or not ctx.response:
            return findings

        country = self._extract_country(ctx.prompt)
        if not country:
            # Prompt isn't clearly a capital question
            return findings

        expected_capitals = self.capitals.get(country)
        if not expected_capitals:
            # Country not in our tiny knowledge base
            return findings

        response_lower = ctx.response.lower()

        # If NONE of the expected tokens appear in the response, flag a risk
        if not any(token in response_lower for token in expected_capitals):
            findings.append(
                RiskFinding(
                    risk_type=RiskType.HALLUCINATION,
                    severity=Severity.HIGH,
                    rule_id=self.id,
                    rule_name=self.name,
                    message=(
                        f"Response may hallucinate the capital of '{country}'. "
                        f"Expected something like: {', '.join(expected_capitals)}."
                    ),
                    metadata={
                        "country": country,
                        "expected_capitals": expected_capitals,
                        "response_snippet": ctx.response[:200],
                    },
                )
            )

        return findings
