"""
LLM Agent System - Clean abstraction for working with prompt-based agents.

This module provides the core Agent class that bridges database prompts (templates)
with executable LLM agents. Agents are instances of prompts with:
- Variable replacement
- Config overrides
- Easy execution interface
- Conversation management

Architecture:
- Agent = Template + Variables (pre-execution, reusable)
- Conversation = Execution result + History (post-execution, stateful)
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from database.main.models import Prompts
from prompts.manager import pm
import uuid

if TYPE_CHECKING:
    from typing import Any as StreamHandler  # placeholder: socket_printer not needed in matrx-ai

# Import the unified system classes
from config.unified_config import UnifiedConfig
from client.unified_client import AIMatrixRequest


class AgentVariable(BaseModel):
    """Represents a variable in an agent/prompt"""
    name: str
    value: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = False
    help_text: Optional[str] = None
    
    model_config = ConfigDict(extra='allow')
    
    def get_value(self) -> str:
        """Get the final value with priority: value > default_value > error if required"""
        if self.value is not None:
            return self.value
        if self.default_value:
            return self.default_value
        if self.required:
            raise ValueError(f"Required variable '{self.name}' has no value")
        return ""


class Agent:
    """
    An LLM Agent - an instance of a prompt template with variables and config.
    
    Usage:
        # Load from database
        agent = await Agent.from_prompt_id("prompt-uuid")
        
        # Set variables
        agent.set_variable("topic", "AI Safety")
        
        # Override config
        agent.set_config(temperature=0.7)
        
        # Get executable config
        config = agent.to_config()
        
        # Or execute directly
        response = await agent.execute()
    """
    
    def __init__(
        self,
        prompt: Prompts,
        variables: Optional[Dict[str, str]] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ):
        self.prompt = prompt
        self._variables: Dict[str, AgentVariable] = {}
        self._config_overrides = config_overrides or {}
        
        # Initialize variables from prompt defaults
        self._init_variables()
        
        # Apply provided variables
        if variables:
            for name, value in variables.items():
                self.set_variable(name, value)
    
    def _init_variables(self):
        """Initialize variables from prompt's variable_defaults"""
        for var_def in self.prompt.variable_defaults:
            self._variables[var_def["name"]] = AgentVariable(
                name=var_def["name"],
                default_value=var_def.get("defaultValue", ""),
                required=var_def.get("required", False),
                help_text=var_def.get("helpText"),
            )
    
    def set_variable(self, name: str, value: str) -> "Agent":
        """Set a variable value (chainable)"""
        if name not in self._variables:
            # Allow setting variables not in defaults (for flexibility)
            self._variables[name] = AgentVariable(name=name, value=value)
        else:
            self._variables[name].value = value
        return self
    
    def set_variables(self, variables: Dict[str, str]) -> "Agent":
        """Set multiple variables at once (chainable)"""
        for name, value in variables.items():
            self.set_variable(name, value)
        return self
    
    def set_config(self, **kwargs) -> "Agent":
        """Override config settings (chainable)"""
        self._config_overrides.update(kwargs)
        return self
    
    def _replace_variables_in_messages(self) -> List[Dict[str, str]]:
        """Replace variables in all messages"""
        # Build final values dict
        final_values = {}
        for var_name, var in self._variables.items():
            try:
                final_values[var_name] = var.get_value()
            except ValueError as e:
                # Re-raise with context
                raise ValueError(f"Agent variable error: {str(e)}")
        
        # Replace in messages
        updated_messages = []
        for message in self.prompt.messages:
            updated_message = message.copy()
            content = updated_message.get("content", "")
            
            for var_name, var_value in final_values.items():
                content = content.replace(f"{{{{{var_name}}}}}", str(var_value))
            
            updated_message["content"] = content
            updated_messages.append(updated_message)
        
        return updated_messages
    
    def to_config(self) -> UnifiedConfig:
        """
        Convert agent to UnifiedConfig (the system's standard config class).
        
        Returns UnifiedConfig with:
        - Messages with variables replaced
        - Settings from prompt
        - Config overrides applied
        """
        # Get messages with variables replaced
        messages = self._replace_variables_in_messages()
        
        # Start with prompt settings and add messages
        config_dict = {
            "messages": messages,
            **self.prompt.settings,
        }
        
        # Apply overrides
        config_dict.update(self._config_overrides)
        
        # Use UnifiedConfig.from_dict() to create proper dataclass
        return UnifiedConfig.from_dict(config_dict)
    
    def get_variable(self, name: str) -> Optional[str]:
        """Get current value of a variable"""
        if name in self._variables:
            try:
                return self._variables[name].get_value()
            except ValueError:
                return None
        return None
    
    def list_variables(self) -> Dict[str, Dict[str, Any]]:
        """List all variables with their current state"""
        return {
            name: {
                "value": var.value,
                "default": var.default_value,
                "required": var.required,
                "help_text": var.help_text,
            }
            for name, var in self._variables.items()
        }
    
    @classmethod
    async def from_prompt_id(
        cls,
        prompt_id: str,
        variables: Optional[Dict[str, str]] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ) -> "Agent":
        """Load agent from prompt ID in database"""
        prompt = await pm.load_prompt(prompt_id)
        return cls(prompt, variables, config_overrides)
    
    @classmethod
    def from_prompt(
        cls,
        prompt: Prompts,
        variables: Optional[Dict[str, str]] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ) -> "Agent":
        """Create agent from existing Prompts object"""
        return cls(prompt, variables, config_overrides)
    
    def clone(self) -> "Agent":
        """Create a copy of this agent"""
        return Agent(
            prompt=self.prompt,
            variables={name: var.value for name, var in self._variables.items() if var.value},
            config_overrides=self._config_overrides.copy(),
        )
    
    def with_variables(self, **kwargs) -> "Agent":
        """
        Clone agent and set variables (functional style).
        Returns new agent instance without modifying original.
        
        Example:
            spanish_agent = base_agent.with_variables(language="Spanish")
        """
        clone = self.clone()
        clone.set_variables(kwargs)
        return clone
    
    def is_ready(self) -> bool:
        """Check if all required variables are set"""
        return len(self.missing_variables()) == 0
    
    def missing_variables(self) -> List[str]:
        """Get list of required variables that haven't been set"""
        missing = []
        for var in self._variables.values():
            if var.required and var.value is None and not var.default_value:
                missing.append(var.name)
        return missing
    
    def _apply_user_input(self, config: UnifiedConfig, user_input: str) -> None:
        """
        Apply user_input to config.messages following the rules:
        - If last message is role='user': append to the LAST text content item in that message
        - If last message is NOT role='user': create new user message with user_input
        
        Note: A user message can have multiple content items (text, images, documents, etc.)
        We append to the last text-type content item.
        
        Args:
            config: UnifiedConfig to modify (modifies in place)
            user_input: User input text to apply
        """
        if not user_input:
            return
        
        messages = config.messages._messages
        
        if messages and str(messages[-1].role) == "user":
            # Find the last text content in the last user message
            last_message = messages[-1]
            last_text_content = None
            
            # Iterate through content items to find the last text-type item
            for item in last_message.content:
                if hasattr(item, 'type') and str(item.type) in ["text", "input_text"]:
                    last_text_content = item
            
            if last_text_content:
                # Append to existing text content
                last_text_content.text += "\n" + user_input
            else:
                # No text content found, create one
                from config.unified_config import TextContent
                last_message.content.append(
                    TextContent(type="text", text=user_input)
                )
        else:
            # Create new user message using the config's built-in method
            config.append_user_message(user_input)
    
    async def execute(
        self,
        user_input: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        emitter: Optional["StreamHandler"] = None,
        **config_overrides
    ) -> "Conversation":
        """
        Execute agent and return Conversation.
        
        Args:
            user_input: Optional input to append/add to messages
            user_id: User ID for tracking
            conversation_id: Optional conversation ID (creates new if not provided)
            emitter: Optional stream handler for real-time streaming
            **config_overrides: Override any config settings
            
        Returns:
            Conversation object (even for one-shot usage)
        """
        # Import here to avoid circular dependency
        from client.unified_client import UnifiedAIClient
        from client.ai_requests import execute_until_complete
        
        # Check if ready
        if not self.is_ready():
            raise ValueError(
                f"Agent not ready to execute. Missing required variables: {self.missing_variables()}"
            )
        
        # Get UnifiedConfig with variables replaced
        config = self.to_config()  # Returns UnifiedConfig
        
        # Apply user_input (appends to last user message or creates new one)
        if user_input:
            self._apply_user_input(config, user_input)
        
        # Apply config overrides directly to UnifiedConfig attributes
        for key, value in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Generate IDs if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        if not user_id:
            user_id = "anonymous"  # Default user
        
        # Get model_id from prompt settings
        model_id = self.prompt.settings.get("model_id", "")
        
        # Create AIMatrixRequest directly (no dict conversion!)
        request = AIMatrixRequest(
            conversation_id=conversation_id,
            user_id=user_id,
            ai_model_id=model_id,
            config=config,  # Direct UnifiedConfig
            debug=False,
            emitter=emitter,
        )
        
        # Create conversation object (before execution for tracking)
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            agent=self,
            emitter=emitter,
        )
        
        # Save initial state (request started)
        await conversation._save_start()
        
        try:
            # Execute
            client = UnifiedAIClient()
            
            result = await execute_until_complete(
                initial_request=request,
                client=client,
                max_iterations=10,
                max_retries_per_iteration=0,
            )
            
            # Update conversation with result
            conversation._update_from_result(result)
            
            # Save final state (request completed)
            await conversation._save_complete()
            
            return conversation
            
        except Exception as e:
            # Save failed state
            await conversation._save_error(str(e))
            raise
    
    async def execute_oneshot(
        self,
        user_input: Optional[str] = None,
        user_id: Optional[str] = None,
        emitter: Optional["StreamHandler"] = None,
        **config_overrides
    ) -> str:
        """
        Execute agent and return just the response text (convenience method).
        
        Perfect for one-shot agents or tool usage where you don't need
        the conversation object.
        
        Returns:
            String response from the agent
        """
        conversation = await self.execute(
            user_input=user_input,
            user_id=user_id,
            emitter=emitter,
            **config_overrides
        )
        return conversation.last_response
    
    async def __call__(
        self,
        user_input: Optional[str] = None,
        **kwargs
    ) -> "Conversation":
        """
        Make agent callable for cleaner syntax.
        
        Example:
            conversation = await agent("Hello, world!")
        """
        return await self.execute(user_input=user_input, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to dict for debugging/serialization.
        """
        return {
            "prompt_id": str(self.prompt.id) if hasattr(self.prompt, 'id') else None,
            "prompt_name": self.prompt.name if hasattr(self.prompt, 'name') else None,
            "variables": {
                name: {
                    "value": var.value,
                    "default": var.default_value,
                    "required": var.required,
                }
                for name, var in self._variables.items()
            },
            "is_ready": self.is_ready(),
            "missing_variables": self.missing_variables(),
            "config_overrides": self._config_overrides,
            "model_id": self.prompt.settings.get("model_id") if hasattr(self.prompt, 'settings') and isinstance(self.prompt.settings, dict) else None,
        }
    
    def __repr__(self) -> str:
        var_count = len([v for v in self._variables.values() if v.value is not None])
        ready = "✓" if self.is_ready() else "✗"
        return f"Agent(name='{self.prompt.name}', variables={var_count}/{len(self._variables)}, ready={ready})"


# ============================================================================
# CONVERSATION CLASS
# ============================================================================


class Conversation:
    """
    Conversation = Agent execution result + message history.
    
    Created automatically when an agent executes.
    Can be continued for multi-turn interactions or just used to extract response.
    
    DESIGN PRINCIPLE: Single Source of Truth
    
    The system GUARANTEES:
    - _request is an AIMatrixRequest
    - _request.config is a UnifiedConfig
    - _request.config.messages is a MessageList
    - _request.config.messages._messages are UnifiedMessage objects
    
    No guessing, no conditionals, no fallbacks - just use the dataclasses directly.
    
    Single copy of messages:
    - Messages are in _request.config.messages (single source of truth)
    - Properties access them directly from there
    - to_dict() shows config (which includes messages) - no duplication
    
    Usage:
        # One-shot
        conversation = await agent.execute(user_input="Hello")
        response = conversation.last_response
        
        # Multi-turn
        await conversation.send("Tell me more")
        response2 = conversation.last_response
        
        # Or with callable syntax
        await conversation("Continue")
    """
    
    def __init__(
        self,
        conversation_id: str,
        user_id: str,
        agent: Agent,
        emitter: Optional["StreamHandler"] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.agent = agent  # Original agent (for reference)
        self.emitter = emitter
        self.metadata = metadata or {}
        self._request: Optional[Any] = None  # AIMatrixRequest with full state
    
    @classmethod
    async def load(cls, conversation_id: str) -> "Conversation":
        """
        Load existing conversation from database.
        
        TODO: Implement database loading
        - Load conversation by ID
        - Restore message history
        - Restore config
        - Restore metadata
        """
        # Placeholder for database integration
        raise NotImplementedError(
            "Conversation.load() requires database integration. "
            "Will load conversation state from DB by conversation_id."
        )
    
    async def send(
        self,
        message: str,
        **config_overrides
    ) -> "Conversation":
        """
        Continue conversation with a new message.
        
        Args:
            message: User message to send
            **config_overrides: Optional config overrides for this message
            
        Returns:
            Self (for chaining)
        """
        # Import here to avoid circular dependency
        from client.unified_client import UnifiedAIClient
        from client.ai_requests import execute_until_complete
        
        if not self._request:
            raise RuntimeError("Conversation has no request state. Cannot send message.")
        
        # Simply append user message to the existing config
        # The config already has all previous messages, tool calls, thinking, etc.
        self._request.config.append_user_message(message)
        
        # Apply config overrides if any
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(self._request.config, key):
                    setattr(self._request.config, key, value)
        
        # Save continuation state
        await self._save_continuation()
        
        try:
            # Execute with the updated request
            # The request already has conversation_id, user_id, ai_model_id, etc.
            client = UnifiedAIClient()
            
            result = await execute_until_complete(
                initial_request=self._request,
                client=client,
                max_iterations=10,
                max_retries_per_iteration=0,
            )
            
            # Result is CompletedRequest, extract the updated request
            if hasattr(result, 'request'):
                self._request = result.request
            else:
                self._request = result
            
            # Save updated state
            await self._save_complete()
            
            return self
            
        except Exception as e:
            await self._save_error(str(e))
            raise
    
    async def __call__(self, message: str, **kwargs) -> "Conversation":
        """
        Make conversation callable for cleaner syntax.
        
        Example:
            await conversation("Tell me more")
        """
        return await self.send(message, **kwargs)
    
    @property
    def last_response(self) -> str:
        """
        Get content of last assistant message.
        
        The system ALWAYS returns UnifiedMessage objects - no guessing needed.
        """
        if not self._request or not hasattr(self._request.config, 'messages'):
            return ""
        
        # Work with UnifiedMessage objects directly - they're ALWAYS UnifiedMessages
        messages = self._request.config.messages._messages
        
        # Find last assistant message and extract text
        for message in reversed(messages):
            # UnifiedMessage always has .role attribute
            if str(message.role) == "assistant":
                # Content is always a list of content items (TextContent, ThinkingContent, etc.)
                text_parts = []
                for item in message.content:
                    # Extract text from TextContent objects
                    if str(item.type) == "text":
                        text_parts.append(item.text)
                return "\n".join(text_parts)
        return ""
    
    @property
    def last_message(self) -> Dict[str, Any]:
        """
        Get full last message object (as dict).
        
        The system ALWAYS returns UnifiedMessage objects with to_dict() method.
        """
        if not self._request or not hasattr(self._request.config, 'messages'):
            return {}
        
        # UnifiedMessage always has to_dict() method
        messages = self._request.config.messages._messages
        if messages:
            return messages[-1].to_dict()
        return {}
    
    @property
    def messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages in conversation (as dicts for compatibility).
        
        MessageList ALWAYS has to_list() method that converts UnifiedMessages to dicts.
        """
        if not self._request or not hasattr(self._request.config, 'messages'):
            return []
        
        # MessageList.to_list() always exists and converts properly
        return self._request.config.messages.to_list()
    
    def _update_from_result(self, result: Any) -> None:
        """
        Update conversation state from execution result.
        
        Simple: Extract the AIMatrixRequest from CompletedRequest!
        The request contains:
        - Full UnifiedConfig with all messages (including tool calls, thinking, etc.)
        - conversation_id, user_id, ai_model_id
        - All usage, timing, and tool call history
        """
        # Result is a CompletedRequest with .request attribute
        if hasattr(result, 'request'):
            self._request = result.request
        else:
            # Fallback if it's already an AIMatrixRequest
            self._request = result
    
    # ========================================================================
    # DATABASE PERSISTENCE (Placeholders)
    # ========================================================================
    
    async def _save_start(self) -> None:
        """
        Save conversation start state (lazy/background).
        
        TODO: Implement database save
        - Save initial conversation state
        - Mark as 'in_progress'
        - Store: conversation_id, user_id, agent template ID, initial config
        - Run in background task to not block execution
        
        Purpose: Track that request was initiated (even if it fails)
        """
        # Placeholder - will implement with proper DB integration
        pass
    
    async def _save_complete(self) -> None:
        """
        Save conversation completion state (lazy/background).
        
        TODO: Implement database save
        - Update conversation state
        - Mark as 'completed'
        - Store: final message history, tokens used, timing info
        - Run in background task
        
        Purpose: Track successful completion and final state
        """
        # Placeholder - will implement with proper DB integration
        pass
    
    async def _save_continuation(self) -> None:
        """
        Save conversation continuation (lazy/background).
        
        TODO: Implement database save
        - Update conversation with new user message
        - Mark as 'continuing'
        - Store updated message history
        - Run in background task
        """
        # Placeholder - will implement with proper DB integration
        pass
    
    async def _save_error(self, error: str) -> None:
        """
        Save conversation error state (lazy/background).
        
        TODO: Implement database save
        - Update conversation state
        - Mark as 'failed'
        - Store: error message, stack trace, partial state
        - Run in background task
        
        Purpose: Track failures for debugging and analytics
        """
        # Placeholder - will implement with proper DB integration
        pass
    
    async def save(self) -> None:
        """
        Explicitly save conversation (usually auto-saved).
        
        TODO: Implement database save
        - Force immediate save (not background)
        - Useful for critical checkpoints
        """
        # Placeholder - will implement with proper DB integration
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert conversation to dict for debugging/serialization.
        
        IMPORTANT: Messages are in config.messages - don't duplicate them!
        """
        # UnifiedConfig.to_dict() always exists
        config_dict = self._request.config.to_dict() if self._request else None
        
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "agent": {
                "prompt_id": str(self.agent.prompt.id) if hasattr(self.agent.prompt, 'id') else None,
                "prompt_name": self.agent.prompt.name if hasattr(self.agent.prompt, 'name') else None,
            },
            "config": config_dict,  # Messages are in here (config.messages)
            "message_count": len(self.messages),
            "last_response_preview": self.last_response[:200] if self.last_response else None,
            "has_emitter": self.emitter is not None,
            "metadata": self.metadata,
        }
    
    def __repr__(self) -> str:
        msg_count = len(self.messages)
        return f"Conversation(id='{self.conversation_id[:8]}...', messages={msg_count})"
