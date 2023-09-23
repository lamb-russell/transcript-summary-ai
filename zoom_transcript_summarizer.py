"""
This script monitors ZOOM_TRANSCRIPT_PATH for new zoom transcripts.  When a transcript is found, the text is
divided into chunks of length WORDS_PER_CHUNK and sent to Open AI for summarization.  The model used is
determined by MODEL_NAME. When summarizing, the prompt used for the chatbot's role is defined in
DETAILED_SUMMARY_ROLE.

After the transcript is summarized, another call to OpenAI is made to summarize the summaries into
an executive summary.  The prompt used is in EXECUTIVE_SUMMARY_ROLE.

The results of the combined summaries are saved into a directory in SAVE_TO_PATH.

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

# USER CONFIGURATION
DETAILED_SUMMARY_ROLE = """You are a professional assistant that summarizes portions of Zoom transcripts as detailed 
        bullet points.  Your response will be combined with others to generate a summary of the full meeting, 
        so they should only contain the relevant bullet points, including names of people,
        and should be as accurate as possible."""
EXECUTIVE_SUMMARY_ROLE = """You are a professional assistant that creates executive summaries of meeting transcripts.  
        You will produce a concise executive summary in bullet points with only the most important information. 
        Be as accurate as possible.
        Summary should contain the following:
        1. Participants - people who speak in the call
        2. Action items - names and responsibilities of people asked to do something during the call.  
        3. Key Takeaways - a few bullet points that convey the essence of the call. 
        """
WORDS_PER_CHUNK = 2000
MODEL_NAME = "gpt-3.5-turbo"
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
    This event handler watches for file system events sent via the watchdog library.
    Whenever a file or directory is created in the watched folder, it will process the file (or files contained
    in the directory) by chunking it into fragments, summarizing each fragment, then combining into a full
    summary.
    """

    def on_created(self, event):
        logging.info(f"File System Event Detected: {event}")

        if event.is_directory:
            logging.info("Directory event")
            directory_path = event.src_path

        else:
            transcript_file = event.src_path
            self.process_file(transcript_file)

    def process_file(self, transcript_file):
        logging.info(f"New transcript found: {transcript_file}")
        transcript_content = self.read_transcript(transcript_file)
        full_summary = self.summarize_transcript(transcript_content, transcript_file)

    def summarize_transcript(self, transcript_content, transcript_file):
        # Split transcript into chunks based on word count
        words_per_chunk = WORDS_PER_CHUNK
        words = transcript_content.split()
        chunks = [" ".join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]

        summaries = []
        role_chunk = DETAILED_SUMMARY_ROLE
        for chunk in chunks:
            logging.info(f"sending chunk to summarize.  word count: {len(chunk.split())}")
            # Send chunk to OpenAI for summarization using the ChatCompletion endpoint and "gpt-3.5-turbo-16k" model
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": role_chunk},
                    {"role": "user", "content": chunk},
                ]
            )
            summary = response.choices[0].message['content'].strip()
            logging.info(f"summary word count: {len(summary.split())}")
            summaries.append(summary)

        combined_summaries = "\n".join(summaries)
        logging.info(f"all chunks summarized. word count: {len(combined_summaries.split())}"
                     f", char length:{len(combined_summaries)}")

        # create executive summary
        role_full = EXECUTIVE_SUMMARY_ROLE
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": role_full},
                {"role": "user", "content": combined_summaries},
            ]
        )
        full_summary = response.choices[0].message['content'].strip()
        logging.info(f"exec summary complete.  full length: {len(full_summary)}, "
                     f"word count: {len(full_summary.split())}")

        # format summary
        formatted_date = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        summary_header = f"{formatted_date} - Summary of file: {transcript_file} \n"
        content = f"{summary_header}\nExecutive summary:\n {full_summary} \nDetailed Summary:\n {combined_summaries}\n"
        print(f"prepare to output content:\n{content}")

        # write to file
        last_directory = os.path.basename(
            os.path.dirname(transcript_file))  # last directory of file path is meeting name
        save_to_path = os.path.expanduser(os.path.join(SAVE_TO_PATH, last_directory))
        logging.info(f"saving to path {save_to_path}")
        self.write_to_file(content, save_to_path)
        return full_summary

    def read_transcript(self, transcript_file):
        # Read the transcript content
        with open(transcript_file, 'r') as f:
            transcript_content = f.read()
        return transcript_content

    # Function to write summary to a file
    def write_to_file(self, summary, filename):
        with open(filename, 'w') as f:
            f.write(summary)
        print(f"Summary written to {filename}")


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
