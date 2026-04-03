from typing import Literal, TypedDict


IntentType = Literal["transactional", "informational", "navigational"]
BuyerStage = Literal["awareness", "consideration", "decision"]
LabelType = Literal["HIGH_INTENT", "MEDIUM", "LOW"]
DecisionType = Literal["HIGH_VALUE_LEAD", "MEDIUM_VALUE_LEAD", "LOW_VALUE", "DISCARD"]
ActionabilityType = Literal["HIGH", "MEDIUM", "LOW"]


class IntentAnalysis(TypedDict):
    intent_type: IntentType
    buyer_stage: BuyerStage
    urgency: int


class ScoreBreakdown(TypedDict):
    service_relevance: int
    intent_match: int
    content_depth: int
    authority: int
    contact: int
    commercial_intent: int
    url_quality: int
    noise_penalty: int


class WeightedBreakdown(TypedDict):
    service_relevance: float
    intent_match: float
    content_depth: float
    authority: float
    contact: float
    commercial_intent: float
    url_quality: float
    noise_penalty: float


class ScoreExplanations(TypedDict):
    service_relevance: str
    intent_match: str
    content_depth: str
    authority: str
    contact: str
    commercial_intent: str
    url_quality: str
    noise_penalty: str


class ScoreResult(TypedDict):
    url: str
    score: float
    normalized_score: float
    label: LabelType
    intent_type: IntentType
    trust_score: float
    content_type: str
    breakdown: ScoreBreakdown
    weighted_breakdown: WeightedBreakdown
    explanations: ScoreExplanations
    entity: dict
    actionability_score: float
    reason: str


class FinalResult(TypedDict):
    company_name: str
    url: str
    normalized_score: float
    opportunity_score: float
    intent: IntentType
    decision: DecisionType
    actionability: ActionabilityType
    trust_score: float
    contact_available: bool
    key_signals: dict
    reason: str
