#!/bin/python3

# A file for testing new features and methods.

from ttcg_tools import get_sequence_combinations
from ttcg_tools import get_combination_id

TYPE_LIST = ["Spell", "Earth", "Fire", "Water", "Air", "Light", "Dark", "Electric", "Nature"]
SUBTYPES_LIST = ["Avian", "Dragon", "Beast", "Elemental", "Aquatic", "Warrior", "Spellcaster", "Machine", "Ghost", "Insect", "Reptile", "Fairy", "Undead", "Botanic"]

LIST = TYPE_LIST + SUBTYPES_LIST + [""]
LIST_LOWER = [l.lower() for l in LIST]

all_combinations = get_sequence_combinations(LIST_LOWER)
print(len(all_combinations))


val = get_combination_id("air, Reptile, Elemental", LIST_LOWER)
print(val)
val = get_combination_id("earth, Spellcaster, fairy", LIST_LOWER)
print(val)
val = get_combination_id("water, warrior, fairy", LIST_LOWER)
print(val)
val = get_combination_id("light, Reptile, fairy", LIST_LOWER)
print(val)
val = get_combination_id("nature, Aquatic, Fairy", LIST_LOWER)
print(val)
