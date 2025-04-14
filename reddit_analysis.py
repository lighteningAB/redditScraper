import praw
import csv
from test_language_model_processor import SimpleLanguageModelProcessor
from dotenv import load_dotenv
import os
import time

def setup_reddit():
    """Initialize and return a Reddit API client."""
    load_dotenv()
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'ComplaintAnalysis/1.0')
    )

def get_reddit_comments(reddit, search_query, post_limit=5):
    """Fetch posts and comments from Reddit based on search query."""
    comments = []
    subreddits = ['android', 'nothingphone', 'smartphones', 'techsupport']
    
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        search_results = subreddit.search(search_query, limit=post_limit)
        
        for post in search_results:
            print(f"\nAnalyzing post: {post.title}")
            print(f"URL: {post.url}")
            
            # Get post comments
            post.comments.replace_more(limit=0)  # Remove MoreComments objects
            for comment in post.comments.list():
                if hasattr(comment, 'body') and comment.body:
                    comments.append(comment.body)
            
            # Add a small delay to respect Reddit's rate limits
            time.sleep(1)
    
    return comments

def main():
    # Initialize Reddit client
    reddit = setup_reddit()
    
    # Search query
    search_query = "Nothing Phone 3a OR Nothing Phone 3a Pro"
    
    # Get comments from Reddit
    print("Fetching comments from Reddit...")
    reddit_comments = get_reddit_comments(reddit, search_query)
    
    if not reddit_comments:
        print("No comments found!")
        return
    
    print(f"\nFound {len(reddit_comments)} comments to analyze")
    
    # Initialize the processor
    processor = SimpleLanguageModelProcessor()
    
    # Process each comment
    for comment in reddit_comments:
        processor.process_complaint(comment)
    
    # Get the processed complaints
    complaints = processor.get_complaints()
    
    # Write results to CSV
    with open('reddit_complaints_analysis.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Complaint', 'Count'])
        for complaint, count in complaints.items():
            writer.writerow([complaint, count])
    
    print("\nAnalysis complete! Results have been saved to 'reddit_complaints_analysis.csv'")
    print("\nSummary of complaints:")
    for complaint, count in complaints.items():
        print(f"\nComplaint: {complaint}")
        print(f"Occurrences: {count}")

if __name__ == "__main__":
    main() 