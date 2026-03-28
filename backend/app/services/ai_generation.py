import json
import re
from collections import Counter
from typing import Any

import httpx

from ..config import get_settings
from ..schemas import GeneratedQuestionSuggestion
from .text_utils import extract_key_concepts


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


def _call_openai_json(prompt: str, schema_name: str, schema: dict[str, Any]) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.resolved_llm_api_key:
        return None

    payload = {
        "model": settings.llm_model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": "Return only the requested JSON object."}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }
        },
    }

    try:
        with httpx.Client(timeout=25) as client:
            response = client.post(
                f"{settings.resolved_llm_base_url.rstrip('/')}/responses",
                headers={
                    "Authorization": f"Bearer {settings.resolved_llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            content = _extract_response_text(response.json())
            return json.loads(content)
    except Exception:
        return None


def _call_openai_text(prompt: str) -> str | None:
    settings = get_settings()
    if not settings.resolved_llm_api_key:
        return None

    payload = {
        "model": settings.llm_model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": "Write a concise, professional answer only."}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            },
        ],
    }

    try:
        with httpx.Client(timeout=25) as client:
            response = client.post(
                f"{settings.resolved_llm_base_url.rstrip('/')}/responses",
                headers={
                    "Authorization": f"Bearer {settings.resolved_llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            return _extract_response_text(response.json()).strip() or None
    except Exception:
        return None


def _pick_supporting_sentences(text: str, limit: int = 3) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if len(sentence.strip()) > 60
    ]
    return sentences[:limit]


def generate_question_suggestions_from_text(text: str, limit: int = 3) -> list[GeneratedQuestionSuggestion]:
    excerpt = text[:4000]
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "suggestions": {
                "type": "array",
                "minItems": 1,
                "maxItems": limit,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "question_text": {"type": "string"},
                        "model_answer": {"type": "string"},
                        "expected_concepts": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                            "maxItems": 5,
                        },
                        "source_excerpt": {"type": "string"},
                    },
                    "required": ["question_text", "model_answer", "expected_concepts", "source_excerpt"],
                },
            }
        },
        "required": ["suggestions"],
    }
    prompt = (
        "You are helping a teacher create short-answer Computer Science questions from a textbook excerpt.\n"
        f"Generate up to {limit} useful subjective questions.\n"
        "For each suggestion, include:\n"
        "- question_text\n"
        "- model_answer\n"
        "- expected_concepts (2 to 5 short concepts)\n"
        "- source_excerpt\n"
        "Use only the provided text.\n\n"
        f"Textbook excerpt:\n{excerpt}"
    )
    parsed = _call_openai_json(prompt, "textbook_question_suggestions", schema)
    if parsed and isinstance(parsed.get("suggestions"), list):
        return [
            GeneratedQuestionSuggestion(**item)
            for item in parsed["suggestions"][:limit]
        ]

    supporting_sentences = _pick_supporting_sentences(text, limit=limit)
    if not supporting_sentences:
        supporting_sentences = [text[:300].strip()] if text.strip() else []

    suggestions: list[GeneratedQuestionSuggestion] = []
    for sentence in supporting_sentences[:limit]:
        concepts = extract_key_concepts(sentence, limit=4)
        lead_concept = concepts[0] if concepts else "the main concept"
        question_text = f"Explain {lead_concept} in your own words."
        suggestions.append(
            GeneratedQuestionSuggestion(
                question_text=question_text[0].upper() + question_text[1:],
                model_answer=sentence,
                expected_concepts=concepts[:4] or ["definition", "purpose"],
                source_excerpt=sentence[:220],
            )
        )
    return suggestions


def generate_student_report_text(
    student_name: str,
    question_text: str,
    final_score: float,
    bloom_level: str,
    keyword_score: float,
    semantic_score: float,
    grammar_score: float,
    feedback: str,
) -> str:
    prompt = (
        "Write a short, professional student performance report.\n"
        "Use a supportive teacher tone.\n"
        "Mention the overall score, Bloom level, strengths, weaknesses, and one next-step suggestion.\n"
        "Keep it between 120 and 160 words.\n\n"
        f"Student Name: {student_name}\n"
        f"Question: {question_text}\n"
        f"Final Score: {final_score}/10\n"
        f"Bloom Level: {bloom_level}\n"
        f"Keyword Score: {keyword_score:.2f}\n"
        f"Semantic Score: {semantic_score:.2f}\n"
        f"Grammar Score: {grammar_score:.2f}\n"
        f"Feedback Hint: {feedback}\n"
    )
    generated = _call_openai_text(prompt)
    if generated:
        return generated

    performance_label = "strong" if final_score >= 7 else "developing" if final_score >= 4 else "early-stage"
    return (
        f"{student_name}'s answer shows {performance_label} performance on the question \"{question_text}\". "
        f"The current score is {final_score}/10 with a Bloom level of {bloom_level}, which suggests the response "
        f"demonstrates {'clear conceptual depth' if final_score >= 7 else 'partial understanding' if final_score >= 4 else 'limited conceptual understanding'}. "
        f"Keyword coverage, meaning alignment, and readability together indicate where the answer was strongest. "
        f"Next, the student should focus on {feedback.lower()}"
    )


def generate_class_report_text(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No graded results are available yet. Grade a few answers to generate a class insight report."

    scores = [float(item["final_score"]) for item in results]
    average_score = sum(scores) / len(scores)
    bloom_counts = Counter(item.get("bloom_level", "Understand") for item in results)
    common_bloom = bloom_counts.most_common(1)[0][0]
    top_result = max(results, key=lambda item: item["final_score"])
    low_result = min(results, key=lambda item: item["final_score"])

    prompt = (
        "Write a concise class performance report for a teacher.\n"
        "Include overall trend, common Bloom depth, one strength, one weakness, and one next action.\n"
        "Keep it between 130 and 170 words.\n\n"
        f"Total graded responses: {len(results)}\n"
        f"Average score: {average_score:.1f}/10\n"
        f"Most common Bloom level: {common_bloom}\n"
        f"Highest score: {top_result['final_score']}/10 on {top_result['question_text']}\n"
        f"Lowest score: {low_result['final_score']}/10 on {low_result['question_text']}\n"
    )
    generated = _call_openai_text(prompt)
    if generated:
        return generated

    return (
        f"The current class snapshot is based on {len(results)} graded responses, with an average score of "
        f"{average_score:.1f}/10. The most common Bloom level is {common_bloom}, which suggests where most answers "
        f"currently sit in terms of cognitive depth. The strongest recent performance came on \"{top_result['question_text']}\" "
        f"with a score of {top_result['final_score']}/10, while \"{low_result['question_text']}\" had the lowest score at "
        f"{low_result['final_score']}/10. The next teaching step should be to model one deeper, example-rich answer and "
        f"then let students compare it with a surface-level response."
    )
