from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    intent: str
    confidence: float
    scores: Dict[str, float]


class RouteResponse(PredictResponse):
    route_to: str
    reason: str


class ExecuteRequest(TextRequest):
    context: Optional[str] = ""


class ExecuteResponse(RouteResponse):
    status: str
    answer: str
    actions: List[Dict[str, Any]]
