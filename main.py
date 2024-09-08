from src.search_agent.tools.general_web import GoogleSearch, PerplexitySearch
from src.search_agent.agent.agent import create_agent, run_agent
from src.search_agent.utils.custom_logging import setup_logger
from src.config import settings

from langchain.agents import Tool

logger = setup_logger("main")


def main():
    # Initialize search classes
    google_search = GoogleSearch()
    perplexity_search = PerplexitySearch()

    # Define the tools our agent can use
    tools = [
        Tool(
            name="Google Search",
            func=google_search.search,
            description="Useful for when you need to search for general information on the web."
        ),
        Tool(
            name="Perplexity Search",
            func=perplexity_search.search,
            description="Useful for when you need more detailed or analytical information on a topic."
        )
    ]

    # Create the agent
    agent_executor = create_agent(tools)

    # Example query
    query = "Are Alex and Melissa Witkoff art collectors?"

    try:
        result = run_agent(agent_executor, query)
        logger.info(f"Query: {query}")
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
