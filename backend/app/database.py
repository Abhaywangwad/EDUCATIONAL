import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from .config import get_settings
from .sample_data import (
    DEMO_ASSIGNMENTS,
    DEMO_CASES,
    DEMO_PARENTS,
    DEMO_QUESTIONS,
    DEMO_STUDENTS,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    db_path = settings.resolved_database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                question_text TEXT NOT NULL,
                model_answer TEXT NOT NULL,
                expected_concepts TEXT NOT NULL,
                synonyms TEXT NOT NULL,
                weights TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                grade_level TEXT NOT NULL,
                parent_ids TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS parents (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                child_ids TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assignments (
                id TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                instructions TEXT NOT NULL,
                due_label TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 20,
                status TEXT NOT NULL DEFAULT 'assigned',
                latest_result_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(question_id) REFERENCES questions(id),
                FOREIGN KEY(student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                student_answer TEXT NOT NULL,
                model_answer TEXT NOT NULL,
                expected_concepts TEXT NOT NULL,
                weights TEXT NOT NULL,
                student_id TEXT,
                student_name TEXT,
                assignment_id TEXT,
                keyword_score REAL NOT NULL,
                semantic_score REAL NOT NULL,
                depth_fact_score REAL NOT NULL,
                bloom_level TEXT NOT NULL DEFAULT 'Understand',
                bloom_score REAL NOT NULL DEFAULT 0.4,
                grammar_score REAL NOT NULL,
                facts_understanding_score REAL NOT NULL,
                final_score REAL NOT NULL,
                reasoning TEXT NOT NULL,
                feedback TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            );
            """
        )

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(results)").fetchall()
        }
        result_migrations = {
            "bloom_level": "ALTER TABLE results ADD COLUMN bloom_level TEXT NOT NULL DEFAULT 'Understand'",
            "bloom_score": "ALTER TABLE results ADD COLUMN bloom_score REAL NOT NULL DEFAULT 0.4",
            "student_id": "ALTER TABLE results ADD COLUMN student_id TEXT",
            "student_name": "ALTER TABLE results ADD COLUMN student_name TEXT",
            "assignment_id": "ALTER TABLE results ADD COLUMN assignment_id TEXT",
        }
        for column, statement in result_migrations.items():
            if column not in columns:
                connection.execute(statement)


def row_to_question(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "question_text": row["question_text"],
        "model_answer": row["model_answer"],
        "expected_concepts": json.loads(row["expected_concepts"]),
        "synonyms": json.loads(row["synonyms"]),
        "weights": json.loads(row["weights"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def row_to_student(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "grade_level": row["grade_level"],
        "parent_ids": json.loads(row["parent_ids"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def row_to_parent(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "child_ids": json.loads(row["child_ids"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def row_to_assignment(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "question_id": row["question_id"],
        "question_text": row["question_text"],
        "student_id": row["student_id"],
        "student_name": row["student_name"],
        "instructions": row["instructions"],
        "due_label": row["due_label"],
        "duration_minutes": row["duration_minutes"],
        "status": row["status"],
        "latest_result_id": row["latest_result_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def row_to_result(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "question_id": row["question_id"],
        "question_text": row["question_text"],
        "student_answer": row["student_answer"],
        "model_answer": row["model_answer"],
        "expected_concepts": json.loads(row["expected_concepts"]),
        "weights": json.loads(row["weights"]),
        "student_id": row["student_id"],
        "student_name": row["student_name"],
        "assignment_id": row["assignment_id"],
        "keyword_score": row["keyword_score"],
        "semantic_score": row["semantic_score"],
        "depth_fact_score": row["depth_fact_score"],
        "bloom_level": row["bloom_level"] or "Understand",
        "bloom_score": row["bloom_score"] if row["bloom_score"] is not None else 0.4,
        "grammar_score": row["grammar_score"],
        "facts_understanding_score": row["facts_understanding_score"],
        "final_score": row["final_score"],
        "reasoning": row["reasoning"],
        "feedback": row["feedback"],
        "created_at": row["created_at"],
    }


def _seed_initial_results(connection: sqlite3.Connection, now: str) -> None:
    existing = connection.execute("SELECT COUNT(*) AS count FROM results").fetchone()
    if existing["count"] > 0:
        return

    from .schemas import ScoreWeights
    from .services.grading import grade_answer

    question_lookup = {question["id"]: question for question in DEMO_QUESTIONS}
    case_lookup = {case["id"]: case for case in DEMO_CASES}
    student_lookup = {student["id"]: student for student in DEMO_STUDENTS}
    assignment_lookup = {assignment["id"]: assignment for assignment in DEMO_ASSIGNMENTS}

    seeds = (
        {
            "id": "result-aarav-process",
            "assignment_id": "assignment-aarav-process",
            "student_id": "student-aarav",
            "case_id": "case-thread-deep",
        },
        {
            "id": "result-meera-dbms",
            "assignment_id": "assignment-meera-dbms",
            "student_id": "student-meera",
            "case_id": "case-normalization-deep",
        },
    )

    for seed in seeds:
        assignment = assignment_lookup[seed["assignment_id"]]
        question = question_lookup[assignment["question_id"]]
        student = student_lookup[seed["student_id"]]
        sample_case = case_lookup[seed["case_id"]]
        weights = ScoreWeights(**question["weights"])
        graded = grade_answer(
            question_text=question["question_text"],
            model_answer=question["model_answer"],
            expected_concepts=question["expected_concepts"],
            synonyms=question["synonyms"],
            weights=weights,
            student_answer=sample_case["student_answer"],
        )

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
                seed["id"],
                question["id"],
                question["question_text"],
                sample_case["student_answer"],
                question["model_answer"],
                json.dumps(question["expected_concepts"]),
                json.dumps(question["weights"]),
                student["id"],
                student["full_name"],
                assignment["id"],
                graded.keyword_score,
                graded.semantic_score,
                graded.depth_fact_score,
                graded.bloom_level,
                graded.bloom_score,
                graded.grammar_score,
                graded.facts_understanding_score,
                graded.final_score,
                graded.reasoning,
                graded.feedback,
                now,
            ),
        )


def _sync_assignment_statuses(connection: sqlite3.Connection, now: str) -> None:
    rows = connection.execute(
        """
        SELECT assignment_id, id
        FROM results
        WHERE assignment_id IS NOT NULL
        ORDER BY created_at DESC
        """
    ).fetchall()
    latest_by_assignment: dict[str, str] = {}
    for row in rows:
        assignment_id = row["assignment_id"]
        if assignment_id and assignment_id not in latest_by_assignment:
            latest_by_assignment[assignment_id] = row["id"]

    for assignment_id, result_id in latest_by_assignment.items():
        connection.execute(
            """
            UPDATE assignments
            SET status = 'graded', latest_result_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (result_id, now, assignment_id),
        )


def seed_demo_questions() -> None:
    now = utc_now_iso()
    with get_connection() as connection:
        for question in DEMO_QUESTIONS:
            connection.execute(
                """
                INSERT OR IGNORE INTO questions (
                    id, question_text, model_answer, expected_concepts, synonyms, weights, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question["id"],
                    question["question_text"],
                    question["model_answer"],
                    json.dumps(question["expected_concepts"]),
                    json.dumps(question["synonyms"]),
                    json.dumps(question["weights"]),
                    now,
                    now,
                ),
            )

        for student in DEMO_STUDENTS:
            connection.execute(
                """
                INSERT OR IGNORE INTO students (
                    id, full_name, grade_level, parent_ids, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    student["id"],
                    student["full_name"],
                    student["grade_level"],
                    json.dumps(student["parent_ids"]),
                    now,
                    now,
                ),
            )

        for parent in DEMO_PARENTS:
            connection.execute(
                """
                INSERT OR IGNORE INTO parents (
                    id, full_name, child_ids, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    parent["id"],
                    parent["full_name"],
                    json.dumps(parent["child_ids"]),
                    now,
                    now,
                ),
            )

        for assignment in DEMO_ASSIGNMENTS:
            connection.execute(
                """
                INSERT OR IGNORE INTO assignments (
                    id, question_id, student_id, instructions, due_label, duration_minutes,
                    status, latest_result_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 'assigned', NULL, ?, ?)
                """,
                (
                    assignment["id"],
                    assignment["question_id"],
                    assignment["student_id"],
                    assignment["instructions"],
                    assignment["due_label"],
                    assignment["duration_minutes"],
                    now,
                    now,
                ),
            )

        _seed_initial_results(connection, now)
        _sync_assignment_statuses(connection, now)
