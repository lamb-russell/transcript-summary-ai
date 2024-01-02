"""
This test module contains unittests for the zoom_transcript_summarizer script. It tests various functionalities including
token counting, text chunking, reading and writing transcripts, and the summarization process.
"""

import unittest
from unittest.mock import Mock, mock_open, patch

from tokenizer import chunk_text_by_tokens, count_tokens


from zoom_transcript_summarizer import TranscriptHandler  # Assuming your script file is named "script_file.py"


class TestChunkTextByTokens(unittest.TestCase):
    """
    Test cases for checking the functionality of the chunk_text_by_tokens function.
    """
    def test_count_tokens(self):
        text = "ChatGPT-4, isn't it great? I've heard it can process 25+ languages!"

        self.assertEqual(22,count_tokens(text))

    def test_chunking(self):
        # Given test string
        text = ("In the realm of scientific exploration, the idea of cloning dinosaurs has always stirred "
                "a mix of awe and controversy. With advancements in biotechnology, the potential to extract "
                "and utilize ancient DNA from well-preserved amber fossils is becoming increasingly feasible. "
                "Scientists envision resurrecting these colossal creatures, offering humanity a chance to witness "
                "the Mesozoic era's majestic beasts firsthand."
                "\n\n"
                "However, this pursuit is riddled with ethical and ecological questions. Would a cloned dinosaur, "
                "born millions of years after its natural era, truly belong in our contemporary world? Modern "
                "ecosystems are vastly different, and these creatures might find no niche or face unforeseen health "
                "issues. There's also the moral quandary of creating life for mere spectacle. Would we be subjecting "
                "these animals to a life of confinement, far from the wild landscapes they were adapted to?"
                "\n\n"
                "While the dream of seeing a Tyrannosaurus rex or a Brachiosaurus up close is thrilling, the "
                "responsibility that comes with such power is immense. The technology is advancing, but the global "
                "community must weigh the profound consequences. As we stand on the brink of making science fiction "
                "a reality, intense debate ensures that we proceed with caution and respect for life.")

        #print(text)

        # Expected chunks based on the given max_tokens
        expected_chunks = [
            ("In the realm of scientific exploration, the idea of cloning dinosaurs has always stirred "
             "a mix of awe and controversy. With advancements in biotechnology, the potential to extract "
             "and utilize ancient DNA from well-preserved amber fossils is becoming increasingly feasible. "
             "Scientists envision resurrecting these colossal creatures, offering humanity a chance to witness "
             "the Mesozoic era's majestic beasts firsthand. However, this pursuit is riddled with ethical and "
             "ecological questions."),  #84 tokens
            ("Would a cloned dinosaur, born millions of years after its natural era, truly belong in our "
             "contemporary world? Modern ecosystems are vastly different, and these creatures might find no "
             "niche or face unforeseen health issues. There's also the moral quandary of creating life for mere "
             "spectacle. Would we be subjecting these animals to a life of confinement, far from the wild "
             "landscapes they were adapted to?"), #78 tokens
            ("While the dream of seeing a Tyrannosaurus rex or a Brachiosaurus up close is thrilling, the "
             "responsibility that comes with such power is immense. The technology is advancing, but the global "
             "community must weigh the profound consequences. As we stand on the brink of making science fiction "
             "a reality, intense debate ensures that we proceed with caution and respect for life.") #73 token
        ]

        # Call the function
        result_chunks = chunk_text_by_tokens(text, max_tokens=100, model_name="gpt-3.5-turbo")

        # print(result_chunks)
        # Assert that the result matches the expected chunks
        self.assertEqual(result_chunks, expected_chunks)


class TestTranscriptHandler(unittest.TestCase):
    """
    Test cases for checking the functionality of the TranscriptHandler class.
    """
    def setUp(self):
        self.handler = TranscriptHandler()

    def test_read_transcript(self):
        mock_file_content = "This is a test transcript."
        mo = mock_open(read_data=mock_file_content)
        with patch("builtins.open", mo):
            result = self.handler.read_transcript("test_transcript.txt")
        self.assertEqual(result, mock_file_content)

    def test_write_to_file(self):
        mock_summary = "This is a test summary."
        mock_filename = "test_summary.txt"
        mo = mock_open()
        with patch("builtins.open", mo):
            self.handler.write_to_file(mock_summary, mock_filename)
        mo.assert_called_once_with(mock_filename, "w")
        mo().write.assert_called_once_with(mock_summary)

    @patch("openai.ChatCompletion.create")
    def test_summarize_transcript(self, mock_create):
        mock_create.side_effect = [
            Mock(choices=[Mock(message={"content": "Summary 1"})]),
            Mock(choices=[Mock(message={"content": "Summary 2"})])
        ]
        mock_transcript = "Long transcript content..."
        result = self.handler.summarize_transcript(mock_transcript, "test_transcript.txt")
        expected_combined_summary = "Summary 1\nSummary 2"
        self.assertEqual(result, expected_combined_summary)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.expanduser", return_value="expanded_path")
    @patch("os.path.basename", return_value="test_transcript.txt")
    @patch("os.path.dirname", return_value="Meeting_Name")
    @patch("builtins.print")
    @patch("openai.ChatCompletion.create")
    def test_process_file(self, mock_create, mock_print, mock_dirname, mock_basename, mock_expanduser, mock_open):
        mock_create.side_effect = [
            Mock(choices=[Mock(message={"content": "Detailed Summary"})]),
            Mock(choices=[Mock(message={"content": "Executive Summary"})])
        ]
        mock_open.return_value.read.return_value = "Transcript content..."

        handler = TranscriptHandler()
        handler.process_file("test_transcript.txt")

        self.assertEqual(mock_create.call_count, 2)
        self.assertEqual(mock_print.call_count, 1)
        self.assertEqual(mock_dirname.call_count, 1)
        self.assertEqual(mock_basename.call_count, 1)
        self.assertEqual(mock_expanduser.call_count, 2)
        mock_open.assert_called_once_with("test_transcript.txt", "r")

    @patch("os.path.expanduser")
    @patch("os.path.dirname")
    @patch("watchdog.events.FileSystemEvent")
    def test_on_created_directory_event(self, mock_event, mock_dirname, mock_expanduser):
        mock_event.src_path = "test_directory"
        mock_dirname.return_value = "expanded_path"
        mock_expanduser.return_value = "expanded_path"
        self.handler.on_created(mock_event)
        self.assertEqual(mock_dirname.call_count, 1)
        self.assertEqual(mock_expanduser.call_count, 1)

    @patch("os.path.expanduser")
    @patch("builtins.print")
    @patch("os.path.basename")
    @patch("os.path.dirname")
    @patch("watchdog.events.FileSystemEvent")
    def test_on_created_file_event(self, mock_event, mock_dirname, mock_basename, mock_print, mock_expanduser):
        mock_event.src_path = "test_transcript.txt"
        mock_dirname.return_value = "expanded_path"
        mock_basename.return_value = "test_transcript.txt"
        mock_expanduser.return_value = "expanded_path"
        self.handler.on_created(mock_event)
        self.assertEqual(mock_print.call_count, 1)
        self.assertEqual(mock_dirname.call_count, 1)
        self.assertEqual(mock_basename.call_count, 1)
        self.assertEqual(mock_expanduser.call_count, 1)


if __name__ == "__main__":
    unittest.main()
