import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, date

from database import db, create_document, get_documents
from schemas import Exercise, Workout, WorkoutSession

app = FastAPI(title="Fitness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Fitness API is running"}

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
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Helper: collection names (lowercase of model class names per convention)
EXERCISE_COLL = "exercise"
WORKOUT_COLL = "workout"
SESSION_COLL = "workoutsession"

# Request models for creating data
class WorkoutCreate(BaseModel):
    title: str
    description: Optional[str] = None
    items: List[dict] = []

class SessionCreate(BaseModel):
    date_str: str
    workout_title: str
    notes: Optional[str] = None
    items: List[dict] = []

@app.post("/api/exercises")
def create_exercise(ex: Exercise):
    try:
        inserted_id = create_document(EXERCISE_COLL, ex)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exercises")
def list_exercises():
    try:
        docs = get_documents(EXERCISE_COLL)
        # Convert ObjectIds to strings if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workouts")
def create_workout(workout: Workout):
    try:
        inserted_id = create_document(WORKOUT_COLL, workout)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workouts")
def list_workouts():
    try:
        docs = get_documents(WORKOUT_COLL)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions")
def log_session(sess: WorkoutSession):
    try:
        inserted_id = create_document(SESSION_COLL, sess)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
def list_sessions(date_str: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {"date_str": date_str} if date_str else {}
        docs = get_documents(SESSION_COLL, filter_dict=filter_dict, limit=limit)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        # sort newest first by created_at if present
        docs.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
