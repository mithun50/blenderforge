# Getting Started

Complete guide to installing BlenderForge and connecting it to your AI assistant.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Step 1: Install BlenderForge](#step-1-install-blenderforge)
- [Step 2: Install the Blender Addon](#step-2-install-the-blender-addon)
- [Step 3: Configure Your AI Assistant](#step-3-configure-your-ai-assistant)
- [Step 4: Connect Everything](#step-4-connect-everything)
- [Step 5: Try It Out](#step-5-try-it-out)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)
- [Platform-Specific Notes](#platform-specific-notes)
- [Next Steps](#next-steps)

---

## System Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.10+ | 3.11+ |
| **Blender** | 3.0+ | 4.0+ |
| **RAM** | 4 GB | 8+ GB |
| **Disk Space** | 500 MB | 2+ GB (for assets) |
| **OS** | Windows 10, macOS 10.15, Linux | Latest stable |

### Software Prerequisites

1. **Python 3.10+**
   - [Download Python](https://www.python.org/downloads/)
   - Verify: `python --version` or `python3 --version`

2. **Blender 3.0+**
   - [Download Blender](https://www.blender.org/download/)
   - Recommended: Blender 4.x for best compatibility
   - Verify: Open Blender → `Help` → `About Blender`

3. **MCP-Compatible AI Assistant**
   - See [AI Clients](ai-clients.md) for supported platforms
   - Popular options: Claude Desktop, VS Code + Copilot, Cursor

### Network Requirements

- Internet connection required for:
  - PolyHaven assets (textures, HDRIs, models)
  - Sketchfab models (requires API key)
  - AI 3D generation services (Hyper3D, Hunyuan3D)
- Local-only mode works without internet (core features only)

---

## Quick Start

For experienced users, here's the fastest path to get started:

```bash
# 1. Install BlenderForge
pip install blenderforge

# 2. Verify installation
blenderforge --version

# 3. Download addon.py from repository and install in Blender
# Edit → Preferences → Add-ons → Install...

# 4. Configure your AI client (Claude Desktop example)
# Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
# {
#   "mcpServers": {
#     "blenderforge": {
#       "command": "blenderforge"
#     }
#   }
# }

# 5. In Blender: Press N → BlenderForge tab → "Connect to MCP server"
# 6. Restart your AI assistant
# 7. Ask: "What objects are in my Blender scene?"
```

---

## Step 1: Install BlenderForge

Choose the installation method that best fits your workflow.

### Option A: Install from PyPI (Recommended)

The simplest method for most users:

```bash
pip install blenderforge
```

#### Platform-Specific Commands

**macOS / Linux:**
```bash
# Using pip (may require pip3)
pip3 install blenderforge

# Or if pip is aliased to pip3
pip install blenderforge
```

**Windows (Command Prompt):**
```cmd
pip install blenderforge
```

**Windows (PowerShell):**
```powershell
pip install blenderforge
```

### Option B: Install with UV (Fast Package Manager)

[UV](https://github.com/astral-sh/uv) is a modern, fast Python package manager:

```bash
# Install UV first (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install BlenderForge
uv pip install blenderforge
```

### Option C: Install with pipx (Isolated Environment)

[pipx](https://pipx.pypa.io/) installs packages in isolated environments:

```bash
# Install pipx first (if not installed)
pip install pipx
pipx ensurepath

# Install BlenderForge
pipx install blenderforge
```

### Option D: Install from Source (Development)

For contributors or those who need the latest features:

```bash
# Clone the repository
git clone https://github.com/mithun50/blenderforge.git
cd blenderforge

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Verify Installation

After installation, verify BlenderForge is working:

```bash
# Check version
blenderforge --version

# Should output something like:
# BlenderForge v0.1.0
```

**If `blenderforge` command is not found:**

1. **Check if pip installed to a user directory:**
   ```bash
   # Find where pip installed it
   pip show blenderforge

   # Add the Scripts/bin directory to PATH
   # Look for "Location:" in the output
   ```

2. **Try running as a module:**
   ```bash
   python -m blenderforge --version
   ```

3. **Check PATH environment variable:**
   ```bash
   # macOS/Linux
   echo $PATH

   # Windows
   echo %PATH%
   ```

---

## Step 2: Install the Blender Addon

The Blender addon receives commands from BlenderForge and executes them inside Blender.

### Download the Addon

#### Direct Download (Recommended)

**[⬇️ Download addon.py](https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py)** (Right-click → Save Link As...)

Or use the command line:

```bash
# macOS/Linux
curl -O https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py" -OutFile "addon.py"

# Windows (Command Prompt with curl)
curl -O https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py
```

#### Alternative Download Methods

1. **From GitHub Repository:**
   - Go to [BlenderForge Repository](https://github.com/mithun50/Blender-Forge)
   - Click on `addon.py` file
   - Click the **Download** button (↓) or **Raw** button, then save the page

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/mithun50/Blender-Forge.git
   # addon.py is in the root directory
   ```

### Install in Blender

#### GUI Method (Recommended)

1. **Open Blender**

2. **Open Preferences:**
   - Go to `Edit` → `Preferences` (or press `Ctrl+,` / `Cmd+,`)

3. **Navigate to Add-ons:**
   - Click on the `Add-ons` tab in the left sidebar

4. **Install the Addon:**
   - Click the `Install...` button (top-right corner)
   - Navigate to where you downloaded `addon.py`
   - Select `addon.py`
   - Click `Install Add-on`

5. **Enable the Addon:**
   - After installation, search for "BlenderForge" in the search box
   - Check the checkbox next to **"BlenderForge"** to enable it
   - You should see a checkmark appear

6. **Save Preferences:**
   - Click the hamburger menu (☰) at the bottom-left
   - Select `Save Preferences`
   - This ensures the addon loads automatically every time you start Blender

#### Visual Guide

```
┌─────────────────────────────────────────────────────────────────┐
│  Blender Preferences                                      [X]  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐                                                   │
│  │Interface │   Search: [BlenderForge        ]    [Install...] │
│  │Themes    │                                                   │
│  │Viewport  │   ☑ BlenderForge                                  │
│  │Lights    │     AI-powered Blender control via MCP            │
│  │Editing   │     Version: 1.0.0                                │
│  │Animation │     Author: BlenderForge Team                     │
│  │▶Add-ons  │                                                   │
│  │Input     │   ┌─────────────────────────────────────────────┐ │
│  │Navigation│   │ Preferences:                                │ │
│  │Keymap    │   │  Port: [9876    ]                           │ │
│  │System    │   │  ☑ Use PolyHaven                            │ │
│  │Save&Load │   │  ☐ Use Sketchfab  API Key: [••••••••••]     │ │
│  │File Paths│   │  ☐ Use Hyper3D    API Key: [          ]     │ │
│  └──────────┘   └─────────────────────────────────────────────┘ │
│                                                                 │
│  [☰] ────────────────────────────────────────── [Save Preferences]
└─────────────────────────────────────────────────────────────────┘
```

#### Command Line Method (Advanced)

For automated installation, copy `addon.py` directly to Blender's addon directory:

**macOS:**
```bash
cp addon.py ~/Library/Application\ Support/Blender/4.0/scripts/addons/
```

**Windows (PowerShell):**
```powershell
Copy-Item addon.py "$env:APPDATA\Blender Foundation\Blender\4.0\scripts\addons\"
```

**Linux:**
```bash
cp addon.py ~/.config/blender/4.0/scripts/addons/
```

Then enable in Blender:
```
Edit → Preferences → Add-ons → Search "BlenderForge" → Enable checkbox
```

### Verify Addon Installation

1. **Check Sidebar Panel:**
   - Press `N` to open the sidebar (right side of 3D viewport)
   - Look for the **BlenderForge** tab
   - You should see:
     - Server status indicator
     - Port configuration
     - Connect/Disconnect button
     - Integration checkboxes (PolyHaven, Sketchfab, etc.)

2. **Check Blender Console for Confirmation:**
   - **Windows:** `Window` → `Toggle System Console`
   - **macOS/Linux:** Launch Blender from terminal to see output
   - Look for message: `"BlenderForge addon registered"`

3. **Test the Panel:**
   - The panel should display "Status: Disconnected" initially
   - This is normal - you'll connect after configuring your AI client

---

## Step 3: Configure Your AI Assistant

BlenderForge uses the Model Context Protocol (MCP) to communicate with AI assistants. Each AI client has its own configuration method.

### Quick Configuration Reference

| AI Client | Config File/Method |
|-----------|-------------------|
| Claude Desktop | JSON config file |
| Claude Code | `~/.claude.json` or `claude mcp add` |
| ChatGPT Desktop | Settings → MCP menu |
| VS Code + Copilot | `settings.json` |
| Cursor | Settings → MCP tab |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| Zed | `~/.config/zed/settings.json` |
| Continue.dev | `~/.continue/config.yaml` |

### Claude Desktop Configuration

The most common setup. Edit the config file for your platform:

**macOS:**
```bash
# Open or create the config file
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```cmd
# Open in Notepad
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**Add this configuration:**
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

**With Python path (if command not in PATH):**
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "/path/to/python",
      "args": ["-m", "blenderforge"]
    }
  }
}
```

**With environment variables:**
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "env": {
        "BLENDER_PORT": "9876",
        "DISABLE_TELEMETRY": "true"
      }
    }
  }
}
```

### Other AI Clients

For detailed setup instructions for all supported AI clients, see **[AI Clients](ai-clients.md)**.

---

## Step 4: Connect Everything

Now let's connect all the pieces together.

### Connection Flow

```
AI Assistant  ─MCP Protocol→  BlenderForge Server  ─TCP Socket→  Blender Addon
    │                              │                                  │
    │  JSON-RPC over stdio         │  localhost:9876                  │
    │                              │                                  │
    └──────── Tool Calls ──────────┴────── Commands ──────────────────┘
```

### Start the Connection

1. **Open Blender** with the addon enabled

2. **Open the BlenderForge Panel:**
   - Press `N` to open the sidebar
   - Click the **BlenderForge** tab

3. **Configure Port (if needed):**
   - Default port is `9876`
   - Change if you have conflicts

4. **Start the Server:**
   - Click **"Connect to MCP server"**
   - Status should change to **"Connected"**

5. **Restart Your AI Assistant:**
   - Close and reopen your AI client completely
   - MCP servers are loaded at startup

### Verify Connection

Ask your AI assistant:

```
What objects are in my Blender scene?
```

**Expected Response:**
The AI should query Blender and return information about objects in your scene. For a new scene, this typically includes:
- Camera
- Light (or Lamp)
- Cube (default cube)

**If it works:** Congratulations! BlenderForge is connected.

**If it doesn't work:** See [Troubleshooting](troubleshooting.md).

---

## Step 5: Try It Out

Here are examples organized by complexity.

### Basic Scene Operations

```
"What's in my scene?"
"Get information about the current scene"
"List all objects in the scene"
```

### Object Creation

```
"Add a cube at position (2, 0, 0)"
"Create a sphere with radius 2"
"Add a cylinder at the origin"
"Create a plane for the ground"
```

### Object Manipulation

```
"Move the cube to (0, 0, 3)"
"Rotate the sphere 45 degrees on the Z axis"
"Scale the cube by 2"
"Delete the default cube"
```

### Screenshots

```
"Take a screenshot of the viewport"
"Capture the current render view"
```

### PolyHaven Assets

First enable PolyHaven in the BlenderForge panel, then:

```
"Search for wood textures on PolyHaven"
"Download the 'wood_floor_deck' texture"
"Apply the wood texture to the cube"
"Set up studio HDRI lighting"
"Find outdoor HDRIs"
```

### AI-Powered Features

BlenderForge includes built-in AI features that don't require external API keys:

**AI Material Generator:**
```
"Generate a rusty metal material"
"Create a glowing neon material"
"Make a realistic wood material for the table"
```

**Natural Language Modeling:**
```
"Create a red cube 2 meters tall"
"Add a blue sphere at position 3, 0, 0"
"Make a small green cylinder"
```

**Scene Analysis:**
```
"Analyze my scene composition"
"Give me feedback on my scene"
"What could improve this scene?"
```

**Auto-Rigging:**
```
"Auto-rig the character mesh"
"Create an armature for the humanoid"
```

### Advanced Python Execution

For complete control, execute Python code directly:

```
"Run this Python code in Blender:
import bpy
for i in range(5):
    bpy.ops.mesh.primitive_uv_sphere_add(location=(i*2, 0, 0))"
```

```
"Execute in Blender:
import bpy
# Create a new material
mat = bpy.data.materials.new('Red_Material')
mat.use_nodes = True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1, 0, 0, 1)"
```

---

## Environment Variables

Customize BlenderForge behavior with environment variables.

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLENDER_HOST` | Host where Blender addon runs | `localhost` |
| `BLENDER_PORT` | Port for socket connection | `9876` |
| `BLENDER_TIMEOUT` | Connection timeout (ms) | `30000` |
| `DISABLE_TELEMETRY` | Disable anonymous usage stats | `false` |
| `BLENDERFORGE_DEBUG` | Enable debug logging | `false` |

### Setting Environment Variables

**macOS / Linux (temporary):**
```bash
export BLENDER_PORT=9877
export DISABLE_TELEMETRY=true
blenderforge
```

**macOS / Linux (permanent - add to shell profile):**
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
export BLENDER_PORT=9877
export DISABLE_TELEMETRY=true
```

**Windows (Command Prompt - temporary):**
```cmd
set BLENDER_PORT=9877
set DISABLE_TELEMETRY=true
blenderforge
```

**Windows (PowerShell - temporary):**
```powershell
$env:BLENDER_PORT = "9877"
$env:DISABLE_TELEMETRY = "true"
blenderforge
```

**Windows (permanent - System Properties):**
1. Open "Environment Variables" in System Properties
2. Add new user or system variables

### In MCP Configuration

You can also set environment variables in your AI client's MCP config:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "env": {
        "BLENDER_PORT": "9877",
        "DISABLE_TELEMETRY": "true",
        "BLENDERFORGE_DEBUG": "true"
      }
    }
  }
}
```

---

## Advanced Configuration

### Running Multiple Blender Instances

To connect to multiple Blender instances:

1. **Start each Blender with different ports:**
   - Blender 1: Port 9876 (default)
   - Blender 2: Port 9877
   - Blender 3: Port 9878

2. **Configure multiple MCP servers:**
```json
{
  "mcpServers": {
    "blender1": {
      "command": "blenderforge",
      "env": { "BLENDER_PORT": "9876" }
    },
    "blender2": {
      "command": "blenderforge",
      "env": { "BLENDER_PORT": "9877" }
    }
  }
}
```

### Remote Blender Connection

For advanced use cases (same network):

1. **On the Blender machine:**
   - Modify addon to bind to `0.0.0.0` instead of `localhost`
   - Configure firewall to allow connections

2. **On the AI client machine:**
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "env": {
        "BLENDER_HOST": "192.168.1.100",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

**⚠️ Security Warning:** Remote connections are not encrypted. Only use on trusted networks.

### Using Virtual Environments

If you installed BlenderForge in a virtual environment:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "/path/to/venv/bin/blenderforge"
    }
  }
}
```

Or use the Python interpreter:
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "blenderforge"]
    }
  }
}
```

---

## Platform-Specific Notes

### macOS

**Python Installation:**
- Homebrew: `brew install python@3.11`
- Official installer from python.org

**Common Issues:**
- If `blenderforge` not found, check `~/Library/Python/3.x/bin` is in PATH
- System Integrity Protection may block some operations

**Blender Location:**
- Default: `/Applications/Blender.app`
- Addon directory: `~/Library/Application Support/Blender/4.0/scripts/addons/`

### Windows

**Python Installation:**
- Download from python.org
- **Important:** Check "Add Python to PATH" during installation

**Common Issues:**
- Run Command Prompt as Administrator if permission issues
- Use forward slashes or escaped backslashes in paths

**Blender Location:**
- Default: `C:\Program Files\Blender Foundation\Blender 4.0`
- Addon directory: `%APPDATA%\Blender Foundation\Blender\4.0\scripts\addons\`

### Linux

**Python Installation:**
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3-pip

# Fedora
sudo dnf install python3.11 python3-pip

# Arch
sudo pacman -S python python-pip
```

