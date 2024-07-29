import subprocess
import unittest
from unittest.mock import MagicMock, patch

from src.common.ffmpeg_handler import FFmpegHandler


class TestFFmpegHandler(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_successful_command_execution_emits_finish_signal(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('output', '')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        handler = FFmpegHandler()
        handler._signal_bus.set_detail_progress_finish.emit = MagicMock()

        handler.run_command('ffmpeg -i input.mp4 output.mp3')

        handler._signal_bus.set_detail_progress_finish.emit.assert_called_once()

    @patch('subprocess.Popen')
    def test_command_execution_with_non_zero_exit_code_raises_exception(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        handler = FFmpegHandler()

        with self.assertRaises(subprocess.CalledProcessError):
            handler.run_command('ffmpeg -i input.mp4 output.mp3')

    @patch('subprocess.Popen')
    def test_empty_command_raises_value_error(self, mock_popen):
        handler = FFmpegHandler()

        with self.assertRaises(ValueError):
            handler.run_command('')

    @patch('subprocess.Popen')
    def test_progress_tracking_updates_progress_correctly(self, mock_popen):
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ['frame= 10\n', 'frame= 20\n', '']
        mock_process.communicate.return_value = ('', '')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        handler = FFmpegHandler()
        handler._signal_bus.set_detail_progress_current.emit = MagicMock()

        handler.run_command('ffmpeg -i input.mp4 output.mp3', progress_total=20)

        handler._signal_bus.set_detail_progress_current.emit.assert_any_call(10)
        handler._signal_bus.set_detail_progress_current.emit.assert_any_call(20)

    @patch('subprocess.Popen')
    def test_command_execution_with_stderr_logs_critical_and_emits_failed_signal(self, mock_popen):
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error')
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        handler = FFmpegHandler()
        handler._signal_bus.failed.emit = MagicMock()

        try:
            handler.run_command('ffmpeg -i input.mp4 output.mp3')
        except subprocess.CalledProcessError:
            pass

        handler._signal_bus.failed.emit.assert_called_once()
