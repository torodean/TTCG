#!/bin/python3

import argparse
import os
import re
import csv


def load_placeholder_values(placeholder_dir, placeholder, visited=None):
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


def process_effects_file(input_file, output_file, placeholder_dir, column_name, pattern, exact_line=None):
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
                    for row in rows:
                        effect = row[effect_col]
                        pattern_exists = check_pattern_existence(effect, pattern, placeholder_dir)
                        if pattern_exists and row[col_idx] != "True":
                            row[col_idx] = "True"
                else:
                    print(f"'{column_name}' not found in '{input_file}'. Adding new column.")
                    header.append(column_name)
                    col_idx = len(header) - 1
                    effect_col = header.index('EFFECTNAME') if 'EFFECTNAME' in header else 0
                    updated_rows = []
                    for row in rows:
                        effect = row[effect_col]
                        if len(row) <= col_idx:
                            row.extend([''] * (col_idx - len(row) + 1))
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
    Search for a substring in the effects and set the specified column to True.

    Args:
        input_file (str): Path to the input file (text or CSV).
        output_file (str): Path to the output CSV file.
        column_name (str): Name of the column to update.
        exact_line (str): Substring to match within the effects.
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
