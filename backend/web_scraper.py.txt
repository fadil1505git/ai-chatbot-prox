import requests
from bs4 import BeautifulSoup

def fetch_web_content(url: str) -> str:
    """
    Muat turun dan ekstrak teks bersih dari laman web.
    """
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buang skrip dan gaya
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text = soup.get_text(separator=' ', strip=True)
    return text
