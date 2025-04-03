# Bin Directory README



## Overview
The `bin` directory serves as the central hub for executable scripts used in the effect generation and management workflow. These scripts, primarily written in Python 3 and Bash, automate the creation, annotation, sorting, and organization of effect descriptions (e.g., for game design or simulations). The tools interact with the `placeholders` directory (for placeholder values and configurations) and the `effects` directory (for effect templates and outputs), forming a cohesive system for processing effect-related data.





## Scripts




### `add_csv_field.py`
- **Purpose**: Processes text or semicolon-delimited CSV files containing effect descriptions, adding or updating a custom column to indicate matches against a specified pattern (with placeholders) or exact substring, or deleting lines matching a string.
- **Key Features**:
  - Supports placeholder expansion (e.g., `<number>`, `<type>`) using values from text files in a placeholder directory.
  - Handles both plain text inputs (converted to CSV) and existing CSV files (updates or adds columns).
  - Outputs results as semicolon-delimited CSV files with columns like `EFFECTNAME` and the user-specified column.
  - Options for pattern matching, exact substring matching, or line deletion.
  - Conditional matching based on an existing column’s value (via `-m/--match_column`).- **Usage**: `python3 add_csv_field.py -i INPUT -o OUTPUT -c COLUMN [-t TEXT | -e EXACT]`
- **Usage**: 
  - `python3 add_csv_field.py -i INPUT -o OUTPUT -c COLUMN [-p PLACEHOLDER_DIR] [-t TEXT | -e EXACT | -d DELETE] [-m MATCH_COLUMN]`
  - `-i/--input`: Input file (text or CSV, defaults to `effects/effects_with_placeholders.csv`).
  - `-o/--output`: Output CSV file (defaults to `effects/effects_with_placeholders.csv`).
  - `-c/--column`: Name of the column to add or update (required, e.g., `HasDraw`).
  - `-p/--placeholder_dir`: Directory with placeholder files (defaults to `placeholders`).
  - `-t/--text`: Pattern to match, supporting placeholders (e.g., `Draw <number> cards`).
  - `-e/--exact`: Exact substring to match (e.g., `Draw two`).
  - `-d/--delete`: Exact string to match for deleting lines (e.g., `Discard`).
  - `-m/--match_column`: Existing column that must be `True` for matching (optional, e.g., `UNIT`).
**Dependencies**:
- Python 3 standard libraries (`argparse`, `os`, `re`, `csv`).
- Custom module `ttcg_tools` for placeholder handling and command string generation.
- Placeholder text files in the specified directory (e.g., `placeholders/number.txt`).
**Notes**:
- Exactly one of `-t`, `-e`, or `-d` must be provided.
- For CSV inputs, `-e` requires the column to pre-exist, while `-t` can create it.
- Errors (e.g., missing files, invalid columns) are reported with descriptive messages.





### `alphabetize_file.py`
- **Purpose**: Reads lines from a text file, sorts them alphabetically, and writes the result to an output file.
- **Key Features**: Simple sorting utility, ignores empty lines, and handles basic file errors.
- **Usage**: `python3 alphabetize_file.py [-i INPUT] [-o OUTPUT]`
- **Dependencies**: None beyond Python 3.





### `flip_image.py`
- **Purpose**: Flips an image horizontally and saves the result, optionally overwriting the original file.
- **Key Features**: Horizontal image flipping, optional output path, error handling for image processing.
- **Usage**: `python3 flip_image.py INPUT_FILE [-o OUTPUT]`
- **Dependencies**: Pillow (PIL) library for image processing.





### `create_effect_combinations.py`
- **Purpose**: Generates all possible combinations of effect templates by replacing placeholders with values from a directory, with options for filtering, phrase replacement, deduplication, and alphabetization.
- **Key Features**:
  - Expands placeholders (e.g., `<number>`, `<type>`) in a single sentence or file of sentences using values from placeholder files.
  - Removes duplicates, filters out unwanted combinations based on a config file, and applies phrase replacements (e.g., for grammar fixes).
  - Optionally fixes plurality (e.g., "one X cards" → "one X card") and alphabetizes the output.
  - Supports test mode (output to terminal only) and verbose logging.
  - Includes a deduplication-only mode for existing files via `-d/--dedupe`.
- **Usage**: `python3 create_effect_combinations.py [-s SENTENCE | -f FILE] [-p PLACEHOLDER_DIR] [-o OUTPUT_FILE] [-c CONFIG] [-r REPLACEMENTS] [-t] [-v] [-d [FILE]]`
  - `-s/--sentence`: Single sentence with placeholders (e.g., `Draw <number> cards`).
  - `-f/--file`: File of sentences (defaults to `effects/all_effect_templates.txt` if no file specified).
  - `-p/--placeholder_dir`: Directory with placeholder files (defaults to `placeholders`).
  - `-o/--output_file`: Output file for combinations (defaults to `effects/all_effects.txt`).
  - `-c/--combinations_to_remove`: Config file with phrases to filter (defaults to `placeholders/combinations_to_remove.txt`).
  - `-r/--replacements_file`: Config file with phrase replacements (format: `old: new`, defaults to `placeholders/phrase_replacements.txt`).
  - `-t/--test_mode`: Output to terminal only, no file write (default: `False`).
  - `-v/--verbose`: Enable detailed output (default: `False`).
  - `-d/--dedupe`: Deduplicate a file and exit (defaults to `effects/all_effects.txt` if no file given).
