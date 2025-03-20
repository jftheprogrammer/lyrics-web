from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from services.musicbrainz_service import search_song_by_lyrics

def match_lyrics(query_lyrics: str) -> list:
    """
    Match lyrics using MusicBrainz and enhance with TF-IDF similarity
    """
    try:
        # Get matches from MusicBrainz
        matches = search_song_by_lyrics(query_lyrics)
        if not matches:
            return []

        # Calculate TF-IDF similarity for better confidence scores
        vectorizer = TfidfVectorizer()
        lyrics_list = [query_lyrics] + [match['title'] for match in matches]  # Using titles for similarity
        tfidf_matrix = vectorizer.fit_transform(lyrics_list)

        # Calculate similarities between query and each match
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        # Update confidence scores
        for idx, match in enumerate(matches):
            match['confidence'] = float(similarities[idx])

        # Sort by confidence and return top matches
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:5]

    except Exception as e:
        logging.error(f"Error matching lyrics: {str(e)}")
        return []

def match_melody(query_features: list) -> list:
    """
    Match melody using audio features
    Note: This is a placeholder for future melody matching implementation
    """
    try:
        # For now, return an empty list as melody matching requires additional setup
        return []
    except Exception as e:
        logging.error(f"Error matching melody: {str(e)}")
        return []