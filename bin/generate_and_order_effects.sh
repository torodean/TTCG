#!/bin/bash

# Cleanup old files
rm -rf effects/all_effects.txt
rm -rf effects/effects_with_placeholders.csv

# Create the base list of all effects.
python3 create_effect_combinations.py -f
sleep 1

#alphabetize the effects generated.
python3 alphabetize_file.py -i effects/all_effect_templates.txt -o effects/all_effect_templates.txt
sleep 1

# Generate csv, and add UNIT to csv.
python3 add_csv_field.py -c UNIT -t "<subtype> " -i "effects/all_effects.txt"
sleep 1 # Give the file time to generate.
python3 add_csv_field.py -c SPELL -t "<type> "


# Add some spell specific effects.
python3 add_csv_field.py -c SPELL -t \
    "Your opponent loses <number> point" \
    "Gain <number> point" \
    "Both players" \
	"Add up to <number> rank <rank> <card>" \
	"Add up to <number> rank <rank> or higher <card>" \
	"Add up to <number> rank <rank> or lower <card>" \
	"Counter the effect of a rank <rank> <card>" \
	"Destroy all rank <rank> <card>" \
	"Destroy exactly <number> <card>" \
	"Destroy up to <number> <card>" \
	"Destroy exactly <number> rank <rank> <card>" \
	"Destroy up to <number> rank <rank> <card>" \
	"Discard one rank <rank> <card>" \
	"Discard this card to add one <card>" \
	"Discard this card to add one rank <rank> <card>" \
	"Discard this card to add one rank <rank> or higher <card>" \
	"Discard this card to add one rank <rank> or lower <card>" \
	"Draw <number> card" \
	"Lose <number> point" \
	"Return one rank <rank> <card>" \
	"Reveal the top card of your deck and play one rank <rank> <card>" \
	"Reveal the top <number> cards of your deck and play one rank <rank> <card>" \
	"This turn, all rank <rank> <card>" \
	"This turn, increase the rank of one rank <rank> <card>" \
	"While this card is on the field, all rank <rank> <card>" \
	"Add <number> <card>" \
	"Discard one rank <rank> <card>" \
	"Return one <type> card" \
	"Counter the effect of a <type> card" \
	"Counter the effect of a rank <rank> <card>" \
	"Destroy exactly <number> <type> card" \
	"Destroy exactly <number> rank <rank> <card>" \
	"Destroy exactly <number> <card> controlled by each player" \
	"Destroy up to <number> <type> card" \
	"Destroy up to <number> rank <rank> <card>" \
	"Discard one <type> card" \
	"Discard one rank <rank> <card>" \
	"Discard one <type> card to play up to two" \
	"Discard one rank <rank> <card> to play up to two" \
	"Discard one <type> card to add one" \
	"Discard one rank <rank> <card> to add one" \
	"Discard one <type> card to counter" \
	"Discard one rank <rank> <card> to counter" \
	"Return one <type> card" \
	"Return one rank <rank> <card>" \
	"Reveal the top <number> card" \
	"This turn, all <type> card" \
	"This turn, all rank <rank> <card>" \
	"This turn, change one <type>" \
	"While this card is on the field, all <type>" \
	"While this card is on the field, all rank <rank> <card>" \
	"You can play one extra <type>" \
	"You can play one extra rank <rank> <card>" \
	"Your opponent cannot play <type>" \
	"Take one of your other <card>s on the field" \
	"Play one <card> under this one" \
	"Swap one <typeslevels> card you control with one <typeslevels> card from your <pile>" \
	"Return up to <number> <typeslevels> cards from your discard pile to your hand" \
	"Return one <typeslevels> card from your discard pile to your hand" \
	"Both players <gainlose> <number> points for each <type> card they control" \
	"Both players <gainlose> one point for each <type> card they control" \
	"Whenever a <typeslevels> card is discarded" \
	"Until your next turn, all <type> card" \
	"Swap the attack and defense of one <type> card" \
	"Swap the attack and defense of one rank <rank> <card>" \
	"Force your opponent to discard <number> card" \
	"Place one <type> card from your <pile> under" \
	"Place one rank <rank> <card> from your <pile> under" \
	"Skip your next turn to destroy all <type>" \
	"Skip your next turn to destroy all rank <rank> <card>" \
	"For the next <number> turns, <type> cards" \
	"Activate the effect of a card under this card" \
	"Activate the effect of a card under another card" \
	"Activate the effect of another card" \
	"Add one rank <rank> <card>" \
	"Add one rank <rank> or higher <card>" \
	"Add one rank <rank> or lower <card>" \
	"Add up to <number> <card>" \
	"Destroy one rank <rank> <card>" \
	"Destroy two rank <rank> <card>" \
	"Return up to <number> rank <rank> <card>" \
	"Swap one rank <rank> card you control" \
	"Whenever a rank <rank> card is discarded" \
	"While this card is tapped" \
	"Tap up to <number> <card>" \
	"Untap exactly <number> <card>" \
	"Untap up to <number> <card>" \
	"Tap exactly <number> <card>" \
	"The equip card cannot" \
	"The equip card gains" \
	"The equip card can be" \
	"For each <card> under this one" \
	"When a <card> is sent from the <pile>" \
	"Move up to <number> cards to any other column." \
	"Move one card to any other column." \
	"Whenever your opponent plays a <types> card, they lose one point and you gain one point." \
	"While this card is on the field, reduce the attack of all <type> card." \
	"Copy the effect of one spell card in your discard pile." \
	"Copy the effect of one rank <rank> spell card in your discard pile." \
	"Once per turn, while this card is untapped, you can destroy one card under it to gain one point." \
	"Destroy one <card> you control to gain points" \
	"This turn, <typeslevels> cards you control can be untapped once by paying one point" \
	"While this card is under another, all <type> cards you control gain <atkdef>." \
	"When a <type> card is placed under this one, destroy" \
	"When this card is destroyed, place up to <number> <typeslevels> card" \
	"While this card is on the field, <type> cards you control" \
	"For each <card> tapped this turn, draw <number-1> card" \
	"Whenever a <typeslevels> card is played, shuffle <number> card" \
	"For each <type> card destroyed this turn, add one" \
	"While this card is on the field, <type> cards can rank up using <type>"

