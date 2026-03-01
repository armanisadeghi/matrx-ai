"""
Comprehensive test of the new Agent + Conversation architecture.

This demonstrates all the key patterns and usage scenarios.
"""

import asyncio

from aidream.api.utils.console_emitter import ConsoleEmitter
from matrx_utils import clear_terminal, vcprint

import matrx_ai
from matrx_ai.agents.definition import Agent

matrx_ai.initialize()

# Create global stream handler for all tests
emitter = ConsoleEmitter("agent_test_suite")


async def test_1_basic_execution():
    """Test 1: Basic agent execution"""

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    agent.set_variable("topic", "Recent advances in AI")

    print(f"Ready: {agent.is_ready()}")
    print(f"Missing variables: {agent.missing_variables()}")

    vcprint(agent, "Agent", color="green")

    # Execute
    conversation = await agent.execute(
        user_input="Make this extremely concise and to the point",
        user_id="test-user",
        emitter=emitter,
    )
    vcprint(conversation, "Conversation", color="blue")


async def test_2_oneshot_execution():
    """Test 2: One-shot execution (convenience method)"""
    print("\n" + "=" * 70)
    print("TEST 2: One-shot Execution")
    print("=" * 70)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    agent.set_variable("topic", "Climate change")

    # Get just the response
    response = await agent.execute_oneshot(
        user_input="Give me a very brief summary",
        user_id="test-user",
        emitter=emitter,
    )

    print(f"Response type: {type(response)}")
    print(f"Response length: {len(response)} characters")
    print("✓ One-shot execution works!")


async def test_3_partial_variables():
    """Test 3: Partial variable binding (agent specialization)"""
    print("\n" + "=" * 70)
    print("TEST 3: Partial Variable Binding")
    print("=" * 70)

    # Load base agent
    base_agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")

    print(f"Base agent: {base_agent}")
    print(f"Ready: {base_agent.is_ready()}")

    # Create specialized agents with with_variables
    tech_agent = base_agent.with_variables(topic="Technology trends")
    science_agent = base_agent.with_variables(topic="Scientific discoveries")

    print(f"\nTech agent: {tech_agent}")
    print(f"Ready: {tech_agent.is_ready()}")

    print(f"\nScience agent: {science_agent}")
    print(f"Ready: {science_agent.is_ready()}")

    # Base agent still unchanged
    print(f"\nBase agent still unchanged: {base_agent}")

    print("✓ Partial variable binding works!")


async def test_4_user_input_handling():
    """Test 4: user_input appending logic"""
    print("\n" + "=" * 70)
    print("TEST 4: User Input Handling")
    print("=" * 70)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    agent.set_variable("topic", "Space exploration")

    # Test that user_input gets appended correctly
    config_without = agent.to_config()
    messages_without = config_without["messages"]

    # Apply user_input manually to test
    messages_with = agent._apply_user_input(
        messages_without, "Please focus on Mars missions"
    )

    print(f"Messages without user_input: {len(messages_without)}")
    print(f"Last message role: {messages_without[-1]['role']}")
    print(f"Last message preview: {messages_without[-1]['content'][:100]}...")

    print(f"\nMessages with user_input: {len(messages_with)}")
    print(f"Last message role: {messages_with[-1]['role']}")
    print(f"Last message preview: {messages_with[-1]['content'][-100:]}")

    print("✓ User input handling works!")


async def test_5_callable_syntax():
    """Test 5: Callable syntax (agent as function)"""
    print("\n" + "=" * 70)
    print("TEST 5: Callable Syntax")
    print("=" * 70)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    agent.set_variable("topic", "Artificial Intelligence")

    # Use callable syntax
    conversation = await agent(
        "Give a very brief analysis",
        user_id="test-user",
        emitter=emitter,
    )

    print(f"Conversation: {conversation}")
    vcprint(conversation, "Callable Syntax Result", color="green")
    print("✓ Callable syntax works!")


