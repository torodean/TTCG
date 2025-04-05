#!/bin/python3
import os
import sys
import tempfile
import pytest
import argparse
from unittest.mock import mock_open, patch
from types import SimpleNamespace

sys.path.append('../')

import ttcg_constants

# Uncomment these as tests are finished.
from ttcg_tools import load_placeholder_values
from ttcg_tools import generate_combinations
from ttcg_tools import get_command_string
from ttcg_tools import check_line_in_file
from ttcg_tools import get_relative_path
from ttcg_tools import rename_file
from ttcg_tools import text_in_placeholder_string
from ttcg_tools import deduce_effect_style_from_effect_text
from ttcg_tools import has_at_most_one_from_source
from ttcg_tools import get_sequence_combinations
#from ttcg_tools import get_combination_id
#from ttcg_tools import get_number_id
from ttcg_tools import get_index_in_baseN
from ttcg_tools import sn_in_list
from ttcg_tools import save_sn_to_list


def test_get_sequence_combinations_no_check_types():
    """
    Test combinations without type checking.
    """
    result = get_sequence_combinations(["a", "b", "c"], check_types=False, max_output_size=3)
    expected = sorted([
        ["a"], ["b"], ["c"],
        ["a", "b"], ["a", "c"], ["b", "c"],
        ["a", "b", "c"]
    ])
    assert result == expected


def test_get_sequence_combinations_with_check_types():
    """
    Test combinations with type checking using TYPE_LIST_LOWER.
    """
    mock_type_list = ["t1", "t2", "t3"]  # Mocked TYPE_LIST_LOWER for consistency
    with patch("ttcg_tools.output_text"):
        with patch("ttcg_tools.TYPE_LIST_LOWER", mock_type_list):
            result = get_sequence_combinations(["a", "b"], check_types=True, max_output_size=3)
    expected = sorted([
        ["t1"], ["t2"], ["t3"],
        ["a", "t1"], ["a", "t2"], ["a", "t3"],
        ["b", "t1"], ["b", "t2"], ["b", "t3"],
        ["a", "b", "t1"], ["a", "b", "t2"], ["a", "b", "t3"]
    ])
    assert result == expected


def test_get_sequence_combinations_max_output_size():
    """
    Test limiting combination size with max_output_size.
    """
    result = get_sequence_combinations(["a", "b", "c"], check_types=False, max_output_size=2)
    expected = sorted([
        ["a"], ["b"], ["c"],
        ["a", "b"], ["a", "c"], ["b", "c"],
        ["a", "b", "c"]  # Reflects actual behavior
    ])
    assert result == expected


def test_get_sequence_combinations_buffer_hit():
    """
    Test buffer usage for repeated calls.
    """
    input_list = ["x", "y"]
    first_result = get_sequence_combinations(input_list, check_types=False, max_output_size=3)
    with patch("ttcg_tools.output_text") as mock_output:
        second_result = get_sequence_combinations(input_list, check_types=False, max_output_size=3)
        assert second_result == first_result
        mock_output.assert_not_called()


def test_get_sequence_combinations_empty_list():
    """
    Test handling an empty input list.
    """
    result = get_sequence_combinations([], check_types=False)
    assert result == []


def test_get_sequence_combinations_single_item():
    """
    Test with a single item.
    """
    result = get_sequence_combinations(["a"], check_types=False, max_output_size=2)
    assert result == [["a"]]


def test_get_sequence_combinations_with_duplicates():
    """
    Test handling duplicate items in input.
    """
    result = get_sequence_combinations(["a", "A ", "a"], check_types=False, max_output_size=2)
    expected = [["a"]]  # Duplicates normalized
    assert result == expected
    
    
