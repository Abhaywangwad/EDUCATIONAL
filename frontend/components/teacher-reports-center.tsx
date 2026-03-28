"use client";

import { useEffect, useState } from "react";
import {
  buildApiUrl,
  getClassSummary,
  getRecentResults,
  type ClassReportResponse,
  type GradeResult
} from "../lib/api";

export function TeacherReportsCenter() {
  const [classSummary, setClassSummary] = useState<ClassReportResponse | null>(null);
  const [results, setResults] = useState<GradeResult[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReports() {
      try {
        const [classData, resultData] = await Promise.all([
          getClassSummary(),
          getRecentResults()
        ]);
        setClassSummary(classData);
        setResults(resultData.items);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load reports."
        );
      }
    }

    void loadReports();
  }, []);

  return (
    <div className="portalContent">
      {error ? <p className="error">{error}</p> : null}

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Class report</p>
              <h2>Whole-class summary</h2>
            </div>
          </div>
          {classSummary ? (
            <div className="panelList">
              <div className="listCard">
                <strong className="listTitle">{classSummary.title}</strong>
                <p className="muted">{classSummary.summary}</p>
              </div>
              <div className="miniStats">
                <div className="miniCard">
                  <strong>Average score</strong>
                  <p className="muted">{classSummary.average_score.toFixed(1)} / 10</p>
                </div>
                <div className="miniCard">
                  <strong>Total results</strong>
                  <p className="muted">{classSummary.total_results}</p>
                </div>
                <div className="miniCard">
                  <strong>Common Bloom</strong>
                  <p className="muted">{classSummary.most_common_bloom_level}</p>
                </div>
              </div>
              <div className="actions">
                <a
                  href={buildApiUrl(classSummary.pdf_download_url)}
                  target="_blank"
                  rel="noreferrer"
                  className="secondary"
                >
                  Download class PDF
                </a>
              </div>
            </div>
          ) : (
            <div className="notice">Grade a few student answers to unlock the class report.</div>
          )}
        </div>

        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Student reports</p>
              <h2>Family-ready exports</h2>
            </div>
          </div>
          <div className="panelList">
            {results
              .filter((result) => result.student_name)
              .map((result) => (
                <div className="listCard" key={result.id}>
                  <strong className="listTitle">{result.student_name}</strong>
                  <p className="muted">{result.question_text}</p>
                  <p className="muted">
                    {result.final_score.toFixed(1)} / 10 • {result.bloom_level}
                  </p>
                  <div className="actions">
                    <a
                      href={buildApiUrl(`/api/reports/results/${result.id}/student.pdf`)}
                      target="_blank"
                      rel="noreferrer"
                      className="secondary"
                    >
                      Download student PDF
                    </a>
                  </div>
                </div>
              ))}
            {results.filter((result) => result.student_name).length === 0 ? (
              <div className="notice">Student-specific report exports appear here after the first graded attempt.</div>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  );
}