# Handle some exact matches (used for one off effects)
python3 add_csv_field.py -c SPELL -e \
    "While this card is on the field, attack and defense changes are inverted." \
    "Send one card from under another card to the discard pile." \
    "You can send one card under this card to the discard pile."


####################################################
# Add some level specific specifiers for spell cards.
####################################################

# Exceptions to the below loop(s).
python3 add_csv_field.py -c LEVEL_1 -m SPELL -t \
    "Destroy one <type> card on the field"\
    "Add one <type> card from your <pile> to your hand" \
    "Destroy one <type> card on the field" \
    "Add one <type> card from your <pile> to your hand" \
    "Destroy one" \
    "Return one"
python3 add_csv_field.py -c LEVEL_2 -m SPELL -t \
    "Return one" \
    "Add one rank <rank>"
python3 add_csv_field.py -c LEVEL_3 -m SPELL -t \
    "Add one rank <rank>" \
    "Add one <card> from your <pile> to your hand"

# Spell effects that are the same for each level
for level in LEVEL_{1..3}; do
    python3 add_csv_field.py -c "$level" -m SPELL -t \
        "Your opponent cannot play <types> cards next turn" \
        "This turn, change one <type> card to any other type" \
        "This turn, all <type> cards <gainlose> <atkdef>" \
        "Discard one <type> card to counter the effect of a <type> card" \
        "Discard one <type> card to add one <type> card from your <pile> to your hand" \
        "Discard one <type> card to play one <type> card from your <pile>" \
        "Counter the effect of a <type> card" \
        "While this card is on the field, all <type> card" \
        "Both players discard their hand" \
        "Destroy this card to destroy one <type>" \
        "Destroy this card to destroy up to <number> <type>" \
        "Discard one <type> card" \
        "Discard this card to add one <type>" \
        "Play one <card> under" \
        "Activate the effect of another" \
        "When a <type> card is destroyed" \
        "While this card is on the field, all <type>" \
        "You can rank up one of your <type>" \
        "While this card is on the field, <types>" \
        "Whenever a <type> card is discarded" \
        "This turn, increase the rank of one <type>" \
        "This turn, double the attack of one <type>" \
        "Swap the attack and defense of one <type>" \
        "Swap one <types> card you control" \
        "Skip your next turn to destroy all <type>" \
        "Place one <type>" \
        "While this card is on the field, attack and defense changes" \
        "Discard this card to add one <card>" \
        "Destroy this card to shuffle your discard pile" \
        "Take one of your other <card>s on the field" \
        "The equip card cannot" \
        "The equip card gains" \
        "While this card is tapped, gain one point" \
        "The equip card can be" \
        "For each <card> under this one" \
        "When a <card> is sent from the <pile>" \
        "Whenever your opponent plays a <types> card, they lose one point and you gain one point." \
        "Copy the effect of one spell card in your discard pile." \
        "Once per turn, while this card is untapped, you can destroy one card" \
        "Destroy one <card> you control to gain points" \
        "This turn, <type> cards you control can be untapped once by paying one point" \
        "While this card is under another, all <type> card" \
        "When a <type> card is placed under this one, destroy" \
        "While this card is on the field, <type> cards you control" \
        "For each <type> card destroyed this turn, add one" \
        "Swap this cards rank with another card" \
	    "While this card is on the field, <type> cards can rank up using <type>"
