# utils/env_loader.py

import os

def load_env():
    """Завантажує змінні середовища з файлу .env"""
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
