import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key-123')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///college_doc_hub.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OLLAMA_API = 'http://localhost:11434/api/generate'

TEMPLATES = {
    'student': [
        {'id': 'sick_leave', 'name': 'Sick Leave', 'description': 'Professional format'},
        {'id': 'certificate', 'name': 'Certificate', 'description': 'Auto logo + signature'},
        {'id': 'poster', 'name': 'Poster', 'description': 'Auto text overlay'}
    ],
    'admin': [
        {'id': 'sick_leave', 'name': 'Sick Leave', 'description': 'View all'},
        {'id': 'certificate', 'name': 'Certificate', 'description': 'Issue'},
        {'id': 'poster', 'name': 'Poster', 'description': 'Create'}
    ]
}