"""
Configuration settings for the Content Agency AI application.
All API keys and global settings are managed here.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

ACCOUNT_ID = "API_KEY"
CLOUDFLARE_ACCOUNT_ID = "API_KEY"  
CLOUDFLARE_API_TOKEN = "API_KEY"     
GROQ_API_KEY = "API_KEY"  
GROQ_MODEL = "llama-3.3-70b-versatile"  
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Database
DATABASE_PATH = BASE_DIR / "content_agency.db"

# App Settings
APP_NAME = "Content Agency AI"
APP_VERSION = "1.0.0"
DEBUG = True

# Default content settings
DEFAULT_FORMALITY = 0.7
DEFAULT_HUMOR = 0.3

# Industry categories
INDUSTRIES = [
    "Technology", "Fashion", "Healthcare", "Finance", 
    "Education", "Real Estate", "Food & Beverage", 
    "Travel", "Entertainment", "Other"
]

# Social media platforms
PLATFORMS = ["Instagram", "LinkedIn", "Twitter", "Facebook", "Blog", "Newsletter"]