#!/usr/bin/env python3
"""
MCP Server for System Operations
Provides tools for command execution, file operations, and network management
"""

import asyncio
import json
import subprocess
import os
from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create server instance
app = Server("system-ops-mcp")

# Track command history
command_history = []

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="execute_command",
            description="Execute a bash command on the system. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory (optional, defaults to current)",
                        "default": os.getcwd()
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="network_info",
            description="Get network interface information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="configure_network",
            description="Configure network interface using nmcli",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface": {
                        "type": "string",
                        "description": "Network interface name (e.g., eth0, wlan0)"
                    },
                    "setting_type": {
                        "type": "string",
                        "description": "Type of setting: static_ip, dns, dhcp",
                        "enum": ["static_ip", "dns", "dhcp"]
                    },
                    "value": {
                        "type": "string",
                        "description": "Value for the setting (IP address, DNS server, etc.)"
                    }
                },
                "required": ["interface", "setting_type"]
            }
        ),
        Tool(
            name="system_status",
            description="Get system status information",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "description": "Component to check: cpu, memory, disk, network, docker, kubernetes",
                        "enum": ["cpu", "memory", "disk", "network", "docker", "kubernetes", "all"]
                    }
                },
                "required": ["component"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "execute_command":
            command = arguments["command"]
            working_dir = arguments.get("working_dir", os.getcwd())
            
            # Log command
            command_history.append(command)
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(output, indent=2)
            )]
            
        elif name == "read_file":
            path = arguments["path"]
            with open(path, 'r') as f:
                content = f.read()
            return [TextContent(type="text", text=content)]
            
        elif name == "write_file":
            path = arguments["path"]
            content = arguments["content"]
            
            # Create directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w') as f:
                f.write(content)
            
            return [TextContent(
                type="text",
                text=f"Successfully wrote to {path}"
            )]
            
        elif name == "network_info":
            result = subprocess.run(
                ["nmcli", "device", "status"],
                capture_output=True,
                text=True
            )
            return [TextContent(type="text", text=result.stdout)]
            
        elif name == "configure_network":
            interface = arguments["interface"]
            setting_type = arguments["setting_type"]
            value = arguments.get("value", "")
            
            if setting_type == "dhcp":
                cmd = f"nmcli device modify {interface} ipv4.method auto"
            elif setting_type == "static_ip":
                cmd = f"nmcli device modify {interface} ipv4.method manual ipv4.addresses {value}"
            elif setting_type == "dns":
                cmd = f"nmcli device modify {interface} ipv4.dns {value}"
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown setting type: {setting_type}"
                )]
            
            return [TextContent(
                type="text",
                text=f"Generated command: {cmd}\n\nThis command needs root privileges."
            )]
            
        elif name == "system_status":
            component = arguments["component"]
            outputs = []
            
            if component in ["cpu", "all"]:
                result = subprocess.run(["top", "-bn1"], capture_output=True, text=True)
                outputs.append(f"CPU:\n{result.stdout.split(chr(10))[2]}")
            
            if component in ["memory", "all"]:
                result = subprocess.run(["free", "-h"], capture_output=True, text=True)
                outputs.append(f"Memory:\n{result.stdout}")
            
            if component in ["disk", "all"]:
                result = subprocess.run(["df", "-h"], capture_output=True, text=True)
                outputs.append(f"Disk:\n{result.stdout}")
            
            if component in ["docker", "all"]:
                result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
                outputs.append(f"Docker:\n{result.stdout}")
            
            if component in ["kubernetes", "all"]:
                result = subprocess.run(["kubectl", "get", "pods"], capture_output=True, text=True)
                outputs.append(f"Kubernetes:\n{result.stdout}")
            
            return [TextContent(type="text", text="\n\n".join(outputs))]
            
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
