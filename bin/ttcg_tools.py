import os
import sys
import re
import itertools
from tqdm import tqdm

# Import some constants from the ttxg_constants file.
from ttcg_constants import VALID_OVERLAY_STYLES
from ttcg_constants import DEFAULT_PLACEHOLDERS_FOLDER
from ttcg_constants import EFFECT_STYLE_TEXT_FOLDER
from ttcg_constants import TYPE_LIST_LOWER
from ttcg_constants import CHARACTERS


# Global variables used by these methods.
ALL_SEQUENCE_BUFFER = {}
PRINT_ALL_SEQUENCES = False


def output_text(text, option="text"):
    """
    Print text to the console in a specified color using ANSI escape codes.

    Args:
        text (str): The text to be printed.
        option (str, optional): The color option for the text. Valid options are "text" (default, no color), 
            "warning" (yellow), "error" (red), "note" (blue), "success" (green), "command" (cyan), 
            "test" (magenta), and "program" (orange). Defaults to "text". Invalid options result in uncolored text.

    Returns:
        None

    Note:
        This function uses ANSI escape codes for color formatting. Colors may not display correctly 
        in all environments (e.g., some IDEs or Windows terminals without ANSI support).
    """
    color_codes = {
        "text": "\033[0m",      # Reset color
        "warning": "\033[93m",  # Yellow - Warning text
        "error": "\033[91m",    # Red - Error text
        "note": "\033[94m",     # Blue - Notes or program information
        "success": "\033[92m",  # Green - Success text
        "command": "\033[36m",  # Cyan - Command output text
        "test": "\033[35m",     # Magenta - Testing
        "program": "\033[38;5;208m"  # Orange - Program-specific output
    }
    
    text = str(text)  # Ensure text is a string
    
    if option == "error":
        if "error" not in text.lower():
            text = f"ERROR: {text}"
    elif option == "warning":
        if "error" not in text.lower():
            text = f"WARNING: {text}"
    
    if option in color_codes:
        color_code = color_codes[option]
        reset_code = color_codes["text"]
        print(f"{color_code}{text}{reset_code}")
    else:
        print(text)


def load_placeholder_values(placeholder, placeholder_dir=DEFAULT_PLACEHOLDERS_FOLDER, visited=None):
    """
    Loads and resolves values for a placeholder from a text file, handling nested placeholders recursively.

    This function reads a file named `<placeholder>.txt` from the specified directory, processes its lines into a list of
    values, and recursively resolves any nested placeholders (e.g., `<other>` within a value). It prevents infinite
    recursion by tracking visited placeholders and returning the unresolved placeholder (e.g., `<placeholder>`) if a
    cycle is detected or if the file is missing/empty.

    Args:
        placeholder (str): Name of the placeholder to load values for (e.g., 'number'), without angle brackets.
        placeholder_dir (str): Directory path containing placeholder text files (e.g., 'placeholders/').
        visited (set, optional): Set of placeholders already processed in the recursion stack to detect cycles.
                                 Defaults to None, initializing an empty set if not provided.

    Returns:
        list: A list of resolved string values for the placeholder. If the file doesn’t exist, is empty, or a cycle is
              detected, returns a single-element list containing the unresolved placeholder (e.g., ['<placeholder>']).
    """
    if visited is None:
        visited = set()
    
    if placeholder in visited:
        return [f"<{placeholder}>"]
    
    visited.add(placeholder)
    
    file_path = os.path.join(placeholder_dir, f"{placeholder}.txt")
    if not os.path.exists(file_path):
        visited.remove(placeholder)
        return [f"<{placeholder}>"]
    
    raw_values = []
    with open(file_path, 'r') as f:
        raw_values = [line.replace('_', ' ').strip() for line in f if line.strip()]
    
    if not raw_values:
        visited.remove(placeholder)
        return [f"<{placeholder}>"]
    
    resolved_values = []
    for value in raw_values:
        if re.search(r"<[^>]+>", value):
            sub_combinations = generate_combinations(value, placeholder_dir, visited.copy())
            resolved_values.extend(sub_combinations)
        else:
            resolved_values.append(value)
    
    visited.remove(placeholder)
    return resolved_values


