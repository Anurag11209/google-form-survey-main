import os.path
from google.oauth2.service_account import Credentials # <--- CHANGE IMPORT
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from typing import Optional # Make sure Optional is imported

# If modifying these SCOPES, delete the file token.json. (This comment is less relevant for service accounts)
SCOPES_FORMS = ["https://www.googleapis.com/auth/forms.body", "https://www.googleapis.com/auth/drive"] # Drive scope might be needed for permissions/ownership
SCOPES_GMAIL = ["https://www.googleapis.com/auth/gmail.send"]

# TOKEN_PATH = "token.json" # Not needed for service accounts
# CREDENTIALS_PATH = "credentials.json" # Not needed for service accounts if using service_account.json

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'service_account.json') # Assumes service_account.json is in backend/
                                                                                          # And google_services.py is in backend/app/
                                                                                          # Adjust path if needed.

# Ensure SERVICE_ACCOUNT_FILE path is correct relative to where google_services.py is.
# If google_services.py is in backend/app/ and service_account.json is in backend/, then:
# SERVICE_ACCOUNT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'service_account.json'))
# A simpler approach if running from backend/ directory:
SERVICE_ACCOUNT_FILE = "service_account.json"


def get_google_service(service_name: str, version: str, scopes: list[str]):
    """Generic function to get a Google API service client using a service account."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: Service account file not found at {os.path.abspath(SERVICE_ACCOUNT_FILE)}")
        print("Please download your service account JSON key and place it correctly.")
        return None
    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes
        )
        service = build(service_name, version, credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Google service '{service_name}' with service account: {e}")
        return None


def create_google_form(title: str, questions: list[str]) -> tuple[Optional[str], Optional[str]]:
    """Creates a new Google Form and returns (form_id, form_url) or (None, None) on error."""
    service = get_google_service("forms", "v1", SCOPES_FORMS)
    if not service:
        return None, None
        
    try:
        form_content = {
            "info": {"title": title if title else "New Survey"},
        }
        created_form = service.forms().create(body=form_content).execute()
        form_id = created_form["formId"]
        form_url = created_form["responderUri"]

        # IMPORTANT: By default, the service account will own this form.
        # If other users need to access/edit it, you'll need to use the Drive API
        # to change permissions or transfer ownership IF the Forms API doesn't allow
        # specifying owner/editor during creation.
        # Example (requires Drive API and appropriate scopes):
        # drive_service = get_google_service("drive", "v3", ["https://www.googleapis.com/auth/drive"])
        # if drive_service:
        #     user_permission = {
        #         'type': 'user',
        #         'role': 'writer', # or 'owner'
        #         'emailAddress': 'user@example.com' # The user you want to share with
        #     }
        #     drive_service.permissions().create(
        #         fileId=form_id,
        #         body=user_permission,
        #         fields='id',
        #         sendNotificationEmail=False # Optional
        #     ).execute()
        # else:
        #     print("Warning: Could not get Drive service to set form permissions.")


        if questions:
            requests = []
            for i, q_text in enumerate(questions):
                if not q_text.strip(): continue
                requests.append({
                    "createItem": {
                        "item": {
                            "title": q_text.strip(),
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {"paragraph": False}
                                }
                            },
                        },
                        "location": {"index": i},
                    }
                })
            if requests:
                service.forms().batchUpdate(
                    formId=form_id, body={"requests": requests}
                ).execute()
        
        print(f"Created Google Form via Service Account: {form_id}, URL: {form_url}")
        return form_id, form_url
    except HttpError as err:
        print(f"An error occurred creating form with Service Account: {err}")
        if err.resp.status == 403:
            print("This might be a permission issue. Ensure the service account has rights to create forms or that the API endpoint supports service account creation.")
        return None, None
    except Exception as e:
        print(f"Unexpected error during form creation with Service Account: {e}")
        return None, None


def send_email(to_email: str, subject: str, body_text: str) -> bool:
    # For service accounts, 'me' usually refers to the service account itself.
    # If domain-wide delegation is set up, you can impersonate a user.
    # For simplicity, we'll send as the service account.
    gmail_service = get_google_service("gmail", "v1", SCOPES_GMAIL)
    if not gmail_service:
        return False
        
    try:
        message = MIMEText(body_text)
        message["to"] = to_email
        message["subject"] = subject
        # message["from"] = "your-service-account-email@your-project-id.iam.gserviceaccount.com" # Optional, usually not needed.
                                                                                              # Gmail might show sender as service account name.
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}
        
        send_message = (
            gmail_service.users().messages().send(userId="me", body=create_message).execute() # "me" refers to the service account
        )
        print(f'Sent message to {to_email} via Service Account, Message Id: {send_message["id"]}')
        return True
    except HttpError as error:
        print(f"An error occurred sending email with Service Account: {error}")
        return False
    except Exception as e:
        print(f"Unexpected error during email sending with Service Account: {e}")
        return False