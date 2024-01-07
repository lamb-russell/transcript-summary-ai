import tiktoken
import re


def count_words(text_content):
    """
    Return the number of words in string
    """
    return len(text_content.split())

def chunk_text_by_tokens(text, max_tokens=2048, model_name="gpt-3.5-turbo"):
    """
    Chunks the given text into smaller parts based on token count.
    Tries to split at sentence boundaries.

    :param text: The text to be chunked
    :param max_tokens: The maximum token count for each chunk
    :param model_name: The name of the model for which the encoding is to be used
    :return: A list of text chunks
    """
    # Get the encoding for the specified model
    encoding = tiktoken.encoding_for_model(model_name)

    # Simple split of text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        sentence_token_count = len(encoding.encode(sentence))

        # If adding the next sentence doesn't exceed the max token count, add it
        if current_token_count + sentence_token_count <= max_tokens:
            current_chunk.append(sentence)
            current_token_count += sentence_token_count
        # Otherwise, store the current chunk and start a new one
        else:
            chunks.append(' '.join(current_chunk).strip())
            current_chunk = [sentence]
            current_token_count = sentence_token_count

    # Append any remaining text in the current chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk).strip())

    return chunks

def count_tokens(text_string, model_name="gpt-3.5-turbo"):
    """
    Counts the number of tokens in a string
    :param text_string: input string
    :param model_name: name of model for encoding
    :return: number of tokens
    """
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text_string))

if __name__ == '__main__':
    # read sample meeting transcript into string
    with open(f"./test_meeting_transcript.txt","r") as file:
        sample_text = file.read()

    # assume model is gpt 3.5
    model_name = "gpt-3.5-turbo"
    encoding = tiktoken.encoding_for_model(model_name)

    chunks = chunk_text_by_tokens(sample_text, max_tokens=200)
    for idx, chunk in enumerate(chunks):

        tokens_for_chunk = len(encoding.encode(chunk)) # get tokens in chunk
        print(f"Chunk {idx + 1}, length {len(chunk)}, tokens {tokens_for_chunk}:\n{chunk}\n{'-' * 20}")
