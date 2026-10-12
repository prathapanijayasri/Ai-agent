from app.agent.memory import MemoryManager
from app.agent.state import Message

def test_memory_limit():
    memory = MemoryManager(max_messages=2)
    
    memory.add_message(Message(role="user", content="Msg 1"))
    memory.add_message(Message(role="model", content="Msg 2"))
    memory.add_message(Message(role="user", content="Msg 3"))
    
    context = memory.get_context()
    assert len(context) == 2
    assert context[0].content == "Msg 2"
    assert context[1].content == "Msg 3"
