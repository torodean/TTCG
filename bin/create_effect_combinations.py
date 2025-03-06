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
    

def clean_and_filter_combinations(combinations):
    """
    Processes a list of strings, replaces double spaces with single spaces, and removes strings containing specific phrases.

    Args:
        combinations (list): List of strings to clean and filter.

    Returns:
        list: List of cleaned and filtered strings.
    """
    phrases_to_remove = [
        "1 or lower",
        "1 or higher",
        "5 or lower",
        "5 or higher",
        "all point",
        "spell creature",
        "rank 4 spell",
        "rank 5 spell",
        "Add all rank",
        "Draw all card",
        "discard all card",
        "the top all card",
        "mill all card",
        "spell cards gain",
        "spell card gain",
        "spell cards lose",
        "spell card lose",
        "rank -2",
        "rank -1",
        "rank 0",
        "rank 6",
        "rank 7",
        "rank 8",
        "Add four"
        "Add five"
        "Add three"
        # Add more phrases here as needed
    ]
    
    cleaned_combinations = []
    
    for line in combinations:
        # Replace all double spaces with single spaces
        cleaned_line = line.replace("  ", " ")
        
        # Check if any phrase from the list is in the string
        if not any(phrase in cleaned_line for phrase in phrases_to_remove):
            # Only keep the string if no phrases match
            cleaned_combinations.append(cleaned_line.strip())
    
    return cleaned_combinations


def replace_phrases_in_combinations(combinations):
    """
    Searches a list of strings and replaces specific phrases with their designated replacements.

    Args:
        combinations (list): List of strings to process.

    Returns:
        list: List of strings with phrases replaced.
    """
    # Define the dictionary of phrases to replace and their replacements
    phrase_replacements = {
        # Numbered point(s) cleanup
        "one point(s)": "one point",
        "two point(s)": "two points",
        "three point(s)": "three points",
        "four point(s)": "four points",
        "five point(s)": "five points",
        "one points": "one point",
        "two point": "two points",
        "three point": "three points",
        "four point": "four points",
        "five point": "five points",
        
        # Numbered card(s) cleanup
        "one card(s)": "one card",
        "two card(s)": "two cards",
        "three card(s)": "three cards",
        "four card(s)": "four cards",
        "five card(s)": "five cards",
        "one cards": "one card",
        "two card": "two cards",
        "three card": "three cards",
        "four card": "four cards",
        "five card": "five cards",
        
        # Numbered target(s) cleanup
        "one target(s)": "one target",
        "two target(s)": "two targets",
        "three target(s)": "three targets",
        "four target(s)": "four targets",
        "five target(s)": "five targets",
        "one targets": "one target",
        "two target": "two targets",
        "three target": "three targets",
        "four target": "four targets",
        "five target": "five targets",
                
        # Numbered spell(s) cleanup
        "one spell(s)": "one spell",
        "two spell(s)": "two spells",
        "three spell(s)": "three spells",
        "four spell(s)": "four spells",
        "five spell(s)": "five spells",
        "one spells": "one spell",
        "two spell": "two spells",
        "three spell": "three spells",
        "four spell": "four spells",
        "five spell": "five spells",
                
        # Numbered creature(s) cleanup
        "one creature(s)": "one creature",
        "two creature(s)": "two creatures",
        "three creature(s)": "three creatures",
        "four creature(s)": "four creatures",
        "five creature(s)": "five creatures",
        "one creatures": "one creature",
        "two creature": "two creatures",
        "three creature": "three creatures",
        "four creature": "four creatures",
        "five creature": "five creatures",
        
        # remaining non-numbered words to be fixed
        "spell(s)": "spells",
        "target(s)": "targets",
        "point(s)": "points",
        "card(s)": "cards",
        "creature(s)": "creatures",
        "spellss": "spells",
        "targetss": "targets",
        "pointss": "points",
        "cardss": "cards",
        "creaturess": "creatures",
        
        # duplicate card        
        "card card": "card",
    }
    
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
    args = parser.parse_args()
    
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
    all_combinations = clean_and_filter_combinations(all_combinations)
    all_combinations = replace_phrases_in_combinations(all_combinations)
    all_combinations = alphabetize_strings(all_combinations)
    
    if not args.test_mode:
        write_combinations_to_file(all_combinations, args.output_file)
    
    # Print each generated combination
    for combo in all_combinations:
        print(combo)

    print(f"Total combinations: {len(all_combinations)}")
