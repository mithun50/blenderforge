# Architecture

Technical overview of how BlenderForge works internally.

---

## System Overview

BlenderForge consists of three main components that communicate over different protocols:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AI ASSISTANT                               │
│                    (Claude, ChatGPT, etc.)                          │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ MCP Protocol (stdio)
                                  │ JSON-RPC 2.0 messages
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BLENDERFORGE SERVER                            │
│                     (Python MCP Server)                             │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │   FastMCP   │  │   Tool      │  │    External APIs            │ │
│  │   Runtime   │  │   Registry  │  │ (PolyHaven, Sketchfab, etc) │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ TCP Socket (localhost:9876)
                                  │ JSON messages
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BLENDER + ADDON                              │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │   Socket    │  │   Command   │  │    Blender Python API       │ │
│  │   Server    │  │   Executor  │  │         (bpy)               │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. BlenderForge Server

The MCP server that bridges AI assistants and Blender.

**Location**: `src/blenderforge/server.py`

**Technology Stack**:
- **FastMCP**: High-level MCP server framework
- **Python 3.10+**: Runtime environment
- **asyncio**: Asynchronous I/O for handling requests

**Key Responsibilities**:
- Register and expose MCP tools
- Handle MCP protocol communication
- Route commands to Blender
- Integrate with external APIs (PolyHaven, Sketchfab, etc.)

```python
# Simplified server structure
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("blenderforge")

@mcp.tool()
async def get_scene_info() -> dict:
    """Get information about the Blender scene."""
    return await send_to_blender({"command": "get_scene_info"})

def main():
    mcp.run()  # Starts stdio transport
```

### 2. Blender Addon

The Blender-side component that executes commands.

**Location**: `addon.py`

**Technology Stack**:
- **Blender Python API (bpy)**: Blender manipulation
- **Socket Server**: TCP communication
- **Threading**: Background socket listener

**Key Responsibilities**:
- Listen for incoming connections
- Parse and validate commands
- Execute Python code in Blender's context
- Return results to the MCP server

```python
# Simplified addon structure
import bpy
import socket
import json

class BlenderForgeServer:
    def __init__(self, port=9876):
        self.socket = socket.socket()
        self.socket.bind(('localhost', port))

    def handle_command(self, command):
        if command['type'] == 'get_scene_info':
            return {
                'name': bpy.context.scene.name,
                'objects': [obj.name for obj in bpy.data.objects]
            }
        elif command['type'] == 'execute_code':
            exec(command['code'])
            return {'success': True}
```

### 3. Communication Protocol

**MCP Layer (AI ↔ Server)**:
- Transport: stdio (standard input/output)
- Protocol: JSON-RPC 2.0
- Messages: Tool calls and responses

**Socket Layer (Server ↔ Blender)**:
- Transport: TCP socket
- Host: localhost
- Port: 9876 (default)
- Protocol: JSON messages with length prefix

---

## Data Flow

### Tool Execution Flow

```
1. AI sends tool call
   └─→ {"method": "tools/call", "params": {"name": "get_scene_info"}}

2. MCP server receives and routes
   └─→ FastMCP dispatches to registered tool handler

3. Tool handler prepares Blender command
   └─→ {"command": "get_scene_info"}

4. Server sends to Blender via socket
   └─→ TCP connection to localhost:9876

5. Addon receives and executes
   └─→ Query bpy.data.objects, etc.

6. Addon returns result
   └─→ {"name": "Scene", "objects": [...]}

7. Server formats MCP response
   └─→ {"result": {"name": "Scene", ...}}

8. AI receives result
   └─→ Processes and responds to user
```

### External API Flow (e.g., PolyHaven)

```
1. AI requests texture download
   └─→ download_polyhaven_asset("wood_floor_deck")

2. Server queries PolyHaven API
   └─→ GET https://api.polyhaven.com/files/wood_floor_deck

3. Server downloads texture files
   └─→ Saves to temporary directory

4. Server sends import command to Blender
   └─→ {"command": "import_texture", "path": "/tmp/..."}

5. Addon imports and sets up material
   └─→ bpy.ops.image.open(), material nodes setup

6. Result returned to AI
   └─→ {"success": true, "material_name": "wood_floor_deck"}
```

