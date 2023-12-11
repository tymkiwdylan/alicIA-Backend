import aiohttp
from dotenv import dotenv_values
import langchain
from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.requests import RequestsWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.agents.agent_toolkits.openapi import planner
# import json
from pathlib import Path
from pprint import pprint
import yaml
from langchain.chains import LLMMathChain
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.memory import (
  ConversationBufferMemory, 
  ReadOnlySharedMemory, 
  ConversationSummaryMemory, 
  ConversationBufferWindowMemory, 
  ConversationSummaryBufferMemory, 
  ConversationEntityMemory,
  ReadOnlySharedMemory
)
from langchain.chains import ConversationChain
# from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import OpenAI
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema.language_model import BaseLanguageModel
from typing import Any, Callable, Dict, List, Optional
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.agents.agent import AgentExecutor
from langchain.prompts.prompt import PromptTemplate
from langchain.agents import ZeroShotAgent
from langchain.chains.llm import LLMChain
from langchain.agents.agent_toolkits.openapi import planner
from custom_planner import create_openapi_agent
import json

config = dotenv_values(".env")
print(langchain.__version__)


class CalculatorInput(BaseModel):
    question: str = Field()

class ChatBot:
    api_url = ""
    login_access_token = ""

    def __init__(self, email, password):
        self.email =  email
        self.password = password
        with open("openapi.json") as f:
            self.api_data = json.load(f)

    async def login(self):
        login_data = {
            "email": self.email,
            "password": self.password
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url+"/auth/token", data=login_data) as response:
                response_data =  await response.json()
                self.login_access_token = f'Bearer {response_data["access"]}'
                
    def _handle_error(error) -> str:
        return str(error)[:50]

    
    def ask_api_questions(self, question):
        llm = ChatOpenAI(openai_api_key=config.get('OPENAI_API_KEY'), temperature=0.0, model="gpt-4")
        openai_api_spec = reduce_openapi_spec(self.api_data)
        headers = {
            # "Authorization": self.login_access_token,
            "Content-Type": "application/json"
        }
        requests_wrapper = RequestsWrapper(headers=headers)
        
        
        messages = [
            HumanMessage(content="Hey I am mohammed"),
            AIMessage(content="Hey mohammed, how can I help u?"),
        ]
        tools=[]
        llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

        
        tools.append(
            Tool.from_function(
                func=llm_math_chain.run,
                name="Calculator",
                description="useful for when you need to answer questions about math",
                # coroutine= ... <- you can specify an async method if desired as well
            )
        )
        
        def _create_planner_tool(llm, shared_memory):
            
            def _create_planner_agent(question: str):
                agent = create_openapi_agent(
                    openai_api_spec, 
                    requests_wrapper, 
                    llm, 
                    handle_parsing_errors=self._handle_error,
                    shared_memory=shared_memory,
                )
                return agent.run(input=question)
            
            
            return Tool(
                name="api_planner_controller",
                func=_create_planner_agent,
                description="Can be used to execute a plan of API calls and adjust the API call to retrieve the correct data for CompanyX",
            )
        
        prefix = """
            You are an AI assistant developed by xxx.
            
        """
        
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""
        
        
        prompt = ZeroShotAgent.create_prompt(
           tools, 
            prefix=prefix, 
            suffix=suffix, 
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )

        chat_history = ChatMessageHistory(messages=messages)
        window_memory = ConversationSummaryBufferMemory(llm=llm, chat_memory=chat_history, input_key="input", memory_key="chat_history")
        shared_memory = ReadOnlySharedMemory(memory=window_memory)
        tools.append(_create_planner_tool(llm, shared_memory))
        
        llm_chain = LLMChain(llm=llm, prompt=prompt, memory=window_memory)

        agent = ZeroShotAgent(
            llm_chain=llm_chain, 
            tools=tools, 
            verbose=True,     
            handle_parsing_errors="Check your output and make sure it conforms!",
            prompt=prompt
        )
        
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=tools, 
            verbose=True,
            memory=window_memory
        )

        output = agent_executor.run(input=question)

chatbot = ChatBot('ajaaja','jdhnbhs')

chatbot.ask_api_questions('Hello, hows your day')