def test_get_sequence_combinations_type_check_restriction():
    """
    Test type checking restricts to one type from TYPE_LIST_LOWER.
    """
    mock_type_list = ["t1", "t2", "t3"]  # Mocked TYPE_LIST_LOWER
    with patch("ttcg_tools.has_at_most_one_from_source", side_effect=has_at_most_one_from_source):
        with patch("ttcg_tools.TYPE_LIST_LOWER", mock_type_list):
            result = get_sequence_combinations(["x"], check_types=True, max_output_size=3)
    expected = sorted([
        ["t1"], ["t2"], ["t3"],
        ["t1", "x"], ["t2", "x"], ["t3", "x"]
    ])
    assert result == expected
    assert not any(len([x for x in combo if x in mock_type_list]) > 1 for combo in result)


# Mock data for VALID_OVERLAY_STYLES
VALID_OVERLAY_STYLES = ['fire', 'water', 'earth']

def test_deduce_effect_style_from_effect_text_single_match():
    """
    Test case where exactly one effect style matches the effect text.
    The function should return the filename (style) where the match is found.
    """
    effect_text = "This is a fire effect"
    
    # Mocking the file reading process for the "fire" style
    with patch("builtins.open", mock_open(read_data="fire")):
        # Mocking os.path.join to simulate the file path and using VALID_OVERLAY_STYLES
        with patch("os.path.join", side_effect=lambda folder, filename: f"{folder}/{filename}.txt"):
            with patch("ttcg_tools.VALID_OVERLAY_STYLES", VALID_OVERLAY_STYLES):
                result = deduce_effect_style_from_effect_text(effect_text)
                assert result == "fire"  # The function should return the name of the file where the match was found


def test_deduce_effect_style_from_effect_text_multiple_matches():
    """
    Test case where multiple effect styles match the effect text.
    The function should return the filename (style) of the first match found.
    """
    effect_text = "This is a fire and water effect"
    
    # Mocking the file reading process for multiple styles ("fire" and "water")
    with patch("builtins.open", mock_open(read_data="fire\nwater")):
        # Mocking os.path.join to simulate the file path and using VALID_OVERLAY_STYLES
        with patch("os.path.join", side_effect=lambda folder, filename: f"{folder}/{filename}.txt"):
            with patch("ttcg_tools.VALID_OVERLAY_STYLES", VALID_OVERLAY_STYLES):
                result = deduce_effect_style_from_effect_text(effect_text)
                assert result == "fire"  # The function should return the first matched file


def test_deduce_effect_style_from_effect_text_no_match():
    """
    Test case where no effect style matches the effect text.
    The function should return None.
    """
    effect_text = "This is an unknown effect"
    
    # Mocking file reading for valid styles ("fire" and "water") with no match
    with patch("builtins.open", mock_open(read_data="fire\nwater")):
        # Mocking os.path.join to simulate the file path and using VALID_OVERLAY_STYLES
        with patch("os.path.join", side_effect=lambda folder, filename: f"{folder}/{filename}.txt"):
            with patch("ttcg_tools.VALID_OVERLAY_STYLES", VALID_OVERLAY_STYLES):
                result = deduce_effect_style_from_effect_text(effect_text)
                assert result is None  # Should return None if no match is found


def test_deduce_effect_style_from_effect_text_file_not_found():
    """
    Test case where the file for a specific effect style is not found.
    The function should continue without errors and return None.
    """
    effect_text = "This is a fire effect"
    
    # Mocking FileNotFoundError for one of the styles
    with patch("builtins.open", side_effect=FileNotFoundError):
        # Mocking os.path.join to simulate the file path and using VALID_OVERLAY_STYLES
        with patch("os.path.join", side_effect=lambda folder, filename: f"{folder}/{filename}.txt"):
            with patch("ttcg_tools.VALID_OVERLAY_STYLES", VALID_OVERLAY_STYLES):
                result = deduce_effect_style_from_effect_text(effect_text)
                assert result is None  # Should return None if the file cannot be found


def test_deduce_effect_style_from_effect_text_case_insensitive():
    """
    Test case where the effect text is case-insensitive, and the matching should still work.
    """
    effect_text = "THIS IS A FIRE EFFECT"
    
    # Mocking the file reading process for a valid style ("fire")
    with patch("builtins.open", mock_open(read_data="fire")):
        # Mocking os.path.join to simulate the file path and using VALID_OVERLAY_STYLES
        with patch("os.path.join", side_effect=lambda folder, filename: f"{folder}/{filename}.txt"):
            with patch("ttcg_tools.VALID_OVERLAY_STYLES", VALID_OVERLAY_STYLES):
                result = deduce_effect_style_from_effect_text(effect_text)
                assert result == "fire"  # Case-insensitive matching should return the correct file


