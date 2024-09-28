from src.search_agent.tools.base import BaseSearch
import requests
from openai import OpenAI
import logging
from src.config import settings
from src.search_agent.tools.web_crawler import WebCrawler
from src.search_agent.utils.custom_funcs import ContentProcessor

# Initialize logger
logger = logging.getLogger("main.general_web")


class GoogleSearch(BaseSearch, ContentProcessor):
    def __init__(self) -> None:
        super().__init__()
        self._crawler: WebCrawler = WebCrawler()

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

        logger.debug(f"Received {len(search_results)} result from Google Search")
        for idx, result in enumerate(search_results):
            url = result.get("url")
            content = self._crawler.crawl(url=url)
            main_content = content.get("main_content", "")
            truncated_content = self.truncate_content(main_content)
            result["content"] = truncated_content

        return search_results


class PerplexitySearch(BaseSearch):
    def __init__(self):
        self.client = OpenAI(api_key=settings.credentials.perplexity_api_key, 
                             base_url="https://api.perplexity.ai")

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
                model=settings.perplexity.model,
                messages=messages,
            )
            return [response.choices[0].message.content]
        except Exception as e:
            return [f"Error: {str(e)}"]
        