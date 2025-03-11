#!/bin/bash

# Cleanup old files
rm -rf effects/all_effects.txt
rm -rf effects/effects_with_placeholders.csv

# Create the base list of all effects.
python3 create_effect_combinations.py -f
sleep 1

# Generate csv, and add UNIT to csv.
python3 add_csv_field.py -c UNIT -t "<subtype> " -i "effects/all_effects.txt"
sleep 1 # Give the file time to generate.
python3 add_csv_field.py -c SPELL -t "<type> "

# Add rank specific columns.
# Creature effects can typically have the rank of that creature, one higher, etc.
# TODO


# Add some spell specific effects.
python3 add_csv_field.py -c SPELL -t "Your opponent loses <number> point"
python3 add_csv_field.py -c SPELL -t "Gain <number> point"
python3 add_csv_field.py -c SPELL -t "Both players"
python3 add_csv_field.py -c SPELL -t "Add up to <number> rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Add up to <number> rank <rank> or higher <card>"
python3 add_csv_field.py -c SPELL -t "Add up to <number> rank <rank> or lower <card>"
python3 add_csv_field.py -c SPELL -t "Counter the effect of a rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy all rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy exactly <number> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy up to <number> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy exactly <number> rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy up to <number> rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Discard one rank <rank> <card> from your hand"
python3 add_csv_field.py -c SPELL -t "Discard this card to add one <card>"
python3 add_csv_field.py -c SPELL -t "Discard this card to add one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Discard this card to add one rank <rank> or higher <card>"
python3 add_csv_field.py -c SPELL -t "Discard this card to add one rank <rank> or lower <card>"
python3 add_csv_field.py -c SPELL -t "Draw <number> card"
python3 add_csv_field.py -c SPELL -t "Lose <number> point"
python3 add_csv_field.py -c SPELL -t "Return one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Reveal the top card of your deck and play one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Reveal the top <number> cards of your deck and play one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "This turn, all rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "This turn, increase the rank of one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "While this card is on the field, all rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Add <number> <card>"
python3 add_csv_field.py -c SPELL -t "Discard one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Return one <type> card"
python3 add_csv_field.py -c SPELL -t "Counter the effect of a <type> card"
python3 add_csv_field.py -c SPELL -t "Counter the effect of a rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy exactly <number> <type> card"
python3 add_csv_field.py -c SPELL -t "Destroy exactly <number> rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Destroy exactly <number> <card> controlled by each player"
python3 add_csv_field.py -c SPELL -t "Destroy up to <number> <type> card"
python3 add_csv_field.py -c SPELL -t "Destroy up to <number> rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Discard one <type> card from your hand"
python3 add_csv_field.py -c SPELL -t "Discard one rank <rank> <card> from your hand"
python3 add_csv_field.py -c SPELL -t "Discard one <type> card from your hand to play up to two"
python3 add_csv_field.py -c SPELL -t "Discard one rank <rank> <card> from your hand to play up to two"
python3 add_csv_field.py -c SPELL -t "Discard one <type> card to add one"
python3 add_csv_field.py -c SPELL -t "Discard one rank <rank> <card> to add one"
python3 add_csv_field.py -c SPELL -t "Discard one <type> card to counter"
python3 add_csv_field.py -c SPELL -t "Discard one rank <rank> <card> to counter"
python3 add_csv_field.py -c SPELL -t "Return one <type> card"
python3 add_csv_field.py -c SPELL -t "Return one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Reveal the top <number> card"
python3 add_csv_field.py -c SPELL -t "This turn, all <type> card"
python3 add_csv_field.py -c SPELL -t "This turn, all rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "This turn, change one <type>"
python3 add_csv_field.py -c SPELL -t "While this card is on the field, all <type>"
python3 add_csv_field.py -c SPELL -t "While this card is on the field, all rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "You can play one extra <type>"
python3 add_csv_field.py -c SPELL -t "You can play one extra rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Your opponent cannot play <type>"
python3 add_csv_field.py -c SPELL -t "Take one of your other <card>(s) on the field and move it under this card"
python3 add_csv_field.py -c SPELL -t "Play one <card> under this one"
python3 add_csv_field.py -c SPELL -t "Swap one <typeslevels> card you control with one <typeslevels> card from your <pile>"
python3 add_csv_field.py -c SPELL -t "Return up to <number> <typeslevels> card(s) from your discard pile to your hand"
python3 add_csv_field.py -c SPELL -t "Both players gain <number> point(s) for each <type> card they control"
python3 add_csv_field.py -c SPELL -t "Whenever a <typeslevels> card is discarded"
python3 add_csv_field.py -c SPELL -t "Until your next turn, all <type> card"
python3 add_csv_field.py -c SPELL -t "Swap the attack and defense of one <type> card"
python3 add_csv_field.py -c SPELL -t "Swap the attack and defense of one rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "Force your opponent to discard <number> card"
python3 add_csv_field.py -c SPELL -t "Place one <type> card from your <pile> under"
python3 add_csv_field.py -c SPELL -t "Place one rank <rank> <card> from your <pile> under"
python3 add_csv_field.py -c SPELL -t "Skip your next turn to destroy all <type>"
python3 add_csv_field.py -c SPELL -t "Skip your next turn to destroy all rank <rank> <card>"
python3 add_csv_field.py -c SPELL -t "For the next <number> turns, <type> cards"
python3 add_csv_field.py -c SPELL -t "Activate the effect of a card under this card"
python3 add_csv_field.py -c SPELL -t "Activate the effect of a card under another card"

