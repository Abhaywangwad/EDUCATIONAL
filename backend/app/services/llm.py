import json
from dataclasses import dataclass
from typing import Any

import httpx

from ..config import get_settings
from .text_utils import clamp, lexical_similarity, tokenize

BLOOM_SCORES = {
    "Remember": 0.2,
    "Understand": 0.4,
    "Apply": 0.6,
    "Analyze": 0.75,
    "Evaluate": 0.9,
    "Create": 1.0,
}


@dataclass
class DepthReview:
    score: float
    bloom_level: str
    bloom_score: float
    reasoning: str
    feedback: str


def _resolve_bloom_score(level: str) -> float:
    return BLOOM_SCORES.get(level, 0.4)


def _heuristic_bloom_level(student_answer: str, lexical: float, coverage: float) -> str:
    normalized = student_answer.lower()
    create_markers = {"design", "propose", "improve", "create", "build", "develop", "invent"}
    evaluate_markers = {"better", "best", "prefer", "advantage", "disadvantage", "trade-off", "should"}
    analyze_markers = {"because", "therefore", "whereas", "while", "difference", "compare", "impact", "reason"}
    apply_markers = {"for example", "for instance", "used in", "in practice", "application", "when used"}

    if any(marker in normalized for marker in create_markers):
        return "Create"
    if any(marker in normalized for marker in evaluate_markers):
        return "Evaluate"
    if any(marker in normalized for marker in analyze_markers):
        return "Analyze"
    if any(marker in normalized for marker in apply_markers):
        return "Apply"
    if lexical >= 0.42 or coverage >= 0.35:
        return "Understand"
    return "Remember"


def _heuristic_depth_review(question_text: str, model_answer: str, student_answer: str) -> DepthReview:
    reasoning_markers = {
        "because",
        "therefore",
        "so",
        "which",
        "allows",
        "helps",
        "used",
        "means",
        "while",
        "whereas",
        "for example",
    }

    answer_tokens = tokenize(student_answer, keep_stopwords=True)
    model_tokens = tokenize(model_answer)
    coverage = 0.0
    if model_tokens:
        coverage = len(set(answer_tokens) & set(model_tokens)) / len(set(model_tokens))

    marker_hits = sum(1 for marker in reasoning_markers if marker in student_answer.lower())
    sentence_count = max(student_answer.count("."), 1)
    avg_sentence_depth = min(marker_hits / sentence_count, 1.0)
    lexical = lexical_similarity(model_answer, student_answer)
    bloom_level = _heuristic_bloom_level(student_answer, lexical, coverage)
    bloom_score = _resolve_bloom_score(bloom_level)
    score = clamp((coverage * 0.45) + (avg_sentence_depth * 0.25) + (lexical * 0.30))
    score = clamp((score * 0.7) + (bloom_score * 0.3))

    if score >= 0.75:
        reasoning = f"The answer aligns with Bloom's level {bloom_level} because it explains the concept clearly and connects ideas beyond surface keywords."
        feedback = "Strong answer. To score even higher, add one more precise example or contrast."
    elif score >= 0.45:
        reasoning = f"The answer fits Bloom's level {bloom_level} because it covers the main idea, but it still needs stronger explanation or clearer connections between concepts."
        feedback = "Add cause-and-effect wording and one concrete example to improve depth."
    else:
        reasoning = f"The answer falls near Bloom's level {bloom_level} because it is too shallow or incomplete to show enough conceptual understanding."
        feedback = "State the main definition first, then explain why it matters or how it works."

    return DepthReview(
        score=round(score, 4),
        bloom_level=bloom_level,
        bloom_score=round(bloom_score, 4),
        reasoning=reasoning,
        feedback=feedback,
    )


def _extract_response_text(data: dict[str, Any]) -> str:
    direct_text = data.get("output_text")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text

    output = data.get("output", [])
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text
    return ""


