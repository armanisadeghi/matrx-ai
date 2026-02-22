"""
Comparison: Old approach vs New Agent system

This shows how the Agent system simplifies prompt handling.
"""

import asyncio
from client.unified_client import UnifiedAIClient, AIMatrixRequest
from prompts.tests.agent_old import Agent
from context.console_emitter import ConsoleEmitter
from client.ai_requests import execute_until_complete
from tests.ai.test_context import create_test_execution_context
from initialize_systems import initialize
from matrx_utils import vcprint, clear_terminal

initialize()
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


# ============================================================================
# NEW APPROACH: Using Agent System (Clean & Simple)
# ============================================================================

async def create_conversation_with_agent(
    prompt_id: str,
    variables: dict,
    debug: bool = False,
):
    """Using Agent system - clean, type-safe, easy to understand"""
    agent = await Agent.from_prompt_id(prompt_id, variables=variables)
    
    conversation = await agent.execute(
        user_input="Please analyze this topic",
    )
    
    return conversation


# ============================================================================
# EVEN SIMPLER: One-liner approach
# ============================================================================

async def create_conversation_simple(
    prompt_id: str,
    variables: dict,
    debug: bool = False,
):
    """Simplest: Everything in one flow (conceptual example)"""
    agent = await Agent.from_prompt_id(prompt_id, variables=variables)
    return agent.to_config()


async def main():
    clear_terminal()
    
    print("=" * 70)
    print("AGENT SYSTEM COMPARISON")
    print("=" * 70)
    
    prompt_id = "002edf1b-26e6-4fb1-86cb-21000e319f2a"
    variables = {
        "topic": "Recent fires at a Swiss ski resort",
        "random": "IF YOU SEE THIS, DO NOT RESPOND",
    }
    
    print("\nUsing NEW Agent System:")
    print("-" * 70)
    
    print("\nBenefits:")
    print("  - Clean, type-safe API")
    print("  - Variables handled automatically")
    print("  - Config overrides support")
    print("  - Chainable methods")
    print("  - Easy to test and reuse")
    print("  - Self-documenting code")
    
    print("\n" + "=" * 70)
    print("Testing actual execution...")
    print("=" * 70)
    
    try:
        conversation = await create_conversation_with_agent(
            prompt_id, variables, debug=False
        )
        print("\nExecution completed successfully!")
        print(f"Conversation: {conversation}")
        print(f"Response preview: {conversation.last_response[:200]}...")
    except Exception as e:
        print(f"\nError (expected if model_id not configured): {e}")


if __name__ == "__main__":
    asyncio.run(main())