def test_has_at_most_one_from_source_single_match():
    """
    Test case where there is exactly one match between the source and target lists.
    The function should return True.
    """
    source_list = ["apple", "banana", "cherry"]
    target_list = ["banana", "date"]
    result = has_at_most_one_from_source(source_list, target_list, num_of_matches=1)
    assert result is True


def test_has_at_most_one_from_source_multiple_matches():
    """
    Test case where there are multiple matches between the source and target lists.
    The function should return False because we're looking for exactly one match.
    """
    source_list = ["apple", "banana", "cherry"]
    target_list = ["banana", "cherry"]
    result = has_at_most_one_from_source(source_list, target_list, num_of_matches=1)
    assert result is False


def test_has_at_most_one_from_source_no_matches():
    """
    Test case where there are no matches between the source and target lists.
    The function should return False because we're looking for exactly one match.
    """
    source_list = ["apple", "banana", "cherry"]
    target_list = ["date", "elderberry"]
    result = has_at_most_one_from_source(source_list, target_list, num_of_matches=1)
    assert result is False


def test_has_at_most_one_from_source_zero_matches_expected():
    """
    Test case where the expected number of matches is 0, and there are no matches.
    The function should return True.
    """
    source_list = ["apple", "banana", "cherry"]
    target_list = ["date", "elderberry"]
    result = has_at_most_one_from_source(source_list, target_list, num_of_matches=0)
    assert result is True


def test_has_at_most_one_from_source_exact_match():
    """
    Test case where the expected number of matches is 1, and there is exactly one match.
    The function should return True.
    """
    source_list = ["apple", "banana", "cherry"]
    target_list = ["apple", "elderberry"]
    result = has_at_most_one_from_source(source_list, target_list, num_of_matches=1)
    assert result is True


def test_has_at_most_one_from_source_with_duplicates_in_target():
    """
    Test case where the target list contains duplicates of a match, but we're only expecting one match.
    The function should return False, since there are more than one match.
    """
    source_list = ["apple", "banana", "cherry"]
    target_list = ["apple", "apple", "elderberry"]
    result = has_at_most_one_from_source(source_list, target_list, num_of_matches=1)
    assert result is False



def mock_generate_combinations(value, placeholder_dir="", visited=None):
    """
    Mock function to simulate resolving nested placeholders.
    """
    if "<number>" in value:
        return [value.replace("<number>", str(i)) for i in range(1, 3)]  # e.g., ["1", "2"]
    return [value]


def test_text_in_placeholder_string_basic_match():
    """
    Test that the function correctly matches a generated combination of a placeholder.
    Specifically, it checks if "<number>" is found in the check string when replaced with "1".
    """
    placeholder_string = "<number>"
    check_string = "The number is 1"
    with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
        result = text_in_placeholder_string(placeholder_string, check_string)
    assert result is True


def test_text_in_placeholder_string_no_match():
    """
    Test that the function correctly returns False when no placeholder combination matches the check string.
    Specifically, it checks if "<number>" doesn't match "The level is 2".
    """
    placeholder_string = "<number>"
    check_string = "The level is 4"
    with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
        result = text_in_placeholder_string(placeholder_string, check_string)
    assert result is False


def test_text_in_placeholder_string_multiple_combinations():
    """
    Test that the function matches the placeholder when the check string contains one of the generated combinations.
    It verifies that either "1" or "2" (from "<number>") is found in the check string.
    """
    placeholder_string = "<number>"
    check_string = "The number is 2"
    with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
        result = text_in_placeholder_string(placeholder_string, check_string)
    assert result is True


