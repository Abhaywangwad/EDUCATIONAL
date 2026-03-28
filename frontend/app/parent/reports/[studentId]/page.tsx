import { ParentReportScreen } from "../../../../components/parent-report-screen";

export default function ParentReportPage({
  params
}: {
  params: { studentId: string };
}) {
  return <ParentReportScreen studentId={params.studentId} />;
}
