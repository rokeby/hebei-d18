"""CSV data loading utilities for the folktale generator."""

import os
import csv
from typing import List, Dict, Optional

def load_bilingual_csv(filename: str, data_path: str = "./data") -> List[Dict[str, str]]:
    """Load CSV file and return list of bilingual pairs (zh, en).
    
    Args:
        filename: The name of the CSV file.
        data_path: The directory containing the CSV file.
        
    Returns:
        A list of dictionaries with 'zh' and 'en' keys.
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
    """
    data = []
    filepath = os.path.join(data_path, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:  # Ensure we have both languages
                    zh = row[0].strip('"')
                    en = row[1].strip('"')
                    data.append({"zh": zh, "en": en})
                elif len(row) == 1:  # Handle single language entries
                    item = row[0].strip('"')
                    data.append({"zh": item, "en": item})
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        raise
    return data

def load_all_data_files(data_path: str = "./data") -> Dict[str, List[Dict[str, str]]]:
    """Load all CSV data files from the data directory.
    
    Args:
        data_path: The directory containing the CSV files.
        
    Returns:
        A dictionary mapping file names (without .csv) to lists of bilingual data.
    """
    data_sets = {}
    data_files = [
        "characters.csv",
        "places.csv",
        "objects.csv",
        "events.csv",
        "interventions.csv",
        "story_seeds.csv",
        "endings.csv"
    ]
    
    for filename in data_files:
        try:
            base_name = os.path.splitext(filename)[0]  # Remove .csv extension
            data_sets[base_name] = load_bilingual_csv(filename, data_path)
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Using empty list.")
            data_sets[base_name] = []
    
    return data_sets