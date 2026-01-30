"""
Base agent class with tool calling capabilities.
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json


class Tool:
    """Represents a tool that an agent can use."""
    
    def __init__(self, name: str, description: str, parameters: dict):
        self.name = name
        self.description = description
        self.parameters = parameters  # JSON schema for parameters
    
    def to_dict(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.tools = []
        self._register_tools()
    
    def _register_tools(self):
        """Register the tools available to this agent."""
        self.tools = self.get_available_tools()
    
    @abstractmethod
    def get_available_tools(self) -> List[Tool]:
        """Return available tools for this agent."""
        pass
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.
        
        Args:
            task: The task description
            context: Additional context for the task
            
        Returns:
            Result of the task execution
        """
        # Default implementation - can be overridden by subclasses
        pass
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool by name with the given arguments.
        
        Override this method to implement actual tool calls.
        """
        raise NotImplementedError(f"Tool '{tool_name}' not implemented")
    
    def format_result(self, result: Any) -> str:
        """Format the result for output."""
        if isinstance(result, dict):
            return json.dumps(result, indent=2)
        return str(result)


class AgentToolCall:
    """Represents a tool call in a conversation."""
    
    def __init__(self, tool_name: str, arguments: Dict[str, Any]):
        self.tool_name = tool_name
        self.arguments = arguments
    
    @classmethod
    def from_response(cls, response) -> "AgentToolCall":
        """Create from OpenAI-style response."""
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            return cls(
                tool_name=tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments)
            )
        return None
    
    def to_dict(self) -> dict:
        return {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": f"call_{self.tool_name}",
                    "type": "function",
                    "function": {
                        "name": self.tool_name,
                        "arguments": json.dumps(self.arguments)
                    }
                }
            ]
        }
