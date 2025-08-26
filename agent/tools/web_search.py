# type: ignore
import os
import requests
from langchain.tools import tool
import json
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

@tool
def web_search(query: str) -> str:
    """Web search using Serper API."""
    try:
        if not SERPER_API_KEY:
            return "WebSearch Error: API key not set."
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query.strip()[:100]})
        headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        result_text = "🔍 Web Results:\n"
        if 'organic' in data and data['organic']:
            for i, res in enumerate(data['organic'][:3], 1):
                result_text += f"{i}. {res.get('title', 'No title')}\n   {res.get('link', 'No link')}\n   {res.get('snippet', 'No snippet')}\n\n"
        return result_text or "No relevant results found."
    except Exception as e:
        return f"WebSearch Error: {str(e)}"