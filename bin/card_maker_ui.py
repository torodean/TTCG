#!/usr/bin/env python3

import argparse
import tkinter as tk
import random
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
import threading

#import sv_ttk

# Used for randomly generating effects.
from generate_random_effects import load_and_filter_csv
from generate_random_effects import get_random_effect

# Inports from ttcg_tools
from ttcg_tools import output_text
from ttcg_tools import check_line_in_file
from ttcg_tools import get_relative_path
from ttcg_tools import rename_file
from ttcg_tools import deduce_effect_style_from_effect_text
from ttcg_tools import get_sequence_combinations, ALL_SEQUENCE_BUFFER
from ttcg_tools import get_combination_id
from ttcg_tools import get_number_id
from ttcg_tools import get_index_in_baseN
from ttcg_tools import sn_in_list
from ttcg_tools import save_sn_to_list

# Import needed constants from ttcg_constants
from ttcg_constants import TYPE_LIST
from ttcg_constants import CARD_LIST_HEADER
from ttcg_constants import SUBTYPES_LIST
from ttcg_constants import VALID_IMAGE_EXTENSIONS
from ttcg_constants import VALID_OVERLAY_STYLES
from ttcg_constants import VALID_TRANSLUCENT_VALUES
from ttcg_constants import DEFAULT_CARD_LIST_FILE
from ttcg_constants import ALL_TYPES_LIST_LOWER
from ttcg_constants import DEFAULT_SERIAL_LIST_FILE
from ttcg_constants import EXTRA_EFFECT_KEYWORDS
from ttcg_constants import CHARACTERS

# Used for flipping and correcting images.
from flip_image import flip_image

# Used for generating card preview.
from create_card import create_card
import os
import tempfile
from PIL import Image, ImageTk

# For SN generation
import hashlib

# Used for card data output.
import csv


# Global var to determine when preview should be generated vs not.
SKIP_PREVIEW = False
LAST_UPDATE_CARD_DATA = None

# Get script's directory (useful for relative paths)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
output_text(f"SCRIPT_DIR set to: {SCRIPT_DIR}", "program")

# The number of effect boxes in the UI. Used in various places so it's a global var here.
NUMBER_OF_EFFECT_BOXES = 50

# For global threading.
processing_thread = None

# Store sthe load_mode globally. This is set to true with the -L flag.
LOAD_CARD_MODE = False
    

def get_next_image(current_path):
    """
    Get the next image file in a directory or the first image if a directory is provided.
    
    Args:
        current_path (str or Path): File path to an image or directory path.
            If a file path, returns the next image in the directory.
            If a directory path, returns the first image in the directory.
    
    Returns:
        str: Full path to the next image file (or first file if at the end),
             or None if no image files are found or path is invalid.
    
    Notes:
        - Supported image extensions: .jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp
        - Files are sorted alphabetically
        - If input is an image file and it's the last in the directory,
          returns the first image file
        - Case-insensitive extension matching
    """
    # Define common image extensions
    image_extensions = VALID_IMAGE_EXTENSIONS
    
    # Convert input to Path object
    path = Path(current_path)
    
    # If it's a directory, return the first image file
    if path.is_dir():
        for file in sorted(os.listdir(path)):
            file_path = path / file
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                return str(file_path)
        return None  # Return None if no image files found
    
    # If it's a file, get its directory and find the next image
    if path.is_file():
        directory = path.parent
        files = []
        
        # Collect all image files in the directory
        for file in sorted(os.listdir(directory)):
            file_path = directory / file
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                files.append(file_path)
        
        if not files:
            return None  # No image files in directory
        
        # Find current file's position
        try:
            current_index = files.index(path)
            # Return next file, or first file if at the end
            next_index = (current_index + 1) % len(files)
            return str(files[next_index])
        except ValueError:
            # If current file isn't an image, return first image
            return str(files[0]) if files else None
    
    return None  # Return None if path doesn't exist
    
    
def get_card_data(print_data=False):
    """
    Collect card data from GUI widgets into a dictionary.

    This function gathers input from various Tkinter widgets in the card creator UI and
    returns a dictionary containing the card's attributes. Empty or invalid inputs are
    replaced with default values to ensure consistent output.

    Args:
        print_data (bool): Set true to print the card data.

    Returns:
        dict: A dictionary with the following keys and values:
            - "type" (str): Card type (defaults to "Unknown" if empty).
            - "level" (int): Card level (defaults to 1 if empty or invalid).
            - "name" (str): Card name (defaults to "Unnamed" if empty).
            - "subtype" (str): Comma-separated list of selected subtypes (empty if none selected).
            - "attack" (str): Attack value (defaults to "0" if empty).
            - "defense" (str): Defense value (defaults to "0" if empty).
            - "effect1" (str): First effect text (empty if none provided).
            - "effect2" (str): Second effect text (empty if none provided).
            - "effect1_style (str): The first effect style to use.
            - "effect2_style (str): The second effect style to use.
            - "image" (str): Image file path (defaults to "default.png" if empty).
            - "serial" (str): Serial number (always empty in this context).

    Notes:
        - All string values are stripped of leading/trailing whitespace.
        - Used by update_preview, save_to_card_list, and reset_ui to centralize data collection.
    """
    card_data = {
        "type": WIDGETS["type_combo"].get().strip() or "Unknown",
        "level": WIDGETS["level_var"].get() or 1,
        "name": WIDGETS["name_entry"].get().strip() or "Unnamed",
        "subtype": ", ".join(get_selected_subtypes()),
        "attack": WIDGETS["atk_entry"].get().strip() or "0",
        "defense": WIDGETS["def_entry"].get().strip() or "0",
        "effect1": WIDGETS["effect1_entry"].get("1.0", tk.END).strip() or "",
        "effect1_style": WIDGETS["effect1_style_var"].get().strip() or None,
        "effect2": WIDGETS["effect2_entry"].get("1.0", tk.END).strip() or "",
        "effect2_style": WIDGETS["effect2_style_var"].get().strip() or None,
        "image": WIDGETS["image_entry"].get().strip() or "default.png",
        "translucency": WIDGETS["translucent_var"].get(),
        "serial": WIDGETS["serial_entry"].get().strip() or "",
        "rarity": "0" # Rarity is not handled in this app so default to 0.
    }
    
    if print_data:
        output_text(f"Collected card data: {card_data}", "note")
    return card_data


def check_for_effect_combination_in_file(file_path, effect_1, effect_2):
    """
    Check if a specific effect combination exists in a file. 
    This will check for both possible orders of the input effect combination.
    
    Args:
        file_path (str): Path to the file to check.
        effect_1 (str): The first effect to search for.
        effect_2 (str): The second effect to search for.
    
    Returns:
        bool: True if the combination is found, False otherwise.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there’s an issue reading the file.
    """
    try:
        effect_combo_1 = f"{effect_1};{effect_2}"
        effect_combo_2 = f"{effect_2};{effect_1}"
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if effect_combo_1 in line or effect_combo_2 in line:
                    return True
        return False
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except IOError as e:
        raise IOError(f"Error reading file '{file_path}': {e}")


def overwrite_card_in_file(filename, row):
    """
    Overwrite an existing card in the CSV file if the name matches.

    Args:
        filename (str): Path to the CSV file.
        row (list): List containing the new card data in the order of CARD_LIST_HEADER.

    Returns:
        bool: True if the card was overwritten, False if not found.
    """
    if not LOAD_CARD_MODE:
        output_text("ERROR: Cards not not editable: -L was not specified!", "error")

    card_name = row[0].strip()  # NAME is at index 0
    lines = []
    found = False

    # Read existing file
    if os.path.isfile(filename):
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            header = next(reader)  # Preserve header
            lines.append(header)
            for existing_row in reader:
                if existing_row[0].strip() == card_name:  # Match by NAME
                    found = True
                    lines.append(row)  # Use the provided row directly
                else:
                    lines.append(existing_row)

    if not found:
        return False

    # Write back to file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(lines)
    
    output_text(f"Overwrote card '{card_name}' in {filename}", "success")
    return True


