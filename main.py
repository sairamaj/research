from bs4 import BeautifulSoup
import sys
from web_browser import scrape_with_selenium

def extract_startup_links(html):
    soup = BeautifulSoup(html, "html.parser")
    startup_links = [
        tag["href"]
        for tag in soup.find_all("a", href=True)
        if "/startup" in tag["href"]
    ]
    return startup_links



def main():
        if len(sys.argv) < 2:
            print("Usage: python main.py <html_file>")
            print("Please provide the path to an HTML file as a command line argument.")
            sys.exit(1)
        input_file = sys.argv[1]
        with open(input_file, "r", encoding="utf-8") as fin:
            html = fin.read()
        startup_links = extract_startup_links(html)
        print(startup_links)
        #for link in startup_links:
        #    scrape_with_selenium(link)

if __name__ == "__main__":
    main()  