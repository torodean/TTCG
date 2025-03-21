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

def browse_image(image_entry):
    """Open a file dialog to select an image and update the entry field."""
    filename = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    if filename:
        image_entry.delete(0, tk.END)
        image_entry.insert(0, filename)


def update_preview(
    type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
    atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
):
    """
    Gather UI input, create a card image, and display it in the preview window.

    This function collects card data from the GUI, generates a card image using create_card,
    saves it to a temporary folder, and updates the preview canvas with the resulting image.

    Args:
        type_combo (ttk.Combobox): Widget for card type.
        level_combo (ttk.Combobox): Widget for card level.
        name_entry (ttk.Entry): Widget for card name.
        subtype_vars (list of tk.BooleanVar): List of BooleanVar for subtype checkboxes.
        subtype_labels (list of str): List of subtype labels.
        atk_entry (ttk.Entry): Widget for attack value.
        def_entry (ttk.Entry): Widget for defense value.
        effect1_entry (tk.Text): Widget for first effect text.
        effect2_entry (tk.Text): Widget for second effect text.
        preview_canvas (tk.Canvas): Canvas widget to display the preview.
    """
    # Gather card data from UI
    card_data = {
        "type": type_combo.get().strip() or "Unknown",
        "level": int(level_combo.get().strip() or 1),
        "name": name_entry.get().strip() or "Unnamed",
        "subtype": ", ".join(get_selected_subtypes(subtype_vars, subtype_labels)),
        "attack": atk_entry.get().strip() or "0",
        "defense": def_entry.get().strip() or "0",
        "effect1": effect1_entry.get("1.0", tk.END).strip() or "",
        "effect2": effect2_entry.get("1.0", tk.END).strip() or ""
    }

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
        preview_canvas.delete("all")  # Clear previous content
        preview_canvas.create_image(
            preview_width // 2, preview_height // 2, image=photo
        )
        # Store reference to prevent garbage collection
        preview_canvas.image = photo


def randomize_atk_def(level_combo, atk_entry, def_entry):
    """
    Randomize ATK and DEF values based on the selected level.

    This function generates random ATK and DEF values in increments of 5, ensuring their sum
    equals 5 times the selected level. The values are then populated into the provided entry widgets.

    Args:
        level_combo (ttk.Combobox): The combobox widget containing the selected level (1-5).
        atk_entry (ttk.Entry): The entry widget to populate with the random ATK value.
        def_entry (ttk.Entry): The entry widget to populate with the random DEF value.
    """
    # Get the selected level, default to 1 if empty or invalid
    level_str = level_combo.get().strip()
    level = int(level_str) if level_str in [str(i) for i in range(1, 6)] else 1

    # Calculate total points (5 * level)
    total_points = 500 * level

    # Generate ATK in increments of 5, leaving at least 0 for DEF
    max_atk = total_points  # ATK can be 0 to total_points
    atk = random.randrange(0, max_atk + 5, 5)  # Start at 0, step by 5, inclusive of max_atk

    # DEF is the remainder to ensure atk + def = total_points
    def_ = total_points - atk

    # Clear and populate the entry fields
    atk_entry.delete(0, tk.END)
    atk_entry.insert(0, str(atk))
    def_entry.delete(0, tk.END)
    def_entry.insert(0, str(def_))


def get_selected_subtypes(subtype_vars, subtype_labels):
    """
    Return a list of selected subtype labels based on their BooleanVar states.

    Args:
        subtype_vars (list of tk.BooleanVar): List of BooleanVar objects tied to subtype checkboxes.
        subtype_labels (list of str): List of subtype labels corresponding to the vars.

    Returns:
        list of str: List of selected subtype labels.
    """
    return [label for var, label in zip(subtype_vars, subtype_labels) if var.get()]


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