def generate_combinations(sentence, placeholder_dir=DEFAULT_PLACEHOLDERS_FOLDER, visited=None):
    """
    Generate all possible combinations by replacing placeholders in the sentence with their corresponding values,
    handling nested placeholders and offsets (e.g., <rank+1>, <rank-1>) recursively.

    Args:
        sentence (str): Sentence containing placeholders enclosed in <> (e.g., "<rank>", "<rank+1>", "<rank-1>").
        placeholder_dir (str): Directory containing placeholder text files.
        visited (set, optional): Set of placeholders already processed to prevent infinite recursion.

    Returns:
        list: List of all possible sentence combinations with no placeholders remaining.
    """
    if visited is None:
        visited = set()
    
    # Extract all placeholders, including those with offsets (e.g., "rank", "rank+1", "rank-1")
    placeholders = re.findall(r"<([^>]+)>", sentence)
    if not placeholders:  # Base case: no placeholders left
        return [sentence]
    
    # Split placeholders into base and offset parts
    placeholder_values = {}
    base_to_offsets = {}  # Track offsets for each base (e.g., "rank": ["+1", "-1"])
    
    for placeholder in placeholders:
        # Check for offset (e.g., "rank+1" or "rank-1")
        offset_match = re.match(r"(\w+)(?:([+-])(\d+))?", placeholder)
        if not offset_match:
            continue  # Skip malformed placeholders
        
        base, sign, offset = offset_match.groups()  # e.g., ("rank", "+", "1") or ("rank", None, None)
        if sign is None:  # No offset (plain "<rank>")
            offset_value = 0
        else:
            offset_value = int(offset) if sign == "+" else -int(offset)  # Positive or negative
        
        if base not in placeholder_values:
            # Load values for the base placeholder (e.g., "rank")
            placeholder_values[base] = load_placeholder_values(base, placeholder_dir, visited)
            base_to_offsets[base] = set()
        
        # Track this offset for the base
        base_to_offsets[base].add(offset_value)
    
    # Generate values for all placeholders, including offsets
    all_placeholder_values = {}
    for base, offsets in base_to_offsets.items():
        base_values = placeholder_values[base]
        for offset in offsets:
            # Create a new placeholder key like "rank+1" or "rank-1"
            if offset == 0:
                offset_key = base
            elif offset > 0:
                offset_key = f"{base}+{offset}"
            else:
                offset_key = f"{base}{offset}"  # e.g., "rank-1"
            # Compute offset values (assuming base values are numeric)
            all_placeholder_values[offset_key] = []
            for value in base_values:
                try:
                    num_value = int(value)  # Convert to int
                    all_placeholder_values[offset_key].append(str(num_value + offset))
                except ValueError:
                    # If not numeric, keep as-is
                    all_placeholder_values[offset_key].append(value)
    
    # Generate combinations
    combinations = []
    all_values = [all_placeholder_values[p] if p in all_placeholder_values else placeholder_values[p] 
                  for p in placeholders]
    for combo in itertools.product(*all_values):
        result = sentence
        for placeholder, value in zip(placeholders, combo):
            result = result.replace(f"<{placeholder}>", value)
        combinations.append(result)
    
    return combinations


def get_command_string(args):
    """
    Reconstructs the command string from parsed arguments dynamically.

    Args:
        args: Parsed arguments from argparse (typically an argparse.Namespace object).

    Returns:
        str: The command string as it would be run from the terminal.
    """
    # Get the script name from sys.argv[0] or __file__
    script_name = sys.argv[0] if sys.argv[0] else __file__
    command = ["python3", script_name]

    # Convert args to a dict and iterate over all attributes
    args_dict = vars(args)
    for arg_name, arg_value in args_dict.items():
        if arg_value is not None:  # Skip unset arguments
            # Convert long argument name to flag (e.g., 'input' -> '--input')
            flag = f"--{arg_name}" if len(arg_name) > 1 else f"-{arg_name}"
            # Handle boolean flags (no value) vs. arguments with values
            if isinstance(arg_value, bool):
                if arg_value:  # Only include if True
                    command.append(flag)
            else:
                command.extend([flag, str(arg_value)])

    return " ".join(command)
    
    
