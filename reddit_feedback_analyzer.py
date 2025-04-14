import os
import praw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, List
from dotenv import load_dotenv
from openai import OpenAI
import argparse
import json

class RedditFeedbackAnalyzer:
    def __init__(self, product_name: str):
        """Initialize the analyzer with product name and API clients."""
        load_dotenv()
        self.product_name = product_name
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        self.openai_client = OpenAI()  # It will automatically use OPENAI_API_KEY from environment
        
        # Define feedback categories
        self.feature_categories = [
            "design", "camera", "performance", "battery", 
            "software", "display", "price", "audio"
        ]
        
        self.feedback_types = [
            "missing_feature",
            "unuseful_feature",
            "worse_than_competitor",
            "very_good_feature",
            "better_than_competitor",
            "neutral"
        ]
        
        # Initialize feedback matrix
        self.feedback_matrix = np.zeros((len(self.feature_categories), len(self.feedback_types)))
        self.feedback_details = []

    def fetch_reddit_posts(self, limit: int = 10) -> List[Dict]:
        """Fetch posts and comments from Reddit about the product."""
        print(f"Fetching posts about {self.product_name}...")
        posts_data = []
        subreddits = ["Smartphones", "Android", "NothingTech"]
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                search_results = subreddit.search(self.product_name, limit=limit, sort='relevance')
                
                for post in search_results:
                    print(f"\nAnalyzing post: {post.title}")
                    print(f"URL: {post.url}\n")
                    
                    # Get comments
                    post.comments.replace_more(limit=0)
                    comments = [comment.body for comment in post.comments.list() if hasattr(comment, 'body')]
                    
                    posts_data.append({
                        'title': post.title,
                        'url': post.url,
                        'content': post.selftext if hasattr(post, 'selftext') else '',
                        'comments': comments
                    })
            except Exception as e:
                print(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
                continue
        
        print(f"\nFound {len(posts_data)} posts to analyze")
        return posts_data

    def analyze_feedback(self, posts_data: List[Dict]):
        """Analyze the feedback from posts and update the feedback matrix."""
        print("Analyzing feedback...")
        
        for post in posts_data:
            prompt = f"""
            Analyze this post about {self.product_name}:
            Title: {post['title']}
            Content: {post['content']}
            Comments: {', '.join(post['comments'])}
            
            For each feature category mentioned (design, camera, performance, battery, software, display, price, audio),
            classify the feedback type as one of:
            - missing_feature
            - unuseful_feature
            - worse_than_competitor
            - very_good_feature
            - better_than_competitor
            - neutral
            
            Also provide a brief summary (max 100 characters) of the feedback for each feature.
            
            Format: Return a JSON object with feature categories as keys and objects as values.
            Each object should have 'type' and 'summary' fields.
            Only include features that are explicitly mentioned.
            Example response format:
            {{
                "camera": {{
                    "type": "very_good_feature",
                    "summary": "Excellent low-light performance and color accuracy"
                }},
                "battery": {{
                    "type": "worse_than_competitor",
                    "summary": "Battery life shorter than Samsung Galaxy S24"
                }}
            }}
            """
            
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a product feedback analyzer. Analyze the given text and return feedback in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    response_format={"type": "json_object"}
                )
                
                feedback = json.loads(response.choices[0].message.content)
                print(f"\nAnalyzing post: {post['title']}")
                print(f"Feedback: {feedback}")
                
                # Update feedback matrix
                for feature, feedback_data in feedback.items():
                    if feature in self.feature_categories and feedback_data['type'] in self.feedback_types:
                        feature_idx = self.feature_categories.index(feature)
                        feedback_type_idx = self.feedback_types.index(feedback_data['type'])
                        self.feedback_matrix[feature_idx, feedback_type_idx] += 1
                        
                        # Store detailed feedback with summary
                        self.feedback_details.append({
                            'title': post['title'],
                            'feature': feature,
                            'feedback_type': feedback_data['type'],
                            'summary': feedback_data['summary'],
                            'url': post['url']
                        })
                        
            except Exception as e:
                print(f"Error analyzing post {post['title']}: {str(e)}")
                continue

    def visualize_feedback_matrix(self) -> None:
        """Visualize the feedback matrix using matplotlib."""
        plt.figure(figsize=(15, 10))
        
        # Create a more informative heatmap
        sns.heatmap(
            self.feedback_matrix,
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
        feature_totals = np.sum(self.feedback_matrix, axis=1)
        feature_percentages = feature_totals / np.sum(feature_totals) * 100
        
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

    def export_feedback_details(self, filename: str = 'complaints.csv') -> None:
        """Export detailed feedback to a CSV file."""
        df = pd.DataFrame(self.feedback_details)
        df.to_csv(filename, index=False)
        print(f"Feedback details exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Reddit feedback about a product')
    parser.add_argument('product', help='Product to search for')
    parser.add_argument('--posts', type=int, default=10, help='Number of posts to analyze')
    args = parser.parse_args()

    # Initialize analyzer
    analyzer = RedditFeedbackAnalyzer(args.product)
    
    # Fetch posts
    print(f"Fetching posts about {args.product}...")
    posts_data = analyzer.fetch_reddit_posts(args.posts)
    print(f"Found {len(posts_data)} posts to analyze")
    
    # Analyze feedback
    print("Analyzing feedback...")
    analyzer.analyze_feedback(posts_data)
    
    # Visualize results
    print("Visualizing feedback matrix...")
    analyzer.visualize_feedback_matrix()
    
    # Export details
    print("Exporting feedback details...")
    analyzer.export_feedback_details()
    
    print("Analysis complete!")

if __name__ == "__main__":
    main() 