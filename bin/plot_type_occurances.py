#!/bin/python3

import csv
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import Counter

# Imports from ttcg_tools
from ttcg_tools import output_text

# Import needed constants from ttcg_constants
from ttcg_constants import TYPE_LIST
from ttcg_constants import SUBTYPES_LIST
from ttcg_constants import DEFAULT_CARD_LIST_FILE

def read_cards(file_path):
    """
    Read the CSV file into a list of dictionaries.
    """
    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        return list(reader)

def count_types(cards):
    """
    Count occurrences of each type from TYPE_LIST in the TYPE column.
    """
    type_counts = Counter(card['TYPE'] for card in cards if card['TYPE'] in TYPE_LIST)
    return {t: type_counts.get(t, 0) for t in TYPE_LIST}

def count_subtypes(cards):
    """
    Count occurrences of each subtype from SUBTYPES_LIST in the SUBTYPES column.
    Each subtype in a comma-separated list counts as 1.
    """
    subtype_counts = Counter()
    for card in cards:
        subtypes = [s.strip() for s in card['SUBTYPES'].split(',') if s.strip()]
        subtype_counts.update(subtypes)
    return {s: subtype_counts.get(s, 0) for s in SUBTYPES_LIST}

def count_effect_mentions(cards):
    """
    Count how many cards' effects mention each type and subtype.
    """
    effect_mentions = Counter()
    all_terms = TYPE_LIST + SUBTYPES_LIST
    
    for card in cards:
        effects = f"{card['EFFECT1']} {card['EFFECT2']}".lower()
        mentioned = set(term.lower() for term in all_terms if term.lower() in effects)
        effect_mentions.update(mentioned)
    
    return {term: effect_mentions.get(term.lower(), 0) for term in all_terms}

def count_type_effect_interactions(cards):
    """
    Count how many cards of each type mention each type or subtype in their effects.
    Returns a 2D dict: {card_type: {effect_term: count}}.
    """
    type_effect_counts = {t: Counter() for t in TYPE_LIST}
    all_terms = TYPE_LIST + SUBTYPES_LIST
    
    for card in cards:
        if card['TYPE'] not in TYPE_LIST:
            continue
        effects = f"{card['EFFECT1']} {card['EFFECT2']}".lower()
        mentioned_terms = set(t.lower() for t in all_terms if t.lower() in effects)
        type_effect_counts[card['TYPE']].update(mentioned_terms)
    
    return type_effect_counts

def count_subtype_mentions_per_type(cards):
    """
    Count how many times each subtype is mentioned in the effects of cards of each type.
    Returns a 2D dict: {card_type: {subtype: count}}.
    """
    subtype_mentions_per_type = {t: Counter() for t in TYPE_LIST}
    
    for card in cards:
        if card['TYPE'] not in TYPE_LIST:
            continue
        effects = f"{card['EFFECT1']} {card['EFFECT2']}".lower()
        mentioned_subtypes = set(s.lower() for s in SUBTYPES_LIST if s.lower() in effects)
        subtype_mentions_per_type[card['TYPE']].update(mentioned_subtypes)
    
    return subtype_mentions_per_type

