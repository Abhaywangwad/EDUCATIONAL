"use client";

import { useEffect, useState } from "react";
import { buildApiUrl, getParentReportDetail, type ParentReportDetail } from "../lib/api";
import { useDemoSession } from "../lib/demo-session";

export function ParentReportScreen({ studentId }: { studentId: string }) {
  const { session } = useDemoSession("parent");
  const [report, setReport] = useState<ParentReportDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReport() {
      if (!session?.userId) {
        return;
      }

      try {
        const data = await getParentReportDetail(studentId, session.userId);
        setReport(data);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load this parent report."
        );
      }
    }

    void loadReport();
  }, [studentId, session?.userId]);

  if (error) {
    return <div className="portalContent"><p className="error">{error}</p></div>;
  }

  if (!report) {
    return <div className="portalContent"><div className="notice">Loading report...</div></div>;
  }

  return (
    <div className="portalContent">
      <section className="panelSurface">
        <p className="eyebrow">Parent report</p>
        <h2>{report.student_name}</h2>
        <p className="portalLead">{report.progress_summary}</p>

        <div className="miniStats">
          <div className="miniCard">
            <strong>Latest score</strong>
            <p className="muted">
              {report.latest_score != null ? `${report.latest_score.toFixed(1)} / 10` : "Pending"}
            </p>
          </div>
          <div className="miniCard">
            <strong>Bloom level</strong>
            <p className="muted">{report.latest_bloom_level ?? "Waiting"}</p>
          </div>
          <div className="miniCard">
            <strong>Grade level</strong>
            <p className="muted">{report.grade_level}</p>
          </div>
        </div>
      </section>

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <p className="eyebrow">Strengths</p>
          <h3>What is going well</h3>
          <div className="panelList">
            {report.strengths.map((item) => (
              <div className="listCard" key={item}>
                <p className="muted">{item}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="panelSurface">
          <p className="eyebrow">Improvement focus</p>
          <h3>Next academic step</h3>
          <div className="panelList">
            {report.improvements.map((item) => (
              <div className="listCard" key={item}>
                <p className="muted">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <p className="eyebrow">Teacher feedback</p>
          <h3>Latest comment</h3>
          <p className="muted">{report.teacher_feedback}</p>
        </div>

        <div className="panelSurface">
          <p className="eyebrow">Bloom level meaning</p>
          <h3>What the depth level shows</h3>
          <p className="muted">{report.bloom_meaning}</p>
          {report.pdf_download_url ? (
            <div className="actions" style={{ marginTop: 16 }}>
              <a
                href={buildApiUrl(report.pdf_download_url)}
                target="_blank"
                rel="noreferrer"
                className="secondary"
              >
                Download report PDF
              </a>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
