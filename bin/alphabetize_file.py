#!/bin/python3

import argparse
import os

def alphabetize_file(input_file, output_file):
    """
    Read lines from an input file, sort them alphabetically, and write to an output file.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to the output file.
    """
    try:
        # Read all lines from the input file
        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Sort lines alphabetically
        lines.sort()
        
        # Write sorted lines to the output file
        with open(output_file, 'w') as f:
            for line in lines:
                f.write(f"{line}\n")
        
        print(f"Alphabetized '{input_file}' into '{output_file}'.")
    
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
    
    args = parser.parse_args()
    alphabetize_file(args.input, args.output)

if __name__ == "__main__":
    main()