import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from magda_agent.skills.registry import SkillRegistry
from magda_agent.mcp.client import MCPClient
from mcp.client.stdio import StdioServerParameters

@pytest.fixture
def mock_mcp_client_session():
    with patch("magda_agent.mcp.client.ClientSession") as mock_session_cls, \
         patch("magda_agent.mcp.client.stdio_client") as mock_stdio_client:

        # Setup mock stdio client context manager
        mock_stdio_cm = AsyncMock()
        mock_stdio_cm.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_stdio_client.return_value = mock_stdio_cm

        # Setup mock session
        mock_session_inst = AsyncMock()
        mock_session_inst.initialize = AsyncMock()

        # Setup tools result
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test MCP tool"

        mock_tools_result = MagicMock()
        mock_tools_result.tools = [mock_tool]
        mock_session_inst.list_tools = AsyncMock(return_value=mock_tools_result)

        # Setup call tool result
        mock_call_result = MagicMock()
        mock_content = MagicMock()
        mock_content.type = "text"
        mock_content.text = "MCP execution success"
        mock_call_result.content = [mock_content]
        mock_session_inst.call_tool = AsyncMock(return_value=mock_call_result)

        mock_session_cm = AsyncMock()
        mock_session_cm.__aenter__.return_value = mock_session_inst
        mock_session_cls.return_value = mock_session_cm

        yield mock_session_inst

@pytest.mark.asyncio
async def test_mcp_connect_and_register(mock_mcp_client_session):
    registry = SkillRegistry()
    client = MCPClient()
    server_params = StdioServerParameters(command="test_cmd", args=[])

    # Add a small timeout so the infinite loop doesn't block forever if running sequentially
    task = asyncio.create_task(client.connect_and_register(server_params, registry))

    # Give it a moment to run the registration task
    await asyncio.sleep(0.1)

    # Verify session initialized and list_tools called
    mock_mcp_client_session.initialize.assert_awaited_once()
    mock_mcp_client_session.list_tools.assert_awaited_once()

    # Verify tool was registered in registry
    assert "test_tool" in registry.skills
    assert registry.descriptions["test_tool"] == "A test MCP tool"

    # Execute tool. Since execute_skill detects an event loop and returns a Task, we can await it.
    result_task = registry.execute_skill("test_tool", param="value")
    assert asyncio.isfuture(result_task) or isinstance(result_task, asyncio.Task)

    result = await result_task

    mock_mcp_client_session.call_tool.assert_awaited_once_with("test_tool", arguments={"param": "value"})
    assert result == "MCP execution success"

    # Cleanup the infinite loop task
    task.cancel()
