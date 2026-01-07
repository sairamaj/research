# Startup Research Tool

A Python tool for scraping and analyzing startup listings from Acquire.com. This tool extracts startup information, processes it using LLM (Gemini), and generates structured markdown and CSV summaries.

## Features

- **Web Scraping**: Automatically scrapes startup pages from Acquire.com using Selenium
- **LLM Processing**: Extracts structured information from scraped content using Google's Gemini API
- **Caching**: Skips re-scraping if HTML files already exist
- **Batch Processing**: Processes multiple startups in parallel
- **Summary Generation**: Creates merged markdown files and CSV summaries for easy analysis
- **Mock Mode**: Test the tool without incurring LLM API costs

## Requirements

- Python 3.8+
- Chrome browser (for Selenium)
- Google Gemini API key (optional, for real LLM processing)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install ChromeDriver (if not already installed):
   - ChromeDriver should be available in your PATH, or Selenium will use the browser's built-in driver

4. (Optional) Set up Gemini API key for real LLM processing:
   - Create a `.env` file in the project root
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`

## Usage

### Basic Usage

```bash
python main.py <html_file> [max_links] [--use-real-llm]
```

**Parameters:**
- `html_file`: Path to an HTML file containing startup listings from Acquire.com
- `max_links`: (Optional) Maximum number of startup links to scrape (default: 2)
- `--use-real-llm`: (Optional) Use real Gemini API instead of mock mode (default: mock mode)

### Example

```bash
# Scrape first 5 startups using mock LLM (no API costs)
python main.py listings.html 5

# Scrape first 10 startups using real Gemini API
python main.py listings.html 10 --use-real-llm
```

## How It Works

1. **Link Extraction**: Parses the input HTML file to find all startup links (`/startup/...`)

2. **Web Scraping**: 
   - Scrapes each startup page using Selenium with Chrome in headless mode
   - Adds random delays (5-12 seconds) between requests to simulate human browsing
   - Saves HTML content to `output/` directory (cached for future runs)

3. **Information Extraction**:
   - Processes each scraped HTML file using LLM (Gemini) or mock mode
   - Extracts structured information:
     - Brief Description
     - Features
     - Asking Price
     - TTM Revenue & Profit
     - Last Month Revenue & Profit
     - Customers
     - Selling Reasoning
   - Generates markdown files in `generated/` directory

4. **Summary Generation**:
   - Merges all markdown files into `generated/summary.md`
   - Creates a CSV file (`generated/summary.txt`) with key metrics for spreadsheet import

## Project Structure

```
.
├── main.py                      # Main entry point
├── scraper.py                   # Web scraping logic
├── processor.py                 # Batch processing and summary generation
├── extract_info_from_content.py # LLM-based information extraction
├── url_utils.py                 # URL parsing utilities
├── file_utils.py                # File path utilities
├── web_browser.py               # Selenium browser automation
├── prompt.txt                   # LLM prompt template
├── requirements.txt             # Python dependencies
├── output/                      # Scraped HTML files (cached)
└── generated/                   # Generated markdown and CSV files
    ├── *.md                     # Individual startup markdown files
    ├── summary.md               # Merged markdown summary
    └── summary.txt              # CSV summary for spreadsheets
```

## Output Files

### Individual Markdown Files (`generated/*.md`)
Each startup gets its own markdown file with structured information extracted from the webpage.

### Summary Markdown (`generated/summary.md`)
All individual markdown files merged into a single document.

### CSV Summary (`generated/summary.txt`)
A CSV file with the following columns:
- Decision (defaults to "Pending")
- Brief Description
- Asking Price
- TTM Revenue
- TTM Profit
- Last Month Revenue
- Customers
- Selling Reasoning

This file can be imported directly into Google Sheets or Excel for further analysis.

## Mock Mode vs Real LLM

**Mock Mode (Default)**:
- No API costs
- Returns placeholder responses
- Useful for testing the scraping workflow
- Use when you just want to scrape HTML files

**Real LLM Mode (`--use-real-llm`)**:
- Uses Google Gemini API to extract structured information
- Requires `GEMINI_API_KEY` in `.env` file
- Incurs API costs
- Provides accurate information extraction

## Caching

The tool uses caching to avoid re-scraping:
- HTML files in `output/` directory are preserved
- If a startup's HTML file already exists, scraping is skipped
- To re-scrape, delete the corresponding HTML file from `output/`

## Notes

- The tool includes random delays between requests to be respectful to the target website
- Processing happens in parallel (default: 3 concurrent workers) for faster execution
- All monetary values and customer counts are extracted as-is from the source content
- The CSV summary properly handles commas in field values by quoting them

## Troubleshooting

**ChromeDriver not found:**
- Ensure Chrome browser is installed
- Selenium 4+ should automatically manage the driver

**No startup links found:**
- Verify your HTML file contains links with `/startup/` in the href attribute
- Check that the HTML file is from Acquire.com

**LLM API errors:**
- Verify your `GEMINI_API_KEY` is set correctly in `.env`
- Check your API quota/limits
- Use mock mode (`--use-real-llm` flag not set) to test without API

## License

This tool is provided as-is for research purposes.

