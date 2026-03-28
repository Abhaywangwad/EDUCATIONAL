"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getStudentPortalResult, type StudentPortalResult } from "../lib/api";
import { useDemoSession } from "../lib/demo-session";

export function StudentResultScreen({ resultId }: { resultId: string }) {
  const { session } = useDemoSession("student");
  const [result, setResult] = useState<StudentPortalResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadResult() {
      if (!session?.userId) {
        return;
      }

      try {
        const data = await getStudentPortalResult(resultId, session.userId);
        setResult(data);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load this student result."
        );
      }
    }

    void loadResult();
  }, [resultId, session?.userId]);

  if (error) {
    return <div className="portalContent"><p className="error">{error}</p></div>;
  }

  if (!result) {
    return <div className="portalContent"><div className="notice">Loading your result...</div></div>;
  }

  return (
    <div className="portalContent">
      <section className="panelSurface studentResultHero">
        <p className="eyebrow">Submission complete</p>
        <h2>{result.question_text}</h2>
        <div className="scoreHero">
          <div className="scoreBadge">{result.final_score.toFixed(1)} / 10</div>
          <span className="subtleTag">{result.bloom_level}</span>
        </div>
        <p className="portalLead">{result.summary}</p>
      </section>

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <p className="eyebrow">Feedback</p>
          <h3>What went well</h3>
          <p className="muted">{result.feedback}</p>
        </div>

        <div className="panelSurface">
          <p className="eyebrow">Next step</p>
          <h3>How to improve</h3>
          <p className="muted">{result.next_step}</p>
          <div className="actions">
            <Link href="/student">Back to assessment home</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
