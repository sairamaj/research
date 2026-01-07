import sys
import os
from url_utils import extract_startup_links
from scraper import scrape_startups_with_delay
from processor import run_extract_info_for_scraped_files, merge_markdown_files, create_summary_txt

BASE_URL = "https://app.acquire.com"
OUTPUT_DIR = "output"
GENERATED_DIR = "generated"


def parse_args():
    """Parse command line arguments."""
    args = {
        'html_file': None,
        'max_links': 2,
        'use_real_llm': False
    }
    
    # Check for --use-real-llm flag
    if '--use-real-llm' in sys.argv:
        args['use_real_llm'] = True
        sys.argv.remove('--use-real-llm')
    
    # Parse positional arguments
    if len(sys.argv) < 2:
        return None
    
    args['html_file'] = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            args['max_links'] = int(sys.argv[2])
        except ValueError:
            pass
    
    return args


def main():
    """Main entry point for the scraper."""
    args = parse_args()
    
    if not args or not args['html_file']:
        print("Usage: python main.py <html_file> [max_links] [--use-real-llm]")
        print("Please provide the path to an HTML file as a command line argument.")
        print("Optional arguments:")
        print("  max_links: Maximum number of links to scrape (default: 2)")
        print("  --use-real-llm: Use real LLM API instead of mock (default: mock mode)")
        sys.exit(1)

    # Ensure output directories exist (don't delete to preserve cache)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(GENERATED_DIR, exist_ok=True)

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
        print("No startup links found in the HTML file.")

    run_extract_info_for_scraped_files(
        output_dir=OUTPUT_DIR, 
        generated_dir=GENERATED_DIR,
        use_real_llm=args['use_real_llm']
    )
    merge_markdown_files(output_dir=GENERATED_DIR)
    create_summary_txt(generated_dir=GENERATED_DIR)


if __name__ == "__main__":
    main()  