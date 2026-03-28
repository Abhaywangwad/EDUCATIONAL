import io
import unittest

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.main import app


def build_sample_pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 760, text)
    pdf.save()
    return buffer.getvalue()


class TextbookAndReportTests(unittest.TestCase):
    def test_textbook_generation_returns_suggestions(self) -> None:
        sample_pdf = build_sample_pdf_bytes(
            "A process is an independent program in execution. "
            "A thread is a smaller unit inside a process and shares memory."
        )

        with TestClient(app) as client:
            response = client.post(
                "/api/textbooks/generate-questions",
                files={"file": ("sample.pdf", sample_pdf, "application/pdf")},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["textbook_id"])
        self.assertGreater(len(payload["suggestions"]), 0)

    def test_student_and_class_report_endpoints(self) -> None:
        with TestClient(app) as client:
            grade = client.post(
                "/api/grade",
                json={
                    "question_id": "q-os-process-vs-thread",
                    "student_answer": (
                        "A process has its own memory space, while threads share memory inside a process, "
                        "so threads are lighter for concurrent execution."
                    ),
                },
            )

            self.assertEqual(grade.status_code, 200)
            result_id = grade.json()["id"]

            student_report = client.get(f"/api/reports/results/{result_id}/student")
            class_summary = client.get("/api/reports/class-summary")

        self.assertEqual(student_report.status_code, 200)
        self.assertEqual(class_summary.status_code, 200)
        self.assertIn("summary", student_report.json())
        self.assertIn("most_common_bloom_level", class_summary.json())


if __name__ == "__main__":
    unittest.main()
