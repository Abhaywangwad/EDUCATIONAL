"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  buildApiUrl,
  getResult,
  getStudentReport,
  type GradeResult,
  type StudentReportResponse
} from "../lib/api";

function ScoreMeter({
  label,
  score
}: {
  label: string;
  score: number;
}) {
  return (
    <div className="meter">
      <div className="split" style={{ justifyContent: "space-between" }}>
        <strong>{label}</strong>
        <span>{(score * 10).toFixed(1)} / 10</span>
      </div>
      <div className="meterBar">
        <div className="meterFill" style={{ width: `${score * 100}%` }} />
      </div>
    </div>
  );
}

export function ResultDetail({ resultId }: { resultId: string }) {
  const [result, setResult] = useState<GradeResult | null>(null);
  const [studentReport, setStudentReport] = useState<StudentReportResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadResult() {
      try {
        const [resultData, reportData] = await Promise.all([
          getResult(resultId),
          getStudentReport(resultId)
        ]);
        setResult(resultData);
        setStudentReport(reportData);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load the result."
        );
      }
    }

    void loadResult();
  }, [resultId]);

  if (error) {
    return <div className="portalContent"><p className="error">{error}</p></div>;
  }

  if (!result) {
    return <div className="portalContent"><div className="notice">Loading result...</div></div>;
  }

  return (
    <div className="portalContent">
      <section className="panelSurface">
        <div className="pillRow">
          <span className="scoreBadge">{result.final_score.toFixed(1)} / 10</span>
          <span className="subtleTag">{result.bloom_level}</span>
        </div>
        <h2 style={{ marginTop: 18 }}>{result.question_text}</h2>
        <p className="portalLead">
          {result.student_name
            ? `Reviewed for ${result.student_name} on ${new Date(result.created_at).toLocaleString()}.`
            : `Saved on ${new Date(result.created_at).toLocaleString()}.`}
        </p>

        <div className="portalPanelGrid">
          <div className="listCard">
            <strong>Feedback</strong>
            <p className="muted">{result.feedback}</p>
          </div>
          <div className="listCard">
            <strong>Teacher reasoning</strong>
            <p className="muted">{result.reasoning}</p>
          </div>
        </div>

        {studentReport ? (
          <div className="listCard" style={{ marginTop: 16 }}>
            <strong>{studentReport.title}</strong>
            <p className="muted">{studentReport.summary}</p>
          </div>
        ) : null}

        <div className="actions" style={{ marginTop: 16 }}>
          <Link href="/teacher/results" className="secondary">
            Back to results
          </Link>
          <Link href="/teacher/assessments" className="secondary">
            Edit assessments
          </Link>
          {result.assignment_id ? (
            <Link href={`/student/results/${result.id}`} className="secondary">
              Student view
            </Link>
          ) : null}
          {studentReport ? (
            <a
              href={buildApiUrl(studentReport.pdf_download_url)}
              target="_blank"
              rel="noreferrer"
              className="secondary"
            >
              Download student PDF
            </a>
          ) : null}
        </div>
      </section>

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <p className="eyebrow">Rubric breakdown</p>
          <h3>How the score was built</h3>
          <ScoreMeter label="Keyword coverage" score={result.keyword_score} />
          <ScoreMeter label="Grammar readability" score={result.grammar_score} />
          <ScoreMeter label="Semantic similarity" score={result.semantic_score} />
          <ScoreMeter label="Bloom score" score={result.bloom_score} />
          <ScoreMeter label="Depth + factual" score={result.depth_fact_score} />
          <ScoreMeter
            label="Facts understanding"
            score={result.facts_understanding_score}
          />
        </div>

        <div className="panelSurface">
          <p className="eyebrow">Answer comparison</p>
          <h3>Student vs model answer</h3>
          <div className="panelList">
            <div className="miniCard">
              <strong>Student answer</strong>
              <p className="muted">{result.student_answer}</p>
            </div>
            <div className="miniCard">
              <strong>Model answer</strong>
              <p className="muted">{result.model_answer}</p>
            </div>
            <div className="miniCard">
              <strong>Expected concepts</strong>
              <p className="muted">{result.expected_concepts.join(", ")}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
