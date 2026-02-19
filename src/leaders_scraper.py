
import requests 
from bs4 import BeautifulSoup
import re 
import json 

# <25 lines
def get_first_paragraph(wikipedia_url, session):
    r = session.get(wikipedia_url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    first_paragraph = ""
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if text and p.find("b"):
            first_paragraph = text
            break

    for pat, rep in [
        (r"\[[^\]]*?\]", ""), (r"\([^)]*?\)", ""), (r"/[^/]{2,}/", ""),
        (r"(?i)\b(écouter|listen)\b", ""), (r"\u00a0", " "),
        (r"\s+([,;:.!?])", r"\1"), (r"\s+", " ")
    ]:
        first_paragraph = re.sub(pat, rep, first_paragraph).strip()

    return first_paragraph


def get_leaders():
    root_url = "https://country-leaders.onrender.com"

    session = requests.Session()
    session.headers.update({"User-Agent": "SeanBot/1.0 (learning scraping)"})

    cookies = session.get(f"{root_url}/cookie", timeout=10).cookies
    countries = session.get(f"{root_url}/countries", cookies=cookies, timeout=10).json()

    leaders_per_country = {}

    for country in countries:
        leaders = session.get(f"{root_url}/leaders", cookies=cookies, params={"country": country}, timeout=10).json()

        if not isinstance(leaders, list):  # cookie expired / error payload
            cookies = session.get(f"{root_url}/cookie", timeout=10).cookies
            leaders = session.get(f"{root_url}/leaders", cookies=cookies, params={"country": country}, timeout=10).json()
            
        for leader in leaders:
            url = leader.get("wikipedia_url")
            if url:
                leader["first_paragraph"] = get_first_paragraph(url, session)

        leaders_per_country[country] = leaders

    return leaders_per_country


def save(leaders_per_country, filename="leaders.json"): 
    with open(filename, "w", encoding="utf-8") as f: 
        json.dump(leaders_per_country, f, indent=4, ensure_ascii=False)


# 🔥 This part makes the script executable
if __name__ == "__main__":
    data = get_leaders()
    save(data)
    print("Scraping completed and saved to leaders.json")