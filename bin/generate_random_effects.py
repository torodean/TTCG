#!/bin/python3

import argparse
import pandas as pd
import random
import sys
    

def load_and_filter_csv(file_path, columns):
    """
    Load a semicolon-delimited CSV file and filter rows where all specified columns equal 'True'.

    Args:
        file_path (str): Path to the CSV file to read.
        columns (list of str): List of column names to filter on.

    Returns:
        list: Values from the first column of rows where all specified columns are 'True'.

    Raises:
        SystemExit: If the file is not found, is empty, contains invalid data, or if specified
                    columns don’t exist in the CSV, or if no rows match the filter criteria.
    """
    try:
        # Read CSV with semicolon delimiter
        df = pd.read_csv(file_path, sep=';')  # Specify semicolon as delimiter
        
        # Check if all specified columns exist in the DataFrame
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            sys.exit(f"Error: Columns not found in CSV: {', '.join(missing_cols)}")
        
        # Filter rows where all specified columns are 'True'
        mask = True
        for col in columns:
            mask &= (df[col].astype(str).str.lower() == "true")
        filtered_df = df[mask]
        
        # If no rows match, exit with a helpful message
        if filtered_df.empty:
            sys.exit(f"Error: No rows found where all specified columns ({', '.join(columns)}) are 'True'")
        
        print(f"Filtering on: {columns}")
        print(f"Filtered rows:\n{filtered_df}")

        # Extract and return the first column values as a list
        return filtered_df.iloc[:, 0].tolist()
    
    except FileNotFoundError:
        sys.exit(f"Error: File '{file_path}' not found")
    except pd.errors.EmptyDataError:
        sys.exit(f"Error: File '{file_path}' is empty")
    except pd.errors.ParserError as e:
        sys.exit(f"Error: CSV parsing failed. Check file format and delimiter. Details: {str(e)}")
    except Exception as e:
        sys.exit(f"Error processing CSV: {str(e)}")
        

def get_random_effect(values, search_strings=None):
    """
    Generate one random effect from the provided values, optionally filtered by search strings.

    This function takes a list of values and returns a single randomly selected value. If
    search_strings is provided, it filters the values to those containing at least one of
    the specified strings (case-insensitive) before selecting.

    Args:
        values (list): List of values to select from (e.g., effect strings).
        search_strings (list of str, optional): List of strings to search for within the values.
            If None, no filtering is applied. Defaults to None.

    Returns:
        str: A single randomly selected value from the (filtered) list.

    Raises:
        SystemExit: If the input list is empty or if no values match the search strings.

    Example:
        >>> get_random_effect(['Draw 1 card', 'Gain 2 points', 'Lose 1 life'])
        'Gain 2 points'
        >>> get_random_effect(['Draw 1 card', 'Gain 2 points', 'Lose 1 life'], ['draw', 'gain'])
        'Draw 1 card'  # Only 'Draw 1 card' and 'Gain 2 points' match, one is chosen
    """
    if not values:
        sys.exit("Error: Need at least one value to generate an effect")

    # If no search strings provided, return a random value from the full list
    if search_strings is None:
        return random.choice(values)

    # Filter values containing at least one search string (case-insensitive)
    filtered_values = [
        value for value in values
        if any(search.lower() in value.lower() for search in search_strings)
    ]

    # Check if any values match the search criteria
    if not filtered_values:
        sys.exit(f"Error: No effects found matching any of {search_strings}")

    # Return a random value from the filtered list
    return random.choice(filtered_values)


def get_random_pairs(values, num_pairs=10):
    """
    Generate a list of random effect pairs by selecting individual effects.

    This function creates pairs of effects by calling `get_random_effect` twice for each pair.
    It returns up to `num_pairs` pairs (default 10), or fewer if there aren’t enough unique values.
    Each pair is a tuple of two randomly selected effects.

    Args:
        values (list): List of values to create pairs from (e.g., effect strings).
        num_pairs (int, optional): Number of pairs to return. Defaults to 10.

    Returns:
        list of tuples: List of pairs, where each pair is a tuple of two effect strings.

    Raises:
        SystemExit: If there are fewer than 2 values, as pairs cannot be formed.

    Example:
        >>> get_random_pairs(['A', 'B', 'C', 'D'], num_pairs=2)
        [('B', 'A'), ('D', 'C')]
    """
    if len(values) < 2:
        sys.exit("Error: Need at least 2 values to form pairs")

    # Calculate maximum possible pairs based on input length and desired number
    max_pairs = min(num_pairs, len(values) // 2)

    # Generate pairs by calling get_random_effect twice for each pair
    pairs = []
    for _ in range(max_pairs):
        effect1 = get_random_effect(values)
        # Ensure effect2 is different from effect1 if possible
        effect2 = get_random_effect([v for v in values if v != effect1]) if len(values) > 1 else effect1
        pairs.append((effect1, effect2))

    return pairs


def main():
    """
    Main function to orchestrate CSV filtering and random pair generation.

    This function ties together argument parsing, CSV loading/filtering, and pair generation.
    It prints 10 random pairs (or fewer if limited by data) from the first column of rows
    where all specified columns are 'True'.

    Exits with an error message if any step fails (e.g., file not found, no matching rows).
    """
    parser = argparse.ArgumentParser(
        description="Filter rows in a CSV file where specified columns contain 'True', "
                    "then select and print 10 random pairs of values from the first column."
    )
    parser.add_argument(
        "-i",
        "--input_file",
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
    parser.add_argument(
        "-p",
        "--pairs",
        type=int,
        default=10,
        help="Number of random pairs to generate (default: 10)."
    )
    
    # Parse command-line arguments
    args = parser.parse_args()
    input_file = args.input_file
    columns = args.column

    # Load CSV and filter for rows where specified columns are 'True'
    first_col_values = load_and_filter_csv(input_file, columns)
    
    # Generate 10 random pairs from the filtered first column values
    pairs = get_random_pairs(first_col_values, num_pairs=args.pairs)
    
    # Print the results in a readable format
    print(f"Found {len(first_col_values)} matching rows. Here are 10 random pairs from the first column:")
    for i, (val1, val2) in enumerate(pairs, 1):
        print(f"{i}. {val1} - {val2}")

if __name__ == "__main__":
    main()
