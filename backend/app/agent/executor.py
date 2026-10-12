import logging
import uuid
from typing import Optional
from google import genai
from google.genai import types

from .state import AgentState, Message
from .memory import MemoryManager
from .registry import registry
from .prompts import SYSTEM_PROMPT
from ..core.config import settings
from . import tools # Ensure tools are loaded

logger = logging.getLogger(__name__)

class MaxIterationsExceeded(Exception):
    pass

class AgentExecutor:
    def __init__(self, memory: MemoryManager = None):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")
        
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.memory = memory or MemoryManager()
        self.state = AgentState(conversation_id=str(uuid.uuid4()))
        self.max_iterations = settings.MAX_AGENT_ITERATIONS
        self.model_name = settings.MODEL_NAME

    def _get_gemini_tools(self):
        gemini_tools = registry.get_gemini_tools()
        if not gemini_tools:
            return None
        return gemini_tools

    def process_message(self, user_input: str) -> str:
        logger.info(f"Processing user input: {user_input}")
        
        # Add to state and memory
        user_msg = Message(role="user", content=user_input)
        self.state.messages.append(user_msg)
        self.memory.add_message(user_msg)

        iteration = 0
        
        history_for_chat = []
        for msg in self.memory.get_gemini_history()[:-1]:
            history_for_chat.append(
                types.Content(
                    role=msg["role"], 
                    parts=[types.Part.from_text(text=p["text"]) for p in msg["parts"]]
                )
            )

        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=self._get_gemini_tools(),
                temperature=0.2,
            ),
            history=history_for_chat if history_for_chat else None
        )

        current_msg = user_input

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")
            logger.debug(f"Second model request / sending request to model: {current_msg}")
            
            try:
                response = chat.send_message(current_msg)
                logger.debug(f"Model response / parts: {response.parts}")
                
                if response.function_calls:
                    function_responses = []
                    for function_call in response.function_calls:
                        tool_name = function_call.name
                        tool_args = function_call.args
                        logger.info(f"Tool selected: {tool_name} with args {tool_args}")
                        logger.debug(f"Function call details: {function_call}")
                        
                        try:
                            tool = registry.get_tool(tool_name)
                            args_dict = dict(tool_args) if tool_args else {}
                            result = tool.execute(**args_dict)
                            logger.info(f"Tool result: {result}")
                            
                            self.state.messages.append(
                                Message(role="model", content="", name=tool_name, tool_call_id=tool_name)
                            )
                            self.state.messages.append(
                                Message(role="tool", content=str(result), name=tool_name)
                            )
                            
                            function_resp = types.Part.from_function_response(
                                name=tool_name,
                                response=result
                            )
                            logger.debug(f"Function response part: {function_resp}")
                            function_responses.append(function_resp)
                            
                        except ValueError as e:
                            logger.error(f"Unknown tool requested: {tool_name}")
                            err_resp = {"error": str(e)}
                            function_responses.append(types.Part.from_function_response(name=tool_name, response=err_resp))
                        except Exception as e:
                            logger.error(f"Tool execution failed: {str(e)}")
                            err_resp = {"error": f"Tool execution failed: {str(e)}"}
                            function_responses.append(types.Part.from_function_response(name=tool_name, response=err_resp))
                    
                    current_msg = function_responses
                    continue
                
                final_text = response.text
                logger.info(f"Final response: {final_text}")
                logger.debug(f"Second model response (final): {final_text}")
                
                model_msg = Message(role="model", content=final_text)
                self.state.messages.append(model_msg)
                self.memory.add_message(model_msg)
                return final_text
                
            except Exception as e:
                logger.error(f"LLM Error: {str(e)}")
                raise

        raise MaxIterationsExceeded(f"Agent exceeded maximum iterations ({self.max_iterations})")
