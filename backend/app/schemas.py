from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ScoreWeights(BaseModel):
    keyword_coverage: float = 0.3
    grammar_readability: float = 0.2
    facts_understanding: float = 0.5

    @model_validator(mode="after")
    def validate_weights(self) -> "ScoreWeights":
        for field_name in ("keyword_coverage", "grammar_readability", "facts_understanding"):
            value = getattr(self, field_name)
            if value < 0 or value > 1:
                raise ValueError("Weights must be between 0 and 1.")

        total = self.keyword_coverage + self.grammar_readability + self.facts_understanding
        if abs(total - 1.0) > 0.001:
            raise ValueError("Weights must add up to 1.0.")
        return self


class QuestionConfigInput(BaseModel):
    id: str | None = None
    question_text: str = Field(min_length=10)
    model_answer: str = Field(min_length=20)
    expected_concepts: list[str] = Field(default_factory=list)
    synonyms: dict[str, list[str]] = Field(default_factory=dict)
    weights: ScoreWeights = Field(default_factory=ScoreWeights)


class QuestionConfig(QuestionConfigInput):
    id: str
    created_at: datetime
    updated_at: datetime


class GradeRequest(BaseModel):
    question_id: str
    student_answer: str = Field(min_length=1)
    student_id: str | None = None
    assignment_id: str | None = None


class GradeBreakdown(BaseModel):
    keyword_score: float
    semantic_score: float
    depth_fact_score: float
    bloom_level: str
    bloom_score: float
    grammar_score: float
    facts_understanding_score: float
    final_score: float
    reasoning: str
    feedback: str


class GradeResult(BaseModel):
    id: str
    question_id: str
    question_text: str
    student_answer: str
    model_answer: str
    expected_concepts: list[str]
    weights: ScoreWeights
    student_id: str | None = None
    student_name: str | None = None
    assignment_id: str | None = None
    keyword_score: float
    semantic_score: float
    depth_fact_score: float
    bloom_level: str
    bloom_score: float
    grammar_score: float
    facts_understanding_score: float
    final_score: float
    reasoning: str
    feedback: str
    created_at: datetime


class ResultsListResponse(BaseModel):
    items: list[GradeResult]


class PortalUser(BaseModel):
    id: str
    full_name: str
    role: Literal["teacher", "student", "parent"]
    grade_level: str | None = None
    linked_student_ids: list[str] = Field(default_factory=list)
    linked_parent_ids: list[str] = Field(default_factory=list)


class DemoUsersResponse(BaseModel):
    teacher: PortalUser
    students: list[PortalUser]
    parents: list[PortalUser]


class AssessmentAssignmentInput(BaseModel):
    question_id: str
    student_id: str
    instructions: str = Field(min_length=10, max_length=300)
    due_label: str = Field(min_length=3, max_length=80)
    duration_minutes: int = Field(default=20, ge=5, le=180)


class AssessmentAssignment(BaseModel):
    id: str
    question_id: str
    question_text: str
    student_id: str
    student_name: str
    instructions: str
    due_label: str
    duration_minutes: int
    status: Literal["assigned", "graded"]
    latest_result_id: str | None = None
    created_at: datetime
    updated_at: datetime


class TeacherAssignmentsResponse(BaseModel):
    items: list[AssessmentAssignment]


class StudentAssessmentSummary(BaseModel):
    id: str
    question_id: str
    question_text: str
    student_id: str
    student_name: str
    instructions: str
    due_label: str
    duration_minutes: int
    status: Literal["assigned", "graded"]
    latest_result_id: str | None = None


class StudentAssessmentDetail(StudentAssessmentSummary):
    submission_guidance: str


class StudentAssessmentsResponse(BaseModel):
    items: list[StudentAssessmentSummary]


class StudentSubmissionRequest(BaseModel):
    student_id: str
    student_answer: str = Field(min_length=1)


class StudentPortalResult(BaseModel):
    id: str
    assignment_id: str | None = None
    question_text: str
    final_score: float
    bloom_level: str
    summary: str
    feedback: str
    next_step: str
    created_at: datetime


class ParentReportSummary(BaseModel):
    student_id: str
    student_name: str
    grade_level: str
    latest_score: float | None = None
    latest_bloom_level: str | None = None
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    latest_result_id: str | None = None
    report_status: Literal["ready", "waiting"]
    pdf_download_url: str | None = None


class ParentReportsResponse(BaseModel):
    items: list[ParentReportSummary]


class ParentReportDetail(BaseModel):
    student_id: str
    student_name: str
    grade_level: str
    latest_score: float | None = None
    latest_bloom_level: str | None = None
    progress_summary: str
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    teacher_feedback: str
    bloom_meaning: str
    latest_result_id: str | None = None
    pdf_download_url: str | None = None


class DemoCase(BaseModel):
    id: str
    question_id: str
    label: str
    category: str
    expected_outcome: str
    student_answer: str


class DemoCasesResponse(BaseModel):
    items: list[DemoCase]


class GeneratedQuestionSuggestion(BaseModel):
    question_text: str
    model_answer: str
    expected_concepts: list[str]
    source_excerpt: str


class TextbookGenerationResponse(BaseModel):
    textbook_id: str
    extracted_preview: str
    suggestions: list[GeneratedQuestionSuggestion]


class StudentReportResponse(BaseModel):
    title: str
    summary: str
    pdf_download_url: str


class ClassReportResponse(BaseModel):
    title: str
    summary: str
    average_score: float
    total_results: int
    most_common_bloom_level: str
    pdf_download_url: str
