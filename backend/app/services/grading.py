from dataclasses import dataclass
from functools import lru_cache

from ..config import get_settings
from ..schemas import ScoreWeights
from .llm import review_depth_and_feedback
from .text_utils import clamp, extract_key_concepts, lexical_similarity, match_phrase_in_text, tokenize

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency fallback
    np = None
    SentenceTransformer = None


@dataclass
class GradeComputation:
    keyword_score: float
    semantic_score: float
    depth_fact_score: float
    bloom_level: str
    bloom_score: float
    grammar_score: float
    facts_understanding_score: float
    final_score: float
    reasoning: str
    feedback: str


@lru_cache(maxsize=1)
def _load_semantic_model():
    if SentenceTransformer is None:
        return None
    settings = get_settings()
    try:
        return SentenceTransformer(settings.semantic_model_name)
    except Exception:
        return None


def suggest_concepts(model_answer: str, limit: int = 8) -> list[str]:
    return extract_key_concepts(model_answer, limit=limit)


def compute_keyword_score(
    expected_concepts: list[str],
    synonyms: dict[str, list[str]],
    student_answer: str,
) -> float:
    if not expected_concepts:
        return 0.0

    hits = 0
    for concept in expected_concepts:
        matched = match_phrase_in_text(concept, student_answer)
        if not matched:
            for synonym in synonyms.get(concept, []):
                if match_phrase_in_text(synonym, student_answer):
                    matched = True
                    break
        if matched:
            hits += 1

    return round(clamp(hits / len(expected_concepts)), 4)


def compute_semantic_score(model_answer: str, student_answer: str) -> float:
    model = _load_semantic_model()
    if model is None or np is None:
        return round(lexical_similarity(model_answer, student_answer), 4)

    embeddings = model.encode([model_answer, student_answer], normalize_embeddings=True)
    score = float(np.dot(embeddings[0], embeddings[1]))
    return round(clamp((score + 1) / 2), 4)


def compute_grammar_score(student_answer: str) -> float:
    stripped = student_answer.strip()
    if not stripped:
        return 0.0

    sentences = [segment.strip() for segment in stripped.replace("?", ".").replace("!", ".").split(".") if segment.strip()]
    words = tokenize(student_answer, keep_stopwords=True)
    if not words:
        return 0.0

    sentence_count = max(len(sentences), 1)
    avg_sentence_length = len(words) / sentence_count
    length_fit = 1.0 - min(abs(avg_sentence_length - 14) / 20, 1.0)
    capitalization = 1.0 if stripped[0].isupper() else 0.6
    punctuation = 1.0 if stripped[-1] in ".?!" else 0.7
    word_variety = len(set(words)) / max(len(words), 1)
    very_short_penalty = 0.4 if len(words) < 8 else 1.0
    score = (length_fit * 0.35) + (capitalization * 0.15) + (punctuation * 0.15) + (word_variety * 0.35)
    return round(clamp(score * very_short_penalty), 4)


def grade_answer(
    question_text: str,
    model_answer: str,
    expected_concepts: list[str],
    synonyms: dict[str, list[str]],
    weights: ScoreWeights,
    student_answer: str,
) -> GradeComputation:
    keyword_score = compute_keyword_score(expected_concepts, synonyms, student_answer)
    semantic_score = compute_semantic_score(model_answer, student_answer)
    depth_review = review_depth_and_feedback(question_text, model_answer, student_answer)
    grammar_score = compute_grammar_score(student_answer)

    facts_understanding_score = round(
        clamp((semantic_score * 0.6) + (depth_review.score * 0.4)),
        4,
    )
    final_score = round(
        (
            (keyword_score * weights.keyword_coverage)
            + (grammar_score * weights.grammar_readability)
            + (facts_understanding_score * weights.facts_understanding)
        )
        * 10,
        1,
    )

    score_summary = (
        f"Keyword coverage {keyword_score:.2f}, semantic understanding {semantic_score:.2f}, "
        f"Bloom level {depth_review.bloom_level}, depth/factual review {depth_review.score:.2f}, grammar/readability {grammar_score:.2f}."
    )
    reasoning = f"{depth_review.reasoning} {score_summary}"

    return GradeComputation(
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        depth_fact_score=depth_review.score,
        bloom_level=depth_review.bloom_level,
        bloom_score=depth_review.bloom_score,
        grammar_score=grammar_score,
        facts_understanding_score=facts_understanding_score,
        final_score=final_score,
        reasoning=reasoning,
        feedback=depth_review.feedback,
    )
