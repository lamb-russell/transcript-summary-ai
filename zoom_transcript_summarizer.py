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
import os
import time
from datetime import datetime

import openai
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from tokenizer import chunk_text_by_tokens, count_tokens, count_words

# USER CONFIGURATION
DETAILED_SUMMARY_ROLE = """You are a professional assistant tasked with summarizing Zoom meeting transcripts. 
    The summaries are intended for my boss, so they should be concise, clear, and cover all essential points discussed, 
    including decisions, action items, and key takeaways. Focus on providing a clear understanding of the meeting's 
    content and outcomes, as if explaining to a senior executive."""
MAX_TOKENS = 125000  # model gpt-4-1106-preview has context window of 128k tokens
MODEL_NAME = "gpt-4-1106-preview"   # options include: gpt-4, gpt-3.5-turbo, gpt-3.5-turbo-16k
SAVE_TO_PATH = "~/Documents/Zoom_Summaries"  # this is where summaries will be saved to local machine
ZOOM_TRANSCRIPT_PATH = "~/Documents/Zoom"  # this is directory where Zoom saves meeting transcriptions

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Replace with your actual OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY", None)
if openai.api_key is None:
    raise KeyError("Open AI key not found in environment variable")

class TranscriptHandler(FileSystemEventHandler):
    """
    A custom handler for file system events. It processes new files (Zoom transcripts) by creating summaries.
    The summaries are designed to be concise and clear, suitable for a senior executive audience,
    focusing on essential points, decisions, action items, and key takeaways.
    """

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
        full_summary = self.summarize_transcript(transcript_content)
        self.format_and_save_summary(full_summary, transcript_file)

    def summarize_transcript(self, transcript_content):
        """
        Generates a summary of the transcript content.
        Args:
            transcript_content: The content of the transcript to summarize.
        Returns:
            str: The comprehensive summary of the transcript.
        """
        logging.info("Summarizing transcript")
        role_chunk = DETAILED_SUMMARY_ROLE
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": role_chunk},
                {"role": "user", "content": transcript_content},
            ]
        )
        logging.info(f"transcript {count_tokens(transcript_content) } tokens, {count_words(transcript_content)} words")
        return response.choices[0].message['content'].strip()

    def format_and_save_summary(self, summary, transcript_file):
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
