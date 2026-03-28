from fastapi import APIRouter, HTTPException

from ..repository import (
    get_assignment,
    get_question,
    get_student,
    mark_assignment_graded,
    save_result,
)
from ..schemas import GradeRequest, GradeResult, ScoreWeights
from ..services.grading import grade_answer


router = APIRouter(prefix="/api/grade", tags=["grading"])


@router.post("", response_model=GradeResult)
def grade_student_answer(payload: GradeRequest) -> GradeResult:
    question = get_question(payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")

    assignment = None
    if payload.assignment_id:
        assignment = get_assignment(payload.assignment_id)
        if assignment is None:
            raise HTTPException(status_code=404, detail="Assignment not found.")
        if assignment["question_id"] != question["id"]:
            raise HTTPException(status_code=400, detail="Assignment does not match the selected question.")

    student = None
    resolved_student_id = payload.student_id or (assignment["student_id"] if assignment else None)
    if resolved_student_id:
        student = get_student(resolved_student_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found.")
        if assignment and assignment["student_id"] != student["id"]:
            raise HTTPException(status_code=400, detail="Assignment does not belong to this student.")

    weights = ScoreWeights(**question["weights"])
    graded = grade_answer(
        question_text=question["question_text"],
        model_answer=question["model_answer"],
        expected_concepts=question["expected_concepts"],
        synonyms=question["synonyms"],
        weights=weights,
        student_answer=payload.student_answer,
    )

    result = save_result(
        {
            "question_id": question["id"],
            "question_text": question["question_text"],
            "student_answer": payload.student_answer.strip(),
            "model_answer": question["model_answer"],
            "expected_concepts": question["expected_concepts"],
            "weights": weights.model_dump(),
            "student_id": student["id"] if student else None,
            "student_name": student["full_name"] if student else None,
            "assignment_id": assignment["id"] if assignment else payload.assignment_id,
            "keyword_score": graded.keyword_score,
            "semantic_score": graded.semantic_score,
            "depth_fact_score": graded.depth_fact_score,
            "bloom_level": graded.bloom_level,
            "bloom_score": graded.bloom_score,
            "grammar_score": graded.grammar_score,
            "facts_understanding_score": graded.facts_understanding_score,
            "final_score": graded.final_score,
            "reasoning": graded.reasoning,
            "feedback": graded.feedback,
        }
    )
    if assignment:
        mark_assignment_graded(assignment["id"], result["id"])

    return GradeResult(**result)
