#!/bin/python3
import os
import sys
import tempfile
import pytest
from unittest.mock import mock_open, patch

sys.path.append('../')

import ttcg_constants

# Uncomment these as tests are finished.
from ttcg_tools import load_placeholder_values
from ttcg_tools import generate_combinations
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
from ttcg_tools import get_index_in_baseN
from ttcg_tools import sn_in_list
from ttcg_tools import save_sn_to_list


# Mock load_placeholder_values
def mock_load_placeholder_values(placeholder, placeholder_dir, visited):
    """
    Mock function to return placeholder values.
    """
    if placeholder == "rank":
        return ["1", "2", "3"]
    if placeholder == "color":
        return ["red", "blue"]
    return [f"<{placeholder}>"]  # Default for unknown placeholders

# Tests
def test_generate_combinations_no_placeholders():
    """
    Test a sentence with no placeholders.
    """
    result = generate_combinations("plain text")
    assert result == ["plain text"]


def test_generate_combinations_single_placeholder():
    """
    Test a sentence with one simple placeholder.
    """
    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values):
        result = generate_combinations("Rank <rank>")
        assert result == ["Rank 1", "Rank 2", "Rank 3"]


def test_generate_combinations_multiple_placeholders():
    """
    Test a sentence with multiple placeholders.
    """
    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values):
        result = generate_combinations("<rank> <color>")
        assert result == [
            "1 red", "1 blue",
            "2 red", "2 blue",
            "3 red", "3 blue"
        ]


def test_generate_combinations_with_offset():
    """
    Test a sentence with an offset placeholder.
    """
    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values):
        result = generate_combinations("Rank <rank+1>")
        assert result == ["Rank 2", "Rank 3", "Rank 4"]


def test_generate_combinations_negative_offset():
    """Test a sentence with a negative offset"""
    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values):
        result = generate_combinations("Rank <rank-1>")
        assert result == ["Rank 0", "Rank 1", "Rank 2"]


def test_generate_combinations_mixed_offsets():
    """Test a sentence with mixed offsets and plain placeholders"""
    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values):
        result = generate_combinations("<rank> to <rank+2>")
        assert result == [
            "1 to 3", "1 to 4", "1 to 5",
            "2 to 3", "2 to 4", "2 to 5",
            "3 to 3", "3 to 4", "3 to 5"
        ]


def test_generate_combinations_non_numeric_values():
    """
    Test handling of non-numeric placeholder values with offsets.
    """
    with patch("ttcg_tools.load_placeholder_values", return_value=["red", "blue"]):
        result = generate_combinations("Color <color+1>")
        assert result == ["Color red", "Color blue"]  # Offset ignored for non-numeric


def test_generate_combinations_custom_dir():
    """
    Test using a custom placeholder_dir.
    """
    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values) as mock_load:
        custom_dir = "custom/path/"
        result = generate_combinations("<rank>", placeholder_dir=custom_dir)
        mock_load.assert_called_with("rank", custom_dir, {"rank"})
        assert result == ["1", "2", "3"]


# TODO - This feature is currently un-used and actually needs fixed in generate_combinations...
#def test_generate_combinations_visited_cycle():
#    """
#    Test handling of a potential cycle with visited set.
#    """
#    with patch("ttcg_tools.load_placeholder_values", side_effect=mock_load_placeholder_values):
#        visited = {"rank"}
#        result = generate_combinations("<rank+1>", visited=visited)
#        assert result == ["<rank+1>"]  # Unresolved due to visited


def mock_generate_combinations(value, placeholder_dir, visited):
    """
    Mock function to simulate resolving nested placeholders.
    """
    if "<number>" in value:
        return [value.replace("<number>", str(i)) for i in range(1, 3)]  # e.g., ["1", "2"]
    return [value]

# Tests
def test_load_placeholder_values_file_not_found():
    """
    Test when the placeholder file doesn’t exist.
    """
    with patch("os.path.exists", return_value=False):
        result = load_placeholder_values("missing")
        assert result == ["<missing>"]


def test_load_placeholder_values_empty_file():
    """
    Test when the file exists but is empty.
    """
    mock_file_content = ""
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = load_placeholder_values("empty")
            assert result == ["<empty>"]


def test_load_placeholder_values_only_whitespace():
    """
    Test when the file contains only whitespace lines.
    """
    mock_file_content = "\n  \n\t\n"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = load_placeholder_values("whitespace")
            assert result == ["<whitespace>"]


def test_load_placeholder_values_simple_values():
    """
    Test loading simple values without nested placeholders.
    """
    mock_file_content = "value1\nvalue2\n_value3_\n"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = load_placeholder_values("simple")
            assert result == ["value1", "value2", "value3"]  # _ removed


