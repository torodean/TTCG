#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import textwrap
import argparse
import random
import csv
import os

# Import common methods from ttcg_tools.
from ttcg_tools import output_text

# Import constants from ttcg_tools_constants.
from ttcg_constants import VALID_OVERLAY_POSITIONS
from ttcg_constants import VALID_OVERLAY_STYLES
from ttcg_constants import VALID_TRANSLUCENT_VALUES
from ttcg_constants import DEFAULT_CARD_WIDTH
from ttcg_constants import DEFAULT_CARD_HEIGHT


def add_effect_overlay_image(final_img, style, position, width=DEFAULT_CARD_WIDTH, height=DEFAULT_CARD_HEIGHT):
    """
    This method will add an effect overlay to an image.
    
    Args:
        final_image (Image): The image to add the overlay to.
        style (str): The overlay style to use. Valid options are "continuous", 
            "counter", "dormant", "equip", "latent", "passive"
        position (str): The position to place the overlay. This is either the effect 1 
            box or effect two box. Valid options are "top" or "bottom"        
        
    Returns:
        final_image (Image): The image with the added overlay or the original 
            image if the overlay was not successfully added.
    """
    if position not in VALID_OVERLAY_POSITIONS:
        output_text(f"Invalid overlay position argument: {position}", "error")
        output_text(f"Valid overlay positions are: {VALID_OVERLAY_POSITIONS}", "warning")
        return final_img
        
    if style not in VALID_OVERLAY_STYLES:
        output_text(f"Invalid overlay style argument: {style}", "error")
        output_text(f"Valid overlay styles are: {VALID_OVERLAY_STYLES}", "warning")
        return final_img
    
    base_image_path = f"../images/card pngs/{style}-{position}.png"
    try:
        base_img = Image.open(base_image_path).convert("RGBA")
        if base_img.size != (width, height):
            base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
        # Ensure we're using the alpha channel correctly
        final_img = Image.alpha_composite(final_img, base_img)
    except FileNotFoundError:
        # If no type image found, keep just the original
        pass
    
    return final_img


def create_base_card(card_type, 
                     card_level, 
                     width=DEFAULT_CARD_WIDTH, 
                     height=DEFAULT_CARD_HEIGHT, 
                     card_image=None, 
                     transparency=100, 
                     effect1_style=None, 
                     effect2_style=None):
    """
    Creates the base card image based on type and level, with a type-specific background
    and a level-specific overlay, and an optional card image behind everything resized to width.
    
    Args:
        card_type (str): The type of the card.
        card_level (int): The level of the card.
        width (int): The width of the card (Defaults to 750).
        height (int): The height of the card (Defaults to 1050).
        card_image (str): The main image to use behind the card. (Defaults to None).
        transparency (int): The transparency to use for minor features of the card art. 
        effect1_style (str): The style to use for effect one.
        effect2_style (str): The style to use for effect two.
    
    Returns:
        Image: The base card image with optional background image, type background, and level overlay.
    """
    # Start with transparent canvas
    final_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Add card_image as bottom layer if provided, resized to width only
    if card_image:
        try:
            bg_img = Image.open(card_image).convert("RGBA")
            if bg_img.size != (width, height):
                # Calculate new height maintaining aspect ratio
                aspect_ratio = bg_img.size[1] / bg_img.size[0]
                new_height = int(width * aspect_ratio)
                bg_img = bg_img.resize((width, new_height), Image.Resampling.LANCZOS)
            final_img.paste(bg_img, (0, 0), bg_img)
        except FileNotFoundError:
            pass

    # Get base image based on type (case-insensitive)
    if transparency == 100:
        base_image_path = f"../images/card pngs/{card_type.lower()}.png"
    else:
        base_image_path = f"../images/card pngs/{card_type.lower()}-{transparency}.png"
        
    # Print base image path for debugging.
    output_text(f"base_image_path set to: {base_image_path}", "note")
        
    try:
        base_img = Image.open(base_image_path).convert("RGBA")
        if base_img.size != (width, height):
            base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
        # Ensure we're using the alpha channel correctly
        final_img = Image.alpha_composite(final_img, base_img)
    except FileNotFoundError:
        # If no type image found, keep just the card_image or transparent
        pass
        
    if effect1_style is not None:
        final_img = add_effect_overlay_image(final_img, effect1_style, "top")
        
    if effect2_style is not None:
        final_img = add_effect_overlay_image(final_img, effect2_style, "bottom")

    # Overlay level-specific PNG
    level_image_path = f"../images/card pngs/{card_level} star.png"
    try:
        level_img = Image.open(level_image_path).convert("RGBA")
        if level_img.size != (width, height):
            level_img = level_img.resize((width, height), Image.Resampling.LANCZOS)
        # Use alpha_composite for level overlay too
        final_img = Image.alpha_composite(final_img, level_img)
    except FileNotFoundError:
        # No overlay if level image not found
        pass

    return final_img


