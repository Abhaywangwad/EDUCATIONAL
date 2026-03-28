export type Role = "teacher" | "student" | "parent";

export type ScoreWeights = {
  keyword_coverage: number;
  grammar_readability: number;
  facts_understanding: number;
};

export type QuestionConfig = {
  id: string;
  question_text: string;
  model_answer: string;
  expected_concepts: string[];
  synonyms: Record<string, string[]>;
  weights: ScoreWeights;
  created_at: string;
  updated_at: string;
};

export type GradeResult = {
  id: string;
  question_id: string;
  question_text: string;
  student_answer: string;
  model_answer: string;
  expected_concepts: string[];
  weights: ScoreWeights;
  student_id?: string | null;
  student_name?: string | null;
  assignment_id?: string | null;
  keyword_score: number;
  semantic_score: number;
  depth_fact_score: number;
  bloom_level: string;
  bloom_score: number;
  grammar_score: number;
  facts_understanding_score: number;
  final_score: number;
  reasoning: string;
  feedback: string;
  created_at: string;
};

export type PortalUser = {
  id: string;
  full_name: string;
  role: Role;
  grade_level?: string | null;
  linked_student_ids: string[];
  linked_parent_ids: string[];
};

export type DemoUsersResponse = {
  teacher: PortalUser;
  students: PortalUser[];
  parents: PortalUser[];
};

export type TeacherAssignment = {
  id: string;
  question_id: string;
  question_text: string;
  student_id: string;
  student_name: string;
  instructions: string;
  due_label: string;
  duration_minutes: number;
  status: "assigned" | "graded";
  latest_result_id?: string | null;
  created_at: string;
  updated_at: string;
};

export type StudentAssessment = {
  id: string;
  question_id: string;
  question_text: string;
  student_id: string;
  student_name: string;
  instructions: string;
  due_label: string;
  duration_minutes: number;
  status: "assigned" | "graded";
  latest_result_id?: string | null;
};

export type StudentAssessmentDetail = StudentAssessment & {
  submission_guidance: string;
};

export type StudentPortalResult = {
  id: string;
  assignment_id?: string | null;
  question_text: string;
  final_score: number;
  bloom_level: string;
  summary: string;
  feedback: string;
  next_step: string;
  created_at: string;
};

export type ParentReportSummary = {
  student_id: string;
  student_name: string;
  grade_level: string;
  latest_score?: number | null;
  latest_bloom_level?: string | null;
  strengths: string[];
  improvements: string[];
  latest_result_id?: string | null;
  report_status: "ready" | "waiting";
  pdf_download_url?: string | null;
};

export type ParentReportDetail = {
  student_id: string;
  student_name: string;
  grade_level: string;
  latest_score?: number | null;
  latest_bloom_level?: string | null;
  progress_summary: string;
  strengths: string[];
  improvements: string[];
  teacher_feedback: string;
  bloom_meaning: string;
  latest_result_id?: string | null;
  pdf_download_url?: string | null;
};

export type DemoCase = {
  id: string;
  question_id: string;
  label: string;
  category: string;
  expected_outcome: string;
  student_answer: string;
};

export type GeneratedQuestionSuggestion = {
  question_text: string;
  model_answer: string;
  expected_concepts: string[];
  source_excerpt: string;
};

export type TextbookGenerationResponse = {
  textbook_id: string;
  extracted_preview: string;
  suggestions: GeneratedQuestionSuggestion[];
};

export type StudentReportResponse = {
  title: string;
  summary: string;
  pdf_download_url: string;
};

export type ClassReportResponse = {
  title: string;
  summary: string;
  average_score: number;
  total_results: number;
  most_common_bloom_level: string;
  pdf_download_url: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export function buildApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: isFormData
        ? init?.headers
        : {
            "Content-Type": "application/json",
            ...(init?.headers ?? {})
          },
      cache: "no-store"
    });
  } catch {
    throw new Error(
      `Could not reach the backend at ${API_BASE_URL}. Start the backend server and try again.`
    );
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Request failed");
  }

  return response.json() as Promise<T>;
}