done

# Some various <number> effect combinations for spells.
NUMS=(zero one two three four) # Array for number words
for l in "LEVEL_1 1 2" "LEVEL_2 2 3" "LEVEL_3 3 4"; do
    read level min max <<< "$l"
    for ((m=min; m<=max; m++)); do
        python3 add_csv_field.py -c "$level" -m SPELL -t \
            "Add up to ${NUMS[m]}" \
            "Reveal the top ${NUMS[m]} card$( ((m>1)) && echo "s") of your deck and play one <type> card" \
            "Destroy up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") on the field" \
            "Destroy exactly ${NUMS[m]} <card>$( ((m>1)) && echo "s") controlled by each player" \
            "Destroy exactly ${NUMS[m]} <type> card$( ((m>1)) && echo "s") on the field" \
            "Both players mill ${NUMS[m]} card$( ((m>1)) && echo "s") from their deck" \
            "Both players lose ${NUMS[m]} point" \
            "Both players discard ${NUMS[m]} card" \
            "Add up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") from your <pile> to your hand" \
            "Destroy up to ${NUMS[m]} <type> card$( ((m>1)) && echo "s") on the field" \
            "Both players discard ${NUMS[m]} card" \
            "Lose ${NUMS[m]} point" \
            "Gain ${NUMS[m]} point" \
            "Draw ${NUMS[m]} card" \
            "Destroy up to ${NUMS[m]}" \
            "Destroy exactly ${NUMS[m]}" \
            "Add ${NUMS[m]} rank <rank> <type>" \
            "Add ${NUMS[m]} rank <rank> <card>" \
            "Gain ${NUMS[m]} point" \
            "Your opponent loses ${NUMS[m]} point" \
            "You can play ${NUMS[m]} extra rank <rank>" \
            "Both players <gainlose> ${NUMS[m]} point" \
            "This turn, all rank ${m}" \
            "Destroy two <type> cards you own to play" \
            "For the next ${NUMS[m]} turn" \
            "your opponent takes ${NUMS[m]} points of damage" \
            "Reveal the top ${NUMS[m]} cards of your deck and play one" \
            "Return up to ${NUMS[m]}" \
            "Force your opponent to discard ${NUMS[m]}" \
            "Tap up to ${NUMS[m]} <card>" \
            "Untap exactly ${NUMS[m]} <card>" \
            "Untap up to ${NUMS[m]} <card>" \
            "Tap exactly ${NUMS[m]} <card>" \
            "Move up to ${NUMS[m]} cards to any other column." \
            "Move ${NUMS[m]} card to any other column." \
            "When this card is destroyed, place up to ${NUMS[m]} <typeslevels> card" \
            "For each <card> tapped this turn, draw ${NUMS[m-1]} card" \
            "Whenever a <typeslevels> card is played, shuffle ${NUMS[m]} card" \
            "Swap this cards rank with another card"
    done
