#!/usr/bin/env python3
"""
Screenshot Search Tool - Finds top 5 matches from indexed screenshots
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DESCRIPTIONS_FILE = "screenshot_descriptions.json"

def load_descriptions(file_path: str = DESCRIPTIONS_FILE) -> Dict[str, str]:
    """Load descriptions from JSON file."""
    if not os.path.exists(file_path):
        print(f"Error: Descriptions file '{file_path}' not found.")
        print("Please run index_screenshots.py first to create the index.")
        return {}
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Error: Could not read descriptions file '{file_path}'.")
        return {}

def search_screenshots(query: str, descriptions: Dict[str, str], top_k: int = 5) -> List[Tuple[str, str, int]]:
    """Search for screenshots matching the query."""
    if not descriptions:
        return []
    
    # Prepare the search prompt
    descriptions_text = "\n".join([f"{i+1}. {filename}: {desc}" for i, (filename, desc) in enumerate(descriptions.items())])
    
    search_prompt = f"""Given this search query: '{query}', rank these screenshot descriptions by relevance. Return the top {top_k} matches with confidence scores (0-100).

Format your response as:
1. filename: confidence_score
2. filename: confidence_score
...

Screenshot descriptions:
{descriptions_text}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": search_prompt
                }
            ],
            max_tokens=500
        )
        
        results = []
        response_text = response.choices[0].message.content
        
        # Parse the response to extract results
        lines = response_text.strip().split('\n')
        for line in lines:
            if ':' in line and any(char.isdigit() for char in line):
                try:
                    # Extract filename and confidence score
                    parts = line.split(':')
                    if len(parts) >= 2:
                        filename_part = parts[0].strip()
                        score_part = parts[1].strip()
                        
                        # Remove numbering from filename
                        filename = filename_part.split('. ', 1)[-1] if '. ' in filename_part else filename_part
                        
                        # Extract confidence score
                        score = int(''.join(filter(str.isdigit, score_part)))
                        
                        if filename in descriptions:
                            results.append((filename, descriptions[filename], score))
                except (ValueError, IndexError):
                    continue
        
        return results[:top_k]
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []

def display_results(results: List[Tuple[str, str, int]], query: str) -> None:
    """Display search results in a formatted way."""
    if results:
        print(f"\nTop {len(results)} results for '{query}':")
        print("-" * 60)
        for i, (filename, description, score) in enumerate(results, 1):
            print(f"{i}. {Path(filename).name}")
            print(f"   Confidence: {score}%")
            print(f"   Description: {description[:100]}...")
            print()
    else:
        print("No results found.")

def main():
    parser = argparse.ArgumentParser(description="Search indexed screenshots")
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--input', default=DESCRIPTIONS_FILE, help=f'Input JSON file (default: {DESCRIPTIONS_FILE})')
    parser.add_argument('--top', type=int, default=5, help='Number of top results to return (default: 5)')
    
    args = parser.parse_args()
    
    # Load descriptions
    descriptions = load_descriptions(args.input)
    if not descriptions:
        return
    
    print(f"Loaded {len(descriptions)} screenshot descriptions from {args.input}")
    
    # Search
    results = search_screenshots(args.query, descriptions, args.top)
    
    # Display results
    display_results(results, args.query)

if __name__ == "__main__":
    main()