
from src.scraper import WikipediaScraper
import time 

def main(): 
    start = time.time()
    scraper = WikipediaScraper()

    for country in scraper.get_countries(): 
        scraper.get_leaders(country)

    output_type = "json"
    scraper.save(f"leaders.{output_type}", filetype=output_type)

    end = time.time()
    print(f"Scraping completed in {end - start:.2f} seconds and saved.")

if __name__ == "__main__":
    main()