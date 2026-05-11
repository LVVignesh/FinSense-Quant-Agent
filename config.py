import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# App Settings
MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() == "true"
DEFAULT_MODEL = "llama-3.3-70b-versatile"  # Updated to newest Groq model
FALLBACK_MODEL = "mixtral-8x7b-32768"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CHROMA_DB_PATH = os.path.join(BASE_DIR, "memory", "chroma_db")

# Institutional Risk Limits
MAX_NOTIONAL_VALUE = 150000
MAX_PORTFOLIO_VAR = 0.05
