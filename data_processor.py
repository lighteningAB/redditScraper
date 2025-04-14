import pandas as pd
from typing import List, Dict
from language_model_processor import LanguageModelProcessor

class DataProcessor:
    def __init__(self):
        self.lm_processor = LanguageModelProcessor()

    def extract_complaints(self, posts_data: List[Dict]) -> Dict[str, int]:
        """
        Extract and process complaints from posts and comments using language model.
        Returns a dictionary with complaint summaries and their counts.
        """
        # Process all text from posts and comments
        for post in posts_data:
            # Process post title and text
            if post['title']:
                self.lm_processor.process_complaint(post['title'])
            if post['text']:
                self.lm_processor.process_complaint(post['text'])
            
            # Process comments
            for comment in post['comments']:
                if comment['text']:
                    self.lm_processor.process_complaint(comment['text'])
        
        return self.lm_processor.get_complaints()

    def save_to_csv(self, complaints: Dict[str, int], filename: str = 'nothing_phone_complaints.csv'):
        """
        Save complaints data to a CSV file.
        """
        df = pd.DataFrame({
            'Complaint Summary': list(complaints.keys()),
            'Count': list(complaints.values())
        })
        
        # Sort by count in descending order
        df = df.sort_values('Count', ascending=False)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"Complaints data saved to {filename}") 