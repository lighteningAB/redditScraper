import os
import praw
import pandas as pd
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from test_language_model_processor import SimpleLanguageModelProcessor

def setup_reddit_client() -> praw.Reddit:
    """Set up and return a Reddit client using environment variables."""
    load_dotenv()
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )

def get_reddit_comments(reddit: praw.Reddit, product: str, limit: int = 100) -> List[str]:
    """Fetch comments from Reddit about a specific product."""
    comments = []
    subreddits = ['Smartphones', 'Android', 'NothingTech', 'TechReviews']
    
    for subreddit in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit)
            search_results = subreddit.search(product, limit=limit, sort='relevance')
            
            for post in search_results:
                print(f"\nAnalyzing post: {post.title}")
                print(f"URL: {post.url}\n")
                
                # Get comments from the post
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    if comment.body and len(comment.body.strip()) > 20:  # Filter out very short comments
                        comments.append(comment.body)
                        
        except Exception as e:
            print(f"Error fetching from r/{subreddit}: {str(e)}")
            
    return comments

def analyze_complaints(comments: List[str], processor: SimpleLanguageModelProcessor) -> List[Tuple[str, int]]:
    """Analyze comments and return top complaints."""
    for comment in comments:
        processor.process_complaint(comment)
    return processor.get_complaints()

def export_complaints(complaints: List[Tuple[str, int]], output_file: str = 'top_10_complaints.csv'):
    """Export complaints to a CSV file."""
    df = pd.DataFrame(complaints[:10], columns=['Complaint', 'Count'])
    df.to_csv(output_file, index=False)
    print(f"\nTop 10 complaints exported to {output_file}\n")

def print_complaints(complaints: List[Tuple[str, int]]):
    """Print the top complaints in a readable format."""
    print("\nTop 10 Most Frequent Complaints:")
    for i, (complaint, count) in enumerate(complaints[:10], 1):
        print(f"{i}. {complaint} (Count: {count})")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Export top complaints about a product from Reddit')
    parser.add_argument('product', help='Product to search for')
    parser.add_argument('--posts', type=int, default=100, help='Number of posts to analyze')
    parser.add_argument('--output', default='top_10_complaints.csv', help='Output CSV file')
    args = parser.parse_args()

    # Initialize Reddit client and processor
    reddit = setup_reddit_client()
    processor = SimpleLanguageModelProcessor()

    # Fetch and analyze comments
    print(f"Fetching comments about {args.product}...")
    comments = get_reddit_comments(reddit, args.product, args.posts)
    print(f"\nFound {len(comments)} comments to analyze")

    # Process complaints
    complaints = analyze_complaints(comments, processor)
    
    # Export and print results
    export_complaints(complaints, args.output)
    print_complaints(complaints)

if __name__ == "__main__":
    main() 