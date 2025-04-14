import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import re
from openai import OpenAI

class SimpleLanguageModelProcessor:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
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
        self.negative_words = [
            'bad', 'poor', 'terrible', 'awful', 'horrible', 'worst', 'disappointing',
            'mediocre', 'subpar', 'inferior', 'inadequate', 'faulty', 'defective',
            'problem', 'issue', 'complaint', 'dislike', 'hate', 'regret'
        ]
        self.comparison_words = ['better', 'worse', 'than', 'compared', 'vs', 'versus', 'over']
        self.product_name = 'nothing phone 3a'

    def _is_negative_feedback(self, text: str) -> bool:
        """Check if the text contains negative sentiment."""
        text_lower = text.lower()
        return any(word in text_lower for word in self.negative_words)

    def _extract_core_issue(self, text: str, category: str) -> str:
        """Extract the core issue from the complaint text."""
        # Get the relevant keywords for the category
        keywords = self.complaint_keywords[category]
        
        # Find sentences containing category keywords
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                # Clean up the sentence
                sentence = sentence.strip()
                # Remove unnecessary context
                sentence = re.sub(r'^(i|my|the|this|that|it|they|we|you|he|she|it)\s+', '', sentence, flags=re.IGNORECASE)
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            # Return the shortest relevant sentence (usually the most focused on the issue)
            return min(relevant_sentences, key=len)
        return text

    def _is_about_target_product(self, text: str) -> bool:
        """Check if the comment is specifically about the target product."""
        text_lower = text.lower()
        return self.product_name in text_lower or 'nothing 3a' in text_lower

    def _get_complaint_summary(self, text: str) -> List[str]:
        """Use OpenAI to generate concise summaries of complaints in the text."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a product complaint analyzer. Extract and summarize negative feedback about products. Each summary should be exactly 10 words or less, focusing on the specific issue. If there are multiple complaints, provide a separate summary for each. Only include actual complaints, not positive feedback."},
                    {"role": "user", "content": f"Analyze this text about {self.product_name} and provide 10-word summaries of any complaints. Text: {text}"}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            # Split the response into individual summaries
            summaries = [s.strip() for s in response.choices[0].message.content.split('\n') if s.strip()]
            return summaries
        except Exception as e:
            print(f"Error getting complaint summary: {str(e)}")
            return []

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

        # Skip if not negative feedback
        if not self._is_negative_feedback(cleaned_complaint):
            return

        # Get summaries from OpenAI
        summaries = self._get_complaint_summary(cleaned_complaint)
        
        # Process each summary
        for summary in summaries:
            if not summary:
                continue
                
            # Get complaint category
            category = self._get_complaint_category(summary)
            if category == 'other':
                continue

            # Format the complaint with category
            formatted_complaint = self._format_complaint(summary, category)

            # Check for similar existing complaints
            for existing_complaint in list(self.complaints.keys()):
                if self.is_similar_complaint(formatted_complaint, [existing_complaint]):
                    self.complaints[existing_complaint] += 1
                    return

            # If no similar complaint found, add as new
            self.complaints[formatted_complaint] = 1

    def get_complaints(self) -> List[Tuple[str, int]]:
        """Return the processed complaints and their counts."""
        return sorted(self.complaints.items(), key=lambda x: x[1], reverse=True) 