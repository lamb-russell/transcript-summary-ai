import unittest
from unittest.mock import Mock, mock_open, patch
from datetime import datetime
import os
import openai
from zoom_transcript_summarizer import TranscriptHandler  # Assuming your script file is named "script_file.py"

class TestTranscriptHandler(unittest.TestCase):

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
