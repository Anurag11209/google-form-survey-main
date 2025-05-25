from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import SurveyStatus # Re-use enum

class SurveyBase(BaseModel):
    questions_text: str
    title: Optional[str] = None # Optional: can derive from first question

class SurveyCreate(SurveyBase):
    pass

class SurveyUpdate(BaseModel):
    status: Optional[SurveyStatus] = None
    recipient_email: Optional[EmailStr] = None

class SurveyResponse(BaseModel):
    id: int
    title: Optional[str] = None
    google_form_id: Optional[str] = None
    form_url: Optional[str] = None
    status: SurveyStatus
    questions_text: str
    recipient_email: Optional[EmailStr] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # For SQLAlchemy model conversion
        use_enum_values = True # Ensure enum values are strings

class ApproveSurveyRequest(BaseModel):
    recipient_email: EmailStr