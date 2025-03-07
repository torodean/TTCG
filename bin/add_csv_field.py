#!/bin/python3

import argparse
import os
import re
import csv


def load_placeholder_values(placeholder_dir, placeholder, visited=None):
    """
    Loads and resolves values for a placeholder from a text file, handling nested placeholders recursively.

    This function reads a file named `<placeholder>.txt` from the specified directory, processes its lines into a list of
    values, and recursively resolves any nested placeholders (e.g., `<other>` within a value). It prevents infinite
    recursion by tracking visited placeholders and returning the unresolved placeholder (e.g., `<placeholder>`) if a
    cycle is detected or if the file is missing/empty.

    Args:
        placeholder_dir (str): Directory path containing placeholder text files (e.g., 'placeholders/').
        placeholder (str): Name of the placeholder to load values for (e.g., 'number'), without angle brackets.
        visited (set, optional): Set of placeholders already processed in the recursion stack to detect cycles.
                                 Defaults to None, initializing an empty set if not provided.

    Returns:
        list: A list of resolved string values for the placeholder. If the file doesn’t exist, is empty, or a cycle is
              detected, returns a single-element list containing the unresolved placeholder (e.g., ['<placeholder>']).

    Examples:
        >>> load_placeholder_values('placeholders/', 'number')
        ['1', '2', '3']  # Assuming placeholders/number.txt contains "1\n2\n3"
        >>> load_placeholder_values('placeholders/', 'missing')
        ['<missing>']  # If placeholders/missing.txt doesn’t exist
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
        raw_values = [line.strip().replace('_', '') for line in f if line.strip()]
    
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


def generate_combinations(sentence, placeholder_dir, visited=None):
    """
    Generates all possible combinations of a sentence by replacing placeholders with their resolved values.

    This function takes a sentence containing placeholders (e.g., '<number>') and replaces each with values loaded from
    corresponding files in the specified directory, using `load_placeholder_values`. It computes the Cartesian product
    of all placeholder value sets to produce every possible combination. Recursion is managed via a visited set to avoid
    infinite loops with nested placeholders.

    Args:
        sentence (str): Input sentence with placeholders in angle brackets (e.g., "Draw <number> cards").
        placeholder_dir (str): Directory path containing placeholder text files (e.g., 'placeholders/').
        visited (set, optional): Set of placeholders already processed in the recursion stack to detect cycles.
                                 Defaults to None, initializing an empty set if not provided.

    Returns:
        list: A list of strings, each representing a unique combination of the sentence with all placeholders replaced.
              If no placeholders are found, returns a single-element list containing the original sentence.

    Examples:
        >>> generate_combinations("Draw <number> cards", "placeholders/")
        ['Draw 1 cards', 'Draw 2 cards', 'Draw 3 cards']  # Assuming number.txt has "1\n2\n3"
        >>> generate_combinations("No placeholders here", "placeholders/")
        ['No placeholders here']  # No placeholders, returns original sentence
    """
    if visited is None:
        visited = set()
    
    placeholders = re.findall(r"<([^>]+)>", sentence)
    if not placeholders:
        return [sentence]
    
    placeholder_values = {p: load_placeholder_values(placeholder_dir, p, visited.copy()) for p in placeholders}
    from itertools import product
    combinations = []
    all_values = [placeholder_values[p] for p in placeholders]
    for combo in product(*all_values):
        result = sentence
        for placeholder, value in zip(placeholders, combo):
            result = result.replace(f"<{placeholder}>", value)
        combinations.append(result)
    return combinations


def check_pattern_existence(effect, pattern, placeholder_dir):
    """
    Checks if a pattern, with or without placeholders, exists within an effect string.

    This function determines whether a given pattern matches an effect string. It handles three cases: (1) a single
    placeholder (e.g., '<type>'), checking if its resolved values or the placeholder itself appear in the effect; (2) a
    pattern with multiple placeholders (e.g., 'Destroy <number> cards'), generating all combinations and checking for
    matches; and (3) a literal string with no placeholders, performing a direct substring check. Placeholder values are
    loaded from files in the specified directory using `load_placeholder_values`.

    Args:
        effect (str): The effect string to search within (e.g., "Destroy 2 creature cards").
        pattern (str): The pattern to search for, which may include placeholders (e.g., "Destroy <number> cards").
        placeholder_dir (str): Directory path containing placeholder text files (e.g., 'placeholders/').

    Returns:
        bool: True if the pattern (or any of its resolved combinations) exists in the effect, False otherwise.

    Examples:
        >>> check_pattern_existence("Draw 2 cards", "Draw <number> cards", "placeholders/")
        True  # Assuming number.txt has "2"
        >>> check_pattern_existence("Gain life", "<type>", "placeholders/")
        False  # No "<type>" or its values in "Gain life"
        >>> check_pattern_existence("Lose 5 points", "Lose", "placeholders/")
        True  # Literal match
    """
    # Check if pattern is a single placeholder (e.g., "<type>")
    placeholder_match = re.search(r"^<([^>]+)>$", pattern)
    if placeholder_match:
        placeholder_name = placeholder_match.group(1)
        file_path = os.path.join(placeholder_dir, f"{placeholder_name}.txt")
        if not os.path.exists(file_path):
            return False
        
        if f"<{placeholder_name}>" in effect:
            return True
        
        resolved_values = load_placeholder_values(placeholder_dir, placeholder_name)
        return any(value in effect for value in resolved_values if value != f"<{placeholder_name}>")
    
    # Handle patterns with placeholders (e.g., "Destroy <number> <type> cards")
    placeholders = re.findall(r"<([^>]+)>", pattern)
    if placeholders:
        # Check if all placeholder files exist
        for placeholder in placeholders:
            file_path = os.path.join(placeholder_dir, f"{placeholder}.txt")
            if not os.path.exists(file_path):
                return False
        
        # Check if the pattern with placeholders appears literally
        if pattern in effect:
            return True
        
        # Generate all combinations of the pattern
        resolved_patterns = generate_combinations(pattern, placeholder_dir)
        return any(resolved_pattern in effect for resolved_pattern in resolved_patterns)
    
    # No placeholders, just literal match
    return pattern in effect


def process_effects_file(input_file, output_file, placeholder_dir, column_name, pattern, exact_line=None, match_column=None):
    """
    Processes an effects file and generates a CSV with a column indicating pattern or exact match existence.

    This function reads an input file (text or semicolon-delimited CSV), evaluates each effect against a pattern or exact
    substring, and writes the results to an output CSV. For text inputs, it creates a new CSV with 'EFFECTNAME' and the
    specified column. For CSV inputs, it updates an existing column or adds a new one, setting values to 'True' or 'False'
    based on matches. If `exact_line` is provided, it delegates to `set_exact_match_to_true`; otherwise, it uses
    `check_pattern_existence` for pattern matching with placeholders. If `match_column` is specified for CSV inputs,
    only rows where that column is 'True' are evaluated for matches.

    Args:
        input_file (str): Path to the input file (text or CSV) containing effects.
        output_file (str): Path to the output CSV file to write results.
        placeholder_dir (str): Directory path containing placeholder text files (e.g., 'placeholders/').
        column_name (str): Name of the column to add or update (e.g., 'HasDraw').
        pattern (str): Pattern to match against effects, may include placeholders (e.g., 'Draw <number> cards').
        exact_line (str, optional): Exact substring to match instead of a pattern. If provided, overrides pattern matching.
                                    Defaults to None.
        match_column (str, optional): Name of an existing CSV column that must be 'True' for pattern matching to proceed.
                                      Ignored for text inputs or if None. Defaults to None.

    Returns:
        None: Writes results to `output_file` and prints status messages; does not return a value.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If `match_column` is specified but not found in the CSV header.
        Exception: For other processing errors (e.g., malformed CSV), with an error message.

    Examples:
        >>> process_effects_file('effects.txt', 'out.csv', 'placeholders/', 'HasDraw', 'Draw <number> cards')
        # Creates out.csv with EFFECTNAME and HasDraw columns from effects.txt
        >>> process_effects_file('in.csv', 'out.csv', 'placeholders/', 'HasSpell', 'Cast <type>', match_column='UNIT')
        # Updates out.csv with HasSpell column, only where UNIT is 'True'
        >>> process_effects_file('in.csv', 'out.csv', 'placeholders/', 'HasSpell', 'Cast <type>', exact_line='Cast spell')
        # Updates out.csv with HasSpell column based on exact match 'Cast spell', ignoring match_column
    """
    if exact_line is not None:
        set_exact_match_to_true(input_file, output_file, column_name, exact_line)
    else:
        # Existing pattern-matching logic here
        try:
            is_csv = input_file.endswith('.csv')
            
            if is_csv:
                with open(input_file, 'r', newline='') as f:
                    reader = csv.reader(f, delimiter=';')
                    header = next(reader)
                    rows = list(reader)
                
                if column_name in header:
                    print(f"'{column_name}' exists in '{input_file}'. Updating False to True where pattern matches.")
                    col_idx = header.index(column_name)
                    effect_col = header.index('EFFECTNAME') if 'EFFECTNAME' in header else 0
                    if match_column is not None:
                        match_idx = header.index(match_column)  # Raises ValueError if not found
                    for row in rows:
                        effect = row[effect_col]
                        if match_column is not None:
                            col_match = row[match_idx]
                            if col_match != 'True':
                                continue
                        pattern_exists = check_pattern_existence(effect, pattern, placeholder_dir)
                        if pattern_exists and row[col_idx] != "True":
                            row[col_idx] = "True"
                else:
                    print(f"'{column_name}' not found in '{input_file}'. Adding new column.")
                    header.append(column_name)
                    col_idx = len(header) - 1
                    effect_col = header.index('EFFECTNAME') if 'EFFECTNAME' in header else 0
                    if match_column is not None:
                        match_idx = header.index(match_column)  # Raises ValueError if not found
                    updated_rows = []
                    for row in rows:
                        effect = row[effect_col]
                        if len(row) <= col_idx:
                            row.extend([''] * (col_idx - len(row) + 1))
                        if match_column is not None:
                            col_match = row[match_idx]
                            if col_match != 'True':
                                continue
                        pattern_exists = check_pattern_existence(effect, pattern, placeholder_dir)
                        row[col_idx] = "True" if pattern_exists else "False"
                        updated_rows.append(row)
                    rows = updated_rows
            
            else:
                with open(input_file, 'r') as f:
                    effects = [line.strip() for line in f if line.strip()]
                
                header = ["EFFECTNAME", column_name]
                rows = []
                for effect in effects:
                    pattern_exists = check_pattern_existence(effect, pattern, placeholder_dir)
                    rows.append([effect, str(pattern_exists)])
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(header)
                writer.writerows(rows)
            
            print(f"Processed '{input_file}' into '{output_file}' with column '{column_name}'.")
        
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            exit(1)
        except Exception as e:
            print(f"Error processing file: {e}")
            exit(1)


def set_exact_match_to_true(input_file, output_file, column_name, exact_line):
    """
    Searches for an exact substring in effect strings and sets a specified column to True in the output CSV.

    This function processes an input file (text or semicolon-delimited CSV) containing effect descriptions. For text
    inputs, it generates a new CSV with 'EFFECTNAME' and the specified column, setting the column to 'True' if the
    substring matches, 'False' otherwise. For CSV inputs, it updates an existing column to 'True' where the substring
    appears in the effect, requiring the column to already exist. The result is written to the output CSV file.

    Args:
        input_file (str): Path to the input file (text or CSV) containing effects.
        output_file (str): Path to the output CSV file to write results.
        column_name (str): Name of the column to update or create (e.g., 'HasExactMatch').
        exact_line (str): Exact substring to search for within the effects (e.g., 'Draw two').

    Returns:
        None: Writes results to `output_file` and prints status messages; does not return a value.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If `column_name` is not found in an input CSV’s header.
        Exception: For other processing errors (e.g., file write issues), with an error message.

    Examples:
        >>> set_exact_match_to_true('effects.txt', 'out.csv', 'HasDraw', 'Draw two')
        # Creates out.csv with EFFECTNAME and HasDraw columns, True where 'Draw two' appears
        >>> set_exact_match_to_true('in.csv', 'out.csv', 'HasSpell', 'Cast spell')
        # Updates out.csv, setting HasSpell to True where 'Cast spell' matches (column must exist)
    """
    try:
        is_csv = input_file.endswith('.csv')
        
        if is_csv:
            with open(input_file, 'r', newline='') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader)
                rows = list(reader)
            
            if column_name not in header:
                raise ValueError(f"Column '{column_name}' not found in '{input_file}'.")
            
            col_idx = header.index(column_name)
            effect_col = header.index('EFFECTNAME') if 'EFFECTNAME' in header else 0
            for row in rows:
                effect = row[effect_col]
                if exact_line in effect:
                    row[col_idx] = "True"
        
        else:
            with open(input_file, 'r') as f:
                effects = [line.strip() for line in f if line.strip()]
            
            header = ["EFFECTNAME", column_name]
            rows = []
            for effect in effects:
                rows.append([effect, "True" if exact_line in effect else "False"])
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(header)
            writer.writerows(rows)
        
        print(f"Processed '{input_file}' into '{output_file}', set '{column_name}' to True for substring match '{exact_line}'.")
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="Convert effects file to CSV with custom pattern check.")
    parser.add_argument('-i', '--input', default='effects/effects_with_placeholders.csv',
                        help="Input file (text or CSV) containing effects (defaults to 'effects/effects_with_placeholders.csv').")
    parser.add_argument('-p', '--placeholder_dir', default='placeholders',
                        help="Directory containing placeholder files (defaults to 'placeholders').")
    parser.add_argument('-o', '--output', default='effects/effects_with_placeholders.csv',
                        help="Output CSV file (defaults to 'effects/effects_with_placeholders.csv').")
    parser.add_argument('-c', '--column', required=True,
                        help="Name of the column to update or add (e.g., 'HasMyString').")
    parser.add_argument('-t', '--text',
                        help="Pattern to search for (e.g., 'some text <placeholder> more text').")
    parser.add_argument('-e', '--exact', help="Exact line to match and set the specified column to True.")
    parser.add_argument('-m', '--match_column', help="An extra identifier for specifying a column which must be true to evaluate as a match.")
    args = parser.parse_args()

    # Ensure exactly one of -e or -t is provided
    if (args.text is None) == (args.exact is None):
        parser.error("You must provide exactly one of -t/--text or -e/--exact, but not both.")
    
    process_effects_file(args.input, args.output, args.placeholder_dir, args.column, args.text, args.exact)

if __name__ == "__main__":
    main()
