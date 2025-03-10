# Bin Directory README

## Overview
The `bin` directory serves as the central hub for executable scripts used in the effect generation and management workflow. These scripts, primarily written in Python 3 and Bash, automate the creation, annotation, sorting, and organization of effect descriptions (e.g., for game design or simulations). The tools interact with the `placeholders` directory (for placeholder values and configurations) and the `effects` directory (for effect templates and outputs), forming a cohesive system for processing effect-related data.

## Scripts

### `add_csv_field.py`
- **Purpose**: Processes text or CSV files containing effects, adding or updating a custom column to indicate whether each effect matches a specified pattern (with placeholders) or exact substring.
- **Key Features**: Supports placeholder expansion, handles both text and CSV inputs, and outputs semicolon-delimited CSV files.
- **Usage**: `python3 add_csv_field.py -i INPUT -o OUTPUT -c COLUMN [-t TEXT | -e EXACT]`
- **Dependencies**: Relies on placeholder files in `../placeholders/`.

### `alphabetize_file.py`
- **Purpose**: Reads lines from a text file, sorts them alphabetically, and writes the result to an output file.
- **Key Features**: Simple sorting utility, ignores empty lines, and handles basic file errors.
- **Usage**: `python3 alphabetize_file.py [-i INPUT] [-o OUTPUT]`
- **Dependencies**: None beyond Python 3.

### `create_effect_combinations.py`
- **Purpose**: Generates all possible combinations of effect templates by replacing placeholders with values, with configurable filtering and phrase replacement.
- **Key Features**: Supports nested placeholders and offsets (e.g., `<rank+1>`), filters unwanted combinations, replaces phrases for refinement, and alphabetizes output.
- **Usage**: `python3 create_effect_combinations.py [-s SENTENCE | -f FILE] [-c CONFIG] [-r REPLACEMENTS]`
- **Configuration Files**: Uses `../placeholders/combinations_to_remove.txt` (phrases to filter) and `../placeholders/phrase_replacements.txt` (replacements), both supporting `#` comments.
- **Dependencies**: Relies on placeholder files in `../placeholders/` and effect templates in `../effects/`.

### `generate_and_order_effects.sh`
- **Purpose**: Orchestrates the generation and categorization of effects, coordinating other scripts to produce and annotate a comprehensive effect list.
- **Key Features**: Cleans up old files, generates effects, and adds metadata columns (e.g., UNIT, SPELL) based on patterns or exact matches.
- **Usage**: `./generate_and_order_effects.sh`
- **Dependencies**: Requires `create_effect_combinations.py`, `add_csv_field.py`, and files in `../effects/` and `../placeholders/`.

### Other Scripts
- Additional scripts in this directory may support related tasks (e.g., data validation, conversion).

## Related Directories

### `placeholders/`
- **Purpose**: Contains all placeholder files (e.g., `type.txt`, `number.txt`) and configuration files for `create_effect_combinations.py` (`combinations_to_remove.txt`, `phrase_replacements.txt`).
- **Contents**: 
  - Placeholder files provide values for substitution/matching (e.g., `number.txt`: `1`, `2`, `3`).
  - Configuration files customize filtering and refinement (see `placeholders/README.md` for details).
- **Usage**: Referenced by scripts via the `-p/--placeholder_dir` argument (defaults to `placeholders`).

### `effects/`
- **Purpose**: Houses effect-related data, including templates, generated effect lists, and CSV outputs.
- **Contents**:
  - **Templates**: Files like `all_effect_templates.txt` with placeholder-based effect patterns (e.g., "Draw <number> cards").
  - **Effect Lists**: Generated outputs like `all_effects.txt` from `create_effect_combinations.py`.
  - **CSVs**: Annotated files like `effects_with_placeholders.csv` from `add_csv_field.py` or `generate_and_order_effects.sh`.
- **Usage**: Scripts read from and write to this directory (e.g., `-f` and `-o` arguments).

## Usage Notes
- **Execution**: Run scripts from the `bin` directory, ensuring relative paths to `placeholders` and `effects` are correct (e.g., `../placeholders/`).
- **Customization**: Modify files in `placeholders` and `effects` to adjust script behavior without altering code.
- **Dependencies**: Ensure Python 3 and Bash are installed. Scripts assume a Unix-like environment.
