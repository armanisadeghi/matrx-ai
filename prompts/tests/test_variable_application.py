"""
Quick test to verify variable application works correctly
"""
import asyncio
from prompts.agent import Agent
from config.unified_config import UnifiedConfig
from prompts.variables import AgentVariable


async def test_variable_application():
    """Test that variables are properly applied to config"""
    
    # Create a simple config with variable placeholder
    config_dict = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Tell me about {{topic}} in a concise way."
            }
        ],
        "system_instruction": "You are an expert on {{topic}}. Be helpful and concise."
    }
    
    # Create agent
    agent = Agent.from_dict(
        config_dict,
        variable_defaults={
            "topic": AgentVariable(name="topic", required=True)
        }
    )
    
    # Set variable
    agent.set_variable("topic", "AI Safety")
    
    print("Before applying variables:")
    print(f"System instruction: {agent.config.system_instruction}")
    print(f"First message: {agent.config.messages[0].content[0].text}")
    print()
    
    # Apply variables
    agent.apply_variables()
    
    print("After applying variables:")
    print(f"System instruction: {agent.config.system_instruction}")
    print(f"First message: {agent.config.messages[0].content[0].text}")
    print()
    
    # Verify replacement worked
    assert "{{topic}}" not in agent.config.system_instruction
    assert "AI Safety" in agent.config.system_instruction
    assert "{{topic}}" not in agent.config.messages[0].content[0].text
    assert "AI Safety" in agent.config.messages[0].content[0].text
    
    print("✓ Variables applied correctly!")
    
    # Test that applying again doesn't break anything
    agent.apply_variables()
    print("✓ Re-applying variables is safe (no-op)")
    
    # Test with_variables convenience method
    agent2 = Agent.from_dict(
        config_dict,
        variable_defaults={
            "topic": AgentVariable(name="topic", required=True)
        }
    )
    agent2.with_variables(topic="Machine Learning")
    
    assert "Machine Learning" in agent2.config.system_instruction
    assert "{{topic}}" not in agent2.config.system_instruction
    print("✓ with_variables() works correctly!")
    
    print("\n✅ All variable application tests passed!")

if __name__ == "__main__":
    asyncio.run(test_variable_application())
