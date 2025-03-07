#!/bin/bash

# Cleanup old files
rm -rf effects/all_effects.txt
rm -rf effects/effects/effects_with_placeholders.csv

# Create the base list of all effects.
./create_effect_combinations.py -f
sleep 1

# Generate csv, and add UNIT to csv.
./add_csv_field.py -c UNIT -t "<subtype> " -i "effects/all_effects.txt"
sleep 1 # Give the file time to generate.
./add_csv_field.py -c SPELL -t "<type> "

# Add rank specific columns.
# Creature effects can typically have the rank of that creature, one higher, 


# Add some spell specific effects.
./add_csv_field.py -c SPELL -t "Your opponent loses <number> point"
./add_csv_field.py -c SPELL -t "Gain <number> point"
./add_csv_field.py -c SPELL -t "Both players"
./add_csv_field.py -c SPELL -t "Add <number> rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Add <number> rank <rank> or higher <card>"
./add_csv_field.py -c SPELL -t "Add <number> rank <rank> or lower <card>"
./add_csv_field.py -c SPELL -t "Counter the effect of a rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Destroy all rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Destroy exactly <number> <card>"
./add_csv_field.py -c SPELL -t "Destroy up to <number> <card>"
./add_csv_field.py -c SPELL -t "Destroy exactly <number> rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Destroy up to <number> rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Destroy <number> rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Discard <number> rank <rank> <card> from your hand"
./add_csv_field.py -c SPELL -t "Discard <number> rank <rank> <card> card from your hand"
./add_csv_field.py -c SPELL -t "Discard this card to add one <card>"
./add_csv_field.py -c SPELL -t "Discard this card to add one rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Discard this card to add one rank <rank> or higher <card>"
./add_csv_field.py -c SPELL -t "Discard this card to add one rank <rank> or lower <card>"
./add_csv_field.py -c SPELL -t "Draw <number> card"
./add_csv_field.py -c SPELL -t "Lose <number> point"
./add_csv_field.py -c SPELL -t "Return one rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Reveal the top card of your deck and play one rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Reveal the top <number> cards of your deck and play one rank <rank> <card>"
./add_csv_field.py -c SPELL -t "This turn, all rank <rank> <card>"
./add_csv_field.py -c SPELL -t "This turn, increase the rank of one rank <rank> <card>"
./add_csv_field.py -c SPELL -t "While this card is on the field, all rank <rank> <card>"
./add_csv_field.py -c SPELL -t "Add <number> <card>"
./add_csv_field.py -c SPELL -t "Discard one rank <rank> <card>"


# Add some unit specific effects.
./add_csv_field.py -c UNIT -t "You can send <number> card"
./add_csv_field.py -c UNIT -t "When this card is sent to the discard pile"
./add_csv_field.py -c UNIT -t "Destroy this card to"
./add_csv_field.py -c UNIT -t "Lose <number> point"
./add_csv_field.py -c UNIT -t "You can play one extra rank <rank> <card>"


#Handle some exact matches (used for one off effects)
./add_csv_field.py -c SPELL -e "While this card is on the field, attack and defense changes are inverted."
./add_csv_field.py -c UNIT -e "While this card is on the field, attack and defense changes are inverted."
