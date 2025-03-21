#!/usr/bin/env python3

import argparse
import tkinter as tk
import random
from tkinter import ttk
from tkinter import filedialog

# Used for randomly generating effects.
from generate_random_effects import load_and_filter_csv
from generate_random_effects import get_random_effect

# Used for generating card preview.
from create_card import create_card
import os
import tempfile
from PIL import Image, ImageTk

# For SN generation
import hashlib

# Global var to determine when preview should be generated vs not.
SKIP_PREVIEW = False


def get_card_data():
    """Collect card data from GUI widgets into a dictionary.

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
    return {
        "type": WIDGETS["type_combo"].get().strip() or "Unknown",
        "level": int(WIDGETS["level_combo"].get().strip() or 1),
        "name": WIDGETS["name_entry"].get().strip() or "Unnamed",
        "subtype": ", ".join(get_selected_subtypes()),
        "attack": WIDGETS["atk_entry"].get().strip() or "0",
        "defense": WIDGETS["def_entry"].get().strip() or "0",
        "effect1": WIDGETS["effect1_entry"].get("1.0", tk.END).strip() or "",
        "effect2": WIDGETS["effect2_entry"].get("1.0", tk.END).strip() or "",
        "image": WIDGETS["image_entry"].get().strip() or "default.png",
        "serial": ""
    }


def save_to_card_list():
    """
    Save card data from the UI to a spreadsheet.

    This function collects card details from the GUI widgets and saves them to a spreadsheet.
    The implementation for saving (e.g., CSV, Excel) is left to be completed.

    Returns:
        None: Saves data to a spreadsheet.
    """
    # Collect card data from UI
    card_data = get_card_data()

    # TODO: Implement spreadsheet saving logic here
    print("Card data to save:", card_data)  # Placeholder for debugging


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
    """Open a file dialog to select an image and update the entry field."""
    filename = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if filename:
        WIDGETS["image_entry"].delete(0, tk.END)
        WIDGETS["image_entry"].insert(0, filename)


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

    # Use a temporary folder for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate the card image
        create_card(card_data, temp_dir)
        
        # Load the generated image
        output_file = f"{temp_dir}/{card_data['type'].replace(' ', '_')}_card_{card_data['name'].replace(' ', '_')}.png"
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


def randomize_atk_def():
    """
    Randomize ATK and DEF values based on the selected level.

    This function generates random ATK and DEF values in increments of 5, ensuring their sum
    equals 5 times the selected level. The values are then populated into the provided entry widgets.
    """
    # Get the selected level, default to 1 if empty or invalid
    level_str = WIDGETS["level_combo"].get().strip()
    level = int(level_str) if level_str in [str(i) for i in range(1, 6)] else 1

    # Calculate total points (5 * level)
    total_points = 500 * level

    # Generate ATK in increments of 5, leaving at least 0 for DEF
    max_atk = total_points  # ATK can be 0 to total_points
    atk = random.randrange(0, max_atk + 5, 5)  # Start at 0, step by 5, inclusive of max_atk

    # DEF is the remainder to ensure atk + def = total_points
    def_ = total_points - atk

    # Clear and populate the entry fields
    WIDGETS["atk_entry"].delete(0, tk.END)
    WIDGETS["atk_entry"].insert(0, str(atk))
    WIDGETS["def_entry"].delete(0, tk.END)
    WIDGETS["def_entry"].insert(0, str(def_))


def get_selected_subtypes():
    """
    Return a list of selected subtype labels based on their BooleanVar states.

    Returns:
        list of str: List of selected subtype labels.
    """
    return [label for var, label in zip(WIDGETS["subtype_vars"], WIDGETS["subtype_labels"]) if var.get()]


def generate_effects(effect_buttons, input_file, columns, subtypes):
    """
    Generate 10 random effects and populate the effect buttons.

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
    target_with_subtypes = 5

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
    remaining = 10 - len(generated_effects)
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
    subtypes = card_data.get('subtypes', [])
    rarity = card_data.get('rarity', '')
    image = card_data.get('image', '')
    attack = card_data.get('attack', '')
    defense = card_data.get('defense', '')
    effect1 = card_data.get('effect1', '')
    effect2 = card_data.get('effect2', '')
        
    # Placeholder: Combine attributes into a unique string
    attribute_string = (
        f"{name}|{card_type}|{' '.join(subtypes)}|{rarity}|"
        f"{image}|{attack}|{defense}|{effect1}|{effect2}"
    )

    # TODO: Implement serial number generation logic here
    #serial_number = "IMPLEMENT_ME"  # TODO
    serial_number = hashlib.sha256(attribute_string.encode('utf-8')).hexdigest()[:14] # Testing with hash
    
    return serial_number


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
        values=["Earth", "Fire", "Water", "Air", "Light", "Dark", "Electric", "Nature"],
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

    # Middle - Preview window
    preview_frame = ttk.LabelFrame(main_frame, text="Card Preview", padding="15")
    preview_frame.grid(row=0, column=1, padx=15, sticky="nsew")
    preview_canvas = tk.Canvas(
        preview_frame,
        width=PREVIEW_WIDTH,
        height=PREVIEW_HEIGHT,
        bg="white",
        highlightthickness=1,
        highlightbackground="black",
    )
    preview_canvas.grid(row=0, column=0)

    # Save to Card List button
    save_btn = ttk.Button(
        preview_frame,
        text="Save to Card List",
        command=lambda: save_to_card_list()
    )
    save_btn.grid(row=1, column=0, pady=8, padx=5, sticky="ew")
    
    # Reset button
    reset_btn = ttk.Button(
        preview_frame,
        text="Reset",
        command=lambda: reset_ui()
    )
    reset_btn.grid(row=2, column=0, pady=8, padx=5, sticky="ew")

    # Right - Effects Generator window
    effects_frame = ttk.LabelFrame(main_frame, text="Effects Generator", padding="15")
    effects_frame.grid(row=0, column=2, padx=15, sticky="nsew")

    # Generate Effects button
    generate_btn = ttk.Button(
        effects_frame,
        text="Generate Effects",
        command=lambda: [
            generate_effects(
                effect_buttons, args.input_file,
                get_gui_metadata(),
                get_selected_subtypes()
            ),
            update_preview()
        ]
    )
    generate_btn.grid(row=0, column=0, pady=8, padx=5, sticky="ew")

    # Effect buttons (10)
    effect_buttons = []
    for i in range(10):
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
    image_entry.bind("<FocusOut>", lambda e: update_preview())
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
        "preview_canvas": preview_canvas  # Include this too, since it’s used often
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