# Handle some exact matches (used for one off effects)
python3 add_csv_field.py -c SPELL -e "While this card is on the field, attack and defense changes are inverted."


####################################################
# Add some level specific specifiers for spell cards.
####################################################

# Exceptions to the below loop(s).
python3 add_csv_field.py -c LEVEL_1 -m SPELL -t "Destroy one <type> card on the field"
python3 add_csv_field.py -c LEVEL_1 -m SPELL -t "Add one <type> card from your <pile> to your hand"
python3 add_csv_field.py -c LEVEL_1 -m SPELL -t "Destroy one <type> card on the field"
python3 add_csv_field.py -c LEVEL_1 -m SPELL -t "Add one <type> card from your <pile> to your hand"
python3 add_csv_field.py -c LEVEL_1 -m SPELL -t "Destroy one"

# Spell effects that are the same for each level
for level in LEVEL_{1..3}; do
    python3 add_csv_field.py -c "$level" -m SPELL -t "Your opponent cannot play <types> cards next turn"
    python3 add_csv_field.py -c "$level" -m SPELL -t "This turn, change one <type> card to any other type"
    python3 add_csv_field.py -c "$level" -m SPELL -t "This turn, all <type> cards gain <atkdef>"
    python3 add_csv_field.py -c "$level" -m SPELL -t "Discard one <type> card to counter the effect of a <type> card"
    python3 add_csv_field.py -c "$level" -m SPELL -t "Discard one <type> card to add one <type> card from your <pile> to your hand"
    python3 add_csv_field.py -c "$level" -m SPELL -t "Discard one <type> card from your hand to play one <type> card from your <pile>"
    python3 add_csv_field.py -c "$level" -m SPELL -t "Counter the effect of a <type> card"
done

