"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import {
  getDemoCases,
  getQuestions,
  gradeAnswer,
  type DemoCase,
  type QuestionConfig
} from "../lib/api";

export function StudentWorkbench() {
  const [questions, setQuestions] = useState<QuestionConfig[]>([]);
  const [demoCases, setDemoCases] = useState<DemoCase[]>([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState("");
  const [studentAnswer, setStudentAnswer] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  useEffect(() => {
    async function loadQuestions() {
      try {
        const data = await getQuestions();
        setQuestions(data);
        if (data[0]) {
          setSelectedQuestionId(data[0].id);
        }
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load questions."
        );
      }
    }

    void loadQuestions();
  }, []);

  useEffect(() => {
    async function loadDemoCases() {
      if (!selectedQuestionId) {
        setDemoCases([]);
        return;
      }

      try {
        const data = await getDemoCases(selectedQuestionId);
        setDemoCases(data.items);
      } catch {
        setDemoCases([]);
      }
    }

    void loadDemoCases();
  }, [selectedQuestionId]);

  const selectedQuestion = questions.find(
    (question) => question.id === selectedQuestionId
  );

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    startTransition(async () => {
      try {
        const result = await gradeAnswer({
          question_id: selectedQuestionId,
          student_answer: studentAnswer
        });
        router.push(`/results/${result.id}`);
      } catch (submitError) {
        setError(
          submitError instanceof Error
            ? submitError.message
            : "Could not grade this answer."
        );
      }
    });
  }

  function loadDemoAnswer(answer: string) {
    setStudentAnswer(answer);
  }

  function clearAnswer() {
    setStudentAnswer("");
  }

  return (
    <>
      <section className="pageIntro">
        <p className="eyebrow">Student workspace</p>
        <h1>Grade an answer without extra setup.</h1>
        <p>
          Choose a question, paste or write the answer, then grade it. You can
          also load a prepared demo answer with one click.
        </p>
      </section>

      <section className="gridPanels">
      <div className="formPanel">
        <h2>Answer submission</h2>
        <p className="helperText">
          This is the simplest path for the live demo.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="question-select">Question</label>
            <select
              id="question-select"
              value={selectedQuestionId}
              onChange={(event) => setSelectedQuestionId(event.target.value)}
            >
              {questions.map((question) => (
                <option key={question.id} value={question.id}>
                  {question.question_text}
                </option>
              ))}
            </select>
            <span className="fieldHint">
              {selectedQuestion?.expected_concepts.length
                ? `Expected concepts: ${selectedQuestion.expected_concepts.join(", ")}`
                : "Select a question to see the expected concepts."}
            </span>
          </div>

          <div className="field">
            <label htmlFor="student-answer">Student answer</label>
            <textarea
              id="student-answer"
              value={studentAnswer}
              onChange={(event) => setStudentAnswer(event.target.value)}
              placeholder="Write a clear explanation in your own words..."
            />
          </div>

          {error ? <p className="error">{error}</p> : null}

          <div className="actions">
            <button type="submit" disabled={isPending || !selectedQuestionId}>
              {isPending ? "Grading..." : "Grade answer"}
            </button>
            <button type="button" className="secondary" onClick={clearAnswer}>
              Clear
            </button>
          </div>
        </form>
      </div>

      <div className="scorePanel">
        <h2>Quick demo answers</h2>
        <p className="helperText">
          Use these when you want to show shallow, deep, or off-topic grading fast.
        </p>
        <div className="panelList">
          <div className="listCard">
            <strong className="listTitle">Current question</strong>
            <p>{selectedQuestion?.question_text ?? "No question loaded yet."}</p>
            <p className="muted">
              Best demo: compare a shallow answer and a deep answer for the same question.
            </p>
          </div>
          {demoCases.map((demoCase) => (
            <div className="listCard" key={demoCase.id}>
              <div className="pillRow">
                <strong className="listTitle">{demoCase.label}</strong>
                <span className="pill">{demoCase.category}</span>
              </div>
              <p className="muted">{demoCase.expected_outcome}</p>
              <button
                type="button"
                className="secondary"
                onClick={() => loadDemoAnswer(demoCase.student_answer)}
              >
                Use demo answer
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
    </>
  );
}
