from reddit_scraper import RedditScraper
from data_processor import DataProcessor
import pandas as pd

def test_scraper():
    print("Starting test scraper for Nothing Phone 3a complaints...")
    
    # Initialize scraper and processor
    scraper = RedditScraper()
    processor = DataProcessor()
    
    try:
        # Get posts from Reddit (limited to 10 posts)
        print("\nFetching posts from Reddit...")
        posts_data = scraper.get_posts(limit=10)  # We'll add this parameter to RedditScraper
        print(f"Found {len(posts_data)} posts")
        
        # Print sample of raw data
        print("\nSample of raw data:")
        for i, post in enumerate(posts_data[:2]):  # Show first 2 posts as sample
            print(f"\nPost {i+1}:")
            print(f"Title: {post['title']}")
            print(f"Text: {post['text'][:200]}...")  # First 200 chars
            print(f"Number of comments: {len(post['comments'])}")
            if post['comments']:
                print("First comment:", post['comments'][0]['text'][:100], "...")
        
        # Process complaints
        print("\nAnalyzing complaints...")
        complaints = processor.extract_complaints(posts_data)
        print(f"Found {len(complaints)} unique complaints")
        
        # Print sample of processed complaints
        print("\nSample of processed complaints:")
        for complaint, count in list(complaints.items())[:5]:  # Show first 5 complaints
            print(f"\nComplaint: {complaint}")
            print(f"Count: {count}")
        
        # Save to CSV
        output_file = 'test_complaints.csv'
        processor.save_to_csv(complaints, filename=output_file)
        print(f"\nComplaints data saved to {output_file}")
        
        # Read and display the CSV
        print("\nContents of CSV file:")
        df = pd.read_csv(output_file)
        print(df.head())
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_scraper() 