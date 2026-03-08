"""
Rebuilt Agent System - Proper architecture using core components.

Key Principles:
1. Agent uses UnifiedConfig directly (no modifications)
2. Prompts/PromptBuiltins are just sources to create agents
3. Variables are separate from config (applied when needed)
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from matrx_ai.agents.manager import pm
from matrx_ai.agents.types import AgentConfig
from matrx_ai.agents.variables import AgentVariable
from matrx_ai.config.unified_config import UnifiedConfig, UnifiedMessage
from matrx_ai.config.usage_config import AggregatedUsage, TokenUsage
from matrx_ai.orchestrator.executor import execute_ai_request
from matrx_ai.orchestrator.requests import CompletedRequest

# ============================================================================
# AGENT EXECUTE RESULT
# ============================================================================


@dataclass
class AgentExecuteResult:
    output: str
    assistant_response: UnifiedMessage | None
    config: UnifiedConfig
    usage: AggregatedUsage = field(default_factory=AggregatedUsage)
    usage_history: list[TokenUsage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# AGENT
# ============================================================================


class Agent:
    """
    An LLM Agent - UnifiedConfig + variable management.

    Core components:
    - config: UnifiedConfig (the actual dataclass, unmodified)
    - variable_defaults: dict[str, AgentVariable] (defined variables)
    - variable_values: dict[str, Any] (current values)

    Prompts/PromptBuiltins are sources to create agents, not core to the agent itself.
    """

    def __init__(
        self,
        config: UnifiedConfig,
        variable_defaults: dict[str, AgentVariable] | None = None,
        name: str | None = None,
    ):
        """
        Initialize agent with core components.

        Args:
            config: UnifiedConfig instance (the actual dataclass)
            variable_defaults: Dict of variable definitions
            name: Optional name for identification in logs
        """
        self.name = name or "Agent"
        self.config = config
        self.variable_defaults = variable_defaults or {}
        self.variable_values: dict[str, Any] = {}
        self._variables_applied = False

        self.request_metadata: dict[str, Any] = {}
        self.last_completed_request: CompletedRequest | None = None

    def clone(self) -> Agent:
        """
        Create a complete, independent copy of this agent.

        Deep copies all components:
        - config (UnifiedConfig with all messages)
        - variable_defaults (AgentVariable definitions)
        - variable_values (current variable values)

        Resets the variables_applied flag so clones can reapply variables to their copy.

        IMPORTANT: Best practice is to clone BEFORE applying variables or executing.
        If you clone after variables are applied, the placeholders ({{var}}) are gone,
        so setting new variables on the clone won't work as expected.

        Recommended pattern:
            base = await Agent.from_prompt("id")  # Don't apply variables yet
            agent1 = base.clone().with_variables(topic="AI")
            agent2 = base.clone().with_variables(topic="ML")

        Returns:
            New Agent instance (completely independent)
        """
        cloned = Agent(
            config=deepcopy(self.config),
            variable_defaults=deepcopy(self.variable_defaults),
            name=self.name,  # Preserve name in clone
        )
        # Copy variable_values but not the applied flag
        cloned.variable_values = {}  # Start fresh for new variables
        # Reset the applied flag
        cloned._variables_applied = False
        return cloned

    def clone_with_variables(self, **variables) -> Agent:
        """
        Clone and immediately set/apply variables (convenience method).

        Common pattern: Create base agent, then make variations with different variables.

        Args:
            **variables: Variable names and values to set and apply

        Returns:
            New Agent instance with variables applied

        Example:
            base = await Agent.from_prompt("prompt-id")

            # Create multiple variations
            agent_en = base.clone_with_variables(language="English")
            agent_es = base.clone_with_variables(language="Spanish")
            agent_fr = base.clone_with_variables(language="French")
        """
        return self.clone().with_variables(**variables)

    def clone_with_overrides(self, **overrides) -> Agent:
        """
        Clone and immediately apply config overrides (convenience method).

        Args:
            **overrides: Config settings to override

        Returns:
            New Agent instance with overrides applied

        Example:
            base = await Agent.from_prompt("prompt-id")

            # Create variations with different configs
            agent_creative = base.clone_with_overrides(temperature=0.9)
            agent_precise = base.clone_with_overrides(temperature=0.1)
        """
        return self.clone().apply_config_overrides(**overrides)

    def clone_with(
        self,
        variables: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> Agent:
        """
        Clone and apply both variables and config overrides (comprehensive method).

        Args:
            variables: Optional dict of variable values to set and apply
            config_overrides: Optional dict of config settings to override

        Returns:
            New Agent instance with all modifications applied

        Example:
            base = await Agent.from_prompt("prompt-id")

            # Create variation with both variables and config changes
            agent = base.clone_with(
                variables={"language": "Spanish", "tone": "formal"},
                config_overrides={"temperature": 0.7, "max_output_tokens": 2000}
            )
        """
        cloned = self.clone()

        if variables:
            cloned.with_variables(**variables)

        if config_overrides:
            cloned.apply_config_overrides(**config_overrides)

        return cloned

    def set_variable(self, name: str, value: Any) -> Agent:
        """
        Set a variable value.

        Args:
            name: Variable name
            value: Variable value (will be converted to string when replaced)

        Returns:
            Self (for method chaining)

        Example:
            agent.set_variable("topic", "AI Safety")
        """
        self.variable_values[name] = value
        return self

    def set_variables(self, **variables) -> Agent:
        """
        Set multiple variable values at once.

        Args:
            **variables: Variable names and values as kwargs

        Returns:
            Self (for method chaining)

        Example:
            agent.set_variables(topic="AI Safety", audience="developers")
        """
        self.variable_values.update(variables)
        return self

    def apply_variables(self, force: bool = False) -> Agent:
        """
        Apply variable replacements to the config.
        Replaces all {{variable_name}} placeholders in system_instruction and messages.

        Variables are only applied once by default to avoid issues with multi-turn conversations.
        Use force=True to reapply variables.

        Uses values from variable_values (set via set_variable/set_variables).
        Variables with no value set become "" — no defaults are applied, no errors are raised.

        Args:
            force: If True, apply variables even if already applied

        Returns:
            Self (for method chaining)

        Example:
            agent.set_variables(topic="AI", audience="devs").apply_variables()
        """
        # Skip if already applied (unless forced)
        if self._variables_applied and not force:
            return self

        # Build final values dict (variable_values + defaults)
        final_values = {}

        for var_name, var_def in self.variable_defaults.items():
            if var_name in self.variable_values:
                # Use explicitly set value
                final_values[var_name] = self.variable_values[var_name]
            else:
                # Use AgentVariable.get_value() to handle defaults and required
                final_values[var_name] = var_def.get_value()

        # Also include any variable_values that aren't in variable_defaults
        for var_name, var_value in self.variable_values.items():
            if var_name not in final_values:
                final_values[var_name] = var_value

        # Use UnifiedConfig's replace_variables method
        self.config.replace_variables(final_values)

        # Mark as applied
        self._variables_applied = True

        return self

    def with_variables(self, **variables) -> Agent:
        """
        Set variables and apply them in one call (convenience method).
        This is the most common usage pattern.

        Args:
            **variables: Variable names and values as kwargs

        Returns:
            Self (for method chaining)

        Example:
            agent.with_variables(topic="AI Safety", audience="developers")
        """
        self.set_variables(**variables)
        self.apply_variables()
        return self

    def apply_config_overrides(self, **overrides) -> Agent:
        """
        Apply config overrides to the agent's UnifiedConfig.
        Can be called at any time to modify config settings.

        Args:
            **overrides: Config settings to override (e.g., temperature=0.7, max_output_tokens=2000)

        Returns:
            Self (for method chaining)

        Example:
            agent.apply_config_overrides(temperature=0.9, max_output_tokens=4000)
        """
        for key, value in overrides.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        return self

    @classmethod
    def from_dict(
        cls,
        config_dict: dict[str, Any],
        variable_defaults: dict[str, AgentVariable] | None = None,
        variables: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> Agent:
        """
        Create agent from config dictionary.

        Args:
            config_dict: Dictionary containing config data (messages, model, etc.)
            variable_defaults: Optional dict of variable definitions
            variables: Optional dict of variable values to set and apply immediately
            config_overrides: Optional dict of config settings to override

        Returns:
            Agent instance
        """
        # Use UnifiedConfig's from_dict method
        config = UnifiedConfig.from_dict(config_dict)
        agent = cls(config=config, variable_defaults=variable_defaults)

        # Apply variables if provided
        if variables:
            agent.with_variables(**variables)

        # Apply config overrides if provided
        if config_overrides:
            agent.apply_config_overrides(**config_overrides)

        return agent

    @classmethod
    def _build_from_config(
        cls,
        agent_config: AgentConfig,
        variables: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> Agent:
        agent = cls(
            config=agent_config.config,
            variable_defaults=agent_config.variable_defaults,
            name=agent_config.name,
        )
        if variables:
            agent.with_variables(**variables)
        if config_overrides:
            agent.apply_config_overrides(**config_overrides)
        return agent

    @classmethod
    async def from_id(
        cls,
        prompt_id: str,
        variables: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> Agent:
        agent_config = await pm.get_config(prompt_id)
        return cls._build_from_config(agent_config, variables, config_overrides)

    @classmethod
    async def from_prompt(
        cls,
        prompt_id: str,
        variables: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> Agent:
        agent_config = await pm.get_prompt_config(prompt_id)
        return cls._build_from_config(agent_config, variables, config_overrides)

    @classmethod
    async def from_builtin(
        cls,
        builtin_id: str,
        variables: dict[str, Any] | None = None,
        config_overrides: dict[str, Any] | None = None,
    ) -> Agent:
        agent_config = await pm.get_builtin_config(builtin_id)
        return cls._build_from_config(agent_config, variables, config_overrides)

    def set_user_input(self, user_input: str | list[dict[str, Any]]) -> Agent:
        self.config.append_or_extend_user_input(user_input)
        return self

    async def execute(
        self, user_input: str | list[dict[str, Any]] | None = None
    ) -> AgentExecuteResult:
        """Execute the agent with optional user input.

        Applies variables on first execution, appends user_input if provided,
        then delegates entirely to execute_ai_request() which reads all context
        (user_id, conversation_id, emitter, debug) from AppContext.

        This works identically whether called from an API route task, a tool
        spawning a sub-agent, or a local test script.
        """
        if self.variable_values and not self._variables_applied:
            self.apply_variables()
        if user_input:
            self.set_user_input(user_input)

        completed = await execute_ai_request(
            self.config,
            metadata=self.request_metadata,
        )
        return self._clean_up_response(completed)

    def _clean_up_response(self, response: CompletedRequest) -> AgentExecuteResult:
        last_response = response.request.config.messages.get_last_by_role("assistant")
        last_output = response.request.config.get_last_output()
        self.config = response.request.config
        self.last_completed_request = response
        return AgentExecuteResult(
            output=last_output,
            assistant_response=last_response,
            config=self.config,
            usage=response.total_usage,
            usage_history=list(response.request.usage_history),
            metadata=response.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "config": self.config,
            "variable_defaults": self.variable_defaults,
            "variable_values": self.variable_values,
            "variables_applied": self._variables_applied,
        }
