"""
Shared types for the prompts/agent system.

This module contains dataclasses and type definitions used across
the prompts and agent modules to avoid circular imports.
"""

from typing import Dict
from dataclasses import dataclass
from config.unified_config import UnifiedConfig
from prompts.variables import AgentVariable


@dataclass
class AgentConfig:
    """
    Configuration for creating an Agent instance.
    
    This is the return type from manager.to_config() methods.
    Contains all necessary components to initialize an Agent.
    
    Attributes:
        name: Display name for the agent
        config: UnifiedConfig instance with messages, model settings, etc.
        variable_defaults: Dictionary of variable definitions (name -> AgentVariable)
    """
    name: str
    config: UnifiedConfig
    variable_defaults: Dict[str, AgentVariable]
