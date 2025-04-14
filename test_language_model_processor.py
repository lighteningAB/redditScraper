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
        
    def _clean_complaint(self, text: str) -> str:
        """Clean and normalize complaint text."""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        
        # Remove very short complaints
        if len(text.split()) < 3:
            return ""
            
        return text.lower()

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

    def _extract_complaint_summary(self, text: str, category: str) -> str:
        """Extract a concise complaint summary from the text."""
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        complaint_sentences = []
        
        # Get keywords for the category
        keywords = self.complaint_keywords.get(category, [])
        
        # Filter out personal story indicators
        personal_indicators = ['i ', 'my ', 'we ', 'our ', 'me ', 'mine ', 'myself ', 'us ', 'our ', 'ours ',
                             'tried', 'switched', 'bought', 'purchased', 'owned', 'using', 'used']
        
        # Complaint indicators
        complaint_indicators = ['bad', 'poor', 'terrible', 'awful', 'horrible', 'disappointing', 'worst', 
                              'issue', 'problem', 'bug', 'glitch', 'fault', 'fail', 'broken', 'doesn\'t work',
                              'does not work', 'not working', 'lack of', 'missing', 'no ', 'without', 'expensive',
                              'slow', 'laggy', 'buggy', 'limited', 'restricted', 'difficult', 'hard', 'annoying']
        
        # Positive indicators (to filter out positive statements)
        positive_indicators = ['good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'perfect',
                             'better', 'best', 'love', 'like', 'enjoy', 'impressed', 'impressive']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence.split()) < 3:
                continue
                
            sentence_lower = sentence.lower()
            
            # Skip sentences with personal pronouns or story indicators
            if any(indicator in sentence_lower for indicator in personal_indicators):
                continue
                
            # Skip positive statements
            if any(indicator in sentence_lower for indicator in positive_indicators):
                continue
                
            # Check if sentence contains relevant keywords and complaint indicators
            has_keyword = any(keyword in sentence_lower for keyword in keywords)
            has_complaint = any(indicator in sentence_lower for indicator in complaint_indicators)
            
            if has_keyword and has_complaint:
                # Clean up the sentence
                cleaned = re.sub(r'\s+', ' ', sentence).strip()
                if len(cleaned.split()) <= 15:  # Only keep reasonably short sentences
                    complaint_sentences.append(cleaned)
        
        if complaint_sentences:
            # Return the shortest complaint that makes sense
            valid_complaints = [c for c in complaint_sentences if len(c.split()) >= 5]
            if valid_complaints:
                return min(valid_complaints, key=len)
        
        # If no good complaints found, return a generic one
        return f"Issues reported with {category} quality and performance."

    def _generate_concise_summary(self, text: str, category: str) -> str:
        """Generate a concise summary of the complaint focusing on key issues."""
        # Extract a focused complaint summary
        summary = self._extract_complaint_summary(text, category)
        
        # Clean up the summary
        summary = summary.strip()
        summary = re.sub(r'\s+', ' ', summary)  # Remove extra whitespace
        
        # Ensure the summary ends with a period
        if not summary.endswith('.'):
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
        cleaned_complaint = self._clean_complaint(complaint)
        if not cleaned_complaint:
            return
            
        # Check if this complaint is similar to any existing ones
        for existing_complaint in list(self.complaints.keys()):
            if self.is_similar_complaint(cleaned_complaint, existing_complaint):
                self.complaints[existing_complaint] += 1
                return
                
        # If no similar complaint found, add as new
        summary = self._summarize_complaint(cleaned_complaint)
        self.complaints[summary] = 1

    def get_complaints(self) -> Dict[str, int]:
        """Return the processed complaints and their counts."""
        return self.complaints 
        return self.complaints 