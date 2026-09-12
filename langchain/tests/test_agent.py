from agent import create_agent_executor


def test_create_agent_executor():
    executor = create_agent_executor()
    assert executor is not None
    assert len(executor.tools) == 12
