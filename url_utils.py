from bs4 import BeautifulSoup
from urllib.parse import urlparse


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

