from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from models import Song
import logging

def match_lyrics(query_lyrics):
    """
    Match lyrics using TF-IDF and cosine similarity
    """
    try:
        songs = Song.query.all()
        if not songs:
            return []

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        lyrics_list = [song.lyrics for song in songs if song.lyrics]
        if not lyrics_list:
            return []

        lyrics_list.append(query_lyrics)
        tfidf_matrix = vectorizer.fit_transform(lyrics_list)

        # Calculate similarities
        similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]

        # Get top matches
        matches = []
        for idx, similarity in enumerate(similarities):
            if similarity > 0.1:  # Minimum similarity threshold
                matches.append({
                    'title': songs[idx].title,
                    'artist': songs[idx].artist,
                    'confidence': float(similarity)
                })

        return sorted(matches, key=lambda x: x['confidence'], reverse=True)[:5]
    except Exception as e:
        logging.error(f"Error matching lyrics: {str(e)}")
        raise

def match_melody(query_features):
    """
    Match melody using feature similarity
    """
    try:
        songs = Song.query.all()
        if not songs:
            return []

        matches = []
        query_features = np.array(query_features)

        for song in songs:
            if song.melody_features:
                song_features = np.array(eval(song.melody_features))
                # Dynamic Time Warping could be used here for better matching
                similarity = 1 / (1 + np.mean(np.abs(query_features - song_features)))

                if similarity > 0.6:  # Minimum similarity threshold
                    matches.append({
                        'title': song.title,
                        'artist': song.artist,
                        'confidence': float(similarity)
                    })

        return sorted(matches, key=lambda x: x['confidence'], reverse=True)[:5]
    except Exception as e:
        logging.error(f"Error matching melody: {str(e)}")
        raise