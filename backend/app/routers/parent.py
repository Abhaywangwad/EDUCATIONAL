from fastapi import APIRouter, HTTPException, Query

from ..repository import get_parent, get_student, list_results, list_students
from ..schemas import ParentReportDetail, ParentReportsResponse, ParentReportSummary
from ..services.reporting import generate_parent_report_detail, generate_parent_report_summary


router = APIRouter(prefix="/api/parent", tags=["parent"])


@router.get("/reports", response_model=ParentReportsResponse)
def get_parent_reports(parent_id: str = Query(...)) -> ParentReportsResponse:
    parent = get_parent(parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent not found.")

    student_lookup = {student["id"]: student for student in list_students()}
    items = []
    for student_id in parent["child_ids"]:
        student = student_lookup.get(student_id)
        if student is None:
            continue
        student_results = list_results(limit=10, student_id=student_id)
        items.append(ParentReportSummary(**generate_parent_report_summary(student, student_results)))

    return ParentReportsResponse(items=items)


@router.get("/reports/{student_id}", response_model=ParentReportDetail)
def get_parent_report_detail_for_student(
    student_id: str,
    parent_id: str = Query(...),
) -> ParentReportDetail:
    parent = get_parent(parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent not found.")
    if student_id not in parent["child_ids"]:
        raise HTTPException(status_code=403, detail="Student does not belong to this parent account.")

    student = get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    student_results = list_results(limit=10, student_id=student_id)
    return ParentReportDetail(**generate_parent_report_detail(student, student_results))
