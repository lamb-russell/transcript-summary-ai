import logging

import openai

from tokenizer import count_tokens, count_words
import os

# Replace with your actual OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY", None)
if openai.api_key is None:
    raise KeyError("Open AI key not found in environment variable")


def summarize_transcript(transcript_content):
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


MODEL_NAME = "gpt-4-0125-preview"   # options include: gpt-4, gpt-3.5-turbo, gpt-3.5-turbo-16k
MAX_TOKENS = 125000  # model gpt-4-1106-preview has context window of 128k tokens
DETAILED_SUMMARY_ROLE = """You are a professional assistant tasked with summarizing Zoom meeting transcripts. 
    The summaries are intended for my boss, so they should be concise, clear, and cover only essential points discussed, 
    including decisions, action items, and key takeaways. Focus on providing a clear understanding of the meeting's 
    content and outcomes, as if explaining to a senior executive."""