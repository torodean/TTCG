#!/bin/python3

import re
import argparse

# load needed methods from ttcg_tools
from ttcg_tools import generate_combinations
from ttcg_tools import get_command_string

# Load some needed constants from ttcg_constants
from ttcg_constants import DEFAULT_PLACEHOLDERS_FOLDER
from ttcg_constants import DEFAULT_ALL_EFFECTS_FILE
from ttcg_constants import DEFAULT_ALL_EFFECT_TEMPLATES_FILE
from ttcg_constants import DEFAULT_COMBOS_TO_REMOVE_FILE
from ttcg_constants import DEFAULT_PHRASES_TO_REPLACE_FILE


def write_combinations_to_file(combinations, output_file):
    """
    Append all generated combinations to a specified file.

    Args:
        combinations (list): List of sentence combinations.
        output_file (str): Path to the output file.
    """
    with open(output_file, 'a') as f:
        for combination in combinations:
            f.write(combination + '\n')


def clean_and_filter_combinations(combinations, config_file, verbose=False):
    """
    Processes a list of strings, replaces double spaces with single spaces, and removes strings containing specific phrases
    loaded from a configuration file.

    Args:
        combinations (list): List of strings to clean and filter.
        config_file (str): Path to the configuration file containing phrases to remove (default: 'placeholders/combinations_to_remove.txt').
        verbose (bool): Adds extra output.

    Returns:
        list: List of cleaned and filtered strings.
    """
    if verbose:
        print(f"Cleaning combinations based on config file: {config_file}")

    # Load phrases to remove from the configuration file
    try:
        with open(config_file, 'r') as f:
            phrases_to_remove = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except FileNotFoundError:
        # If the file doesn't exist, use an empty list or raise a warning
        phrases_to_remove = []
        print(f"Warning: Configuration file '{config_file}' not found. No phrases will be filtered.")
    except Exception as e:
        phrases_to_remove = []
        print(f"Error loading configuration file '{config_file}': {e}")

    cleaned_combinations = []

    for line in combinations:
        # Replace all double spaces with single spaces
        cleaned_line = line.replace("  ", " ")

        # Check if any phrase from the list is in the string
        if not any(phrase in cleaned_line for phrase in phrases_to_remove):
            # Only keep the string if no phrases match
            cleaned_combinations.append(cleaned_line.strip())

    return cleaned_combinations


