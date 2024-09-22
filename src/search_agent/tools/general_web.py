from src.search_agent.tools.base import BaseSearch
import requests
from openai import OpenAI
import logging
from src.config import settings

# Initialize logger
logger = logging.getLogger("main.general_web")


class GoogleSearch(BaseSearch):
    def search(self, query: str) -> list[dict]:
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": settings.credentials.google_api_key,
            "cx": settings.credentials.google_cse_id,
            "q": query,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()

        search_results = []
        for item in results.get("items", []):
            result = {
                "url": item["link"],
                "title": item["title"],
                "snippet": item["snippet"].replace('\xa0', ' '),
                "thumbnail": item.get("pagemap", {}).get("cse_thumbnail", [{}])[0].get("src")
            }
            search_results.append(result)

        return search_results


class PerplexitySearch(BaseSearch):
    def __init__(self):
        self.client = OpenAI(api_key=settings.credentials.perplexity_api_key, base_url="https://api.perplexity.ai")

    def search(self, query: str) -> list[str]:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant. Provide a detailed and informative response to the user's query."
                ),
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-small-128k-online",
                messages=messages,
            )
            return [response.choices[0].message.content]
        except Exception as e:
            return [f"Error: {str(e)}"]