done


# Some various <rank> effect combinations for spells.
for l in "LEVEL_1 1 2" "LEVEL_2 2 4" "LEVEL_3 4 5"; do
    read level min max <<< "$l"
    for ((m=min; m<=max; m++)); do
        python3 add_csv_field.py -c "$level" -m SPELL -t \
            "Add up to <number> rank ${m} light cards from your deck to your hand." \
            "Destroy this card to destroy one rank ${m}" \
            "Destroy this card to destroy up to <number> rank ${m}" \
            "Destroy two rank ${m}" \
            "Discard one rank ${m}" \
            "card to add one rank ${m}" \
            "card to play up to two rank ${m}" \
            "card to play one rank ${m}" \
            "Destroy all rank ${m} <card>" \
            "Counter the effect of a rank ${m} <card>" \
            "Discard this card to add one rank ${m}" \
            "Return one rank ${m}" \
            "Whenever a rank ${m}" \
            "While this card is on the field, all rank ${m}" \
            "Until your next turn, all <type> cards you control become rank ${m}" \
            "Swap the attack and defense of one rank ${m}" \
            "Swap one rank ${m}" \
            "Place one rank ${m}" \
            "This turn, increase the rank of one rank ${m}" \
            "Skip your next turn to destroy all rank ${m}" \
            "While this card is tapped, only cards <abovebelow> rank ${m}" \
            "Copy the effect of one rank ${m} spell card in your discard pile" \
            "This turn, rank ${m} <card>s you control can be untapped once by paying one point"
    done
done


# Add some unit specific effects.
python3 add_csv_field.py -c UNIT -t \
    "You can send up to <number> card" \
    "Send up to <number> card" \
    "When this card is sent to the discard pile" \
    "Destroy this card to" \
    "Lose <number> point" \
    "You can play one extra rank <rank> <subtype>" \
    "You can play one extra <subtype>" \
    "Return one <subtype> card" \
    "Discard this card to add one <subtype>" \
    "Discard this card to add one rank <rank> <subtype>" \
    "Discard this card to add one rank <rank> or higher <subtype>" \
    "Discard this card to add one rank <rank> or lower <subtype>" \
    "Take one of your other <card>s on the field" \
    "Play one <card> under this one." \
    "Both players <gainlose> <number> points for each <subtype> card they control" \
    "Both players <gainlose> one point for each <subtype> card they control" \
    "Whenever a <subtype> card is discarded" \
    "Until your next turn, all <subtype> card" \
    "Swap the attack and defense of one <subtype> card" \
    "Place one <subtype> card from your <pile> under" \
    "Skip your next turn to destroy all <subtype>" \
    "For the next <number> turns, <subtype> cards" \
    "for each card under this one" \
    "Activate the effect of another unit" \
    "Place one rank <rank> unit card from your" \
    "This card gains <atkdef> for each card" \
    "While this card is tapped" \
    "For each <card> under this one" \
    "Once per turn, while this card is under another" \
    "While this card is under another" \
    "You can rank up this card using a <types> card" \
    "While this card is on the field, reduce the attack of all <subtype> cards" \
    "Copy the effect of one <typeslevels> card in your discard pile." \
    "Once per turn, while this card is untapped, you can destroy one card under it to gain one point." \
    "This turn, <subtype> cards you control can be untapped once by paying one point" \
    "Whenever a <typeslevels> card you control is attacked" \
    "Whenever a <typeslevels> card you control is targeted" \
    "While this card is under another, all <subtype> cards you control gain <atkdef>." \
    "When a <subtype> card is placed under this one, destroy one card" \
    "When this card is destroyed, place up to <number> <subtype> card" \
    "While this card is on the field, <subtype> cards you control" \
    "For each <subtype> card destroyed this turn, add one" \
    "Whenever a card is moved from under this card, both players mill <number> card" \
    "Swap this cards rank with another card"



