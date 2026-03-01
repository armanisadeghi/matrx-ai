"""
Example usage of the Agent system - showing how simple it is to work with agents.
"""

import asyncio

from matrx_utils import clear_terminal, vcprint

from agents.definition import Agent
from initialize_systems import initialize

initialize()


async def example_1_basic_usage():
    """Example 1: Basic agent usage"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Agent Usage")
    print("=" * 60)

    # Load agent from prompt
    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")

    print(f"\nLoaded: {agent}")
    print(f"\nVariables: {agent.list_variables()}")

    # Set variable
    agent.set_variable("topic", "Recent fires at a Swiss ski resort")

    # Get config (ready to execute)
    config = agent.to_config()

    vcprint(config, "Agent Config", color="green")


async def example_2_chainable_api():
    """Example 2: Chainable API for fluent configuration"""
    print("\n" + "=" * 60)
    print("Example 2: Chainable/Fluent API")
    print("=" * 60)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")

    # Chain everything together
    config = (
        agent.set_variable("topic", "AI Safety Regulations")
        .set_config(temperature=0.7, reasoning_effort="high")
        .to_config()
    )

    vcprint(config, "Chained Config", color="blue")


async def example_3_multiple_variables():
    """Example 3: Setting multiple variables at once"""
    print("\n" + "=" * 60)
    print("Example 3: Multiple Variables")
    print("=" * 60)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")

    # Set multiple variables
    agent.set_variables(
        {
            "topic": "Climate Change Policy",
        }
    )

    config = agent.to_config()

    # Check that variable was replaced in message
    user_message = config["messages"][1]["content"]
    print(f"\nUser message content:\n{user_message[:200]}...")
    print("\n✓ Variable replaced: " + str("{{topic}}" not in user_message))


async def example_4_initialization_with_values():
    """Example 4: Initialize agent with variables and config"""
    print("\n" + "=" * 60)
    print("Example 4: Initialize with Values")
    print("=" * 60)

    agent = await Agent.from_prompt_id(
        "002edf1b-26e6-4fb1-86cb-21000e319f2a",
        variables={"topic": "Healthcare Reform"},
        config_overrides={"temperature": 0.5, "stream": False},
    )

    config = agent.to_config()
    print("\nAgent created with variables and config overrides")
    print(f"Topic: {agent.get_variable('topic')}")
    print(f"Temperature: {config.get('temperature')}")
    print(f"Stream: {config.get('stream')}")


async def example_5_clone_and_modify():
    """Example 5: Clone an agent and modify the copy"""
    print("\n" + "=" * 60)
    print("Example 5: Clone and Modify")
    print("=" * 60)

    # Create original
    original = await Agent.from_prompt_id(
        "002edf1b-26e6-4fb1-86cb-21000e319f2a", variables={"topic": "Education Policy"}
    )

    # Clone and modify
    clone = original.clone()
    clone.set_variable("topic", "Tax Reform")

    print(f"\nOriginal topic: {original.get_variable('topic')}")
    print(f"Clone topic: {clone.get_variable('topic')}")
    print("✓ Clone is independent from original")


async def main():
    clear_terminal()

    print("=" * 60)
    print("AGENT SYSTEM EXAMPLES")
    print("=" * 60)

    await example_1_basic_usage()
    await example_2_chainable_api()
    await example_3_multiple_variables()
    await example_4_initialization_with_values()
    await example_5_clone_and_modify()

    print("\n" + "=" * 60)
    print("All examples completed successfully! ✓")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
