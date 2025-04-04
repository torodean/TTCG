#!/bin/python3
import os
import sys
import tempfile
import pytest
from unittest.mock import mock_open, patch

sys.path.append('../')

# Uncomment these as tests are finished.
#from ttcg_tools import load_placeholder_values
#from ttcg_tools import generate_combinations
#from ttcg_tools import get_command_string
#from ttcg_tools import check_line_in_file
#from ttcg_tools import get_relative_path
#from ttcg_tools import rename_file
#from ttcg_tools import text_in_placeholder_string
#from ttcg_tools import deduce_effect_style_from_effect_text
#from ttcg_tools import has_at_most_one_from_source
#from ttcg_tools import get_sequence_combinations
#from ttcg_tools import get_combination_id
#from ttcg_tools import get_number_id
#from ttcg_tools import get_index_in_baseN
#from ttcg_tools import sn_in_list
from ttcg_tools import save_sn_to_list


def test_save_sn_to_list_successful_write():
    """
    Test that serial number is successfully appended to file.
    """
    mock_file_content = ""
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
        result = save_sn_to_list("SN12345", "test_file.txt")
        
        # Check return value
        assert result == True
        
        # Check that file was opened in append mode
        mock_file.assert_called_once_with("test_file.txt", 'a')
        
        # Check that write was called with serial number and newline
        mock_file().write.assert_called_once_with("SN12345\n")

def test_save_sn_to_list_empty_serial_number():
    """
    Test that empty or whitespace-only serial number is rejected.
    """
    with patch('builtins.open', mock_open()) as mock_file:
        with patch('__main__.output_text') as mock_output:  # Adjust path as needed
            # Test empty string
            result = save_sn_to_list("", "test_file.txt")
            assert result == False  # Implicit return False when condition fails
            mock_output.assert_called_once()
            mock_file.assert_not_called()  # File shouldn't be opened
            
            # Reset mocks
            mock_output.reset_mock()
            mock_file.reset_mock()
            
            # Test whitespace-only string
            result = save_sn_to_list("   ", "test_file.txt")
            assert result == False
            mock_output.assert_called_once()        
            mock_file.assert_not_called()

def test_save_sn_to_list_io_error():
    """
    Test handling of IOError during file operation.
    """
    with patch('builtins.open', side_effect=IOError("File system full")) as mock_open_file:
        with patch('__main__.output_text') as mock_output:
            result = save_sn_to_list("SN12345", "test_file.txt")
            
            assert result == False
            mock_output.assert_called_once()

def test_save_sn_to_list_special_characters():
    """
    Test that serial numbers with special characters are written correctly.
    """
    with patch('builtins.open', mock_open()) as mock_file:
        result = save_sn_to_list("SN#@$%^", "test_file.txt")
        
        assert result == True
        mock_file().write.assert_called_once_with("SN#@$%^\n")
