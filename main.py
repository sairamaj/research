from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urlparse
from web_browser import scrape_with_selenium

BASE_URL = "https://app.acquire.com"
OUTPUT_DIR = "output"


def extract_startup_links(html):
    """Extract all startup links from HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    startup_links = [
        tag["href"]
        for tag in soup.find_all("a", href=True)
        if "/startup" in tag["href"]
    ]
    return startup_links


def extract_startup_id_from_url(url):
    """
    Extract unique startup ID from URL.
    
    Example: '/startup/vfSZGGC6Tdcm31CLnSZu9bRulbJ3/kNCw0mGio9RUf2y0YwX8'
    Returns: 'vfSZGGC6Tdcm31CLnSZu9bRulbJ3'
    """
    parsed_path = urlparse(url).path
    parts = parsed_path.split('/')
    
    if "startup" in parts:
        startup_idx = parts.index("startup")
        if len(parts) > startup_idx + 1:
            return parts[startup_idx + 1]
    
    return "unknown"


def get_output_filepath(unique_id, output_dir=OUTPUT_DIR):
    """Generate output file path for a startup ID."""
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{unique_id}.html")


def scrape_startup(link, base_url=BASE_URL):
    """Scrape a single startup page."""
    full_url = base_url + link
    print(f"Scraping {full_url}")
    
    unique_id = extract_startup_id_from_url(full_url)
    output_filename = get_output_filepath(unique_id)
    
    scrape_with_selenium(full_url, output_filename)


def main():
    """Main entry point for the scraper."""
    import shutil

    if len(sys.argv) < 2:
        print("Usage: python main.py <html_file>")
        print("Please provide the path to an HTML file as a command line argument.")
        sys.exit(1)

    # Clean the output directory if it exists
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as fin:
        html = fin.read()

    startup_links = extract_startup_links(html)

    # For now, only scrape the first startup
    if startup_links:
        for link in startup_links:
            scrape_startup(link)
            break   #for now, only scrape the first startup
    else:
        print("No startup links found in the HTML file.")


if __name__ == "__main__":
    main()  