import logging
import os
from anthropic import Anthropic
from tokenizer import count_tokens, count_words

# Configuration for detailed summary role
DETAILED_SUMMARY_ROLE = """You are a professional assistant tasked with summarizing Zoom meeting transcripts. 
    The summaries are intended for an executive, so they should be concise, clear, and cover key points discussed, 
    including decisions, action items, and key takeaways. Provide context and names of folks who are the subject
    of discussion.  If people have varying points of view please note that.  If there are timelines discussed, please 
    include dates and deliverables. """

def summarize_transcript_with_claude(transcript_content):
    """
    Summarizes the transcript content using Claude.

    Args:
        transcript_content (str): The content of the transcript to summarize.

    Returns:
        str: The comprehensive summary of the transcript.
    """
    logging.info("Summarizing transcript with Claude")

    # Retrieve Anthropic (Claude) API key from environment variable
    claude_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not claude_api_key:
        raise KeyError("Anthropic (Claude) API key not found in environment variable")

    # Initialize the Anthropic client with the API key
    client = Anthropic(api_key=claude_api_key)

    message = f"{DETAILED_SUMMARY_ROLE}\n{transcript_content}"

    # Create the summarization request
    # message = "how are you today?"
    response = client.messages.create(
        max_tokens=4096,
        #system={"content": DETAILED_SUMMARY_ROLE},  # Adjust based on the correct usage of 'system'
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        model="claude-2.1",  # Specify the correct model identifier (claude-instant-1.2, claude-2.1)
        # stream=True
    )

    #for attribute_name in dir(response.content[0].text):
    #    attribute_value = getattr(response.content[0].text, attribute_name, None)
    #    print(f"{attribute_name}:{attribute_value}")
    summary=response.content[0].text

    return summary

if __name__ == "__main__":
    # Example usage of the Claude summarizer
    with open("test_meeting_transcript.txt") as file:
        transcript_content=file.readlines()
    # transcript_content = "Your transcript content goes here."
    summary = summarize_transcript_with_claude(transcript_content)
    print("Claude Summary:", summary)
