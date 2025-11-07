from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class RiskType(str, Enum):
    HALLUCINATION = "hallucination"
    BIAS = "bias"
    LATENCY = "latency"
    SAFETY = "safety"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFinding(BaseModel):
    """Single risk finding produced by a rule."""
    risk_type: RiskType
    severity: Severity
    rule_id: str
    rule_name: str
    message: str
    metadata: Dict[str, Any] = {}


class EvaluationContext(BaseModel):
    """
    Input to the engine for one LLM call.
    In real system this will come from your app / logs.
    """
    prompt: str
    response: str
    latency_ms: Optional[float] = None
    model_name: Optional[str] = None
    user_id: Optional[str] = None
    source: Optional[str] = None  # e.g., "chat", "api", "batch"
    extra: Dict[str, Any] = {}