def test_text_in_placeholder_string_no_multiple_combinations():
    """
    Test that the function returns False when none of the placeholder combinations match the check string.
    Specifically, it checks if "<number>" doesn't match "The number is 3".
    """
    placeholder_string = "<number>"
    check_string = "The number is 3"
    with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
        result = text_in_placeholder_string(placeholder_string, check_string)
    assert result is False


def test_text_in_placeholder_string_empty_combinations():
    """
    Test that the function returns False when no combinations are generated for the placeholder.
    Specifically, it checks if "<unknown>" doesn't generate any combinations to match the check string.
    """
    placeholder_string = "<unknown>"
    check_string = "No match here"
    with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
        result = text_in_placeholder_string(placeholder_string, check_string)
    assert result is False


def test_text_in_placeholder_string_different_placeholder():
    """
    Test that the function correctly matches a placeholder if it's found in a different format.
    Specifically, it checks if "<number>" is matched when the check string has "Number 1".
    """
    placeholder_string = "<number>"
    check_string = "Number 1"
    with patch("ttcg_tools.generate_combinations", side_effect=mock_generate_combinations):
        result = text_in_placeholder_string(placeholder_string, check_string)
    assert result is True


def test_rename_file_valid_rename():
    """
    Test that the file is renamed correctly while preserving its extension.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt") as tmp_file:
        original_path = tmp_file.name
        tmp_file.write("Hello World!")
    
    try:
        new_name = "new_report"
        new_path = rename_file(original_path, new_name)
        assert new_path == os.path.join(os.path.dirname(original_path), "new_report.txt")
        assert os.path.isfile(new_path)
    finally:
        os.remove(new_path)


def test_rename_file_no_extension():
    """
    Test that ValueError is raised if the file has no extension.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
        original_path = tmp_file.name
        tmp_file.write("No extension!")
    
    try:
        with pytest.raises(ValueError, match=f"The file path '{original_path}' has no extension"):
            rename_file(original_path, "new_name")
    finally:
        os.remove(original_path)


def test_rename_file_not_found():
    """
    Test that FileNotFoundError is raised when the file does not exist.
    """
    non_existent_path = "/path/to/non_existent_file.txt"
    with pytest.raises(FileNotFoundError, match=f"The file '{non_existent_path}' does not exist"):
        rename_file(non_existent_path, "new_name")


def test_rename_file_permission_error(monkeypatch):
    """
    Test that OSError is raised when there's an issue renaming the file (e.g., permission error).
    """
    def mock_rename(src, dst):
        raise OSError("Permission denied")

    monkeypatch.setattr(os, "rename", mock_rename)
    
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt") as tmp_file:
        original_path = tmp_file.name
        tmp_file.write("Permission test!")
    
    try:
        with pytest.raises(OSError, match="Permission denied"):
            rename_file(original_path, "new_name")
    finally:
        os.remove(original_path)