def assign_effect(effect_text, effect1_entry, effect2_entry):
    """Assign the clicked effect to the first empty effect field."""
    current_effect1 = effect1_entry.get("1.0", tk.END).strip()
    current_effect2 = effect2_entry.get("1.0", tk.END).strip()
    if not current_effect1:
        effect1_entry.delete("1.0", tk.END)
        effect1_entry.insert("1.0", effect_text)
    elif not current_effect2:
        effect2_entry.delete("1.0", tk.END)
        effect2_entry.insert("1.0", effect_text)


def get_gui_metadata(type_combo, level_combo):
    """
    Analyze GUI input and return a list of metadata strings.

    This function checks the selected type and level from the GUI, returning a list containing:
    - 'UNIT' if the type is not 'Spell' (case-insensitive), 'SPELL' if it is.
    - 'LEVEL_#' where # is the selected level (1-5).

    Args:
        type_combo (ttk.Combobox): The combobox widget containing the selected type.
        level_combo (ttk.Combobox): The combobox widget containing the selected level.

    Returns:
        list of str: A list of metadata strings (e.g., ['UNIT', 'LEVEL_3'] or ['SPELL', 'LEVEL_1']).
    """
    metadata = []

    # Get the selected type and determine UNIT or SPELL
    selected_type = type_combo.get().strip().lower()
    if selected_type == "spell":
        metadata.append("SPELL")
    else:
        metadata.append("UNIT")

    # Get the selected level and add LEVEL_#
    selected_level = level_combo.get().strip()
    if selected_level in [str(i) for i in range(1, 6)]:  # Validate it’s 1-5
        metadata.append(f"LEVEL_{selected_level}")
    else:
        metadata.append("LEVEL_1")  # Default to 1 if invalid or empty

    return metadata


def main():
    """Set up and run the Game Card Creator GUI."""
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
    subtype_vars = [tk.BooleanVar() for _ in range(13)]
    subtype_labels = ["Dragon", "Beast", "Elemental", "Aquatic", "Warrior", "Spellcaster", "Machine", "Ghost", "Insect", "Reptile", "Fairy", "Undead", "Botanic"]
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
            randomize_atk_def(level_combo, atk_entry, def_entry),
            update_preview(
                type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
                atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
            )
        ]
    )

    # Image with browse button
    ttk.Label(left_frame, text="Image:").grid(row=4, column=0, pady=8, padx=5, sticky="e")
    image_entry = ttk.Entry(left_frame, width=30, font=("Helvetica", 12))
    image_entry.grid(row=4, column=1, pady=8, padx=5, sticky="w")
    browse_btn = ttk.Button(
        left_frame, text="Browse", command=lambda: browse_image(image_entry)
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
            randomize_atk_def(level_combo, atk_entry, def_entry),
            update_preview(
                type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
                atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
            )
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
                get_gui_metadata(type_combo, level_combo),
                get_selected_subtypes(subtype_vars, subtype_labels)
            ),
            update_preview(
                type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
                atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
            )
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
                assign_effect(effect_buttons[i].cget("text"), effect1_entry, effect2_entry),
                update_preview(
                    type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
                    atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
                )
            ]
        )
        btn.grid(row=i + 1, column=0, pady=5, padx=5, sticky="ew")
        effect_buttons.append(btn)

    # Bind additional UI updates
    type_combo.bind("<<ComboboxSelected>>", lambda e: update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    ))
    name_entry.bind("<FocusOut>", lambda e: update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    ))
    atk_entry.bind("<FocusOut>", lambda e: update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    ))
    def_entry.bind("<FocusOut>", lambda e: update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    ))
    effect1_entry.bind("<FocusOut>", lambda e: update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    ))
    effect2_entry.bind("<FocusOut>", lambda e: update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    ))
    for var in subtype_vars:
        var.trace("w", lambda *args: update_preview(
            type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
            atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
        ))

    # Initial preview update
    update_preview(
        type_combo, level_combo, name_entry, subtype_vars, subtype_labels,
        atk_entry, def_entry, effect1_entry, effect2_entry, preview_canvas
    )

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
