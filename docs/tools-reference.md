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

## Tool Availability

Not all tools are available at all times. Availability depends on:

| Tool Category | Requirement |
|---------------|-------------|
| Core Tools | Always available |
| PolyHaven | Enable in BlenderForge panel |
| Sketchfab | Enable + API key |
| Hyper3D Rodin | Enable + API key |
| Hunyuan3D | Enable + Tencent credentials |

Check availability using the `get_*_status` tools.
