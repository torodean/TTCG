#!/bin/python3

import argparse
import os
from PIL import Image
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas

# For progress/status messages.
from tqdm import tqdm

# Import methods from ttcg_tools
from ttcg_tools import output_text

# Import needed constants from the ttcg_constants file.
from ttcg_constants import DEFAULT_GENERATED_CARDS_FOLDER
from ttcg_constants import DEFAULT_GENERATED_CARDS_PDF


def get_page_size(size_name):
    """
    Return page size tuple based on the specified name.

    Args:
        size_name (str): Name of the page size ('letter' or 'A4').

    Returns:
        tuple: (width, height) in points for the specified page size.
    """
    sizes = {'letter': letter, 'A4': A4}
    return sizes.get(size_name.lower(), letter)


def get_image_files(input_folder):
    """
    Retrieve a list of image files from the input folder.

    Args:
        input_folder (str): Path to the folder containing images.

    Returns:
        list: List of filenames with .png, .jpg, or .jpeg extensions (case-insensitive).
    """
    return [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]


def create_pdf(input_folder, output_file, page_size_name):
    """
    Create a PDF with images arranged in a 3x3 grid, with no gaps between images.

    Images are placed edge-to-edge within the grid, with margins calculated to center
    the grid on the specified page size. Assumes all images have the same size.

    Args:
        input_folder (str): Path to the folder containing input images.
        output_file (str): Path where the output PDF will be saved.
        page_size_name (str): Page size ('letter' or 'A4').
    """
    # Initialize PDF
    page_size = get_page_size(page_size_name)
    c = canvas.Canvas(output_file, pagesize=page_size)
    page_width, page_height = page_size

    # Get image files
    image_files = get_image_files(input_folder)
    if not image_files:
        output_text("ERROR: No images found in the input folder!", "error")
        return

    # Set fixed dimensions for MTG card size (2.5 x 3.5 inches at 72 points/inch)
    img_width = 2.5 * 72  # 180 points
    img_height = 3.5 * 72  # 252 points

    # Calculate margins to center the 3x3 grid (no gaps between images)
    total_grid_width = 3 * img_width
    total_grid_height = 3 * img_height
    margin_x = (page_width - total_grid_width) / 2    # Split remaining space into left and right margins
    margin_y = (page_height - total_grid_height) / 2  # Split remaining space into top and bottom margins

    # Validate that the grid fits the page
    if margin_x < 0 or margin_y < 0:
        output_text(f"ERROR: 3x3 grid of MTG-sized cards (7.5 x 10.5 inches) does not fit on {page_size_name} page.", "error")
        return

    cards_per_page = 0
    row, col = 0, 0

    for img_file in tqdm(image_files, desc=f"Processing images"):
        img_path = os.path.join(input_folder, img_file)
        try:
            img = Image.open(img_path)

            # Calculate position (3x3 grid with no gaps)
            x = margin_x + col * img_width
            y = page_height - margin_y - (row + 1) * img_height

            # Draw image at its original size
            c.drawImage(img_path, x, y, img_width, img_height)
            cards_per_page += 1

            # Update grid position
            col += 1
            if col == 3:
                col = 0
                row += 1

            # Start new page if 9 cards are placed
            if cards_per_page == 9:
                c.showPage()
                row, col = 0, 0
                cards_per_page = 0

        except Exception as e:
            output_text(f"Error processing {img_file}: {e}")

    # Save PDF if any cards were added
    if cards_per_page > 0 or len(image_files) > 0:
        c.save()
        output_text(f"PDF created successfully at {output_file}", "success")
    else:
        output_text("WARNING: No valid images processed, PDF not created.", "warning")


def main():
    """
    Parse command-line arguments and generate a PDF from images.

    Accepts input folder, output file path, and page size as arguments, with defaults
    from ttcg_constants, a placeholder output path, and letter page size.
    """
    parser = argparse.ArgumentParser(description="Generate a PDF from images in a 3x3 grid with no gaps.")
    parser.add_argument('-i', '--input-folder', type=str, default=DEFAULT_GENERATED_CARDS_FOLDER,
                        help=f'Folder containing input images. Defaults to {DEFAULT_GENERATED_CARDS_FOLDER}')
    parser.add_argument('-o', '--output-file', type=str, default=DEFAULT_GENERATED_CARDS_PDF,  # Placeholder, replace with your constant
                        help=f'Output PDF file path. Defaults to: {DEFAULT_GENERATED_CARDS_PDF}')
    parser.add_argument('-s', '--page-size', type=str, default='letter', choices=['letter', 'A4'],
                        help='Page size for the PDF (letter or A4)')

    args = parser.parse_args()

    # Ensure input folder exists
    if not os.path.isdir(args.input_folder):
        output_text(f"ERROR: Input folder {args.input_folder} does not exist.", "error")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output_file) or '.', exist_ok=True)

    create_pdf(args.input_folder, args.output_file, args.page_size)

if __name__ == "__main__":
    main()
