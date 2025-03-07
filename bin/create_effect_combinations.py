#!/bin/python3

import os
import itertools
import re
import argparse


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


def load_placeholder_values(placeholder_dir, placeholder, visited=None):
    """
    Load possible values for a given placeholder from a corresponding text file, recursively resolving nested placeholders.

    Args:
        placeholder_dir (str): Directory containing placeholder text files.
        placeholder (str): Placeholder name.
        visited (set, optional): Set of placeholders already processed to prevent infinite recursion.

    Returns:
        list: List of fully resolved values for the placeholder.
    """
    # Initialize visited set to track recursion and prevent cycles
    if visited is None:
        visited = set()
    
    # Avoid infinite recursion by skipping if placeholder already visited
    if placeholder in visited:
        return [f"<{placeholder}>"]  # Return unresolved placeholder as-is to signal a cycle
    
    visited.add(placeholder)
    
    file_path = os.path.join(placeholder_dir, f"{placeholder}.txt")
    if not os.path.exists(file_path):
        visited.remove(placeholder)  # Clean up before returning
        return [f"<{placeholder}>"]  # Return unresolved placeholder if file missing
    
    raw_values = []
    with open(file_path, 'r') as f:
        raw_values = [line.strip().replace('_', '') for line in f if line.strip()]
    
    if not raw_values:
        visited.remove(placeholder)
        return [f"<{placeholder}>"]  # Return unresolved if file empty
    
    # Process each value for nested placeholders
    resolved_values = []
    for value in raw_values:
        if re.search(r"<[^>]+>", value):  # Check if value contains placeholders
            # Treat value as a sentence and recursively generate combinations
            sub_combinations = generate_combinations(value, placeholder_dir, visited.copy())
            resolved_values.extend(sub_combinations)
        else:
            resolved_values.append(value)
    
    visited.remove(placeholder)  # Clean up after processing
    return resolved_values


def generate_combinations(sentence, placeholder_dir, visited=None):
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
            placeholder_values[base] = load_placeholder_values(placeholder_dir, base, visited)
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
    

def clean_and_filter_combinations(combinations, config_file):
    """
    Processes a list of strings, replaces double spaces with single spaces, and removes strings containing specific phrases
    loaded from a configuration file.

    Args:
        combinations (list): List of strings to clean and filter.
        config_file (str): Path to the configuration file containing phrases to remove (default: 'placeholders/combinations_to_remove.txt').

    Returns:
        list: List of cleaned and filtered strings.
    """
    # Load phrases to remove from the configuration file
    try:
        with open(config_file, 'r') as f:
            phrases_to_remove = [line.strip() for line in f if line.strip()]
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


def replace_phrases_in_combinations(combinations, replacements_file):
    """
    Searches a list of strings and replaces specific phrases with their designated replacements loaded from a configuration file.
    Lines starting with '#' in the file are treated as comments and ignored.

    Args:
        combinations (list): List of strings to process.
        replacements_file (str): Path to the configuration file containing phrase replacements (default: 'placeholders/phrase_replacements.txt').

    Returns:
        list: List of strings with phrases replaced.
    """
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


def dedupe_file(file_path):
    """
    Reads a file, removes duplicate lines, writes back the unique lines, and exits the program.

    Args:
        file_path (str): Path to the file to deduplicate.
    """
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate all possible combinations for placeholders in a sentence.")
    parser.add_argument('-s', "--sentence", default=None, 
                        help="Sentence with placeholders enclosed in <>.")
    parser.add_argument('-f', "--file", nargs='?', const="effects/all_effect_templates.txt", default=None,
                        help="A file of sentences with placeholders enclosed in <>. Defaults to 'default.txt' if no file specified.")    
    parser.add_argument('-p', "--placeholder_dir", default="placeholders", 
                        help="Directory containing placeholder text files.")
    parser.add_argument('-o', "--output_file", default="effects/all_effects.txt",
                        help="The file to output the effects to.")
    parser.add_argument('-t', "--test_mode", default=False, action='store_true', 
                        help="Test mode will only output the combinations to terminal.")
    parser.add_argument('-d', '--dedupe', nargs='?', const='effects/all_effects.txt', default=None,
                        help="Remove duplicate lines from the specified file (or 'effects/all_effects.txt' if none given) and exit.")
    parser.add_argument('-c', '--combinations_to_remove', default='placeholders/combinations_to_remove.txt',
                    help="List file containing phrases to remove from resulting combinations (default: 'placeholders/combinations_to_remove.txt').")
    parser.add_argument('-r', '--replacements_file', default='placeholders/phrase_replacements.txt',
                    help="Configuration file containing phrase replacements (format: 'old phrase: new phrase') (default: 'placeholders/phrase_replacements.txt').")
    args = parser.parse_args()
    
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
            
    
    all_combinations = remove_duplicates(all_combinations)
    all_combinations = clean_and_filter_combinations(all_combinations, args.combinations_to_remove)
    all_combinations = replace_phrases_in_combinations(all_combinations, args.replacements_file)
    all_combinations = alphabetize_strings(all_combinations)
    
    if not args.test_mode:
        write_combinations_to_file(all_combinations, args.output_file)
    
    # Print each generated combination
    for combo in all_combinations:
        print(combo)

    print(f"Total combinations: {len(all_combinations)}")
