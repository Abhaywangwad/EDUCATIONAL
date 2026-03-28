from fastapi import APIRouter

from ..repository import list_parents, list_students
from ..sample_data import DEMO_TEACHER
from ..schemas import DemoUsersResponse, PortalUser


router = APIRouter(prefix="/api", tags=["session"])


@router.get("/demo-users", response_model=DemoUsersResponse)
def get_demo_users() -> DemoUsersResponse:
    students = [
        PortalUser(
            id=student["id"],
            full_name=student["full_name"],
            role="student",
            grade_level=student["grade_level"],
            linked_parent_ids=student["parent_ids"],
        )
        for student in list_students()
    ]
    parents = [
        PortalUser(
            id=parent["id"],
            full_name=parent["full_name"],
            role="parent",
            linked_student_ids=parent["child_ids"],
        )
        for parent in list_parents()
    ]
    return DemoUsersResponse(
        teacher=PortalUser(
            id=DEMO_TEACHER["id"],
            full_name=DEMO_TEACHER["full_name"],
            role="teacher",
        ),
        students=students,
        parents=parents,
    )
