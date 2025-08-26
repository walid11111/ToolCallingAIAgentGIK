import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set.")
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not set.")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "data", "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)