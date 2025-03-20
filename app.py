import os
import logging
from flask import Flask, render_template, request, jsonify
from database import db
from audio_processor import process_audio
from song_matcher import match_lyrics, match_melody

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET")

    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///songs.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)

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

            matches = match_lyrics(lyrics)
            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in lyrics matching: {str(e)}")
            return jsonify({'error': 'Failed to process lyrics'}), 500

    @app.route('/match_melody', methods=['POST'])
    def melody_matching():
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400

            audio_file = request.files['audio']
            audio_features = process_audio(audio_file)
            matches = match_melody(audio_features)
            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in melody matching: {str(e)}")
            return jsonify({'error': 'Failed to process audio'}), 500

    return app