# services/document_ai.py
import io
import logging

import pdfplumber
from fastapi import UploadFile, HTTPException

logger = logging.getLogger("documents")
logger.setLevel(logging.INFO)


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text from a PDF file WITHOUT Google Document AI.
    Uses pdfplumber (local, free, no billing required).
    """
    try:
        # Read file bytes from the UploadFile
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty PDF file")

        # Open the PDF from memory
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

        full_text = "\n\n".join(pages_text).strip()

        if not full_text:
            logger.warning(
                "No text extracted from PDF. It might be a scanned image without embedded text."
            )

        logger.info(
            f"Extracted {len(full_text)} characters of text from PDF '{file.filename}'"
        )

        return full_text

    except HTTPException:
        # Re-raise FastAPI HTTPExceptions directly
        raise
    except Exception as e:
        logger.exception("Error extracting text from PDF")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text from PDF: {e}",
        )
