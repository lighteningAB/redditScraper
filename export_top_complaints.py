import os
import praw
import csv
from dotenv import load_dotenv
from test_language_model_processor import SimpleLanguageModelProcessor
import argparse

def fetch_reddit_comments(product_name, num_posts=10):
    """Fetch comments from Reddit posts about a specific product."""
    load_dotenv()
    
    # Initialize Reddit client
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    
    # Search for posts about the product
    search_query = f"{product_name} review OR {product_name} thoughts OR {product_name} experience"
    subreddits = ['android', 'smartphones', 'gadgets', 'technology']
    
    all_comments = []
    posts_processed = 0
    
    print(f"Fetching comments about {product_name}...")
    
    for subreddit_name in subreddits:
        if posts_processed >= num_posts:
            break
            
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.search(search_query, sort='relevance', time_filter='month', limit=num_posts):
            if posts_processed >= num_posts:
                break
                
            print(f"\nAnalyzing post: {post.title}")
            print(f"URL: {post.url}")
            
            # Get comments from the post
            post.comments.replace_more(limit=0)  # Remove MoreComments objects
            for comment in post.comments.list():
                if hasattr(comment, 'body') and comment.body:
                    all_comments.append(comment.body)
                    
            posts_processed += 1
    
    print(f"\nFound {len(all_comments)} comments to analyze")
    return all_comments

def export_top_complaints(complaints, filename="top_10_complaints.csv"):
    """Export the top 10 most frequent complaints to a CSV file."""
    # Sort complaints by count in descending order
    sorted_complaints = sorted(complaints.items(), key=lambda x: x[1], reverse=True)
    
    # Take the top 10
    top_10 = sorted_complaints[:10]
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Summary', 'Count'])
        
        for complaint, count in top_10:
            writer.writerow([complaint, count])
    
    print(f"\nTop 10 complaints exported to {filename}")
    
    # Print the top 10 complaints to console
    print("\nTop 10 Most Frequent Complaints:")
    for i, (complaint, count) in enumerate(top_10, 1):
        print(f"{i}. {complaint} (Count: {count})")

def main():
    parser = argparse.ArgumentParser(description='Analyze Reddit comments about a product and extract top complaints.')
    parser.add_argument('product', help='Product name to search for (e.g., "iPhone 15" or "Samsung S24")')
    parser.add_argument('--posts', type=int, default=10, help='Number of Reddit posts to analyze (default: 10)')
    parser.add_argument('--output', default='top_10_complaints.csv', help='Output CSV file name (default: top_10_complaints.csv)')
    
    args = parser.parse_args()
    
    # Fetch comments from Reddit
    comments = fetch_reddit_comments(args.product, args.posts)
    
    # Process comments using the language model
    processor = SimpleLanguageModelProcessor()
    for comment in comments:
        processor.process_complaint(comment)
    
    # Export and display top complaints
    export_top_complaints(processor.get_complaints(), args.output)

if __name__ == "__main__":
    main() 