def check_line_in_file(file_path, target_line):
    """
    Check if a specific line exists in a file.
    
    Args:
        file_path (str): Path to the file to check.
        target_line (str): The line to search for.
    
    Returns:
        bool: True if the line is found, False otherwise.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there’s an issue reading the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if target_line.strip() in line:
                    return True
        return False
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except IOError as e:
        raise IOError(f"Error reading file '{file_path}': {e}")
        
        
def get_relative_path(from_path, to_path):
    """
    Returns the relative path from one path (file or directory) to another.

    Args:
        from_path (str): The starting path (file or directory).
        to_path (str): The target path (file or directory).

    Returns:
        str: The relative path from from_path to to_path.

    Raises:
        ValueError: If the paths are invalid or cannot be resolved on the current platform.

    This method calculates the relative path from `from_path` to `to_path`. If `from_path` is a file,
    the relative path is computed from its containing directory. If `from_path` is a directory,
    it is used directly as the starting point.

    Example:
        from_path = '/home/user/project/bin'
        to_path = '/home/user/project/images/file.jpg'
        Returns: '../images/file.jpg'

    Note: Uses `os.path.relpath()` to compute the relative path based on the operating system's path conventions.

    Example usage:
        relative_path = get_relative_path('/home/user/project/bin', '/home/user/project/images/file.jpg')
        # Outputs in orange: 'Relative path: ../images/file.jpg'
    """
    # If from_path is a file, use its directory; if it's a directory, use it directly
    start_dir = os.path.dirname(from_path) if os.path.isfile(from_path) else from_path
    relative_path = os.path.relpath(to_path, start_dir)
    return relative_path
    

def rename_file(file_path, new_name):
    """
    Rename a file by changing its base name while keeping the original extension.

    Args:
        file_path (str): The full path to the file to be renamed (e.g., '/path/to/file.txt').
        new_name (str): The new base name for the file (without extension, e.g., 'newfile').

    Returns:
        str: The new full path of the renamed file.

    Raises:
        FileNotFoundError: If the file at file_path does not exist.
        OSError: If there’s an error renaming the file (e.g., permission denied, file already exists).
        ValueError: If file_path has no extension or is invalid.

    This method renames a file by replacing its base name with new_name while preserving its extension.
    The new file remains in the same directory as the original.

    Example:
        rename_file('/home/user/docs/report.txt', 'summary')
        # Renames '/home/user/docs/report.txt' to '/home/user/docs/summary.txt'

    Note: The new_name should not include the extension; it will be appended from the original file_path.
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist")

    # Split the file path into directory, base name, and extension
    directory, filename = os.path.split(file_path)
    _, ext = os.path.splitext(filename)

    # Validate that there’s an extension
    if not ext:
        raise ValueError(f"The file path '{file_path}' has no extension")

    # Construct the new file path
    new_filename = f"{new_name}{ext}"
    new_file_path = os.path.join(directory, new_filename)

    # Rename the file
    os.rename(file_path, new_file_path)
    
    return new_file_path
    
    
def text_in_placeholder_string(placeholder_string, check_string):
    """
    This will determine if any combination of a string containing a placeholder exists within another string.
    
    Args:
        placeholder_string (str): The string containing placeholders.
        check_string (str): The string to check if one of the placeholder string variations exists in.
        
    Returns:
        bool: True if any placeholder combination is found in check_string, False otherwise.
    """
    all_combinations = generate_combinations(placeholder_string)
    if any(combo in check_string for combo in all_combinations):
        return True
    return False
    

def deduce_effect_style_from_effect_text(effect_text):
    """
    This method will return the effect style based on the effect text by comparing
    against patterns stored in style-specific text files.
    
    Args:
        effect_text (str): This is the effect text to process.
        
    Returns:
        effect_style (str): This is the appropriate effect style or None if no match.
    """
    # Convert effect_text to lowercase for case-insensitive matching
    effect_text = effect_text.lower()
    
    # Store matches to check for multiple
    matched_styles = []
    
    # Check each valid style
    for style in VALID_OVERLAY_STYLES:
        if style is None:
            continue
            
        # Construct file path using the EFFECT_STYLE_TEXT_FOLDER variable
        file_path = os.path.join(EFFECT_STYLE_TEXT_FOLDER, f"{style}.txt")
        
        try:
            # Read patterns from file
            with open(file_path, 'r') as f:
                patterns = [line.strip().lower() for line in f if line.strip()]
                
            # Check each pattern using text_in_placeholder_string
            for pattern in patterns:
                if text_in_placeholder_string(pattern, effect_text):
                    matched_styles.append(style)
                    break  # Move to next style after first match in file
                    
        except FileNotFoundError:
            # Skip if style file doesn't exist
            continue
    
    # Handle results
    if len(matched_styles) > 1:
        output_text(f"Error: Multiple effect styles matched for text '{effect_text}': {matched_styles}", "error")
        return matched_styles[0]  # Return first match despite error
    elif len(matched_styles) == 1:
        return matched_styles[0]
    else:
        return None


