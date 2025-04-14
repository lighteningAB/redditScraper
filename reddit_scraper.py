import praw
import os
from dotenv import load_dotenv
from typing import List, Dict

class RedditScraper:
    def __init__(self):
        load_dotenv()
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.search_terms = ['nothing phone 3a', 'nothing phone 3a pro']
        self.subreddits = ['android', 'smartphones', 'nothingphone']

    def get_posts(self, limit: int = 100) -> List[Dict]:
        """
        Scrape Reddit posts and comments related to Nothing Phone 3a and 3a Pro.
        Args:
            limit: Maximum number of posts to fetch per search term (default: 100)
        Returns:
            A list of dictionaries containing post data.
        """
        posts_data = []
        
        for subreddit_name in self.subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for search_term in self.search_terms:
                print(f"Searching r/{subreddit_name} for '{search_term}'...")
                # Search for posts
                for submission in subreddit.search(search_term, limit=limit):
                    post_data = {
                        'title': submission.title,
                        'text': submission.selftext,
                        'score': submission.score,
                        'url': submission.url,
                        'comments': []
                    }
                    
                    # Get comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        post_data['comments'].append({
                            'text': comment.body,
                            'score': comment.score
                        })
                    
                    posts_data.append(post_data)
                    print(f"Found post: {submission.title[:50]}...")
        
        return posts_data 