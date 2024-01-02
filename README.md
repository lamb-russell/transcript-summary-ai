
# Zoom Transcript Summarizer

The Zoom Transcript Summarizer is a Python application designed to automatically monitor a specified directory for new Zoom meeting transcripts and summarize them. It utilizes the OpenAI GPT models to create detailed and executive summaries of the meeting transcripts.

## Features

- **Transcript Monitoring**: Watches a specified directory for new transcript files.
- **Automatic Summarization**: Splits transcripts into smaller chunks and summarizes them using OpenAI's GPT models.
- **Dual Summaries**: Generates both a detailed summary (with bullet points) and an executive summary.
- **Local Saving**: Summaries are saved to a specified local directory.

## Components

1. **zoom_summarizer.py**: The main script that monitors for new transcripts and processes them.
2. **tokenizer.py**: A utility module for text chunking based on token count, crucial for handling large transcripts.
3. **test.py**: Contains unit tests to ensure the reliability of the summarizer and tokenizer functionalities.

## tokenizer.py

The `tokenizer.py` module provides functions for dividing text into manageable chunks based on token counts, which is essential for processing large texts with token-limited models.

### Functions

- `chunk_text_by_tokens(text, max_tokens, model_name)`: Splits the text into chunks without exceeding the specified maximum token count, ideally at sentence boundaries.
- `count_tokens(text_string, model_name)`: Counts the number of tokens in a given string based on the specified model's encoding.

## Installation

1. Clone the repository.
2. Ensure Python 3.x is installed.
3. Install dependencies: `pip install -r requirements.txt` (Note: requirements.txt should list necessary libraries like `watchdog`, `openai`, and `tiktoken`).

## Configuration

Set the following parameters in `zoom_summarizer.py`:

- `DETAILED_SUMMARY_ROLE` and `EXECUTIVE_SUMMARY_ROLE`: Define the prompts for detailed and executive summaries.
- `WORDS_PER_CHUNK`, `MAX_TOKENS`, `MODEL_NAME`, `SUMMARY_MODEL_NAME`: Set token limits and model names.
- `SAVE_TO_PATH`, `ZOOM_TRANSCRIPT_PATH`: Specify paths for saving summaries and locating Zoom transcripts.

## Usage

1. Run `python zoom_summarizer.py` to start the summarizer.
2. The script will monitor the specified Zoom transcript directory and process new files as they appear.

## Testing

Run `python -m unittest test.py` to execute the test suite and verify the functionality.

---

*Note*: Ensure that the OpenAI API key is correctly set in the environment variables for the script to function properly.