def test_load_placeholder_values_nested_placeholders():
    """
    Test resolving nested placeholders with generate_combinations.
    """
    mock_file_content = "test<number>\nplain\n"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
                result = load_placeholder_values("nested")
                assert result == ["test1", "test2", "plain"]


def test_load_placeholder_values_recursion_cycle():
    """
    Test handling of a recursion cycle.
    """
    mock_file_content = "<nested>"  # Self-reference indirectly via visited
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("ttcg_tools.generate_combinations", side_effect=lambda v, d, vis: load_placeholder_values("nested", d, vis)):
                result = load_placeholder_values("nested")
                assert result == ["<nested>"]


def test_load_placeholder_values_custom_dir():
    """
    Test using a custom placeholder_dir.
    """
    mock_file_content = "custom_value\n"
    custom_dir = "custom/path/"
    with patch("os.path.exists", return_value=True) as mock_exists:
        with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
            result = load_placeholder_values("custom", placeholder_dir=custom_dir)
            mock_exists.assert_called_once_with(os.path.join(custom_dir, "custom.txt"))
            mock_file.assert_called_once_with(os.path.join(custom_dir, "custom.txt"), 'r')
            assert result == ["custom value"]


def test_load_placeholder_values_visited_state():
    """
    Test that visited set is properly managed (no side effects).
    """
    mock_file_content = "value1\n<other>\n"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            with patch("ttcg_tools.generate_combinations", return_value=["other_value"]):
                visited = set(["external"])
                result = load_placeholder_values("test", visited=visited)
                assert result == ["value1", "other_value"]
                assert visited == {"external"}  # Original set unchanged


# Mock CHARACTERS as a fixture to make tests flexible
@pytest.fixture
def mock_characters():
    # Example CHARACTERS for testing; can be any string
    return "0123456789ABCDEF"  # Base 16 for simplicity, but tests won't depend on this


def test_get_index_in_baseN_none_input(mock_characters):
    """
    Test that None input returns '0'.
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)  # Mock CHARACTERS
        result = get_index_in_baseN(None, ["a", "b", "c"], N=len(mock_characters))
        assert result == "0"


def test_get_index_in_baseN_empty_list(mock_characters):
    """
    Test that empty list returns '0'
    ."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        result = get_index_in_baseN("a", [], N=len(mock_characters))
        assert result == "0"


def test_get_index_in_baseN_not_found(mock_characters):
    """
    Test that string not in list returns '0'.
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        result = get_index_in_baseN("x", ["a", "b", "c"], N=len(mock_characters))
        assert result == "0"


def test_get_index_in_baseN_index_zero(mock_characters):
    """
    Test that index 0 returns '0' in any base.
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        result = get_index_in_baseN("a", ["a", "b", "c"], N=len(mock_characters))
        assert result == "0"


def test_get_index_in_baseN_base_conversion(mock_characters):
    """
    Test base-N conversion for various indices.
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        N = len(mock_characters)  # e.g., 16 for "0123456789ABCDEF"
        search_list = list("abcdefghijklmnop")  # 16 items
        
        # Index 1 should be CHARACTERS[1]
        assert get_index_in_baseN("b", search_list, N=N) == mock_characters[1]
        
        # Index 5 should be CHARACTERS[5]
        assert get_index_in_baseN("f", search_list, N=N) == mock_characters[5]
        
        # Index N (e.g., 16) should be "10" in base N
        if len(search_list) > N:
            assert get_index_in_baseN(search_list[N], search_list, N=N) == "10"


def test_get_index_in_baseN_small_base(mock_characters):
    """
    Test conversion with a smaller base.
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        search_list = ["a", "b", "c", "d"]
        # Use base 2
        result = get_index_in_baseN("c", search_list, N=2)
        assert result == "10"  # 2 in base 2
        result = get_index_in_baseN("d", search_list, N=2)
        assert result == "11"  # 3 in base 2


def test_get_index_in_baseN_large_index(mock_characters):
    """
    Test conversion of a larger index in base N.
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        N = len(mock_characters)
        search_list = [str(i) for i in range(N + 1)]  # 0 to N items
        # Index N in base N should be "10"
        result = get_index_in_baseN(str(N), search_list, N=N)
        assert result == "10"


def test_get_index_in_baseN_custom_n(mock_characters):
    """
    Test with N different from len(CHARACTERS).
    """
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("ttcg_constants.CHARACTERS", mock_characters)
        search_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
        # Use N=10, regardless of len(CHARACTERS)
        assert get_index_in_baseN("a", search_list, N=10) == "0"
        assert get_index_in_baseN("b", search_list, N=10) == "1"
        assert get_index_in_baseN("d", search_list, N=10) == "3"
        assert get_index_in_baseN("l", search_list, N=10) == "11"



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