def save_to_card_list(filename=DEFAULT_CARD_LIST_FILE):
    """
    Save card data from the UI to a spreadsheet.

    This function collects card details from the GUI widgets and saves them to a CSV file
    with the header matching {CARD_LIST_HEADER}.
    Data is appended to the file, and the header is written if the file doesn’t exist.

    Args:
        filename (str): The path to the output CSV file (e.g., 'card_list.csv').

    Returns:
        None: Saves data to the specified CSV file.
    """
    # Collect card data from UI
    card_data = get_card_data()
    card_name = card_data.get("name", "").strip()
    
    # Check if the name already exists
    if not LOAD_CARD_MODE and is_name_in_card_list(card_name):
        output_text(f"Card name '{card_name}' already exists in {filename}! Skipping", "error")
        load_next_image()  # Still load next image even if skipped
        return

    # Define the header
    header = CARD_LIST_HEADER

    # Check if file exists to determine if header needs to be written
    file_exists = os.path.isfile(filename)

    # Open the file in append mode
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')

        # Write header if the file is new
        if not file_exists:
            writer.writerow(header)
            
        # Adjust subtypes for spell cards - it should have none.   
        if card_data["type"].lower() == "spell":
            card_data["subtype"] = ""
        
        # Rename the image file based on the new name selected.
        image_path = card_data.get("image", "")
        output_text(f"Full image path: {image_path}", "note")
        new_image_name = card_data.get("name", "")
        output_text(f"Image name: {new_image_name}", "note")
        if new_image_name not in image_path and "Unnamed" not in new_image_name:
            image_path = rename_file(image_path, new_image_name)
            WIDGETS["image_entry"].delete(0, tk.END)
            WIDGETS["image_entry"].insert(0, image_path)  # Update UI with new path
        
        # Generate relative path for images.
        rel_image_path = get_relative_path(SCRIPT_DIR, image_path)
        output_text(f"Relative path for image set to: {rel_image_path}", "note")
        
        # Prepare the row data, adding a default 'RARITY' since it’s not in card_data
        row = [
            card_data.get("name", ""),
            card_data.get("type", ""),
            card_data.get("subtype", ""),
            card_data.get("level", ""),
            rel_image_path,
            card_data.get("attack", ""),
            card_data.get("defense", ""),
            card_data.get("effect1", ""),
            card_data.get("effect2", ""),
            card_data.get("serial", ""),   # If this index changes, mdify the sn value below.
            card_data.get("rarity", ""),
            card_data.get("translucency", ""),
            card_data.get("effect1_style", ""),
            card_data.get("effect2_style", "")
        ]                
            
        # Just a sanity check in case additions are added.
        if len(CARD_LIST_HEADER) != len(row):
            output_text(f"ERROR: row data inconsistent with CARD_LIST_HEADER: {row} -> {CARD_LIST_HEADER}", "error")

        if LOAD_CARD_MODE:
            # Overwrite existing line if name matches
            if overwrite_card_in_file(filename, row):
                output_text(f"Card data saved to {filename}: {card_data}", "success")
                sn = row[9]
                save_sn_to_list(sn, DEFAULT_SERIAL_LIST_FILE)
                output_text(f"Serial number {sn} saved to {DEFAULT_SERIAL_LIST_FILE}", "success")
                load_next_image()
                return  # Exit after overwriting

        # Write the row to the CSV if it's not a duplicate.
        if not check_line_in_file(filename, ";".join(str(r) for r in row)):
            if not check_for_effect_combination_in_file(filename, row[7], row[8]):
                writer.writerow(row)
                output_text(f"Card data saved to {filename}: {card_data}", "success")
                sn = row[9]
                save_sn_to_list(sn, DEFAULT_SERIAL_LIST_FILE)
                output_text(f"Serial number {sn} saved to {DEFAULT_SERIAL_LIST_FILE}", "success")
                load_next_image()
            else:
                output_text(f"Effect combination already exists in output file! Skipping", "error") 
        else:
            output_text(f"Card already exists in output file! Skipping", "error") 


def reset_ui():
    """
    Reset the UI to default values and update the preview once.
    """
    global SKIP_PREVIEW
    SKIP_PREVIEW = True  # Prevent updates during reset

    # Reset widgets to default values
    WIDGETS['type_combo'].set("Fire")
    WIDGETS["level_var"].set(1)
    WIDGETS["name_entry"].delete(0, tk.END)
    WIDGETS["name_entry"].insert(0, "Unnamed")
    for var in WIDGETS["subtype_vars"]:
        var.set(False)
    WIDGETS["atk_entry"].delete(0, tk.END)
    WIDGETS["atk_entry"].insert(0, "0")
    WIDGETS["def_entry"].delete(0, tk.END)
    WIDGETS["def_entry"].insert(0, "0")
    WIDGETS["effect1_entry"].delete("1.0", tk.END)
    WIDGETS["effect2_entry"].delete("1.0", tk.END)
    WIDGETS["image_entry"].delete(0, tk.END)
    WIDGETS["image_entry"].insert(0, "")
    WIDGETS["effect1_style_var"].set(None)
    WIDGETS["effect2_style_var"].set(None)

    # Re-enable preview and update once
    SKIP_PREVIEW = False
    update_preview()
    

