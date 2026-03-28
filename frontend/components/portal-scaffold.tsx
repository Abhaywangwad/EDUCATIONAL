"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clearDemoSession, useDemoSession } from "../lib/demo-session";
import type { Role } from "../lib/api";

type NavItem = {
  href: string;
  label: string;
};

const roleCopy: Record<Role, { eyebrow: string; title: string; description: string }> = {
  teacher: {
    eyebrow: "Teacher portal",
    title: "Assessment operations",
    description: "Create assessments, assign students, review grading quality, and export reports."
  },
  student: {
    eyebrow: "Student portal",
    title: "Assessment workspace",
    description: "Read the question carefully, focus on your answer, and review the result clearly."
  },
  parent: {
    eyebrow: "Parent portal",
    title: "Progress and reports",
    description: "See your child's latest academic report in simple, parent-friendly language."
  }
};

export function PortalScaffold({
  role,
  nav,
  children
}: {
  role: Role;
  nav: NavItem[];
  children: ReactNode;
}) {
  const pathname = usePathname();
  const { session, isAllowed } = useDemoSession(role);
  const copy = roleCopy[role];

  if (!session || !isAllowed) {
    return (
      <div className="accessCard">
        <p className="eyebrow">{copy.eyebrow}</p>
        <h1>{copy.title}</h1>
        <p className="portalLead">{copy.description}</p>
        <p className="muted">
          This portal expects a matching demo user session. Choose the correct role from the login page.
        </p>
        <div className="actions">
          <Link href="/login">Go to login</Link>
          <Link href="/" className="secondary">
            Back to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="portalShell">
      <aside className="portalSidebar">
        <Link href="/" className="portalBrand">
          HLGS
        </Link>
        <div className="portalIdentity">
          <p className="eyebrow">{copy.eyebrow}</p>
          <strong>{session.displayName}</strong>
          <p className="muted">
            {session.gradeLevel ? `${session.gradeLevel} learner profile` : copy.description}
          </p>
        </div>
        <nav className="portalNav">
          {nav.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link key={item.href} href={item.href} className={isActive ? "active" : ""}>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="portalSidebarFoot">
          <button type="button" className="secondary" onClick={clearDemoSession}>
            Sign out
          </button>
          <Link href="/login" className="secondary">
            Switch role
          </Link>
        </div>
      </aside>

      <div className="portalMain">
        <header className="portalHeader">
          <div>
            <p className="eyebrow">{copy.eyebrow}</p>
            <h1>{copy.title}</h1>
            <p className="portalLead">{copy.description}</p>
          </div>
          <div className="portalHeaderMeta">
            <span className="chip">Mock session</span>
            <span className="chip">{session.displayName}</span>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}
