import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import re

class SimpleLanguageModelProcessor:
    def __init__(self):
        self.complaints = {}  # Dictionary to store complaints and their counts
        self.complaint_keywords = {
            'camera': ['camera', 'photo', 'picture', 'sensor', 'lens', 'telephoto', 'periscope', 'ultrawide', 'selfie'],
            'performance': ['processor', 'chip', 'snapdragon', 'dimensity', 'performance', 'speed', 'fast', 'slow', 'lag', 'stutter'],
            'battery': ['battery', 'charge', 'charging', 'power', 'endurance', 'life', 'drain'],
            'storage': ['storage', 'memory', 'ram', 'ufs', 'space', 'gb', 'microsd', 'sd card'],
            'display': ['screen', 'display', 'panel', 'oled', 'amoled', 'brightness', 'refresh rate', 'hz', 'resolution'],
            'design': ['design', 'look', 'ugly', 'beautiful', 'glyph', 'light', 'back', 'camera module', 'build'],
            'price': ['price', 'expensive', 'cheap', 'value', 'cost', 'worth', 'overpriced', 'budget'],
            'software': ['software', 'os', 'android', 'update', 'bug', 'glitch', 'feature', 'ui', 'ux'],
            'hardware': ['button', 'port', 'usb', 'jack', 'speaker', 'microphone', 'fingerprint', 'sensor']
        }
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special characters but keep sentence endings
        text = re.sub(r'[^\w\s.!?]', ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text

    def _get_complaint_category(self, text: str) -> str:
        """Determine the main category of a complaint."""
        text = text.lower()
        category_scores = {}
        
        for category, keywords in self.complaint_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            category_scores[category] = score
            
        if not category_scores:
            return "other"
            
        return max(category_scores.items(), key=lambda x: x[1])[0]

    def _extract_key_sentence(self, text: str) -> str:
        """Extract the most relevant sentence from a longer text."""
        sentences = re.split(r'[.!?]+', text)
        # Remove very short or very long sentences
        valid_sentences = [s.strip() for s in sentences if 5 <= len(s.split()) <= 25]
        if valid_sentences:
            return valid_sentences[0]
        return text.split('.')[0] if text else ""

    def _extract_complaint_summary(self, text: str, category: str) -> str:
        """Extract a concise complaint summary from the text."""
        # Clean the text first
        text = self._clean_text(text)
        
        # Split into sentences and clean each one
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Get keywords for the category
        keywords = self.complaint_keywords.get(category, [])
        
        # Complaint indicators - expanded and more specific
        complaint_indicators = [
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing', 'worst',
            'issue', 'problem', 'bug', 'glitch', 'fault', 'fail', 'broken',
            'doesn\'t work', 'does not work', 'not working', 'lack of', 'missing',
            'no ', 'without', 'expensive', 'slow', 'laggy', 'buggy', 'limited',
            'restricted', 'difficult', 'hard', 'annoying', 'weak', 'short',
            'unreliable', 'inconsistent', 'unstable', 'inadequate', 'insufficient',
            'mediocre', 'overpriced', 'cheap', 'flimsy', 'uncomfortable',
            'worse', 'inferior', 'subpar', 'below average', 'disappointed',
            'frustrated', 'annoyed', 'upset', 'complaint', 'concern', 'worry',
            'not worth', 'waste', 'regret', 'should have', 'would not recommend'
        ]
        
        # Positive indicators to filter out
        positive_indicators = [
            'great', 'good', 'excellent', 'amazing', 'perfect', 'best', 'love',
            'recommend', 'happy', 'satisfied', 'impressed', 'pleased', 'enjoy',
            'worth', 'value', 'solid', 'reliable', 'consistent', 'stable'
        ]
        
        # First, look for direct complaints about features
        feature_complaints = []
        for sentence in sentences:
            if 5 <= len(sentence.split()) <= 25:  # Keep reasonably sized sentences
                sentence_lower = sentence.lower()
                
                # Skip if sentence contains positive indicators
                if any(indicator in sentence_lower for indicator in positive_indicators):
                    continue
                
                # Check for relevant keywords and complaints
                has_keyword = any(keyword in sentence_lower for keyword in keywords)
                has_complaint = any(indicator in sentence_lower for indicator in complaint_indicators)
                
                if has_keyword and has_complaint:
                    feature_complaints.append(sentence)
        
        # If we found direct complaints, return the most concise one
        if feature_complaints:
            return min(feature_complaints, key=len) + '.'
        
        # If no direct complaints, look for feature discussions with negative sentiment
        feature_discussions = []
        for sentence in sentences:
            if 5 <= len(sentence.split()) <= 25:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in keywords):
                    # Check if the sentence has any negative sentiment
                    if any(indicator in sentence_lower for indicator in complaint_indicators):
                        feature_discussions.append(sentence)
        
        if feature_discussions:
            return min(feature_discussions, key=len) + '.'
        
        # If still nothing found, return None to indicate no valid complaint
        return None

    def _generate_concise_summary(self, text: str, category: str) -> str:
        """Generate a concise summary of the complaint focusing on key issues."""
        # Extract a focused complaint summary
        summary = self._extract_complaint_summary(text, category)
        
        # Clean up the summary
        summary = summary.strip()
        summary = re.sub(r'\s+', ' ', summary)  # Remove extra whitespace
        
        # Ensure the summary ends with proper punctuation
        if not any(summary.endswith(p) for p in '.!?'):
            summary += '.'
            
        return summary

    def _summarize_complaint(self, text: str) -> str:
        """Create a brief summary of the complaint."""
        category = self._get_complaint_category(text)
        summary = self._generate_concise_summary(text, category)
        return summary

    def is_similar_complaint(self, new_complaint: str, existing_complaint: str) -> bool:
        """Check if two complaints are similar based on keyword matching."""
        new_complaint = new_complaint.lower()
        existing_complaint = existing_complaint.lower()
        
        # Get categories for both complaints
        new_category = self._get_complaint_category(new_complaint)
        existing_category = self._get_complaint_category(existing_complaint)
        
        # If categories don't match, they're not similar
        if new_category != existing_category:
            return False
            
        # Count matching keywords
        new_keywords = set(self.complaint_keywords[new_category])
        new_words = set(new_complaint.split())
        existing_words = set(existing_complaint.split())
        
        # Check for keyword overlap
        matching_keywords = new_keywords.intersection(new_words).intersection(existing_words)
        
        # If there's significant keyword overlap, consider them similar
        return len(matching_keywords) >= 2

    def process_complaint(self, complaint: str) -> None:
        """Process a new complaint and update the complaints dictionary."""
        cleaned_complaint = self._clean_text(complaint)
        if not cleaned_complaint:
            return
            
        # Get the category and summary
        category = self._get_complaint_category(cleaned_complaint)
        summary = self._extract_complaint_summary(cleaned_complaint, category)
        
        # Only process if we found a valid complaint summary
        if summary:
            # Check if this complaint is similar to any existing ones
            for existing_complaint in list(self.complaints.keys()):
                if self.is_similar_complaint(summary, existing_complaint):
                    self.complaints[existing_complaint] += 1
                    return
                    
            # If no similar complaint found, add as new
            self.complaints[summary] = 1

    def get_complaints(self) -> Dict[str, int]:
        """Return the processed complaints and their counts."""
        return self.complaints 
        return self.complaints 