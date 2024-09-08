from abc import ABC, abstractmethod

class BaseSearch(ABC):
    @abstractmethod
    def search(self, query: str) -> list[str]:
        pass
