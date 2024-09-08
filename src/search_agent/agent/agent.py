from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from src.search_agent.agent.custom_prompt import get_prompt
from src.search_agent.agent.custom_output_parser import CustomOutputParser
from src.config import settings


def create_agent(tools):
    llm = OpenAI(temperature=settings.agent_temperature)
    prompt = get_prompt(tools)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]

    output_parser = CustomOutputParser()

    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)


def run_agent(agent_executor, query: str) -> str:
    return agent_executor.run(query)