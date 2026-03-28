import type { ReactNode } from "react";
import { PortalScaffold } from "../../components/portal-scaffold";

const studentNav = [
  { href: "/student", label: "Assessment Home" }
];

export default function StudentLayout({ children }: { children: ReactNode }) {
  return <PortalScaffold role="student" nav={studentNav}>{children}</PortalScaffold>;
}
