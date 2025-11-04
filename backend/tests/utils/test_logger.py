"""Tests for logger utility."""
import pytest
from unittest.mock import patch, call
from backend.src.utils.logger import info, warning, error, debug, logger


class TestLogger:
    """Test logger utility functions."""

    def test_info_logging(self):
        """Test info level logging."""
        with patch.object(logger, 'info') as mock_info:
            info("Test info message")
            mock_info.assert_called_once_with("Test info message")

    def test_warning_logging(self):
        """Test warning level logging."""
        with patch.object(logger, 'warning') as mock_warning:
            warning("Test warning message")
            mock_warning.assert_called_once_with("Test warning message")

    def test_error_logging(self):
        """Test error level logging."""
        with patch.object(logger, 'error') as mock_error:
            error("Test error message")
            mock_error.assert_called_once_with("Test error message")

    def test_debug_logging(self):
        """Test debug level logging."""
        with patch.object(logger, 'debug') as mock_debug:
            debug("Test debug message")
            mock_debug.assert_called_once_with("Test debug message")

    def test_multiple_log_calls(self):
        """Test multiple logging calls."""
        with patch.object(logger, 'info') as mock_info:
            info("First message")
            info("Second message")
            info("Third message")
            
            assert mock_info.call_count == 3
            mock_info.assert_has_calls([
                call("First message"),
                call("Second message"),
                call("Third message")
            ])

    def test_log_with_special_characters(self):
        """Test logging messages with special characters."""
        with patch.object(logger, 'info') as mock_info:
            message = "User: test@example.com | Status: 200 | Path: /api/preps"
            info(message)
            mock_info.assert_called_once_with(message)

    def test_log_with_empty_string(self):
        """Test logging empty string."""
        with patch.object(logger, 'info') as mock_info:
            info("")
            mock_info.assert_called_once_with("")