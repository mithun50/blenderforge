---
title: Home
description: Control Blender with AI through natural language conversation
---

# BlenderForge

<p class="hero-gradient" style="font-size: 1.4em; font-weight: 500; margin-bottom: 2em;">
Control Blender with AI through natural language conversation
</p>

<div class="grid" markdown>

<div class="card" markdown>
### :material-robot: AI-Powered
Connect any MCP-compatible AI assistant to Blender. Works with Claude, ChatGPT, Copilot, and 481+ more.
</div>

<div class="card" markdown>
### :material-lightning-bolt: Natural Language
Just describe what you want. No menus, no scripts - pure conversation.
</div>

<div class="card" markdown>
### :material-palette: Rich Features
Materials, lighting, assets, 3D generation - everything through simple commands.
</div>

<div class="card" markdown>
### :material-open-source-initiative: Open Source
MIT licensed, community-driven, and completely free to use.
</div>

</div>

---

## :rocket: Quick Start

=== "pip"

    ```bash
    pip install blenderforge
    ```

=== "uv"

    ```bash
    uv pip install blenderforge
    ```

=== "pipx"

    ```bash
    pipx install blenderforge
    ```

Then configure your AI assistant:

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

[:octicons-arrow-right-24: Full Installation Guide](getting-started.md)

---

## :sparkles: What Can You Do?

Instead of learning complex Blender menus and Python scripts, just describe what you want:

```
You: Create a cozy coffee shop scene with wooden tables and warm lighting

AI: I'll create that for you...
    ✓ Setting up warm HDRI lighting from PolyHaven
    ✓ Adding wooden tables with realistic textures
    ✓ Placing coffee cups and decorations
    ✓ Adjusting camera for a cozy atmosphere
```

### Core Capabilities

| Capability | Description |
|------------|-------------|
| :material-cube-scan: **Query Scene** | Get information about objects, materials, settings |
| :material-cube-outline: **Create Objects** | Add and modify 3D objects |
| :material-code-tags: **Run Python** | Execute any Blender Python code |
| :material-camera: **Take Screenshots** | Capture viewport images |
| :material-download: **Download Assets** | Get free textures, HDRIs, and 3D models |
| :material-creation: **AI Generation** | Generate 3D models from text or images |

### AI-Powered Features

| Feature | Description |
|---------|-------------|
| :material-palette-swatch: **AI Material Generator** | Create PBR materials from text descriptions or images |
| :material-chat-processing: **Natural Language Modeling** | Create objects with plain English |
| :material-chart-line: **AI Scene Analyzer** | Get professional critique with scores and suggestions |
| :material-human: **Smart Auto-Rig** | Automatically rig characters with proper bone hierarchies |
| :material-lightbulb-on: **Auto-Lighting** | Set up studio, cinematic, or dramatic lighting presets |

---

## :globe_with_meridians: Supported AI Assistants

BlenderForge works with **any AI that supports MCP**:

| AI Assistant | Developer | Status |
|--------------|-----------|--------|
| Claude Desktop | Anthropic | :white_check_mark: Full support |
| Claude Code | Anthropic | :white_check_mark: Full support |
| ChatGPT Desktop | OpenAI | :white_check_mark: Full support |
| Google Antigravity | Google | :white_check_mark: Full support |
| VS Code + Copilot | Microsoft | :white_check_mark: Full support |
| Cursor IDE | Cursor | :white_check_mark: Full support |
| Windsurf | Codeium | :white_check_mark: Full support |
| Zed Editor | Zed | :white_check_mark: Full support |
| Continue.dev | Continue | :white_check_mark: Full support |

!!! tip "Open Standard"
    MCP is an **open standard** (like USB for AI tools). Any AI that "speaks MCP" can use BlenderForge - no special integration needed.

---

## :building_construction: How It Works

```mermaid
flowchart LR
    A[AI Assistant] -->|MCP Protocol| B[BlenderForge Server]
    B -->|Socket| C[Blender Addon]
    C -->|Python API| D[Blender]

    style A fill:#7c3aed,stroke:#5b21b6,color:#fff
    style B fill:#a855f7,stroke:#7c3aed,color:#fff
    style C fill:#f59e0b,stroke:#d97706,color:#fff
    style D fill:#fb923c,stroke:#f59e0b,color:#fff
```

BlenderForge uses the **Model Context Protocol (MCP)** - an open standard that lets AI assistants use external tools.

1. **AI Assistant** sends natural language requests via MCP
2. **BlenderForge Server** translates requests into Blender commands
3. **Blender Addon** executes commands via Python API
4. **Results** flow back to your AI assistant

---

## :desktop_computer: System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.10 or higher |
| **Blender** | 3.0 or higher (4.x recommended) |
| **OS** | Windows, macOS, or Linux |
| **Network** | Localhost access (no internet required for core features) |

---

## :link: Quick Links

<div class="grid" markdown>

[:material-github: **GitHub Repository**](https://github.com/mithun50/blenderforge){ .md-button }

[:material-book-open-variant: **Documentation**](getting-started.md){ .md-button }

[:fontawesome-brands-python: **PyPI Package**](https://pypi.org/project/blenderforge/){ .md-button }

[:material-help-circle: **Get Help**](troubleshooting.md){ .md-button }

</div>

---

## :balance_scale: License

MIT License - see [LICENSE](https://github.com/mithun50/blenderforge/blob/main/LICENSE) for details.

Made with :heart: by [Mithun Gowda B](https://github.com/mithun50)
