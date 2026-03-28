from fastapi import APIRouter

from ..repository import list_questions, upsert_question
from ..schemas import QuestionConfig, QuestionConfigInput
from ..services.grading import suggest_concepts


router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=list[QuestionConfig])
def get_questions() -> list[QuestionConfig]:
    return [QuestionConfig(**question) for question in list_questions()]


@router.post("", response_model=QuestionConfig)
def create_or_update_question(payload: QuestionConfigInput) -> QuestionConfig:
    expected_concepts = payload.expected_concepts or suggest_concepts(payload.model_answer)
    normalized_synonyms = {
        concept: [item.strip() for item in values if item.strip()]
        for concept, values in payload.synonyms.items()
    }
    question = upsert_question(
        {
            "id": payload.id,
            "question_text": payload.question_text.strip(),
            "model_answer": payload.model_answer.strip(),
            "expected_concepts": [concept.strip() for concept in expected_concepts if concept.strip()],
            "synonyms": normalized_synonyms,
            "weights": payload.weights.model_dump(),
        }
    )
    return QuestionConfig(**question)