def browse_image():
    """
    Open a file dialog to select an image and update the entry field.
    """
    filename = filedialog.askopenfilename(
        initialdir="../images", 
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if filename:
        WIDGETS["image_entry"].delete(0, tk.END)
        WIDGETS["image_entry"].insert(0, filename)
        
    update_name_from_image()    
    update_preview()


def update_preview(force_update=False):
    """
    Gather UI input, create a card image, and display it in the preview window.
    
    Args:
        force_update (bool): True to force an update.

    This function collects card data from the GUI, generates a card image using create_card,
    saves it to a temporary folder, and updates the preview canvas with the resulting image.
    """
    # Stores the last card data where an update was triggered.
    global LAST_UPDATE_CARD_DATA
    
    # Skip preview update during reset
    global SKIP_PREVIEW
    if SKIP_PREVIEW and not force_update:
        return
        
    # Collect card data from UI
    card_data = get_card_data()
    
    if card_data == LAST_UPDATE_CARD_DATA and not force_update:
        return
    else:
        LAST_UPDATE_CARD_DATA = card_data
    
    #Set the serial number.
    serial_number = generate_serial_number(card_data)
    update_serial_number(serial_number)

    # Use a temporary folder for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate the card image
        output_file_name = f"{card_data['type'].replace(' ', '_')}_card_{card_data['name'].replace(' ', '_')}-{card_data['translucency']}.png"
        create_card(card_data, temp_dir, output_file_name, tmp_file=True)
        
        # Load the generated image
        output_file = f"{temp_dir}/{output_file_name}"
        card_image = Image.open(output_file)
        
        # Resize to fit preview canvas
        preview_width, preview_height = 400, 580
        card_image = card_image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage for Tkinter
        photo = ImageTk.PhotoImage(card_image)
        
        # Update the canvas
        WIDGETS["preview_canvas"].delete("all")  # Clear previous content
        WIDGETS["preview_canvas"].create_image(
            preview_width // 2, preview_height // 2, image=photo
        )
        # Store reference to prevent garbage collection
        WIDGETS["preview_canvas"].image = photo


def generate_stat_pair(stat_bonus):
    """
    Generate two random values between -stat_bonus and stat_bonus (inclusive).
    
    Args:
        stat_bonus (int): The maximum absolute value for the random range.
        
    Returns:
        tuple: A pair of integers (value1, value2) where each is between -stat_bonus and stat_bonus.
    """
    value1 = random.randint(-stat_bonus, stat_bonus) * 5
    value2 = random.randint(-stat_bonus, stat_bonus) * 5
    return (value1, value2)


def get_sign(value):
    """
    Return the sign of a number as a string.
    
    Args:
        value (int or float): The number to check.
        
    Returns:
        str: "+" if value is >= 0, "" if value < 0.
        
    Note: This returns "" for negative numbers because they will already have a negative on them.
    """
    return "+" if value >= 0 else ""


def randomize_atk_def(isSpell=False):
    """
    Randomize ATK and DEF values based on the selected level and type.

    This function generates random ATK and DEF values in increments of 5, ensuring their sum
    equals 5 times the selected level. The values are then populated into the provided entry widgets.
    For spells, the values are slightly different and instead range as bonuses from +/- 5*level.
    
    Args:
        isSpell (bool): Sets the generation to spell mode.
    """
    # Get the selected level, default to 1 if empty or invalid
    level_str = str(WIDGETS["level_var"].get()).strip()
    card_type = WIDGETS["type_combo"].get().strip().lower()
    level = int(level_str) if level_str in [str(i) for i in range(1, 6)] else 1

    # Clear the entry fields
    WIDGETS["atk_entry"].delete(0, tk.END)
    WIDGETS["def_entry"].delete(0, tk.END)

    # Calculate total points (5 * level)
    if (card_type == "spell"):
        # Get stat bonuses.
        card_atk, card_def = generate_stat_pair(level*2)
    
        # Populate the entry fields.
        WIDGETS["atk_entry"].insert(0, f"{get_sign(card_atk)}{card_atk}")
        WIDGETS["def_entry"].insert(0, f"{get_sign(card_def)}{card_def}")
    else:
        total_points = 500 * level

        # Generate ATK in increments of 5, leaving at least 0 for DEF
        max_atk = total_points  # ATK can be 0 to total_points
        card_atk = random.randrange(0, max_atk + 5, 5)  # Start at 0, step by 5, inclusive of max_atk

        # DEF is the remainder to ensure atk + def = total_points
        card_def = total_points - card_atk
    
        # Populate the entry fields.
        WIDGETS["atk_entry"].insert(0, str(card_atk))
        WIDGETS["def_entry"].insert(0, str(card_def))


def get_selected_subtypes():
    """
    Return a list of selected subtype labels based on their BooleanVar states.

    Returns:
        list of str: List of selected subtype labels.
    """
    selected = [label for var, label in zip(WIDGETS["subtype_vars"], WIDGETS["subtype_labels"]) if var.get()]
    return selected


def adjust_listbox_width():
    """
    Adjust the width of the effect_listbox to the length of its longest string,
    only increasing it if necessary.
    Assumes WIDGETS is a global dictionary containing the effect_listbox.
    """
    global WIDGETS
    try:
        listbox = WIDGETS["effect_listbox"]
        # Get all items in the Listbox
        items = listbox.get(0, tk.END)
        if not items:
            # Set a default width if the Listbox is empty (only if not set)
            current_width = listbox.cget("width")
            if current_width == 0:  # Default is 20 if unset, but check for safety
                listbox.config(width=20)
            return
        
        # Find the length of the longest item
        max_length = max(len(str(item)) for item in items)
        # Adjusted width with your scaling factor
        adjusted_width = int(max_length * 0.85)
        
        # Get the current width
        current_width = listbox.cget("width")
        
        # Only increase width if the new width is larger
        if adjusted_width > current_width:
            listbox.config(width=adjusted_width)
    except KeyError:
        output_text("Error: 'effect_listbox' not found in WIDGETS", "error")
    except Exception as e:
        output_text(f"Error adjusting Listbox width: {e}", "error")


def generate_effects(input_file, columns, subtypes):
    """
    Generate NUMBER_OF_EFFECT_BOXES random effects and populate the effect buttons.

    This function loads effects from a CSV file, filters them based on specified columns,
    and generates 10 unique random effects: up to 5 using subtypes or spell search values as search strings,
    and the rest without. If fewer than 5 unique effects match the criteria, it continues
    with unfiltered effects to reach 10 total, without resetting.

    Args:
        input_file (str): Path to the input CSV file containing effect data.
        columns (list of str): List of column names to filter on (rows where these are 'True').
        subtypes (list of str): List of selected subtypes to use as search strings for up to 5 effects (for units).
    """
    # Load CSV and filter for rows where specified columns are 'True'
    possible_effect_values = load_and_filter_csv(input_file, columns)
    
    # Track used effects to avoid duplicates
    used_effects = set()
    generated_effects = []
    strings_to_omit = []
    
    # Determine if we're generating for a spell or unit
    is_spell = WIDGETS["type_combo"].get().strip().lower() == "spell"
    
    if not is_spell:
        # Unit-specific logic
        # Get selected effect search values from effect_search_vars
        effect_search_vars = WIDGETS["effect_search_vars"]  # List of StringVar objects
        effect_search_values = [var.get() for var in effect_search_vars if var.get()]  # Filter out empty strings
        
        strings_to_omit = ["lose <atkdef>", "destroy up to <number> <typeslevels>"]
        
        target_with_search_terms = NUMBER_OF_EFFECT_BOXES // 2

        search_terms = subtypes + effect_search_values      
        
        # Generate up to half the effects using search_terms as search strings
        if search_terms:  # Only if search_terms are provided
            for _ in range(target_with_search_terms):
                if not possible_effect_values or len(used_effects) >= len(possible_effect_values):
                    break  # Stop if no more unique effects are available
                effect = get_random_effect(possible_effect_values, search_strings=search_terms, omit_strings=strings_to_omit)
                while effect in used_effects:
                    effect = get_random_effect(possible_effect_values, search_strings=search_terms, omit_strings=strings_to_omit)
                    if len(used_effects) >= len(possible_effect_values):
                        break  # Avoid infinite loop
                used_effects.add(effect)
                generated_effects.append(effect)
    else:
        # Spell-specific logic
        # Get selected effect search values from effect_search_vars
        effect_search_vars = WIDGETS["effect_search_vars"]  # List of StringVar objects
        effect_search_values = [var.get() for var in effect_search_vars if var.get()]  # Filter out empty strings
        target_with_search = NUMBER_OF_EFFECT_BOXES // 2

        # Generate up to half the effects using spell search values as search strings
        if effect_search_values:  # Only if spell search values are selected
            for _ in range(target_with_search):
                if not possible_effect_values or len(used_effects) >= len(possible_effect_values):
                    break  # Stop if no more unique effects are available
                effect = get_random_effect(possible_effect_values, search_strings=effect_search_values)
                while effect in used_effects:
                    effect = get_random_effect(possible_effect_values, search_strings=effect_search_values)
                    if len(used_effects) >= len(possible_effect_values):
                        break  # Avoid infinite loop
                used_effects.add(effect)
                generated_effects.append(effect)

    # Generate remaining effects without search strings (up to 10 total)
    remaining = NUMBER_OF_EFFECT_BOXES - len(generated_effects)
    for _ in range(remaining):
        if not possible_effect_values or len(used_effects) >= len(possible_effect_values):
            break  # Stop if no more unique effects are available
        effect = get_random_effect(possible_effect_values)  # No search_strings
        while effect in used_effects:
            effect = get_random_effect(possible_effect_values)
            if len(used_effects) >= len(possible_effect_values):
                break  # Avoid infinite loop
        used_effects.add(effect)
        generated_effects.append(effect)

    # Set the Listbox text, filling remaining
    WIDGETS['effect_listbox'].delete(0, tk.END)  # Clear existing items
    for i in range(NUMBER_OF_EFFECT_BOXES):
        if i < len(generated_effects):
            WIDGETS['effect_listbox'].insert(tk.END, generated_effects[i])
            
    adjust_listbox_width()


def is_name_in_card_list(card_name, filename=DEFAULT_CARD_LIST_FILE):
    """
    Check if a card name already exists in the DEFAULT_CARD_LIST_FILE file.

    Args:
        card_name (str): The name to check against the 'NAME' column in the CSV.
        filename (str): Path to the CSV file (e.g., 'card_list.csv').

    Returns:
        bool: True if the card name is found in the file, False otherwise.
    """
    # Resolve the filename to an absolute path relative to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_filename = os.path.join(script_dir, filename) if not os.path.isabs(filename) else filename
    output_text(f"Checking file: {abs_filename}", "note")

    # If the file doesn’t exist, no names can match
    if not os.path.isfile(abs_filename):
        output_text(f"File {abs_filename} does not exist", "warning")
        return False

    # Open and read the CSV file
    try:
        with open(abs_filename, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            
            # Get the header row to find the 'NAME' column index
            try:
                header = next(reader)
                name_index = header.index("NAME")
            except StopIteration:
                output_text("File is empty", "warning")
                return False
            except ValueError:
                output_text("CSV file does not contain a 'NAME' column in the header", "error")
                raise ValueError("CSV file does not contain a 'NAME' column in the header")

            # Check each row for a matching name
            for row in reader:
                #output_text(f"Row: {row}", "note")
                if len(row) > name_index:
                    csv_name = row[name_index].strip()
                    if csv_name == card_name.strip():
                        output_text(f"Found match: '{csv_name}' == '{card_name}'", "success")
                        return True
                else:
                    output_text(f"Skipping malformed row: {row}", "warning")
    
    except Exception as e:
        output_text(f"Error reading {abs_filename}: {str(e)}", "error")
        return False

    output_text(f"No match found for '{card_name}' in {abs_filename}", "note")
    return False


def assign_effect(effect_text):
    """
    Assign the clicked effect to the first empty effect field.
    """
    current_effect1 = WIDGETS["effect1_entry"].get("1.0", tk.END).strip()
    current_effect2 = WIDGETS["effect2_entry"].get("1.0", tk.END).strip()
    if not current_effect1:
        effect_style = deduce_effect_style_from_effect_text(effect_text)
        WIDGETS["effect1_entry"].delete("1.0", tk.END)
        WIDGETS["effect1_entry"].insert("1.0", effect_text)
        if effect_style is not None:
            WIDGETS['effect1_style_var'].set(effect_style)
    elif not current_effect2:
        effect_style = deduce_effect_style_from_effect_text(effect_text)
        WIDGETS["effect2_entry"].delete("1.0", tk.END)
        WIDGETS["effect2_entry"].insert("1.0", effect_text)
        if effect_style is not None:
            WIDGETS['effect2_style_var'].set(effect_style)


def generate_serial_number(card_data, waitForThreads=False):
    """
    Generate a unique serial number for a trading card based on its attributes.

    This function takes a dictionary of card attributes and returns a unique serial number.
    The implementation should ensure uniqueness across potentially millions of cards using
    attributes like name, type, subtypes, rarity, image, attack, defense, and effects.

    Args:
        card_data (dict): A dictionary containing card details with the following keys:
            - name (str): Card name.
            - type (str): Card type (e.g., 'Fire').
            - subtypes (list of str): List of subtypes (e.g., ['Dragon', 'Warrior']).
            - rarity (str): Card rarity (e.g., 'Rare').
            - image (str): Path to the image file (e.g., 'dragon.png').
            - attack (str): Attack value (e.g., '1500').
            - defense (str): Defense value (e.g., '1200').
            - effect1 (str): First effect text (e.g., 'Draw 1 card').
            - effect1_style (str): The effect1_style string.
            - effect2 (str): Second effect text (e.g., 'Gain 2 life').
            - effect2_style (str): The effect1_style string.

    Returns:
        str: A unique serial number (e.g., 'FRA-DRWA-5f3a2b', 'e80b50170989').

    Notes:
        - The serial number should be concise (e.g., 8-12 characters) yet unique.
        - Implementation details (e.g., hash, counter, UUID) are left to the user.
    """
    if waitForThreads:
        wait_for_preprocessing()
    
    if not PREPROCESSING_FINISHED:
        return "Loading.."
    
    # Extract attributes from card_data
    name = card_data.get('name', '')
    card_type = card_data.get('type', '')
    level = card_data.get('level', '')
    subtypes = card_data.get('subtype', '')
    rarity = card_data.get('rarity', '')
    image = card_data.get('image', '')
    attack = card_data.get('attack', '')
    defense = card_data.get('defense', '')
    effect1 = card_data.get('effect1', '')
    effect1_style = card_data.get('effect1_style', '')
    effect2 = card_data.get('effect2', '')
    effect2_style = card_data.get('effect2_style', '')
        
    # Placeholder: Combine attributes into a unique string
    card_attributes = (
        f"{name}-{card_type}-{subtypes}-{level}-{image}-{attack}-{defense}-{effect1}-{effect1_style}-{effect2}-{effect2_style}-{rarity}"
    )

    output_text(f"Creating serial number for: {card_attributes}", "note")

    if subtypes == "":
        all_types = card_type
    else:
        all_types = card_type + ", " + subtypes
    all_types_id = get_combination_id(all_types, ALL_TYPES_LIST_LOWER)
    effect1_style_id = get_index_in_baseN(effect1_style, VALID_OVERLAY_STYLES)
    effect2_style_id = get_index_in_baseN(effect2_style, VALID_OVERLAY_STYLES)
    
    if effect1 == "":
        effect1_id = "0"
    else:
        effect1_id = effect1[0]
    
    if effect2 == "":
        effect2_id = "0"
    else:
        effect2_id = effect2[0]

    serial_number = ""                             # Create the initial SN string.
    serial_number += name[0].capitalize()          # Add the first letter of the name.
    serial_number += str(level)                    # Add the level.
    serial_number += all_types_id                  # Add the unique type+subtype identifier.
    
    # Since level is included as part of the SN, the atk and defense can be generated on a scale relative to the level.
    if "+" in attack or "-" in attack: # Spell stats
        # For spells, this value x ranges from -level*10 < x < level*10. So if we add level*10 to the value x, we have
        # 0 < x < 2level*10 => 0 < x < level*20, so, the per level value can be treated as 20. 
        serial_number += get_number_id(int(attack[1:])+level*10, level, per_level_val=20)  # Add the attack value identifier.
        serial_number += get_number_id(int(defense[1:])+level*10, level, per_level_val=20) # Add the attack value identifier.    
    else: # Unit stats
        serial_number += get_number_id(int(attack), level)  # Add the attack value identifier.
        serial_number += get_number_id(int(defense), level) # Add the attack value identifier.
    
    serial_number += effect1_id                    # Add the first letter of the effect1.
    serial_number += effect1_style_id              # Add the unique identifier for the the effect1 style.
    serial_number += effect2_id                    # Add the first letter of the effect2.
    serial_number += effect2_style_id              # Add the unique identifier for the the effect1 style.
    serial_number += str(rarity)                   # Add the rarity of the card.
    
    # Update the pad bit.
    pad_bit_index = 0 
    pad_bit = "0"
    temp_serial_number = serial_number + pad_bit   # Create what the serial number is without any pad bit modifications.
    while sn_in_list(temp_serial_number, DEFAULT_SERIAL_LIST_FILE):
        pad_bit_index += 1                         # Increment the index
        if pad_bit_index >= len(CHARACTERS):       # Prevent index out of bounds
            raise ValueError("No unique serial number available - all padding options exhausted")
        pad_bit = CHARACTERS[pad_bit_index]        # Increment pad bit.
        temp_serial_number = serial_number + pad_bit
        
    # We expect the card to exist if we are loading in an existing card.
    if LOAD_CARD_MODE:
        pad_bit_index -= 1
        pad_bit = CHARACTERS[pad_bit_index]        # De-increment pad bit.
    
    serial_number += pad_bit                       # One pad bit for expansion (Allows 36 possibilities with all other options the same).

    #output_text(f"Created serial_number: {serial_number}", "note")
    card_data["serial"] = serial_number
    
    return serial_number


def update_serial_number(new_serial):
    """
    Updates the serial number displayed in the serial_entry widget.

    Temporarily enables the serial_entry widget, clears its current content,
    inserts the new serial number, and then disables it again to prevent user edits.

    Args:
        new_serial (str): The new serial number to display in the widget.

    Returns:
        None
    """
    #output_text(f"Updating serial number to: {new_serial}", "note")
    WIDGETS["serial_entry"].configure(state="normal")    # Enable editing
    WIDGETS["serial_entry"].delete(0, tk.END)            # Clear current text
    WIDGETS["serial_entry"].insert(0, new_serial)        # Insert new serial
    WIDGETS["serial_entry"].configure(state="disabled")  # Disable again
    #output_text(f"Updated serial number!", "success")


def get_gui_metadata():
    """
    Analyze GUI input and return a list of metadata strings.

    This function checks the selected type and level from the GUI, returning a list containing:
    - 'UNIT' if the type is not 'Spell' (case-insensitive), 'SPELL' if it is.
    - 'LEVEL_#' where # is the selected level (1-5).

    Returns:
        list of str: A list of metadata strings (e.g., ['UNIT', 'LEVEL_3'] or ['SPELL', 'LEVEL_1']).
    """
    metadata = []

    # Get the selected type and determine UNIT or SPELL
    selected_type = WIDGETS["type_combo"].get().strip().lower()
    if selected_type == "spell":
        metadata.append("SPELL")
    else:
        metadata.append("UNIT")

    # Get the selected level and add LEVEL_#
    selected_level = str(WIDGETS["level_var"].get()).strip()
    if selected_level in [str(i) for i in range(1, 6)]:  # Validate it’s 1-5
        metadata.append(f"LEVEL_{selected_level}")
    else:
        metadata.append("LEVEL_1")  # Default to 1 if invalid or empty

    return metadata


def update_name_from_image(force_update=False):
    """
    Update the card name and type based on the image path provided in the UI.

    This function retrieves the image path from the 'image_entry' widget and the current name from
    the 'name_entry' widget. It checks if the image path contains any type from TYPE_LIST and
    updates the 'type_combo' widget accordingly. If the current name is 'Unnamed' and a valid
    image path is provided, it extracts the filename (without path or extension) and updates
    the 'name_entry' widget with it. Various status messages are output via output_text() to
    indicate success, warnings, or errors.
    
    Args:
        force_update (bool): Update the name regardless of what the name field currently is.

    Behavior:
        - Updates 'type_combo' if a TYPE_LIST item is found in the image path (case-insensitive).
        - Updates 'name_entry' to the filename if the current name is 'Unnamed' and the image is valid.
        - Skips name update if the filename starts with '_' (indicating a default hash name).
        - Outputs messages for invalid image paths, missing paths, or unchanged names.

    Raises:
        No exceptions are raised directly, but Image.open() may trigger FileNotFoundError, IOError,
        or ValueError if the image path is invalid, which are caught and handled with error messages.
    """
    image_path = WIDGETS["image_entry"].get()
    current_name = WIDGETS["name_entry"].get().strip()
    
    # Image path not set yet.
    if image_path == "":
        return
        
    # Check if any item from TYPE_LIST is in card_data["image"] and update type_combo
    image_value = image_path.strip()  # Remove extra whitespace
    for type_item in TYPE_LIST:
        if type_item.lower() in image_value.lower():
            output_text(f"Setting type_combo to: {type_item}", "note")
            WIDGETS["type_combo"].set(type_item)
            break  # Stop after the first match
    else:
        output_text(f"No match from TYPE_LIST found in {image_value}", "warning")
    
    if (current_name == "Unnamed" and image_path) or (force_update and image_path):
        # Check if the image_path points to a valid image file
        try:
            # Attempt to open the image to verify it's valid
            with Image.open(image_path):
                # Extract just the filename without path or extension
                filename = os.path.splitext(os.path.basename(image_path))[0]
                # Update the name_entry with the extracted filename
                WIDGETS["name_entry"].delete(0, tk.END)
                WIDGETS["name_entry"].insert(0, filename)
                output_text(f"Name updated to: {filename}", "note")
        except (FileNotFoundError, IOError, ValueError):
            # If image_path isn't valid, don't update and print a message
            output_text(f"Invalid image path: {image_path}", "error")
    elif not image_path:
        output_text("No image path provided", "error")
    else:
        output_text(f"Name not updated: current name is '{current_name}', not 'Unnamed'", "warning")    


def load_next_image(image_file=None, filename=DEFAULT_CARD_LIST_FILE):
    """
    Select and load the next image file within the folder of the currently
    selected/loaded image file whose name isn’t already in DEFAULT_CARD_LIST_FILE.
    Clears the effect fields to prep the UI for a new card.
    
    Args:
        image_file (str, optional): The current image file to use for loading the next. 
            Defaults to gathering this field from the UI.
        filename (str, optional): Path to the CSV file to check names against. 
            Defaults to DEFAULT_CARD_LIST_FILE.
    """
    output_text("Loading next image file!", "note")
    
    # Get the current image
    if image_file is None:
        current_image_file = WIDGETS["image_entry"].get().strip()
    else:
        current_image_file = image_file
       
    output_text(f"Current image file: {current_image_file}", "note")
    
    # Track checked images to avoid infinite loops
    checked_images = set([current_image_file]) if current_image_file else set()
    next_image_file = get_next_image(current_image_file)
    output_text(f"Next image file (initial): {next_image_file}", "note")

    # Clear the current image entry
    WIDGETS["image_entry"].delete(0, tk.END)

    # Loop to find an image with a unique name
    while next_image_file is not None:
        # Set the image entry and update the name
        WIDGETS["image_entry"].insert(0, next_image_file)
        update_name_from_image(force_update=True)  # This sets name_entry
        
        # Get the name from the UI
        potential_name = WIDGETS["name_entry"].get().strip()
        output_text(f"Checking name: {potential_name}", "note")

        # Check if the name is already in the card list
        if not is_name_in_card_list(potential_name):
            output_text(f"Loaded image with unique name: {next_image_file}", "success")
            break  # Name is unique, keep this image
        
        # Name exists, try the next image
        output_text(f"Name '{potential_name}' already exists, trying next image", "warning")
        checked_images.add(next_image_file)
        next_image_file = get_next_image(next_image_file)
        output_text(f"Next image file: {next_image_file}", "note")

        # Prevent infinite loop: if we've checked all images or cycled back, stop
        if next_image_file in checked_images or next_image_file == current_image_file:
            output_text("No unique image name found in directory!", "warning")
            next_image_file = None
            break
        
        # Clear image entry for the next iteration
        WIDGETS["image_entry"].delete(0, tk.END)

    # Finalize the UI state
    if next_image_file is None:
        output_text("No next image file with a unique name found!", "warning")
        WIDGETS["image_entry"].insert(0, "")  # Clear the field
    
    # Clear effect fields
    WIDGETS["effect1_entry"].delete("1.0", tk.END)
    WIDGETS["effect2_entry"].delete("1.0", tk.END)
    WIDGETS["effect1_style_var"].set(None)
    WIDGETS["effect2_style_var"].set(None)
    
    # Final update of name and preview (redundant if loop succeeded, but ensures consistency)
    update_name_from_image(force_update=True)
    update_preview()


def load_selected_card(csv_file, listbox, headers):
    """
    Load the selected card from the CSV file into the UI widgets.

    Args:
        csv_file (str): Path to the CSV file containing card data.
        listbox (tk.Listbox): The Listbox widget with card entries.
        headers (list): The header row from the CSV file (not used directly here, but passed for consistency).
    """
    # Get the selected index from the Listbox
    selection = listbox.curselection()
    if not selection:
        return  # No selection made

    selected_index = selection[0]

    # Read the CSV file and find the selected row
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f, fieldnames=CARD_LIST_HEADER, delimiter=';')
            next(reader)  # Skip header row since DictReader uses fieldnames
            for i, row in enumerate(reader):
                if i == selected_index:
                    # Populate UI widgets with row data
                    WIDGETS["name_entry"].delete(0, tk.END)
                    WIDGETS["name_entry"].insert(0, row.get("NAME", "Unnamed"))

                    WIDGETS["type_combo"].set(row.get("TYPE", "fire"))

                    level = int(row.get("LEVEL", 1)) if row.get("LEVEL", "1").isdigit() else 1
                    WIDGETS["level_var"].set(level)

                    WIDGETS["atk_entry"].delete(0, tk.END)
                    WIDGETS["atk_entry"].insert(0, row.get("ATTACK", "0"))

                    WIDGETS["def_entry"].delete(0, tk.END)
                    WIDGETS["def_entry"].insert(0, row.get("DEFENSE", "0"))

                    WIDGETS["image_entry"].delete(0, tk.END)
                    WIDGETS["image_entry"].insert(0, row.get("IMAGE", ""))

                    WIDGETS["effect1_entry"].delete("1.0", tk.END)
                    WIDGETS["effect1_entry"].insert("1.0", row.get("EFFECT1", ""))

                    WIDGETS["effect2_entry"].delete("1.0", tk.END)
                    WIDGETS["effect2_entry"].insert("1.0", row.get("EFFECT2", ""))

                    WIDGETS["serial_entry"].configure(state="normal")  # Enable for editing
                    WIDGETS["serial_entry"].delete(0, tk.END)
                    WIDGETS["serial_entry"].insert(0, row.get("SERIAL", ""))
                    WIDGETS["serial_entry"].configure(state="disabled")  # Disable again

                    translucency = int(row.get("TRANSPARENCY", 50)) if row.get("TRANSPARENCY", "50").isdigit() else 50
                    WIDGETS["translucent_var"].set(translucency)

                    WIDGETS["effect1_style_var"].set(row.get("EFFECT1_STYLE", "None") or "None")
                    WIDGETS["effect2_style_var"].set(row.get("EFFECT2_STYLE", "None") or "None")

                    # Handle subtypes (comma-separated string to BooleanVars)
                    subtypes = [s.strip() for s in row.get("SUBTYPES", "").split(",") if s.strip()]
                    for i, subtype in enumerate(WIDGETS["subtype_labels"]):
                        WIDGETS["subtype_vars"][i].set(subtype in subtypes)

                    # Update the preview
                    update_preview()
                    break
    except FileNotFoundError:
        output_text(f"Error: Could not find file '{csv_file}'.", "error")
    except Exception as e:
        output_text(f"Error loading card: {e}", "error")


def on_effect_select(event):
    """
    Handle selection in the effects Listbox.
    """
    listbox = event.widget
    selection = listbox.curselection()  # Get selected index
    if selection:  # Ensure something is selected
        effect_name = listbox.get(selection[0])  # Get the selected effect
        assign_effect(effect_name)
        update_preview()


PREPROCESSING_FINISHED = False

def preprocess_all_types_list():
    """
    This method will pre-process the ALL_TYPES_LIST_LOWER combinations into a buffer
    so that the SN generation method can use it without having to load it initially.
    """
    global PREPROCESSING_FINISHED  # Declare the variable as global to modify it.
    output_text("Pre-processing started for ALL_TYPE combinations...", "program")
    get_sequence_combinations(ALL_TYPES_LIST_LOWER)
    output_text("Pre-processing Finished for ALL_TYPE combinations...", "program")
    PREPROCESSING_FINISHED = True


def wait_for_preprocessing():
    """
    Wait for the preprocessing thread to complete before proceeding.

    This function checks if a global `processing_thread` exists and, if so, blocks execution
    until the thread finishes using `join()`. It provides feedback on the thread's status
    via print statements. If no thread is defined, it indicates that there’s nothing to wait for.

    Global Variables:
        processing_thread (threading.Thread or None): The thread object to wait for, expected
            to be set globally before calling this function.

    Returns:
        None

    Notes:
        - Assumes `processing_thread` is a `threading.Thread` object initialized elsewhere
          (e.g., in `main()`).
        - Prints status messages to stdout for debugging or user feedback.
    """
    global processing_thread
    if processing_thread is not None:
        processing_thread.join()
    else:
        output_text("No preprocessing thread to wait for!", "warning")


def initialize_preprocessing():
    """
    Starts the preprocessing for the various combinations for serial number generation.
    """
    global processing_thread
    output_text("Initializing preprocessing...", "program")
    processing_thread = threading.Thread(target=preprocess_all_types_list)
    processing_thread.start()


def main():
    """
    Set up and run the Card Creator GUI.
    """
    parser = argparse.ArgumentParser(
        description="User Interface for card generation."
    )
    parser.add_argument(
        "-i",
        "--input_file",
        default="effects/effects_with_placeholders.csv",
        help="Path to the input CSV file to process for effects. If not provided, defaults to "
             "'effects/effects_with_placeholders.csv'. The file should contain a header row "
             "with column names."
    )
    parser.add_argument(
        "-o",
        "--output_file",
        default=DEFAULT_CARD_LIST_FILE,
        help=f"Path to the output CSV file for saving card data. Defaults to '{DEFAULT_CARD_LIST_FILE}'."
    )
    parser.add_argument(
        "-L",
        "--load_mode",
        action="store_true",
        help="Enable loading mode to load and overwrite existing values from the output CSV."
    )
    
    args = parser.parse_args()
    
    # Start preprocessing combinations into RAM. Create and start the thread.
    initialize_preprocessing()
    
    root = tk.Tk()
    root.title("Game Card Creator")
    
    # Dark mode - broken for some features on linux.
    #sv_ttk.set_theme("dark")

    DPI = 96
    PREVIEW_WIDTH = int(399)
    PREVIEW_HEIGHT = int(579)

    main_frame = ttk.Frame(root, padding="15")
    main_frame_column = 0  # Default column for main_frame
    
    
    # Check for and initialize loading mode
    if args.load_mode:
        # Set global load mode for various features.        
        global LOAD_CARD_MODE
        LOAD_CARD_MODE = True
        
        # Create load_frame to the left of main_frame
        load_frame = ttk.LabelFrame(root, text="Load Card", padding="15")
        load_frame.grid(row=0, column=0, sticky="nsew")
        main_frame_column = 1  # Shift main_frame to column 1
        
        # Fixed width for the Listbox (adjust as needed)
        LOAD_FRAME_WIDTH = 225  # Placeholder; set your desired width here
        
        # Create Listbox for selectable lines
        load_listbox = tk.Listbox(
            load_frame,
            width=LOAD_FRAME_WIDTH // 10,  # Approximate width in characters (adjust based on font)
            height=PREVIEW_HEIGHT // 20,   # Approximate height in lines (adjust to match window)
            font=("Helvetica", 12),
            selectmode="single"  # One line selectable at a time
        )
        load_listbox.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
        
        # Scrollbar for Listbox
        scrollbar = ttk.Scrollbar(load_frame, orient="vertical", command=load_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        load_listbox.config(yscrollcommand=scrollbar.set)
        
        # Load CSV lines into Listbox
        try:
            with open(args.output_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                headers = next(reader)  # Skip header row if present
                for row in reader:
                    # Display a concise representation of each row (customize as needed)
                    display_text = f"{row[0]}"  # e.g., use Name or ID column; adjust index
                    load_listbox.insert(tk.END, display_text)
        except FileNotFoundError:
            load_listbox.insert(tk.END, "None.")

        # Load button
        load_btn = ttk.Button(
            load_frame,
            text="Load Card",
            command=lambda: load_selected_card(args.output_file, load_listbox, headers)
        )
        load_btn.grid(row=1, column=0, pady=8, padx=5, sticky="ew")

        # Configure load_frame grid weights
        load_frame.columnconfigure(0, weight=1)
        load_frame.rowconfigure(0, weight=1)  # Listbox expands vertically
        load_frame.rowconfigure(1, weight=0)  # Button stays fixed
    
    
    main_frame.grid(row=0, column=main_frame_column, sticky="nsew")

    left_frame = ttk.LabelFrame(main_frame, text="Card Details", padding="15")
    left_frame.grid(row=0, column=0, sticky="nsew")

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 12))
    style.configure("TButton", font=("Helvetica", 12))
    style.configure("TCheckbutton", font=("Helvetica", 12))

    # Name
    ttk.Label(left_frame, text="Name:").grid(row=0, column=0, pady=8, padx=5, sticky="e")
    name_entry = ttk.Entry(left_frame, width=30, font=("Helvetica", 12))
    name_entry.grid(row=0, column=1, pady=8, padx=5, sticky="w")
    name_entry.insert(0, "Unnamed")  # Default

    # Type dropdown
    ttk.Label(left_frame, text="Type:").grid(row=1, column=0, pady=8, padx=5, sticky="e")
    type_combo = ttk.Combobox(
        left_frame,
        values=TYPE_LIST,
        width=27,
        font=("Helvetica", 12),
    )
    type_combo.grid(row=1, column=1, pady=8, padx=5, sticky="w")
    type_combo.set("Fire")  # Default

    # Subtypes checkboxes
    subtypes_frame = ttk.LabelFrame(left_frame, text="Subtypes", padding="8")
    subtypes_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")
    subtype_vars = [tk.BooleanVar() for _ in range(len(SUBTYPES_LIST))]
    subtype_labels = SUBTYPES_LIST
    for i, label in enumerate(subtype_labels):
        ttk.Checkbutton(subtypes_frame, text=label, variable=subtype_vars[i]).grid(
            row=i // 3, column=i % 3, padx=8, pady=5, sticky="w"
        )

    # Level checkboxes
    ttk.Label(left_frame, text="Level:").grid(row=3, column=0, pady=8, padx=5, sticky="e")


    level_frame = ttk.LabelFrame(left_frame, text="Level", padding="8")  # Changed to left_frame
    level_frame.grid(row=3, column=0, columnspan=2, pady=8, sticky="ew")  # row=10, spans both columns
    # Single variable to track the selected level (1-5)
    level_var = tk.IntVar(value=1)  # Default to level 1

    # Create 5 checkboxes
    for i in range(1, 6):
        ttk.Checkbutton(
            level_frame,
            text=str(i),
            variable=level_var,
            onvalue=i,   # When checked, set level_var to this value
            offvalue=0,  # When unchecked, set to 0 (but we enforce one always on)
            command=lambda: [randomize_atk_def(), update_preview()]
        ).grid(row=3, column=i, pady=8, padx=5, sticky="w")

    # Ensure one is always selected by initializing with level 1
    level_var.set(1)

    # Image with browse button
    ttk.Label(left_frame, text="Image:").grid(row=4, column=0, pady=8, padx=5, sticky="e")
    image_entry = ttk.Entry(left_frame, width=35, font=("Helvetica", 12))
    image_entry.grid(row=4, column=1, pady=8, padx=5, sticky="w")    
    browse_btn = ttk.Button(
        left_frame, text="Browse", command=lambda: browse_image()
    )
    browse_btn.grid(row=5, column=1, pady=8, padx=5, sticky="w")
    
    # Add Next Image button
    next_img_btn = ttk.Button(
        left_frame, 
        text="Next Image", 
        command=lambda: [
            load_next_image(),
            update_preview()
        ]
    )
    next_img_btn.grid(row=5, column=1, pady=8, padx=(105, 0), sticky="w")  # Adjusted padx
    
    # Add Flip Image button
    flip_btn = ttk.Button(
        left_frame, 
        text="Flip Image", 
        command=lambda: [
            flip_image(image_entry.get()),
            update_preview(True)
        ]
    )
    flip_btn.grid(row=5, column=1, pady=8, padx=(205, 0), sticky="w")  # Adjusted padx

    # ATK
    ttk.Label(left_frame, text="ATK:").grid(row=6, column=0, pady=8, padx=5, sticky="e")
    atk_entry = ttk.Entry(left_frame, width=10, font=("Helvetica", 12))
    atk_entry.grid(row=6, column=1, pady=8, padx=5, sticky="w")
    atk_entry.insert(0, "0")  # Default

    # DEF
    ttk.Label(left_frame, text="DEF:").grid(row=7, column=0, pady=8, padx=5, sticky="e")
    def_entry = ttk.Entry(left_frame, width=10, font=("Helvetica", 12))
    def_entry.grid(row=7, column=1, pady=8, padx=5, sticky="w")
    def_entry.insert(0, "0")  # Default

    # Randomize button
    randomize_btn = ttk.Button(
        left_frame,
        text="Randomize",
        command=lambda: [
            randomize_atk_def(),
            update_preview()
        ]
    )
    randomize_btn.grid(row=8, column=1, pady=8, padx=5, sticky="w")

    # Effect 1
    ttk.Label(left_frame, text="Effect 1:").grid(row=9, column=0, pady=8, padx=5, sticky="e")
    effect1_entry = tk.Text(left_frame, height=3, width=35, font=("Helvetica", 12))
    effect1_entry.grid(row=9, column=1, pady=8, padx=5, sticky="w")
    
    # Effect 1 style(s)
    effect1_style_frame = ttk.LabelFrame(left_frame, text="Effect 1 Style", padding="8")  # Changed to left_frame
    effect1_style_frame.grid(row=10, column=0, columnspan=2, pady=8, sticky="ew")  # row=10, spans both columns
    effect1_style_var = tk.StringVar(value="None")
    effect1_style_value = VALID_OVERLAY_STYLES 
    for i, value in enumerate(effect1_style_value):
        display_text = "None" if value is None else value.capitalize()  # Use "None" as text for None
        ttk.Checkbutton(
            effect1_style_frame,
            text=display_text,
            variable=effect1_style_var,
            onvalue="None" if value is None else value,  # Convert None to "None" for UI,
            offvalue=-1,  # Unique off value to ensure mutual exclusivity
            command=update_preview
        ).grid(row=i // 4, column=i % 4, padx=5, sticky="w")  

    # Effect 2
    ttk.Label(left_frame, text="Effect 2:").grid(row=11, column=0, pady=8, padx=5, sticky="e")
    effect2_entry = tk.Text(left_frame, height=3, width=35, font=("Helvetica", 12))
    effect2_entry.grid(row=11, column=1, pady=8, padx=5, sticky="w")
    
    # Effect 2 style(s)
    effect2_style_frame = ttk.LabelFrame(left_frame, text="Effect 2 Style", padding="8")  # Changed to left_frame
    effect2_style_frame.grid(row=12, column=0, columnspan=2, pady=8, sticky="ew")  # row=10, spans both columns
    effect2_style_var = tk.StringVar(value="None")
    effect2_style_value = VALID_OVERLAY_STYLES 
    for i, value in enumerate(effect2_style_value):
        display_text = "None" if value is None else value.capitalize()  # Use "None" as text for None
        ttk.Checkbutton(
            effect2_style_frame,
            text=display_text,
            variable=effect2_style_var,
            onvalue="None" if value is None else value,  # Convert None to "None" for UI,
            offvalue=-1,  # Unique off value to ensure mutual exclusivity
            command=update_preview
        ).grid(row=i // 4, column=i % 4, padx=5, sticky="w")  

    # Serial Number (non-editable)
    ttk.Label(left_frame, text="Serial #:").grid(row=13, column=0, pady=8, padx=5, sticky="e")
    serial_entry = ttk.Entry(left_frame, width=30, font=("Helvetica", 12))
    serial_entry.insert(0, "AUTO-GENERATED")
    serial_entry.configure(state="disabled")
    serial_entry.grid(row=13, column=1, pady=8, padx=5, sticky="w")

    # Middle Section
    preview_frame = ttk.LabelFrame(main_frame, text="Card Preview", padding="15")
    preview_frame.grid(row=0, column=1, padx=15, sticky="nsew")
    
    # Translucency selection
    translucent_frame = ttk.LabelFrame(preview_frame, text="Translucency", padding="8")
    translucent_frame.grid(row=0, column=0, pady=8, sticky="ew")
    translucent_var = tk.IntVar(value=50)  # Default to 100%

    translucent_value = VALID_TRANSLUCENT_VALUES
    for i, value in enumerate(translucent_value):
        ttk.Checkbutton(
            translucent_frame,
            text=f"{value}%",
            variable=translucent_var,
            onvalue=value,
            offvalue=-1,  # Unique off value to ensure mutual exclusivity
            command=update_preview
        ).grid(row=0, column=i, padx=5, sticky="w")

    # Preview window
    preview_canvas = tk.Canvas(
        preview_frame,
        width=PREVIEW_WIDTH,
        height=PREVIEW_HEIGHT,
        bg="white",
        highlightthickness=1,
        highlightbackground="black",
    )
    preview_canvas.grid(row=1, column=0)

    # Save to Card List button
    save_btn = ttk.Button(
        preview_frame,
        text="Save to Card List",
        command=lambda: save_to_card_list(args.output_file)
    )
    save_btn.grid(row=2, column=0, pady=8, padx=5, sticky="ew")
    
    # Reset button
    reset_btn = ttk.Button(
        preview_frame,
        text="Reset",
        command=lambda: reset_ui()
    )
    reset_btn.grid(row=3, column=0, pady=8, padx=5, sticky="ew")
    
    # Spell Search Area
    effect_search_frame = ttk.LabelFrame(preview_frame, text="Effect Keywords For Search", padding="8")
    effect_search_frame.grid(row=4, column=0, pady=8, sticky="ew")
    effect_search_list = TYPE_LIST + SUBTYPES_LIST + EXTRA_EFFECT_KEYWORDS
    effect_search_vars = [tk.StringVar(value="") for _ in range(len(effect_search_list))]  # Default to empty string
    for i, value in enumerate(effect_search_list):
        display_text = value.capitalize()
        ttk.Checkbutton(
            effect_search_frame,
            text=display_text,
            variable=effect_search_vars[i],
            onvalue=value,  # e.g., "Spell", "Fire"
            offvalue="",   # Empty string when unchecked
            command=update_preview
        ).grid(row=i // 4, column=i % 4, padx=5, sticky="w")
        
    # Right - Effects Generator window
    effects_frame = ttk.LabelFrame(main_frame, text="Effects Generator", padding="15")
    effects_frame.grid(row=0, column=2, padx=15, sticky="nsew")

    # Define a custom style for the button
    style = ttk.Style()
    style.configure("Standout.TButton", 
                    font=("Helvetica", 12, "bold"), # Bold and larger font
                    foreground="white",             # Text color
                    background="black",             # Background color (may not work on all platforms)
                    padding=6)                      # Extra padding for size

    # Generate Effects button with standout style
    generate_btn = ttk.Button(
        effects_frame,
        text="Generate Effects",
        style="Standout.TButton",  # Apply the custom style
        command=lambda: [
            generate_effects(
                args.input_file,
                get_gui_metadata(),
                get_selected_subtypes()
            ),
            update_preview()
        ]
    )
    generate_btn.grid(row=0, column=0, pady=12, padx=10, sticky="ew")  # Increased padding

    # Create the Listbox for effect generation.
    effect_listbox = tk.Listbox(
        effects_frame,
        width = 100,
        height=NUMBER_OF_EFFECT_BOXES,  # Visible rows, adjust as needed
        selectmode="single"  # Single selection mode
    )
    effect_listbox.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

    # Horizontal scrollbar for listbox.
    scrollbar_horiz = ttk.Scrollbar(effects_frame, orient="horizontal", command=effect_listbox.xview)
    scrollbar_horiz.grid(row=2, column=0, pady=5, sticky="ew")
    effect_listbox.config(xscrollcommand=scrollbar_horiz.set)

    # Bind additional UI updates
    effect_listbox.bind("<<ListboxSelect>>", on_effect_select)
    type_combo.bind("<<ComboboxSelected>>", lambda e: update_preview())
    name_entry.bind("<FocusOut>", lambda e: update_preview())
    atk_entry.bind("<FocusOut>", lambda e: update_preview())
    def_entry.bind("<FocusOut>", lambda e: update_preview())
    effect1_entry.bind("<FocusOut>", lambda e: update_preview())
    effect2_entry.bind("<FocusOut>", lambda e: update_preview())
    image_entry.bind("<FocusOut>", lambda e: [update_name_from_image(), update_preview()])
    for var in subtype_vars:
        var.trace("w", lambda *args: update_preview())     
    
    # global variable to store UI elements.
    global WIDGETS
    WIDGETS = {
        "type_combo": type_combo,
        "level_var": level_var,
        "name_entry": name_entry,
        "subtype_vars": subtype_vars,
        "subtype_labels": subtype_labels,
        "atk_entry": atk_entry,
        "def_entry": def_entry,
        "effect1_entry": effect1_entry,
        "effect2_entry": effect2_entry,
        "image_entry": image_entry,
        "preview_canvas": preview_canvas,
        "translucent_var": translucent_var,
        "serial_entry" : serial_entry,
        "effect1_style_var": effect1_style_var,
        "effect2_style_var": effect2_style_var,
        "effect_search_vars": effect_search_vars,
        "effect_listbox" : effect_listbox
    }

    # Initial preview update
    update_preview()

    # Configure grid weights
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=0)
    main_frame.columnconfigure(2, weight=0)
    main_frame.rowconfigure(0, weight=1)

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()


if __name__ == "__main__":
    main()
