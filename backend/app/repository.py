import json
import uuid
from typing import Any

from .database import (
    get_connection,
    row_to_assignment,
    row_to_parent,
    row_to_question,
    row_to_result,
    row_to_student,
    utc_now_iso,
)

_ASSIGNMENT_SELECT = """
SELECT
    assignments.*,
    questions.question_text AS question_text,
    students.full_name AS student_name
FROM assignments
JOIN questions ON questions.id = assignments.question_id
JOIN students ON students.id = assignments.student_id
"""


def list_questions() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM questions ORDER BY updated_at DESC, question_text ASC"
        ).fetchall()
        return [row_to_question(row) for row in rows]


def get_question(question_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
        return row_to_question(row) if row else None


def upsert_question(question_payload: dict[str, Any]) -> dict[str, Any]:
    question_id = question_payload["id"] or str(uuid.uuid4())
    existing = get_question(question_id)
    now = utc_now_iso()
    created_at = existing["created_at"] if existing else now

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO questions (
                id, question_text, model_answer, expected_concepts, synonyms, weights, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                question_text = excluded.question_text,
                model_answer = excluded.model_answer,
                expected_concepts = excluded.expected_concepts,
                synonyms = excluded.synonyms,
                weights = excluded.weights,
                updated_at = excluded.updated_at
            """,
            (
                question_id,
                question_payload["question_text"],
                question_payload["model_answer"],
                json.dumps(question_payload["expected_concepts"]),
                json.dumps(question_payload["synonyms"]),
                json.dumps(question_payload["weights"]),
                created_at,
                now,
            ),
        )
    return get_question(question_id)  # type: ignore[return-value]


def list_students() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM students ORDER BY full_name ASC"
        ).fetchall()
        return [row_to_student(row) for row in rows]


def get_student(student_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return row_to_student(row) if row else None


def list_parents() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM parents ORDER BY full_name ASC"
        ).fetchall()
        return [row_to_parent(row) for row in rows]


def get_parent(parent_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM parents WHERE id = ?", (parent_id,)).fetchone()
        return row_to_parent(row) if row else None


def list_assignments() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            f"{_ASSIGNMENT_SELECT} ORDER BY assignments.updated_at DESC, assignments.created_at DESC"
        ).fetchall()
        return [row_to_assignment(row) for row in rows]


def list_student_assignments(student_id: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            f"{_ASSIGNMENT_SELECT} WHERE assignments.student_id = ? ORDER BY assignments.updated_at DESC",
            (student_id,),
        ).fetchall()
        return [row_to_assignment(row) for row in rows]


def get_assignment(assignment_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            f"{_ASSIGNMENT_SELECT} WHERE assignments.id = ?",
            (assignment_id,),
        ).fetchone()
        return row_to_assignment(row) if row else None


def create_assignment(assignment_payload: dict[str, Any]) -> dict[str, Any]:
    assignment_id = assignment_payload.get("id") or str(uuid.uuid4())
    now = utc_now_iso()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO assignments (
                id, question_id, student_id, instructions, due_label, duration_minutes,
                status, latest_result_id, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assignment_id,
                assignment_payload["question_id"],
                assignment_payload["student_id"],
                assignment_payload["instructions"],
                assignment_payload["due_label"],
                assignment_payload["duration_minutes"],
                assignment_payload.get("status", "assigned"),
                assignment_payload.get("latest_result_id"),
                now,
                now,
            ),
        )
    return get_assignment(assignment_id)  # type: ignore[return-value]


def mark_assignment_graded(assignment_id: str, result_id: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE assignments
            SET status = 'graded', latest_result_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (result_id, utc_now_iso(), assignment_id),
        )


def save_result(result_payload: dict[str, Any]) -> dict[str, Any]:
    result_id = result_payload.get("id") or str(uuid.uuid4())
    created_at = utc_now_iso()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO results (
                id, question_id, question_text, student_answer, model_answer, expected_concepts, weights,
                student_id, student_name, assignment_id, keyword_score, semantic_score, depth_fact_score,
                bloom_level, bloom_score, grammar_score, facts_understanding_score, final_score, reasoning,
                feedback, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result_id,
                result_payload["question_id"],
                result_payload["question_text"],
                result_payload["student_answer"],
                result_payload["model_answer"],
                json.dumps(result_payload["expected_concepts"]),
                json.dumps(result_payload["weights"]),
                result_payload.get("student_id"),
                result_payload.get("student_name"),
                result_payload.get("assignment_id"),
                result_payload["keyword_score"],
                result_payload["semantic_score"],
                result_payload["depth_fact_score"],
                result_payload["bloom_level"],
                result_payload["bloom_score"],
                result_payload["grammar_score"],
                result_payload["facts_understanding_score"],
                result_payload["final_score"],
                result_payload["reasoning"],
                result_payload["feedback"],
                created_at,
            ),
        )
    return get_result(result_id)  # type: ignore[return-value]


def get_result(result_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM results WHERE id = ?", (result_id,)).fetchone()
        return row_to_result(row) if row else None


def get_student_result(result_id: str, student_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM results WHERE id = ? AND student_id = ?",
            (result_id, student_id),
        ).fetchone()
        return row_to_result(row) if row else None


def list_results(limit: int = 10, student_id: str | None = None) -> list[dict[str, Any]]:
    query = "SELECT * FROM results"
    params: list[Any] = []
    if student_id:
        query += " WHERE student_id = ?"
        params.append(student_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [row_to_result(row) for row in rows]


def list_results_for_students(student_ids: list[str], limit: int = 20) -> list[dict[str, Any]]:
    if not student_ids:
        return []

    placeholders = ", ".join("?" for _ in student_ids)
    query = (
        f"SELECT * FROM results WHERE student_id IN ({placeholders}) "
        "ORDER BY created_at DESC LIMIT ?"
    )
    params = [*student_ids, limit]
    with get_connection() as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
        return [row_to_result(row) for row in rows]
