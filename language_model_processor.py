import os
from typing import List, Dict, Tuple
import openai
from dotenv import load_dotenv
import numpy as np
import re

class LanguageModelProcessor:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI()
        self.complaints = {}  # Dictionary to store complaints and their counts
        self.embeddings = {}  # Dictionary to store embeddings for each complaint
        self.similarity_threshold = 0.85  # Threshold for considering complaints similar

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text using OpenAI's API.
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def is_similar_complaint(self, new_complaint: str, existing_complaints: List[str]) -> Tuple[bool, str]:
        """
        Check if a new complaint is similar to any existing complaints.
        Returns (is_similar, most_similar_complaint).
        """
        if not existing_complaints:
            return False, ""

        # Get embedding for new complaint
        new_embedding = self.get_embedding(new_complaint)
        
        # Compare with existing complaints
        max_similarity = -1
        most_similar_complaint = ""
        
        for complaint in existing_complaints:
            if complaint not in self.embeddings:
                self.embeddings[complaint] = self.get_embedding(complaint)
            
            similarity = self.cosine_similarity(new_embedding, self.embeddings[complaint])
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_complaint = complaint
        
        return max_similarity >= self.similarity_threshold, most_similar_complaint

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
            self.embeddings[cleaned_complaint] = self.get_embedding(cleaned_complaint)

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