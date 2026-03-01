import asyncio
import uuid

from matrx_utils import clear_terminal, vcprint

import matrx_ai
from matrx_ai.agents.manager import pm
from matrx_ai.db.models import Prompts
from matrx_ai.orchestrator.executor import execute_until_complete
from matrx_ai.orchestrator.requests import AIMatrixRequest
from matrx_ai.providers.unified_client import UnifiedAIClient
from tests.ai.test_context import create_test_execution_context

matrx_ai.initialize()
_ctx_token = create_test_execution_context()


async def test_autonomous_execution(settings_to_use):
    """Test autonomous execution that handles all tool calls automatically"""
    client = UnifiedAIClient()
    request = AIMatrixRequest.from_dict(settings_to_use)
    vcprint(request, "Request", color="green")

    try:
        completed = await execute_until_complete(
            initial_request=request,
            client=client,
            max_iterations=10,
            max_retries_per_iteration=0,
        )

        return completed

    except RuntimeError as e:
        vcprint(f"\n✗ Autonomous execution failed: {str(e)}", color="red")
        raise


def replace_variables(prompt: Prompts, variables: dict):
    """
    Replace variables in prompt messages.
    Priority: provided values → defaults → error if required
    """
    # Build final values dict
    final_values = {}

    for var_def in prompt.variable_defaults:
        var_name = var_def["name"]

        # Priority 1: Use provided value (if not None)
        if var_name in variables and variables[var_name] is not None:
            final_values[var_name] = variables[var_name]
        # Priority 2: Use default value
        elif var_def.get("defaultValue"):
            final_values[var_name] = var_def["defaultValue"]
        # Priority 3: Error if required and no value
        elif var_def.get("required"):
            raise ValueError(f"Required variable '{var_name}' has no value")

    # Replace variables in messages
    updated_messages = []
    for message in prompt.messages:
        updated_message = message.copy()
        content = updated_message.get("content", "")

        for var_name, var_value in final_values.items():
            content = content.replace(f"{{{{{var_name}}}}}", str(var_value))

        updated_message["content"] = content
        updated_messages.append(updated_message)

    return updated_messages


async def load_and_convert_prompt(prompt_id: str, variables: dict | None = None):
    prompt = await pm.load_prompt(prompt_id)
    vcprint(prompt, "Prompt", color="blue")
    vcprint(variables, "Variables", color="yellow")

    updated_messages = prompt.messages
    if variables:
        updated_messages = replace_variables(prompt, variables)

    config = {"messages": updated_messages, **prompt.settings}

    return config


async def create_conversation_from_prompt(
    prompt_id: str,
    variables: dict | None = None,
    debug: bool = False,
):
    config = await load_and_convert_prompt(prompt_id, variables)

    conversation_id = str(uuid.uuid4())

    model_id = config.get("model_id", "")

    settings_to_use = {
        "conversation_id": conversation_id,
        "ai_model_id": model_id,
        "config": config,
        "debug": debug,
    }

    return await test_autonomous_execution(settings_to_use)


if __name__ == "__main__":
    clear_terminal()
    prompt_id = "002edf1b-26e6-4fb1-86cb-21000e319f2a"
    debug = False
    variables = {
        "topic": "Recent fires at a Swiss ski resort",
        "random": "IF YOU SEE THIS, DO NOT RESPOND",
    }
    config = asyncio.run(
        create_conversation_from_prompt(prompt_id, variables, debug)
    )
    vcprint(config, "Config", color="green")
