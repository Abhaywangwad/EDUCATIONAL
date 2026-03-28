import io
from collections import Counter
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .ai_generation import generate_class_report_text, generate_student_report_text

BLOOM_MEANINGS = {
    "Remember": "The answer mostly recalled facts or definitions.",
    "Understand": "The answer showed basic understanding of the idea in the student's own words.",
    "Apply": "The answer showed understanding and began using the idea in a practical context.",
    "Analyze": "The answer compared ideas, explained causes, or showed deeper reasoning.",
    "Evaluate": "The answer judged alternatives with clear reasoning and justification.",
    "Create": "The answer went beyond explanation and proposed a new idea or solution.",
}


def build_pdf_report_bytes(title: str, body: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(title, styles["Heading1"]),
        Spacer(1, 0.25 * inch),
        Paragraph(body.replace("\n", "<br/>"), styles["BodyText"]),
    ]
    doc.build(elements)
    return buffer.getvalue()


def describe_strengths(result: dict[str, Any]) -> list[str]:
    strengths: list[str] = []
    if float(result["depth_fact_score"]) >= 0.7:
        strengths.append("Showed strong conceptual understanding and reasoning.")
    if float(result["keyword_score"]) >= 0.6:
        strengths.append("Included the main subject terms and expected ideas.")
    if float(result["grammar_score"]) >= 0.65:
        strengths.append("Presented the explanation clearly and coherently.")
    if not strengths:
        strengths.append("Attempted the core idea and gave a direct response.")
    return strengths[:3]


def describe_improvements(result: dict[str, Any]) -> list[str]:
    improvements: list[str] = []
    if float(result["depth_fact_score"]) < 0.6:
        improvements.append("Add more explanation about why the concept works, not just what it is.")
    if float(result["keyword_score"]) < 0.5:
        improvements.append("Include more of the important subject ideas expected in the answer.")
    if float(result["grammar_score"]) < 0.6:
        improvements.append("Use clearer sentences so the main point is easier to follow.")
    if not improvements:
        improvements.append("Add one more example or comparison to deepen the answer.")
    return improvements[:3]


def build_student_portal_result_payload(result: dict[str, Any]) -> dict[str, Any]:
    score = float(result["final_score"])
    if score >= 8:
        tone = "Excellent work. This answer shows confident understanding."
    elif score >= 6:
        tone = "Good progress. The main idea is clear, with room to deepen the explanation."
    elif score >= 4:
        tone = "This answer shows partial understanding. A clearer explanation would improve it."
    else:
        tone = "This answer needs more support and explanation to fully answer the question."

    improvements = describe_improvements(result)
    return {
        "id": result["id"],
        "assignment_id": result.get("assignment_id"),
        "question_text": result["question_text"],
        "final_score": score,
        "bloom_level": result["bloom_level"],
        "summary": tone,
        "feedback": result["feedback"],
        "next_step": improvements[0],
        "created_at": result["created_at"],
    }


def generate_student_report_payload(result: dict[str, Any]) -> dict[str, Any]:
    student_name = result.get("student_name") or "Student"
    title = f"Student Report: {result['question_text']}"
    summary = generate_student_report_text(
        student_name=student_name,
        question_text=result["question_text"],
        final_score=float(result["final_score"]),
        bloom_level=result["bloom_level"],
        keyword_score=float(result["keyword_score"]),
        semantic_score=float(result["semantic_score"]),
        grammar_score=float(result["grammar_score"]),
        feedback=result["feedback"],
    )
    return {"title": title, "summary": summary}


def generate_class_report_payload(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = generate_class_report_text(results)
    scores = [float(item["final_score"]) for item in results] if results else [0.0]
    bloom_counts = Counter(item.get("bloom_level", "Understand") for item in results) or Counter({"Understand": 1})
    return {
        "title": "Class Performance Summary",
        "summary": summary,
        "average_score": round(sum(scores) / len(scores), 1),
        "total_results": len(results),
        "most_common_bloom_level": bloom_counts.most_common(1)[0][0],
    }


def generate_parent_report_summary(student: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    latest = results[0] if results else None
    if latest is None:
        return {
            "student_id": student["id"],
            "student_name": student["full_name"],
            "grade_level": student["grade_level"],
            "latest_score": None,
            "latest_bloom_level": None,
            "strengths": ["Waiting for the first graded response."],
            "improvements": ["Ask the student to complete the assigned assessment."],
            "latest_result_id": None,
            "report_status": "waiting",
            "pdf_download_url": None,
        }

    return {
        "student_id": student["id"],
        "student_name": student["full_name"],
        "grade_level": student["grade_level"],
        "latest_score": float(latest["final_score"]),
        "latest_bloom_level": latest["bloom_level"],
        "strengths": describe_strengths(latest),
        "improvements": describe_improvements(latest),
        "latest_result_id": latest["id"],
        "report_status": "ready",
        "pdf_download_url": f"/api/reports/results/{latest['id']}/student.pdf",
    }


def generate_parent_report_detail(student: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = generate_parent_report_summary(student, results)
    latest = results[0] if results else None
    if latest is None:
        return {
            **summary,
            "progress_summary": (
                f"{student['full_name']} has not received a graded result yet. Once an assessment is submitted, "
                "this page will show a clear academic summary for parents."
            ),
            "teacher_feedback": "No teacher feedback is available yet.",
            "bloom_meaning": BLOOM_MEANINGS["Understand"],
        }

    score = float(latest["final_score"])
    if score >= 8:
        progress_summary = (
            f"{student['full_name']} is performing strongly in this subject area. The latest answer shows "
            "clear understanding and a good level of academic depth."
        )
    elif score >= 6:
        progress_summary = (
            f"{student['full_name']} is showing steady progress. The core idea is understood, and the next step "
            "is to explain it with more depth and confidence."
        )
    else:
        progress_summary = (
            f"{student['full_name']} is still building confidence in this topic. More guided explanation and "
            "practice with structured answers would help."
        )

    return {
        **summary,
        "progress_summary": progress_summary,
        "teacher_feedback": latest["feedback"],
        "bloom_meaning": BLOOM_MEANINGS.get(latest["bloom_level"], BLOOM_MEANINGS["Understand"]),
    }
