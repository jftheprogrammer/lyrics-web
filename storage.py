import json
import os
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash

DATA_FILE = 'data/server.json'

def ensure_data_file():
    """Ensure the data file exists with initial structure"""
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({
                "users": [],
                "songs": [],
                "favorites": [],
                "search_history": []
            }, f, indent=2)

def load_data():
    """Load data from JSON file"""
    ensure_data_file()
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        return {"users": [], "songs": [], "favorites": [], "search_history": []}

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving data: {str(e)}")
        raise

class User:
    @staticmethod
    def get_by_id(user_id):
        data = load_data()
        user = next((u for u in data['users'] if u['id'] == user_id), None)
        return User(**user) if user else None

    @staticmethod
    def get_by_username(username):
        data = load_data()
        user = next((u for u in data['users'] if u['username'] == username), None)
        return User(**user) if user else None

    def __init__(self, id=None, username=None, email=None, password_hash=None, created_at=None, last_login=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.last_login = last_login

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        data = load_data()
        user_dict = {
            'id': self.id or len(data['users']) + 1,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'last_login': self.last_login
        }

        if not self.id:  # New user
            self.id = user_dict['id']
            data['users'].append(user_dict)
        else:  # Update existing user
            for i, user in enumerate(data['users']):
                if user['id'] == self.id:
                    data['users'][i] = user_dict
                    break

        save_data(data)
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)