import openai
import requests
import json
from typing import List, Dict
import uuid
from .plugins.plugin import PluginInterface
import importlib
import os
import pkgutil

PLUGIN_PATH = os.path.join(os.path.dirname(__file__), 'plugins')

GPT_MODEL = "gpt-3.5-turbo-16k-0613"
SYSTEM_PROMPT = """
You are a helpful AI stock management assistant for CompanyX. You answer user queries related
to stock and the products the company, you take the help of functions provided to you.
With the help of said functions, you can:
1. Get all items from the company 
2. Update the items (oid needed)
3. Delete items (oid needed)
4. Add/update/delete locations (oid needed for updating and deleting)
5. add/update/delete batches of an item given its id (oid needed for updating and deleting)
6. Add/update/delete suppliers (oid needed for updating and deleting)
7. Get/update stock levels of an item given its id 
8. Log and get stock movements
Remember that you are the best stock manager in the world. This means that 
you should always log movements when an item is added/sold/updated/etc. 
You are also very cautios, so you will always ask for confirmation before making
any kind of changes or deleting something. When in doubt, always ask what approach you should take.
DO NOT MAKE DATA UP. If you are missing some information, you can either ask for it
or use functions to find that data. And be extra cautios with IDs.
"""
openai.api_key = "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"

class Conversation:
    """
    This class represents a conversation with the ChatGPT model.
    It stores the conversation history in the form of a list of messages.
    """
    def __init__(self):
        self.conversation_history: List[Dict] = []

    def add_message(self, role, content):
        message = {"role": role, "content": content}
        self.conversation_history.append(message)
    

class ChatSession:
    """
    Represents a chat session.
    Each session has a unique id to associate it with the user.
    It holds the conversation history
    and provides functionality to get new response from ChatGPT
    for user query.
    """    
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.conversation = Conversation()
        self.plugins: Dict[str, PluginInterface] = {}
       
        plugin_classes = self.get_all_plugin_classes()
        plugins = [cls() for cls in plugin_classes]
        
        for plugin in plugins:
            self.register_plugin(plugin)

        # self.register_plugin(WebSearchPlugin())
        # self.register_plugin(WebScraperPlugin())
        # self.register_plugin(PythonInterpreterPlugin())
        # self.register_plugin(GetItemsPlugin())
        # self.register_plugin(AddItemPlugin())
        # self.register_plugin(UpdateItemPlugin())
        # self.register_plugin(ItemSearchPlugin())
        self.conversation.add_message("system", SYSTEM_PROMPT)
        
    def get_all_plugin_classes(self):
    # Create a list to hold all plugin classes
        all_plugin_classes = []

        # Loop over each module in the 'plugins' package
        for (_, module_name, _) in pkgutil.iter_modules([PLUGIN_PATH]):
            # Import the module
            module = importlib.import_module(f'.plugins.{module_name}', __package__)

            # Find classes that are subclass of PluginInterface but not PluginInterface itself
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                    all_plugin_classes.append(attr)

        return all_plugin_classes
    
    def register_plugin(self, plugin: PluginInterface):
        """
        Register a plugin for use in this session
        """
        self.plugins[plugin.get_name()] = plugin
    
    def get_messages(self) -> List[Dict]:
        """
        Return the list of messages from the current conversaion
        """
        if len(self.conversation.conversation_history) == 1:
            return []
        return self.conversation.conversation_history[1:]
    
    def _get_functions(self) -> List[Dict]:
        """
        Generate the list of functions that can be passed to the chatgpt
        API call.
        """
        return [self._plugin_to_function(p) for
                p in self.plugins.values()]

    def _plugin_to_function(self, plugin: PluginInterface) -> Dict:
        """
        Convert a plugin to the function call specification as
        required by the ChatGPT API:
        https://platform.openai.com/docs/api-reference/chat/create#chat/create-functions
        """
        function = {}
        function["name"] = plugin.get_name()
        function["description"] = plugin.get_description()
        function["parameters"] = plugin.get_parameters()
        return function
    
    def _execute_plugin(self, func_call) -> str:
        """
        If a plugin exists for the given function call, execute it.
        """
        func_name = func_call.get("name")
        print(f"Executing plugin {func_name}")
        if func_name in self.plugins:
            arguments = json.loads(func_call.get("arguments"))
            plugin = self.plugins[func_name]
            plugin_response = plugin.execute(**arguments)
        else:
            plugin_response = {"error": f"No plugin found with name {func_call}"}

        # We need to pass the plugin response back to ChatGPT
        # so that it can process it. In order to do this we
        # need to append the plugin response into the conversation
        # history. However, this is just temporary so we make a
        # copy of the messages and then append to that copy.
        print(f"Response from plugin {func_name}: {plugin_response}")
        messages = list(self.conversation.conversation_history)
        messages.append({"role": "function",
                         "content": json.dumps(plugin_response),
                         "name": func_name})
        next_chatgpt_response = self._chat_completion_request(messages)

        # If ChatGPT is asking for another function call, then
        # we need to call _execute_plugin again. We will keep
        # doing this until ChatGPT keeps returning function_call
        # in its response. Although it might be a good idea to
        # cut it off at some point to avoid an infinite loop where
        # it gets stuck in a plugin loop.
        if next_chatgpt_response.get("function_call"):
            return self._execute_plugin(next_chatgpt_response.get("function_call"))
        return next_chatgpt_response.get("content")


    def get_chatgpt_response(self, user_message: str) -> str:
        """
        For the given user_message,
        get the response from ChatGPT
        """        
        self.conversation.add_message("user", user_message)
        try:
            chatgpt_response = self._chat_completion_request(
                self.conversation.conversation_history)
            
            if chatgpt_response.get("function_call"):
                chatgpt_message = self._execute_plugin(
                    chatgpt_response.get("function_call"))
            else:
                chatgpt_message = chatgpt_response.get("content")
            self.conversation.add_message("assistant", chatgpt_message)
            return chatgpt_message
        except Exception as e:
            print(e)
            return "something went wrong"


    def _chat_completion_request(self, messages: List[Dict]):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + openai.api_key,
        }
        json_data = {"model": GPT_MODEL, "messages": messages, "temperature": 0.7}
        if self.plugins:
            json_data.update({"functions": self._get_functions()})
        try:
            print('Hello')
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            print(response.json())
            return response.json()["choices"][0]["message"]
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

