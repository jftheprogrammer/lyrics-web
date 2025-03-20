import os
import logging
from flask import Flask, render_template, request, jsonify, url_for
from audio_processor import process_audio
from song_matcher import match_lyrics, match_melody
from error_handlers import register_error_handlers
from middleware import init_middleware, apply_rate_limits
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def create_app():
    # Create Flask app with absolute path to static folder
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, 
                static_folder=static_folder,
                template_folder=template_folder)

    app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

    # Initialize extensions
    init_middleware(app)
    register_error_handlers(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/match_lyrics', methods=['POST'])
    def lyrics_matching():
        try:
            lyrics = request.form.get('lyrics', '').strip()
            logging.info(f"Received lyrics: {lyrics}")

            if not lyrics:
                logging.warning("No lyrics provided")
                return jsonify({'error': 'No lyrics provided'}), 400

            if len(lyrics) > 1000:
                logging.warning("Lyrics too long")
                return jsonify({'error': 'Lyrics too long. Maximum 1000 characters allowed.'}), 400

            matches = match_lyrics(lyrics)
            logging.info(f"Found {len(matches)} matches")
            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in lyrics matching: {str(e)}")
            return jsonify({'error': 'An error occurred while processing your request'}), 500

    @app.route('/match_melody', methods=['POST'])
    def melody_matching():
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400

            audio_file = request.files['audio']
            if not audio_file.filename:
                return jsonify({'error': 'No selected file'}), 400

            # Validate file type
            allowed_extensions = {'wav', 'mp3', 'ogg'}
            if not ('.' in audio_file.filename and
                   audio_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                return jsonify({'error': 'Invalid file type. Allowed types: WAV, MP3, OGG'}), 400

            audio_features = process_audio(audio_file)
            matches = match_melody(audio_features)
            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in melody matching: {str(e)}")
            return jsonify({'error': 'An error occurred while processing your request'}), 500

    # Apply rate limits after routes are registered
    apply_rate_limits(app)

    return app