"use client";

import Link from "next/link";
import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { getDemoUsers, type DemoUsersResponse, type PortalUser } from "../lib/api";
import { saveDemoSession } from "../lib/demo-session";

function destinationFor(user: PortalUser) {
  if (user.role === "teacher") {
    return "/teacher";
  }
  if (user.role === "student") {
    return "/student";
  }
  return "/parent";
}

function PersonaCard({
  user,
  description,
  onSelect,
  isPending
}: {
  user: PortalUser;
  description: string;
  onSelect: (user: PortalUser) => void;
  isPending: boolean;
}) {
  return (
    <div className="personaCard">
      <div className="pillRow">
        <span className="pill">{user.role}</span>
        {user.grade_level ? <span className="subtleTag">{user.grade_level}</span> : null}
      </div>
      <h3>{user.full_name}</h3>
      <p className="muted">{description}</p>
      <button type="button" onClick={() => onSelect(user)} disabled={isPending}>
        Continue as {user.full_name.split(" ")[0]}
      </button>
    </div>
  );
}

export function LoginScreen() {
  const [users, setUsers] = useState<DemoUsersResponse | null>(null);
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await getDemoUsers();
        setUsers(data);
      } catch (loadError) {
        const message =
          loadError instanceof Error
            ? loadError.message
            : "Could not load demo users.";
        if (message.includes("Not Found")) {
          setError(
            "The backend is running, but it is an older version and does not have the portal routes yet. Restart the backend on port 8000, then refresh this page."
          );
          return;
        }
        setError(
          message
        );
      }
    }

    void loadUsers();
  }, []);

  function handleSelect(user: PortalUser) {
    startTransition(() => {
      saveDemoSession(user);
      router.push(destinationFor(user));
    });
  }

  return (
    <div className="marketingShell">
      <header className="marketingHeader">
        <Link href="/" className="portalBrand">
          HLGS
        </Link>
        <div className="actions">
          <Link href="/" className="secondary">
            Back home
          </Link>
        </div>
      </header>

      <section className="heroStage">
        <div className="heroCopy">
          <p className="eyebrow">Portal access</p>
          <h1>Enter the platform as a teacher, student, or parent.</h1>
          <p className="portalLead">
            This demo uses mock accounts so you can experience each role without a full authentication setup.
          </p>
        </div>
      </section>

      {error ? <p className="error">{error}</p> : null}

      <section className="roleGrid">
        <div className="roleColumn">
          <p className="eyebrow">Teacher</p>
          {users ? (
            <PersonaCard
              user={users.teacher}
              description="Create assessments, assign work, review results, and export reports."
              onSelect={handleSelect}
              isPending={isPending}
            />
          ) : error ? (
            <div className="notice">Teacher portal is unavailable until the backend is restarted.</div>
          ) : (
            <div className="notice">Loading teacher access...</div>
          )}
        </div>

        <div className="roleColumn">
          <p className="eyebrow">Students</p>
          <div className="panelList">
            {users ? (
              users.students.map((student) => (
                <PersonaCard
                  key={student.id}
                  user={student}
                  description="Open assigned assessments, answer in exam mode, and review simplified results."
                  onSelect={handleSelect}
                  isPending={isPending}
                />
              ))
            ) : error ? (
              <div className="notice">Student portal is unavailable until the backend is restarted.</div>
            ) : (
              <div className="notice">Loading student access...</div>
            )}
          </div>
        </div>

        <div className="roleColumn">
          <p className="eyebrow">Parents</p>
          <div className="panelList">
            {users ? (
              users.parents.map((parent) => (
                <PersonaCard
                  key={parent.id}
                  user={parent}
                  description="Read your child's report in clear, parent-friendly language."
                  onSelect={handleSelect}
                  isPending={isPending}
                />
              ))
            ) : error ? (
              <div className="notice">Parent portal is unavailable until the backend is restarted.</div>
            ) : (
              <div className="notice">Loading parent access...</div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
