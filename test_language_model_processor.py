import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import re

class SimpleLanguageModelProcessor:
    def __init__(self):
        load_dotenv()
        self.complaints = {}  # Dictionary to store complaints and their counts
        self.complaint_keywords = [
            'bad', 'terrible', 'awful', 'disappointed', 'issue', 'problem',
            'bug', 'crash', 'broken', 'not working', 'doesn\'t work', 'poor',
            'horrible', 'worst', 'fail', 'faulty', 'defect'
        ]

    def is_similar_complaint(self, new_complaint: str, existing_complaints: List[str]) -> Tuple[bool, str]:
        """
        Check if a new complaint is similar to any existing complaints using keyword matching.
        Returns (is_similar, most_similar_complaint).
        """
        if not existing_complaints:
            return False, ""
        
        # Extract keywords from new complaint
        new_keywords = set(word.lower() for word in new_complaint.split() 
                          if word.lower() in self.complaint_keywords)
        
        if not new_keywords:
            return False, ""
        
        # Compare with existing complaints
        max_common_keywords = 0
        most_similar_complaint = ""
        
        for complaint in existing_complaints:
            # Extract keywords from existing complaint
            existing_keywords = set(word.lower() for word in complaint.split() 
                                  if word.lower() in self.complaint_keywords)
            
            # Count common keywords
            common_keywords = len(new_keywords.intersection(existing_keywords))
            
            if common_keywords > max_common_keywords:
                max_common_keywords = common_keywords
                most_similar_complaint = complaint
        
        # Consider complaints similar if they share at least one keyword
        return max_common_keywords > 0, most_similar_complaint

    def process_complaint(self, complaint_text: str) -> None:
        """
        Process a new complaint and either add it or update existing similar complaint.
        """
        # Clean the complaint text
        cleaned_complaint = self._clean_complaint(complaint_text)
        if not cleaned_complaint:
            return

        # Check if this complaint is similar to any existing ones
        is_similar, similar_complaint = self.is_similar_complaint(
            cleaned_complaint,
            list(self.complaints.keys())
        )

        if is_similar:
            # Update count for similar complaint
            self.complaints[similar_complaint] += 1
        else:
            # Add new complaint
            self.complaints[cleaned_complaint] = 1

    def _clean_complaint(self, text: str) -> str:
        """
        Clean and normalize complaint text.
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        
        # Remove very short complaints
        if len(text.split()) < 3:
            return ''
            
        return text

    def get_complaints(self) -> Dict[str, int]:
        """
        Return the processed complaints and their counts.
        """
        return self.complaints 