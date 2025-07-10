# Visual Memory Search

A screenshot search tool that allows you to search your screenshot history using natural language queries for both text content AND visual elements.

## Overview

Visual Memory Search enables you to find specific screenshots by describing what you're looking for in plain English. Whether you need to find "error message about auth" or "screenshot with blue button", this tool uses AI-powered image analysis to understand both the visual content and any text within your screenshots.

## Features

- **Natural Language Search**: Search using plain English queries like "error message about auth" or "screenshot with blue button"
- **Multi-Modal Analysis**: Analyzes both visual elements and text content within screenshots
- **Top 5 Results**: Returns the most relevant matches with confidence scores
- **Web Interface**: User-friendly web application with drag & drop upload
- **Batch Processing**: Command-line tools for processing large collections of screenshots
- **Multiple Formats**: Supports PNG, JPG, JPEG, GIF, BMP, and WEBP formats
- **AI-Powered**: Uses OpenAI's GPT-4 Vision API for intelligent image understanding

## Technical Stack

- **Backend**: Flask (Python)
- **AI Engine**: OpenAI GPT-4 Vision API
- **Frontend**: HTML/CSS/JavaScript
- **File Handling**: Werkzeug for secure uploads

## Prerequisites

- Python 3.7 or higher
- OpenAI API key
- Modern web browser

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd project-2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create a .env file in the project root
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

## Usage

### Web Interface

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and go to `http://localhost:5000`

3. Upload screenshots by dragging and dropping them onto the upload area

4. Search using natural language queries in the search box

### Command Line Tools

#### Index Screenshots
```bash
python index_screenshots.py --folder /path/to/screenshots
```

#### Search from Command Line
```bash
python search_screenshots.py --query "error message about authentication"
```

## Example Queries

- "error message about auth"
- "screenshot with blue button"
- "login form with username field"
- "red warning notification"
- "dashboard with charts"
- "settings page with toggle switches"

## Project Structure

```
project-2/
├── app.py                      # Flask web application
├── index_screenshots.py        # Batch indexing tool
├── search_screenshots.py       # Command-line search tool
├── requirements.txt           # Python dependencies
├── screenshot_descriptions.json # Generated descriptions database
├── screenshots/              # Upload directory for screenshots
├── templates/
│   └── index.html           # Web interface template
└── static/
    ├── style.css           # Styling
    └── script.js           # Frontend JavaScript
```

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload and process screenshots
- `POST /search` - Search screenshots with natural language
- `GET /screenshots/<filename>` - Serve uploaded images
- `GET /status` - Get indexing status

## How It Works

1. **Upload**: Screenshots are uploaded via web interface or processed in batch
2. **Analysis**: GPT-4 Vision API analyzes each image for both visual elements and text content
3. **Indexing**: Descriptions are stored in a JSON database for fast searching
4. **Search**: Natural language queries are matched against descriptions using AI
5. **Results**: Top 5 most relevant matches are returned with confidence scores

## Configuration

The application uses the following configuration:
- Maximum file size: 16MB
- Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP
- Default port: 5000
- Results per search: 5 (configurable)

## Contributing

This project is part of a buildathon challenge focusing on visual memory search capabilities. The implementation balances text and visual relevance using a multi-modal embedding approach.
