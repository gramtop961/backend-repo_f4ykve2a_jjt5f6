import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Database helpers
from database import db, create_document, get_documents

app = FastAPI(title="Networks Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Networks Learning API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Schemas for request bodies
class WorksheetPayload(BaseModel):
    name: str
    class_name: str | None = None
    answers: Dict[str, Any]

class ReflectionPayload(BaseModel):
    submission_id: str
    reflection_text: str
    rating: int | None = None

class QuizSubmitPayload(BaseModel):
    name: str
    answers: List[str]

# Simple quiz bank for automatic grading (topology basics)
QUIZ_QUESTIONS = [
    {
        "q": "Which topology uses a central hub/switch to connect all devices?",
        "options": ["Bus", "Star", "Ring", "Mesh"],
        "answer": "Star",
    },
    {
        "q": "In which topology does a single cable act as a backbone for all devices?",
        "options": ["Bus", "Tree", "Hybrid", "Ring"],
        "answer": "Bus",
    },
    {
        "q": "Which topology provides multiple redundant paths between nodes?",
        "options": ["Mesh", "Star", "Bus", "Tree"],
        "answer": "Mesh",
    },
    {
        "q": "Which topology is a hierarchical combination of star and bus?",
        "options": ["Tree", "Ring", "Hybrid", "Mesh"],
        "answer": "Tree",
    },
    {
        "q": "In which topology does data travel in one direction around a circle?",
        "options": ["Ring", "Star", "Bus", "Mesh"],
        "answer": "Ring",
    },
]

@app.get("/api/quiz")
def get_quiz():
    # Return questions without the correct answers
    public_questions = [
        {"q": q["q"], "options": q["options"]} for q in QUIZ_QUESTIONS
    ]
    return {"questions": public_questions}

@app.post("/api/quiz/submit")
def submit_quiz(payload: QuizSubmitPayload):
    if len(payload.answers) != len(QUIZ_QUESTIONS):
        raise HTTPException(status_code=400, detail="Invalid number of answers")
    score = 0
    for given, meta in zip(payload.answers, QUIZ_QUESTIONS):
        if given == meta["answer"]:
            score += 1
    # Persist attempt
    attempt_doc = {
        "name": payload.name,
        "score": score,
        "total": len(QUIZ_QUESTIONS),
        "answers": payload.answers,
    }
    create_document("quizattempt", attempt_doc)
    return {"score": score, "total": len(QUIZ_QUESTIONS)}

@app.post("/api/worksheet")
def submit_worksheet(payload: WorksheetPayload):
    doc = {
        "name": payload.name,
        "class_name": payload.class_name,
        "answers": payload.answers,
    }
    inserted = create_document("worksheetsubmission", doc)
    # Return inserted id for linking reflection
    return {"submission_id": str(inserted.get("_id", ""))}

@app.post("/api/reflection")
def submit_reflection(payload: ReflectionPayload):
    doc = {
        "submission_id": payload.submission_id,
        "reflection_text": payload.reflection_text,
        "rating": payload.rating,
    }
    create_document("reflection", doc)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
