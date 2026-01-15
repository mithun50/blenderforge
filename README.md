<div align="center">

# 🔥 BlenderForge

### Control Blender with AI through natural language conversation

[![PyPI Version](https://img.shields.io/pypi/v/blenderforge?color=blue&label=PyPI)](https://pypi.org/project/blenderforge/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/blenderforge?color=green&label=Downloads)](https://pypi.org/project/blenderforge/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Blender 3.0+](https://img.shields.io/badge/Blender-3.0+-E87D0D?logo=blender&logoColor=white)](https://www.blender.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/mithun50/blenderforge/blob/main/LICENSE)

[![GitHub Stars](https://img.shields.io/github/stars/mithun50/blenderforge?style=social)](https://github.com/mithun50/blenderforge/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/mithun50/blenderforge?style=social)](https://github.com/mithun50/blenderforge/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/mithun50/blenderforge)](https://github.com/mithun50/blenderforge/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/mithun50/blenderforge)](https://github.com/mithun50/blenderforge/pulls)

[![CI](https://img.shields.io/github/actions/workflow/status/mithun50/blenderforge/ci.yml?branch=main&label=CI&logo=github)](https://github.com/mithun50/blenderforge/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/github/actions/workflow/status/mithun50/blenderforge/docs.yml?branch=main&label=Docs&logo=github)](https://mithun50.github.io/blenderforge/)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-261230?logo=ruff&logoColor=D7FF64)](https://github.com/astral-sh/ruff)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-00D4AA?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6Ii8+PC9zdmc+)](https://modelcontextprotocol.io/)

[![Documentation](https://img.shields.io/badge/📚_Documentation-mithun50.github.io/blenderforge-7c3aed?style=for-the-badge)](https://mithun50.github.io/blenderforge/)

</div>

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

1. **[Download addon.py](https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py)** (Right-click → Save Link As)
2. In Blender: `Edit` → `Preferences` → `Add-ons` → `Install...`
3. Select `addon.py` and click `Install Add-on`
4. Enable the "BlenderForge" addon (check the checkbox)
5. Click `Save Preferences` to keep it enabled

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

### AI-Powered Features

| Feature | Description |
|---------|-------------|
| **AI Material Generator** | Create PBR materials from text or images |
| **Natural Language Modeling** | Create objects with plain English ("a red cube 2m tall") |
| **AI Scene Analyzer** | Professional critique with scores and suggestions |
| **Smart Auto-Rig** | Automatically rig characters with bone hierarchies |
| **Auto-Lighting** | Studio, cinematic, dramatic lighting presets |

---

## 📚 Documentation

> **Full documentation available at: [mithun50.github.io/blenderforge](https://mithun50.github.io/blenderforge/)**

| Document | Description |
|----------|-------------|
| [📖 Getting Started](https://mithun50.github.io/blenderforge/getting-started/) | Installation and setup guide |
| [🤖 AI Clients](https://mithun50.github.io/blenderforge/ai-clients/) | Configuration for each AI platform |
| [🔧 Tools Reference](https://mithun50.github.io/blenderforge/tools-reference/) | Complete tool documentation (40+ tools) |
| [✨ AI Features](https://mithun50.github.io/blenderforge/ai-features/) | AI material generator, NLP modeling, scene analysis |
| [📦 Asset Integrations](https://mithun50.github.io/blenderforge/asset-integrations/) | PolyHaven, Sketchfab, AI generation |
| [🐍 Blender API Reference](https://mithun50.github.io/blenderforge/blender-api-reference/) | Python API quick reference |
| [🏗️ Architecture](https://mithun50.github.io/blenderforge/architecture/) | How BlenderForge works |
| [🔍 Troubleshooting](https://mithun50.github.io/blenderforge/troubleshooting/) | Common issues and solutions |
| [👨‍💻 Development](https://mithun50.github.io/blenderforge/development/) | Contributing guide |

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10+ |
| Blender | 3.0+ (4.x recommended) |
| OS | Windows, macOS, Linux |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/mithun50/blenderforge/blob/main/CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/mithun50/blenderforge.git
cd blenderforge
pip install -e ".[dev]"
pytest
```

---

## License

MIT License - see [LICENSE](https://github.com/mithun50/blenderforge/blob/main/LICENSE) for details.

---

## Links

- 📚 [**Documentation**](https://mithun50.github.io/blenderforge/) - Full docs with guides and API reference
- 📦 [**PyPI Package**](https://pypi.org/project/blenderforge/) - Install via pip
- 🔌 [**Model Context Protocol**](https://modelcontextprotocol.io/) - MCP specification
- 🎨 [**Blender Python API**](https://docs.blender.org/api/current/) - Blender scripting reference
- 🌐 [**PolyHaven**](https://polyhaven.com/) - Free HDRIs, textures, and models
- 🎭 [**Sketchfab**](https://sketchfab.com/) - 3D model marketplace

---

<div align="center">

**[⬆ Back to Top](#-blenderforge)**

Made with ❤️ by [Mithun Gowda B](https://github.com/mithun50)

</div>
