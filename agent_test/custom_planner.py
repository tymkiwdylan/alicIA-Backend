from langchain.agents import ZeroShotAgent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents.agent_toolkits.openapi.planner import (
    _create_api_planner_tool,
    _create_api_controller_tool,
)
from langchain.agents.agent_toolkits.openapi.spec import ReducedOpenAPISpec
from langchain.schema.language_model import BaseLanguageModel
from langchain.memory import ReadOnlySharedMemory
from langchain.requests import RequestsWrapper
from langchain.agents import AgentExecutor
from langchain.callbacks.base import BaseCallbackManager
from typing import Optional, Any, Dict, List

API_ORCHESTRATOR_PROMPT = """
You are an AI assistant that makes plans to call APIs. You are given a goal, a list of available API actions, and any initial context. Determine an optimal sequence of API calls to accomplish the goal. 

The available API actions are:

{tool_descriptions}

Initial context:
{chat_history}  

Goal: {input}

Plan:
"""

def create_openapi_agent(
    api_spec: ReducedOpenAPISpec,
    requests_wrapper: RequestsWrapper,
    llm: BaseLanguageModel,
    shared_memory: Optional[ReadOnlySharedMemory] = None,
    memory: Optional[Any] = None,
    callback_manager: Optional[BaseCallbackManager] = None,
    verbose: bool = True,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    tools: Optional[List] = [],
    **kwargs: Dict[str, Any],
) -> AgentExecutor:

    tools = [
        _create_api_planner_tool(api_spec, llm),
        _create_api_controller_tool(api_spec, requests_wrapper, llm),
        *tools,
    ]

    prompt = PromptTemplate(
        template=API_ORCHESTRATOR_PROMPT,
        input_variables=["input", "chat_history", "agent_scratchpad"],
        partial_variables={
            "tool_names": ", ".join([tool.name for tool in tools]),
            "tool_descriptions": "\n".join(
                [f"{tool.name}: {tool.description}" for tool in tools]
            ),
        },
    )

    agent = ZeroShotAgent(
        llm_chain=LLMChain(llm=llm, prompt=prompt, memory=memory),
        allowed_tools=[tool.name for tool in tools],
        **kwargs,
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        memory=memory,
        **(agent_executor_kwargs or {}),
    )
