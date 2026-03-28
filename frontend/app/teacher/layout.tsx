import type { ReactNode } from "react";
import { PortalScaffold } from "../../components/portal-scaffold";

const teacherNav = [
  { href: "/teacher", label: "Dashboard" },
  { href: "/teacher/assessments", label: "Assessments" },
  { href: "/teacher/results", label: "Review & Results" },
  { href: "/teacher/reports", label: "Reports" }
];

export default function TeacherLayout({ children }: { children: ReactNode }) {
  return <PortalScaffold role="teacher" nav={teacherNav}>{children}</PortalScaffold>;
}
