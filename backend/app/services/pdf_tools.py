import hashlib
import io

import pdfplumber


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    text_content: list[str] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_content.append(page_text.strip())

    return "\n\n".join(text_content)


def generate_textbook_id(text_content: str) -> str:
    signature_text = text_content[:5000]
    return hashlib.md5(signature_text.encode("utf-8")).hexdigest()
