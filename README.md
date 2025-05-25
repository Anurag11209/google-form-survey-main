# Google Forms Creation & Review System

This project allows users to dynamically create Google Forms from a text-based question list, review them, and send them via email upon approval.

## Features

*   **FastAPI Backend:**
    *   Accepts text input for survey questions.
    *   Integrates with Google Forms API to create forms.
    *   Implements a review workflow (Draft -> Approved).
    *   Sends email notifications via Gmail API upon approval.
    *   Stores survey metadata in an SQLite database.
    *   Exposes an OpenAPI specification (`/docs`, `/openapi.json`).
*   **ReactJS Frontend:**
    *   Allows manual entry of survey questions.
    *   Displays newly created forms for review.
    *   Allows approval of forms, triggering email notifications.
    *   Supports deleting surveys (soft delete).
*   **Python SDK:**
    *   Generated via OpenAPI Generator CLI for programmatic API interaction.
*   **Automation Scripts:**
    *   Scripts for easy setup and execution of the system.

## Prerequisites

*   Python 3.8+ and pip
*   Node.js and npm
*   Google Cloud Platform Account
*   `openapi-generator-cli` (Install with `npm install @openapitools/openapi-generator-cli -g`)

## Google Cloud Setup

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (or select an existing one).
3.  Enable the **Google Forms API** and **Gmail API** for your project.
    *   Search for "Google Forms API" in the API Library and enable it.
    *   Search for "Gmail API" in the API Library and enable it.
4.  Create OAuth 2.0 Credentials:
    *   Navigate to "APIs & Services" -> "Credentials".
    *   Click "Create Credentials" -> "OAuth client ID".
    *   Select Application type: "Desktop app" (or "Web application" for more advanced setups).
    *   Give it a name (e.g., "Forms App Client").
    *   Click "Create".
    *   Download the JSON file. Rename it to `credentials.json`.
5.  **Place the `credentials.json` file into the `backend/` directory of this project.**


## Setup

1.  Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd google-forms-creator
    ```
2.  Run the setup script (for Linux/macOS):
    ```bash
    chmod +x scripts/setup.sh
    ./scripts/setup.sh
    ```
    This will:
    *   Set up a Python virtual environment for the backend and install dependencies.
    *   Install Node.js dependencies for the frontend.
    *   Remind you to place `credentials.json` in `backend/`.

## Running the System

1.  Run the execution script (for Linux/macOS):
    ```bash
    chmod +x scripts/run.sh
    ./scripts/run.sh
    ```
    This script will:
    *   Start the FastAPI backend (default: `http://localhost:8000`).
        *   **Important:** The first time the backend starts and tries to access Google APIs, it will print a URL to your console. Copy this URL into your browser, authenticate with your Google account, and grant the requested permissions. You'll be redirected to a localhost URL (or shown a code). The server will capture this and create a `token.json` in the `backend/` directory for future use.
    *   Start the ReactJS frontend development server (default: `http://localhost:3000`) and open it in your browser.

2.  Access the application:
    *   Frontend UI: `http://localhost:3000`
    *   Backend API Docs: `http://localhost:8000/docs`

## Development

### Backend (FastAPI)

*   Located in the `backend/` directory.
*   Activate virtual environment: `source backend/venv/bin/activate`
*   Run dev server: `cd backend && uvicorn app.main:app --reload`
*   Run tests: `cd backend && pytest`

### Frontend (ReactJS)

*   Located in the `frontend/` directory.
*   Run dev server: `cd frontend && npm start`

### Python SDK

1.  Ensure the FastAPI backend is running.
2.  Navigate to the project root.
3.  Generate the SDK:
    ```bash
    openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o sdk/google_form_sdk --package-name google_form_sdk
    ```
4.  An example usage script is `sdk_usage_example.py` in the project root. To run it:
    *   Install the SDK: `cd sdk && pip install ./google_form_sdk && cd ..`
    *   Ensure the backend is running.
    *   Run the script: `python sdk_usage_example.py`
