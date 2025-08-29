from langchain.tools import tool
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

@tool
def web_search(query: str) -> str:
    """
    Performs a web search using the Tavily API to find information on a given query.

    Args:
        query: The search query.

    Returns:
        A JSON string containing the search results, including source names and URLs.
    """
    # Ensure the Tavily API key is set

    results = requests.get(f'http://searxn.runflare.run/search?q={query}&format=json&pageno=1').json()
    
    # Format results to a more readable string if needed,
    # or return the structured list of documents directly.
    return str(results)