# Handle some exact matches (used for one off effects)
python3 add_csv_field.py -c UNIT -e \
    "While this card is on the field, attack and defense changes are inverted." \
    "Activate the effect of a card under this one." \
    "Activate the effect of a card under another card." \
    "Take one of your other units on the field and move it under this card." \
    "You can send one card under this card to the discard pile."




####################################################
# Add some level specific specifiers for unit cards.
####################################################

# Exceptions to the below loop(s).
python3 add_csv_field.py -c LEVEL_1 -m UNIT -t \
"You can send one card under this card to the discard pile" \
    "Send one card from under another card to the discard pile" \
    "Lose one point to destroy one <subtype> card on the field" \
    "Destroy this card to destroy one <subtype> card on the field" \
    "Add one rank <rank> <subtype>" \
    "Add one <subtype>" \
    "Return one"

python3 add_csv_field.py -c LEVEL_2 -m UNIT -t \
    "You can send one card under this card to the discard pile" \
    "Send one card from under another card to the discard pile" \
    "Lose one point to destroy one <subtype> card on the field" \
    "Destroy this card to destroy one <subtype> card on the field" \
    "Add one rank <rank> <subtype>" \
    "Add one <subtype>" \
    "Return one"

python3 add_csv_field.py -c LEVEL_4 -m UNIT -t "Destroy this card to destroy all <subtype>"
python3 add_csv_field.py -c LEVEL_5 -m UNIT -t "Destroy this card to destroy all <subtype>"



# Unit effects that are the same for each level
for level in LEVEL_{1..5}; do
    python3 add_csv_field.py -c "$level" -m UNIT -t \
        "Activate the effect of a card under this card" \
        "Activate the effect of a card under another card" \
        "for each card under this one" \
        "Place one <subtype> card from your <pile> under" \
        "Whenever a <subtype> card is discarded" \
        "Skip your next turn to destroy all <subtype>" \
        "Swap the attack and defense of one <subtype> card" \
        "Until your next turn, all <subtype> card" \
        "While this card is on the field, all <subtype> card" \
        "Counter the effect of a <subtype> card" \
        "This turn, all <subtype> cards gain" \
        "Destroy this card to destroy one <subtype>" \
        "Destroy this card to destroy up to <number> <subtype>" \
        "Destroy two <subtype> cards you own to play" \
        "Discard one <subtype> card" \
        "Discard this card to add one <subtype>" \
        "Play one <card> under" \
        "Activate the effect of another" \
        "When a <subtype> card is destroyed" \
        "While this card is on the field, all <subtype>" \
        "You can rank up this unit" \
        "You can play one extra <types>" \
        "While this card is on the field, <subtype>" \
        "This turn, increase the rank of one <subtype>" \
        "This turn, change one <subtype>" \
        "Swap one <subtype> card you control" \
        "This card gains <atkdef> for each card" \
        "You can rank up one of your <subtype>" \
        "While this card is on the field, attack and defense changes" \
        "When this card is sent to the discard pile, your opponent" \
        "This turn, double the attack of one <subtype>" \
        "Destroy this card to shuffle your discard pile" \
        "Take one of your other <card>s on the field" \
        "For each <card> under this one" \
        "Once per turn, while this card is under another" \
        "While this card is under another" \
        "You can rank up this card using a <types> card" \
        "Copy the effect of one <typeslevels> card in your discard pile." \
        "Once per turn, while this card is untapped, you can destroy one card" \
        "Whenever a <typeslevels> card you control is attacked" \
        "Whenever a <typeslevels> card you control is targeted" \
        "While this card is under another, all <subtype> card" \
        "When a <subtype> card is placed under this one, destroy one card" \
        "While this card is on the field, <subtype> cards you control" \
        "For each <subtype> card destroyed this turn, add one" \
        "Swap this cards rank with another card"
