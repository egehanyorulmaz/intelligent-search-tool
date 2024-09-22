from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from src.search_agent.tools.general_web import GoogleSearch, PerplexitySearch
from src.search_agent.tools.web_crawler import WebCrawler
from src.search_agent.utils.custom_logging import setup_logger
from src.search_agent.tools.custom import get_current_date, calculate_date_interval
from datetime import datetime, timedelta

logger = setup_logger("workflow.agents")

google_search = GoogleSearch()
perplexity_search = PerplexitySearch()
web_crawler = WebCrawler()

def router_agent(state):
    logger.info("Entering search_agent")
    messages = state['messages']
    user_query = messages[0].content



def search_agent(state):
    """
    Perform a search based on the user's query.

    This function processes the user's query, generates a search query, and performs searches using Google and Perplexity.

    :param state: A dictionary containing the current state of the conversation.
    :type state: dict
    :return: A dictionary with updated messages and the next action.
    :rtype: dict

    The function does the following:
    1. Extracts the user query from the state.
    2. Adds date context to the query if it's about recent events.
    3. Generates a specific search query using an AI model.
    4. Performs searches using Google and Perplexity.
    5. Combines and returns the search results.
    """
    logger.info("Entering search_agent")
    messages = state['messages']
    user_query = messages[-1].content

    # Get current date
    current_date = get_current_date()["current_date"]
    
    # Check if the query is about a recent event
    if "recent" in user_query.lower() or "latest" in user_query.lower() or "today" in user_query.lower():
        user_query += f" as of {current_date}"
    
    # Check if the query is about something that happened in the last X days
    if "last" in user_query.lower() and "days" in user_query.lower():
        try:
            days = int(''.join(filter(str.isdigit, user_query.split("last")[1].split("days")[0])))
            start_date = (datetime.fromisoformat(current_date) - timedelta(days=days)).isoformat()
            interval = calculate_date_interval(start_date, current_date)["interval_days"]
            user_query += f" between {start_date} and {current_date}"
        except ValueError:
            logger.warning("Could not parse the number of days from the query")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a search agent. Generate a specific and relevant search query based on the user's question. Focus on the key entities and their relationships."),
        ("human", "Generate a search query for the following question: {input}")
    ])
    
    chain = prompt | ChatOpenAI(temperature=0)
    search_query = chain.invoke({"input": user_query})
    
    logger.info(f"Generated search query: {search_query.content}")
    google_response = google_search.search(search_query.content)
    perplexity_response = perplexity_search.search(user_query)
    
    logger.info(f"Google search response: {str(google_response)[:500]}...")  # Log first 500 characters
    logger.info(f"Perplexity search response: {str(perplexity_response)[:500]}...")  # Log first 500 characters
    
    combined_response = {
        "google_results": google_response,
        "perplexity_results": perplexity_response
    }
    
    return {
        "messages": [*messages, AIMessage(content=str(combined_response))],
        "next": "analyze"
    }

def analyze_agent(state):
    """
    Analyze the search results and determine the next action.

    This function examines the search results, assesses their relevance to the original query,
    and decides whether to perform a new search, crawl a specific website, or proceed to summarization.

    :param state: A dictionary containing the current state of the conversation.
    :type state: dict
    :return: A dictionary with updated messages and the next action.
    :rtype: dict

    The function does the following:
    1. Extracts the original query and search results from the state.
    2. Uses an AI model to analyze the relevance of the search results.
    3. Based on the analysis, decides to either:
       - Perform a new search with refined keywords
       - Crawl a specific website for more information
       - Proceed to summarize the information
    """
    logger.info("Entering analyze_agent")
    messages = state['messages']
    original_query = messages[0].content
    search_result = messages[-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an analysis agent. Examine the search results and determine their relevance to the original query. If the results are not relevant, request a new search with refined keywords. If relevant, decide if we need to crawl a specific website for more information."),
        ("human", "Original query: {original_query}\nSearch results: {search_result}\n\nAre the results relevant? If not, provide refined search keywords. If relevant, do we need to crawl a specific website? If yes, provide the URL.")
    ])
    
    chain = prompt | ChatOpenAI(temperature=0)
    
    logger.info(f"Analyzing search results for query: {original_query}")
    response = chain.invoke({"original_query": original_query, "search_result": search_result})
    logger.info(f"Analysis response: {response.content}")
    
    if "not relevant" in response.content.lower():
        logger.info("Decision: Perform new search")
        return {
            "messages": [*messages, AIMessage(content=str(response))],
            "next": "search"
        }
    elif "http" in response.content:
        logger.info("Decision: Crawl website")
        return {
            "messages": [*messages, AIMessage(content=str(response))],
            "next": "crawl"
        }
    else:
        logger.info("Decision: Proceed to summarize")
        return {
            "messages": [*messages, AIMessage(content=str(response))],
            "next": "summarize"
        }

def crawl_agent(state):
    """
    Crawl a specific website for more information.

    This function extracts a URL from the previous message and uses a web crawler to fetch
    additional information from that website.

    :param state: A dictionary containing the current state of the conversation.
    :type state: dict
    :return: A dictionary with updated messages and the next action.
    :rtype: dict
ı
    The function does the following:
    1. Extracts the URL to crawl from the previous message.
    2. Uses a web crawler to fetch information from the URL.
    3. If successful, adds the crawled information to the messages and proceeds to summarization.
    4. If unsuccessful, logs the error and returns to the analyze agent for the next action.
    """
    logger.info("Entering crawl_agent")
    messages = state['messages']
    url = messages[-1].content.split("http", 1)[-1].split()[0]
    url = "http" + url
    
    logger.info(f"Crawling URL: {url}")
    try:
        result = web_crawler.crawl(url)
        logger.info(f"Crawl result: {result[:500]}...")  # Log first 500 characters
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
        return {
            "messages": [*messages, AIMessage(content=f"Failed to crawl {url}. Error: {str(e)}")],
            "next": "analyze"  # Return to analyze agent to decide next action
        }
    
    return {
        "messages": [*messages, AIMessage(content=str(result))],
        "next": "summarize"
    }

def summarize_agent(state):
    logger.info("Entering summarize_agent")
    messages = state['messages']
    original_query = messages[0].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a summarization agent. Provide a concise summary of the information gathered, focusing on answering the original query. If the information is insufficient or irrelevant, state so clearly."),
        ("human", "Original query: {original_query}\nInformation: {info}\n\nProvide a summary that answers the original query. If unable to answer, explain why.")
    ])
    
    chain = prompt | ChatOpenAI(temperature=0)
    
    info = "\n".join([m.content for m in messages[1:]])
    logger.info(f"Summarizing information for query: {original_query}")
    response = chain.invoke({"original_query": original_query, "info": info})
    logger.info(f"Summary: {response.content}")
    
    return {
        "messages": [*messages, AIMessage(content=str(response))],
        "next": "end"
    }