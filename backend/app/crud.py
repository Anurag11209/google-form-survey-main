from sqlalchemy.orm import Session
from . import models, schemas
from .models import SurveyStatus
from typing import Optional

def get_survey(db: Session, survey_id: int):
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()

def get_surveys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Survey).offset(skip).limit(limit).all()

def create_survey(db: Session, survey_create: schemas.SurveyCreate, form_id: Optional[str], form_url: Optional[str]):
    title = survey_create.title
    if not title and survey_create.questions_text:
        title = survey_create.questions_text.splitlines()[0][:80] # Use first line as title
    
    db_survey = models.Survey(
        title=title,
        questions_text=survey_create.questions_text,
        google_form_id=form_id,
        form_url=form_url,
        status=SurveyStatus.DRAFT
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey

def update_survey_status(db: Session, survey_id: int, new_status: SurveyStatus, recipient_email: Optional[str] = None):
    db_survey = get_survey(db, survey_id)
    if not db_survey:
        return None
    db_survey.status = new_status
    if recipient_email:
        db_survey.recipient_email = recipient_email
    db.commit()
    db.refresh(db_survey)
    return db_survey

def delete_survey_db(db: Session, survey_id: int):
    db_survey = get_survey(db, survey_id)
    if not db_survey:
        return None
    # Option 1: Hard delete
    # db.delete(db_survey)
    # db.commit()
    # return {"message": "Survey deleted"}

    # Option 2: Soft delete (mark as deleted)
    db_survey.status = SurveyStatus.DELETED
    db.commit()
    db.refresh(db_survey)
    return db_survey