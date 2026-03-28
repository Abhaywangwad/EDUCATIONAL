"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { buildApiUrl, getParentReports, type ParentReportSummary } from "../lib/api";
import { useDemoSession } from "../lib/demo-session";

export function ParentOverview() {
  const { session } = useDemoSession("parent");
  const [reports, setReports] = useState<ParentReportSummary[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReports() {
      if (!session?.userId) {
        return;
      }

      try {
        const data = await getParentReports(session.userId);
        setReports(data.items);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load parent reports."
        );
      }
    }

    void loadReports();
  }, [session?.userId]);

  return (
    <div className="portalContent">
      <section className="panelSurface">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Child overview</p>
            <h2>Readable academic progress</h2>
          </div>
        </div>
        <p className="portalLead">
          Review the latest performance snapshot, teacher feedback, and downloadable report for each child.
        </p>
        {error ? <p className="error">{error}</p> : null}

        <div className="panelList">
          {reports.map((report) => (
            <div className="listCard" key={report.student_id}>
              <div className="split" style={{ justifyContent: "space-between" }}>
                <div>
                  <strong className="listTitle">{report.student_name}</strong>
                  <p className="muted">{report.grade_level}</p>
                </div>
                <span className={report.report_status === "ready" ? "pill" : "subtleTag"}>
                  {report.report_status}
                </span>
              </div>
              <p className="muted">
                {report.latest_score != null
                  ? `${report.latest_score.toFixed(1)} / 10 • ${report.latest_bloom_level}`
                  : "Waiting for the first graded result"}
              </p>
              <p className="muted">Strength: {report.strengths[0]}</p>
              <p className="muted">Next focus: {report.improvements[0]}</p>
              <div className="actions">
                <Link href={`/parent/reports/${report.student_id}`}>Open full report</Link>
                {report.pdf_download_url ? (
                  <a
                    href={buildApiUrl(report.pdf_download_url)}
                    target="_blank"
                    rel="noreferrer"
                    className="secondary"
                  >
                    Download PDF
                  </a>
                ) : null}
              </div>
            </div>
          ))}
          {reports.length === 0 && !error ? (
            <div className="notice">No child reports are available yet.</div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
