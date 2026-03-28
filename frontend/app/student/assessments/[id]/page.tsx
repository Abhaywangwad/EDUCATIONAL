import { StudentExamSession } from "../../../../components/student-exam-session";

export default function StudentAssessmentPage({
  params
}: {
  params: { id: string };
}) {
  return <StudentExamSession assignmentId={params.id} />;
}
