import os
import logging
from flask import Flask, render_template, request, jsonify
from database import db
from audio_processor import process_audio
from song_matcher import match_lyrics, match_melody
from error_handlers import register_error_handlers
from middleware import init_middleware, apply_rate_limits
from auth import init_auth
from flask_login import login_required, current_user
from datetime import datetime
from routes.user import user_bp

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
    init_auth(app)
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/user')

    with app.app_context():
        import models
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/match_lyrics', methods=['POST'])
    @login_required
    def lyrics_matching():
        try:
            lyrics = request.form.get('lyrics', '').strip()
            if not lyrics:
                return jsonify({'error': 'No lyrics provided'}), 400
            if len(lyrics) > 1000:
                return jsonify({'error': 'Lyrics too long. Maximum 1000 characters allowed.'}), 400

            matches = match_lyrics(lyrics)

            # Record search history
            if matches:
                search = models.SearchHistory(
                    user_id=current_user.id,
                    song_id=matches[0]['id'] if matches else None,
                    search_type='lyrics',
                    query_text=lyrics,
                    confidence_score=matches[0]['confidence'] if matches else 0,
                    success=bool(matches)
                )
                db.session.add(search)
                db.session.commit()

            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in lyrics matching: {str(e)}")
            raise

    @app.route('/match_melody', methods=['POST'])
    @login_required
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

            # Record search history
            if matches:
                search = models.SearchHistory(
                    user_id=current_user.id,
                    song_id=matches[0]['id'] if matches else None,
                    search_type='melody',
                    query_text=audio_file.filename,
                    confidence_score=matches[0]['confidence'] if matches else 0,
                    success=bool(matches)
                )
                db.session.add(search)
                db.session.commit()

            return jsonify({'matches': matches})
        except Exception as e:
            logging.error(f"Error in melody matching: {str(e)}")
            raise

    @app.route('/favorite/<int:song_id>', methods=['POST'])
    @login_required
    def toggle_favorite(song_id):
        try:
            existing_favorite = models.Favorite.query.filter_by(
                user_id=current_user.id,
                song_id=song_id
            ).first()

            if existing_favorite:
                db.session.delete(existing_favorite)
                is_favorite = False
            else:
                new_favorite = models.Favorite(user_id=current_user.id, song_id=song_id)
                db.session.add(new_favorite)
                is_favorite = True

            db.session.commit()
            return jsonify({'success': True, 'is_favorite': is_favorite})
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error toggling favorite: {str(e)}")
            return jsonify({'error': 'Failed to update favorite status'}), 500

    @app.route('/favorite/status/<int:song_id>')
    @login_required
    def check_favorite_status(song_id):
        try:
            is_favorite = models.Favorite.query.filter_by(
                user_id=current_user.id,
                song_id=song_id
            ).first() is not None
            return jsonify({'is_favorite': is_favorite})
        except Exception as e:
            logging.error(f"Error checking favorite status: {str(e)}")
            return jsonify({'error': 'Failed to check favorite status'}), 500

    # Apply rate limits after routes are registered
    apply_rate_limits(app)

    return app