def plot_data(type_counts, subtype_counts, effect_mentions, cards, plot_3d=False):
    """
    Generate bar plots for type counts, subtype counts, effect mentions, subtype mentions per type,
    and optionally a 3D plot.
    """
    # Plot 1: Type Counts
    plt.figure(figsize=(10, 5))
    plt.bar(type_counts.keys(), type_counts.values(), color='skyblue')
    plt.title('Number of Cards by Type')
    plt.xlabel('Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('card_list/type_counts.png')
    plt.close()

    # Plot 2: Subtype Counts
    plt.figure(figsize=(12, 6))
    plt.bar(subtype_counts.keys(), subtype_counts.values(), color='lavender')
    plt.title('Number of Cards by Subtype')
    plt.xlabel('Subtype')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('card_list/subtype_counts.png')
    plt.close()

    # Plot 3: Effect Mentions
    plt.figure(figsize=(12, 6))
    terms = list(effect_mentions.keys())
    counts = list(effect_mentions.values())
    colors = ['lightcoral' if term in TYPE_LIST else 'lightgreen' for term in terms]
    plt.bar(terms, counts, color=colors)
    plt.title('Number of Cards with Effects Mentioning Each Type/Subtype')
    plt.xlabel('Type/Subtype')
    plt.ylabel('Number of Cards')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('card_list/effect_mentions.png')
    plt.close()

    # Plot 4: Subtype Mentions per Type (one plot per type)
    subtype_mentions_per_type = count_subtype_mentions_per_type(cards)
    for card_type, subtype_mentions in subtype_mentions_per_type.items():
        plt.figure(figsize=(12, 6))
        subtypes = SUBTYPES_LIST
        counts = [subtype_mentions.get(s.lower(), 0) for s in subtypes]
        plt.bar(subtypes, counts, color='lightblue')
        plt.title(f'Subtype Mentions in Effects of {card_type} Cards')
        plt.xlabel('Subtype')
        plt.ylabel('Number of Mentions')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'card_list/{card_type.lower()}_subtype_mentions.png')
        plt.close()

    # Optional 3D Plot
    if plot_3d:
        type_effect_counts = count_type_effect_interactions(cards)
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Prepare data
        x_labels = TYPE_LIST
        y_labels = TYPE_LIST + SUBTYPES_LIST
        x_pos = np.arange(len(x_labels))
        y_pos = np.arange(len(y_labels))
        x_pos, y_pos = np.meshgrid(x_pos, y_pos)
        x_pos = x_pos.flatten()
        y_pos = y_pos.flatten()
        
        # Z-values (frequencies) and colors
        z_pos = np.zeros_like(x_pos, dtype=float)
        dz = [type_effect_counts[x_labels[x]].get(y_labels[y].lower(), 0) 
              for x, y in zip(x_pos, y_pos)]
        max_dz = max(dz) if dz else 1
        colors = [plt.cm.viridis(d / max_dz) for d in dz]
        
        # Plot bars
        ax.bar3d(x_pos, y_pos, z_pos, 1, 1, dz, color=colors, zsort='average')
        
        # Labels and customization
        ax.set_xlabel('Card Type')
        ax.set_ylabel('Type/Subtype in Effects')
        ax.set_zlabel('Frequency')
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha='right')
        ax.set_yticklabels(y_labels, rotation=-45, va='top')
        ax.set_title('Frequency of Card Types Mentioning Types/Subtypes in Effects')
        
        plt.tight_layout()
        plt.savefig('card_list/type_effect_3d.png')
        plt.close()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Analyze and plot card type and effect mention frequencies.")
    parser.add_argument('--plot-3d', action='store_true', help="Generate an additional 3D plot of type vs. effect type frequencies.")
    args = parser.parse_args()
    
    # Read the data
    cards = read_cards(DEFAULT_CARD_LIST_FILE)
    
    # Count types, subtypes, and effect mentions
    type_counts = count_types(cards)
    subtype_counts = count_subtypes(cards)
    effect_mentions = count_effect_mentions(cards)
    
    # Print results for quick reference
    output_text("Type Counts:", "note")
    for t, count in type_counts.items():
        output_text(f"{t}: {count}", "note")
    output_text("\nSubtype Counts:", "note")
    for s, count in subtype_counts.items():
        output_text(f"{s}: {count}", "note")
    output_text("\nEffect Mentions:", "note")
    for term, count in effect_mentions.items():
        output_text(f"{term}: {count}", "note")
    
    # Generate plots
    plot_data(type_counts, subtype_counts, effect_mentions, cards, plot_3d=args.plot_3d)
    output_text("\nPlots saved as 'card_list/type_counts.png', 'card_list/subtype_counts.png', 'card_list/effect_mentions.png', and individual type subtype mention plots", "success")
    if args.plot_3d:
        output_text("3D plot saved as 'card_list/type_effect_3d.png'", "success")

if __name__ == "__main__":
    main()
