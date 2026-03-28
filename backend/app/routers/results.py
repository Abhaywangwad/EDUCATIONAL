from fastapi import APIRouter, HTTPException, Query

from ..repository import get_result, list_results
from ..schemas import GradeResult, ResultsListResponse


router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("", response_model=ResultsListResponse)
def get_recent_results(limit: int = Query(default=10, ge=1, le=50)) -> ResultsListResponse:
    return ResultsListResponse(items=[GradeResult(**item) for item in list_results(limit)])


@router.get("/{result_id}", response_model=GradeResult)
def get_result_by_id(result_id: str) -> GradeResult:
    result = get_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found.")
    return GradeResult(**result)