def squish_text_horizontally(text, font_path, font_size, squish_factor, output_path):
    """
    Squishes text horizontally using Pillow.

    Args:
        text (str): The text to squish.
        font_path (str): Path to the font file.
        font_size (int): Font size.
        squish_factor (float): Horizontal squish factor (e.g., 0.5 for half width).
        output_path (str): Path to save the output image.
    """
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = font.getsize(text)

    image = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill="black")

    # Affine transformation matrix for horizontal squishing
    # (a, b, c, d, e, f) corresponds to (x_scale, x_shear, x_translate, y_shear, y_scale, y_translate)
    affine_matrix = (squish_factor, 0, 0, 0, 1, 0)

    # Transform the image
    squished_image = image.transform(image.size, Image.AFFINE, affine_matrix, resample=Image.BILINEAR)

    squished_image.save(output_path)


def draw_single_line_text(draw, text, top_left, bottom_right, initial_font_size=50, color=(0, 0, 0, 255), center=False):
    """
    Draws text within a box defined by top-left and bottom-right corners, auto-adjusting
    font size to fit vertically and squishing horizontally if too wide, without wrapping.
    
    Args:
        draw (ImageDraw.Draw): The drawing context for the image.
        text (str): The text to draw.
        top_left (tuple): (x, y) coordinates of the top-left corner of the box.
        bottom_right (tuple): (x, y) coordinates of the bottom-right corner of the box.
        initial_font_size (int): Starting font size to try (default 50).
        color (tuple): RGBA color tuple (default black: (0, 0, 0, 255)).
        center (bool): If True, centers text vertically and horizontally (default False).
    """
    # Calculate box dimensions
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Adjust box height for descender characters
    if any(char in text for char in 'qypjg'):
        y2 += 5
        
    box_width = x2 - x1
    box_height = y2 - y1

    # Use DejaVu Sans font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        font = ImageFont.truetype(font_path, initial_font_size)
    except:
        font = ImageFont.load_default()
        initial_font_size = 12  # Default font is small, approximate size

    # Start with initial font size and adjust downward for height
    font_size = initial_font_size
    while font_size > 1:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

        # Measure text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Check vertical fit
        if text_height <= box_height:
            if text_width <= box_width:
                # Fits naturally, no squishing
                if center:
                    x_offset = (box_width - text_width) // 2
                    y_offset = (box_height - text_height) // 2
                    draw.text((x1 + x_offset, y1 + y_offset), text, font=font, fill=color)
                else:
                    draw.text((x1, y1), text, font=font, fill=color)
            else:
                # Create temp image for text
                temp_img = Image.new("RGBA", (text_width, box_height + 20), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((0, 0), text, font=font, fill=color)

                # Calculate squish factor
                squish_factor = text_width / box_width  # Note: This seems reversed; should be box_width / text_width
                affine_matrix = (squish_factor, 0, 0, 0, 1, 0)  # Horizontal scale only

                # Squish the text
                squished_img = temp_img.transform((box_width, box_height + 20), Image.AFFINE, affine_matrix, resample=Image.BILINEAR)
                
                # Center horizontally and vertically if requested
                if center:
                    x_offset = (box_width - box_width) // 2  # box_width after squishing
                    y_offset = (box_height - text_height) // 2  # Use text_height for vertical centering
                    draw._image.paste(squished_img, (x1 + x_offset, y1 + y_offset), squished_img)
                else:
                    draw._image.paste(squished_img, (x1, y1), squished_img)
            return
        else:
            font_size -= 1  # Reduce size for height

    # Fallback: Smallest size, squish if needed
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    temp_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((0, 0), text, font=font, fill=color)
    squish_factor = box_width / text_width if text_width > box_width else 1
    affine_matrix = (squish_factor, 0, 0, 0, 1, 0)
    squished_img = temp_img.transform((int(text_width * squish_factor), text_height), Image.AFFINE, affine_matrix, resample=Image.BILINEAR)
    draw._image.paste(squished_img, (x1, y1), squished_img)


def draw_wrapped_text(draw, text, top_left, bottom_right, initial_font_size=50, color=(0, 0, 0, 255)):
    """
    Draws wrapped text within a box defined by top-left and bottom-right corners,
    auto-adjusting font size to fit vertically, with text centered both spatially
    (vertically and horizontally in the box) and in alignment (each line center-aligned).
    
    Args:
        draw (ImageDraw.Draw): The drawing context for the image.
        text (str): The text to draw.
        top_left (tuple): (x, y) coordinates of the top-left corner of the box.
        bottom_right (tuple): (x, y) coordinates of the bottom-right corner of the box.
        initial_font_size (int): Starting font size to try (default 50).
        color (tuple): RGBA color tuple (default black: (0, 0, 0, 255)).
    """
    import textwrap

    # Calculate box dimensions
    x1, y1 = top_left
    x2, y2 = bottom_right        
    box_width = x2 - x1
    box_height = y2 - y1

    # Use DejaVu Sans font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        font = ImageFont.truetype(font_path, initial_font_size)
    except:
        font = ImageFont.load_default()
        initial_font_size = 12  # Default font is small, approximate size

    # Start with initial font size and adjust downward for height
    font_size = initial_font_size
    while font_size > 1:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

        # Wrap text to fit box width
        wrapped_text = textwrap.fill(text, width=int(box_width / (font_size * 0.5)))  # Rough chars-per-line estimate
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Check vertical and horizontal fit
        if text_height <= box_height and text_width <= box_width:
            # Center the wrapped text
            x_offset = (box_width - text_width) // 2
            y_offset = (box_height - text_height) // 2
            draw.text((x1 + x_offset, y1 + y_offset), wrapped_text, font=font, fill=color, align="center")
            return
        else:
            font_size -= 1  # Reduce size if too tall or wide

    # Fallback: Smallest size
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    wrapped_text = textwrap.fill(text, width=int(box_width / (font_size * 0.5)))
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x_offset = (box_width - text_width) // 2
    y_offset = (box_height - text_height) // 2
    draw.text((x1 + x_offset, y1 + y_offset), wrapped_text, font=font, fill=color, align="center")


def create_card(card_data, output_folder, output_file_name=None):
    """
    Creates a TTCG trading card image with specified details and saves it to a file.

    This function generates a 750x1050 pixel card image based on the provided card data,
    including type, level, name, subtype, attack, defense, and effects. It uses a base image
    determined by the card type and level, overlays text in designated areas, and saves the
    result as a PNG file in the specified output folder.

    Args:
        card_data (dict): A dictionary containing card details with the following keys:
            - type (str): Card type (e.g., 'fire') used to select the base image.
            - level (int): Card level (1-5) for the star overlay.
            - name (str): Card name, drawn in a box at the top.
            - subtype (str): Card subtype(s), drawn below the name.
            - attack (str): Attack value, drawn in a box (converted to string if numeric).
            - defense (str): Defense value, drawn in a box (converted to string if numeric).
            - effect1 (str): First effect text, drawn as wrapped text.
            - effect2 (str): Second effect text, drawn as wrapped text.
            - image (str): The image file for this card.
            - serial (str): The serial number for this card.
        output_folder (str): Path to the folder where the card image will be saved.
        output_file_name (str): An optional output file name to use. This should not include the output folder path.

    Returns:
        None: The function saves the card image to a file and prints the file path.

    Notes:
        - The card dimensions are fixed at 750x1050 pixels (2.5" x 3.5" at 300 DPI).
        - Text is drawn in specific boxes using helper functions (`create_base_card`,
          `draw_single_line_text`, `draw_wrapped_text`), which are assumed to be defined elsewhere.
        - The output file is named `<type>_<name>.png`, with spaces in the name replaced by underscores.
    """
    # TTCG card dimensions: 2.5" x 3.5" at 300 DPI = 750 x 1050 pixels
    width, height = DEFAULT_CARD_WIDTH, DEFAULT_CARD_HEIGHT
    
    img = create_base_card(card_data["type"], 
                           card_data["level"], 
                           width, 
                           height, 
                           card_data["image"], 
                           card_data["transparency"],
                           card_data["effect1_style"],
                           card_data["effect2_style"])
    draw = ImageDraw.Draw(img)

    # Draw name in a box from (70, 35) to (585, 70)
    draw_single_line_text(draw, card_data["name"], (70, 35), (585, 70))
    
    # Draw subtypes in a box from (70, 90) to (585, 120)
    card_type = card_data["type"]
    card_subtype = card_data["subtype"]
    if card_type == "Spell":
        subtypes_line = f"{card_type}"
    else:
        subtypes_line = f"{card_type}, {card_subtype}"
    draw_single_line_text(draw, subtypes_line, (70, 90), (585, 120))
    
    # Draw ATK and def in the boxes.
    atk_x_min, atk_x_max = 135, 215    
    atk_y_min, atk_y_max = 628, 665
    draw_single_line_text(draw, 
                          card_data["attack"], 
                          (atk_x_min, atk_y_min), 
                          (atk_x_max, atk_y_max), 
                          initial_font_size=50, 
                          center=True)
    draw_single_line_text(draw, card_data["defense"], 
                          (width - atk_x_max, atk_y_min), 
                          (width - atk_x_min, atk_y_max), 
                          initial_font_size=50, 
                          center=True)
    
    # Draw effects in boxes.
    draw_wrapped_text(draw, card_data["effect1"], (70, 710), (680, 810), initial_font_size=30)
    draw_wrapped_text(draw, card_data["effect2"], (70, 870), (680, 970), initial_font_size=30)
    
    # Draw the serial number and trademark.
    draw_single_line_text(draw, card_data["serial"], (550, 1007), (722, 1022), initial_font_size=20)
    draw_single_line_text(draw, "© True Trading Card Game Company", (31, 1007), (600, 1022), initial_font_size=20)

    # Create the output card name.
    if output_file_name == None:
        output_file = f"{output_folder}/{card_data['type'].replace(' ', '_')}_card_{card_data['name'].replace(' ', '_')}.png"
    else:
        output_file = f"{output_folder}/{output_file_name}"        

    # Save the card
    img.save(output_file)
    output_text(f"Card saved as {output_file}", "success")


def process_csv_to_cards(csv_file_path, output_folder):
    """
    Read a CSV file of card data and create cards by calling create_card for each entry.

    Args:
        csv_file_path (str): Path to the CSV file containing card data.
        output_folder: The folder to output images to.

    Returns:
        None

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file format is invalid (e.g., wrong number of columns).

    The CSV file is expected to have the following columns in order:
    NAME;TYPE;SUBTYPES;LEVEL;IMAGE;ATTACK;DEFENSE;EFFECT1;EFFECT2;SERIAL;RARITY;TRANSPARENCY

    For each row, it constructs a card_data dictionary and calls create_card(card_data, args.output).
    """
    if not os.path.isfile(csv_file_path):
        raise FileNotFoundError(f"The CSV file '{csv_file_path}' does not exist")

    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        # Use semicolon as delimiter
        csv_reader = csv.reader(csvfile, delimiter=';')
        
        # Skip header row if present (assuming first row is header)
        header = next(csv_reader)
        expected_columns = 12  # NAME;TYPE;SUBTYPES;LEVEL;IMAGE;ATTACK;DEFENSE;EFFECT1;EFFECT2;SERIAL;RARITY;TRANSPARENCY
        if len(header) != expected_columns:
            raise ValueError(f"CSV header has {len(header)} columns, expected {expected_columns}")

        # Process each row
        for row in csv_reader:
            if len(row) != expected_columns:
                raise ValueError(f"Row has {len(row)} columns, expected {expected_columns}")

            # Extract data from the row
            name, card_type, subtypes, level, image, attack, defense, effect1, effect2, serial, rarity, transparency = row

            # Handle subtypes (convert to string, could be empty or comma-separated)
            subtype_str = subtypes if subtypes else ""

            # Create card data dictionary
            card_data = {
                "name": name,
                "level": level,
                "type": card_type,
                "subtype": subtype_str,
                "attack": attack,
                "defense": defense,
                "effect1": effect1,
                "effect2": effect2,
                "image": image,
                "transparency": transparency,
                "serial": serial
            }

            # Call create_card with the constructed card_data and args.output
            create_card(card_data, output_folder)


def parse_args():
    """
    A method for parsing the script arguments.
    """
    parser = argparse.ArgumentParser(description="Create a TTCG trading card.")
    parser.add_argument('-l', "--level", type=int, default=1, choices=range(1, 6),
                        help="Card level (1-5)")
    parser.add_argument('-t', "--type", type=str, default="fire",
                        help="Card type (e.g., earth, air, fire, water, etc)")
    parser.add_argument('-n', "--name", type=str, default="Card Name",
                        help="Card name.")
    parser.add_argument('-s', "--subtype", type=str, nargs="+", default=["Dragon", "Warrior"],
                        help="Subtypes (space-separated, e.g., Dragon Spirit)")
    parser.add_argument('-1', "--effect1", type=str, default="Effect 1",
                        help="First effect text.")
    parser.add_argument("--effect1_style", type=str, default=None,
                        help=f"First effect style. Valid styles are {VALID_OVERLAY_STYLES}")
    parser.add_argument('-2', "--effect2", type=str, default="Effect 2",
                        help="Second effect text.")
    parser.add_argument("--effect2_style", type=str, default=None,
                        help="Second effect style. Valid styles same as effect1_style.")
    parser.add_argument('-a', "--attack", type=int, default=None,
                        help="Attack value (defaults to random based on level).")
    parser.add_argument('-d', "--defense", type=int, default=None,
                        help="Defense value (defaults to random based on level, sums with atk to level*500)")
    parser.add_argument('-i', "--image", type=str, default=None,
                        help="The image file for this card.")
    parser.add_argument('-o', "--output", type=str, default="../images/generated_cards",
                        help="The folder to output images to.")
    parser.add_argument("--serial", type=str, default="ABCD1234567890",
                        help="The serial number for the card.")
    parser.add_argument('-T', "--transparency", type=int, default=100,
                        help="The transparency of some card art fields (valid options are 50, 60, 75, and 100).")
    parser.add_argument('-S', "--spreadsheet", type=str, default=None,
                        help="Create's all cards loaded from a spreadsheet (in dev).")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    # Run the complete processing for a csv file.
    if args.spreadsheet is not None:
        process_csv_to_cards(args.spreadsheet, args.output)
        exit(1)

    # Handle random atk/def based on level
    total_stats = args.level * 100
    if args.attack is None and args.defense is None:
        attack = random.randint(0, total_stats)*5
        defense = total_stats*5 - attack
    elif args.attack is None:
        attack = total_stats - args.defense
    elif args.defense is None:
        defense = total_stats - args.attack
    else:
        attack = args.attack
        defense = args.defense

    # Make sure the transparency option is valid.
    if args.transparency not in VALID_TRANSLUCENT_VALUES:
        output_text(f"Invalid transparency option entered: {args.transparency}")
        args.transparency = 100

    # Construct type string with subtype
    subtype_str = ""
    if args.subtype:
        subtype_str += ", ".join(args.subtype)

    # Create card data dictionary
    card_data = {
        "name": args.name,
        "level": args.level,
        "type": args.type,
        "subtype": subtype_str,
        "attack": str(attack),
        "defense": str(defense),
        "effect1": args.effect1,
        "effect1_style": args.effect1_style,
        "effect2": args.effect2,
        "effect2_style": args.effect2_style,
        "image": args.image,
        "transparency": args.transparency,
        "serial": args.serial
    }

    create_card(card_data, args.output)
