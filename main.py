from langchain.schema import HumanMessage
from src.search_agent.workflow.graph import create_workflow
from src.search_agent.utils.custom_logging import setup_logger
from src.search_agent.tools.general_web import GoogleSearch
import logging

logger = setup_logger("main")

web_logger = logging.getLogger("main.general_web")
web_logger.setLevel("DEBUG")

def test_google_search():
    google_search = GoogleSearch()
    results = google_search.search("Who won the last Istanbul derby yesterday? ")
    print(results)

def main():
    logger.info("Starting search agent workflow")
    chain = create_workflow()
    
    while True:
        query = input("Please enter your search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        logger.info(f"Initial query: {query}")
        
        max_retries = 3
        for attempt in range(max_retries):
            result = chain.invoke({
                "messages": [HumanMessage(content=query)],
                "next": "search"
            })
            
            final_answer = result['messages'][-1].content
            if "unable to answer" not in final_answer.lower():
                break
            logger.info(f"Attempt {attempt + 1} failed to provide a satisfactory answer. Retrying...")
        
        logger.info("Workflow completed")
        logger.info(f"Final result: {final_answer}")
        print(f"\nAnswer: {final_answer}\n")
    
    logger.info("Search agent workflow ended")

if __name__ == "__main__":
    test_google_search()