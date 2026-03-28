"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import {
  getDemoCases,
  getStudentAssessment,
  submitStudentAssessment,
  type DemoCase,
  type StudentAssessmentDetail
} from "../lib/api";
import { useDemoSession } from "../lib/demo-session";

function formatTime(totalSeconds: number) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

export function StudentExamSession({ assignmentId }: { assignmentId: string }) {
  const { session } = useDemoSession("student");
  const [assessment, setAssessment] = useState<StudentAssessmentDetail | null>(null);
  const [demoCases, setDemoCases] = useState<DemoCase[]>([]);
  const [studentAnswer, setStudentAnswer] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  const initialSeconds = useMemo(
    () => (assessment ? assessment.duration_minutes * 60 : 0),
    [assessment]
  );
  const [secondsLeft, setSecondsLeft] = useState(0);

  useEffect(() => {
    async function loadAssessment() {
      if (!session?.userId) {
        return;
      }

      try {
        const data = await getStudentAssessment(assignmentId, session.userId);
        setAssessment(data);
        setSecondsLeft(data.duration_minutes * 60);
        const demoData = await getDemoCases(data.question_id);
        setDemoCases(demoData.items);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load this assessment."
        );
      }
    }

    void loadAssessment();
  }, [assignmentId, session?.userId]);

  useEffect(() => {
    if (!assessment || secondsLeft <= 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setSecondsLeft((current) => (current > 0 ? current - 1 : 0));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [assessment, secondsLeft]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session?.userId) {
      return;
    }
    setError("");

    startTransition(async () => {
      try {
        const result = await submitStudentAssessment(assignmentId, {
          student_id: session.userId,
          student_answer: studentAnswer
        });
        router.push(`/student/results/${result.id}`);
      } catch (submitError) {
        setError(
          submitError instanceof Error
            ? submitError.message
            : "Could not submit this answer."
        );
      }
    });
  }

  if (error) {
    return <div className="portalContent"><p className="error">{error}</p></div>;
  }

  if (!assessment) {
    return <div className="portalContent"><div className="notice">Loading assessment...</div></div>;
  }

  return (
    <div className="portalContent">
      <section className="examLayout">
        <div className="examCard">
          <div className="examHeader">
            <div>
              <p className="eyebrow">Exam session</p>
              <h2>{assessment.question_text}</h2>
              <p className="portalLead">{assessment.instructions}</p>
            </div>
            <div className="examTimer">
              <span className="subtleTag">Time guide</span>
              <strong>{formatTime(secondsLeft || initialSeconds)}</strong>
            </div>
          </div>

          <div className="notice">
            <strong>Answer guidance</strong>
            <p className="muted">{assessment.submission_guidance}</p>
          </div>

          <form onSubmit={handleSubmit} className="sectionStack">
            <div className="field">
              <label htmlFor="student-answer">Your answer</label>
              <textarea
                id="student-answer"
                value={studentAnswer}
                onChange={(event) => setStudentAnswer(event.target.value)}
                placeholder="Write a clear and complete answer..."
              />
            </div>

            {error ? <p className="error">{error}</p> : null}

            <div className="actions">
              <button type="submit" disabled={isPending || !studentAnswer.trim()}>
                {isPending ? "Submitting..." : "Submit answer"}
              </button>
            </div>
          </form>
        </div>

        <aside className="examSidebar">
          <div className="panelSurface">
            <p className="eyebrow">Assessment details</p>
            <h3>Session focus</h3>
            <p className="muted">Due {assessment.due_label}</p>
            <p className="muted">Recommended time: {assessment.duration_minutes} minutes</p>
          </div>

          <div className="panelSurface">
            <p className="eyebrow">Demo helpers</p>
            <h3>Sample answer styles</h3>
            <div className="panelList">
              {demoCases.map((demoCase) => (
                <div className="listCard" key={demoCase.id}>
                  <strong className="listTitle">{demoCase.label}</strong>
                  <p className="muted">{demoCase.expected_outcome}</p>
                  <button
                    type="button"
                    className="secondary"
                    onClick={() => setStudentAnswer(demoCase.student_answer)}
                  >
                    Load sample answer
                  </button>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}
