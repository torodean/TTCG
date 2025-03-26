#!/bin/python3

import argparse
from PIL import Image
from ttcg_tools import output_text

def flip_image(input_path, output_path=None):
    """Flip an image horizontally and save it to a new file.

    Args:
        input_path (str): Path to the input image file
        output_path (str, optional): Path where the flipped image will be saved. 
                                   Defaults to None, which uses input_path.

    Raises:
        Exception: If there's an error opening or processing the image
    """
    try:
        # If output_path is None, use input_path
        if output_path is None:
            output_path = input_path
            
        # Open the input image
        with Image.open(input_path) as img:
            # Flip the image horizontally
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            # Save the flipped image
            flipped_img.save(output_path)
            output_text(f"Image successfully flipped and saved as {output_path}", "success")
    except Exception as e:
        output_text(f"Error processing image: {str(e)}", "error")

def main():
    """Parse command line arguments and execute image flipping."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Flip an image horizontally')
    parser.add_argument('input_file', 
                       help='Path to the input image file')
    parser.add_argument('-o', '--output',
                       default=None,
                       help='Path for the output flipped image (default: same as input)')

    # Parse arguments
    args = parser.parse_args()

    # Flip the image
    flip_image(args.input_file, args.output)

if __name__ == '__main__':
    main()
