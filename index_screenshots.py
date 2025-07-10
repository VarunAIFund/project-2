#!/usr/bin/env python3
"""
Screenshot Indexing Tool - Generates JSON descriptions using GPT-4 Vision API
"""

import os
import json
import argparse
import base64
from pathlib import Path
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DESCRIPTIONS_FILE = "screenshot_descriptions.json"
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_description(image_path: str) -> str:
    """Get description of an image using GPT-4 Vision API."""
    try:
        base64_image = encode_image(image_path)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image and provide a description based on the following rules:\n\n1. IF the image contains text, UI elements, buttons, menus, forms, error messages, or any digital interface elements:\n   - Provide a detailed description including ALL visible text, UI elements, colors, buttons, error messages, and any other visual elements that someone might search for.\n\n2. IF the image is purely visual content without text (like nature photos, objects, people, etc.):\n   - Provide only ONE descriptive sentence focusing on the main visual elements, colors, and objects.\n\nAnalyze the image and apply the appropriate rule."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return ""

def load_descriptions(file_path: str) -> Dict[str, str]:
    """Load existing descriptions from JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_descriptions(descriptions: Dict[str, str], file_path: str) -> None:
    """Save descriptions to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(descriptions, f, indent=2)

def index_screenshots(folder_path: str, output_file: str) -> None:
    """Index all screenshots in the given folder."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    descriptions = load_descriptions(output_file)
    
    # Find all image files
    image_files = []
    for ext in SUPPORTED_FORMATS:
        image_files.extend(folder.glob(f"*{ext}"))
        image_files.extend(folder.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"No image files found in '{folder_path}'")
        return
    
    print(f"Found {len(image_files)} image files to process...")
    
    processed = 0
    for image_path in image_files:
        filename = str(image_path)
        
        # Skip if already processed
        if filename in descriptions:
            print(f"Skipping {filename} (already processed)")
            continue
        
        print(f"Processing {filename}...")
        description = get_image_description(str(image_path))
        
        if description:
            descriptions[filename] = description
            processed += 1
            print(f"✓ Processed {filename}")
        else:
            print(f"✗ Failed to process {filename}")
    
    save_descriptions(descriptions, output_file)
    print(f"\nIndexing complete! Processed {processed} new images.")
    print(f"Total images in index: {len(descriptions)}")

def process_single_image(image_path: str, descriptions_file: str) -> bool:
    """Process a single image and add to descriptions file."""
    descriptions = load_descriptions(descriptions_file)
    
    if image_path in descriptions:
        return True  # Already processed
    
    description = get_image_description(image_path)
    if description:
        descriptions[image_path] = description
        save_descriptions(descriptions, descriptions_file)
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Index screenshots using GPT-4 Vision API")
    parser.add_argument('--folder', required=True, help='Path to folder containing screenshots')
    parser.add_argument('--output', default=DESCRIPTIONS_FILE, help=f'Output JSON file (default: {DESCRIPTIONS_FILE})')
    
    args = parser.parse_args()
    
    index_screenshots(args.folder, args.output)

if __name__ == "__main__":
    main()