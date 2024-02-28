from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import chainlit as cl
from langchain.agents import create_openapi_agent
from langchain.chains.openai_functions.openapi import get_openapi_chain
from langchain.agents.agent_toolkits import OpenAPIToolkit
from langchain.requests import TextRequestsWrapper
from langchain.tools.json.tool import JsonSpec
import json

template = """Question: {question}

Answer: Let's think step by step.

Output: Always rewrite the output so it looks nice

"""

@cl.on_chat_start
def main():

    openai_llm = OpenAI(openai_api_key='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', temperature=.7)

    with open("openapi.json") as f:
        openapi_spec = json.load(f)

    json_spec = JsonSpec(dict_ = openapi_spec)

    requests_wrapper = TextRequestsWrapper()

    openapi_toolkit = OpenAPIToolkit.from_llm(
        openai_llm, json_spec, requests_wrapper, verbose=True
    )
    openapi_agent_executor = create_openapi_agent(
        llm=openai_llm, toolkit=openapi_toolkit, verbose=True
    )



    # Store the chain in the user session
    cl.user_session.set("llm_chain", openapi_agent_executor)


@cl.on_message
async def main(message: cl.Message):
    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("llm_chain")  # type: LLMChain

    # Call the chain synchronously in a different thread
    res = await cl.make_async(llm_chain)(
        message.content, callbacks=[cl.LangchainCallbackHandler()]
    )

    # Do any post processing here

    # "res" is a Dict. For this chain, we get the response by reading the "text" key.
    # This varies from chain to chain, you should check which key to read.
    await cl.Message(content=res['output']).send()
    return llm_chain
