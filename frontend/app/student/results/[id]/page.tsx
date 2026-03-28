import { StudentResultScreen } from "../../../../components/student-result-screen";

export default function StudentResultPage({
  params
}: {
  params: { id: string };
}) {
  return <StudentResultScreen resultId={params.id} />;
}