def has_at_most_one_from_source(source_list, target_list, num_of_matches=1):
    """
    Returns True if exactly num_of_matches item(s) from source_list appears in target_list.

    Args:
        source_list (list): The source list to search for items.
        target_list (list): The target list to search for items.
        num_of_matches (int): The number of matches to check against between the lists.

    Returns
        bool: True if the matches found equal num_of_matches.
    """
    source_set = set(source_list)
    matches = sum(1 for item in target_list if item in source_set)
    return matches == num_of_matches


def get_sequence_combinations(current_list, check_types=True, max_output_size=6):
    """
    Generate all unique sorted combinations of items from the given list.
    
    Args:
        current_list (list): List of items to generate combinations from.
        check_types (bool): This check will enable a check to make sure only one type from 
            TYPE_LIST_LOWER exists in the output. This is used for SN generation and other places.
        max_output_size (int): The maximum size for the output items to be.
    
    Returns:
        list: Sorted list of unique combinations.
    """
    # Sort the input list for consistency.
    current_list = sorted(cl.lower().strip() for cl in current_list)
    
    # check if the data is already in the buffer.
    item_tuple = tuple(current_list)
    if item_tuple in ALL_SEQUENCE_BUFFER:
        return ALL_SEQUENCE_BUFFER[item_tuple]
    
    output_text("Calling get_sequence_combinations... This may take some time!", "warning")
    
    # Create the initial list to parse. if check_types is on, we assume that the new_list will
    # only contain individual lists with one of the main TYPES.
    list_to_parse = current_list
    if check_types:
        new_list = [[c] for c in TYPE_LIST_LOWER]
    else:
        new_list = [[c] for c in current_list]
    
    # Loop over the data and generate combinations.
    while len(list_to_parse) > 0:
        for i, item in enumerate(list_to_parse):
            additions_list = []
            for i2, item2 in enumerate(new_list):
                if len(item2) >= max_output_size:
                    continue
                if item not in item2:
                    new_item = sorted([item] + [x for x in item2])
                    if new_item not in new_list:
                        if check_types:
                            # Check against types list: there can only ever be one item from 
                            # TYPE_LIST_LOWER in the output.
                            if has_at_most_one_from_source(TYPE_LIST_LOWER, new_item):
                                additions_list.append(new_item)
                        else:
                            additions_list.append(new_item)
            new_list = new_list + additions_list
            list_to_parse = list_to_parse[1:]
            
    # Sort and return the output as well as adding it to the buffer.
    sorted_output = sorted(new_list)
    ALL_SEQUENCE_BUFFER[item_tuple] = sorted_output
    return sorted_output


def get_combination_id(input_string, item_list, num_digits=4, print_combos=False, N=len(CHARACTERS)):
    """
    Generate a unique combination ID for a given input string based on predefined item combinations.
    
    Args:
        input_string (str): Comma-separated string of input items.
        item_list (list): List of available items to match against.
        num_digits (int, optional): Number of digits for the generated ID. Defaults to 3.
        print_combos (bool, optional): Whether to print all generated combinations. Defaults to False.
    
    Returns:
        str: A unique base-N encoded combination ID.
    
    Raises:
        ValueError: If the number of digits is insufficient for encoding.
    """
    global PRINT_ALL_SEQUENCES  # Declare PRINT_ALL_SEQUENCES as global
    
    # Convert both lists to lowercase for case-insensitive comparison and strip whitespace
    item_list = sorted(i.lower().strip() for i in item_list)
    input_items = sorted([s.strip().lower() for s in input_string.split(",")])    
    
    all_combinations = get_sequence_combinations(item_list)

    # Use PRINT_ALL_SEQUENCES to prevent printing this multiple times.
    if not PRINT_ALL_SEQUENCES and print_combos:
        for combo in all_combinations:
            output_text(f"{combo}", "note")
        PRINT_ALL_SEQUENCES = True
        
    index = all_combinations.index(input_items)
    
    # Fixed base-N conversion: encode full number, then truncate if needed
    result = ""
    temp_value = index
    while temp_value > 0:
        result = CHARACTERS[temp_value % N] + result
        temp_value //= N
    if not result:  # Handle index 0
        result = "0"
    # Pad or truncate to num_digits
    if len(result) < num_digits:
        result = "0" * (num_digits - len(result)) + result
    elif len(result) > num_digits:
        ValueError(f"ERROR: Not enough digits assigned for combinations.")
    return result
    
    

