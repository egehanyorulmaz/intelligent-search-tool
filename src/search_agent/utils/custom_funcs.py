from src.config import settings

class ContentProcessor:
    def __init__(self):
        self.word_threshold = settings.config.word_threshold

    def truncate_content(self, main_content: str) -> str:
        words = main_content.split()
        total_words = len(words)
        if total_words < self.word_threshold:
            return main_content
        
        if total_words > self.word_threshold:
            start = int(0.2 * total_words)
            end = int(0.6 * total_words)
            truncated_content = ' '.join(words[start:end])
            
            if len(truncated_content.split()) > self.word_threshold:
                truncated_content = ' '.join(words[:self.word_threshold])
            
            return truncated_content
        
        return main_content