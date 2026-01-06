import os
import time
import random
from web_browser import scrape_with_selenium
from url_utils import extract_startup_id_from_url
from file_utils import get_output_filepath


def scrape_startup(link, base_url="https://app.acquire.com", output_dir="output"):
    """Scrape a single startup page."""
    full_url = base_url + link
    
    unique_id = extract_startup_id_from_url(full_url)
    output_filename = get_output_filepath(unique_id, output_dir)
    
    # Check if cache exists
    if os.path.exists(output_filename):
        print(f"Cache found for {full_url}, skipping scrape")
        return
    
    print(f"Scraping {full_url}")
    scrape_with_selenium(full_url, output_filename)


def scrape_startups_with_delay(startup_links, base_url="https://app.acquire.com", 
                               output_dir="output", max_links=None):
    """
    Scrape multiple startup pages with random delays between requests.
    
    Args:
        startup_links: List of startup links to scrape
        base_url: Base URL for the website
        output_dir: Directory to save scraped HTML files
        max_links: Maximum number of links to scrape (None for all)
    """
    links_to_scrape = startup_links[:max_links] if max_links else startup_links
    
    for i, link in enumerate(links_to_scrape):
        full_url = base_url + link
        unique_id = extract_startup_id_from_url(full_url)
        output_filename = get_output_filepath(unique_id, output_dir)
        
        if os.path.exists(output_filename):
            print(f"Cache found for {full_url}, skipping scrape")
        else:
            delay = random.uniform(5, 12)
            print(f"Sleeping for {delay:.1f} seconds to simulate human browsing...")
            time.sleep(delay)
            scrape_startup(link, base_url, output_dir)

