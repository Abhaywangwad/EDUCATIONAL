import type { ReactNode } from "react";
import { PortalScaffold } from "../../components/portal-scaffold";

const parentNav = [
  { href: "/parent", label: "Child Overview" }
];

export default function ParentLayout({ children }: { children: ReactNode }) {
  return <PortalScaffold role="parent" nav={parentNav}>{children}</PortalScaffold>;
}
