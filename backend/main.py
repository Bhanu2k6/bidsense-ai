from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from services.document_ai import extract_text_from_pdf
from services.analysis_engine import analyze

# ---------------------------------------------------------
# App Init
# ---------------------------------------------------------
app = FastAPI(title="BidSense AI Backend")

# ---------------------------------------------------------
# ✅ CORS (IMPORTANT – DO NOT DUPLICATE)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows Vercel + localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"status": "BidSense Backend is running"}

# ---------------------------------------------------------
# 🔍 Extract PDF Text (Debug / Test)
# ---------------------------------------------------------
@app.post("/extract")
async def extract_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        text = await extract_text_from_pdf(file)
        return {
            "filename": file.filename,
            "text": text
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {str(e)}"
        )

# ---------------------------------------------------------
# 🧠 Analyze Tender + Vendors
# ---------------------------------------------------------
@app.post("/analyze")
async def analyze_endpoint(
    tender: UploadFile = File(...),
    vendors: List[UploadFile] = File(...)
):
    if not tender.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Tender must be a PDF")

    if not vendors or len(vendors) == 0:
        raise HTTPException(status_code=400, detail="At least one vendor PDF is required")

    for v in vendors:
        if not v.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="All vendor files must be PDFs")

    vendor_dict = {
        f"vendor_{i+1}": v
        for i, v in enumerate(vendors)
    }

    try:
        result = await analyze(tender, vendor_dict)
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal analysis error: {str(e)}"
        )