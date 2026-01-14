# Getting Started

This guide will help you install BlenderForge and connect it to your AI assistant.

---

## Prerequisites

Before installing BlenderForge, ensure you have:

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Blender 3.0+** - [Download Blender](https://www.blender.org/download/) (4.x recommended)
- **An MCP-compatible AI assistant** - See [AI Clients](ai-clients.md)

---

## Step 1: Install BlenderForge

Choose one of the following installation methods:

### Option A: Install from PyPI (Recommended)

```bash
pip install blenderforge
```

### Option B: Install from Source

```bash
git clone https://github.com/yourusername/blenderforge.git
cd blenderforge
pip install -e .
```

### Verify Installation

```bash
blenderforge --version
```

---

## Step 2: Install the Blender Addon

The Blender addon receives commands from BlenderForge and executes them inside Blender.

### Installation Steps

1. **Download** `addon.py` from the [repository](https://github.com/yourusername/blenderforge)

2. **Open Blender**

3. **Navigate to Add-ons**:
   - Go to `Edit` → `Preferences` → `Add-ons`

4. **Install the addon**:
   - Click `Install...`
   - Select the `addon.py` file
   - Click `Install Add-on`

5. **Enable the addon**:
   - Find "BlenderForge" in the list
   - Check the checkbox to enable it

### Verify Addon Installation

1. Press `N` to open the sidebar
2. Look for the **BlenderForge** tab
3. You should see connection settings and options

---

## Step 3: Configure Your AI Assistant

BlenderForge needs to be registered with your AI assistant. See [AI Clients](ai-clients.md) for detailed configuration instructions for each platform.

### Quick Example (Claude Desktop)

Edit the config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

---

## Step 4: Connect Everything

Now let's connect all the pieces together.

### Start the Connection

1. **Open Blender** with the addon enabled

2. **Open the BlenderForge panel**:
   - Press `N` to open the sidebar
   - Click the **BlenderForge** tab

3. **Start the server**:
   - Click **"Connect to MCP server"**
   - The status should change to "Connected"

4. **Restart your AI assistant** to load the new MCP server

### Verify Connection

Ask your AI assistant:

```
What objects are in my Blender scene?
```

If everything is connected correctly, the AI will query Blender and return the scene information.

---

## Step 5: Try It Out

Here are some things you can try:

### Basic Commands

```
"What's in my scene?"
"Add a cube at position (2, 0, 0)"
"Delete all mesh objects"
"Take a screenshot of the viewport"
```

### With PolyHaven Assets

First, enable PolyHaven in the BlenderForge panel, then:

```
"Search for wood textures on PolyHaven"
"Download the 'wood_floor_deck' texture and apply it to the cube"
"Set up an HDRI for studio lighting"
```

### Advanced Python Execution

```
"Run this Python code in Blender:
import bpy
for i in range(5):
    bpy.ops.mesh.primitive_uv_sphere_add(location=(i*2, 0, 0))"
```

---

## Environment Variables

You can customize BlenderForge behavior with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `BLENDER_HOST` | Host where Blender addon runs | `localhost` |
| `BLENDER_PORT` | Port for connection | `9876` |
| `DISABLE_TELEMETRY` | Disable anonymous usage stats | `false` |

### Example

```bash
export BLENDER_PORT=9877
export DISABLE_TELEMETRY=true
blenderforge
```

---

## Next Steps

- [Configure more AI clients](ai-clients.md)
- [Explore available tools](tools-reference.md)
- [Set up asset integrations](asset-integrations.md)
- [Learn the architecture](architecture.md)

---

## Having Issues?

See [Troubleshooting](troubleshooting.md) for common problems and solutions.
