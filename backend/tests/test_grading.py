import unittest

from app.schemas import ScoreWeights
from app.services.grading import grade_answer

BLOOM_ORDER = {
    "Remember": 1,
    "Understand": 2,
    "Apply": 3,
    "Analyze": 4,
    "Evaluate": 5,
    "Create": 6,
}


class GradingTests(unittest.TestCase):
    def test_deep_answer_beats_surface_answer(self) -> None:
        weights = ScoreWeights()
        question = "Why is normalization important in DBMS?"
        model_answer = (
            "Normalization organizes tables to reduce redundancy, improve consistency, "
            "prevent anomalies, and simplify maintenance."
        )
        expected_concepts = [
            "reduce redundancy",
            "data consistency",
            "prevent anomalies",
            "easy maintenance",
        ]
        synonyms = {
            "data consistency": ["consistency"],
            "easy maintenance": ["simple maintenance", "simplify maintenance"],
        }

        shallow = grade_answer(
            question,
            model_answer,
            expected_concepts,
            synonyms,
            weights,
            "Normalization means database tables. It is used in DBMS.",
        )
        deep = grade_answer(
            question,
            model_answer,
            expected_concepts,
            synonyms,
            weights,
            (
                "Normalization is important because it removes repeated data and keeps records consistent. "
                "It also prevents update anomalies, so the database is easier to maintain and trust."
            ),
        )

        self.assertGreater(deep.final_score, shallow.final_score)
        self.assertGreaterEqual(BLOOM_ORDER[deep.bloom_level], BLOOM_ORDER[shallow.bloom_level])


if __name__ == "__main__":
    unittest.main()