# Some various <number> effect combinations for spells.
NUMS=(zero one two three four) # Array for number words
for l in "LEVEL_1 1 2" "LEVEL_2 2 3" "LEVEL_3 3 4"; do
    read level min max <<< "$l"
    for ((m=min; m<=max; m++)); do
        python3 add_csv_field.py -c "$level" -m SPELL -t "Reveal the top ${NUMS[m]} card$( ((m>1)) && echo "s") of your deck and play one <type> card from among them"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") on the field"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy exactly ${NUMS[m]} <card>$( ((m>1)) && echo "s") controlled by each player"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy exactly ${NUMS[m]} <type> card$( ((m>1)) && echo "s") on the field"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Both players mill ${NUMS[m]} card$( ((m>1)) && echo "s") from their deck"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Both players lose ${NUMS[m]} point"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Both players discard ${NUMS[m]} card"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Add up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") from your <pile> to your hand"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") on the field"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Both players discard ${NUMS[m]} card"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Reveal the top ${NUMS[m]} card$( ((m>1)) && echo "s") of your deck and play one <type> card from among them"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Add up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") from your <pile> to your hand"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Lose ${NUMS[m]} point"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Gain ${NUMS[m]} point"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Draw ${NUMS[m]} card"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy up to ${NUMS[m]}"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy exactly ${NUMS[m]}"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Add ${NUMS[m]} rank <rank> <type>"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Add ${NUMS[m]} rank <rank> <card>"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Gain ${NUMS[m]} point"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Your opponent loses ${NUMS[m]} point"
    done
done



# Add some unit specific effects.
python3 add_csv_field.py -c UNIT -t "You can send up to <number> card"
python3 add_csv_field.py -c UNIT -t "Send up to <number> card"
python3 add_csv_field.py -c UNIT -t "When this card is sent to the discard pile"
python3 add_csv_field.py -c UNIT -t "Destroy this card to"
python3 add_csv_field.py -c UNIT -t "Lose <number> point"
python3 add_csv_field.py -c UNIT -t "You can play one extra rank <rank> <card>"
python3 add_csv_field.py -c UNIT -t "Return one <subtype> card"
python3 add_csv_field.py -c UNIT -t "Discard this card to add one <subtype>"
python3 add_csv_field.py -c UNIT -t "Discard this card to add one rank <rank> <subtype>"
python3 add_csv_field.py -c UNIT -t "Discard this card to add one rank <rank> or higher <subtype>"
python3 add_csv_field.py -c UNIT -t "Discard this card to add one rank <rank> or lower <subtype>"
python3 add_csv_field.py -c UNIT -t "Take one of your other <card>(s) on the field and move it under this card."
python3 add_csv_field.py -c UNIT -t "Play one <card> under this one."
python3 add_csv_field.py -c UNIT -t "Both players gain <number> point(s) for each <subtype> card they control"
python3 add_csv_field.py -c UNIT -t "Whenever a <subtype> card is discarded"
python3 add_csv_field.py -c UNIT -t "Until your next turn, all <subtype> card"
python3 add_csv_field.py -c UNIT -t "Swap the attack and defense of one <subtype> card"
python3 add_csv_field.py -c UNIT -t "Place one <subtype> card from your <pile> under"
python3 add_csv_field.py -c UNIT -t "Skip your next turn to destroy all <subtype>"
python3 add_csv_field.py -c UNIT -t "For the next <number> turns, <subtype> cards"
python3 add_csv_field.py -c UNIT -t "for each card under this one"

# Handle some exact matches (used for one off effects)
python3 add_csv_field.py -c UNIT -e "While this card is on the field, attack and defense changes are inverted."
python3 add_csv_field.py -c UNIT -e "Activate the effect of a card under this one."
python3 add_csv_field.py -c UNIT -e "Activate the effect of a card under another card."

# Some various <rank> effect combinations for spells.
for l in "LEVEL_1 1 2" "LEVEL_2 2 4" "LEVEL_3 4 5"; do
    read level min max <<< "$l"
    for ((r=min; r<=max; r++)); do
        python3 add_csv_field.py -c "$level" -m SPELL -t "card to add one rank $r"
        python3 add_csv_field.py -c "$level" -m SPELL -t "card from your hand to play up to two rank $r"
        python3 add_csv_field.py -c "$level" -m SPELL -t "card from your hand to play one rank $r"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Destroy all rank $r <card>"
        python3 add_csv_field.py -c "$level" -m SPELL -t "Counter the effect of a rank $r <card>"
    done
done


####################################################
# Add some level specific specifiers for unit cards.
####################################################

