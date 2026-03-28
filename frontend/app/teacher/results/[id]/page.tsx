import { ResultDetail } from "../../../../components/result-detail";

export default function TeacherResultDetailPage({
  params
}: {
  params: { id: string };
}) {
  return <ResultDetail resultId={params.id} />;
}
