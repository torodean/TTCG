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

### `filter_effects_and_pair.py`
- **Purpose**: Filters rows from a CSV file based on specified columns containing "True" and generates random pairs of values from the first column.
- **Key Features**: Accepts multiple column filters via `-c`, extracts rows where all specified columns are "True" (case-insensitive), selects 10 random pairs from the first column, and handles errors gracefully with informative messages.
- **Usage**: `python3 filter_effects_and_pair.py [INPUT_FILE] -c COLUMN [-c COLUMN ...]`
- **Input**: Defaults to `effects/effects_with_placeholders.csv` if no input file is provided; expects a CSV with a header row.
- **Dependencies**: Requires `pandas` for CSV processing (`pip install pandas`); no additional configuration files needed.
- **Output**: Prints 10 random pairs (or fewer if limited by data) from the first column of filtered rows, numbered for clarity.
  
### `generate_and_order_effects.sh`
- **Purpose**: Orchestrates the generation and categorization of effects, coordinating other scripts to produce and annotate a comprehensive effect list.
- **Key Features**: Cleans up old files, generates effects, and adds metadata columns (e.g., UNIT, SPELL) based on patterns or exact matches.
- **Usage**: `./generate_and_order_effects.sh`
- **Dependencies**: Requires `create_effect_combinations.py`, `add_csv_field.py`, and files in `../effects/` and `../placeholders/`.

### `create_card.py`
- **Purpose**: Generates a trading card image in TTCG format with customizable text, type, level, effects, and stats, overlaying them on a type-specific background and level-specific star overlay.
- **Key Features**: Creates a 750x1050 pixel card (2.5" x 3.5" at 300 DPI) with a base image based on card type and a level-specific star overlay; supports single-line text for name, subtype, attack, and defense (with centering for stats), and wrapped text for two effects; uses predefined layout coordinates.
- **Usage**: `python3 create_card.py [-l {1,2,3,4,5}] [-t TYPE] [-n NAME] [-s SUBTYPE [SUBTYPE ...]] [-1 EFFECT1] [-2 EFFECT2] [-a ATTACK] [-d DEFENSE] [-i IMAGE] [-o OUTPUT] [--serial SERIAL] [-T TRANSPARENCY]`
- **Input**: Command-line arguments for card details; no defaults for type or level; attack and defense optional (no random generation in this version); expects PNG images in `../images/card pngs/` (e.g., `fire.png`, `1 star.png`).
- **Dependencies**: Requires `Pillow` for image processing (`pip install Pillow`); assumes helper functions like `create_base_card`, `draw_single_line_text`, and `draw_wrapped_text`.
- **Output**: Saves a PNG card image to `<output_folder>/<type>_<name>.png` (spaces replaced with underscores), e.g., `ttcg_card_Card_Name.png`; defaults to `../images/generated_cards/` if `-o` is not specified.

### `card_maker_ui.py`
- **Purpose**: Provides a Tkinter-based GUI for creating trading cards in TTCG format, allowing real-time preview, effect generation, and data saving, with customizable attributes like type, level, name, subtypes, stats, effects, and image.
- **Key Features**: Interactive UI with dropdowns (type, level), checkboxes (subtypes), text entries (name, stats, effects), and buttons for randomization, reset, and saving; generates a 400x580 pixel preview (resized from 750x1050) using `create_card`; supports random ATK/DEF based on level and effect generation from a CSV file; centralizes widget access via a global `WIDGETS` dictionary.
- **Usage**: `python3 card_maker_ui.py [-i INPUT_FILE]`
- **Input**: Optional command-line argument `-i/--input_file` for the effects CSV (defaults to `effects/effects_with_placeholders.csv`); GUI inputs for card details with defaults (e.g., "Fire" type, level 1, "Unnamed", 0 ATK/DEF).
- **Dependencies**: Requires `Pillow` (`pip install Pillow`) for image processing, `tkinter` (standard library), and custom modules `create_card.py` and `generate_random_effects.py`; assumes effect CSV and image assets in `../images/card pngs/`.
- **Output**: Displays a live card preview in the GUI; saves card data to console (placeholder for spreadsheet implementation); generated card images stored temporarily via `tempfile`.

