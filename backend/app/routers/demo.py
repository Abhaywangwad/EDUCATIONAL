from fastapi import APIRouter, Query

from ..sample_data import DEMO_CASES
from ..schemas import DemoCase, DemoCasesResponse


router = APIRouter(prefix="/api/demo-cases", tags=["demo"])


@router.get("", response_model=DemoCasesResponse)
def get_demo_cases(question_id: str | None = Query(default=None)) -> DemoCasesResponse:
    items = [
        DemoCase(**item)
        for item in DEMO_CASES
        if question_id is None or item["question_id"] == question_id
    ]
    return DemoCasesResponse(items=items)
