from reddit_scraper import RedditScraper
from data_processor import DataProcessor

def main():
    print("Starting Reddit scraper for Nothing Phone 3a complaints...")
    
    # Initialize scraper and processor
    scraper = RedditScraper()
    processor = DataProcessor()
    
    try:
        # Get posts from Reddit
        print("Fetching posts from Reddit...")
        posts_data = scraper.get_posts()
        print(f"Found {len(posts_data)} posts")
        
        # Process complaints
        print("Analyzing complaints...")
        complaints = processor.extract_complaints(posts_data)
        print(f"Found {len(complaints)} unique complaints")
        
        # Save to CSV
        processor.save_to_csv(complaints)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 