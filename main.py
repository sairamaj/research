import sys
import os
from url_utils import extract_startup_links
from scraper import scrape_startups_with_delay
from processor import run_extract_info_for_scraped_files, merge_markdown_files, create_summary_txt

BASE_URL = "https://app.acquire.com"
OUTPUT_DIR = "output"
GENERATED_DIR = "generated"


def parse_args():
    """
    Parse command line arguments.

    Tasks:
      --extract-links      Extract all links from the HTML file
      --scrape            Scrape the web for each link
      --use-llm           Use LLM to process data
      --merge             Merge the processed data
      --all               Do all tasks above (default if no task args are supplied)

    Usage:
      python main.py <html_file> [max_links] [task flags]
    """
    import argparse

    parser = argparse.ArgumentParser(description='Startup Web Automation Tool')
    parser.add_argument('html_file', type=str, help='Path to the HTML file')
    parser.add_argument('max_links', type=int, nargs='?', default=2, help='Maximum number of links to process (default: 2)')
    parser.add_argument('--extract-links', action='store_true', help='Extract all links from the HTML file')
    parser.add_argument('--scrape', action='store_true', help='Scrape the web for each link')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM to process data')
    parser.add_argument('--merge', action='store_true', help='Merge the processed data')
    parser.add_argument('--all', action='store_true', help='Do all tasks (extract, scrape, LLM, merge)')

    args = parser.parse_args()

    # If no task args given, treat as --all
    if not (args.extract_links or args.scrape or args.use_llm or args.merge or args.all):
        parser.print_help()
        sys.exit(1)
    do_all = args.all

    task_flags = {
        'extract_links': args.extract_links or do_all,
        'scrape': args.scrape or do_all,
        'use_llm': args.use_llm or do_all,
        'merge': args.merge or do_all
    }

    return {
        'html_file': args.html_file,
        'max_links': args.max_links,
        'use_real_llm': args.use_llm or do_all,
        **task_flags
    }

def main():
    """Main entry point for the scraper."""
    args = parse_args()

    if not args or not args['html_file']:
        print("Usage: python main.py <html_file> [max_links] [task flags]")
        print("Please provide the path to an HTML file as a command line argument.")
        print("Optional arguments:")
        print("  max_links: Maximum number of links to process (default: 2)")
        print("Task flags:")
        print("  --extract-links      Extract all links from the HTML file")
        print("  --scrape            Scrape the web for each link")
        print("  --use-llm           Use LLM to process data")
        print("  --merge             Merge the processed data")
        print("  --all               Do all tasks above (default if no task args are supplied)")
        sys.exit(1)

    # Ensure output directories exist (don't delete to preserve cache)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(GENERATED_DIR, exist_ok=True)

    # Step 1: Extract Links
    if args['extract_links']:
        with open(args['html_file'], "r", encoding="utf-8") as fin:
            html = fin.read()
        startup_links = extract_startup_links(html)
        if startup_links:
            print(f"Extracted {len(startup_links)} links from HTML file.")
            with open("links.txt", "w", encoding="utf-8") as fout:
                for link in startup_links:
                    fout.write(link + "\n")
            print("Links have been written to links.txt.")
        else:
            print("No startup links found in the HTML file.")
    else:
        startup_links = None

    # Step 2: Scrape
    if args['scrape']:
        if startup_links is None:
            # Need to parse HTML file if not already read above
            with open(args['html_file'], "r", encoding="utf-8") as fin:
                html = fin.read()
            startup_links = extract_startup_links(html)
        if startup_links:
            scrape_startups_with_delay(
                startup_links, 
                base_url=BASE_URL, 
                output_dir=OUTPUT_DIR, 
                max_links=args['max_links']
            )
        else:
            print("No startup links to scrape.")

    # Step 3: Use LLM for Extraction
    if args['use_llm']:
        run_extract_info_for_scraped_files(
            output_dir=OUTPUT_DIR, 
            generated_dir=GENERATED_DIR,
            use_real_llm=args['use_real_llm']
        )

    # Step 4: Merge
    if args['merge']:
        merge_markdown_files(output_dir=GENERATED_DIR)
        create_summary_txt(generated_dir=GENERATED_DIR)

if __name__ == "__main__":
    main()  