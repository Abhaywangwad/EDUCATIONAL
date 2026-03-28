"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import {
  createTeacherAssignment,
  generateQuestionsFromPdf,
  getDemoUsers,
  getQuestions,
  getTeacherAssignments,
  saveQuestion,
  type GeneratedQuestionSuggestion,
  type PortalUser,
  type QuestionConfig,
  type TeacherAssignment
} from "../lib/api";

function parseConcepts(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseSynonyms(value: string): Record<string, string[]> {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .reduce<Record<string, string[]>>((accumulator, line) => {
      const [conceptPart, synonymPart = ""] = line.split(":");
      const concept = conceptPart.trim();
      if (!concept) {
        return accumulator;
      }

      accumulator[concept] = synonymPart
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      return accumulator;
    }, {});
}

function formatSynonyms(synonyms: Record<string, string[]>) {
  return Object.entries(synonyms)
    .map(([concept, values]) => `${concept}: ${values.join(", ")}`)
    .join("\n");
}

const defaultWeights = {
  keyword_coverage: 0.3,
  grammar_readability: 0.2,
  facts_understanding: 0.5
};

export function TeacherWorkbench() {
  const [questions, setQuestions] = useState<QuestionConfig[]>([]);
  const [students, setStudents] = useState<PortalUser[]>([]);
  const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [questionText, setQuestionText] = useState("");
  const [modelAnswer, setModelAnswer] = useState("");
  const [conceptText, setConceptText] = useState("");
  const [synonymText, setSynonymText] = useState("");
  const [weights, setWeights] = useState(defaultWeights);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  const [assignmentQuestionId, setAssignmentQuestionId] = useState("");
  const [selectedStudentId, setSelectedStudentId] = useState("");
  const [assignmentInstructions, setAssignmentInstructions] = useState(
    "Write in your own words and explain the main idea clearly."
  );
  const [assignmentDueLabel, setAssignmentDueLabel] = useState("Next class, 10:00 AM");
  const [assignmentDuration, setAssignmentDuration] = useState(20);
  const [assignmentMessage, setAssignmentMessage] = useState("");
  const [isAssigning, startAssigning] = useTransition();

  const [textbookFile, setTextbookFile] = useState<File | null>(null);
  const [textbookPreview, setTextbookPreview] = useState("");
  const [suggestions, setSuggestions] = useState<GeneratedQuestionSuggestion[]>([]);
  const [generationMessage, setGenerationMessage] = useState("");
  const [isGenerating, startGeneration] = useTransition();

  useEffect(() => {
    async function loadData() {
      try {
        const [questionData, userData, assignmentData] = await Promise.all([
          getQuestions(),
          getDemoUsers(),
          getTeacherAssignments()
        ]);
        setQuestions(questionData);
        setStudents(userData.students);
        setAssignments(assignmentData.items);
        if (questionData[0]) {
          setAssignmentQuestionId(questionData[0].id);
        }
        if (userData.students[0]) {
          setSelectedStudentId(userData.students[0].id);
        }
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load assessment data."
        );
      }
    }

    void loadData();
  }, []);

  const totalWeight = useMemo(
    () =>
      Number(weights.keyword_coverage) +
      Number(weights.grammar_readability) +
      Number(weights.facts_understanding),
    [weights]
  );
  const totalWeightLabel = totalWeight.toFixed(2);
  const isWeightValid = Math.abs(totalWeight - 1) < 0.001;

  function loadQuestion(question: QuestionConfig) {
    setActiveId(question.id);
    setQuestionText(question.question_text);
    setModelAnswer(question.model_answer);
    setConceptText(question.expected_concepts.join(", "));
    setSynonymText(formatSynonyms(question.synonyms));
    setWeights(question.weights);
    setAssignmentQuestionId(question.id);
    setMessage(`Loaded "${question.question_text}" for editing.`);
    setError("");
  }

  function loadSuggestion(suggestion: GeneratedQuestionSuggestion) {
    setActiveId(null);
    setQuestionText(suggestion.question_text);
    setModelAnswer(suggestion.model_answer);
    setConceptText(suggestion.expected_concepts.join(", "));
    setSynonymText("");
    setMessage("Loaded AI suggestion into the assessment form. Review and save it.");
    setError("");
  }

  function resetForm() {
    setActiveId(null);
    setQuestionText("");
    setModelAnswer("");
    setConceptText("");
    setSynonymText("");
    setWeights(defaultWeights);
    setMessage("Ready to create a new assessment.");
    setError("");
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError("");

    startTransition(async () => {
      try {
        const saved = await saveQuestion({
          id: activeId ?? undefined,
          question_text: questionText,
          model_answer: modelAnswer,
          expected_concepts: parseConcepts(conceptText),
          synonyms: parseSynonyms(synonymText),
          weights
        });

        setQuestions((current) => [
          saved,
          ...current.filter((item) => item.id !== saved.id)
        ]);
        setActiveId(saved.id);
        setAssignmentQuestionId(saved.id);
        setMessage("Assessment saved successfully.");
      } catch (saveError) {
        setError(
          saveError instanceof Error
            ? saveError.message
            : "Could not save the assessment."
        );
      }
    });
  }

  function handleGenerateFromPdf() {
    if (!textbookFile) {
      setGenerationMessage("Choose a PDF first.");
      return;
    }

    setGenerationMessage("");
    startGeneration(async () => {
      try {
        const data = await generateQuestionsFromPdf(textbookFile);
        setSuggestions(data.suggestions);
        setTextbookPreview(data.extracted_preview);
        setGenerationMessage(
          `Generated ${data.suggestions.length} suggestion${data.suggestions.length === 1 ? "" : "s"} from the uploaded textbook.`
        );
      } catch (generationError) {
        setGenerationMessage(
          generationError instanceof Error
            ? generationError.message
            : "Could not generate textbook questions."
        );
      }
    });
  }

  function handleAssignAssessment(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAssignmentMessage("");

    startAssigning(async () => {
      try {
        const saved = await createTeacherAssignment({
          question_id: assignmentQuestionId,
          student_id: selectedStudentId,
          instructions: assignmentInstructions,
          due_label: assignmentDueLabel,
          duration_minutes: assignmentDuration
        });
        setAssignments((current) => [saved, ...current]);
        setAssignmentMessage(`Assigned "${saved.question_text}" to ${saved.student_name}.`);
      } catch (assignmentError) {
        setAssignmentMessage(
          assignmentError instanceof Error
            ? assignmentError.message
            : "Could not assign this assessment."
        );
      }
    });
  }

  return (
    <div className="portalContent">
      <section className="portalPanelGrid">
        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Assessment studio</p>
              <h2>Create or refine a subjective question</h2>
            </div>
            <span className={`inlineStatus ${isWeightValid ? "statusGood" : "statusWarn"}`}>
              Weight total {totalWeightLabel}
            </span>
          </div>

          <div className="sectionStack">
            <div className="miniCard">
              <strong>Import from textbook PDF</strong>
              <p className="muted">
                Upload a textbook extract to generate editable question suggestions with model answers and key concepts.
              </p>
              <div className="field">
                <label htmlFor="textbook-upload">Textbook PDF</label>
                <input
                  id="textbook-upload"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={(event) => setTextbookFile(event.target.files?.[0] ?? null)}
                />
              </div>
              <div className="actions">
                <button type="button" onClick={handleGenerateFromPdf} disabled={isGenerating}>
                  {isGenerating ? "Generating..." : "Generate suggestions"}
                </button>
              </div>
              {generationMessage ? <p className="notice">{generationMessage}</p> : null}
              {textbookPreview ? (
                <div className="notice">
                  <strong>Extract preview</strong>
                  <p className="muted">{textbookPreview}</p>
                </div>
              ) : null}
            </div>

            {suggestions.length > 0 ? (
              <div className="panelList">
                {suggestions.map((suggestion, index) => (
                  <div className="listCard" key={`${suggestion.question_text}-${index}`}>
                    <strong className="listTitle">{suggestion.question_text}</strong>
                    <p className="muted">{suggestion.model_answer}</p>
                    <p className="muted">Concepts: {suggestion.expected_concepts.join(", ")}</p>
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => loadSuggestion(suggestion)}
                    >
                      Load into editor
                    </button>
                  </div>
                ))}
              </div>
            ) : null}

            <form onSubmit={handleSubmit} className="sectionStack">
              <div className="field">
                <label htmlFor="question-text">Question</label>
                <textarea
                  id="question-text"
                  value={questionText}
                  onChange={(event) => setQuestionText(event.target.value)}
                  placeholder="Explain the difference between a process and a thread."
                />
              </div>

              <div className="field">
                <label htmlFor="model-answer">Model answer</label>
                <textarea
                  id="model-answer"
                  value={modelAnswer}
                  onChange={(event) => setModelAnswer(event.target.value)}
                  placeholder="A process is an independent program in execution..."
                />
              </div>

              <div className="field">
                <label htmlFor="concepts">Expected concepts</label>
                <textarea
                  id="concepts"
                  value={conceptText}
                  onChange={(event) => setConceptText(event.target.value)}
                  placeholder="independent execution, own memory space, shared memory"
                />
                <span className="fieldHint">Comma-separated concepts used in keyword coverage.</span>
              </div>

              <div className="field">
                <label htmlFor="synonyms">Optional synonyms</label>
                <textarea
                  id="synonyms"
                  value={synonymText}
                  onChange={(event) => setSynonymText(event.target.value)}
                  placeholder={
                    "shared memory: same memory, common memory\nindependent execution: separate program"
                  }
                />
                <span className="fieldHint">One concept per line: concept: synonym1, synonym2</span>
              </div>

              <div className="weights">
                <div className="weightCard">
                  <label htmlFor="weight-keyword">Keyword coverage</label>
                  <input
                    id="weight-keyword"
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={weights.keyword_coverage}
                    onChange={(event) =>
                      setWeights((current) => ({
                        ...current,
                        keyword_coverage: Number(event.target.value)
                      }))
                    }
                  />
                </div>
                <div className="weightCard">
                  <label htmlFor="weight-grammar">Grammar readability</label>
                  <input
                    id="weight-grammar"
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={weights.grammar_readability}
                    onChange={(event) =>
                      setWeights((current) => ({
                        ...current,
                        grammar_readability: Number(event.target.value)
                      }))
                    }
                  />
                </div>
                <div className="weightCard">
                  <label htmlFor="weight-facts">Facts and depth</label>
                  <input
                    id="weight-facts"
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={weights.facts_understanding}
                    onChange={(event) =>
                      setWeights((current) => ({
                        ...current,
                        facts_understanding: Number(event.target.value)
                      }))
                    }
                  />
                </div>
              </div>

              {message ? <p className="notice">{message}</p> : null}
              {error ? <p className="error">{error}</p> : null}
              {!isWeightValid ? (
                <p className="error">Adjust the weights so the total becomes 1.00.</p>
              ) : null}

              <div className="actions">
                <button type="submit" disabled={isPending || !isWeightValid}>
                  {isPending ? "Saving..." : activeId ? "Update assessment" : "Create assessment"}
                </button>
                <button type="button" className="secondary" onClick={resetForm}>
                  New assessment
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="panelSurface">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Delivery</p>
              <h2>Assign to a student</h2>
            </div>
          </div>

          <form onSubmit={handleAssignAssessment} className="sectionStack">
            <div className="field">
              <label htmlFor="assignment-question">Assessment</label>
              <select
                id="assignment-question"
                value={assignmentQuestionId}
                onChange={(event) => setAssignmentQuestionId(event.target.value)}
              >
                {questions.map((question) => (
                  <option key={question.id} value={question.id}>
                    {question.question_text}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label htmlFor="assignment-student">Student</label>
              <select
                id="assignment-student"
                value={selectedStudentId}
                onChange={(event) => setSelectedStudentId(event.target.value)}
              >
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.full_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label htmlFor="assignment-instructions">Instructions</label>
              <textarea
                id="assignment-instructions"
                value={assignmentInstructions}
                onChange={(event) => setAssignmentInstructions(event.target.value)}
                placeholder="Explain what the student should include in the answer."
              />
            </div>

            <div className="dualFields">
              <div className="field">
                <label htmlFor="assignment-due">Due label</label>
                <input
                  id="assignment-due"
                  value={assignmentDueLabel}
                  onChange={(event) => setAssignmentDueLabel(event.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="assignment-duration">Duration (minutes)</label>
                <input
                  id="assignment-duration"
                  type="number"
                  min="5"
                  max="180"
                  value={assignmentDuration}
                  onChange={(event) => setAssignmentDuration(Number(event.target.value))}
                />
              </div>
            </div>

            {assignmentMessage ? <p className="notice">{assignmentMessage}</p> : null}

            <div className="actions">
              <button type="submit" disabled={isAssigning || !assignmentQuestionId || !selectedStudentId}>
                {isAssigning ? "Assigning..." : "Assign assessment"}
              </button>
            </div>
          </form>

          <div className="sectionDivider" />

          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Existing assessments</p>
              <h2>Question bank</h2>
            </div>
          </div>
          <div className="panelList">
            {questions.map((question) => (
              <div className="listCard" key={question.id}>
                <strong className="listTitle">{question.question_text}</strong>
                <p className="muted">{question.expected_concepts.join(", ")}</p>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => loadQuestion(question)}
                >
                  Edit assessment
                </button>
              </div>
            ))}
          </div>

          <div className="sectionDivider" />

          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Assigned queue</p>
              <h2>Student assessments</h2>
            </div>
          </div>
          <div className="panelList">
            {assignments.map((assignment) => (
              <div className="listCard" key={assignment.id}>
                <div className="pillRow">
                  <strong className="listTitle">{assignment.question_text}</strong>
                  <span className={assignment.status === "graded" ? "pill" : "subtleTag"}>
                    {assignment.status}
                  </span>
                </div>
                <p className="muted">
                  {assignment.student_name} • {assignment.due_label} • {assignment.duration_minutes} min
                </p>
                <p className="muted">{assignment.instructions}</p>
              </div>
            ))}
            {assignments.length === 0 ? (
              <div className="notice">Assign an assessment to make it appear in the student portal.</div>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  );
}
