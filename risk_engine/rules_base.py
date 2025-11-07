from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .models import EvaluationContext, RiskFinding


class Rule(ABC):
    """
    Abstract base class for all rules.
    Deterministic, non-ML, pure functions over EvaluationContext.
    """

    id: str
    name: str
    description: str

    def __init__(self):
        if not hasattr(self, "id"):
            raise ValueError("Rule must define 'id'")
        if not hasattr(self, "name"):
            raise ValueError("Rule must define 'name'")
        if not hasattr(self, "description"):
            self.description = ""

    @abstractmethod
    def apply(self, ctx: EvaluationContext) -> List[RiskFinding]:
        """Evaluate this rule against the given context."""
        ...
