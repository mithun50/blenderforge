# BlenderForge MCP - GitHub Copilot Instructions

When using BlenderForge MCP tools to control Blender:

## Available MCP Tools (84 tools)

### Essential Tools
| Tool | Purpose |
|------|---------|
| `get_scene_info` | Get scene overview - always call first |
| `get_object_info` | Get specific object details |
| `create_object` | Create primitives (cube, sphere, etc.) |
| `execute_blender_code` | Run custom Python in Blender |
| `take_screenshot` | Capture viewport |

### Modeling Tools
| Tool | Purpose |
|------|---------|
| `boolean_operation` | Union/Difference/Intersect |
| `create_array` | Duplicate with offset |
| `add_bevel` | Bevel edges |
| `mirror_object` | Mirror geometry |
| `extrude_faces` | Extrude geometry |
| `loop_cut` | Add edge loops |

### Animation Tools
| Tool | Purpose |
|------|---------|
| `insert_keyframe` | Add animation keys |
| `create_turntable` | 360° rotation |
| `animate_path` | Follow curve |
| `add_shape_key` | Morph targets |

### Physics Tools
| Tool | Purpose |
|------|---------|
| `add_rigid_body` | Physics dynamics |
| `add_cloth_simulation` | Cloth physics |
| `add_collision` | Collision object |
| `create_force_field` | Forces (wind, etc.) |

### Rendering Tools
| Tool | Purpose |
|------|---------|
| `setup_studio_render` | Quick studio lighting |
| `set_render_settings` | Engine, quality |
| `render_image` | Render frame |
| `render_animation` | Render sequence |

### Asset Tools
| Tool | Purpose |
|------|---------|
| `search_polyhaven_assets` | Free HDRIs/textures |
| `download_polyhaven_asset` | Apply assets |
| `ai_generate_material` | AI PBR materials |

## Best Practices

1. **Start with `get_scene_info`** to understand current state
2. **Use descriptive names** for objects (not Cube.001)
3. **Organize with collections** for complex scenes
4. **Save frequently** with `save_blend`
5. **Use modifiers** for non-destructive editing

## Standard Workflow

```
get_scene_info → create_object → add_modifier → set_material → setup_studio_render → render_image
```
