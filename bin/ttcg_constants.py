
# List of all valid card types and subtypes.
TYPE_LIST = ["Spell", "Earth", "Fire", "Water", "Air", "Light", "Dark", "Electric", "Nature"]
TYPE_LIST_LOWER = [l.lower() for l in TYPE_LIST]
SUBTYPES_LIST = ["Avian", "Dragon", "Beast", "Elemental", "Aquatic", "Warrior", "Spellcaster", "Machine", "Ghost", "Insect", "Reptile", "Fairy", "Undead", "Botanic"]
SUBTYPES_LIST_LOWER = [l.lower() for l in SUBTYPES_LIST]
ALL_TYPES_LIST = TYPE_LIST + SUBTYPES_LIST
ALL_TYPES_LIST_LOWER = [l.lower() for l in ALL_TYPES_LIST]

# Valid options for effect overlay's (the positions are top and bottom representing effects 1 and 2 respectively).
VALID_OVERLAY_POSITIONS = ["top", "bottom"]
VALID_OVERLAY_STYLES = [None, "continuous", "counter", "dormant", "latent", "passive", "equip", "overload", "echo", "pulse"]

# Valid translucent values for card art.
VALID_TRANSLUCENT_VALUES = [30, 50, 60, 75, 100]

# Base card values
DEFAULT_CARD_WIDTH = 750
DEFAULT_CARD_HEIGHT = 1050

# Card List values.
CARD_LIST_HEADER = ["NAME", "TYPE", "SUBTYPES", "LEVEL", "IMAGE", "ATTACK", "DEFENSE", "EFFECT1", "EFFECT2", "SERIAL", "RARITY", "TRANSPARENCY", "EFFECT1_STYLE", "EFFECT2_STYLE"]

# Used for image processing. We only really use the uncommented ones.
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png'] #, '.gif', '.bmp', '.tiff', '.webp']

# File paths for the various files. This is relative to this directory.
DEFAULT_CARD_LIST_FILE = "card_list/card_list.csv"
DEFAULT_PLACEHOLDERS_FOLDER = "placeholders"
DEFAULT_ALL_EFFECTS_FILE = "effects/all_effects.txt"
DEFAULT_ALL_EFFECT_TEMPLATES_FILE = "effects/all_effect_templates.txt"
DEFAULT_COMBOS_TO_REMOVE_FILE = "placeholders/combinations_to_remove.txt"
DEFAULT_PHRASES_TO_REPLACE_FILE = "placeholders/phrase_replacements.txt"
EFFECT_STYLE_TEXT_FOLDER = "effect_style_text"

# Characters to be used in serial number generation. These are all values that show up nicely without 
# having to worry about what letters are what or the font effecting the serial number display size.
CHARACTERS = "0123456789AaBbCcDdEeFfGHhiKkLMmNnoPRrSsTtUuVvWwXxYZz"
