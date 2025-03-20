from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from storage import load_data

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/history')
@login_required
def history():
    data = load_data()
    searches = [
        search for search in data['search_history']
        if search['user_id'] == current_user.id
    ]
    searches.sort(key=lambda x: x['timestamp'], reverse=True)
    searches = searches[:50]  # Limit to last 50 searches
    return render_template('user/history.html', searches=searches)

@user_bp.route('/favorites')
@login_required
def favorites():
    data = load_data()
    favorite_song_ids = [
        f['song_id'] for f in data['favorites']
        if f['user_id'] == current_user.id
    ]
    favorite_songs = [
        song for song in data['songs']
        if song['id'] in favorite_song_ids
    ]
    favorite_songs.sort(key=lambda x: next(
        f['added_at'] for f in data['favorites']
        if f['user_id'] == current_user.id and f['song_id'] == x['id']
    ), reverse=True)
    return render_template('user/favorites.html', songs=favorite_songs)