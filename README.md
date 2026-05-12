# BidSense AI

BidSense AI is an intelligent tender evaluation system that automates vendor bid analysis using AI-assisted scoring techniques.

## Features

- Upload tender PDF documents
- Upload multiple vendor bid PDFs
- Technical score evaluation
- Financial score evaluation
- Risk analysis and compliance checking
- Fraud similarity detection
- Automated winner recommendation
- Responsive dashboard UI

## Tech Stack

### Frontend
- React.js
- CSS

### Backend
- FastAPI
- Python

### AI / Processing
- PDF text extraction
- TF-IDF similarity detection
- Rule-based risk scoring

## Project Workflow

1. Upload tender document
2. Upload vendor bid documents
3. System extracts and analyzes vendor information
4. Vendors are scored based on:
   - Technical compliance
   - Financial competitiveness
   - Risk evaluation
5. Best vendor recommendation is generated

## Setup Instructions

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

## Future Improvements

- Advanced AI recommendation engine
- Real-time analytics dashboard
- Authentication system
- Cloud deployment improvements