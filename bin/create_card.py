#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import textwrap
import argparse
import random


def create_base_card(card_type, card_level, width=750, height=1050, card_image=None):
    """
    Creates the base card image based on type and level, with a type-specific background
    and a level-specific overlay.
    
    Args:
        card_type (str): The type of the card.
        card_level (int): The level of the card.
        width (int): The width of the card (Defaults to 750).
        height (int): The height of the card (Defaults to 1050).
        card_image (str): The main image to use for the card. (Defaults to None for testing).
    
    Returns:
        Image: The base card image with type background and level overlay.
    """
    # Get base image based on type (case-insensitive)
    base_image_path = f"../images/card pngs/{card_type.lower()}.png"
    try:
        base_img = Image.open(base_image_path).convert("RGBA")
        if base_img.size != (width, height):
            base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
    except FileNotFoundError:
        # Fallback to white background if image not found
        base_img = Image.new("RGBA", (width, height), (255, 255, 255, 255))

    # Overlay level-specific PNG
    level_image_path = f"../images/card pngs/{card_level} star.png"
    try:
        level_img = Image.open(level_image_path).convert("RGBA")
        if level_img.size != (width, height):
            level_img = level_img.resize((width, height), Image.Resampling.LANCZOS)
        base_img.paste(level_img, (0, 0), level_img)  # Overlay with transparency
    except FileNotFoundError:
        # No overlay if level image not found
        pass

    return base_img


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


def create_card(card_data, output_folder):
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

    Returns:
        None: The function saves the card image to a file and prints the file path.

    Notes:
        - The card dimensions are fixed at 750x1050 pixels (2.5" x 3.5" at 300 DPI).
        - Text is drawn in specific boxes using helper functions (`create_base_card`,
          `draw_single_line_text`, `draw_wrapped_text`), which are assumed to be defined elsewhere.
        - The output file is named `<type>_<name>.png`, with spaces in the name replaced by underscores.
    """
    # TTCG card dimensions: 2.5" x 3.5" at 300 DPI = 750 x 1050 pixels
    width, height = 750, 1050
    
    img = create_base_card(card_data["type"], card_data["level"], width, height)
    draw = ImageDraw.Draw(img)

    # Draw name in a box from (70, 35) to (585, 70)
    draw_single_line_text(draw, card_data["name"], (70, 35), (585, 70))
    
    # Draw subtypes in a box from (70, 90) to (585, 120)
    draw_single_line_text(draw, card_data["subtype"], (70, 90), (585, 120))
    
    # Draw ATK and def in the boxes.
    atk_x_min, atk_x_max = 135, 215    
    atk_y_min, atk_y_max = 628, 665
    draw_single_line_text(draw, card_data["attack"], (atk_x_min, atk_y_min), (atk_x_max, atk_y_max), initial_font_size=50, center=True)
    draw_single_line_text(draw, card_data["defense"], (width - atk_x_max, atk_y_min), (width - atk_x_min, atk_y_max), initial_font_size=50, center=True)
    
    # Draw effects in boxes.
    draw_wrapped_text(draw, card_data["effect1"], (70, 710), (680, 810), initial_font_size=30)
    draw_wrapped_text(draw, card_data["effect2"], (70, 870), (680, 970), initial_font_size=30)
    
    # Draw the serial number and trademark.
    draw_single_line_text(draw, card_data["serial"], (550, 1007), (722, 1022), initial_font_size=20)
    draw_single_line_text(draw, "© True Trading Card Game Company", (31, 1007), (600, 1022), initial_font_size=20)

    # Save the card
    output_file = f"{output_folder}/{card_data['type'].replace(' ', '_')}_card_{card_data['name'].replace(' ', '_')}.png"
    img.save(output_file)
    print(f"Card saved as {output_file}")


def parse_args():
    """
    A method for parsing the script arguments.
    """
    parser = argparse.ArgumentParser(description="Create a TTCG trading card.")
    parser.add_argument('-l', "--level", type=int, default=1, choices=range(1, 6),
                        help="Card level (1-5)")
    parser.add_argument('-t', "--type", type=str, default="fire",
                        help="Card type (e.g., Creature, Artifact)")
    parser.add_argument('-n', "--name", type=str, default="Card Name",
                        help="Card name")
    parser.add_argument('-s', "--subtype", type=str, nargs="+", default=["Dragon", "Warrior"],
                        help="Subtypes (space-separated, e.g., Dragon Spirit)")
    parser.add_argument('-1', "--effect1", type=str, default="Effect 1",
                        help="First effect text")
    parser.add_argument('-2', "--effect2", type=str, default="Effect 2",
                        help="Second effect text")
    parser.add_argument('-a', "--attack", type=int, default=None,
                        help="Attack value (defaults to random based on level)")
    parser.add_argument('-d', "--defense", type=int, default=None,
                        help="Defense value (defaults to random based on level, sums with atk to level*500)")
    parser.add_argument('-i', "--image", type=str, default="image.png",
                        help="The image file for this card.")
    parser.add_argument('-o', "--output", type=str, default="../images/generated_cards",
                        help="The folder to output images to.")
    parser.add_argument("--serial", type=str, default="ABCD1234567890",
                        help="The serial number for the card.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

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
        "effect2": args.effect2,
        "image": args.image,
        "serial": args.serial
    }

    create_card(card_data, args.output)
