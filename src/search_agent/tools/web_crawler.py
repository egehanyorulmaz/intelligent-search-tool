from src.search_agent.tools.html_processor import HTMLProcessor

class WebCrawler:
    def __init__(self):
        self.processor = HTMLProcessor()

    def crawl(self, url):
        result = self.processor.crawl_and_process(url)
        if result:
            # You can customize this output based on what information you want to prioritize
            return f"Title: {result['title']}\n\nMain Content: {result['main_content'][:500]}..."
        else:
            return "Failed to crawl the website."