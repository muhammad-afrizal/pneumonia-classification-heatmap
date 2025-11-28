import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pneumonia_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-very-secure-random-string-here')