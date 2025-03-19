#!/bin/python3

import csv

def find_all_false_levels(input_file):
    """
    Parse a CSV file containing effect data and identify effects based on specific conditions.

    Args:
        input_file (str): The path to the CSV file to be parsed. The file should have
                         headers including EffectName, Unit, Spell, and level columns
                         (e.g., LEVEL_1, LEVEL_2, ..., LEVEL_5) with values as 'True' or 'False'.
                         The file uses semicolons (;) as delimiters.

    Returns:
        None: Prints the list of effect names where:
              1. All level columns (e.g., LEVEL_1 to LEVEL_5) are 'False', or
              2. Both Unit and Spell columns are 'False' (regardless of level columns).
              Also prints the total number of unique effects meeting either condition.
              If no such effects are found for either condition, prints a corresponding message.
              If the file cannot be read or columns are missing, prints an error message.
    """
    # Lists to store effects for each condition
    all_false_levels = []
    both_false_unit_spell = []
    
    try:
        # Read the CSV file with semicolon as delimiter
        with open(input_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            # Debug: Print all detected column names
            print("Detected column names:", reader.fieldnames)
            
            # Check if required columns exist
            required_columns = {'EFFECTNAME', 'UNIT', 'SPELL'}  # Updated to match case
            level_columns = [col.strip() for col in reader.fieldnames if col.strip().upper().startswith('LEVEL')]
            if not level_columns:
                print("Error: No level columns (e.g., LEVEL_1, LEVEL_2, etc.) found in the file.")
                return
            if not all(col in reader.fieldnames for col in required_columns):
                print("Error: Missing required columns (EFFECTNAME, UNIT, or SPELL).")
                return
            
            # Iterate through each row
            for row in reader:
                # Extract level columns dynamically
                levels = [row[col] for col in level_columns]
                
                # Check if all levels are False
                if all(level.lower() == 'false' for level in levels):
                    all_false_levels.append(row['EFFECTNAME'])  # Updated to match case
                
                # Check if both Unit and Spell are False
                if row['UNIT'].lower() == 'false' and row['SPELL'].lower() == 'false':
                    both_false_unit_spell.append(row['EFFECTNAME'])  # Updated to match case
    
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return
    
    # Output the results for all false levels
    if all_false_levels:
        print("\nEffects with all levels (e.g., LEVEL_1 to LEVEL_5) set to False:")
        for effect in all_false_levels:
            print(f"- {effect}")
    else:
        print("\nNo effects found with all levels set to False.")
    
    # Output the results for both Unit and Spell being False
    if both_false_unit_spell:
        print("\nEffects with both Unit and Spell set to False (regardless of levels):")
        for effect in both_false_unit_spell:
            print(f"- {effect}")
    else:
        print("\nNo effects found with both Unit and Spell set to False.")
    
    # Calculate and print the total count of unique effects
    # Use a set to avoid double-counting effects that appear in both lists
    unique_effects = set(all_false_levels).union(set(both_false_unit_spell))
    total_count = len(unique_effects)
    print(f"\nTotal number of unique effects meeting malformed condition(s): {total_count}")

# Specify the input file name
input_file = 'effects_with_placeholders.csv' 
find_all_false_levels(input_file)