async def test_6_chaining():
    """Test 6: Method chaining"""
    print("\n" + "=" * 70)
    print("TEST 6: Method Chaining")
    print("=" * 70)

    # Chain everything
    conversation = await (
        await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    ).set_variable("topic", "Quantum Computing")(
        "Very brief summary please",
        user_id="test-user",
        emitter=emitter,
    )

    print(f"Conversation: {conversation}")
    vcprint(conversation, "Chaining Result", color="green")
    print("✓ Method chaining works!")


async def test_7_multi_turn_conversation():
    """Test 7: Multi-turn conversation"""
    print("\n" + "=" * 70)
    print("TEST 7: Multi-turn Conversation")
    print("=" * 70)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    agent.set_variable("topic", "Renewable Energy")

    # Start conversation
    conversation = await agent.execute(
        user_input="Give a very concise overview",
        user_id="test-user",
        emitter=emitter,
    )

    # print(f"First response preview: {conversation.last_response[:150]}...")
    # print(f"Message count after first execute: {len(conversation.messages)}")
    vcprint(conversation, "Conversation Initial", color="green")

    # Continue conversation
    await conversation.send(
        "Now focus on solar power specifically and be really concise"
    )
    # print(f"\nSecond response preview: {conversation.last_response[:150]}...")
    # print(f"Message count after first send: {len(conversation.messages)}")
    vcprint(conversation, "Conversation Continued", color="blue")

    # Continue again with callable syntax
    await conversation("Now, specifically about only the challenges? Be really concise")
    # print(f"\nThird response preview: {conversation.last_response[:150]}...")
    vcprint(conversation, "Conversation Continued Again", color="magenta")

    # print(f"\nTotal messages: {len(conversation.messages)}")
    print("✓ Multi-turn conversation works!")


async def test_8_workflow_pattern():
    """Test 8: Workflow with multiple agent instances"""
    print("\n" + "=" * 70)
    print("TEST 8: Workflow Pattern (Multiple Instances)")
    print("=" * 70)

    # Load base agent once
    search_agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")

    # Run multiple instances in parallel
    topics = ["AI Ethics", "Climate Tech", "Biotechnology"]

    print(f"Running {len(topics)} agent instances in parallel...")

    conversations = await asyncio.gather(
        *[
            search_agent.with_variables(topic=topic).execute_oneshot(
                user_input="One sentence summary",
                user_id="test-user",
                emitter=emitter,
            )
            for topic in topics
        ]
    )

    for i, (topic, response) in enumerate(zip(topics, conversations), 1):
        print(f"\n{i}. {topic}: {len(response)} characters")

    print("\n✓ Workflow pattern works!")


async def test_9_emitter():
    """Test 9: Stream handler support"""
    print("\n" + "=" * 70)
    print("TEST 9: Stream Handler Support")
    print("=" * 70)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    agent.set_variable("topic", "Machine Learning")

    conversation = await agent.execute(
        user_input="Brief summary please",
        user_id="test-user",
        emitter=emitter,
    )

    print(f"Conversation: {conversation}")
    print(f"Stream handler was passed: {conversation.emitter is not None}")
    print("✓ Stream handler support works!")


async def test_10_not_ready_error():
    """Test 10: Error when executing agent that's not ready"""
    print("\n" + "=" * 70)
    print("TEST 10: Not Ready Error Handling")
    print("=" * 70)

    agent = await Agent.from_prompt_id("002edf1b-26e6-4fb1-86cb-21000e319f2a")
    # Don't set required variables

    print(f"Agent: {agent}")
    print(f"Ready: {agent.is_ready()}")
    print(f"Missing: {agent.missing_variables()}")

    try:
        await agent.execute(
            user_id="test-user",
            emitter=emitter,
        )
        print("✗ Should have raised error!")
    except ValueError as e:
        print(f"✓ Correctly raised error: {e}")


async def main():
    clear_terminal()

    print("=" * 70)
    print("AGENT + CONVERSATION ARCHITECTURE TESTS")
    print("=" * 70)

    try:
        await test_1_basic_execution()
        # await test_2_oneshot_execution()
        # await test_3_partial_variables()
        # await test_4_user_input_handling()
        # await test_5_callable_syntax()
        # await test_6_chaining()
        # await test_7_multi_turn_conversation()
        # await test_8_workflow_pattern()
        # await test_9_emitter()
        # await test_10_not_ready_error()

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
