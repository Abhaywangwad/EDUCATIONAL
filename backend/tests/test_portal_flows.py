import unittest

from fastapi.testclient import TestClient

from app.main import app


class PortalFlowTests(unittest.TestCase):
    def test_demo_users_endpoint_returns_roles(self) -> None:
        with TestClient(app) as client:
            response = client.get("/api/demo-users")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["teacher"]["role"], "teacher")
        self.assertGreaterEqual(len(payload["students"]), 1)
        self.assertGreaterEqual(len(payload["parents"]), 1)

    def test_student_submission_and_parent_report_flow(self) -> None:
        with TestClient(app) as client:
            assessment_list = client.get("/api/student/assessments", params={"student_id": "student-isha"})
            self.assertEqual(assessment_list.status_code, 200)
            assignments = assessment_list.json()["items"]
            self.assertGreaterEqual(len(assignments), 1)

            assignment_id = assignments[0]["id"]
            submit = client.post(
                f"/api/student/assessments/{assignment_id}/submit",
                json={
                    "student_id": "student-isha",
                    "student_answer": (
                        "Data is raw facts, while information is processed data that becomes meaningful "
                        "and helps people make decisions."
                    ),
                },
            )
            self.assertEqual(submit.status_code, 200)
            result_id = submit.json()["id"]

            parent_reports = client.get("/api/parent/reports", params={"parent_id": "parent-kavya"})
            self.assertEqual(parent_reports.status_code, 200)
            summaries = parent_reports.json()["items"]
            self.assertGreaterEqual(len(summaries), 1)
            self.assertEqual(summaries[0]["report_status"], "ready")

            parent_detail = client.get(
                "/api/parent/reports/student-isha",
                params={"parent_id": "parent-kavya"},
            )
            self.assertEqual(parent_detail.status_code, 200)
            self.assertEqual(parent_detail.json()["latest_result_id"], result_id)


if __name__ == "__main__":
    unittest.main()
