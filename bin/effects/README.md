# Bin Directory README

## Overview
The `bin/effects` directory serves as the central location for generated effects, effect templates, and tools used for trimming the complete list of possible effects.

## Files

### `all_effect_templates.txt`
- **Purpose**: This file contains all of the templates for all possible effects.
- **Key Features**: The templates in these files use the placeholder values `<value>` in the template strings. These placeholders should match the files located in `../placeholders/`.
  
### `all_effects.txt`
- **Purpose**: This file contains all of the generated effects based on the `all_effect_templates.txt` file.
  
### `effects_with_placeholders.csv`
- **Purpose**: This file contains all of the generated effects based on the `all_effect_templates.txt` file with various categories added for sorting and other features.

## Scripts

### `find_malformed_lines.py`
- **Purpose**: This script parses a CSV file containing effect data for a card game, identifying effects that meet specific conditions: those where all level columns (e.g., LEVEL_1 to LEVEL_5) are "False" and those where both "UNIT" and "SPELL" columns are "False" (regardless of level columns). It also provides a total count of unique effects meeting either condition.
- **Key Features**: 
  - Identifies effects with all level columns set to "False".
  - Identifies effects with both "UNIT" and "SPELL" columns set to "False".
  - Dynamically detects level columns (e.g., LEVEL_1, LEVEL_2, etc.) in a case-insensitive manner.
  - Handles semicolon (`;`) delimited CSV files.
  - Provides a total count of unique effects meeting either condition, avoiding double-counting.
  - Includes error handling for missing files, missing columns, and other potential issues.
  - Outputs debug information (detected column names) for troubleshooting.
- **Usage**: 
  - Ensure your CSV file has headers including `EFFECTNAME`, `UNIT`, `SPELL`, and level columns (e.g., `LEVEL_1`, `LEVEL_2`, ..., `LEVEL_5`), with values as "True" or "False", and uses semicolons (`;`) as delimiters.
  - Update the `input_file` variable in the script to point to your CSV file (e.g., `input_file = 'your_data_file.csv'`).
  - Run the script using Python: `python find_malformed_lines.py`.
  - The script will output:
    - A list of effects where all level columns are "False".
    - A list of effects where both "UNIT" and "SPELL" are "False".
    - The total number of unique effects meeting either condition.
- **Dependencies**: 
  - Python 3.x
  - The `csv` module (part of Python's standard library, no external installation required)