def replace_phrases_in_combinations(combinations, replacements_file, verbose=False, fix_plurality=True):
    """
    Searches a list of strings and replaces specific phrases with their designated replacements loaded from a configuration file.
    Lines starting with '#' in the file are treated as comments and ignored.

    Args:
        combinations (list): List of strings to process.
        replacements_file (str): Path to the configuration file containing phrase replacements (default: 'placeholders/phrase_replacements.txt').
        verbose (bool): Adds extra output.
        fix_plurality (bool): Also performs various plurality fixes.

    Returns:
        list: List of strings with phrases replaced.
    """
    if verbose:
        print(f"Replacing phrases from replacement file: {replacements_file}")

    # Load phrase replacements from the configuration file
    phrase_replacements = {}
    try:
        with open(replacements_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines or comments (lines starting with '#')
                if not line or line.startswith('#'):
                    continue
                if ':' in line:  # Ensure line has a key-value separator
                    old_phrase, new_phrase = map(str.strip, line.split(':', 1))
                    phrase_replacements[old_phrase] = new_phrase
    except FileNotFoundError:
        print(f"Warning: Replacement file '{replacements_file}' not found. No replacements will be applied.")
    except Exception as e:
        print(f"Error loading replacement file '{replacements_file}': {e}")

    updated_combinations = []
    
    for line in combinations:
        updated_line = line
        
        # Apply each replacement to the string
        for old_phrase, new_phrase in phrase_replacements.items():
            updated_line = updated_line.replace(old_phrase, new_phrase)
            
        if fix_plurality:
            # Fix grammar for phrases similar to "two ___ card", "two ___ cards", etc...
            updated_line = re.sub(r"one (\w+) cards\b", r"one \1 card", updated_line)
            updated_line = re.sub(r"one (\w+) spells\b", r"one \1 spell", updated_line)
            updated_line = re.sub(r"one (\w+) creatures\b", r"one \1 creature", updated_line)
            updated_line = re.sub(r"one (\w+) targets\b", r"one \1 target", updated_line)
            updated_line = re.sub(r"one (\w+ \d+) cards\b", r"one \1 card", updated_line)
            updated_line = re.sub(r"one (\w+ \d+) spells\b", r"one \1 spell", updated_line)
            updated_line = re.sub(r"one (\w+ \d+) creatures\b", r"one \1 creature", updated_line)
            updated_line = re.sub(r"one (\w+ \d+) targets\b", r"one \1 target", updated_line)
            
            updated_line = re.sub(r"one (.+?) cards\b", r"one \1 card", updated_line)
            updated_line = re.sub(r"one (.+?) spells\b", r"one \1 spell", updated_line)
            updated_line = re.sub(r"one (.+?) creatures\b", r"one \1 creature", updated_line)
            updated_line = re.sub(r"one (.+?) targets\b", r"one \1 target", updated_line)
        
        updated_combinations.append(updated_line)
    
    return updated_combinations


def remove_duplicates(strings):
    """
    Removes all duplicate strings from a list, keeping only the first occurrence.

    Args:
        strings (list): List of strings to process.

    Returns:
        list: List with duplicates removed, preserving order of first appearance.
    """
    seen = set()
    unique_strings = []
    
    for s in strings:
        if s not in seen:
            seen.add(s)
            unique_strings.append(s)
    
    return unique_strings


def alphabetize_strings(string_list):
    """
    Takes a list of strings and returns a new list sorted alphabetically.

    Args:
        string_list (list): List of strings to alphabetize.

    Returns:
        list: New list with strings in alphabetical order.
    """
    return sorted(string_list)


def dedupe_file(file_path, verbose=False):
    """
    Reads a file, removes duplicate lines, writes back the unique lines, and exits the program.

    Args:
        file_path (str): Path to the file to deduplicate.
        verbose (bool): Adds extra output.
    """
    if verbose:
        print(f"De-duplicating file: {file_path}.")

    try:
        # Read all lines, preserving order, removing duplicates
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Remove duplicates while preserving order
        seen = set()
        unique_lines = [line for line in lines if not (line in seen or seen.add(line))]
        
        # Write back to the same file
        with open(file_path, 'w') as f:
            f.writelines(unique_lines)
        
        print(f"Duplicates removed from '{file_path}'. Exiting.")
        exit(0)
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        exit(1)
        
        
def capitalize_list(string_list):
    """
    Takes a list of strings and returns a new list with each string's first letter capitalized.
    
    Args:
        string_list (list): A list of strings to be capitalized
        
    Returns:
        list: A new list with capitalized strings
    """
    return [s.capitalize() for s in string_list]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate all possible combinations for placeholders in a sentence.")
    parser.add_argument('-s', "--sentence", default=None, 
                        help="Sentence with placeholders enclosed in <>.")
    parser.add_argument('-f', "--file", nargs='?', const=DEFAULT_ALL_EFFECT_TEMPLATES_FILE, default=None,
                        help="A file of sentences with placeholders enclosed in <>. Defaults to None if no file specified.")    
    parser.add_argument('-p', "--placeholder_dir", default=DEFAULT_PLACEHOLDERS_FOLDER, 
                        help="Directory containing placeholder text files.")
    parser.add_argument('-o', "--output_file", default=DEFAULT_ALL_EFFECTS_FILE,
                        help="The file to output the effects to.")
    parser.add_argument('-t', "--test_mode", default=False, action='store_true', 
                        help="Test mode will only output the combinations to terminal.")
    parser.add_argument('-v', "--verbose", default=False, action='store_true',
                        help="Adds extra output during program processing.")
    parser.add_argument('-d', '--dedupe', nargs='?', const=DEFAULT_ALL_EFFECTS_FILE, default=None,
                        help=f"Remove duplicate lines from the specified file (or '{DEFAULT_ALL_EFFECTS_FILE}' if none given) and exit.")
    parser.add_argument('-c', '--combinations_to_remove', default=DEFAULT_COMBOS_TO_REMOVE_FILE,
                    help=f"List file containing phrases to remove from resulting combinations (default: '{DEFAULT_COMBOS_TO_REMOVE_FILE}').")
    parser.add_argument('-r', '--replacements_file', default=DEFAULT_PHRASES_TO_REPLACE_FILE,
                    help=f"Configuration file containing phrase replacements (format: 'old phrase: new phrase') (default: '{DEFAULT_PHRASES_TO_REPLACE_FILE}').")
    args = parser.parse_args()

    # Print the command using the generic method
    print(get_command_string(args))

    # Run deduplication if -d is specified
    if args.dedupe:
        dedupe_file(args.dedupe)
    
    # Custom validation: ensure exactly one of -s or -f is provided
    if (args.sentence is None) == (args.file is None):
        parser.error("You must provide exactly one of -s/--sentence or -f/--file, but not both.")

    # Process the input
    all_combinations = []

    if args.sentence:
        # Process a single sentence
        combinations = generate_combinations(args.sentence, args.placeholder_dir)
        all_combinations.extend(combinations)
    elif args.file:
        # Process each line from the file
        try:
            with open(args.file, 'r') as f:
                for line in f:
                    sentence = line.strip()
                    if sentence:  # Skip empty lines
                        combinations = generate_combinations(sentence, args.placeholder_dir)
                        all_combinations.extend(combinations)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            exit(1)
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
            
    
    # First, remove any duplicates that were generated.
    all_combinations = remove_duplicates(all_combinations)
    
    # Replace phrases to fix errors made during template replacement.
    all_combinations = replace_phrases_in_combinations(all_combinations, args.replacements_file)
    
    # This must appear after the call to replace_phrases_in_combinations because some of the phrases in the
    # config file will only appear after it has been ran.
    all_combinations = clean_and_filter_combinations(all_combinations, args.combinations_to_remove)
    
    # Run replace_phrases_in_combinations again without plurality fixes to catch some straggler phrases that became incorrect.
    all_combinations = replace_phrases_in_combinations(all_combinations, args.replacements_file, fix_plurality=False)
    
    # alphabetize the output effect combinations.
    all_combinations = alphabetize_strings(all_combinations)
    
    # Make sure the first letter of each string is capitalized.
    all_combinations = capitalize_list(all_combinations)
    
    if not args.test_mode:
        write_combinations_to_file(all_combinations, args.output_file)

    if args.verbose:
        # Print each generated combination
        for combo in all_combinations:
            print(combo)

    print(f"Total combinations: {len(all_combinations)}")