def _openai_depth_review(
    question_text: str, model_answer: str, student_answer: str
) -> DepthReview:
    settings = get_settings()
    schema = {
        "name": "depth_grade",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "score": {"type": "number"},
                "bloom_level": {"type": "string", "enum": list(BLOOM_SCORES.keys())},
                "bloom_score": {"type": "number"},
                "reasoning": {"type": "string"},
                "feedback": {"type": "string"},
            },
            "required": ["score", "bloom_level", "bloom_score", "reasoning", "feedback"],
        },
        "strict": True,
    }
    prompt = (
        "You are grading a typed Computer Science theory answer for depth and factual quality only. "
        "Classify the answer into one Bloom's Taxonomy level from Remember, Understand, Apply, Analyze, Evaluate, Create. "
        "Set bloom_score using this scale exactly: Remember=0.2, Understand=0.4, Apply=0.6, Analyze=0.75, Evaluate=0.9, Create=1.0. "
        "Reward answers that explain meaning, contrast ideas, use examples, or show cause and effect. "
        "Penalize keyword stuffing, vague answers, and irrelevant details. "
        "The score must be between 0 and 1 and should reflect overall depth/factual quality, not just Bloom level.\n\n"
        f"Question:\n{question_text}\n\n"
        f"Teacher model answer:\n{model_answer}\n\n"
        f"Student answer:\n{student_answer}"
    )
    payload = {
        "model": settings.llm_model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Return only the requested JSON object.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
        "text": {"format": {"type": "json_schema", **schema}},
    }

    with httpx.Client(timeout=20) as client:
        response = client.post(
            f"{settings.resolved_llm_base_url.rstrip('/')}/responses",
            headers={
                "Authorization": f"Bearer {settings.resolved_llm_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        content = _extract_response_text(data)
        parsed = json.loads(content)
        return DepthReview(
            score=round(clamp(float(parsed.get("score", 0.0))), 4),
            bloom_level=str(parsed.get("bloom_level", "Understand")).strip() or "Understand",
            bloom_score=round(clamp(float(parsed.get("bloom_score", 0.4))), 4),
            reasoning=str(parsed.get("reasoning", "")).strip() or "The model reviewed the answer depth.",
            feedback=str(parsed.get("feedback", "")).strip() or "Clarify the explanation and add one specific example.",
        )


def _chat_completions_depth_review(
    question_text: str, model_answer: str, student_answer: str
) -> DepthReview:
    settings = get_settings()
    prompt = (
        "You are grading a typed Computer Science theory answer.\n"
        "Score only the depth and factual quality of the student's answer against the model answer.\n"
        "Classify the answer into one Bloom's Taxonomy level from Remember, Understand, Apply, Analyze, Evaluate, Create.\n"
        "Return strict JSON with keys: score, bloom_level, bloom_score, reasoning, feedback.\n"
        "Use bloom_score exactly as: Remember=0.2, Understand=0.4, Apply=0.6, Analyze=0.75, Evaluate=0.9, Create=1.0.\n"
        "score must be a number between 0 and 1.\n"
        f"Question: {question_text}\n"
        f"Model answer: {model_answer}\n"
        f"Student answer: {student_answer}\n"
    )

    payload = {
        "model": settings.llm_model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "You return concise JSON only.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    with httpx.Client(timeout=20) as client:
        response = client.post(
            f"{settings.resolved_llm_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.resolved_llm_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return DepthReview(
            score=round(clamp(float(parsed.get("score", 0.0))), 4),
            bloom_level=str(parsed.get("bloom_level", "Understand")).strip() or "Understand",
            bloom_score=round(clamp(float(parsed.get("bloom_score", 0.4))), 4),
            reasoning=str(parsed.get("reasoning", "")).strip() or "The model reviewed the answer depth.",
            feedback=str(parsed.get("feedback", "")).strip() or "Clarify the explanation and add one specific example.",
        )


def review_depth_and_feedback(question_text: str, model_answer: str, student_answer: str) -> DepthReview:
    settings = get_settings()
    if settings.llm_provider == "mock" or not settings.resolved_llm_api_key:
        return _heuristic_depth_review(question_text, model_answer, student_answer)

    try:
        if settings.llm_provider == "openai":
            return _openai_depth_review(question_text, model_answer, student_answer)
        return _chat_completions_depth_review(question_text, model_answer, student_answer)
    except Exception:
        return _heuristic_depth_review(question_text, model_answer, student_answer)
