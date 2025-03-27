#!/usr/bin/env python3

import argparse
import tkinter as tk
import random
from tkinter import ttk
from tkinter import filedialog

# Used for randomly generating effects.
from generate_random_effects import load_and_filter_csv
from generate_random_effects import get_random_effect

# Inports from ttcg_tools
from ttcg_tools import output_text
from ttcg_tools import check_line_in_file
from ttcg_tools import get_relative_path
from ttcg_tools import rename_file

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
# Get script's directory (useful for relative paths)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
output_text(f"SCRIPT_DIR set to: {SCRIPT_DIR}", "program")

    
def get_card_data():
    """
    Collect card data from GUI widgets into a dictionary.

    This function gathers input from various Tkinter widgets in the card creator UI and
    returns a dictionary containing the card's attributes. Empty or invalid inputs are
    replaced with default values to ensure consistent output.

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
            - "image" (str): Image file path (defaults to "default.png" if empty).
            - "serial" (str): Serial number (always empty in this context).

    Notes:
        - All string values are stripped of leading/trailing whitespace.
        - Used by update_preview, save_to_card_list, and reset_ui to centralize data collection.
    """
    card_data = {
        "type": WIDGETS["type_combo"].get().strip() or "Unknown",
        "level": int(WIDGETS["level_combo"].get().strip() or 1),
        "name": WIDGETS["name_entry"].get().strip() or "Unnamed",
        "subtype": ", ".join(get_selected_subtypes()),
        "attack": WIDGETS["atk_entry"].get().strip() or "0",
        "defense": WIDGETS["def_entry"].get().strip() or "0",
        "effect1": WIDGETS["effect1_entry"].get("1.0", tk.END).strip() or "",
        "effect2": WIDGETS["effect2_entry"].get("1.0", tk.END).strip() or "",
        "image": WIDGETS["image_entry"].get().strip() or "default.png",
        "transparency": WIDGETS["transparency_var"].get(),
        "serial": WIDGETS["serial_entry"].get().strip() or "",
        "rarity": "0" # Rarity is not handled in this app so default to 0.
    }
    output_text(f"Collected card data: {card_data}", "note")  # Debug statement
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


def save_to_card_list(filename):
    """
    Save card data from the UI to a spreadsheet.

    This function collects card details from the GUI widgets and saves them to a CSV file
    with the header 'NAME;TYPE;SUBTYPES;LEVEL;IMAGE;ATTACK;DEFENSE;EFFECT1;EFFECT2;SERIAL;RARITY;TRANSPARENCY'.
    Data is appended to the file, and the header is written if the file doesn’t exist.

    Args:
        filename (str): The path to the output CSV file (e.g., 'card_list.csv').

    Returns:
        None: Saves data to the specified CSV file.
    """
    # Collect card data from UI
    card_data = get_card_data()

    # Define the header
    header = ["NAME", "TYPE", "SUBTYPES", "LEVEL", "IMAGE", "ATTACK", "DEFENSE", "EFFECT1", "EFFECT2", "SERIAL", "RARITY", "TRANSPARENCY"]

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
            card_data.get("serial", ""),
            card_data.get("rarity", ""),
            card_data.get("transparency", "")
        ]

        # Write the row to the CSV if it's not a duplicate.
        if not check_line_in_file(filename, ";".join(str(r) for r in row)):
            if not check_for_effect_combination_in_file(filename, row[7], row[8]):
                writer.writerow(row)
                output_text(f"Card data saved to {filename}: {card_data}", "success")
                reset_ui()
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
    WIDGETS["level_combo"].set("1")
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


