from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


# ============================================================================
# AGENT VARIABLE
# ============================================================================


class AgentVariable(BaseModel):
    """Represents a variable in an agent/prompt"""

    name: str
    value: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = False
    help_text: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    def get_value(self) -> str:
        """Get the final value with priority: value > default_value > error if required"""
        if self.value is not None:
            return self.value
        if self.default_value:
            return self.default_value
        if self.required:
            raise ValueError(f"Required variable '{self.name}' has no value")
        return ""

    @classmethod
    def from_dict(cls, var_def: Dict[str, Any]) -> "AgentVariable":
        """
        Create AgentVariable from dictionary.

        Args:
            var_def: Dictionary with keys: name, defaultValue, required, helpText

        Returns:
            AgentVariable instance
        """
        return cls(
            name=var_def["name"],
            default_value=var_def.get("defaultValue", ""),
            required=var_def.get("required", False),
            help_text=var_def.get("helpText"),
        )

    @staticmethod
    def from_list(var_defs: Optional[list]) -> Dict[str, "AgentVariable"]:
        """
        Parse list of variable definitions into dict of AgentVariables.

        Args:
            var_defs: List of variable definition dicts (from database)

        Returns:
            Dict mapping variable names to AgentVariable instances
        """
        if not var_defs:
            return {}

        return {
            var_def["name"]: AgentVariable.from_dict(var_def) for var_def in var_defs
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent variables to a dictionary.
        """
        return {
            "name": self.name,
            "value": self.value,
            "default_value": self.default_value,
            "required": self.required,
            "help_text": self.help_text,
        }