---

## Project Structure

```
blenderforge/
├── src/
│   └── blenderforge/
│       ├── __init__.py      # Package initialization
│       ├── server.py        # Main MCP server
│       ├── config.py        # Configuration management
│       ├── telemetry.py     # Usage telemetry
│       └── telemetry_decorator.py  # Telemetry decorator
├── addon.py                 # Blender addon (standalone)
├── tests/
│   ├── conftest.py         # Test configuration
│   ├── test_config.py      # Config tests
│   ├── test_server.py      # Server tests
│   └── test_telemetry.py   # Telemetry tests
├── docs/                    # Documentation
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI pipeline
│       └── release.yml     # Release pipeline
├── pyproject.toml          # Project configuration
└── README.md               # Main documentation
```

---

## MCP Protocol Details

### Transport

BlenderForge uses **stdio transport** - the most common MCP transport method:

- Server reads JSON-RPC messages from stdin
- Server writes responses to stdout
- AI clients spawn the server as a subprocess
- Simple, secure, and widely supported

### Message Format

```json
// Tool list request
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

// Tool list response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_scene_info",
        "description": "Get information about the Blender scene",
        "inputSchema": {...}
      }
    ]
  }
}

// Tool call request
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "execute_blender_code",
    "arguments": {"code": "bpy.ops.mesh.primitive_cube_add()"}
  }
}

// Tool call response
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{"type": "text", "text": "{\"success\": true}"}]
  }
}
```

---

## Socket Protocol Details

### Connection

1. Addon starts socket server on startup
2. MCP server connects when tool is called
3. Connection persists for session duration
4. Reconnects automatically if connection drops

### Message Format

Messages are JSON with a 4-byte length prefix:

```
[4 bytes: message length (big-endian)] [JSON message bytes]
```

Example:
```python
def send_message(sock, data):
    message = json.dumps(data).encode('utf-8')
    length = len(message).to_bytes(4, 'big')
    sock.sendall(length + message)

def receive_message(sock):
    length_bytes = sock.recv(4)
    length = int.from_bytes(length_bytes, 'big')
    message = sock.recv(length)
    return json.loads(message.decode('utf-8'))
```

---

## Telemetry System

BlenderForge includes optional, anonymous telemetry.

### What's Collected

- Tool usage counts (which tools are called)
- Error rates (how often tools fail)
- Session duration
- Anonymized session IDs

### What's NOT Collected

- User prompts or conversations
- Blender file contents
- Personal information
- IP addresses

### Implementation

```python
# Decorator-based telemetry
@telemetry.track
async def get_scene_info():
    # Telemetry automatically records:
    # - Tool name
    # - Execution time
    # - Success/failure
    return await execute_command(...)
```

### Disabling Telemetry

```bash
export DISABLE_TELEMETRY=true
```

Or in the config file:
```python
# src/blenderforge/config.local.py
telemetry_config = TelemetryConfig(enabled=False)
```

---

## Security Considerations

### Code Execution

The `execute_blender_code` tool runs arbitrary Python. Mitigations:

1. **Local-only connection**: Socket binds to localhost only
2. **User consent**: AI assistants ask before running code
3. **No network exposure**: MCP uses stdio, not network ports

### API Keys

External service keys are stored in Blender preferences:

1. **Not in code**: Keys entered via UI, stored in Blender prefs
2. **Not transmitted**: Keys only used for direct API calls
3. **Optional**: Core features work without any keys

### Socket Security

1. Binds to `localhost` only - not accessible from network
2. No authentication (local trust model)
3. Port can be changed if 9876 is untrusted

---

## Extending BlenderForge

### Adding New Tools

1. Add tool function in `server.py`:

```python
@mcp.tool()
async def my_new_tool(param: str) -> dict:
    """Description of what the tool does."""
    return await send_to_blender({
        "command": "my_command",
        "param": param
    })
```

2. Add handler in `addon.py`:

```python
def handle_my_command(self, params):
    # Execute in Blender
    result = do_something(params['param'])
    return {"success": True, "result": result}
```

### Adding External APIs

1. Create API client module
2. Add configuration options to addon preferences
3. Add tools that use the API
4. Document in asset-integrations.md
