from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import TextbookGenerationResponse
from ..services.ai_generation import generate_question_suggestions_from_text
from ..services.pdf_tools import extract_text_from_pdf_bytes, generate_textbook_id


router = APIRouter(prefix="/api/textbooks", tags=["textbooks"])


@router.post("/generate-questions", response_model=TextbookGenerationResponse)
async def generate_questions_from_textbook(file: UploadFile = File(...)) -> TextbookGenerationResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    pdf_bytes = await file.read()
    text_content = extract_text_from_pdf_bytes(pdf_bytes)
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="Could not extract readable text from the PDF.")

    suggestions = generate_question_suggestions_from_text(text_content)
    return TextbookGenerationResponse(
        textbook_id=generate_textbook_id(text_content),
        extracted_preview=text_content[:700],
        suggestions=suggestions,
    )
