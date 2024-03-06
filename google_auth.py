from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json
import pickle

SCOPES = ['https://www.googleapis.com/auth/documents']


def get_google_credentials():
    creds = None

    # Load the OAuth2 credentials from a single environment variable
    creds_json_str = os.environ.get("GOOGLE_DOCS_SUMMARIZER_JSON")
    if not creds_json_str:
        raise ValueError("The GOOGLE_DOCS_SUMMARIZER_JSON environment variable is not set.")

    creds_info = json.loads(creds_json_str)

    # Check if a token.pickle file exists for storing access and refresh tokens
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        # Read the token from the file
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)

    # Refresh or obtain new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(creds_info, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)

    return creds
