
# List of all valid card types and subtypes.
TYPE_LIST = ["Spell", "Earth", "Fire", "Water", "Air", "Light", "Dark", "Electric", "Nature"]
SUBTYPES_LIST = ["Avian", "Dragon", "Beast", "Elemental", "Aquatic", "Warrior", "Spellcaster", "Machine", "Ghost", "Insect", "Reptile", "Fairy", "Undead", "Botanic"]

# Valid options for effect overlay's (the positions are top and bottom representing effects 1 and 2 respectively).
VALID_OVERLAY_POSITIONS = ["top", "bottom"]
VALID_OVERLAY_STYLES = [None, "continuous", "counter", "dormant", "latent", "passive", "equip", "overload", "echo", "pulse"]

# Valid translucent values for card art.
VALID_TRANSLUCENT_VALUES = [50, 60, 75, 100]

# Base card values
DEFAULT_CARD_WIDTH = 750
DEFAULT_CARD_HEIGHT = 1050

# Card List values.
CARD_LIST_HEADER = ["NAME", "TYPE", "SUBTYPES", "LEVEL", "IMAGE", "ATTACK", "DEFENSE", "EFFECT1", "EFFECT2", "SERIAL", "RARITY", "TRANSPARENCY", "EFFECT1_STYLE", "EFFECT2_STYLE"]

# Used for image processing. We only really use the uncommented ones.
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png'] #, '.gif', '.bmp', '.tiff', '.webp']
