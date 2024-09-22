from src.search_agent.tools.html_processor import HTMLProcessor
import logging

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):
        self.processor = HTMLProcessor()
    
    def crawl(self, url: str) -> dict:
        result = self.processor.crawl_and_process(url)
        if result:
            return result
        else:
            logger.error(f"Failed to crawl the website: {url}")
            return {}