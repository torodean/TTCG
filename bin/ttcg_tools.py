import os
import re
import csv

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