# Exceptions to the below loop(s).
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t "You can send one card under this card to the discard pile"
python3 add_csv_field.py -c LEVEL_2 -m UNIT -t "You can send one card under this card to the discard pile"
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t "Send one card from under another card to the discard pile"
python3 add_csv_field.py -c LEVEL_2 -m UNIT -t "Send one card from under another card to the discard pile"
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t "Lose one point to destroy one <subtype> card on the field"
python3 add_csv_field.py -c LEVEL_2 -m UNIT -t "Lose one point to destroy one <subtype> card on the field"
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t "Destroy this card to destroy one <subtype> card on the field"
python3 add_csv_field.py -c LEVEL_2 -m UNIT -t "Destroy this card to destroy one <subtype> card on the field"
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t "Add one rank <rank> <subtype>"
python3 add_csv_field.py -c LEVEL_2 -m UNIT -t "Add one rank <rank> <subtype>"
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t "Add one <subtype>"
python3 add_csv_field.py -c LEVEL_2 -m UNIT -t "Add one <subtype>"

# Unit effects that are the same for each level
for level in LEVEL_{1..5}; do
    python3 add_csv_field.py -c "$level" -m UNIT -t "Activate the effect of a card under this card"
    python3 add_csv_field.py -c "$level" -m UNIT -t "Activate the effect of a card under another card"
    python3 add_csv_field.py -c "$level" -m UNIT -t "for each card under this one"
    python3 add_csv_field.py -c "$level" -m UNIT -t "Place one <subtype> card from your <pile> under"
    python3 add_csv_field.py -c "$level" -m UNIT -t "Whenever a <subtype> card is discarded"
    python3 add_csv_field.py -c "$level" -m UNIT -t "Skip your next turn to destroy all <subtype>"
    python3 add_csv_field.py -c "$level" -m UNIT -t "Swap the attack and defense of one <subtype> card"
    python3 add_csv_field.py -c "$level" -m UNIT -t "Until your next turn, all <subtype> card"
done

# Some various <number> effect combinations for units.
NUMS=(zero one two three four five) # Array for number words
for l in "LEVEL_1 1 2" "LEVEL_2 1 3" "LEVEL_3 2 4" "LEVEL_4 3 5" "LEVEL_5 4 5"; do
    read level min max <<< "$l"
    for ((m=min; m<=max; m++)); do
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to mill ${NUMS[m]} card$( ((m>1)) && echo "s") from your deck"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to draw ${NUMS[m]} card"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to draw ${NUMS[m]} card"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to add one rank ${m} <subtype> card from your <pile> to your hand"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to draw ${NUMS[m]} card"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Send up to ${NUMS[m]} card$( ((m>1)) && echo "s") from under another card to the discard pile"
        python3 add_csv_field.py -c "$level" -m UNIT -t "You can send up to ${NUMS[m]} card$( ((m>1)) && echo "s") under this card to the discard pile"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to destroy one rank ${m} <subtype> card on the field"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Lose ${NUMS[m]} point to play one rank ${m} <subtype> card from your hand"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to gain ${NUMS[m]} point"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to shuffle one rank ${m} <subtype> card from your discard pile into your deck"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to return one rank ${m} <subtype> card from your <pile> to your hand"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to counter the effect of a rank ${m} <subtype> card"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to destroy up to ${NUMS[m]} <subtype> cards on the field"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to add one rank ${m} <subtype> card from your <pile> to your hand"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to play one rank ${m} <subtype> card from your hand"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Destroy this card to destroy up to ${NUMS[m]} <subtype> card$( ((m>1)) && echo "s") on the field"
        python3 add_csv_field.py -c "$level" -m UNIT -t "card to add one rank ${m}"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Add up to ${NUMS[m]} rank <rank> <subtype>"
        python3 add_csv_field.py -c "$level" -m UNIT -t "Add up to ${NUMS[m]} <subtype>"
        python3 add_csv_field.py -c "$level" -m UNIT -t "For the next ${NUMS[m]} turns, <subtype> cards"
    done
done