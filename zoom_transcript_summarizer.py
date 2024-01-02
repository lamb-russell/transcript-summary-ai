"""
This script monitors ZOOM_TRANSCRIPT_PATH for new zoom transcripts.  When a transcript is found, the text is
divided into chunks of length WORDS_PER_CHUNK or MAX_TOKENS and sent to Open AI for summarization.
Whether tokens or words are used to divide up the text is determined by SEPARATE_CHUNKS_BY_TOKENS.  The model used is
determined by MODEL_NAME. When summarizing, the prompt used for the chatbot's role is defined in
DETAILED_SUMMARY_ROLE.

After the transcript is summarized, another call to OpenAI is made to summarize the summaries into
an executive summary.  The prompt used is in EXECUTIVE_SUMMARY_ROLE.

Model used for summarizing determined by SUMMARY_MODEL_NAME.

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
from tokenizer import chunk_text_by_tokens, count_tokens

# USER CONFIGURATION
DETAILED_SUMMARY_ROLE = """You are a professional assistant that summarizes portions of Zoom transcripts as detailed 
        bullet points.  Your response will be combined with others to generate a summary of the full meeting, 
        so they should only contain bullet points and lots of detail.  
        Each bullet point should include all important details and be as accurate as possible.  
        Important details include financials, metrics, questions, responses, agreements, proposed actions, follow ups, 
        names, and dates.  Include names of those who spoke about a topic if possible.  
        Include as much context as needed in the bullet point to understand what's being discussed and
        actions required.  
        """
EXECUTIVE_SUMMARY_ROLE = """You are a professional assistant that creates executive summaries of meeting transcripts.  
        You will produce a concise executive summary in bullet points with all of the important information from the 
        call, such as names, actions, and dates. 
        Be as accurate as possible.
        Summary should contain the following:
        1. Participants - people who speak in the call
        2. Action items - names and responsibilities of people asked to do something during the call.  
        3. Key Takeaways - a few bullet points that convey the essence of the call. 
        """
WORDS_PER_CHUNK = 2000
MAX_TOKENS = 15000
SEPARATE_CHUNKS_BY_TOKENS= True # when True, separate text by token count
MODEL_NAME = "gpt-3.5-turbo-16k"   # options include: gpt-4, gpt-3.5-turbo, gpt-3.5-turbo-16k
SUMMARY_MODEL_NAME = "gpt-4"
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
    """

    def on_created(self, event):
        """
        Method called by watchdog when a file creation event is detected.
        Args:
            event: The file system event object containing information about the created file.
        """
        logging.info(f"File System Event Detected: {event}")

        if event.is_directory:
            logging.info("Directory event")
            directory_path = event.src_path

        else:
            transcript_file = event.src_path
            self.process_file(transcript_file)

    def process_file(self, transcript_file):
        """
        Processes the given transcript file by summarizing its content.
        Args:
            transcript_file: The path to the transcript file to be processed.
        """
        logging.info(f"New transcript found: {transcript_file}")
        transcript_content = self.read_transcript(transcript_file)
        full_summary = self.summarize_transcript(transcript_content, transcript_file)


    def summarize_transcript(self, transcript_content, transcript_file):
        """
        Summarizes the given transcript content.
        Args:
            transcript_content: The content of the transcript to summarize.
            transcript_file: The file path of the transcript for reference in the summary.
        Returns:
            str: The final executive summary of the transcript.
        """
        chunks = self.get_chunks(transcript_content) #separate text into chunks to accommodate model limits

        summaries = []
        role_chunk = DETAILED_SUMMARY_ROLE
        for chunk in chunks:  # turn each chunk into bullet points
            logging.info(f"sending chunk to summarize.  words: {len(chunk.split())}, tokens: {count_tokens(chunk)}")
            # Send chunk to OpenAI for summarization using the ChatCompletion endpoint and "gpt-3.5-turbo-16k" model
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": role_chunk},
                    {"role": "user", "content": chunk},
                ]
            )
            summary = response.choices[0].message['content'].strip()
            logging.info(f"summary word count: {len(summary.split())}, tokens: {count_tokens(summary)}")
            summaries.append(summary)

        combined_summaries = "\n".join(summaries)  # combine all bullet points for further summarization
        logging.info(f"all chunks summarized. word: {len(combined_summaries.split())}"
                     f", chars:{len(combined_summaries)}, tokens {count_tokens(combined_summaries)}")

        # create executive summary
        role_full = EXECUTIVE_SUMMARY_ROLE
        response = openai.ChatCompletion.create(
            model=SUMMARY_MODEL_NAME,  # this model is used for summarizing the bullet points
            messages=[
                {"role": "system", "content": role_full},
                {"role": "user", "content": combined_summaries},
            ]
        )
        full_summary = response.choices[0].message['content'].strip()  # get the summary from model
        logging.info(f"exec summary complete.  full length: {len(full_summary)}, "
                     f"word count: {len(full_summary.split())}, tokens {count_tokens(full_summary)}")

        # format summary
        formatted_date = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        summary_header = f"{formatted_date} - Summary of file: {transcript_file} \n"
        content = f"{summary_header}\nExecutive summary:\n {full_summary} \nDetailed Summary:\n {combined_summaries}\n"
        print(f"prepare to output content:\n{content}")

        # write to file
        last_directory = os.path.basename(
            os.path.dirname(transcript_file))  # last directory of file path is meeting name
        suffix=datetime.now().strftime('%Y%m%d%H%M%S')
        filename=f"{last_directory}_{suffix}" # append date generated to meeting name
        logging.info(f"filename: {filename}")
        save_to_path = os.path.expanduser(os.path.join(SAVE_TO_PATH, filename))
        logging.info(f"saving to path {save_to_path}")
        self.write_to_file(content, save_to_path)
        return full_summary

    def get_chunks(self, transcript_content):
        """
        Chunks the transcript content based on the specified mode (by tokens or words).
        Args:
            transcript_content: The content of the transcript to chunk.
        Returns:
            list: A list of text chunks.
        """
        if SEPARATE_CHUNKS_BY_TOKENS:
            logging.info(f"Separating text by token count, max tokens {MAX_TOKENS}, model {MODEL_NAME} ")
            return chunk_text_by_tokens(transcript_content, MAX_TOKENS, MODEL_NAME)  # use token count to chunk
        else:
            logging.info(f"Separating text by words, max words {WORDS_PER_CHUNK} ")
            return self.chunk_by_words(transcript_content)  # use words count to chunk


    def chunk_by_words(self, transcript_content):
        """
        Chunks the transcript content based on a word count threshold.
        Args:
            transcript_content: The content of the transcript to chunk.
        Returns:
            list: A list of text chunks.
        """
        # Split transcript into chunks based on word count
        words_per_chunk = WORDS_PER_CHUNK
        words = transcript_content.split()
        chunks = [" ".join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
        return chunks

    def read_transcript(self, transcript_file):
        """
        Reads the content of a transcript file.
        Args:
            transcript_file: The path to the transcript file to be read.
        Returns:
            str: The content of the transcript file.
        """
        # Read the transcript content
        with open(transcript_file, 'r') as f:
            transcript_content = f.read()
        return transcript_content

    # Function to write summary to a file
    def write_to_file(self, summary, filename):
        """
        Writes the summary to a file.
        Args:
            summary: The summary text to write.
            filename: The name of the file to write the summary to.
        """
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