done

# Some various <number> effect combinations for units.
NUMS=(zero one two three four five) # Array for number words
for l in "LEVEL_1 1 2" "LEVEL_2 1 3" "LEVEL_3 2 4" "LEVEL_4 3 5" "LEVEL_5 4 5"; do
    read level min max <<< "$l"
    for ((m=min; m<=max; m++)); do
        python3 add_csv_field.py -c "$level" -m UNIT -t \
            "Destroy this card to mill ${NUMS[m]} card$( ((m>1)) && echo "s") from your deck" \
            "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to draw ${NUMS[m]} card" \
            "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to draw ${NUMS[m]} card" \
            "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to add one rank ${m} <subtype> card" \
            "Destroy this card to draw ${NUMS[m]} card" \
            "Send up to ${NUMS[m]} card$( ((m>1)) && echo "s") from under another carde" \
            "You can send up to ${NUMS[m]} card$( ((m>1)) && echo "s") under this card" \
            "Destroy this card to destroy one rank ${m} <subtype> card on the field" \
            "Lose ${NUMS[m]} point to play one rank ${m} <subtype> card" \
            "Destroy this card to gain ${NUMS[m]} point" \
            "Destroy this card to shuffle one rank ${m} <subtype> card" \
            "Destroy this card to return one rank ${m} <subtype> card from your <pile> to your hand" \
            "Destroy this card to counter the effect of a rank ${m} <subtype> card" \
            "Lose ${NUMS[m]} point$( ((m>1)) && echo "s") to destroy up to ${NUMS[m]} <subtype> card" \
            "Destroy this card to add one rank ${m} <subtype> card from your <pile> to your hand" \
            "Destroy this card to play one rank ${m} <subtype> card" \
            "Destroy this card to destroy up to ${NUMS[m]} <subtype> card" \
            "card to add one rank ${m}" \
            "Add up to ${NUMS[m]}" \
            "For the next ${NUMS[m]} turns, <subtype> cards" \
            "Both players <gainlose> ${NUMS[m]} point" \
            "Destroy this card to destroy up to <number> rank ${m}" \
            "This turn, all <subtype> cards gain" \
            "This turn, all rank ${m}" \
            "Destroy this card to destroy one rank ${m}" \
            "Destroy this card to destroy up to <number> rank ${m}" \
            "Destroy two rank ${m}" \
            "Discard one rank ${m}" \
            "Discard this card to add one rank ${m}" \
            "For the next ${NUMS[m]} turn" \
            "Return one rank ${m}" \
            "Whenever a rank ${m}" \
            "While this card is on the field, all rank ${m}" \
            "your opponent takes ${NUMS[m]} points of damage" \
            "Swap one rank ${m}" \
            "Reveal the top ${NUMS[m]} cards of your deck and play one" \
            "Return up to ${NUMS[m]}" \
            "This turn, increase the rank of one rank ${m}" \
            "Skip your next turn to destroy all rank ${m}" \
            "While this card is tapped, only cards <abovebelow> rank ${m}" \
            "When this card is destroyed, place up to ${NUMS[m]} <subtype> card" \
            "Whenever a card is moved from under this card, both players mill ${NUMS[m]} card"
    done
done