def get_number_id(number, level=5, per_level_val=500 , N=len(CHARACTERS)):
    """
    Generates a unique (ish) ID for a number by dividing the range 0-2500 into N equal parts.
    This assigns the input number to the closest part, used for card stats where max attack/defense is 2500.
    
    Args:
        number (int or float): The input number to convert to an ID (typically 0-2500).
        level (int): Optional specifier for level to adjust max.
        per_level_val (int): The change in value per level.
        N (int): The base number to use.
    
    Returns:
        int: An ID from 0 to 35 representing which of the N segments the number falls into.
    """
    # Maximum value for card stats (500 * level, assuming max level 5 = 2500)
    max_value = level * per_level_val
    
    # Calculate the size of each segment (2500 divided into N parts)
    segment_size = max_value / N
    
    # Ensure the number stays within bounds (0 to 2500)
    clamped_number = max(0, min(number, max_value))
    
    # Calculate which segment this number falls into
    # Use integer division to get the segment index (0 to N-1)
    segment_index = int(clamped_number // segment_size)
    
    # Handle the edge case where number equals max_value
    # Without this, 2500 would give N, which is out of our 0 to N - 1 range
    if segment_index >= N:
        segment_index = N - 1
    
    return CHARACTERS[segment_index]
    
    
def get_index_in_baseN(search_string, search_list, N=len(CHARACTERS)):
    """
    Find the index of a string in a list and return it in base N notation.
    
    Args:
        search_string (str or None): The string to search for in the list, or None.
        search_list (list): The list to search in, containing strings or other elements.
        N (int): The base to use for conversions.
    
    Returns:
        str: The index of the search_string in base N using CHARACTERS, or "0" if not found or input is None.
    """
    # Handle None input or empty list by returning "0" (base N for 0)
    if search_string is None or not search_list:
        return "0"
    
    # Find the index of the search_string in the list, default to -1 if not found
    try:
        index = search_list.index(search_string)
    except ValueError:
        return "0"  # Return "0" if the string isn't in the list
    
    # Convert the index to base N
    if index == 0:
        return "0"  # Special case for index 0
    
    result = ""
    num = index
    while num > 0:
        # Get the remainder when divided by N and map to CHARACTERS
        digit = num % N
        result = CHARACTERS[digit] + result
        num //= N  # Integer division for next digit
    
    return result
    

def sn_in_list(serial_number, filename):
    """
    Check if a serial number exists in a text file with one serial number per line.
    
    Args:
        serial_number (str): The serial number to check
        filename (str): Path to the file containing serial numbers
        
    Returns:
        bool: True if serial number exists in file, False otherwise
    """
    if serial_number.strip() == "":
        output_text(f"Serial number should not be empty!", "error")
        return False
 
    try:
        with open(filename, 'r') as file:
            # Read all lines and strip whitespace, compare with serial_number
            serial_numbers = [line.strip() for line in file]
            return serial_number.strip() in serial_numbers
    except FileNotFoundError:
        # Handle case where file doesn't exist
        return False
    except Exception as e:
        # Handle other potential errors (permissions, etc.)
        output_text(f"Error reading serial number list: {e}", "error")
        return False
        
        
def save_sn_to_list(serial_number, filename):
    """
    Save a serial number to a text file, appending it as a new line.
    
    Args:
        serial_number (str): The serial number to save
        filename (str): Path to the file containing serial numbers
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    if serial_number.strip() == "":
        output_text(f"Serial number should not be empty!", "error")
        return False

    try:
        with open(filename, 'a') as file:  # 'a' mode appends to end of file
            file.write(f"{serial_number}\n")  # Add newline to maintain one SN per line
        return True
    except IOError as e:
        output_text(f"Saving serial number to file: {e}", "error")
        return False
