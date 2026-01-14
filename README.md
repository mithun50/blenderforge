# BlenderForge

> Control Blender with AI through natural language conversation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Blender 3.0+](https://img.shields.io/badge/blender-3.0+-orange.svg)](https://www.blender.org/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is BlenderForge?

BlenderForge connects AI assistants to Blender using the **Model Context Protocol (MCP)**. Instead of learning complex menus and Python scripts, just describe what you want:

```
You: Create a cozy coffee shop scene with wooden tables and warm lighting

AI: I'll create that for you...
    ✓ Setting up warm HDRI lighting from PolyHaven
    ✓ Adding wooden tables with realistic textures
    ✓ Placing coffee cups and decorations
    ✓ Adjusting camera for a cozy atmosphere
```

---

## Quick Start

### 1. Install BlenderForge

```bash
pip install blenderforge
```

### 2. Install the Blender Addon

1. Download `addon.py` from this repository
2. In Blender: `Edit` → `Preferences` → `Add-ons` → `Install...`
3. Enable the "BlenderForge" addon

### 3. Configure Your AI Assistant

Add to your AI client's MCP configuration:

```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

### 4. Connect

1. In Blender, press `N` → BlenderForge tab → "Connect to MCP server"
2. Restart your AI assistant
3. Start creating!

---

## Supported AI Assistants

| AI Assistant | Developer | Status |
|--------------|-----------|--------|
| Claude Desktop/Code | Anthropic | ✅ |
| ChatGPT Desktop | OpenAI | ✅ |
| Google Antigravity | Google | ✅ |
| VS Code + Copilot | Microsoft | ✅ |
| Cursor IDE | Cursor | ✅ |
| Windsurf | Codeium | ✅ |
| Zed Editor | Zed | ✅ |
| Continue.dev | Continue | ✅ |

BlenderForge works with **any MCP-compatible client** (481+ and growing).

---

## Features

| Feature | Description |
|---------|-------------|
| **Scene Control** | Query and modify Blender scenes |
| **Code Execution** | Run Python scripts in Blender |
| **Screenshots** | Capture viewport images |
| **PolyHaven** | Free HDRIs, textures, and models |
| **Sketchfab** | Download 3D models (API key required) |
| **Hyper3D Rodin** | AI-generated 3D from text/images |
| **Hunyuan3D** | Tencent's AI 3D generation |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and setup |
| [AI Clients](docs/ai-clients.md) | Configuration for each AI platform |
| [Tools Reference](docs/tools-reference.md) | Complete tool documentation |
| [Asset Integrations](docs/asset-integrations.md) | PolyHaven, Sketchfab, AI generation |
| [Architecture](docs/architecture.md) | How BlenderForge works |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |
| [Development](docs/development.md) | Contributing guide |

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10+ |
| Blender | 3.0+ (4.x recommended) |
| OS | Windows, macOS, Linux |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/yourusername/blenderforge.git
cd blenderforge
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [PolyHaven](https://polyhaven.com/)
- [Sketchfab](https://sketchfab.com/)
