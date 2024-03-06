"""
This script monitors ZOOM_TRANSCRIPT_PATH for new zoom transcripts.  When a transcript is found, the text is
divided into chunks of length MAX_TOKENS and sent to Open AI for summarization.
The model used is determined by MODEL_NAME. When summarizing, the prompt used for the chatbot's role is defined in
DETAILED_SUMMARY_ROLE.

The results of the summary are saved into a directory in SAVE_TO_PATH.

OPENAI_API_KEY environment variable should contain your API key.

In order to use this script, you should configure the constants in the USER CONFIGURATION section of the code
to match your environment

"""

import logging
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from save_summary import save_google_doc, format_and_save_summary
from summarize import summarize_transcript

from googleapiclient.discovery import build
import os
from google_auth import get_google_credentials

# USER CONFIGURATION
ZOOM_TRANSCRIPT_PATH = "~/Documents/Zoom"  # this is directory where Zoom saves meeting transcriptions

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class TranscriptHandler(FileSystemEventHandler):
    """
    A custom handler for file system events. It processes new files (Zoom transcripts) by creating summaries.
    The summaries are designed to be concise and clear, suitable for a senior executive audience,
    focusing on essential points, decisions, action items, and key takeaways.
    """

    def __init__(self):
        super().__init__()  # Initialize the superclass
        creds = get_google_credentials()  # Use the refactored function to get credentials
        self.service = build('docs', 'v1', credentials=creds)

    def on_created(self, event):
        """
        Method called by watchdog when a file creation event is detected.
        Args:
            event: The file system event object containing information about the created file.
        """
        logging.info(f"File System Event Detected: {event}")

        if not event.is_directory:
            transcript_file = event.src_path
            self.process_file(transcript_file)

    def process_file(self, transcript_file):
        """
        Processes the given transcript file by summarizing its content and then formatting and saving the summary.
        Args:
            transcript_file: The path to the transcript file to be processed.
        """
        logging.info(f"New transcript found: {transcript_file}")
        transcript_content = self.read_transcript(transcript_file)
        full_summary = summarize_transcript(transcript_content)
        format_and_save_summary(full_summary, transcript_file)
        self.format_and_save_to_google_docs(full_summary,transcript_file)

    def format_and_save_to_google_docs(self, summary, transcript_file):
        """Formats the summary and saves it to a Google Doc."""
        service = self.service
        if service:
            save_google_doc(service, summary, transcript_file)

    def read_transcript(self, transcript_file):
        """
        Reads the content of a transcript file.
        Args:
            transcript_file: The path to the transcript file to be read.
        Returns:
            str: The content of the transcript file.
        """
        with open(transcript_file, 'r') as file:
            return file.read()


if __name__ == "__main__":

    zoom_directory = os.path.expanduser("%s" % ZOOM_TRANSCRIPT_PATH)  # Replace with your actual Zoom directory path
    event_handler = TranscriptHandler()
    observer = Observer()
    observer.schedule(event_handler, path=zoom_directory, recursive=True)
    observer.start()

    try:
        print("Zoom transcript summarizer is running...")
        print(f"monitoring path {zoom_directory}")
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
