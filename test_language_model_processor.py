import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import re

class SimpleLanguageModelProcessor:
    def __init__(self):
        self.complaints = {}  # Dictionary to store complaints and their counts
        self.complaint_keywords = {
            'performance': ['slow', 'lag', 'freeze', 'crash', 'stutter', 'buggy', 'unstable'],
            'battery': ['drain', 'battery', 'overheat', 'hot', 'temperature'],
            'camera': ['blurry', 'grainy', 'noisy', 'poor', 'camera', 'photo'],
            'build': ['cheap', 'flimsy', 'break', 'crack', 'scratch', 'build'],
            'software': ['bug', 'glitch', 'issue', 'problem', 'update'],
            'features': ['missing', 'lack', 'limited', 'restricted', 'no'],
            'price': ['expensive', 'overpriced', 'cost', 'price'],
            'display': ['screen', 'dim', 'brightness', 'tint', 'display']
        }
        self.comparison_words = ['better', 'worse', 'than', 'compared', 'vs', 'versus', 'over']
        self.product_name = 'nothing phone 3a'

    def _is_about_target_product(self, text: str) -> bool:
        """Check if the comment is specifically about the target product."""
        text_lower = text.lower()
        return self.product_name in text_lower or 'nothing 3a' in text_lower

    def _get_complaint_category(self, text: str) -> str:
        """Determine the main category of a complaint."""
        text_lower = text.lower()
        max_count = 0
        category = 'other'
        
        for cat, keywords in self.complaint_keywords.items():
            count = sum(1 for word in keywords if word in text_lower)
            if count > max_count:
                max_count = count
                category = cat
        
        return category if max_count > 0 else 'other'

    def is_similar_complaint(self, new_complaint: str, existing_complaints: List[str]) -> bool:
        """Check if a new complaint is similar to existing ones using category and keyword matching."""
        new_category = self._get_complaint_category(new_complaint)
        new_words = set(new_complaint.lower().split())
        
        for existing in existing_complaints:
            existing_category = self._get_complaint_category(existing)
            if new_category == existing_category:
                existing_words = set(existing.lower().split())
                common_words = new_words.intersection(existing_words)
                if len(common_words) >= 3:  # At least 3 common words
                    return True
        return False

    def _clean_complaint(self, complaint: str) -> str:
        """Clean and normalize complaint text."""
        # Remove URLs
        complaint = re.sub(r'http\S+|www\S+|https\S+', '', complaint, flags=re.MULTILINE)
        
        # Remove special characters and extra whitespace
        complaint = re.sub(r'[^\w\s.,!?-]', ' ', complaint)
        complaint = ' '.join(complaint.split())
        
        # Remove very short complaints
        if len(complaint.split()) < 3:
            return ""
            
        return complaint.strip()

    def _format_complaint(self, text: str, category: str) -> str:
        """Format the complaint with its category."""
        text = text.strip()
        if not text.endswith(('.', '!', '?')):
            text += '.'
        return f"[{category.upper()}] {text}"

    def process_complaint(self, complaint: str) -> None:
        """Process a new complaint and update the complaints dictionary."""
        if not complaint or len(complaint.strip()) < 10:
            return

        # Clean and normalize the complaint
        cleaned_complaint = self._clean_complaint(complaint)
        if not cleaned_complaint:
            return

        # Skip if not about target product
        if not self._is_about_target_product(cleaned_complaint):
            return

        # Get complaint category
        category = self._get_complaint_category(cleaned_complaint)
        if category == 'other':
            return

        # Format the complaint with category
        formatted_complaint = self._format_complaint(cleaned_complaint, category)

        # Check for similar existing complaints
        for existing_complaint in list(self.complaints.keys()):
            if self.is_similar_complaint(cleaned_complaint, [existing_complaint]):
                self.complaints[existing_complaint] += 1
                return

        # If no similar complaint found, add as new
        self.complaints[formatted_complaint] = 1

    def get_complaints(self) -> List[Tuple[str, int]]:
        """Return the processed complaints and their counts."""
        return sorted(self.complaints.items(), key=lambda x: x[1], reverse=True) 