"""MCP server setup with tool registration"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
from typing import Any, Sequence

from app.mcp.tools import (
    snowflake_query,
    snowflake_vector_search,
    score_match,
    tts_speak,
    opt_plan,
    metrics_simulate,
    storage_put,
    storage_url,
    audit_log
)
from app.logging_config import get_logger

logger = get_logger(__name__)

# Create MCP server instance
mcp_server = Server("mad-ads-backend")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools"""
    return [
        Tool(
            name="snowflake.query",
            description="Query Snowflake for facts/metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query string"},
                    "params": {"type": "object", "description": "Query parameters"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="snowflake.vector_search",
            description="Vector search using Snowflake Cortex",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Query text"},
                    "k": {"type": "integer", "description": "Number of results", "default": 5}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="score.match",
            description="Calculate hybrid match score between content and ad",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {"type": "string", "description": "Content item ID"},
                    "ad_id": {"type": "string", "description": "Optional ad ID"},
                    "ad_text": {"type": "string", "description": "Optional ad text for direct matching"}
                },
                "required": ["content_id"]
            }
        ),
        Tool(
            name="tts.speak",
            description="Convert text to speech using ElevenLabs",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert"},
                    "voice": {"type": "string", "description": "Optional voice ID"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="opt.plan",
            description="Generate budget/media plan using optimization",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Campaign goal"},
                    "variants": {"type": "array", "items": {"type": "string"}, "description": "List of variant IDs"},
                    "channels": {"type": "array", "items": {"type": "string"}, "description": "List of channel names"},
                    "budget": {"type": "number", "description": "Total budget"}
                },
                "required": ["goal", "variants", "channels", "budget"]
            }
        ),
        Tool(
            name="metrics.simulate",
            description="Start metrics simulation for a campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string", "description": "Campaign ID to simulate"}
                },
                "required": ["campaign_id"]
            }
        ),
        Tool(
            name="storage.put",
            description="Store object in storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_data": {"type": "string", "description": "Object data (base64 encoded)"},
                    "object_key": {"type": "string", "description": "Storage key/path"}
                },
                "required": ["object_data", "object_key"]
            }
        ),
        Tool(
            name="storage.url",
            description="Get URL for stored object",
            inputSchema={
                "type": "object",
                "properties": {
                    "storage_id": {"type": "string", "description": "Storage ID"}
                },
                "required": ["storage_id"]
            }
        ),
        Tool(
            name="audit.log",
            description="Log audit event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event": {"type": "string", "description": "Event name"},
                    "payload": {"type": "object", "description": "Event payload"}
                },
                "required": ["event", "payload"]
            }
        )
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> Sequence[TextContent]:
    """Handle tool calls"""
    logger.info("mcp_tool_called", tool_name=name, arguments=arguments)
    
    try:
        if name == "snowflake.query":
            result = await snowflake_query(
                arguments.get("query", ""),
                arguments.get("params")
            )
        elif name == "snowflake.vector_search":
            result = await snowflake_vector_search(
                arguments.get("text", ""),
                arguments.get("k", 5)
            )
        elif name == "score.match":
            result = await score_match(
                arguments.get("content_id", ""),
                arguments.get("ad_id"),
                arguments.get("ad_text")
            )
        elif name == "tts.speak":
            result = await tts_speak(
                arguments.get("text", ""),
                arguments.get("voice")
            )
        elif name == "opt.plan":
            result = await opt_plan(
                arguments.get("goal", ""),
                arguments.get("variants", []),
                arguments.get("channels", []),
                arguments.get("budget", 0.0)
            )
        elif name == "metrics.simulate":
            result = await metrics_simulate(
                arguments.get("campaign_id", "")
            )
        elif name == "storage.put":
            # In real implementation, decode base64
            import base64
            object_data = base64.b64decode(arguments.get("object_data", ""))
            result = await storage_put(
                object_data,
                arguments.get("object_key", "")
            )
        elif name == "storage.url":
            result = await storage_url(
                arguments.get("storage_id", "")
            )
        elif name == "audit.log":
            await audit_log(
                arguments.get("event", ""),
                arguments.get("payload", {})
            )
            result = {"status": "logged"}
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        import json
        return [TextContent(type="text", text=json.dumps(result))]
    
    except Exception as e:
        logger.error("mcp_tool_error", tool_name=name, error=str(e), exc_info=True)
        raise


async def run_mcp_server():
    """Run MCP server (for standalone mode)"""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(run_mcp_server())

