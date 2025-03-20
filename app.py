import os
import logging
from flask import Flask, render_template, request, jsonify
from database import db
from audio_processor import process_audio
from song_matcher import match_lyrics, match_melody
from error_handlers import register_error_handlers
from middleware import init_middleware, apply_rate_limits

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET")

    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///songs.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Configure upload limits
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Initialize extensions
    db.init_app(app)
    init_middleware(app)
    register_error_handlers(app)

    with app.app_context():
        import models
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/match_lyrics', methods=['POST'])
    def lyrics_matching():
        try:
            lyrics = request.form.get('lyrics', '').strip()
            if not lyrics:
                return jsonify({'error': 'No lyrics provided'}), 400
            if len(lyrics) > 1000:
                return jsonify({'error': 'Lyrics too long. Maximum 1000 characters allowed.'}), 400

            matches = match_lyrics(lyrics)
            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in lyrics matching: {str(e)}")
            raise

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
            raise

    # Apply rate limits after routes are registered
    apply_rate_limits(app)

    return app