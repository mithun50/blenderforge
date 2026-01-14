# AI Client Configuration

BlenderForge works with any AI assistant that supports the Model Context Protocol (MCP). This guide covers configuration for popular AI clients.

---

## Overview

All MCP clients use a similar configuration pattern:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

The key differences are **where** this configuration goes for each client.

---

## Claude Desktop

**Developer**: Anthropic
**Platform**: macOS, Windows, Linux

### Configuration File Location

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

### Configuration

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### Steps

1. Create or edit the config file at the path above
2. Add the configuration
3. Restart Claude Desktop
4. BlenderForge tools will appear in the tools menu

---

## Claude Code

**Developer**: Anthropic
**Platform**: CLI tool

### Configuration

Claude Code uses the same configuration as Claude Desktop. Create or edit the config file:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### Steps

1. Create the config file in the appropriate location for your OS
2. Restart Claude Code
3. BlenderForge tools will be available

---

## ChatGPT Desktop

**Developer**: OpenAI
**Platform**: macOS, Windows

### Configuration Steps

1. Open ChatGPT Desktop
2. Enable **Developer Mode**:
   - Go to `Settings` → `Developer Mode`
   - Toggle it ON
3. Add the connector:
   - Go to `Settings` → `Connectors`
   - Click **Add Connector**
4. Configure the connector:
   - **Name**: `blenderforge`
   - **Command**: `blenderforge`
5. Save and restart ChatGPT

### Notes

- Developer Mode is required for MCP support
- Connectors appear in the chat interface once configured

---

## Google Antigravity

**Developer**: Google
**Platform**: Web-based AI coding platform

### Configuration

Add to your Antigravity MCP configuration:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### Steps

1. Open Antigravity settings
2. Navigate to MCP configuration
3. Add BlenderForge as a server
4. Save and refresh

---

## VS Code + GitHub Copilot

**Developer**: Microsoft
**Platform**: VS Code extension

### Configuration File

Edit your VS Code `settings.json`:

- **Open Settings**: `Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"

### Configuration

```json
{
  "github.copilot.chat.mcp.servers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### Steps

1. Install the GitHub Copilot extension
2. Add the configuration to `settings.json`
3. Reload VS Code
4. BlenderForge will be available in Copilot chat

---

## Cursor IDE

**Developer**: Cursor
**Platform**: macOS, Windows, Linux

### Configuration Steps

1. Open Cursor
2. Go to `Settings` → `MCP`
3. Add the configuration:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

4. Save and restart Cursor

---

## Windsurf

**Developer**: Codeium
**Platform**: macOS, Windows, Linux

### Configuration

Add to your Windsurf MCP configuration:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### Steps

1. Open Windsurf settings
2. Navigate to MCP servers configuration
3. Add BlenderForge
4. Restart Windsurf

---

## Zed Editor

**Developer**: Zed Industries
**Platform**: macOS, Linux

### Configuration

Edit your Zed settings file:

```json
{
  "mcp_servers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### Steps

1. Open Zed settings (`Cmd+,` on macOS)
2. Add the MCP server configuration
3. Save and restart Zed

---

## Continue.dev

**Developer**: Continue
**Platform**: VS Code extension

### Configuration File

Edit `~/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "name": "blenderforge",
        "command": "blenderforge"
      }
    ]
  }
}
```

### Steps

1. Install the Continue extension in VS Code
2. Create or edit `~/.continue/config.json`
3. Add the configuration
4. Reload VS Code

---

## Custom MCP Clients

If you're using a different MCP client, the general pattern is:

1. Find the MCP configuration section
2. Add a new server with:
   - **Name**: `blenderforge`
   - **Command**: `blenderforge`
   - **Transport**: `stdio` (default for most clients)

### Python Example

```python
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def connect():
    params = StdioServerParameters(
        command="blenderforge",
        args=[]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Use BlenderForge tools
            tools = await session.list_tools()
            print(tools)
```

---

## Verifying Connection

After configuring your AI client, verify the connection:

1. **Ensure Blender is running** with the addon enabled
2. **Start the BlenderForge server** in Blender's sidebar panel
3. **Ask your AI**: "What tools do you have for Blender?"

The AI should list BlenderForge tools like:
- `get_scene_info`
- `get_object_info`
- `execute_blender_code`
- `get_viewport_screenshot`

---

## Troubleshooting

### "Tools not appearing"

1. Restart your AI client after adding the configuration
2. Check the config file path is correct for your OS
3. Validate JSON syntax (use a JSON validator)
4. Check AI client logs for MCP errors

### "Connection refused"

1. Ensure Blender is running
2. Ensure the addon is enabled
3. Click "Connect to MCP server" in Blender's BlenderForge panel
4. Check the port number matches (default: 9876)

See [Troubleshooting](troubleshooting.md) for more solutions.