export function getQuestions(): Promise<QuestionConfig[]> {
  return apiFetch<QuestionConfig[]>("/api/questions");
}

export function saveQuestion(payload: {
  id?: string;
  question_text: string;
  model_answer: string;
  expected_concepts: string[];
  synonyms: Record<string, string[]>;
  weights: ScoreWeights;
}): Promise<QuestionConfig> {
  return apiFetch<QuestionConfig>("/api/questions", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function gradeAnswer(payload: {
  question_id: string;
  student_answer: string;
  student_id?: string;
  assignment_id?: string;
}): Promise<GradeResult> {
  return apiFetch<GradeResult>("/api/grade", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getRecentResults(): Promise<{ items: GradeResult[] }> {
  return apiFetch<{ items: GradeResult[] }>("/api/results");
}

export function getResult(id: string): Promise<GradeResult> {
  return apiFetch<GradeResult>(`/api/results/${id}`);
}

export function getDemoCases(questionId?: string): Promise<{ items: DemoCase[] }> {
  const query = questionId ? `?question_id=${encodeURIComponent(questionId)}` : "";
  return apiFetch<{ items: DemoCase[] }>(`/api/demo-cases${query}`);
}

export function generateQuestionsFromPdf(file: File): Promise<TextbookGenerationResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return apiFetch<TextbookGenerationResponse>("/api/textbooks/generate-questions", {
    method: "POST",
    body: formData
  });
}

export function getStudentReport(resultId: string): Promise<StudentReportResponse> {
  return apiFetch<StudentReportResponse>(`/api/reports/results/${resultId}/student`);
}

export function getClassSummary(limit = 12): Promise<ClassReportResponse> {
  return apiFetch<ClassReportResponse>(`/api/reports/class-summary?limit=${limit}`);
}

export function getDemoUsers(): Promise<DemoUsersResponse> {
  return apiFetch<DemoUsersResponse>("/api/demo-users");
}

export function getTeacherAssignments(): Promise<{ items: TeacherAssignment[] }> {
  return apiFetch<{ items: TeacherAssignment[] }>("/api/teacher/assignments");
}

export function createTeacherAssignment(payload: {
  question_id: string;
  student_id: string;
  instructions: string;
  due_label: string;
  duration_minutes: number;
}): Promise<TeacherAssignment> {
  return apiFetch<TeacherAssignment>("/api/teacher/assignments", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getStudentAssessments(studentId: string): Promise<{ items: StudentAssessment[] }> {
  return apiFetch<{ items: StudentAssessment[] }>(
    `/api/student/assessments?student_id=${encodeURIComponent(studentId)}`
  );
}

export function getStudentAssessment(
  assignmentId: string,
  studentId: string
): Promise<StudentAssessmentDetail> {
  return apiFetch<StudentAssessmentDetail>(
    `/api/student/assessments/${assignmentId}?student_id=${encodeURIComponent(studentId)}`
  );
}

export function submitStudentAssessment(
  assignmentId: string,
  payload: { student_id: string; student_answer: string }
): Promise<StudentPortalResult> {
  return apiFetch<StudentPortalResult>(`/api/student/assessments/${assignmentId}/submit`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getStudentPortalResult(
  attemptId: string,
  studentId: string
): Promise<StudentPortalResult> {
  return apiFetch<StudentPortalResult>(
    `/api/student/results/${attemptId}?student_id=${encodeURIComponent(studentId)}`
  );
}

export function getParentReports(parentId: string): Promise<{ items: ParentReportSummary[] }> {
  return apiFetch<{ items: ParentReportSummary[] }>(
    `/api/parent/reports?parent_id=${encodeURIComponent(parentId)}`
  );
}

export function getParentReportDetail(
  studentId: string,
  parentId: string
): Promise<ParentReportDetail> {
  return apiFetch<ParentReportDetail>(
    `/api/parent/reports/${studentId}?parent_id=${encodeURIComponent(parentId)}`
  );
}
