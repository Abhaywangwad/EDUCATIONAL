"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getStudentAssessments, type StudentAssessment } from "../lib/api";
import { useDemoSession } from "../lib/demo-session";

export function StudentAssessmentHome() {
  const { session } = useDemoSession("student");
  const [assessments, setAssessments] = useState<StudentAssessment[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAssessments() {
      if (!session?.userId) {
        return;
      }

      try {
        const data = await getStudentAssessments(session.userId);
        setAssessments(data.items);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load student assessments."
        );
      }
    }

    void loadAssessments();
  }, [session?.userId]);

  return (
    <div className="portalContent">
      <section className="panelSurface">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Assessment home</p>
            <h2>Assigned work for {session?.displayName ?? "student"}</h2>
          </div>
        </div>
        <p className="portalLead">
          Choose one assessment, read the instructions, and write your answer in your own words.
        </p>
        {error ? <p className="error">{error}</p> : null}
        <div className="panelList">
          {assessments.map((assessment) => (
            <div className="listCard" key={assessment.id}>
              <div className="pillRow">
                <strong className="listTitle">{assessment.question_text}</strong>
                <span className={assessment.status === "graded" ? "pill" : "subtleTag"}>
                  {assessment.status}
                </span>
              </div>
              <p className="muted">{assessment.instructions}</p>
              <p className="muted">
                Due {assessment.due_label} • {assessment.duration_minutes} minutes
              </p>
              <div className="actions">
                <Link href={`/student/assessments/${assessment.id}`}>
                  {assessment.status === "graded" ? "Open again" : "Start assessment"}
                </Link>
                {assessment.latest_result_id ? (
                  <Link href={`/student/results/${assessment.latest_result_id}`} className="secondary">
                    View result
                  </Link>
                ) : null}
              </div>
            </div>
          ))}
          {assessments.length === 0 && !error ? (
            <div className="notice">No assessments are assigned yet. Ask your teacher to publish one from the teacher portal.</div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
