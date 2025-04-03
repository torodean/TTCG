#!/bin/python3

import argparse
import csv
from card_maker_ui import generate_serial_number
from card_maker_ui import initialize_preprocessing
from ttcg_constants import DEFAULT_CARD_LIST_FILE


def regenerate_serial_numbers(input_file):
    """
    Read a card database file, regenerate serial numbers, and save the updated data.
    
    Args:
        input_file (str): Path to the input card database file.
    """
    # Read the card database
    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile, delimiter=';')
        headers = next(reader)  # Assuming a header row exists.
        
        updated_cards = []
        for row in reader:
            # Map row data to card_data dictionary expected by generate_serial_number
            card_data = {
                'name': row[0],
                'type': row[1],
                'subtypes': row[2],
                'level': int(row[3]),
                'image': row[4],
                'attack': int(row[5]),
                'defense': int(row[6]),
                'effect1': row[7],
                'effect2': row[8],
                'serial': row[9],  # Original serial, will be overwritten
                'rarity': row[10],
                'transparency': row[11],
                'effect1_style': row[12],
                'effect2_style': row[13]
            }
            
            # Regenerate serial number using the imported function
            new_serial = generate_serial_number(card_data, True)
            
            # Update the row with the new serial number
            row[9] = new_serial
            updated_cards.append(row)
    
    # Write the updated data to a new file
    output_file = input_file.replace('.csv', '_updated.csv')  # Avoids overwriting original
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(headers)  # Write headers if present
        writer.writerows(updated_cards)
    
    print(f"Serial numbers regenerated and saved to {output_file}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Regenerate serial numbers for a card database.")
    parser.add_argument('--input_file', type=str, default=DEFAULT_CARD_LIST_FILE,
                        help=f'Path to the card database file (default: {DEFAULT_CARD_LIST_FILE})')
    
    args = parser.parse_args()
    
    # Initialize the pre-processing.
    initialize_preprocessing()
    
    # Regenerate serial numbers
    regenerate_serial_numbers(args.input_file)

if __name__ == "__main__":
    main()
