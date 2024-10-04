import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

class HTMLProcessor:
    def __init__(self):
        self.base_url = None

    def set_base_url(self, url):
        self.base_url = url

    def preprocess_html(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())

        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        text = '\n'.join(chunk for chunk in chunks if chunk)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def extract_links(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            if self.base_url:
                full_url = urljoin(self.base_url, a['href'])
                links.append(full_url)
            else:
                links.append(a['href'])
        return links

    def extract_title(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        title = soup.title.string if soup.title else None
        return title.strip() if title else None

    def extract_main_content(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            return self.preprocess_html(str(main_content))
        else:
            # If no main content area found, return the whole preprocessed HTML
            return self.preprocess_html(html_text)

    def crawl_and_process(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_text = response.text
            self.set_base_url(url)

            processed_text = self.preprocess_html(html_text)
            title = self.extract_title(html_text)
            main_content = self.extract_main_content(html_text)
            links = self.extract_links(html_text)

            return {
                'url': url,
                'title': title,
                'main_content': main_content,
                'full_text': processed_text,
                'links': links
            }
        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")
            return None
