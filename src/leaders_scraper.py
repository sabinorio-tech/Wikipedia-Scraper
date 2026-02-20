
import requests 
from bs4 import BeautifulSoup
import re 
import json 


# Reteurns the first cleaned firzst paragraph of a wikipedia URL
def get_first_paragraph(wikipedia_url, session):
    r = session.get(wikipedia_url, timeout=10)  # makes an http request, timeout: avoids freezing
    soup = BeautifulSoup(r.text, "html.parser") # parses it into a navigable tree

    first_paragraph = ""
    for p in soup.find_all("p"): 
        text = p.get_text(" ", strip=True) # " " ": replaces inner tags with space?, strip removes extra whitespace  "
        if text and p.find("b"): # checks if paragraph isn't empty and contains bold text
            first_paragraph = text  # store it 
            break
    
    # Loop over multiple regex patterns
    for pat, rep in [
        (r"\[[^\]]*?\]", ""),  # removes reference ex: [1]
        (r"\([^)]*?\)", ""),   # removes parantheses ex: (1950)
        (r"/[^/]{2,}/", ""),   # removes prenunciation ex: /'makron/
        (r"(?i)\b(écouter|listen)\b", ""),  # removes "listen" or "écouter"
        (r"\u00a0", " "), # replaces werid non-breaking spaces with normal spaces
        (r"\s+([,;:.!?])", r"\1"),   # fixes spacing before punctuation 
        (r"\s+", " ")   # remove multiple spaces
    ]:
        first_paragraph = re.sub(pat, rep, first_paragraph).strip() # .strip() removes leftover whitespace

    return first_paragraph   # return cleaned paragraph

# main scraping function
def get_leaders():
    root_url = "https://country-leaders.onrender.com"

    session = requests.Session() # Creates persistent session: faster and cleaner cookie handling
    session.headers.update({"User-Agent": "SeanBot/1.0 (learning scraping)"})

    cookies = session.get(f"{root_url}/cookie", timeout=10).cookies # Requests cookie 
    countries = session.get(f"{root_url}/countries", cookies=cookies, timeout=10).json() # Gets list of countries

    leaders_per_country = {}

    for country in countries:
        leaders = session.get(f"{root_url}/leaders", cookies=cookies, params={"country": country}, timeout=10).json() # Fetch leaders for the country

        if not isinstance(leaders, list):  # cookie expired / error payload
            cookies = session.get(f"{root_url}/cookie", timeout=10).cookies
            leaders = session.get(f"{root_url}/leaders", cookies=cookies, params={"country": country}, timeout=10).json()
            
        for leader in leaders:
            url = leader.get("wikipedia_url") # name tag of the url
            if url: # Only if url exists, so it doesn't crash if it's empty
                # Adds new key to dictionary
                leader["first_paragraph"] = get_first_paragraph(url, session)

        leaders_per_country[country] = leaders

    return leaders_per_country

# Function to save data
def save(leaders_per_country, filename="leaders.json"): 
    with open(filename, "w", encoding="utf-8") as f: # UTF-8 is important?
        json.dump(leaders_per_country, f, indent=4, ensure_ascii=False)
        # indent for pretty formatting
        # ensure_ascii keeps special characters readable

# Only run this if script executed directly
if __name__ == "__main__":
    data = get_leaders()
    save(data)
    print("Scraping completed and saved to leaders.json")