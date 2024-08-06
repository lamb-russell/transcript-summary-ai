from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json
import pickle
import logging
from google.auth.exceptions import RefreshError

SCOPES = ['https://www.googleapis.com/auth/documents']

logger = logging.getLogger(__name__)
logging.basicConfig( level=logging.INFO)

def get_google_credentials():
    creds = None

    # Load the OAuth2 credentials from a single environment variable
    creds_json_str = os.environ.get("GOOGLE_DOCS_SUMMARIZER_JSON")
    if not creds_json_str:
        logger.error("Google Json not available.  Please set environment variable with authentication data.")
        raise ValueError("The GOOGLE_DOCS_SUMMARIZER_JSON environment variable is not set.")

    creds_info = json.loads(creds_json_str)

    # Check if a token.pickle file exists for storing access and refresh tokens
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        logger.info("pickle file token found")
        # Read the token from the file
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)

    # Refresh or obtain new credentials if needed
    if not creds or not creds.valid:
        logger.info("No valid credentials.  Refreshing token")
        if creds and creds.expired and creds.refresh_token:
            logger.info("previous token expired.  Refreshing")
            try:  # refresh token and check for error
                creds.refresh(Request())
            except RefreshError as e:
                logger.error(f"refresh error: {e}")
                creds=None  # remove the bad credentials if we can't refresh the token
                os.remove(token_path)  # clear the pickled token so it doesn't happen again

        if not creds or not creds.valid:  #get new token if we dont have valid credentials
            logger.info("get new token")
            flow = InstalledAppFlow.from_client_config(creds_info, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'wb') as token_file:
            logger.info(f"save pickled token {token_path}")
            pickle.dump(creds, token_file)

    return creds
