# AI Client Configuration

BlenderForge works with any AI assistant that supports the Model Context Protocol (MCP). This comprehensive guide covers detailed configuration for all popular AI clients.

---

## Table of Contents

1. [Overview](#overview)
2. [Claude Desktop](#claude-desktop)
3. [Claude Code](#claude-code)
4. [ChatGPT Desktop](#chatgpt-desktop)
5. [VS Code + GitHub Copilot](#vs-code--github-copilot)
6. [Cursor IDE](#cursor-ide)
7. [Windsurf (Codeium)](#windsurf-codeium)
8. [Zed Editor](#zed-editor)
9. [Continue.dev](#continuedev)
10. [Google Antigravity](#google-antigravity)
11. [Custom MCP Clients](#custom-mcp-clients)
12. [Verifying Connection](#verifying-connection)
13. [Troubleshooting](#troubleshooting)

---

## Overview

### What is MCP?

The **Model Context Protocol (MCP)** is an open standard that defines how applications share context with large language models (LLMs). Think of it as a "USB-C port for AI applications" - it provides a standardized way to connect AI models to external tools and data sources.

**Key Concepts:**
- **MCP Server**: Exposes tools and resources (BlenderForge is an MCP server)
- **MCP Client**: AI applications that connect to servers (Claude, ChatGPT, etc.)
- **Transport**: Communication method (stdio for local, HTTP for remote)
- **Tools**: Functions the AI can invoke (like `get_scene_info`, `execute_blender_code`)

### Universal Configuration Pattern

All MCP clients use a similar JSON configuration:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

The differences are **where** this configuration goes and **what format** each client expects.

### Prerequisites

Before configuring any AI client:

1. **Install BlenderForge**: `pip install blenderforge`
2. **Verify installation**: `blenderforge --version`
3. **Ensure command is in PATH**: `which blenderforge` (macOS/Linux) or `where blenderforge` (Windows)

---

## Claude Desktop

**Developer**: Anthropic
**Platform**: macOS, Windows, Linux
**MCP Support**: Full native support
**Documentation**: [Claude MCP Guide](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)

### Configuration File Location

| Operating System | Path |
|------------------|------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

### Step-by-Step Setup

#### Step 1: Locate or Create the Configuration File

**macOS:**
```bash
# Create directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude

# Open or create the config file
open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows (PowerShell):**
```powershell
# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"

# Open or create the config file
notepad "$env:APPDATA\Claude\claude_desktop_config.json"
```

**Linux:**
```bash
# Create directory if it doesn't exist
mkdir -p ~/.config/Claude

# Open or create the config file
nano ~/.config/Claude/claude_desktop_config.json
```

#### Step 2: Add BlenderForge Configuration

Add the following JSON to your config file:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

**If you have other MCP servers**, add BlenderForge to the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/Documents"]
    },
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

#### Step 3: Restart Claude Desktop

1. **Quit Claude Desktop completely** (not just close the window)
   - macOS: `Cmd+Q` or Claude menu → Quit
   - Windows: Right-click system tray icon → Exit
2. **Reopen Claude Desktop**
3. **Look for the MCP indicator** in the bottom-right corner of the chat input

#### Step 4: Verify Tools are Available

In Claude Desktop, you should see a hammer icon or "Tools" indicator. Click it to see available BlenderForge tools like:
- `get_scene_info`
- `get_object_info`
- `execute_blender_code`
- `get_viewport_screenshot`

### Alternative: Desktop Extensions (Newer Method)

Claude Desktop now supports **Desktop Extensions** for easier MCP server management:

1. Navigate to **Settings → Extensions**
2. Click **"Browse extensions"**
3. Search for MCP servers and click to install

*Note: BlenderForge may need to be added manually until it's available in the extension marketplace.*

---

## Claude Code

**Developer**: Anthropic
**Platform**: CLI tool (all platforms)
**MCP Support**: Full native support
**Documentation**: [Claude Code MCP Configuration](https://scottspence.com/posts/configuring-mcp-tools-in-claude-code)

### Configuration

Claude Code uses the same configuration file as Claude Desktop. The configuration location depends on your operating system (see Claude Desktop section above).

### Step-by-Step Setup

#### Step 1: Create/Edit Configuration

```bash
# macOS/Linux
mkdir -p ~/.config/Claude
cat > ~/.config/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
EOF
```

#### Step 2: Restart Claude Code

```bash
# Exit current session and restart
exit
claude
```

#### Step 3: Verify

```bash
# In Claude Code, ask:
"What MCP tools do you have available?"
```

---

## ChatGPT Desktop

**Developer**: OpenAI
**Platform**: macOS, Windows, Web
**MCP Support**: Full support with Developer Mode
**Documentation**: [ChatGPT Developer Mode](https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta)

### Requirements

- **ChatGPT Plus, Pro, Business, Enterprise, or Education** subscription
- **Developer Mode** enabled

### Step-by-Step Setup

#### Step 1: Enable Developer Mode

1. Open **ChatGPT Desktop** or web app
2. Go to **Settings** (gear icon)
3. Navigate to **Connectors → Advanced**
4. Toggle **Developer Mode** to ON

*For Business/Enterprise users:*
- Go to **Workspace Settings → Permissions & Roles**
- Enable **Developer mode / Create custom MCP connectors**

#### Step 2: Create a Custom Connector

1. Go to **Settings → Connectors → Create**
2. Fill in the connector details:

| Field | Value |
|-------|-------|
| **Connector Name** | `BlenderForge` |
| **Description** | `Control Blender through natural language. Create 3D scenes, materials, and animations.` |
| **Command** | `blenderforge` |
| **Transport** | `stdio` |

3. Click **Save**

#### Step 3: Use Developer Mode in Chat

1. Open a new chat
2. Click the **Plus menu** (or model selector)
3. Select **Developer mode**
4. Toggle **BlenderForge** connector ON

*Note: The input field border will turn orange, indicating Developer Mode is active.*

#### Step 4: Security Considerations

- Custom MCP servers are **third-party services** not verified by OpenAI
- Developer Mode allows **read and write operations**
- ChatGPT will show **confirmation modals** for write actions
- Report malicious servers to security@openai.com

---

## VS Code + GitHub Copilot

**Developer**: Microsoft/GitHub
**Platform**: VS Code extension
**MCP Support**: Generally available (VS Code 1.99+)
**Documentation**: [VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)

### Requirements

- **VS Code 1.99 or later**
- **GitHub Copilot extension** installed
- MCP enabled via `chat.mcp.enabled` setting (enabled by default)

### Step-by-Step Setup

#### Method 1: Command Palette (Recommended)

1. Open VS Code
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
3. Type **"MCP: Add Server"** and select it
4. Choose **"Add User Server"** (global) or **"Add Workspace Server"** (project-specific)
5. Enter the configuration:

```json
{
  "blenderforge": {
    "command": "blenderforge"
  }
}
```

#### Method 2: Manual Configuration

**Global Configuration** (applies to all projects):

1. Run command: **"MCP: Open User Configuration"**
2. This opens `~/.vscode/mcp.json`
3. Add BlenderForge:

```json
{
  "servers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

**Workspace Configuration** (project-specific):

1. Create `.vscode/mcp.json` in your project root
2. Add the configuration:

```json
{
  "servers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

#### Step 3: Start the Server

1. Open the `.vscode/mcp.json` file
2. Click the **"Start"** button that appears at the top
3. Or run command: **"MCP: Start Server"**

#### Step 4: Use in Agent Mode

1. Open **GitHub Copilot Chat** panel
2. Select **Agent Mode** (not Chat mode)
3. Ask: "List my Blender scene objects"

### Enterprise Considerations

- Enterprises can control MCP usage via the **"MCP servers in Copilot"** policy
- Policy is **disabled by default** for enterprise accounts
- Admins can whitelist specific MCP servers

---

## Cursor IDE

**Developer**: Cursor
**Platform**: macOS, Windows, Linux
**MCP Support**: Full native support
**Documentation**: [Cursor MCP Docs](https://cursor.com/docs/context/mcp)

### Configuration File Locations

| Scope | Location |
|-------|----------|
| **Global** (all projects) | `~/.cursor/mcp.json` |
| **Local** (current project) | `.cursor/mcp.json` |

### Step-by-Step Setup

#### Method 1: GUI Setup

1. Open Cursor
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
3. Type **"MCP"** and select **"View: Open MCP Settings"**
4. Click **Tools & Integrations** in settings navigation
5. Under **MCP Tools**, click **New MCP Server**
6. Cursor creates an `mcp.json` file - add BlenderForge configuration

#### Method 2: Manual Configuration

**Global Configuration:**

```bash
# Create config directory
mkdir -p ~/.cursor

# Create/edit config file
cat > ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
EOF
```

**Project-specific Configuration:**

```bash
# In your project directory
mkdir -p .cursor

cat > .cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
EOF
```

#### Step 3: Restart Cursor

Close and reopen Cursor, or reload the window.

#### Step 4: Use MCP Tools

1. Open the **AI pane/chat panel**
2. Select **Agent mode**
3. Cursor will prompt for tool approval each time (or enable **Yolo mode** for auto-approval)

### Supported Transport Types

Cursor supports:
- **Local Stdio**: Runs on your machine, streams via stdin/stdout
- **Streamable HTTP**: Remote server handling multiple connections

---

## Windsurf (Codeium)

**Developer**: Codeium
**Platform**: macOS, Windows, Linux
**MCP Support**: Full native support (Cascade integration)
**Documentation**: [Windsurf MCP Guide](https://docs.windsurf.com/windsurf/cascade/mcp)

### Configuration File Location

| Operating System | Path |
|------------------|------|
| **macOS/Linux** | `~/.codeium/windsurf/mcp_config.json` |
| **Windows** | `%USERPROFILE%\.codeium\windsurf\mcp_config.json` |

### Step-by-Step Setup

#### Method 1: MCP Marketplace

1. Open Windsurf
2. Click the **MCPs icon** in the top-right menu of the Cascade panel
3. Browse the marketplace for available servers
4. For servers not in marketplace, use manual configuration

#### Method 2: Settings UI

1. Press `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux) to open Settings
2. Scroll to **"Plugins (MCP servers)"** under Cascade
3. Add BlenderForge configuration

#### Method 3: Manual Configuration

```bash
# Create directory
mkdir -p ~/.codeium/windsurf

# Create config file
cat > ~/.codeium/windsurf/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
EOF
```

#### Step 3: Verify Setup

1. Go to **Cursor Settings → MCP**
2. BlenderForge should appear as a registered MCP server
3. Check the toggle to enable it

### Important Limits

- Cascade has a limit of **100 total tools** at any time
- You can toggle individual tools on/off in MCP settings
- Check logs at `~/.codeium/windsurf/logs` for troubleshooting

### Team/Enterprise Controls

- By default, team members can configure their own MCP servers
- Admins can whitelist specific servers (blocks all non-whitelisted servers)

---

## Zed Editor

**Developer**: Zed Industries
**Platform**: macOS, Linux
**MCP Support**: Native support via `context_servers`
**Documentation**: [Zed MCP Docs](https://zed.dev/docs/assistant/model-context-protocol)

### Configuration

Zed uses the `context_servers` key in its settings.

### Step-by-Step Setup

#### Step 1: Open Zed Settings

Press `Cmd+,` to open Zed settings (JSON format).

#### Step 2: Add BlenderForge Configuration

```json
{
  "context_servers": {
    "blenderforge": {
      "command": {
        "path": "blenderforge",
        "args": [],
        "env": {}
      }
    }
  }
}
```

#### Alternative: Extension-based Configuration

Some MCP servers are available as Zed extensions:

1. Open Command Palette (`Cmd+Shift+P`)
2. Search for **"zed: extensions"**
3. Browse available MCP server extensions

### Current Limitations

- Only **prompts** are supported (shown under `/` command)
- Only **one prompt argument** is supported per prompt
- HTTP-based MCP servers have limited support

### Debugging Tips

1. Test your MCP server with: `npx @modelcontextprotocol/inspector`
2. Check server status in the **Agent Panel settings**
3. Write logs to `stderr` - Zed surfaces these for debugging

---

## Continue.dev

**Developer**: Continue
**Platform**: VS Code extension
**MCP Support**: Full support in Agent mode
**Documentation**: [Continue MCP Guide](https://docs.continue.dev/customize/deep-dives/mcp)

### Configuration Methods

Continue.dev supports two configuration approaches:

1. **Standalone YAML files** in `.continue/mcpServers/` directory
2. **JSON config files** copied from other tools (Claude Desktop, Cursor, etc.)

### Step-by-Step Setup

#### Method 1: YAML Configuration (Recommended)

1. Create the mcpServers directory:

```bash
mkdir -p .continue/mcpServers
```

2. Create a YAML file for BlenderForge:

```yaml
# .continue/mcpServers/blenderforge.yaml
name: BlenderForge MCP Server
version: 0.0.1
schema: v1
mcpServers:
  - name: blenderforge
    command: blenderforge
    args: []
```

#### Method 2: JSON Configuration (Compatible with other tools)

1. Create the mcpServers directory:

```bash
mkdir -p .continue/mcpServers
```

2. Copy a JSON config file:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

Save as `.continue/mcpServers/blenderforge.json`

### Important Notes

- MCP can **only be used in Agent mode** in Continue.dev
- Standalone YAML files require metadata fields: `name`, `version`, `schema`
- Continue.dev auto-detects config files in the `.continue/mcpServers/` directory

---

## Google Antigravity

**Developer**: Google
**Platform**: Web-based AI coding platform
**MCP Support**: Native support

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
2. Navigate to MCP configuration section
3. Add BlenderForge as a server
4. Save and refresh

---

## Custom MCP Clients

For any other MCP-compatible client, the general pattern is:

### Configuration Template

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "args": [],
      "env": {}
    }
  }
}
```

### Python Client Example

```python
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def connect_to_blenderforge():
    """Connect to BlenderForge MCP server."""
    params = StdioServerParameters(
        command="blenderforge",
        args=[]
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call a tool
            result = await session.call_tool("get_scene_info", {})
            print(f"Scene info: {result}")

# Run the client
import asyncio
asyncio.run(connect_to_blenderforge())
```

### TypeScript Client Example

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  const transport = new StdioClientTransport({
    command: "blenderforge",
    args: [],
  });

  const client = new Client({
    name: "blenderforge-client",
    version: "1.0.0",
  }, {
    capabilities: {}
  });

  await client.connect(transport);

  // List tools
  const tools = await client.listTools();
  console.log("Available tools:", tools);

  // Call a tool
  const result = await client.callTool({
    name: "get_scene_info",
    arguments: {}
  });
  console.log("Result:", result);
}

main().catch(console.error);
```

---

## Verifying Connection

After configuring your AI client, verify the connection works:

### Step 1: Ensure Blender is Running

1. Open Blender
2. Ensure the BlenderForge addon is enabled
3. Press `N` to open the sidebar
4. Go to the **BlenderForge** tab
5. Click **"Connect to MCP server"**
6. Status should show **"Connected"**

### Step 2: Verify in AI Client

Ask your AI assistant any of these questions:

```
"What BlenderForge tools do you have available?"
"What objects are in my Blender scene?"
"Take a screenshot of my Blender viewport"
```

### Expected Tools

The AI should list tools including:
- `get_scene_info` - Query scene information
- `get_object_info` - Get object details
- `execute_blender_code` - Run Python in Blender
- `get_viewport_screenshot` - Capture viewport
- `search_polyhaven_assets` - Search free assets
- `generate_material_from_text` - AI material creation
- `create_from_description` - NLP object creation

---

## Troubleshooting

### "Tools not appearing"

1. **Restart your AI client** completely (quit and reopen)
2. **Verify JSON syntax** using a validator like [jsonlint.com](https://jsonlint.com)
3. **Check config file path** matches your OS
4. **Ensure blenderforge is in PATH**:
   ```bash
   which blenderforge  # macOS/Linux
   where blenderforge  # Windows
   ```
5. **Check AI client logs** for MCP-related errors

### "Connection refused"

1. **Ensure Blender is running** with addon enabled
2. **Click "Connect to MCP server"** in Blender's BlenderForge panel
3. **Check port** (default: 9876) isn't used by another app
4. **Restart the connection** in Blender if needed

### "Command not found: blenderforge"

```bash
# Reinstall BlenderForge
pip install --upgrade blenderforge

# Or install with explicit path
pip install --user blenderforge

# Find installation location
pip show blenderforge
```

### Client-Specific Issues

| Client | Common Issue | Solution |
|--------|--------------|----------|
| Claude Desktop | Config not loading | Check JSON syntax, restart app |
| ChatGPT | Developer Mode not visible | Requires Plus/Pro subscription |
| VS Code | Tools not in Copilot | Ensure Agent Mode (not Chat) |
| Cursor | Server not starting | Check `.cursor/mcp.json` path |
| Windsurf | 100 tool limit | Disable unused tools in settings |
| Zed | Only prompts work | HTTP transport has limited support |

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
export BLENDERFORGE_DEBUG=true
blenderforge
```

Check logs for detailed error messages.

---

## Quick Reference Table

| AI Client | Config Location | Format | Key Name |
|-----------|-----------------|--------|----------|
| Claude Desktop | `~/Library/Application Support/Claude/` | JSON | `mcpServers` |
| ChatGPT | Settings UI | UI wizard | Connector |
| VS Code Copilot | `.vscode/mcp.json` | JSON | `servers` |
| Cursor | `~/.cursor/mcp.json` | JSON | `mcpServers` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | JSON | `mcpServers` |
| Zed | Settings JSON | JSON | `context_servers` |
| Continue.dev | `.continue/mcpServers/` | YAML/JSON | `mcpServers` |

---

## See Also

- [Getting Started](getting-started.md) - Installation guide
- [Tools Reference](tools-reference.md) - Complete tool documentation
- [Troubleshooting](troubleshooting.md) - More solutions
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18) - Protocol details

---

## Sources

- [Model Context Protocol Introduction](https://modelcontextprotocol.io/introduction)
- [Claude Desktop MCP Setup](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [ChatGPT Developer Mode](https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta)
- [VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Cursor MCP Documentation](https://cursor.com/docs/context/mcp)
- [Windsurf Cascade MCP Integration](https://docs.windsurf.com/windsurf/cascade/mcp)
- [Zed MCP Documentation](https://zed.dev/docs/assistant/model-context-protocol)
- [Continue.dev MCP Setup](https://docs.continue.dev/customize/deep-dives/mcp)
