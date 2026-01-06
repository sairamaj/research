from bs4 import BeautifulSoup

# Read HTML from file
with open("html.txt", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Extract all hrefs containing "/startup"
startup_links = [
    tag["href"]
    for tag in soup.find_all("a", href=True)
    if "/startup" in tag["href"]
]

# Prepend base URL
base = "https://app.acquire.com/"
full_links = [base + link.lstrip("/") for link in startup_links]

print(full_links)