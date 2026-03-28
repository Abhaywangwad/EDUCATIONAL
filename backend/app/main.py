from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db, seed_demo_questions
from .routers import demo, grading, parent, questions, reports, results, session, student, teacher, textbooks


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_demo_questions()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "HLGS API is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(questions.router)
app.include_router(grading.router)
app.include_router(results.router)
app.include_router(demo.router)
app.include_router(textbooks.router)
app.include_router(reports.router)
app.include_router(session.router)
app.include_router(teacher.router)
app.include_router(student.router)
app.include_router(parent.router)
