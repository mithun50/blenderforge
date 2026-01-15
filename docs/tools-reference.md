# Tools Reference

Complete reference for all BlenderForge tools available to AI assistants.

---

## Core Tools

These tools are always available and provide basic Blender interaction.

### get_scene_info

Get information about the current Blender scene.

**Parameters**: None

**Returns**:
```json
{
  "name": "Scene",
  "object_count": 3,
  "objects": [
    {"name": "Cube", "type": "MESH", "location": [0.0, 0.0, 0.0]},
    {"name": "Camera", "type": "CAMERA", "location": [7.0, -6.0, 5.0]},
    {"name": "Light", "type": "LIGHT", "location": [4.0, 1.0, 6.0]}
  ],
  "materials_count": 1
}
```

**Example Usage**:
```
"What objects are in my scene?"
"How many materials do I have?"
```

---

### get_object_info

Get detailed information about a specific object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object to query |

**Returns**:
```json
{
  "name": "Cube",
  "type": "MESH",
  "location": [0.0, 0.0, 0.0],
  "rotation": [0.0, 0.0, 0.0],
  "scale": [1.0, 1.0, 1.0],
  "visible": true,
  "materials": ["Material"],
  "mesh": {
    "vertices": 8,
    "edges": 12,
    "polygons": 6
  },
  "world_bounding_box": [[-1.0, -1.0, -1.0], [1.0, 1.0, 1.0]]
}
```

**Example Usage**:
```
"What are the properties of the Cube object?"
"Where is the Camera located?"
```

---

### execute_blender_code

Execute arbitrary Python code in Blender's environment.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Python code to execute |

**Returns**:
```json
{
  "success": true,
  "result": "...",
  "output": "...",
  "error": null
}
```

**Example Usage**:
```
"Add 5 spheres in a row"
"Delete all objects named 'Cube*'"
"Set the render resolution to 1920x1080"
```

**Security Note**: This tool executes arbitrary code. Use with caution.

---

### get_viewport_screenshot

Capture a screenshot of the current 3D viewport.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `width` | integer | No | Image width (default: 1920) |
| `height` | integer | No | Image height (default: 1080) |

**Returns**:
```json
{
  "success": true,
  "image_data": "base64_encoded_png...",
  "width": 1920,
  "height": 1080
}
```

**Example Usage**:
```
"Show me the current viewport"
"Take a screenshot of the scene"
```

---

## PolyHaven Tools

