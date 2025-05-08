"""Configuration settings for folktale generator."""

# Application settings
APP_NAME = "Han Dynasty Folktale Generator"
VERSION = "1.0.0"

# Path settings
DATA_DIR = "./data"
STORIES_DIR = "./stories"
CACHE_DIR = "./cache"

# Generation settings
DEFAULT_LANGUAGE = "en"  # "en", "zh", or "both"
MAX_TURNS = 12
MIN_TURNS = 7

# API settings
API_HOST = "0.0.0.0"
API_PORT = 5555
API_DEBUG = True

# Model settings
MODEL_NAME = "deepseek-chat"  # or "gpt-4" for OpenAI
DEFAULT_TEMPERATURE = 0.8
MAX_TOKENS = 500