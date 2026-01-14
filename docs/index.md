# BlenderForge Documentation

> Control Blender with AI through natural language conversation.

Welcome to the BlenderForge documentation. BlenderForge connects AI assistants to Blender using the **Model Context Protocol (MCP)**, letting you create 3D scenes using natural language.

---

## Quick Navigation

| Document | Description |
|----------|-------------|
| [Getting Started](getting-started.md) | Installation, setup, and first steps |
| [AI Clients](ai-clients.md) | Configure Claude, ChatGPT, VS Code, Cursor, and more |
| [Tools Reference](tools-reference.md) | Complete list of available tools |
| [Asset Integrations](asset-integrations.md) | PolyHaven, Sketchfab, Hyper3D Rodin, Hunyuan3D |
| [Architecture](architecture.md) | How BlenderForge works under the hood |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions |
| [Development](development.md) | Contributing and development setup |

---

## What Can You Do?

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
| **Query Scene** | Get information about objects, materials, settings |
| **Create Objects** | Add and modify 3D objects |
| **Run Python** | Execute any Blender Python code |
| **Take Screenshots** | Capture viewport images |
| **Download Assets** | Get free textures, HDRIs, and 3D models |
| **AI Generation** | Generate 3D models from text or images |

---

## How It Works

BlenderForge uses the **Model Context Protocol (MCP)** - an open standard that lets AI assistants use external tools.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR AI ASSISTANT                            │
│         (Claude, ChatGPT, Copilot, Cursor, Antigravity...)         │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ MCP Protocol (standard communication)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BLENDERFORGE SERVER                            │
│                                                                     │
│  Translates AI requests into Blender commands                       │
│  • "Get scene info" → Blender scene data                           │
│  • "Add a cube" → bpy.ops.mesh.primitive_cube_add()                │
│  • "Download wood texture" → PolyHaven API → Material setup        │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ Socket Connection (localhost:9876)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BLENDER + ADDON                                │
│                                                                     │
│  Executes commands in Blender's 3D environment                      │
│  • Creates/modifies objects                                         │
│  • Applies materials and textures                                   │
│  • Manages scene, lighting, camera                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Supported AI Assistants

BlenderForge works with **any AI that supports MCP**. As of 2025, that includes:

| AI Assistant | Developer | Status |
|--------------|-----------|--------|
| Claude Desktop | Anthropic | ✅ Full support |
| Claude Code | Anthropic | ✅ Full support |
| ChatGPT Desktop | OpenAI | ✅ Full support |
| Google Antigravity | Google | ✅ Full support |
| VS Code + Copilot | Microsoft | ✅ Full support |
| Cursor IDE | Cursor | ✅ Full support |
| Windsurf | Codeium | ✅ Full support |
| Zed Editor | Zed | ✅ Full support |
| Continue.dev | Continue | ✅ Full support |

MCP is an **open standard** (like USB for AI tools). Any AI that "speaks MCP" can use BlenderForge - no special integration needed. The ecosystem has **481+ compatible clients** and growing.

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.10 or higher |
| **Blender** | 3.0 or higher (4.x recommended) |
| **OS** | Windows, macOS, or Linux |
| **Network** | Localhost access (no internet required for core features) |

### Platform Support

| Platform | Architecture | Status |
|----------|--------------|--------|
| Windows 10/11 | x64, ARM64 | ✅ Full support |
| macOS 12+ | Intel, Apple Silicon | ✅ Full support |
| Linux | x64, ARM64 | ✅ Full support |

---

## Quick Links

- [GitHub Repository](https://github.com/yourusername/blenderforge)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [PolyHaven](https://polyhaven.com/)

---

## License

MIT License - see [LICENSE](../LICENSE) for details.
