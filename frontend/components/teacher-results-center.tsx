"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getRecentResults, type GradeResult } from "../lib/api";

export function TeacherResultsCenter() {
  const [results, setResults] = useState<GradeResult[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadResults() {
      try {
        const data = await getRecentResults();
        setResults(data.items);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load results."
        );
      }
    }

    void loadResults();
  }, []);

  return (
    <div className="portalContent">
      <section className="panelSurface">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Review and results</p>
            <h2>Detailed grading history</h2>
          </div>
        </div>
        {error ? <p className="error">{error}</p> : null}
        <div className="panelList">
          {results.map((result) => (
            <div className="listCard" key={result.id}>
              <div className="split" style={{ justifyContent: "space-between" }}>
                <div>
                  <strong className="listTitle">{result.question_text}</strong>
                  <p className="muted">
                    {result.student_name ?? "Independent grading"} • {new Date(result.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="pillRow">
                  <span className="scoreBadge">{result.final_score.toFixed(1)} / 10</span>
                  <span className="subtleTag">{result.bloom_level}</span>
                </div>
              </div>
              <p className="muted">{result.feedback}</p>
              <div className="actions">
                <Link href={`/teacher/results/${result.id}`} className="secondary">
                  Open technical detail
                </Link>
                {result.assignment_id ? (
                  <Link href={`/student/results/${result.id}`} className="secondary">
                    Student view
                  </Link>
                ) : null}
              </div>
            </div>
          ))}
          {results.length === 0 && !error ? (
            <div className="notice">Once a student submits an assessment, the teacher review trail will appear here.</div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
