from pydantic import BaseModel, Field
from typing import List, Optional

class AccuracyScores(BaseModel):
    semantic_coherence: float = Field(
        ..., description="Score 0.0 to 1.0. Does this reply address the actual questions/concerns in the incoming email?"
    )
    tone_consistency: float = Field(
        ..., description="Score 0.0 to 1.0. Does the reply mirror the politeness, vocabulary, and formatting of the retrieved examples?"
    )
    factual_confidence: float = Field(
        ..., description="Score 0.0 to 1.0. Does the reply contain unverified claims, incorrect instructions, or outright hallucinations?"
    )
    response_quality: float = Field(
        ..., description="Score 0.0 to 1.0. Is the reply grammatically sound, complete (greeting/body/sign-off), and well-structured?"
    )
    overall_accuracy: float = Field(
        ..., description="Weighted average: (0.30 * Coherence) + (0.25 * Tone) + (0.25 * Confidence) + (0.20 * Quality)"
    )

class ResponseDiagnostics(BaseModel):
    coherence_notes: str = Field(..., description="Justification for the semantic coherence score.")
    tone_notes: str = Field(..., description="Justification for the tone consistency score.")
    confidence_notes: str = Field(..., description="Justification for the factual confidence score.")
    quality_notes: str = Field(..., description="Justification for the structural quality score.")

class ResponseEvaluationReport(BaseModel):
    request_id: str
    incoming_email: str
    generated_reply: str
    metrics: AccuracyScores
    diagnostics: ResponseDiagnostics
    flags: List[str] = Field(default_factory=list, description="Critical issue tags (e.g., 'HALLUCINATION', 'RUDE_TONE', 'INCOMPLETE').")
    recommendation: str = Field(..., description="Must be one of: 'AUTO_SEND', 'SEND_WITH_REVIEW', or 'REJECT'.")
