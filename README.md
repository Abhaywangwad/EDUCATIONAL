# Human-Like Grading System

This repository contains a hackathon-ready multi-role education platform for grading typed Computer Science theory answers with a teacher-style breakdown.

- `Cleaner`: text normalization and concept extraction
- `Grammar Guard`: readability and answer quality heuristics
- `Brain`: keyword coverage, semantic similarity, and LLM-backed depth/factual review
- `Judge`: weighted score aggregation, reasoning, and feedback

The current product now includes:

- `Teacher Portal`: assessment authoring, textbook PDF import, assignment management, detailed review, and reports
- `Student Portal`: assigned assessments, exam-style answer flow, and simplified result view
- `Parent Portal`: plain-language progress report and downloadable PDF access

## Project Layout

```text
backend/
  app/
frontend/
```

## Backend Setup

1. Install Python 3.11+.
2. Create a virtual environment inside `backend`.
3. Install dependencies:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in your LLM credentials if you want hosted depth scoring.
5. Start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

The API seeds three demo Computer Science questions on first run, plus curated demo answers for hackathon storytelling.

## Frontend Setup

1. Install dependencies:

```powershell
cd frontend
npm install
```

2. Copy `.env.local.example` to `.env.local`.
3. Start the Next.js app:

```powershell
npm run dev
```

The frontend expects the backend at `http://localhost:8000` by default.

## Environment Variables

### Backend

- `HLGS_LLM_PROVIDER`: `mock`, `openai`, or `openai_compatible`
- `HLGS_LLM_API_KEY`: API key for the hosted model
- `HLGS_LLM_BASE_URL`: default `https://api.openai.com/v1`
- `HLGS_LLM_MODEL`: model name for depth/factual scoring
- `HLGS_CORS_ORIGINS`: JSON array, for example `["http://localhost:3000"]`
- `OPENAI_API_KEY`: optional alias used automatically by the OpenAI path

### Frontend

- `NEXT_PUBLIC_API_BASE_URL`: default `http://localhost:8000`

## Demo Flow

1. Open `/login` and choose a demo role.
2. In the teacher portal, create or adjust a question and assign it to a student.
3. In the student portal, open the assigned assessment and submit an answer.
4. Review the technical result in the teacher portal.
5. Open the parent portal to see the same attempt as a parent-friendly report.

## MVP Notes

- The backend falls back to heuristic semantic and depth scoring if the embedding model or hosted LLM is unavailable.
- SQLite is used for persistence so the demo can run locally with minimal setup.
- The teacher can auto-suggest concepts from the model answer and then edit them before saving.

## OpenAI Depth Scoring

To use a real hosted OpenAI model for the depth scoring layer:

```powershell
cd backend
Copy-Item .env.example .env
```

Then set these values in `backend/.env`:

```env
HLGS_LLM_PROVIDER=openai
HLGS_LLM_MODEL=gpt-5-mini
OPENAI_API_KEY=your_real_api_key_here
```

The OpenAI path uses the Responses API with structured JSON output for `score`, `reasoning`, and `feedback`.

If you do not want to edit the file manually, you can set the key securely with:

```powershell
.\scripts\set-openai-key.ps1
```

## Demo Dataset

The student screen now includes polished demo answers for each seeded question:

- shallow but correct
- deep conceptual
- paraphrased correct
- grammar-noisy but correct
- off-topic / irrelevant

This makes it easy to show that deeper understanding beats surface-level wording during the demo.

## Portal Routes

- `/login`
- `/teacher`
- `/teacher/assessments`
- `/teacher/results`
- `/teacher/reports`
- `/student`
- `/student/assessments/[id]`
- `/student/results/[id]`
- `/parent`
- `/parent/reports/[studentId]`