def update_preview():
    """
    Gather UI input, create a card image, and display it in the preview window.

    This function collects card data from the GUI, generates a card image using create_card,
    saves it to a temporary folder, and updates the preview canvas with the resulting image.
    """
    # Skip preview update during reset
    global SKIP_PREVIEW
    if SKIP_PREVIEW:
        return
        
    # Collect card data from UI
    card_data = get_card_data()
    
    #Set the serial number.
    serial_number = generate_serial_number(card_data)
    update_serial_number(serial_number)

    # Use a temporary folder for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate the card image
        output_file_name = f"{card_data['type'].replace(' ', '_')}_card_{card_data['name'].replace(' ', '_')}-{card_data['transparency']}.png"
        create_card(card_data, temp_dir, output_file_name)
        
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
    value1 = random.randint(-stat_bonus, stat_bonus) * 10
    value2 = random.randint(-stat_bonus, stat_bonus) * 10
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
    level_str = WIDGETS["level_combo"].get().strip()
    card_type = WIDGETS["type_combo"].get().strip().lower()
    level = int(level_str) if level_str in [str(i) for i in range(1, 6)] else 1

    # Clear the entry fields
    WIDGETS["atk_entry"].delete(0, tk.END)
    WIDGETS["def_entry"].delete(0, tk.END)

    # Calculate total points (5 * level)
    if (card_type == "spell"):
        # Get stat bonuses.
        card_atk, card_def = generate_stat_pair(level)
    
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


def generate_effects(effect_buttons, input_file, columns, subtypes):
    """
    Generate 18 random effects and populate the effect buttons.

    This function loads effects from a CSV file, filters them based on specified columns,
    and generates 10 unique random effects: up to 5 using subtypes as search strings,
    and the rest without. If fewer than 5 unique effects match the subtypes, it continues
    with unfiltered effects to reach 10 total, without resetting.

    Args:
        effect_buttons (list): List of ttk.Button objects to populate with effects.
        input_file (str): Path to the input CSV file containing effect data.
        columns (list of str): List of column names to filter on (rows where these are 'True').
        subtypes (list of str): List of selected subtypes to use as search strings for up to 5 effects.
    """
    # Load CSV and filter for rows where specified columns are 'True'
    possible_effect_values = load_and_filter_csv(input_file, columns)
    
    # Track used effects to avoid duplicates
    used_effects = set()
    generated_effects = []

    # Target: Up to 5 effects with subtypes, rest without
    target_with_subtypes = 10

    # Generate up to 5 effects using subtypes as search strings
    if subtypes:  # Only if subtypes are provided
        for _ in range(target_with_subtypes):
            if not possible_effect_values or len(used_effects) >= len(possible_effect_values):
                break  # Stop if no more unique effects are available
            effect = get_random_effect(possible_effect_values, search_strings=subtypes)
            while effect in used_effects:
                effect = get_random_effect(possible_effect_values, search_strings=subtypes)
                if len(used_effects) >= len(possible_effect_values):
                    break  # Avoid infinite loop
            used_effects.add(effect)
            generated_effects.append(effect)

    # Generate remaining effects without search strings (up to 10 total)
    remaining = 18 - len(generated_effects)
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

    # Set the button texts, filling remaining buttons with empty strings if needed
    for i, btn in enumerate(effect_buttons):
        if i < len(generated_effects):
            btn.config(text=generated_effects[i])
        else:
            btn.config(text="")


def assign_effect(effect_text):
    """
    Assign the clicked effect to the first empty effect field.
    """
    current_effect1 = WIDGETS["effect1_entry"].get("1.0", tk.END).strip()
    current_effect2 = WIDGETS["effect2_entry"].get("1.0", tk.END).strip()
    if not current_effect1:
        WIDGETS["effect1_entry"].delete("1.0", tk.END)
        WIDGETS["effect1_entry"].insert("1.0", effect_text)
    elif not current_effect2:
        WIDGETS["effect2_entry"].delete("1.0", tk.END)
        WIDGETS["effect2_entry"].insert("1.0", effect_text)