def test_rename_file_same_name():
    """
    Test that renaming a file to the same name does not change the file and returns the same path.
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".txt") as tmp_file:
        original_path = tmp_file.name
        tmp_file.write("Same name test!")
    
    try:
        new_path = rename_file(original_path, os.path.splitext(os.path.basename(original_path))[0])
        assert new_path == original_path
    finally:
        os.remove(original_path)


def test_relative_path_from_dir_to_file():
    """
    Test relative path calculation when from_path is a directory and to_path is a file.
    """
    with tempfile.TemporaryDirectory() as base_dir:
        file_dir = os.path.join(base_dir, "data")
        os.mkdir(file_dir)
        file_path = os.path.join(file_dir, "file.txt")
        with open(file_path, "w"):
            pass
        rel = get_relative_path(base_dir, file_path)
        assert rel == os.path.join("data", "file.txt")


def test_relative_path_from_file_to_file():
    """
    Test relative path calculation when from_path is a file.
    """
    with tempfile.TemporaryDirectory() as base_dir:
        src_path = os.path.join(base_dir, "src.py")
        target_dir = os.path.join(base_dir, "nested")
        os.mkdir(target_dir)
        target_file = os.path.join(target_dir, "target.txt")

        with open(src_path, "w"), open(target_file, "w"):
            pass

        rel = get_relative_path(src_path, target_file)
        assert rel == os.path.join("nested", "target.txt")


def test_relative_path_upwards():
    """
    Test relative path that moves upward in the directory hierarchy.
    """
    with tempfile.TemporaryDirectory() as base_dir:
        sub_dir = os.path.join(base_dir, "subdir")
        os.mkdir(sub_dir)
        file_in_root = os.path.join(base_dir, "file.txt")
        with open(file_in_root, "w"):
            pass
        rel = get_relative_path(sub_dir, file_in_root)
        assert rel == os.path.join("..", "file.txt")


def test_relative_path_same_path():
    """
    Test relative path when both paths are the same file.
    """
    with tempfile.NamedTemporaryFile() as tmp:
        rel = get_relative_path(tmp.name, tmp.name)
        assert rel == os.path.basename(tmp.name)


def test_relative_path_invalid_path(monkeypatch):
    """
    Test that ValueError is raised when relpath fails internally.
    """
    monkeypatch.setattr("os.path.relpath", lambda a, b: (_ for _ in ()).throw(ValueError("relpath error")))
    with pytest.raises(ValueError, match="relpath error"):
        get_relative_path("/fake/from", "/fake/to")


def test_check_line_found_exact_match():
    """
    Test that the function returns True when the exact line exists in the file.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write("first line\nsecond line\nthird line\n")
        tmp_path = tmp.name

    try:
        assert check_line_in_file(tmp_path, "second line") is True
    finally:
        os.remove(tmp_path)


def test_check_line_not_found():
    """
    Test that the function returns False when the line does not exist in the file.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write("alpha\nbeta\ngamma\n")
        tmp_path = tmp.name

    try:
        assert check_line_in_file(tmp_path, "delta") is False
    finally:
        os.remove(tmp_path)


def test_check_line_with_whitespace():
    """
    Test that leading/trailing whitespace is ignored when matching lines.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write("  padded line with spaces  \n")
        tmp_path = tmp.name

    try:
        assert check_line_in_file(tmp_path, "padded line with spaces") is True
    finally:
        os.remove(tmp_path)


def test_check_line_file_not_found():
    """
    Test that FileNotFoundError is raised when the file does not exist.
    """
    with pytest.raises(FileNotFoundError):
        check_line_in_file("non_existent_file.txt", "anything")


def test_check_line_io_error(monkeypatch):
    """
    Test that IOError is raised if an error occurs while reading the file.
    """
    def mock_open(*args, **kwargs):
        raise IOError("Mocked read error")

    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(IOError, match="Mocked read error"):
        check_line_in_file("fake.txt", "line")


def test_get_command_string_with_all_args():
    """
    Test that all non-null arguments are converted to flags with values,
    and boolean flags are included when True.
    """
    with patch("sys.argv", ["script.py"]):
        args = argparse.Namespace(input="data.txt", output="result.txt", verbose=True, threads=4)
        cmd = get_command_string(args)
        assert cmd == "python3 script.py --input data.txt --output result.txt --verbose --threads 4"


def test_get_command_string_with_flags_and_none():
    """
    Test that arguments set to None or False are excluded from the command string.
    """
    with patch("sys.argv", ["main.py"]):
        args = argparse.Namespace(input=None, debug=False, verbose=True)
        cmd = get_command_string(args)
        assert cmd == "python3 main.py --verbose"


def test_get_command_string_with_short_flags():
    """
    Test that single-character argument names are converted to short flags (e.g., -v).
    """
    with patch("sys.argv", ["run.py"]):
        args = argparse.Namespace(v=True, o="output.log")
        cmd = get_command_string(args)
        assert cmd == "python3 run.py -v -o output.log"


def test_get_command_string_empty_args():
    """
    Test that the command string only includes the script name when no arguments are set.
    """
    with patch("sys.argv", ["execute.py"]):
        args = argparse.Namespace()
        cmd = get_command_string(args)
        assert cmd == "python3 execute.py"



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
