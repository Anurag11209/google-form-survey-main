from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, models, schemas, google_services
from .database import SessionLocal, engine, get_db
from .models import SurveyStatus

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Google Forms Creation & Review System",
    description="API for creating Google Forms from text, reviewing, and approving them.",
    version="0.1.0",
)

# --- BEGIN CORS MIDDLEWARE CONFIGURATION ---
origins = [
    "http://localhost:3000",  # Your React frontend
    "http://localhost:3001",  # If you ever run React on another port for dev
    # Add any other origins you might need
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    # allow_origins=["*"], # Allows all origins (less secure, use with caution)
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers
)
# --- END CORS MIDDLEWARE CONFIGURATION ---

@app.post("/surveys/", response_model=schemas.SurveyResponse, status_code=status.HTTP_201_CREATED)
def create_survey_endpoint(survey_create: schemas.SurveyCreate, db: Session = Depends(get_db)):
    questions_list = [q.strip() for q in survey_create.questions_text.splitlines() if q.strip()]
    if not questions_list:
        raise HTTPException(status_code=400, detail="No questions provided.")

    title = survey_create.title or questions_list[0][:80] # Use first line or provided title
    
    # Create Google Form
    form_id, form_url = google_services.create_google_form(title, questions_list)
    if not form_id or not form_url:
        raise HTTPException(status_code=500, detail="Failed to create Google Form.")

    # Create survey entry in DB
    db_survey = crud.create_survey(db, survey_create=survey_create, form_id=form_id, form_url=form_url)
    return db_survey


@app.get("/surveys/", response_model=List[schemas.SurveyResponse])
def read_surveys_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    surveys = crud.get_surveys(db, skip=skip, limit=limit)
    return surveys


@app.get("/surveys/{survey_id}/", response_model=schemas.SurveyResponse)
def read_survey_endpoint(survey_id: int, db: Session = Depends(get_db)):
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey


@app.post("/surveys/{survey_id}/approve", response_model=schemas.SurveyResponse)
def approve_survey_endpoint(survey_id: int, approve_request: schemas.ApproveSurveyRequest, db: Session = Depends(get_db)):
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    if db_survey.status != SurveyStatus.DRAFT:
        raise HTTPException(status_code=400, detail=f"Survey cannot be approved. Current status: {db_survey.status.value}")

    # Send email
    email_subject = f"New Survey Ready: {db_survey.title or 'Untitled Survey'}"
    email_body = (
        f"Hello,\n\nA new survey '{db_survey.title or 'Untitled Survey'}' has been approved and is ready for you.\n"
        f"Please find it here: {db_survey.form_url}\n\nThanks!"
    )
    email_sent = google_services.send_email(
        to_email=approve_request.recipient_email,
        subject=email_subject,
        body_text=email_body
    )
    if not email_sent:
        # Log this error, but maybe still approve the survey? Or make it transactional.
        # For now, we proceed to approve even if email fails, but flag it.
        # Could raise an HTTPException here if email is critical.
        print(f"Warning: Email notification failed for survey {survey_id} to {approve_request.recipient_email}")
        # For a robust system, you might want to handle this failure more gracefully.

    updated_survey = crud.update_survey_status(db, survey_id, SurveyStatus.APPROVED, approve_request.recipient_email)
    if updated_survey is None: # Should not happen if previous checks passed
        raise HTTPException(status_code=500, detail="Failed to update survey status after approval.")
    return updated_survey


@app.delete("/surveys/{survey_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_survey_endpoint(survey_id: int, db: Session = Depends(get_db)):
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # For now, we'll just mark as deleted.
    # If you want to delete the Google Form itself, you'd need to add a call
    # to google_services.delete_google_form(db_survey.google_form_id)
    # The Google Drive API is typically used for deleting files, including Forms.
    # service.files().delete(fileId=form_id).execute() -> requires Drive API scope
    
    crud.delete_survey_db(db, survey_id=survey_id)
    return None # FastAPI handles 204 No Content response

# Simple health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# To run (from backend/ folder):
# First time, it will ask you to authenticate with Google via browser.
# uvicorn app.main:app --reload