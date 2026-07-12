"""
Flask Configuration
"""
import os
from datetime import timedelta

class Config:
    """Base Configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hostel_meals.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-change-in-production'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_REFRESH_EACH_REQUEST = True
    
class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing Configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