### `generate_random_effects.py`
- **Purpose**: Filters a CSV file to find rows where specified columns are "True", then generates and prints random pairs from the first column of the filtered rows.
- **Key Features**: 
  - Filters CSV rows based on multiple columns being "True" (case-insensitive).
  - Generates up to a specified number of random pairs (default: 10) from the first column.
  - Handles semicolon-delimited CSV files.
  - Includes error handling for file issues, missing columns, and insufficient data.
- **Usage**: 
  - Run the script with: `python random_pairs.py [-c COLUMN] [-i INPUT_FILE]`.
  - Default input file: `effects/effects_with_placeholders.csv`.
  - Use `-p` to specify the number of pairs (e.g., `-p 5`).
- **Dependencies**: 
  - Python 3.x
  - `pandas` (for CSV processing)
  - `argparse`, `random`, `sys` (standard library)
  
# `parse_image_files.py`
- **Purpose**: Displays images from a specified folder one at a time with a transparent overlay image (`fire.png`) on top, allowing users to:
  - Mark images as "needs fixed" by moving them to a designated folder (e.g., for images where the card name isn’t at the top or doesn’t display correctly).
  - Categorize images into "units" or "spells" subfolders by type (earth, fire, water, air, nature, electric, light, dark).
- **Key Features**: 
  - Recursively loads all images (PNG, JPG, JPEG, GIF, BMP) from a source folder (`../images`) and its subfolders, excluding specified folders and optionally the top-level folder.
  - Resizes each source image to match the overlay’s width while preserving aspect ratio, padding with transparency if shorter or cropping if taller to match the overlay’s height.
  - Composites the overlay image (`fire.png`) at its actual size on top using alpha compositing for proper transparency handling.
  - Provides GUI elements:
    - "Next" button: Advances to the next image.
    - "Needs Fixed" button: Moves the current image to `../images/needs_fixed/`.
    - Side panel with two columns ("Units" and "Spells"), each containing buttons for types (e.g., "Earth", "Fire"). Clicking a type button moves the image to `../images/units/<type>/` or `../images/spells/<type>/`.
  - Creates all destination directories (`needs_fixed`, `units/<type>`, `spells/<type>`) at startup to avoid per-image checks.
  - Excludes specified folders (e.g., `images/needs_fixed`, `images/card pngs`) from image loading.
  - Includes error handling for missing files, no images found, and file movement issues.
- **Usage**: 
  - Run the script with: `python parse_image_files.py`.
  - Source folder: `../images/` (relative to script location).
  - Overlay image: `../images/card pngs/fire.png` (must have transparency).
  - Destination folders:
    - "Needs fixed": `../images/needs_fixed/` (created if not present).
    - Units: `../images/units/<type>/` (e.g., `../images/units/fire/`, created if not present).
    - Spells: `../images/spells/<type>/` (e.g., `../images/spells/water/`, created if not present).
- **Dependencies**: 
  - Python 3.x
  - `Pillow` (for image processing, install with `pip install pillow`)
  - `tkinter` (standard library, for GUI)
  
### `ttcg_tools.py`
- **Purpose**: Provides a collection of shared utility functions and tools used across multiple TTCG-related scripts to streamline common tasks and ensure consistency.
- **Key Features**: Centralizes reusable code for tasks such as data processing, file handling, and configuration management, reducing duplication across scripts.
- **Usage**: Import into other scripts with `import ttcg_tools` or `from ttcg_tools import <function>`; specific functions depend on the current implementation.
- **Notes**: Designed as a dynamic library, so its contents evolve with the needs of other scripts; check the source for the latest available utilities.

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
