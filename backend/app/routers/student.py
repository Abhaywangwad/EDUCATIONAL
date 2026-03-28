from fastapi import APIRouter, HTTPException, Query

from ..repository import (
    get_assignment,
    get_question,
    get_student,
    get_student_result,
    list_student_assignments,
    mark_assignment_graded,
    save_result,
)
from ..schemas import (
    ScoreWeights,
    StudentAssessmentDetail,
    StudentAssessmentsResponse,
    StudentAssessmentSummary,
    StudentPortalResult,
    StudentSubmissionRequest,
)
from ..services.grading import grade_answer
from ..services.reporting import build_student_portal_result_payload


router = APIRouter(prefix="/api/student", tags=["student"])


@router.get("/assessments", response_model=StudentAssessmentsResponse)
def get_student_assessments(student_id: str = Query(...)) -> StudentAssessmentsResponse:
    student = get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    return StudentAssessmentsResponse(
        items=[StudentAssessmentSummary(**item) for item in list_student_assignments(student_id)]
    )


@router.get("/assessments/{assignment_id}", response_model=StudentAssessmentDetail)
def get_student_assessment(assignment_id: str, student_id: str = Query(...)) -> StudentAssessmentDetail:
    assignment = get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    if assignment["student_id"] != student_id:
        raise HTTPException(status_code=403, detail="Assessment does not belong to this student.")

    return StudentAssessmentDetail(
        **assignment,
        submission_guidance=(
            "Answer in your own words, stay focused on the question, and explain the idea clearly."
        ),
    )


@router.post("/assessments/{assignment_id}/submit", response_model=StudentPortalResult)
def submit_student_assessment(
    assignment_id: str,
    payload: StudentSubmissionRequest,
) -> StudentPortalResult:
    assignment = get_assignment(assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    if assignment["student_id"] != payload.student_id:
        raise HTTPException(status_code=403, detail="Assessment does not belong to this student.")

    student = get_student(payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    question = get_question(assignment["question_id"])
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")

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
            "student_id": student["id"],
            "student_name": student["full_name"],
            "assignment_id": assignment["id"],
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
    mark_assignment_graded(assignment["id"], result["id"])
    return StudentPortalResult(**build_student_portal_result_payload(result))


@router.get("/results/{attempt_id}", response_model=StudentPortalResult)
def get_student_portal_result(attempt_id: str, student_id: str = Query(...)) -> StudentPortalResult:
    result = get_student_result(attempt_id, student_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found.")
    return StudentPortalResult(**build_student_portal_result_payload(result))
