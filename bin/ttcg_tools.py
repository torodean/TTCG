import os
import re
import csv
import itertools

def load_placeholder_values(placeholder_dir, placeholder, visited=None):
    """
    Loads and resolves values for a placeholder from a text file, handling nested placeholders recursively.

    This function reads a file named `<placeholder>.txt` from the specified directory, processes its lines into a list of
    values, and recursively resolves any nested placeholders (e.g., `<other>` within a value). It prevents infinite
    recursion by tracking visited placeholders and returning the unresolved placeholder (e.g., `<placeholder>`) if a
    cycle is detected or if the file is missing/empty.

    Args:
        placeholder_dir (str): Directory path containing placeholder text files (e.g., 'placeholders/').
        placeholder (str): Name of the placeholder to load values for (e.g., 'number'), without angle brackets.
        visited (set, optional): Set of placeholders already processed in the recursion stack to detect cycles.
                                 Defaults to None, initializing an empty set if not provided.

    Returns:
        list: A list of resolved string values for the placeholder. If the file doesn’t exist, is empty, or a cycle is
              detected, returns a single-element list containing the unresolved placeholder (e.g., ['<placeholder>']).

    Examples:
        >>> load_placeholder_values('placeholders/', 'number')
        ['1', '2', '3']  # Assuming placeholders/number.txt contains "1\n2\n3"
        >>> load_placeholder_values('placeholders/', 'missing')
        ['<missing>']  # If placeholders/missing.txt doesn’t exist
    """
    if visited is None:
        visited = set()
    
    if placeholder in visited:
        return [f"<{placeholder}>"]
    
    visited.add(placeholder)
    
    file_path = os.path.join(placeholder_dir, f"{placeholder}.txt")
    if not os.path.exists(file_path):
        visited.remove(placeholder)
        return [f"<{placeholder}>"]
    
    raw_values = []
    with open(file_path, 'r') as f:
        raw_values = [line.strip().replace('_', '') for line in f if line.strip()]
    
    if not raw_values:
        visited.remove(placeholder)
        return [f"<{placeholder}>"]
    
    resolved_values = []
    for value in raw_values:
        if re.search(r"<[^>]+>", value):
            sub_combinations = generate_combinations(value, placeholder_dir, visited.copy())
            resolved_values.extend(sub_combinations)
        else:
            resolved_values.append(value)
    
    visited.remove(placeholder)
    return resolved_values


def generate_combinations(sentence, placeholder_dir, visited=None):
    """
    Generate all possible combinations by replacing placeholders in the sentence with their corresponding values,
    handling nested placeholders and offsets (e.g., <rank+1>, <rank-1>) recursively.

    Args:
        sentence (str): Sentence containing placeholders enclosed in <> (e.g., "<rank>", "<rank+1>", "<rank-1>").
        placeholder_dir (str): Directory containing placeholder text files.
        visited (set, optional): Set of placeholders already processed to prevent infinite recursion.

    Returns:
        list: List of all possible sentence combinations with no placeholders remaining.
    """
    if visited is None:
        visited = set()
    
    # Extract all placeholders, including those with offsets (e.g., "rank", "rank+1", "rank-1")
    placeholders = re.findall(r"<([^>]+)>", sentence)
    if not placeholders:  # Base case: no placeholders left
        return [sentence]
    
    # Split placeholders into base and offset parts
    placeholder_values = {}
    base_to_offsets = {}  # Track offsets for each base (e.g., "rank": ["+1", "-1"])
    
    for placeholder in placeholders:
        # Check for offset (e.g., "rank+1" or "rank-1")
        offset_match = re.match(r"(\w+)(?:([+-])(\d+))?", placeholder)
        if not offset_match:
            continue  # Skip malformed placeholders
        
        base, sign, offset = offset_match.groups()  # e.g., ("rank", "+", "1") or ("rank", None, None)
        if sign is None:  # No offset (plain "<rank>")
            offset_value = 0
        else:
            offset_value = int(offset) if sign == "+" else -int(offset)  # Positive or negative
        
        if base not in placeholder_values:
            # Load values for the base placeholder (e.g., "rank")
            placeholder_values[base] = load_placeholder_values(placeholder_dir, base, visited)
            base_to_offsets[base] = set()
        
        # Track this offset for the base
        base_to_offsets[base].add(offset_value)
    
    # Generate values for all placeholders, including offsets
    all_placeholder_values = {}
    for base, offsets in base_to_offsets.items():
        base_values = placeholder_values[base]
        for offset in offsets:
            # Create a new placeholder key like "rank+1" or "rank-1"
            if offset == 0:
                offset_key = base
            elif offset > 0:
                offset_key = f"{base}+{offset}"
            else:
                offset_key = f"{base}{offset}"  # e.g., "rank-1"
            # Compute offset values (assuming base values are numeric)
            all_placeholder_values[offset_key] = []
            for value in base_values:
                try:
                    num_value = int(value)  # Convert to int
                    all_placeholder_values[offset_key].append(str(num_value + offset))
                except ValueError:
                    # If not numeric, keep as-is
                    all_placeholder_values[offset_key].append(value)
    
    # Generate combinations
    combinations = []
    all_values = [all_placeholder_values[p] if p in all_placeholder_values else placeholder_values[p] 
                  for p in placeholders]
    for combo in itertools.product(*all_values):
        result = sentence
        for placeholder, value in zip(placeholders, combo):
            result = result.replace(f"<{placeholder}>", value)
        combinations.append(result)
    
    return combinations