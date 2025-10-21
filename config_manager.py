import os
import json
from pathlib import Path

CONFIG_FILE = 'library_config.json'
DEFAULT_CONFIG = {
    'books_folder': os.path.join(os.path.dirname(__file__), 'bundle test')
}

def load_config():
    """Load configuration from file or create default"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if not os.path.exists(config.get('books_folder', '')):
                    config['books_folder'] = DEFAULT_CONFIG['books_folder']
                return config
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_books_folder():
    """Get the current books folder from config"""
    config = load_config()
    return config.get('books_folder', DEFAULT_CONFIG['books_folder'])

def set_books_folder(folder_path):
    """Update the books folder in config"""
    config = load_config()
    config['books_folder'] = folder_path
    return save_config(config)