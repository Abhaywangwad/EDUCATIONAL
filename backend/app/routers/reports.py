from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..repository import get_result, list_results
from ..schemas import ClassReportResponse, StudentReportResponse
from ..services.reporting import (
    build_pdf_report_bytes,
    generate_class_report_payload,
    generate_student_report_payload,
)


router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/results/{result_id}/student", response_model=StudentReportResponse)
def get_student_report(result_id: str) -> StudentReportResponse:
    result = get_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found.")

    payload = generate_student_report_payload(result)
    return StudentReportResponse(
        title=payload["title"],
        summary=payload["summary"],
        pdf_download_url=f"/api/reports/results/{result_id}/student.pdf",
    )


@router.get("/results/{result_id}/student.pdf")
def download_student_report_pdf(result_id: str) -> StreamingResponse:
    result = get_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found.")

    payload = generate_student_report_payload(result)
    pdf_bytes = build_pdf_report_bytes(payload["title"], payload["summary"])
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="student-report-{result_id}.pdf"'},
    )


@router.get("/class-summary", response_model=ClassReportResponse)
def get_class_summary(limit: int = Query(default=12, ge=1, le=100)) -> ClassReportResponse:
    results = list_results(limit)
    payload = generate_class_report_payload(results)
    return ClassReportResponse(
        title=payload["title"],
        summary=payload["summary"],
        average_score=payload["average_score"],
        total_results=payload["total_results"],
        most_common_bloom_level=payload["most_common_bloom_level"],
        pdf_download_url=f"/api/reports/class-summary.pdf?limit={limit}",
    )


@router.get("/class-summary.pdf")
def download_class_summary_pdf(limit: int = Query(default=12, ge=1, le=100)) -> StreamingResponse:
    results = list_results(limit)
    payload = generate_class_report_payload(results)
    pdf_bytes = build_pdf_report_bytes(payload["title"], payload["summary"])
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="class-summary.pdf"'},
    )
