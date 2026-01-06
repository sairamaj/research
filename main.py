from bs4 import BeautifulSoup
import sys
import os
import asyncio
import time
import random
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
    
    unique_id = extract_startup_id_from_url(full_url)
    output_filename = get_output_filepath(unique_id)
    
    # Check if cache exists
    if os.path.exists(output_filename):
        print(f"Cache found for {full_url}, skipping scrape")
        return
    
    print(f"Scraping {full_url}")
    scrape_with_selenium(full_url, output_filename)


def main():
    """Main entry point for the scraper."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <html_file> [max_links]")
        print("Please provide the path to an HTML file as a command line argument.")
        print("Optional: max_links (default: 2)")
        sys.exit(1)

    # Ensure output directory exists (don't delete to preserve cache)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("generated", exist_ok=True)

    input_file = sys.argv[1]
    max_links = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    with open(input_file, "r", encoding="utf-8") as fin:
        html = fin.read()

    startup_links = extract_startup_links(html)

    if startup_links:
        for i, link in enumerate(startup_links[:max_links]):
            full_url = BASE_URL + link
            unique_id = extract_startup_id_from_url(full_url)
            output_filename = get_output_filepath(unique_id)
            if os.path.exists(output_filename):
                print(f"Cache found for {full_url}, skipping scrape")
            else:
                delay = random.uniform(5, 12)
                print(f"Sleeping for {delay:.1f} seconds to simulate human browsing...")
                time.sleep(delay)
                scrape_startup(link)
    else:
        print("No startup links found in the HTML file.")

    run_extract_info_for_scraped_files()
    merge_markdown_files()


def run_extract_info_for_scraped_files():
    """
    Run the extract_info_from_content process on all HTML files in the OUTPUT_DIR directory,
    and put the resulting markdown in the 'generated' directory.
    """
    from extract_info_from_content import process_file
    html_files = [
        os.path.join(OUTPUT_DIR, f)
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith(".html")
    ]
    if not html_files:
        print(f"No scraped html files found in {OUTPUT_DIR}")
        return

    async def batch_process():
        for html_file in html_files:
            await process_file(html_file, output_dir="generated")
    asyncio.run(batch_process())


def merge_markdown_files(output_dir="generated", summary_filename="summary.md"):
    """
    Merge all .md files in the output_dir into a single summary.md file.
    """
    md_files = [
        f for f in os.listdir(output_dir)
        if f.endswith(".md") and f != summary_filename
    ]
    if not md_files:
        print(f"No markdown files found in {output_dir} to merge.")
        return
    
    merged_content = []
    for md_file in md_files:
        filepath = os.path.join(output_dir, md_file)
        with open(filepath, "r", encoding="utf-8") as fin:
            content = fin.read()
            # Do not add filename as a header
            merged_content.append(f"{content}\n")

    summary_path = os.path.join(output_dir, summary_filename)
    with open(summary_path, "w", encoding="utf-8") as fout:
        fout.write("\n\n".join(merged_content))

    print(f"Merged {len(md_files)} markdown files into {summary_path}")


if __name__ == "__main__":
    main()  