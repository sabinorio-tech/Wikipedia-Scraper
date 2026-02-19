
from src.scraper import WikipediaScraper

def main(): 
    scraper = WikipediaScraper()

    for country in scraper.get_countries(): 
        scraper.get_leaders(country)

    output_type = "csv"
    scraper.save(f"leaders.{output_type}", filetype=output_type)

    print("Scraping completed and saved.")

if __name__ == "__main__":
    main()