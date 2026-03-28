"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  buildApiUrl,
  getClassSummary,
  getQuestions,
  getRecentResults,
  type ClassReportResponse,
  type GradeResult,
  type QuestionConfig
} from "../lib/api";

export function HomeDashboard() {
  const [questions, setQuestions] = useState<QuestionConfig[]>([]);
  const [results, setResults] = useState<GradeResult[]>([]);
  const [classSummary, setClassSummary] = useState<ClassReportResponse | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function load() {
      try {
        const [questionData, resultData, classData] = await Promise.all([
          getQuestions(),
          getRecentResults(),
          getClassSummary()
        ]);
        setQuestions(questionData);
        setResults(resultData.items);
        setClassSummary(classData);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load the dashboard."
        );
      }
    }

    void load();
  }, []);

  const latestResult = results[0];

  return (
    <>
      <section className="statGrid">
        <div className="statCard">
          <p className="cardLabel">Questions ready</p>
          <div className="statValue">{questions.length}</div>
          <p className="muted">Seeded and editable from the teacher screen.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Recent results</p>
          <div className="statValue">{results.length}</div>
          <p className="muted">Saved grading runs available for demo playback.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Latest Bloom level</p>
          <div className="statValue">{latestResult?.bloom_level ?? "-"}</div>
          <p className="muted">The newest graded answer shows its depth level here.</p>
        </div>
      </section>

      <section className="gridPanels">
        <div className="formPanel">
          <h2 className="sectionTitle">Class insight report</h2>
          <p className="helperText">
            This summary adapts the reporting idea from the uploaded project into our grading workflow.
          </p>
          {error ? <p className="error">{error}</p> : null}
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
                  <strong>Common Bloom level</strong>
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
            <div className="notice">
              Grade a few answers to unlock the class insight report.
            </div>
          )}
        </div>

        <div className="scorePanel">
          <h2 className="sectionTitle">Recent grading runs</h2>
          <p className="helperText">
            Open any result to view Bloom level, AI report, and PDF export.
          </p>
          <div className="panelList">
            {results.map((result) => (
              <div className="listCard" key={result.id}>
                <div className="scoreBadge">{result.final_score.toFixed(1)} / 10</div>
                <p className="listTitle">{result.question_text}</p>
                <p className="muted">Bloom level: {result.bloom_level}</p>
                <p className="muted">{result.feedback}</p>
                <Link href={`/results/${result.id}`} className="button secondary">
                  Open result
                </Link>
              </div>
            ))}
            {results.length === 0 && !error ? (
              <div className="notice">
                Grade one student answer and it will appear here.
              </div>
            ) : null}
          </div>
        </div>
      </section>
    </>
  );
}
