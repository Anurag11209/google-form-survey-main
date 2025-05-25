from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum
from .database import Base

class SurveyStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DELETED = "deleted" # Optional: for soft delete

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    google_form_id = Column(String, unique=True, index=True, nullable=True)
    form_url = Column(String, unique=True, nullable=True)
    status = Column(SAEnum(SurveyStatus), default=SurveyStatus.DRAFT)
    questions_text = Column(String) # Store the original text for reference
    recipient_email = Column(String, nullable=True) # Store recipient for approved surveys
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())