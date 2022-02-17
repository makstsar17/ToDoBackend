"""Flask configuration"""

from datetime import timedelta

SECRET_KEY = '33e0bac4b8ba96d1aa1b418d98d1f96603121855caea4780adecf3842356f2ff'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/WEB'
SQLALCHEMY_TRACK_MODIFICATIONS = True
JWT_SECRET_KEY = '4ae635d496d638ffcb1b0e3de587e733f5f58189a3a7be365590a62539646ad5'
# JWT_COOKIE_SECURE = False #set True in Production
# JWT_TOKEN_LOCATION = ['cookies']
# JWT_COOKIE_CSRF_PROTECT = True
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=10)
UPLOAD_FOLDER = 'client_files'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}
