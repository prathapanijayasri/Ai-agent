import os
import pytest
from app.agent.executor import AgentExecutor

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY")
def test_agent_calculator_integration():
    executor = AgentExecutor()
    response = executor.process_message("What is 15 * 3?")
    assert "45" in response
    
    # Check that tool was called
    tool_messages = [m for m in executor.state.messages if m.role == "tool"]
    assert len(tool_messages) > 0
    assert "45" in tool_messages[0].content

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Requires GOOGLE_API_KEY")
def test_agent_conversation_memory():
    executor = AgentExecutor()
    response1 = executor.process_message("Hi, my name is Alice.")
    response2 = executor.process_message("What is my name?")
    assert "Alice" in response2
