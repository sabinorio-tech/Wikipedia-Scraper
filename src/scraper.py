import json 
import re 
import requests
from bs4 import BeautifulSoup
import csv


class WikipediaScraper: 
    def __init__(self): 
        self.base_url = "https://country-leaders.onrender.com"
        self.country_endpoint = "/countries"
        self.leaders_endpoint = "/leaders"
        self.cookies_endpoint = "/cookie"

        self.leaders_data ={}
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "SeanBot/1.0 (learning scraping)"
            }
        )

        self.cookie = self.refresh_cookie()

    def refresh_cookie(self): 
        self.cookie = self.session.get(
            f"{self.base_url}{self.cookies_endpoint}", 
            timeout=10).cookies
        return self.cookie
    
    def get_countries(self): 
        r = self.session.get(
            f"{self.base_url}{self.country_endpoint}", 
            cookies=self.cookie, 
            timeout=10
        )
        return r.json()
    
    def get_leaders(self, country: str):
        r = self.session.get(
            f"{self.base_url}{self.leaders_endpoint}", 
            cookies=self.cookie,
            params={"country": country},
            timeout=10
        )
        leaders = r.json()

        # If cookie expires during run

        if not isinstance(leaders, list):
            self.refresh_cookie()
            r = self.session.get(
                f"{self.base_url}{self.leaders_endpoint}",
                cookies=self.cookie,
                params={"country": country},
                timeout=10
            )
            leaders = r.json()
        
        for leader in leaders: 
            url = leader.get("wikipedia_url")
            if url: 
                leader["first_paragraph"] = self.get_first_paragraph(url)
            
        self.leaders_data[country] = leaders
        
    def get_first_paragraph(self, wikipedia_url: str):
        r = self.session.get(wikipedia_url, timeout=10)
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
    
    def save(self, filepath: str, filetype="json"):
        if filetype == "json": 
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.leaders_data, f, indent=4, ensure_ascii=False)
        
        elif filetype == "csv": 
            with open(filepath, "w", newline="", encoding="utf-8") as f: 
                writer = csv.writer(f)
                writer.writerow(["country", "first_name", "last_name", "first_paragraph"])

                for country, leaders in self.leaders_data.items(): 
                    for leader in leaders: 
                        writer.writerow([
                            country, 
                            leader.get("first_name"),
                            leader.get("last_name"), 
                            leader.get("first_paragraph")
                        ])

if __name__ == "__main__":
    scraper = WikipediaScraper()
    for country in scraper.get_countries():
        scraper.get_leaders(country)
    scraper.to_json_file("../leaders.json")

    print("Scraping completed and saved to leaders.json")