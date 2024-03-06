import logging
import os
from datetime import datetime

from tokenizer import count_tokens, count_words


def save_google_doc(service, summary, transcript_file):
    formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last_directory = os.path.basename(os.path.dirname(transcript_file))
    doc_title = f"{last_directory}_{formatted_date}"
    # Create a new Google Doc
    document = service.documents().create(body={'title': doc_title}).execute()
    doc_id = document.get('documentId')
    # Insert the summary text into the document
    requests = [
        {'insertText': {'location': {'index': 1}, 'text': summary}}
    ]
    service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    logging.info(f"Summary written to Google Docs: {doc_title}")


def format_and_save_summary(summary, transcript_file):
    """
    Formats the summary and saves it to a file.
    Args:
        summary: The summary text to be formatted and saved.
        transcript_file: The path to the original transcript file for reference.
    """
    logging.info(f"summary size {count_tokens(summary)} tokens, {count_words(summary)} words")
    formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last_directory = os.path.basename(
        os.path.dirname(transcript_file))  # last directory of file path is meeting name
    filename = f"{last_directory}_{formatted_date}.txt"
    save_to_path = os.path.join(os.path.expanduser(SAVE_TO_PATH), filename)
    with open(save_to_path, 'w') as file:
        file.write(summary)
    logging.info(f"Summary written to {save_to_path}")
    logging.info(summary)


SAVE_TO_PATH = "~/Documents/Zoom_Summaries"  # this is where summaries will be saved to local machine