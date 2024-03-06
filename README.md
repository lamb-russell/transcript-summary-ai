# Zoom Transcript Summarizer

The Zoom Transcript Summarizer is a Python-based tool designed to automatically process and summarize Zoom meeting transcripts. It monitors a designated directory for new transcript files, summarizes the content using OpenAI's GPT models, and saves the summaries both locally and on Google Docs for easy access and sharing.

## Features

- **Automatic Monitoring**: Watches for new transcript files in a specified directory.
- **Summarization with AI**: Utilizes OpenAI GPT models for intelligent content summarization.
- **Integration with Google Docs**: Automatically saves summaries to Google Docs.
- **Local Backup**: Provides local saving of summaries for offline access.

## Getting Started

### Prerequisites

Ensure Python 3.x is installed on your system and you have a Google Cloud account ready for setup.

### Installation and Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/zoom-transcript-summarizer.git
   cd zoom-transcript-summarizer
   ```

2. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud Project**

   - Create a new project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the Google Docs API and Google Drive API from the Library section.
   - Set up the OAuth consent screen and add your Google user email as a test user.
   - Create OAuth 2.0 Client IDs in the Credentials section and download the JSON file.

4. **Set Environment Variables**

   Set `GOOGLE_DOCS_SUMMARIZER_JSON` with the contents of the downloaded JSON file:

   ```sh
   export GOOGLE_DOCS_SUMMARIZER_JSON='<JSON_CONTENTS>'
   ```

   Set your OpenAI API key:

   ```sh
   export OPENAI_API_KEY='your_openai_api_key_here'
   ```

### Running the Application

1. Update `ZOOM_TRANSCRIPT_PATH` in `zoom_transcript_summarizer.py` to your Zoom transcripts directory.
2. Run the summarizer:

   ```sh
   python zoom_transcript_summarizer.py
   ```

## User Guide

- **Local Summaries**: Find the summaries saved locally in the path specified by `SAVE_TO_PATH`.
- **Google Docs Summaries**: Access the summaries saved in Google Docs titled with the format `MeetingName_YYYY-MM-DD HH:MM:SS`.

## Development

This project consists of several modules working together to monitor, process, and summarize Zoom transcripts. Key components include:

- `zoom_transcript_summarizer.py`: The main script that initiates monitoring and summarization.
- `tokenizer.py`: Utility for text tokenization.
- `summarize.py`: Handles the summarization logic.
- `save_summary.py`: Responsible for saving summaries locally and to Google Docs.
- `google_auth.py`: Manages Google API authentication.
- `tests.py`: Contains unit tests to ensure functionality.

## Testing

To run unit tests and verify component functionality:

```sh
python -m unittest tests.py
```

## Important Note

This tool is designed for educational and professional use. Always adhere to OpenAI's usage policies and Google's API terms of service. Ensure the proper handling of sensitive and private meeting content.

## For New Users

To use this application with your own Google credentials:

- Follow the setup instructions to create a Google Cloud Project and enable necessary APIs.
- Obtain OAuth 2.0 credentials and configure the required environment variables.
- Run the application as instructed, ensuring your Zoom transcripts directory is correctly set.

**Note**: In test mode, application usage is limited to users specified as test users in your Google Cloud project. Consider moving to production mode for broader use, following Google's verification processes.