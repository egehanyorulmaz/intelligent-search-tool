from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage
from src.search_agent.workflow.agents import search_agent, analyze_agent, crawl_agent, summarize_agent

class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation so far"]
    next: str

def create_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("search", search_agent)
    workflow.add_node("analyze", analyze_agent)
    workflow.add_node("crawl", crawl_agent)
    workflow.add_node("summarize", summarize_agent)

    workflow.set_entry_point("search")

    workflow.add_edge("search", "analyze")
    workflow.add_conditional_edges(
        "analyze",
        lambda x: x["next"],
        {
            "search": "search",
            "crawl": "crawl",
            "summarize": "summarize"
        }
    )
    workflow.add_conditional_edges(
        "crawl",
        lambda x: x["next"],
        {
            "analyze": "analyze",
            "summarize": "summarize"
        }
    )
    workflow.add_edge("summarize", END)

    return workflow.compile()