**Configuration Files**:
- `placeholders/combinations_to_remove.txt`: Phrases to exclude from output (lines ignored if empty or starting with `#`).
- `placeholders/phrase_replacements.txt`: Phrase replacements (format: `old phrase: new phrase`, comments with `#`).
**Dependencies**:
- Python 3 standard libraries (`re`, `argparse`).
- Custom module `ttcg_tools` for `generate_combinations` and `get_command_string`.
- Placeholder text files in the specified directory (e.g., `placeholders/number.txt`).
**Notes**:
- Exactly one of `-s/--sentence` or `-f/--file` must be provided.
- Output is appended to the file unless in test mode or deduplication mode.
- Errors (e.g., missing files) are handled with descriptive messages.
  
  
  
  
  
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
  
  
  
  
  
### `parse_image_files.py`
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
  
  
  
  
  
### `plot_type_occurances.py`
- **Purpose**: Analyzes and visualizes card data from a TTCG-format CSV file, generating plots to show distributions of types, subtypes, and effect mentions, aiding in card design balance and identification of underrepresented categories.
- **Key Features**: Produces multiple bar plots including type counts, subtype counts, effect mentions, and per-type subtype mentions in effects; optional 3D plot (still a work in progress) showing type vs. type/subtype effect interactions with color-coded frequency; supports comma-separated subtypes in the `SUBTYPES` column; uses `matplotlib` for visualization and `numpy` for 3D plotting calculations.
- **Usage**: `python3 plot_type_occurances.py [--plot-3d]`
- **Input**: Reads card data from a CSV file specified by `DEFAULT_CARD_LIST_FILE` in `ttcg_constants` (e.g., a semicolon-delimited file with columns like `TYPE`, `SUBTYPES`, `EFFECT1`, `EFFECT2`); optional `--plot-3d` flag to generate the 3D plot.
- **Dependencies**: Requires `matplotlib` (`pip install matplotlib`) and `numpy` (`pip install numpy`) for plotting and array operations; uses custom `ttcg_tools` for `output_text` logging and `ttcg_constants` for `TYPE_LIST`, `SUBTYPES_LIST`, and `DEFAULT_CARD_LIST_FILE`.
- **Output**: Saves plots to the `card_list/` directory:
  - `type_counts.png`: Bar plot of card counts by type.
  - `subtype_counts.png`: Bar plot of card counts by subtype (multi-subtype cards count once per subtype).
  - `effect_mentions.png`: Bar plot of cards mentioning each type/subtype in effects.
  - `<type>_subtype_mentions.png`: One bar plot per type (e.g., `fire_subtype_mentions.png`) showing subtype mentions in effects.
  - `type_effect_3d.png` (if `--plot-3d`): 3D bar plot of type vs. type/subtype effect frequencies with `viridis` colormap.
  - Console output of counts for types, subtypes, and effect mentions via `output_text`.
  
  
  
  
  
## `regen_serial_numbers.py`
- **Purpose**: Reads a card database file, regenerates serial numbers for each card using the `generate_serial_number` method from `card_maker_ui`, and saves the updated data to a new file.  
- **Key Features**:  
  - Parses a CSV file containing card data.  
  - Uses `generate_serial_number` from `card_maker_ui` to generate new serials.  
  - Ensures original data structure is maintained while updating serial numbers.  
  - Writes updated data to a new file to prevent overwriting the original.  
- **Usage**:  
  - `python3 regenerate_serials.py [--input_file INPUT_FILE]`
    - `--input_file`: Path to the card database file (defaults to `DEFAULT_CARD_LIST_FILE` from `ttcg_constants`)
- **Dependencies**:
  - Requires `argparse` (for command-line arguments), `csv` (for file processing), and `card_maker_ui` (for serial number generation and preprocessing).
- **Output**: 
  - Creates a new CSV file (`*_updated.csv`) with regenerated serial numbers.
  - Prints the output file path to the console.





### `ttcg_tools.py`
- **Purpose**: Provides a collection of shared utility functions and tools used across multiple TTCG-related scripts to streamline common tasks and ensure consistency.
- **Key Features**: Centralizes reusable code for tasks such as data processing, file handling, and configuration management, reducing duplication across scripts.
- **Usage**: Import into other scripts with `import ttcg_tools` or `from ttcg_tools import <function>`; specific functions depend on the current implementation.
- **Notes**: Designed as a dynamic library, so its contents evolve with the needs of other scripts; check the source for the latest available utilities.





### `ttcg_tools.py`
- **Purpose**: Provides a collection of shared constants and variables to be used consistently across the TTCG project.
- **Key Features**: Centralizes reusable constants.
- **Usage**: Import into other scripts with `import ttcg_constants` or `from ttcg_constants import <variable>`; specific variable depend on the current implementation.





### Other Scripts
- Additional scripts in this directory may support related tasks (e.g., data validation, conversion).





## Related Directories




### `card_list/`
- **Purpose**: Stores the main `card_list.csv` filr for storing created cards and other files related to this list (such as statistical graphs and card effect analysis).
- **Contents**: One `card_list.csv` file as well as plots related to this file.




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



### `effect_style_text/`
- **Purpose**: Stores text files defining patterns for identifying card effect styles (e.g., "continuous," "equip") used by `deduce_effect_style_from_effect_text`.
- **Contents**: One `.txt` file per style (e.g., `overload.txt`) with unique phrases (e.g., "discard one <typeslevels> card").
- **Usage**: Read by scripts to assign styles to effect text; path set via `EFFECT_STYLE_TEXT_FOLDER` variable. See `effect_style_text/README.md` for details.



## Usage Notes
- **Execution**: Run scripts from the `bin` directory, ensuring relative paths to `placeholders` and `effects` are correct (e.g., `../placeholders/`).
- **Customization**: Modify files in `placeholders`, `effect_style_text` and `effects` to adjust script behavior without altering code.
- **Dependencies**: Ensure Python 3 and Bash are installed. Scripts assume a Unix-like environment.