**Blender Installation:**
- Snap: `sudo snap install blender --classic`
- Flatpak: `flatpak install flathub org.blender.Blender`
- Official tarball from blender.org

**Common Issues:**
- Snap/Flatpak Blender may have restricted file access
- Check permissions on addon directory

**Blender Location:**
- System: `/usr/share/blender/`
- User addon directory: `~/.config/blender/4.0/scripts/addons/`

---

## Next Steps

Now that BlenderForge is installed and connected:

### Learn More

| Resource | Description |
|----------|-------------|
| [AI Clients](ai-clients.md) | Detailed setup for all AI platforms |
| [Tools Reference](tools-reference.md) | Complete list of available tools |
| [AI Features](ai-features.md) | AI material generator, NLP modeling, scene analysis |
| [Asset Integrations](asset-integrations.md) | PolyHaven, Sketchfab, AI generation |
| [Architecture](architecture.md) | How BlenderForge works internally |

### Enable Integrations

In the BlenderForge panel:
- ✅ **PolyHaven** - Free textures, HDRIs, models
- ✅ **Sketchfab** - 3D model marketplace (requires API key)
- ✅ **Hyper3D Rodin** - AI 3D generation (requires API key)
- ✅ **Hunyuan3D** - AI 3D generation (requires Tencent credentials)

### Join the Community

- [GitHub Repository](https://github.com/mithun50/blenderforge)
- [GitHub Issues](https://github.com/mithun50/blenderforge/issues) - Report bugs, request features
- [GitHub Discussions](https://github.com/mithun50/blenderforge/discussions) - Ask questions, share creations

---

## Having Issues?

See **[Troubleshooting](troubleshooting.md)** for common problems and solutions.

Common quick fixes:
1. **Restart both** Blender and your AI assistant
2. **Check the port** is the same in Blender panel and MCP config
3. **Verify** `blenderforge` command is in PATH
4. **Check Blender console** for error messages
