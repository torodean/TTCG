# Effect Style Text README

## Overview
This folder contains text files that define patterns used to identify effect styles for cards. These files are read by the `deduce_effect_style_from_effect_text` function in the `ttcg_tools.py` script to match card effect text against specific phrases, determining the appropriate style (e.g., "continuous," "equip," "overload"). Each file corresponds to a style from `VALID_OVERLAY_STYLES` (from `ttcg_constants.py` and lists one or more unique text patterns.

## Purpose
This folder exists to:
- Centralize editable effect style patterns for the TTCG project.
- Enable case-insensitive matching of effect text against predefined phrases.
- Allow easy addition or modification of styles without altering core code.

The patterns here drive the logic for assigning styles to card effects, influencing gameplay mechanics, visuals, or deck-building rules.

## Structure
- **Files**: One `.txt` file per style in `VALID_OVERLAY_STYLES`, named `<style>.txt` (e.g., `continuous.txt`, `equip.txt`).
- **Contents**: Each file contains one pattern per line, representing a phrase or condition unique to that style.

## How It Works
The `deduce_effect_style_from_effect_text` function:
1. Reads each `<style>.txt` file in this folder.
2. Checks the input `effect_text` against patterns using `text_in_placeholder_string`.
3. Returns the matching style (or the first match if multiple apply, logging an error via `output_text`).
4. Returns `None` if no patterns match.

### Example
For a card with effect text "Discard one fire card":
- The script checks `overload.txt`, finds a match with "discard one <typeslevels> card", and assigns the "overload" style.

## Valid Styles
Styles are defined in `ttcg_constants.VALID_OVERLAY_STYLES`:
- `None`
- `continuous`
- `counter`
- `dormant`
- `latent`
- `passive`
- `equip`
- `overload`
- `echo`
- `pulse`

Each style (except `None`) should have a `.txt` file here.

## Adding or Modifying Styles
1. **New Style**: Create a new `<style>.txt` file with unique patterns and update `VALID_OVERLAY_STYLES` in `ttcg_constants.py`.
2. **Edit Patterns**: Modify the relevant `.txt` file by adding, removing, or changing lines. Keep patterns specific to avoid overlap.
3. **Testing**: Test with sample effect texts to ensure correct matching. Watch for multiple matches, which trigger an error.

### Guidelines
- Use lowercase text in patterns (matching is case-insensitive).
- Make patterns specific to avoid unintended matches (e.g., "counter" alone might catch unrelated text).
- Avoid blank lines or trailing whitespace—they’re stripped during processing.

## Requirements
- Python 3.x (for script compatibility).
- Files must be readable (ensure proper permissions).
- The folder path must match `EFFECT_STYLE_TEXT_FOLDER` in the codebase.

## Limitations
- Missing `.txt` files are silently skipped (no error raised).
- Overlapping patterns may cause multiple matches, logged as errors but returning the first match.
- Pattern syntax relies on `text_in_placeholder_string`—no additional validation here.
