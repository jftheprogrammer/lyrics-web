import musicbrainzngs
import logging
from typing import List, Dict, Optional

# Initialize MusicBrainz API
musicbrainzngs.set_useragent(
    "SongRecognitionApp",
    "1.0",
    "https://replit.com/@user/song-recognition"  # App identifier
)
musicbrainzngs.set_rate_limit(False)  # Rate limiting is handled by our middleware

def search_song_by_lyrics(lyrics: str, limit: int = 5) -> List[Dict]:
    """
    Search for songs using lyrics and return matches with metadata
    """
    try:
        logging.info(f"Searching MusicBrainz for lyrics: {lyrics[:50]}...")

        # Search for recordings that might match the lyrics
        result = musicbrainzngs.search_recordings(
            query=lyrics,
            limit=limit,
            strict=False
        )

        logging.info(f"Raw MusicBrainz response: {result}")

        if not result or 'recording-list' not in result:
            logging.warning("No recordings found in MusicBrainz response")
            return []

        matches = []
        for recording in result['recording-list']:
            try:
                # Extract streaming URLs if available
                streaming_urls = {}
                if 'url-relation-list' in recording:
                    for url in recording['url-relation-list']:
                        if url['type'] in ['spotify', 'youtube']:
                            streaming_urls[url['type']] = url['target']

                # Get release information
                release_data = None
                if 'release-list' in recording and recording['release-list']:
                    release = recording['release-list'][0]
                    release_data = {
                        'album': release.get('title'),
                        'release_year': release.get('date', '').split('-')[0] if 'date' in release else None,
                        'artwork_url': get_cover_art_url(release['id']) if 'id' in release else None
                    }

                match = {
                    'id': recording.get('id', ''),
                    'title': recording.get('title', 'Unknown Title'),
                    'artist': recording.get('artist-credit-phrase', 'Unknown Artist'),
                    'confidence': 0.8,  # Default confidence score
                    'streaming_urls': streaming_urls
                }

                if release_data:
                    match.update(release_data)

                matches.append(match)
                logging.info(f"Processed match: {match['title']} by {match['artist']}")

            except Exception as e:
                logging.error(f"Error processing recording {recording.get('id', 'unknown')}: {str(e)}")
                continue

        logging.info(f"Found {len(matches)} valid matches")
        return matches

    except Exception as e:
        logging.error(f"Error searching MusicBrainz: {str(e)}")
        return []

def get_cover_art_url(release_id: str) -> Optional[str]:
    """
    Get cover art URL for a release
    """
    try:
        logging.info(f"Fetching cover art for release: {release_id}")
        art = musicbrainzngs.get_image_list(release_id)
        if art and 'images' in art and art['images']:
            return art['images'][0]['thumbnails'].get('large')
    except Exception as e:
        logging.error(f"Error fetching cover art for release {release_id}: {str(e)}")
    return None

def get_song_details(song_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific song
    """
    try:
        logging.info(f"Fetching song details for: {song_id}")
        result = musicbrainzngs.get_recording_by_id(
            song_id, 
            includes=['releases', 'url-rels']
        )

        if not result or 'recording' not in result:
            logging.warning(f"No recording found for ID: {song_id}")
            return None

        recording = result['recording']
        logging.info(f"Raw recording data: {recording}")

        details = {
            'id': recording.get('id', ''),
            'title': recording.get('title', 'Unknown Title'),
            'artist': recording.get('artist-credit-phrase', 'Unknown Artist'),
            'length': recording.get('length'),
            'streaming_urls': {}
        }

        # Get streaming URLs
        if 'url-relation-list' in recording:
            for url in recording['url-relation-list']:
                if url['type'] in ['spotify', 'youtube']:
                    details['streaming_urls'][url['type']] = url['target']

        # Get release information
        if 'release-list' in recording and recording['release-list']:
            release = recording['release-list'][0]
            details.update({
                'album': release.get('title'),
                'release_year': release.get('date', '').split('-')[0] if 'date' in release else None,
                'artwork_url': get_cover_art_url(release['id']) if 'id' in release else None
            })

        logging.info(f"Processed song details: {details}")
        return details

    except Exception as e:
        logging.error(f"Error getting song details from MusicBrainz: {str(e)}")
        return None