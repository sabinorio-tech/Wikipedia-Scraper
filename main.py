
from src.scraper import WikipediaScraper
import time
def main():
    start = time.time()

    scraper = WikipediaScraper()
    for country in scraper.get_countries(): 
        scraper.get_leaders(country)
    scraper.get_leaders(country)

    end = time.time()
    print(f"Scraping completed in {end - start:.2f} seconds and saved to leader.json")

if __name__ == "__main__":
    main()