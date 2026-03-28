from fastapi import APIRouter, HTTPException

from ..repository import create_assignment, get_question, get_student, list_assignments
from ..schemas import AssessmentAssignment, AssessmentAssignmentInput, TeacherAssignmentsResponse


router = APIRouter(prefix="/api/teacher", tags=["teacher"])


@router.get("/assignments", response_model=TeacherAssignmentsResponse)
def get_teacher_assignments() -> TeacherAssignmentsResponse:
    return TeacherAssignmentsResponse(
        items=[AssessmentAssignment(**item) for item in list_assignments()]
    )


@router.post("/assignments", response_model=AssessmentAssignment)
def assign_assessment_to_student(payload: AssessmentAssignmentInput) -> AssessmentAssignment:
    question = get_question(payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")

    student = get_student(payload.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    assignment = create_assignment(payload.model_dump())
    return AssessmentAssignment(**assignment)
