import re
from collections import Counter
from difflib import SequenceMatcher


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
    "when",
    "which",
    "this",
    "these",
    "those",
    "their",
    "than",
    "can",
    "used",
    "using",
}

COMMON_TYPOS = {
    "teh": "the",
    "recieve": "receive",
    "defination": "definition",
    "informtion": "information",
    "proces": "process",
    "databse": "database",
    "algorithim": "algorithm",
}


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def simple_lemmatize(token: str) -> str:
    for suffix in ("ingly", "edly", "ing", "ed", "ly", "es", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            return token[: -len(suffix)]
    return token


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    for typo, replacement in COMMON_TYPOS.items():
        lowered = re.sub(rf"\b{re.escape(typo)}\b", replacement, lowered)
    lowered = re.sub(r"[^a-z0-9\.\,\?\!\-\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def tokenize(text: str, keep_stopwords: bool = False) -> list[str]:
    normalized = normalize_text(text)
    tokens = [simple_lemmatize(token) for token in re.findall(r"[a-z0-9]+", normalized)]
    if keep_stopwords:
        return tokens
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def extract_key_concepts(text: str, limit: int = 8) -> list[str]:
    tokens = tokenize(text)
    counts = Counter(tokens)
    concepts = [token for token, _ in counts.most_common(limit * 2)]
    if not concepts:
        return []
    return concepts[:limit]


def lexical_similarity(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0

    overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    ratio = SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()
    return clamp((overlap * 0.6) + (ratio * 0.4))


def match_phrase_in_text(phrase: str, text: str) -> bool:
    phrase_tokens = tokenize(phrase)
    text_tokens = tokenize(text)
    if not phrase_tokens or not text_tokens:
        return False
    joined_text = " ".join(text_tokens)
    joined_phrase = " ".join(phrase_tokens)
    return joined_phrase in joined_text
