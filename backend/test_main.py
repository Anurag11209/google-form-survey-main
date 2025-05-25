from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from app.models import SurveyStatus
from unittest.mock import patch # For mocking Google services

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine) # Create tables in test DB

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Mock Google services to avoid actual API calls during tests
@patch('app.google_services.create_google_form')
@patch('app.google_services.send_email')
def test_create_and_approve_survey(mock_send_email, mock_create_form):
    # Mock successful Google API calls
    mock_create_form.return_value = ("mock_form_id", "http://mock.form.url")
    mock_send_email.return_value = True

    # 1. Create Survey
    response = client.post(
        "/surveys/",
        json={"questions_text": "Q1: What is your name?\nQ2: What is your quest?", "title": "Test Survey"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Survey"
    assert data["status"] == SurveyStatus.DRAFT.value
    assert data["google_form_id"] == "mock_form_id"
    assert data["form_url"] == "http://mock.form.url"
    survey_id = data["id"]
    mock_create_form.assert_called_once()

    # 2. Get Survey
    response = client.get(f"/surveys/{survey_id}/")
    assert response.status_code == 200
    assert response.json()["id"] == survey_id

    # 3. Attempt to approve with invalid status (e.g. if it was already approved)
    #    For this test, we directly try to approve the draft survey.
    #    Let's test approving a draft survey.
    approve_response = client.post(
        f"/surveys/{survey_id}/approve",
        json={"recipient_email": "test@example.com"}
    )
    assert approve_response.status_code == 200
    approved_data = approve_response.json()
    assert approved_data["status"] == SurveyStatus.APPROVED.value
    assert approved_data["recipient_email"] == "test@example.com"
    mock_send_email.assert_called_once_with(
        to_email="test@example.com", 
        subject="New Survey Ready: Test Survey", 
        body_text=f"Hello,\n\nA new survey 'Test Survey' has been approved and is ready for you.\nPlease find it here: http://mock.form.url\n\nThanks!"
    )
    
    # 4. Attempt to approve an already approved survey (should fail)
    fail_approve_response = client.post(
        f"/surveys/{survey_id}/approve",
        json={"recipient_email": "another@example.com"}
    )
    assert fail_approve_response.status_code == 400
    assert "Survey cannot be approved" in fail_approve_response.json()["detail"]

    # 5. List surveys
    response = client.get("/surveys/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 6. Delete survey (soft delete)
    response = client.delete(f"/surveys/{survey_id}/")
    assert response.status_code == 204 # No content

    # Verify it's marked as deleted
    response = client.get(f"/surveys/{survey_id}/")
    assert response.status_code == 200
    assert response.json()["status"] == SurveyStatus.DELETED.value

# Clean up test.db after tests if needed, or use in-memory for tests
# For simplicity, we are using a file based test.db here.