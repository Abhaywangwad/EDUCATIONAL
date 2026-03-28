import { ResultDetail } from "../../../components/result-detail";

export default function ResultPage({
  params
}: {
  params: { id: string };
}) {
  return <ResultDetail resultId={params.id} />;
}
