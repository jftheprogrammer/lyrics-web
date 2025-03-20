from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import SearchHistory, Favorite, Song
from database import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/history')
@login_required
def history():
    searches = SearchHistory.query.filter_by(user_id=current_user.id)\
        .order_by(SearchHistory.timestamp.desc())\
        .limit(50)\
        .all()
    return render_template('user/history.html', searches=searches)

@user_bp.route('/favorites')
@login_required
def favorites():
    favorite_songs = Song.query.join(Favorite)\
        .filter(Favorite.user_id == current_user.id)\
        .order_by(Favorite.added_at.desc())\
        .all()
    return render_template('user/favorites.html', songs=favorite_songs)
