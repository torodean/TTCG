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
from ttcg_tools import sn_in_list
from ttcg_tools import save_sn_to_list


def test_sn_in_list_serial_number_found():
    """
    Test that function returns True when serial number exists in file.
    """
    mock_file_content = "SN12345\nSN67890\nSNABCDE\n"
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        result = sn_in_list("SN67890", "test_file.txt")
        assert result == True

def test_sn_in_list_serial_number_not_found():
    """
    Test that function returns False when serial number is not in file.
    """
    mock_file_content = "SN12345\nSN67890\nSNABCDE\n"
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        result = sn_in_list("SN99999", "test_file.txt")
        assert result == False

def test_sn_in_list_empty_file():
    """
    Test behavior with an empty file.
    """
    mock_file_content = ""
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        result = sn_in_list("SN12345", "test_file.txt")
        assert result == False

def test_sn_in_list_file_not_found():
    """
    Test that function returns False when file doesn't exist.
    """
    with patch('builtins.open', side_effect=FileNotFoundError("No such file")):
        result = sn_in_list("SN12345", "test_file.txt")
        assert result == False

def test_sn_in_list_other_exception():
    """
    Test handling of other exceptions during file reading.
    """
    with patch('builtins.open', side_effect=PermissionError("Access denied")):
        result = sn_in_list("SN12345", "test_file.txt")
        assert result == False

def test_sn_in_list_whitespace_handling():
    """
    Test that whitespace in file and input is stripped when comparing.
    """
    mock_file_content = "  SN12345  \nSN67890\n  \nSNABCDE\n"
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        # Test with a serial number that has surrounding whitespace in file
        result = sn_in_list("SN12345", "test_file.txt")
        assert result == True
        
        # Test with input serial number that has whitespace
        result = sn_in_list("  SN67890  ", "test_file.txt")
        assert result == True

def test_sn_in_list_empty_serial_number():
    """
    Test that empty or whitespace-only serial number is rejected.
    """
    with patch('builtins.open', mock_open()) as mock_file:
        # Test empty string
        result = sn_in_list("", "test_file.txt")
        assert result == False
        mock_file.assert_not_called()
        
        # Test whitespace-only string
        result = sn_in_list("   ", "test_file.txt")
        assert result == False
        mock_file.assert_not_called()

def test_save_sn_to_list_successful_write():
    """
    Test that serial number is successfully appended to file.
    """
    with patch('builtins.open', mock_open()) as mock_file:
        result = save_sn_to_list("SN12345", "test_file.txt")
        assert result == True
        mock_file.assert_called_once_with("test_file.txt", 'a')
        mock_file().write.assert_called_once_with("SN12345\n")

def test_save_sn_to_list_empty_serial_number():
    """
    Test that empty or whitespace-only serial number is rejected.
    """
    with patch('builtins.open', mock_open()) as mock_file:
        # Test empty string
        result = save_sn_to_list("", "test_file.txt")
        assert result == False
        mock_file.assert_not_called()
        
        # Test whitespace-only string
        result = save_sn_to_list("   ", "test_file.txt")
        assert result == False
        mock_file.assert_not_called()

def test_save_sn_to_list_io_error():
    """
    Test handling of IOError during file operation.
    """
    with patch('builtins.open', side_effect=IOError("File system full")):
        result = save_sn_to_list("SN12345", "test_file.txt")
        assert result == False

def test_save_sn_to_list_special_characters():
    """
    Test that serial numbers with special characters are written correctly.
    """
    with patch('builtins.open', mock_open()) as mock_file:
        result = save_sn_to_list("SN#@$%^", "test_file.txt")
        assert result == True
        mock_file().write.assert_called_once_with("SN#@$%^\n")
