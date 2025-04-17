import os
import praw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv
from openai import OpenAI
import argparse
import json
import re
from datetime import datetime, timedelta

# For YouTube API
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

# For Twitter/X API
try:
    import tweepy
    TWITTER_API_AVAILABLE = True
except ImportError:
    TWITTER_API_AVAILABLE = False

class MultiPlatformFeedbackAnalyzer:
    def __init__(self, product_name: str):
        """Initialize the analyzer with product name and API clients."""
        load_dotenv()
        self.product_name = product_name
        
        # Initialize Reddit client
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize YouTube client if API key is available
        self.youtube = None
        if YOUTUBE_API_AVAILABLE and os.getenv('YOUTUBE_API_KEY'):
            self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        # Initialize Twitter/X client if credentials are available
        self.twitter = None
        if TWITTER_API_AVAILABLE and os.getenv('TWITTER_API_KEY') and os.getenv('TWITTER_API_SECRET'):
            client = tweepy.Client(
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            self.twitter = client
        
        # Define feature categories
        self.feature_categories = [
            "design", "camera", "performance", "battery", 
            "software features", "display", "price", "audio", "build quality"
        ]
        
        # Define feedback types
        self.feedback_types = [
            "missing_feature",
            "poor_compared_to_competitor",
            "unnecessary_feature",
            "awesome"
        ]
        
        # Initialize feedback matrix
        self.feedback_matrix = np.zeros((len(self.feature_categories), len(self.feedback_types)))
        self.feedback_details = []

    def fetch_reddit_posts(self, num_posts=3):
        """Fetch posts from Reddit about the product."""
        print(f"Fetching Reddit posts about {self.product_name}...")
        
        try:
            # Search for posts about the product
            search_results = self.reddit.subreddit('all').search(
                self.product_name,
                limit=num_posts,
                sort='relevance'
            )
            
            posts_data = []
            for post in search_results:
                print(f"\nAnalyzing Reddit post: {post.title}")
                print(f"URL: {post.url}\n")
                
                # Add the main post as one piece of feedback
                if hasattr(post, 'selftext') and post.selftext:
                    posts_data.append({
                        'title': f"Post: {post.title}",
                        'content': post.selftext,
                        'url': post.url,
                        'source': 'reddit_post'
                    })
                
                # Get comments and treat each as separate feedback
                post.comments.replace_more(limit=0)  # Remove MoreComments objects
                for comment in post.comments.list():
                    if hasattr(comment, 'body') and comment.body.strip():
                        posts_data.append({
                            'title': f"Comment on: {post.title}",
                            'content': comment.body,
                            'url': f"{post.url}{comment.id}",
                            'source': 'reddit_comment'
                        })
            
            print(f"\nFound {len(posts_data)} Reddit items to analyze (posts and comments)")
            return posts_data
            
        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
            return []

    def fetch_youtube_comments(self, num_posts=3):
        """Fetch comments from YouTube videos about the product.
        
        Args:
            num_posts: Number of videos to analyze (not the number of comments)
        """
        try:
            # Search for videos about the product
            search_response = self.youtube.search().list(
                q=self.product_name,
                part='id,snippet',
                maxResults=num_posts,  # This limits the number of videos to analyze
                type='video',
                order='relevance'
            ).execute()

            comments = []
            for search_result in search_response.get('items', []):
                if search_result['id'].get('videoId'):
                    video_id = search_result['id']['videoId']
                    video_title = search_result['snippet']['title']
                    print(f"\nAnalyzing YouTube video: {video_title}")
                    print(f"URL: https://www.youtube.com/watch?v={video_id}\n")
                    
                    try:
                        # Get comments for the video
                        comments_response = self.youtube.commentThreads().list(
                            part='snippet',
                            videoId=video_id,
                            maxResults=10,  # Get up to 10 comments per video
                            order='relevance'
                        ).execute()

                        # Extract comments
                        for item in comments_response.get('items', []):
                            comment = item['snippet']['topLevelComment']['snippet']
                            comments.append({
                                'title': video_title,
                                'text': comment['textDisplay'],
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'source': 'youtube'
                            })
                    except HttpError as e:
                        print(f"Error fetching comments for video {video_id}: {e}")
                        continue

            print(f"\nFound {len(comments)} YouTube comments to analyze")
            return comments
        except Exception as e:
            print(f"Error fetching YouTube comments: {e}")
            return []

    def fetch_twitter_posts(self, num_posts=3):
        """Fetch posts from Twitter about the product."""
        try:
            if not self.twitter:
                print("Twitter API access not available. Skipping Twitter posts.")
                return []

            # Search for tweets about the product
            query = f"{self.product_name} -is:retweet lang:en"
            tweets = []
            
            try:
                # Use v2 endpoint for searching tweets
                response = self.twitter.search_recent_tweets(
                    query=query,
                    max_results=num_posts,
                    tweet_fields=['text', 'created_at']
                )
                
                if hasattr(response, 'data'):
                    for tweet in response.data:
                        tweets.append({
                            'title': f"Tweet about {self.product_name}",
                            'content': tweet.text,
                            'url': f"https://twitter.com/i/web/status/{tweet.id}",
                            'source': 'twitter'
                        })
            except Exception as e:
                if '403' in str(e):
                    print("Twitter API access level insufficient. Skipping Twitter posts.")
                else:
                    print(f"Error fetching Twitter posts: {e}")
                return []

            return tweets
        except Exception as e:
            print(f"Error fetching Twitter posts: {e}")
            return []

    def analyze_feedback(self, posts_data):
        """Analyze feedback from posts and comments using OpenAI."""
        print("\nAnalyzing feedback...")
        
        # Initialize feedback matrix
        self.feedback_matrix = {feature: {feedback_type: 0 for feedback_type in self.feedback_types} 
                              for feature in self.feature_categories}
        
        # Track feedback by source
        self.feedback_by_source = {'reddit': 0, 'youtube': 0, 'twitter': 0}
        
        # Initialize feedback details list
        self.feedback_details = []
        
        for post in posts_data:
            print(f"\nAnalyzing {post['source']}: {post['title']}")
            
            # Format comments for analysis
            comments_text = post.get('comments', [])
            if isinstance(comments_text, list):
                comments_text = ' '.join(comments_text)
            
            # Create prompt for OpenAI
            prompt = f"""Analyze the following feedback about {self.product_name} and categorize it by feature and feedback type.
            Focus only on specific, meaningful feedback. Ignore generic or empty responses.
            
            Post/Video Title: {post['title']}
            Content: {post.get('content', '')}
            Comments: {comments_text}
            
            Features to analyze:
            - design: Overall look, aesthetics, and visual appeal
            - camera: Photo and video capabilities, image quality
            - performance: Speed, responsiveness, and processing power
            - battery: Battery life and charging capabilities
            - software features: OS, apps, and software functionality
            - display: Screen quality, size, and display features
            - price: Cost and value proposition
            - audio: Speaker quality, headphone jack, and audio features
            - build quality: Durability, materials, and construction quality
            
            Feedback types: {', '.join(self.feedback_types)}
            
            For each feature mentioned, provide:
            1. The type of feedback (one of the feedback types)
            2. A brief summary of the specific feedback
            
            Only include features where there is actual, specific feedback provided.
            If a feature is mentioned but no specific feedback is given, exclude it from the response.
            
            Example response format:
            {{
                "design": {{
                    "type": "awesome",
                    "summary": "Unique transparent back design stands out"
                }},
                "build quality": {{
                    "type": "poor_compared_to_competitor",
                    "summary": "Back glass scratches easily compared to other phones"
                }},
                "software features": {{
                    "type": "missing_feature",
                    "summary": "Lacks eSIM support in the standard version"
                }}
            }}
            
            Return ONLY valid JSON. Do not include any other text."""
            
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a product feedback analyzer. Provide specific, meaningful feedback analysis in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                feedback = json.loads(response.choices[0].message.content)
                print(f"Feedback: {feedback}")
                
                # Update feedback matrix and source tracking
                for feature, data in feedback.items():
                    if feature in self.feature_categories and data.get('type') in self.feedback_types:
                        # Only update if there's actual feedback content
                        if data.get('summary') and not data['summary'].lower().startswith(('no specific', 'no feedback', 'no mention', 'not provided', 'no comments')):
                            self.feedback_matrix[feature][data['type']] += 1
                            self.feedback_by_source[post['source']] += 1
                            
                            # Store detailed feedback
                            self.feedback_details.append({
                                'title': post['title'],
                                'feature': feature,
                                'feedback_type': data['type'],
                                'summary': data['summary'],
                                'url': post.get('url', ''),
                                'source': post['source']
                            })
                
            except Exception as e:
                print(f"Error analyzing {post['source']}: {post['title']}: {e}")
                continue

    def visualize_feedback_matrix(self) -> None:
        """Visualize the feedback matrix using matplotlib."""
        # Convert dictionary feedback matrix to numpy array for visualization
        matrix_data = np.zeros((len(self.feature_categories), len(self.feedback_types)))
        
        for i, feature in enumerate(self.feature_categories):
            for j, feedback_type in enumerate(self.feedback_types):
                matrix_data[i, j] = self.feedback_matrix[feature][feedback_type]
        
        plt.figure(figsize=(15, 10))
        
        # Create a more informative heatmap
        sns.heatmap(
            matrix_data,
            annot=True,
            fmt='.0f',
            cmap='YlOrRd',
            xticklabels=self.feedback_types,
            yticklabels=self.feature_categories,
            cbar_kws={'label': 'Number of Feedback Items'}
        )
        
        plt.title(f'Feedback Matrix for {self.product_name}', pad=20, fontsize=14)
        plt.xlabel('Feedback Type', labelpad=10)
        plt.ylabel('Feature Category', labelpad=10)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save the visualization
        plt.savefig(f'{self.product_name.replace(" ", "_")}_feedback_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create a summary visualization
        plt.figure(figsize=(12, 6))
        
        # Calculate total feedback per feature
        feature_totals = np.array([sum(self.feedback_matrix[feature].values()) for feature in self.feature_categories])
        total_feedback = feature_totals.sum()
        feature_percentages = (feature_totals / total_feedback * 100) if total_feedback > 0 else np.zeros_like(feature_totals)
        
        # Create a bar chart
        plt.bar(self.feature_categories, feature_percentages)
        plt.title(f'Feedback Distribution by Feature for {self.product_name}', pad=20, fontsize=14)
        plt.xlabel('Feature Category', labelpad=10)
        plt.ylabel('Percentage of Total Feedback', labelpad=10)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save the summary visualization
        plt.savefig(f'{self.product_name.replace(" ", "_")}_feedback_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create a source distribution visualization
        plt.figure(figsize=(10, 6))
        
        # Count feedback by source
        source_totals = {source: count for source, count in self.feedback_by_source.items() if count > 0}
        if source_totals:
            plt.pie(
                source_totals.values(),
                labels=source_totals.keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            plt.title(f'Feedback Distribution by Source for {self.product_name}', pad=20, fontsize=14)
            plt.axis('equal')
            
            # Save the source distribution visualization
            plt.savefig(f'{self.product_name.replace(" ", "_")}_source_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

    def export_feedback_details(self, filename: str = 'complaints.csv') -> None:
        """Export detailed feedback to a CSV file."""
        df = pd.DataFrame(self.feedback_details)
        df.to_csv(filename, index=False)
        print(f"Feedback details exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Analyze product feedback from multiple platforms')
    parser.add_argument('product', help='Name of the product to analyze')
    parser.add_argument('--posts', type=int, default=10, help='Number of items to analyze per platform (default: 10)')
    parser.add_argument('--platforms', nargs='+', default=['reddit', 'youtube', 'twitter'],
                      help='Platforms to analyze (default: reddit youtube twitter)')
    args = parser.parse_args()

    # Initialize analyzer
    analyzer = MultiPlatformFeedbackAnalyzer(args.product)
    
    # Collect data from all specified platforms
    all_posts_data = []
    
    if 'reddit' in args.platforms:
        reddit_posts = analyzer.fetch_reddit_posts(args.posts)
        all_posts_data.extend(reddit_posts)
    
    if 'youtube' in args.platforms and YOUTUBE_API_AVAILABLE:
        youtube_posts = analyzer.fetch_youtube_comments(args.posts)
        all_posts_data.extend(youtube_posts)
    
    if 'twitter' in args.platforms and TWITTER_API_AVAILABLE:
        twitter_posts = analyzer.fetch_twitter_posts(args.posts)
        all_posts_data.extend(twitter_posts)
    
    print(f"Found {len(all_posts_data)} total posts to analyze")
    
    # Analyze feedback
    print("Analyzing feedback...")
    analyzer.analyze_feedback(all_posts_data)
    
    # Visualize results
    print("Visualizing feedback matrix...")
    analyzer.visualize_feedback_matrix()
    
    # Export details
    print("Exporting feedback details...")
    analyzer.export_feedback_details()
    
    print("Analysis complete!")

if __name__ == "__main__":
    main() 