"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  getClassSummary,
  getQuestions,
  getRecentResults,
  getTeacherAssignments,
  type ClassReportResponse,
  type GradeResult,
  type QuestionConfig,
  type TeacherAssignment
} from "../lib/api";

export function TeacherDashboard() {
  const [questions, setQuestions] = useState<QuestionConfig[]>([]);
  const [results, setResults] = useState<GradeResult[]>([]);
  const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
  const [classSummary, setClassSummary] = useState<ClassReportResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [questionData, resultData, assignmentData, classData] = await Promise.all([
          getQuestions(),
          getRecentResults(),
          getTeacherAssignments(),
          getClassSummary()
        ]);
        setQuestions(questionData);
        setResults(resultData.items);
        setAssignments(assignmentData.items);
        setClassSummary(classData);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load the teacher dashboard."
        );
      }
    }

    void loadDashboard();
  }, []);

  const gradedAssignments = assignments.filter((item) => item.status === "graded");

  return (
    <div className="portalContent">
      {error ? <p className="error">{error}</p> : null}

      <section className="statStrip">
        <div className="statCard">
          <p className="cardLabel">Assessments ready</p>
          <div className="statValue">{questions.length}</div>
          <p className="muted">Teacher-authored questions available for assignment.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Assigned to students</p>
          <div className="statValue">{assignments.length}</div>
          <p className="muted">Assessment tasks currently visible in student portals.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Graded attempts</p>
          <div className="statValue">{results.length}</div>
          <p className="muted">Saved grading attempts available for review and reporting.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Average score</p>
          <div className="statValue">
            {classSummary ? `${classSummary.average_score.toFixed(1)} / 10` : "-"}
          </div>
          <p className="muted">Current class pulse from the report engine.</p>
        </div>
      </section>

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Quick actions</p>
              <h2>Run the teaching workflow</h2>
            </div>
          </div>
          <div className="actionGrid">
            <Link href="/teacher/assessments" className="actionCard">
              <strong>Create or import assessment</strong>
              <p className="muted">Write a question, refine concepts, or generate one from a textbook PDF.</p>
            </Link>
            <Link href="/teacher/results" className="actionCard">
              <strong>Review grading quality</strong>
              <p className="muted">See Bloom depth, final scores, and the detailed explanation behind each mark.</p>
            </Link>
            <Link href="/teacher/reports" className="actionCard">
              <strong>Open reports center</strong>
              <p className="muted">Export class summaries and student-facing PDF reports for families.</p>
            </Link>
          </div>
        </div>

        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Assignment status</p>
              <h2>Student delivery</h2>
            </div>
          </div>
          <div className="panelList">
            {assignments.slice(0, 4).map((assignment) => (
              <div className="listCard" key={assignment.id}>
                <div className="pillRow">
                  <strong className="listTitle">{assignment.question_text}</strong>
                  <span className={assignment.status === "graded" ? "pill" : "subtleTag"}>
                    {assignment.status}
                  </span>
                </div>
                <p className="muted">
                  Assigned to {assignment.student_name} • {assignment.due_label}
                </p>
              </div>
            ))}
            {assignments.length === 0 ? (
              <div className="notice">Create an assessment assignment to open the student workflow.</div>
            ) : null}
          </div>
        </div>
      </section>

      <section className="portalPanelGrid">
        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Recent grading</p>
              <h2>Latest attempts</h2>
            </div>
            <Link href="/teacher/results" className="textLink">
              View all
            </Link>
          </div>
          <div className="panelList">
            {results.slice(0, 4).map((result) => (
              <div className="listCard" key={result.id}>
                <div className="pillRow">
                  <span className="scoreBadge">{result.final_score.toFixed(1)} / 10</span>
                  <span className="subtleTag">{result.bloom_level}</span>
                </div>
                <strong className="listTitle">{result.question_text}</strong>
                <p className="muted">
                  {result.student_name ?? "Unassigned learner"} • {result.feedback}
                </p>
                <Link href={`/teacher/results/${result.id}`} className="button secondary">
                  Open detail
                </Link>
              </div>
            ))}
            {results.length === 0 ? (
              <div className="notice">Student submissions will appear here once an assessment is completed.</div>
            ) : null}
          </div>
        </div>

        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Reporting pulse</p>
              <h2>Class insight</h2>
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
                  <strong>Common Bloom</strong>
                  <p className="muted">{classSummary.most_common_bloom_level}</p>
                </div>
                <div className="miniCard">
                  <strong>Graded tasks</strong>
                  <p className="muted">{gradedAssignments.length}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="notice">Class reporting becomes richer as students submit more attempts.</div>
          )}
        </div>
      </section>
    </div>
  );
}
