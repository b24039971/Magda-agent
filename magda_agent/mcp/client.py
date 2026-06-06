import asyncio
from typing import Dict, Any, List, Optional
import mcp
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from magda_agent.skills.registry import SkillRegistry
import logging

class MCPClient:
    """
    Client for Model Context Protocol (MCP) servers.
    Connects to MCP servers and registers exposed tools into the Magda SkillRegistry.
    """
    def __init__(self):
        self.sessions: List[ClientSession] = []

    async def connect_and_register(self, server_params: StdioServerParameters, registry: SkillRegistry):
        """
        Connects to an MCP server via stdio and registers its tools to the SkillRegistry.
        """
        # We need to keep the process alive while the session is running
        # mcp client uses async context managers for this.
        # Since we are keeping this simple and experimental, we could create an ongoing task.
        async def run_session():
            try:
                async with stdio_client(server_params) as (read_stream, write_stream):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        self.sessions.append(session)
                        logging.info(f"Connected to MCP Server: {server_params.command}")

                        # Fetch available tools
                        tools_result = await session.list_tools()
                        if hasattr(tools_result, 'tools'):
                            for tool in tools_result.tools:
                                # Wrap the tool call.
                                # Capture 'session' and 'tool.name' in closure.
                                def create_tool_wrapper(sess: ClientSession, tool_name: str):
                                    async def mcp_tool_wrapper(**kwargs) -> Any:
                                        result = await sess.call_tool(tool_name, arguments=kwargs)
                                        # Parse and format result back
                                        if hasattr(result, 'content'):
                                            # Content is usually a list of text or images
                                            texts = [c.text for c in result.content if getattr(c, 'type', '') == 'text']
                                            return "\n".join(texts)
                                        return str(result)
                                    return mcp_tool_wrapper

                                func = create_tool_wrapper(session, tool.name)
                                registry.register_skill(
                                    name=tool.name,
                                    func=func,
                                    description=tool.description or f"MCP tool: {tool.name}"
                                )
                                logging.info(f"Registered MCP tool: {tool.name}")

                        # Wait forever to keep streams open
                        while True:
                            await asyncio.sleep(3600)
            except Exception as e:
                logging.error(f"Error in MCP session: {e}")

        # In a real app we'd manage these background tasks safely
        asyncio.create_task(run_session())
