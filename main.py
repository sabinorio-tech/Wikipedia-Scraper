
from src.scraper import WikipediaScraper

def main(): 
    scraper = WikipediaScraper()
    for country in scraper.get_countries(): 
        scraper.get_leaders(country)
    scraper.get_leaders(country)
    print("Scraping completed and saved to leaders.json")

if __name__ == "__main__":
    main()