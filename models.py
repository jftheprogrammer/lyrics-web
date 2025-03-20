from database import db
from flask_login import UserMixin
from datetime import datetime
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    release_year = db.Column(db.Integer)
    lyrics = db.Column(db.Text, nullable=True)
    melody_features = db.Column(db.Text, nullable=True)  # JSON string of melody features
    artwork_url = db.Column(db.String(500))  # URL to album artwork
    streaming_urls = db.Column(db.Text)  # JSON string of streaming platform URLs

    # Relationships
    favorites = db.relationship('Favorite', backref='song', lazy='dynamic')
    search_matches = db.relationship('SearchHistory', backref='matched_song', lazy='dynamic')

    def set_streaming_urls(self, urls_dict):
        self.streaming_urls = json.dumps(urls_dict)

    def get_streaming_urls(self):
        return json.loads(self.streaming_urls) if self.streaming_urls else {}

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'))
    search_type = db.Column(db.String(20))  # 'lyrics' or 'melody'
    query_text = db.Column(db.Text)  # Store lyrics or audio file path
    confidence_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'song_id', name='unique_user_song_favorite'),
    )