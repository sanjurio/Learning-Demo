import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-key-change-in-production')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application settings
    APP_NAME = "Erlang Systems Learning Platform"
    APP_DESCRIPTION = "Enterprise Erlang Systems Training and Certification Platform"
    
    # Email domain access control
    DOMAIN_ACCESS = {
        'thbs.com': {
            'access_level': 'full_access',
            'description': 'THBS employees - Full access to video and text content'
        },
        'bt.com': {
            'access_level': 'text_only', 
            'description': 'BT employees - Text content only'
        }
    }