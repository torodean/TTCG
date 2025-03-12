#!/usr/bin/env python3

import argparse
import pandas as pd
import random
import sys

def parse_args():
    """
    Parse command-line arguments for the CSV filtering and pairing script.

    This function sets up an ArgumentParser to handle the input file path and column names
    specified via the -c flag. The input file defaults to a specific CSV if not provided,
    and at least one column must be specified for filtering.

    Returns:
        argparse.Namespace: An object containing the parsed arguments:
            - input_file (str): Path to the CSV file.
            - column (list of str): List of column names specified with -c.

    Example:
        >>> args = parse_args()  # With command: python script.py -c active -c enabled
        >>> args.input_file
        'effects/effects_with_placeholders.csv'
        >>> args.column
        ['active', 'enabled']
    """
    parser = argparse.ArgumentParser(
        description="Filter rows in a CSV file where specified columns contain 'True', "
                    "then select and print 10 random pairs of values from the first column."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="effects/effects_with_placeholders.csv",
        help="Path to the input CSV file to process. If not provided, defaults to "
             "'effects/effects_with_placeholders.csv'. The file should contain a header row "
             "with column names."
    )
    parser.add_argument(
        "-c",
        "--column",
        action="append",
        required=True,
        help="Name of a column in the CSV to filter on. Only rows where all specified "
             "columns equal 'True' (case-insensitive) are kept. This flag can be used "
             "multiple times (e.g., -c col1 -c col2) to filter on multiple columns."
    )
    return parser.parse_args()

def load_and_filter_csv(file_path, columns):
    """
    Load a CSV file and filter rows where all specified columns equal 'True'.

    This function reads the CSV into a pandas DataFrame, checks that the specified columns
    exist, and filters for rows where all given columns have the value 'True'. It then
    returns the values from the first column of the filtered rows.

    Args:
        file_path (str): Path to the CSV file to read.
        columns (list of str): List of column names to filter on.

    Returns:
        list: Values from the first column of rows where all specified columns are 'True'.

    Raises:
        SystemExit: If the file is not found, is empty, contains invalid data, or if specified
                    columns don’t exist in the CSV, or if no rows match the filter criteria.

    Example:
        For a CSV like:
        name,active,enabled
        Effect1,True,True
        Effect2,False,True
        Effect3,True,True
        >>> load_and_filter_csv('effects.csv', ['active', 'enabled'])
        ['Effect1', 'Effect3']
    """
    try:
        # Read CSV into a DataFrame, assuming first row is header
        df = pd.read_csv(file_path)
        
        # Check if all specified columns exist in the DataFrame
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            sys.exit(f"Error: Columns not found in CSV: {', '.join(missing_cols)}")
        
        # Filter rows where all specified columns are 'True'
        # Convert to string and lowercase to handle various True formats (e.g., TRUE, true)
        mask = True
        for col in columns:
            mask &= (df[col].astype(str).str.lower() == "true")
        filtered_df = df[mask]
        
        # If no rows match, exit with a helpful message
        if filtered_df.empty:
            sys.exit(f"Error: No rows found where all specified columns ({', '.join(columns)}) are 'True'")
        
        # Extract and return the first column values as a list
        return filtered_df.iloc[:, 0].tolist()
    
    except FileNotFoundError:
        sys.exit(f"Error: File '{file_path}' not found")
    except pd.errors.EmptyDataError:
        sys.exit(f"Error: File '{file_path}' is empty")
    except Exception as e:
        sys.exit(f"Error processing CSV: {str(e)}")

def get_random_pairs(values, num_pairs=10):
    """
    Generate a list of random pairs from the provided values.

    This function takes a list of values, shuffles them, and creates pairs. It returns up to
    `num_pairs` pairs (default 10), or fewer if there aren’t enough values. Each pair
    consists of two consecutive values from the shuffled list.

    Args:
        values (list): List of values to create pairs from (e.g., first column values).
        num_pairs (int, optional): Number of pairs to return. Defaults to 10.

    Returns:
        list of tuples: List of pairs, where each pair is a tuple of two values.

    Raises:
        SystemExit: If there are fewer than 2 values, as pairs cannot be formed.

    Example:
        >>> get_random_pairs(['A', 'B', 'C', 'D'], num_pairs=2)
        [('B', 'D'), ('A', 'C')]
    """
    if len(values) < 2:
        sys.exit("Error: Need at least 2 values to form pairs")
    
    # Calculate maximum possible pairs based on input length
    max_pairs = min(num_pairs, len(values) // 2)
    
    # Shuffle values randomly without modifying the original list
    shuffled = random.sample(values, len(values))
    
    # Create pairs from consecutive elements in the shuffled list
    pairs = [(shuffled[i], shuffled[i + 1]) for i in range(0, max_pairs * 2, 2)]
    
    # Return up to max_pairs pairs
    return pairs[:max_pairs]

def main():
    """
    Main function to orchestrate CSV filtering and random pair generation.

    This function ties together argument parsing, CSV loading/filtering, and pair generation.
    It prints 10 random pairs (or fewer if limited by data) from the first column of rows
    where all specified columns are 'True'.

    Exits with an error message if any step fails (e.g., file not found, no matching rows).
    """
    # Parse command-line arguments
    args = parse_args()
    input_file = args.input_file
    columns = args.column

    # Load CSV and filter for rows where specified columns are 'True'
    first_col_values = load_and_filter_csv(input_file, columns)
    
    # Generate 10 random pairs from the filtered first column values
    pairs = get_random_pairs(first_col_values)
    
    # Print the results in a readable format
    print(f"Found {len(first_col_values)} matching rows. Here are 10 random pairs from the first column:")
    for i, (val1, val2) in enumerate(pairs, 1):
        print(f"{i}. {val1} - {val2}")

if __name__ == "__main__":
    main()