def generate_serial_number(card_data):
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
            - effect2 (str): Second effect text (e.g., 'Gain 2 life').

    Returns:
        str: A unique serial number (e.g., 'FRA-DRWA-5f3a2b', 'e80b50170989').

    Notes:
        - The serial number should be concise (e.g., 8-12 characters) yet unique.
        - Implementation details (e.g., hash, counter, UUID) are left to the user.
    """
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
    effect2 = card_data.get('effect2', '')
        
    # Placeholder: Combine attributes into a unique string
    attribute_string = (
        f"{name}{card_type}{level}{subtypes}{attack}{defense}{effect1}{effect2}{image}{rarity}"
    )

    output_text(f"Created attribute_string: {attribute_string}", "note")

    # TODO: Implement serial number generation logic here
    serial_number = hashlib.sha256(attribute_string.encode('utf-8')).hexdigest() # Testing with hash
    output_text(f"Created serial_number: {serial_number}", "note")
    
    serial_number = serial_number[:14]
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
    output_text(f"Updating serial number to: {new_serial}", "note")
    WIDGETS["serial_entry"].configure(state="normal")    # Enable editing
    WIDGETS["serial_entry"].delete(0, tk.END)            # Clear current text
    WIDGETS["serial_entry"].insert(0, new_serial)        # Insert new serial
    WIDGETS["serial_entry"].configure(state="disabled")  # Disable again
    output_text(f"Updated serial number!", "success")


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
    selected_level = WIDGETS["level_combo"].get().strip()
    if selected_level in [str(i) for i in range(1, 6)]:  # Validate it’s 1-5
        metadata.append(f"LEVEL_{selected_level}")
    else:
        metadata.append("LEVEL_1")  # Default to 1 if invalid or empty

    return metadata


def update_name_from_image():
    image_path = WIDGETS["image_entry"].get()
    current_name = WIDGETS["name_entry"].get().strip()
    
    if current_name == "Unnamed" and image_path:
        # Check if the image_path points to a valid image file
        try:
            # Attempt to open the image to verify it's valid
            with Image.open(image_path):
                # Extract just the filename without path or extension
                filename = os.path.splitext(os.path.basename(image_path))[0]
                if filename[0] == "_":
                    return # This is the case for un-named images with default hash names.
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
        default="card_list/card_list.csv",
        help="Path to the output CSV file for saving card data. Defaults to 'card_list.csv'."
    )
    
    args = parser.parse_args()
    
    root = tk.Tk()
    root.title("Game Card Creator")

    DPI = 96
    PREVIEW_WIDTH = int(400)
    PREVIEW_HEIGHT = int(580)

    main_frame = ttk.Frame(root, padding="15")
    main_frame.grid(row=0, column=0, sticky="nsew")

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
        values=["Earth", "Fire", "Water", "Air", "Light", "Dark", "Electric", "Nature", "Spell"],
        width=27,
        font=("Helvetica", 12),
    )
    type_combo.grid(row=1, column=1, pady=8, padx=5, sticky="w")
    type_combo.set("Fire")  # Default

    # Subtypes checkboxes
    subtypes_frame = ttk.LabelFrame(left_frame, text="Subtypes", padding="8")
    subtypes_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")
    subtype_vars = [tk.BooleanVar() for _ in range(14)]
    subtype_labels = ["Avian", "Dragon", "Beast", "Elemental", "Aquatic", "Warrior", "Spellcaster", "Machine", "Ghost", "Insect", "Reptile", "Fairy", "Undead", "Botanic"]
    for i, label in enumerate(subtype_labels):
        ttk.Checkbutton(subtypes_frame, text=label, variable=subtype_vars[i]).grid(
            row=i // 3, column=i % 3, padx=8, pady=5, sticky="w"
        )

    # Level dropdown
    ttk.Label(left_frame, text="Level:").grid(row=3, column=0, pady=8, padx=5, sticky="e")
    level_combo = ttk.Combobox(
        left_frame,
        values=[str(i) for i in range(1, 6)],
        width=27,
        font=("Helvetica", 12),
    )
    level_combo.grid(row=3, column=1, pady=8, padx=5, sticky="w")
    level_combo.set("1")
    level_combo.bind(
        "<<ComboboxSelected>>",
        lambda e: [
            randomize_atk_def(),
            update_preview()
        ]
    )

    # Image with browse button
    ttk.Label(left_frame, text="Image:").grid(row=4, column=0, pady=8, padx=5, sticky="e")
    image_entry = ttk.Entry(left_frame, width=30, font=("Helvetica", 12))
    image_entry.grid(row=4, column=1, pady=8, padx=5, sticky="w")    
    browse_btn = ttk.Button(
        left_frame, text="Browse", command=lambda: browse_image()
    )
    browse_btn.grid(row=5, column=1, pady=8, padx=5, sticky="w")
    
    # Add Flip Image button
    flip_btn = ttk.Button(
        left_frame, 
        text="Flip Image", 
        command=lambda: [
            flip_image(image_entry.get()),
            update_preview()
        ]
    )
    flip_btn.grid(row=5, column=1, pady=8, padx=(110, 0), sticky="w")  # Adjusted padx

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
    effect1_entry = tk.Text(left_frame, height=3, width=30, font=("Helvetica", 12))
    effect1_entry.grid(row=9, column=1, pady=8, padx=5, sticky="w")

    # Effect 2
    ttk.Label(left_frame, text="Effect 2:").grid(row=10, column=0, pady=8, padx=5, sticky="e")
    effect2_entry = tk.Text(left_frame, height=3, width=30, font=("Helvetica", 12))
    effect2_entry.grid(row=10, column=1, pady=8, padx=5, sticky="w")

    # Serial Number (non-editable)
    ttk.Label(left_frame, text="Serial #:").grid(row=11, column=0, pady=8, padx=5, sticky="e")
    serial_entry = ttk.Entry(left_frame, width=30, font=("Helvetica", 12))
    serial_entry.insert(0, "AUTO-GENERATED")
    serial_entry.configure(state="disabled")
    serial_entry.grid(row=11, column=1, pady=8, padx=5, sticky="w")

    # Middle Section
    preview_frame = ttk.LabelFrame(main_frame, text="Card Preview", padding="15")
    preview_frame.grid(row=0, column=1, padx=15, sticky="nsew")
    
    #Transparency selection
    transparency_frame = ttk.LabelFrame(preview_frame, text="Transparency", padding="8")
    transparency_frame.grid(row=0, column=0, pady=8, sticky="ew")
    transparency_var = tk.IntVar(value=50)  # Default to 100%

    transparency_values = [50, 60, 75, 100]
    for i, value in enumerate(transparency_values):
        ttk.Checkbutton(
            transparency_frame,
            text=f"{value}%",
            variable=transparency_var,
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
                effect_buttons, args.input_file,
                get_gui_metadata(),
                get_selected_subtypes()
            ),
            update_preview()
        ]
    )
    generate_btn.grid(row=0, column=0, pady=12, padx=10, sticky="ew")  # Increased padding

    # Effect buttons (18)
    effect_buttons = []
    for i in range(18):
        btn = ttk.Button(
            effects_frame,
            text="",
            command=lambda i=i: [
                assign_effect(effect_buttons[i].cget("text")),
                update_preview()
            ]
        )
        btn.grid(row=i + 1, column=0, pady=5, padx=5, sticky="ew")
        effect_buttons.append(btn)

    # Bind additional UI updates
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
        "level_combo": level_combo,
        "name_entry": name_entry,
        "subtype_vars": subtype_vars,
        "subtype_labels": subtype_labels,
        "atk_entry": atk_entry,
        "def_entry": def_entry,
        "effect1_entry": effect1_entry,
        "effect2_entry": effect2_entry,
        "image_entry": image_entry,
        "preview_canvas": preview_canvas,
        "transparency_var": transparency_var,
        "serial_entry" : serial_entry
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
