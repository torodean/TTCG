#!/bin/python3

import argparse
import os

def alphabetize_file(input_file, output_file, has_headers=False):
    """
    Read lines from an input file, sort them alphabetically, and write to an output file.
    If has_headers is True, preserves the first line as a header.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
        has_headers (bool): If True, treat the first line as a header and keep it at the top.
    """
    try:
        # Read all lines from the input file
        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            print(f"Warning: Input file '{input_file}' is empty.")
            with open(output_file, 'w') as f:
                pass  # Create empty output file
            return

        if has_headers and len(lines) > 1:
            # Separate header (first line) from data
            header = lines[0]
            data_lines = lines[1:]
            # Sort only the data lines
            data_lines.sort()
            # Combine header with sorted data
            sorted_lines = [header] + data_lines
        else:
            # No headers or only one line; sort all lines
            lines.sort()
            sorted_lines = lines
        
        # Write sorted lines to the output file
        with open(output_file, 'w') as f:
            for line in sorted_lines:
                f.write(f"{line}\n")
        
        print(f"Alphabetized '{input_file}' into '{output_file}'{' with header preserved' if has_headers else ''}.")
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Alphabetize lines in a file.")
    parser.add_argument('-i', '--input', default='input.txt',
                        help="Input file to alphabetize (defaults to 'input.txt').")
    parser.add_argument('-o', '--output', default='output.txt',
                        help="Output file for sorted lines (defaults to 'output.txt').")
    parser.add_argument('-H', '--headers', action='store_true',
                        help="Preserve the first line as a header and sort remaining lines only.")
    
    args = parser.parse_args()
    alphabetize_file(args.input, args.output, args.headers)

if __name__ == "__main__":
    main()
