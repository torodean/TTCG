#!/bin/python3

import argparse
import os
import re
import csv

# load needed methods from ttcg_tools
from ttcg_tools import load_placeholder_values
from ttcg_tools import generate_combinations
from ttcg_tools import get_command_string


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
        
        resolved_values = load_placeholder_values(placeholder_name, placeholder_dir)
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


def delete_matching_lines(input_file, output_file, search_string):
    """
    Deletes lines from a file that contain an exact match to the search string.
    
    Processes an input file (text or CSV) and writes all lines that do not contain
    the exact search string to the output file. For CSV files, checks the EFFECTNAME
    column (or first column if EFFECTNAME not found) for matches.

    Args:
        input_file (str): Path to the input file (text or CSV).
        output_file (str): Path to the output file to write remaining lines.
        search_string (str): Exact string to match for line deletion.

    Returns:
        None: Writes filtered results to output_file and prints status messages.

    Raises:
        FileNotFoundError: If input file doesn't exist.
        Exception: For other processing errors.
    """
    try:
        is_csv = input_file.endswith('.csv')
        
        if is_csv:
            with open(input_file, 'r', newline='') as f:
                reader = csv.reader(f, delimiter=';')
                header = next(reader)
                rows = list(reader)
                
                effect_col = header.index('EFFECTNAME') if 'EFFECTNAME' in header else 0
                filtered_rows = [row for row in rows if search_string not in row[effect_col]]
                
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(header)
                writer.writerows(filtered_rows)
        else:
            with open(input_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                filtered_lines = [line for line in lines if search_string not in line]
                
            with open(output_file, 'w') as f:
                f.write('\n'.join(filtered_lines))
                if filtered_lines:  # Add newline at end if not empty
                    f.write('\n')
        
        print(f"Processed '{input_file}', removed lines matching '{search_string}', wrote to '{output_file}'.")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
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
    parser.add_argument('-d', '--delete', help="Exact string to match for deleting entire lines.")
    args = parser.parse_args()

    # Print the command using the generic method
    print(get_command_string(args))

    # Ensure exactly one of -t/--text, -e/--exact, or -d/--delete is provided
    provided_options = sum(1 for opt in [args.text, args.exact, args.delete] if opt is not None)
    if provided_options != 1:
        parser.error("You must provide exactly one of -t/--text, -e/--exact, or -d/--delete.")
    
    if args.delete:
        delete_matching_lines(args.input, args.output, args.delete)
    else:
        process_effects_file(args.input, args.output, args.placeholder_dir, args.column, args.text, args.exact)
        

if __name__ == "__main__":
    main()
