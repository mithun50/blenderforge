---
title: BlenderForge - AI-Powered Blender Control
description: Control Blender with AI through natural language conversation
---

# BlenderForge

**Control Blender with AI through natural language conversation**

[![PyPI](https://img.shields.io/pypi/v/blenderforge?style=flat-square&color=000)](https://pypi.org/project/blenderforge/)
[![Downloads](https://img.shields.io/pypi/dm/blenderforge?style=flat-square&color=000)](https://pypi.org/project/blenderforge/)
[![Python](https://img.shields.io/badge/Python-3.10+-000?style=flat-square)](https://www.python.org/)
[![Blender](https://img.shields.io/badge/Blender-3.0+-000?style=flat-square)](https://www.blender.org/)
[![License](https://img.shields.io/badge/License-MIT-000?style=flat-square)](https://github.com/mithun50/blenderforge/blob/main/LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-000?style=flat-square)](https://modelcontextprotocol.io/)

---

## Overview

BlenderForge connects AI assistants to Blender using the **Model Context Protocol (MCP)**. Instead of learning complex menus and Python scripts, just describe what you want in plain English.

```text
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

### 2. Install the Blender Addon

1. **[Click here to download addon.py](https://raw.githubusercontent.com/mithun50/Blender-Forge/main/addon.py)**
2. In Blender: `Edit` → `Preferences` → `Add-ons` → `Install...`
3. Select `addon.py` and enable the checkbox
4. Click `Save Preferences`

### 3. Configure Your AI

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

1. In Blender: Press `N` → BlenderForge tab → "Connect to MCP server"
2. Restart your AI assistant
3. Start creating!

[:octicons-arrow-right-24: Full Installation Guide](getting-started.md)

---

## Features

### Core Tools

| Tool | Description |
|------|-------------|
| **Scene Query** | Get information about objects, materials, settings |
| **Object Creation** | Add and modify 3D objects |
| **Code Execution** | Run any Blender Python code |
| **Screenshots** | Capture viewport images |
| **Asset Download** | Get free textures, HDRIs, 3D models |
| **3D Generation** | Generate models from text or images |

### AI-Powered Features

| Feature | Description |
|---------|-------------|
| **Material Generator** | Create PBR materials from text descriptions |
| **NLP Modeling** | Create objects with plain English |
| **Scene Analyzer** | Professional critique with scores |
| **Auto-Rig** | Automatically rig characters |
| **Auto-Lighting** | Studio, cinematic, dramatic presets |

---

## Supported AI Assistants

| AI Assistant | Developer | Status |
|--------------|-----------|--------|
| Claude Desktop/Code | Anthropic | :white_check_mark: |
| ChatGPT Desktop | OpenAI | :white_check_mark: |
| VS Code + Copilot | Microsoft | :white_check_mark: |
| Cursor IDE | Cursor | :white_check_mark: |
| Windsurf | Codeium | :white_check_mark: |
| Zed Editor | Zed | :white_check_mark: |
| Continue.dev | Continue | :white_check_mark: |

Works with **any MCP-compatible client** (481+ and growing).

---

## Architecture

```mermaid
flowchart LR
    A[AI Assistant] -->|MCP Protocol| B[BlenderForge Server]
    B -->|Socket| C[Blender Addon]
    C -->|Python API| D[Blender]

    style A fill:#000,stroke:#333,color:#fff
    style B fill:#333,stroke:#000,color:#fff
    style C fill:#666,stroke:#333,color:#fff
    style D fill:#999,stroke:#666,color:#000
```

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.10+ |
| Blender | 3.0+ (4.x recommended) |
| OS | Windows, macOS, Linux |

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](getting-started.md) | Installation and setup |
| [AI Clients](ai-clients.md) | Configuration for each platform |
| [Tools Reference](tools-reference.md) | Complete tool documentation |
| [AI Features](ai-features.md) | Material generator, NLP, analysis |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |

---

## Links

- [GitHub Repository](https://github.com/mithun50/blenderforge)
- [PyPI Package](https://pypi.org/project/blenderforge/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**License**: MIT | **Author**: [Mithun Gowda B](https://github.com/mithun50)
