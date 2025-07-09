#!/usr/bin/env python3
"""
Flask Web Application for Screenshot Search Tool
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from dotenv import load_dotenv
import shutil

# Import our existing modules
from index_screenshots import get_image_description, load_descriptions, save_descriptions
from search_screenshots import search_screenshots

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'screenshots'
app.config['DESCRIPTIONS_FILE'] = 'screenshot_descriptions.json'

SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and Path(filename).suffix.lower() in SUPPORTED_FORMATS

def file_exists_in_screenshots(filename):
    """Check if file already exists in screenshots folder."""
    return os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400
    
    results = []
    descriptions = load_descriptions(app.config['DESCRIPTIONS_FILE'])
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Check if file already exists
            if file_exists_in_screenshots(filename):
                results.append({
                    'filename': filename,
                    'status': 'skipped',
                    'message': 'File already exists'
                })
                continue
            
            # Save file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get description from GPT-4 Vision
            description = get_image_description(filepath)
            
            if description:
                descriptions[filepath] = description
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'message': 'File uploaded and processed'
                })
            else:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': 'Failed to process image'
                })
        else:
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': 'Invalid file type'
            })
    
    # Save updated descriptions
    save_descriptions(descriptions, app.config['DESCRIPTIONS_FILE'])
    
    return jsonify({
        'results': results,
        'total_processed': len([r for r in results if r['status'] == 'success'])
    })

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests."""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    descriptions = load_descriptions(app.config['DESCRIPTIONS_FILE'])
    
    if not descriptions:
        return jsonify({'error': 'No screenshots indexed yet'}), 400
    
    results = search_screenshots(query, descriptions, top_k=5)
    
    # Format results for frontend
    formatted_results = []
    for filename, description, score in results:
        formatted_results.append({
            'filename': Path(filename).name,
            'full_path': filename,
            'description': description,
            'confidence': score,
            'image_url': f'/screenshots/{Path(filename).name}'
        })
    
    return jsonify({
        'results': formatted_results,
        'query': query,
        'total_found': len(formatted_results)
    })

@app.route('/screenshots/<filename>')
def uploaded_file(filename):
    """Serve uploaded screenshots."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/status')
def status():
    """Get current status of indexed images."""
    descriptions = load_descriptions(app.config['DESCRIPTIONS_FILE'])
    return jsonify({
        'total_images': len(descriptions),
        'indexed_files': list(descriptions.keys())
    })

if __name__ == '__main__':
    # Create screenshots directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)