Free asset downloads from [PolyHaven](https://polyhaven.com/). No API key required.

### get_polyhaven_status

Check if PolyHaven integration is enabled.

**Parameters**: None

**Returns**:
```json
{
  "enabled": true,
  "connected": true
}
```

---

### get_polyhaven_categories

List available asset categories.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_type` | string | Yes | One of: `hdris`, `textures`, `models` |

**Returns**:
```json
{
  "categories": ["outdoor", "indoor", "studio", "nature", "urban"]
}
```

---

### search_polyhaven_assets

Search for assets by type and category.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_type` | string | Yes | One of: `hdris`, `textures`, `models` |
| `category` | string | No | Filter by category |
| `search` | string | No | Search query |

**Returns**:
```json
{
  "assets": [
    {
      "id": "wood_floor_deck",
      "name": "Wood Floor Deck",
      "categories": ["wood", "floor"],
      "download_count": 12345
    }
  ]
}
```

---

### download_polyhaven_asset

Download and import an asset into Blender.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_id` | string | Yes | Asset ID from search results |
| `asset_type` | string | Yes | One of: `hdris`, `textures`, `models` |
| `resolution` | string | No | Resolution (e.g., `1k`, `2k`, `4k`) |

**Returns**:
```json
{
  "success": true,
  "asset_name": "wood_floor_deck",
  "file_path": "/tmp/polyhaven/wood_floor_deck_4k.png"
}
```

---

### set_texture

Apply a downloaded texture to an object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Target object name |
| `texture_path` | string | Yes | Path to texture file |
| `material_name` | string | No | Name for the new material |

**Returns**:
```json
{
  "success": true,
  "material_name": "wood_floor_deck_material"
}
```

---

## Sketchfab Tools

3D model marketplace. Requires API key.

### get_sketchfab_status

Check if Sketchfab integration is enabled and configured.

**Parameters**: None

**Returns**:
```json
{
  "enabled": true,
  "authenticated": true
}
```

---

### search_sketchfab_models

Search for 3D models on Sketchfab.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `downloadable` | boolean | No | Only show downloadable models |
| `animated` | boolean | No | Only show animated models |
| `max_results` | integer | No | Maximum results (default: 24) |

**Returns**:
```json
{
  "models": [
    {
      "uid": "abc123",
      "name": "Coffee Mug",
      "author": "artist_name",
      "thumbnail_url": "https://...",
      "downloadable": true
    }
  ]
}
```

---

### get_sketchfab_model_preview

Get a preview image of a model.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model_uid` | string | Yes | Model UID from search |

**Returns**:
```json
{
  "image_data": "base64_encoded_image...",
  "model_name": "Coffee Mug"
}
```

---

### download_sketchfab_model

Download and import a model into Blender.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model_uid` | string | Yes | Model UID |

**Returns**:
```json
{
  "success": true,
  "model_name": "Coffee Mug",
  "objects_imported": 3
}
```

---

## Hyper3D Rodin Tools

AI-generated 3D models from text or images. Requires API key (free trial available).

### get_hyper3d_status

Check if Hyper3D is enabled and configured.

**Parameters**: None

**Returns**:
```json
{
  "enabled": true,
  "authenticated": true,
  "credits_remaining": 100
}
```

---

### generate_hyper3d_model_via_text

Generate a 3D model from a text description.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the model |
| `quality` | string | No | `draft`, `standard`, `high` |

**Returns**:
```json
{
  "job_id": "job_abc123",
  "status": "processing",
  "estimated_time": 30
}
```

---

### generate_hyper3d_model_via_images

Generate a 3D model from reference images.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_paths` | array | Yes | List of image file paths |
| `quality` | string | No | `draft`, `standard`, `high` |

**Returns**:
```json
{
  "job_id": "job_abc123",
  "status": "processing",
  "estimated_time": 60
}
```

---

### poll_rodin_job_status

Check the status of a generation job.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes | Job ID from generation request |

**Returns**:
```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "progress": 100,
  "download_url": "https://..."
}
```

---

### import_generated_asset

Import a completed generated model into Blender.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes | Completed job ID |
| `object_name` | string | No | Name for imported object |

**Returns**:
```json
{
  "success": true,
  "object_name": "Generated_Model",
  "vertices": 5000
}
```

---

## Hunyuan3D Tools

Tencent's AI 3D generation service. Requires Tencent Cloud credentials.

### get_hunyuan3d_status

Check if Hunyuan3D is enabled and configured.

**Parameters**: None

**Returns**:
```json
{
  "enabled": true,
  "authenticated": true
}
```

---

### generate_hunyuan3d_model

Generate a 3D model from text or image.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | No | Text description |
| `image_path` | string | No | Reference image path |

**Returns**:
```json
{
  "job_id": "hunyuan_abc123",
  "status": "processing"
}
```

---

### poll_hunyuan_job_status

Check Hunyuan generation job status.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes | Job ID |

**Returns**:
```json
{
  "status": "completed",
  "progress": 100
}
```

---

### import_generated_asset_hunyuan

Import completed Hunyuan model.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes | Completed job ID |

**Returns**:
```json
{
  "success": true,
  "object_name": "Hunyuan_Model"
}
```

---

## AI-Powered Tools

Intelligent automation tools for enhanced 3D workflow. See [AI Features](ai-features.md) for detailed documentation.

### generate_material_from_text

Generate a PBR material from a text description.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | Natural language description (e.g., "rusty metal", "glossy wood") |
| `material_name` | string | No | Name for the material (default: "AI_Material") |

**Returns**:
```json
{
  "material_name": "RustyMetal",
  "properties_applied": ["metallic", "roughness", "base_color"],
  "metallic": 0.9,
  "roughness": 0.8
}
```

**Example Usage**:
```
"Create a rusty metal material"
"Generate a polished wooden texture"
```

---

### generate_material_from_image

Generate a PBR material from a reference image.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_path` | string | Yes | Path to the reference image |
| `material_name` | string | No | Name for the material |

---

### list_material_presets

List available AI material presets.

**Parameters**: None

**Returns**:
```json
{
  "presets": ["metal", "wood", "stone", "fabric", "glass", "plastic", "organic"]
}
```

---

### create_from_description

Create 3D objects from natural language descriptions.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | What to create (e.g., "a red cube 2 meters tall") |

**Returns**:
```json
{
  "created_objects": ["Cube"],
  "count": 1,
  "properties": {"color": [1.0, 0.0, 0.0, 1.0]}
}
```

**Example Usage**:
```
"Create a blue sphere at position 5, 0, 0"
"Make a wooden table"
"Add 3 green cylinders"
```

---

### modify_from_description

Modify existing objects using natural language.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Object to modify |
| `modification` | string | Yes | What to change (e.g., "make it red", "scale to 2x") |

---

### analyze_scene_composition

Analyze scene and provide professional critique with scores.

**Parameters**: None

**Returns**:
```json
{
  "lighting": {"score": 75, "issues": [...], "suggestions": [...]},
  "composition": {"score": 80, "issues": [...], "suggestions": [...]},
  "materials": {"score": 60, "issues": [...], "suggestions": [...]},
  "overall_score": 72
}
```

---

### get_improvement_suggestions

Get specific improvement recommendations for the current scene.

**Parameters**: None

---

### auto_optimize_lighting

Automatically set up professional lighting.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `style` | string | No | Lighting style: `studio`, `outdoor`, `dramatic`, `soft`, `product`, `cinematic` |

**Returns**:
```json
{
  "style": "studio",
  "lights_created": ["Key_Light", "Fill_Light", "Back_Light"]
}
```

---

### auto_rig_character

Automatically create an armature for a mesh.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mesh_name` | string | Yes | Mesh object to rig |
| `rig_type` | string | No | `humanoid`, `quadruped`, or `simple` |

**Returns**:
```json
{
  "armature_name": "Character_Armature",
  "bones_created": 15,
  "mesh_parented": true
}
```

---

### auto_weight_paint

Automatically paint vertex weights for mesh-armature binding.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mesh_name` | string | Yes | Mesh object name |
| `armature_name` | string | Yes | Armature object name |

---

### add_ik_controls

Add Inverse Kinematics constraints for animation.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `armature_name` | string | Yes | Armature to add IK to |
| `limb` | string | No | `arm_l`, `arm_r`, `leg_l`, `leg_r`, or `all` |

---

## Tool Availability

Not all tools are available at all times. Availability depends on:

| Tool Category | Requirement |
|---------------|-------------|
| Core Tools | Always available |
| AI-Powered Tools | Always available |
| PolyHaven | Enable in BlenderForge panel |
| Sketchfab | Enable + API key |
| Hyper3D Rodin | Enable + API key |
| Hunyuan3D | Enable + Tencent credentials |

Check availability using the `get_*_status` tools.
