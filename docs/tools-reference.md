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

## Modifier System

Advanced modeling tools using Blender's non-destructive modifier stack.

### add_modifier

Add a modifier to an object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object to modify |
| `modifier_type` | string | Yes | Type: BOOLEAN, BEVEL, ARRAY, MIRROR, SUBSURF, SOLIDIFY, DECIMATE, REMESH, SMOOTH, etc. |
| `settings` | string | No | JSON string of modifier settings |

**Returns**:
```json
{
  "success": true,
  "object": "Cube",
  "modifier_name": "Bevel",
  "modifier_type": "BEVEL"
}
```

**Example Usage**:
```
"Add a bevel modifier to the Cube"
"Apply a mirror modifier with X axis to my mesh"
```

---

### configure_modifier

Configure an existing modifier's settings.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `modifier_name` | string | Yes | Name of the modifier |
| `settings` | string | Yes | JSON string of settings |

---

### apply_modifier

Apply or remove a modifier from an object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `modifier_name` | string | Yes | Name of the modifier |
| `remove_only` | boolean | No | If true, remove without applying (default: false) |

---

### boolean_operation

Perform boolean operations between two objects.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_object` | string | Yes | Object to modify |
| `tool_object` | string | Yes | Object to use as tool |
| `operation` | string | No | UNION, DIFFERENCE, INTERSECT (default: DIFFERENCE) |

**Returns**:
```json
{
  "success": true,
  "operation": "DIFFERENCE",
  "target": "Cube",
  "tool": "Sphere",
  "result_vertices": 156
}
```

**Example Usage**:
```
"Cut a hole in the Cube using the Cylinder"
"Combine these two meshes using union"
```

---

### create_array

Create an array of objects using the array modifier.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `count` | integer | No | Number of copies (default: 3) |
| `offset_x/y/z` | float | No | Offset between copies |
| `use_relative_offset` | boolean | No | Use relative offset (default: true) |

**Example Usage**:
```
"Create an array of 10 cubes along the X axis"
"Duplicate this chair 5 times with 2 meter spacing"
```

---

### add_bevel

Add bevel modifier for edge smoothing.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `width` | float | No | Bevel width (default: 0.1) |
| `segments` | integer | No | Number of segments (default: 3) |
| `profile` | float | No | Profile shape 0-1 (default: 0.5) |
| `limit_method` | string | No | NONE, ANGLE, WEIGHT, VGROUP |

---

### mirror_object

Add mirror modifier for symmetry.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `axis_x/y/z` | boolean | No | Mirror axes (default: X only) |
| `use_clip` | boolean | No | Clip at mirror plane (default: true) |
| `merge_threshold` | float | No | Merge distance (default: 0.001) |

---

### subdivide_smooth

Add subdivision surface for smooth geometry.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `levels` | integer | No | Viewport levels (default: 2) |
| `render_levels` | integer | No | Render levels (default: 3) |
| `use_creases` | boolean | No | Use edge creases (default: true) |

---

## Mesh Editing Operations

Direct mesh manipulation tools for precise modeling.

### extrude_faces

Extrude selected faces of a mesh.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh object |
| `face_indices` | string | Yes | JSON array of face indices, e.g., "[0, 1, 2]" |
| `distance` | float | Yes | Extrusion distance |
| `direction` | string | No | NORMAL, X, Y, Z, or "[x,y,z]" |

**Returns**:
```json
{
  "success": true,
  "faces_extruded": 3,
  "new_vertices": 12
}
```

---

### inset_faces

Inset selected faces.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh object |
| `face_indices` | string | Yes | JSON array of face indices |
| `thickness` | float | No | Inset thickness (default: 0.1) |
| `depth` | float | No | Inset depth (default: 0.0) |

---

### loop_cut

Add loop cuts to a mesh.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh object |
| `edge_index` | integer | Yes | Index of edge to cut through |
| `cuts` | integer | No | Number of cuts (default: 1) |
| `smoothness` | float | No | Smoothness (default: 0.0) |

---

### merge_vertices

Merge vertices by distance.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh object |
| `threshold` | float | No | Merge distance (default: 0.0001) |
| `vertex_indices` | string | No | Optional JSON array of vertex indices |

---

### separate_by_loose

Separate a mesh into multiple objects by loose parts.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh to separate |

---

### join_objects

Join multiple objects into one.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_names` | string | Yes | JSON array of names, e.g., '["Cube", "Sphere"]' |

---

## Animation System

Keyframe animation and motion tools.

### insert_keyframe

Insert a keyframe for an object property.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `data_path` | string | Yes | Property: location, rotation_euler, scale |
| `frame` | integer | Yes | Frame number |
| `value` | string | No | Optional JSON value, e.g., "[1.0, 2.0, 3.0]" |

**Example Usage**:
```
"Set a keyframe for the cube's location at frame 1"
"Animate the sphere to move from 0 to 5 on Z axis"
```

---

### set_animation_range

Set the animation frame range and FPS.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_frame` | integer | No | Start frame (default: 1) |
| `end_frame` | integer | No | End frame (default: 250) |
| `fps` | integer | No | Frames per second (default: 24) |

---

### create_turntable

Create a 360-degree turntable animation.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of object to rotate |
| `frames` | integer | No | Duration in frames (default: 120) |
| `axis` | string | No | Rotation axis X, Y, Z (default: Z) |

**Example Usage**:
```
"Create a turntable animation for the product"
"Make the car rotate 360 degrees over 5 seconds"
```

---

### add_shape_key

Add a shape key to a mesh object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh |
| `name` | string | No | Shape key name (default: "Key") |
| `from_mix` | boolean | No | Create from current mix (default: false) |

---

### animate_shape_key

Animate a shape key's value over time.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh |
| `shape_key_name` | string | Yes | Name of the shape key |
| `keyframes` | string | Yes | JSON array of [frame, value] pairs |

---

### animate_path

Animate an object along a curve path.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of object to animate |
| `curve_name` | string | Yes | Name of curve to follow |
| `frames` | integer | No | Duration in frames (default: 100) |
| `follow_curve` | boolean | No | Align rotation to curve (default: true) |

---

### bake_animation

Bake physics/constraints to keyframes.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `start_frame` | integer | No | Start frame (default: 1) |
| `end_frame` | integer | No | End frame (default: 250) |
| `step` | integer | No | Frame step (default: 1) |
| `bake_types` | string | No | JSON array: '["LOCATION", "ROTATION", "SCALE"]' |

---

## Physics Simulation

Dynamic simulation tools for realistic motion.

### add_rigid_body

Add rigid body physics to an object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `body_type` | string | No | ACTIVE or PASSIVE (default: ACTIVE) |
| `mass` | float | No | Mass in kg (default: 1.0) |
| `friction` | float | No | Friction 0-1 (default: 0.5) |
| `bounciness` | float | No | Bounce 0-1 (default: 0.0) |

**Example Usage**:
```
"Make this ball fall with physics"
"Set the floor as a passive rigid body collider"
```

---

### add_cloth_simulation

Add cloth simulation to a mesh.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the mesh |
| `preset` | string | No | COTTON, DENIM, LEATHER, RUBBER, SILK |
| `collision_objects` | string | No | JSON array of collision object names |

---

### add_collision

Add collision physics for cloth/soft body.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object |
| `damping` | float | No | Damping (default: 0.1) |
| `thickness` | float | No | Thickness (default: 0.02) |

---

### create_force_field

Create a force field for physics simulations.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `field_type` | string | Yes | WIND, VORTEX, TURBULENCE, FORCE, MAGNET |
| `strength` | float | No | Field strength (default: 10.0) |
| `location_x/y/z` | float | No | Field position |

---

### bake_physics

Bake all physics simulations in the scene.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_frame` | integer | No | Start frame (default: 1) |
| `end_frame` | integer | No | End frame (default: 250) |

---

### add_particle_system

Add a particle emitter to an object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of emitter |
| `count` | integer | No | Number of particles (default: 1000) |
| `lifetime` | integer | No | Lifetime in frames (default: 50) |
| `emit_from` | string | No | FACE, VERT, VOLUME |
| `render_type` | string | No | NONE, HALO, PATH, OBJECT, COLLECTION |

---

## Camera & Rendering System

Camera control and render output tools.

### create_camera

Create a new camera in the scene.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | No | Camera name (default: "Camera") |
| `location_x/y/z` | float | No | Camera position |
| `focal_length` | float | No | Focal length in mm (default: 50.0) |

---

### set_active_camera

Set the active camera for rendering.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `camera_name` | string | Yes | Name of camera to activate |

---

### configure_camera

Configure camera settings including depth of field.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `camera_name` | string | Yes | Name of the camera |
| `focal_length` | float | No | Focal length in mm |
| `dof_focus_object` | string | No | Object for DOF focus |
| `aperture` | float | No | F-stop value |
| `sensor_width` | float | No | Sensor width in mm |

---

### camera_look_at

Point a camera at an object or location.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `camera_name` | string | Yes | Name of the camera |
| `target_object` | string | No | Object to look at |
| `target_point` | string | No | JSON point, e.g., "[0, 0, 0]" |

---

### set_render_settings

Configure render engine and settings.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `engine` | string | No | CYCLES, BLENDER_EEVEE, BLENDER_WORKBENCH |
| `samples` | integer | No | Render samples (default: 128) |
| `resolution_x/y` | integer | No | Output resolution |
| `denoise` | boolean | No | Enable denoising (default: true) |
| `use_gpu` | boolean | No | Use GPU rendering (default: true) |

**Example Usage**:
```
"Set render resolution to 4K"
"Switch to Cycles with 256 samples"
```

---

### render_image

Render the current frame to a file.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filepath` | string | Yes | Output file path |
| `format` | string | No | PNG, JPEG, EXR, TIFF (default: PNG) |

---

### render_animation

Render animation sequence.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `output_path` | string | Yes | Output directory/filename |
| `format` | string | No | PNG, JPEG, EXR, FFMPEG |
| `start_frame` | integer | No | Start frame |
| `end_frame` | integer | No | End frame |

---

### setup_studio_render

Set up professional studio lighting.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_object` | string | No | Object to focus on |
| `style` | string | No | PRODUCT, PORTRAIT, DRAMATIC, SOFT |
| `background_color` | string | No | JSON RGB, e.g., "[1.0, 1.0, 1.0]" |

---

## Curves & Text System

Path and typography tools.

### create_bezier_curve

Create a bezier curve from control points.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `points` | string | Yes | JSON array of points, e.g., "[[0,0,0], [1,0,1]]" |
| `name` | string | No | Curve name (default: "Curve") |
| `resolution` | integer | No | Resolution (default: 12) |
| `closed` | boolean | No | Close loop (default: false) |

---

### create_text_object

Create a 3D text object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | The text content |
| `name` | string | No | Object name (default: "Text") |
| `size` | float | No | Text size (default: 1.0) |
| `extrude` | float | No | Extrusion depth (default: 0.0) |
| `bevel_depth` | float | No | Bevel depth (default: 0.0) |
| `font` | string | No | Font file path |

**Example Usage**:
```
"Create 3D text saying 'Hello World'"
"Add extruded text with a bevel"
```

---

### curve_to_mesh

Convert a curve object to a mesh.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `curve_name` | string | Yes | Name of curve to convert |

---

### create_pipe

Create a pipe/tube mesh along a curve.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `curve_name` | string | Yes | Name of curve to follow |
| `radius` | float | No | Pipe radius (default: 0.1) |
| `resolution` | integer | No | Circular resolution (default: 8) |
| `fill_caps` | boolean | No | Cap the ends (default: true) |

---

## Constraints & Relationships

Object relationship and control tools.

### add_constraint

Add a constraint to an object.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Object to constrain |
| `constraint_type` | string | Yes | COPY_LOCATION, COPY_ROTATION, TRACK_TO, etc. |
| `target_object` | string | No | Target object |
| `settings` | string | No | JSON string of settings |

---

### create_empty

Create an empty object for use as control or parent.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | No | Empty name (default: "Empty") |
| `empty_type` | string | No | PLAIN_AXES, ARROWS, CIRCLE, CUBE, SPHERE |
| `location_x/y/z` | float | No | Position |
| `size` | float | No | Display size (default: 1.0) |

---

### parent_objects

Set parent-child relationships.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `child_names` | string | Yes | JSON array of child names |
| `parent_name` | string | Yes | Name of parent |
| `keep_transform` | boolean | No | Maintain world transforms (default: true) |

---

## Scene Organization

Project management and export tools.

### create_collection

Create a new collection for organizing objects.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Collection name |
| `parent_collection` | string | No | Parent collection name |
| `color_tag` | string | No | NONE, COLOR_01 through COLOR_08 |

---

### move_to_collection

Move objects to a collection.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_names` | string | Yes | JSON array of object names |
| `collection_name` | string | Yes | Target collection |

---

### set_collection_visibility

Set collection visibility.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection_name` | string | Yes | Collection name |
| `visible` | boolean | No | Viewport visibility (default: true) |
| `render_visible` | boolean | No | Render visibility (default: true) |

---

### duplicate_linked

Create a linked duplicate sharing mesh data.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Object to duplicate |
| `new_name` | string | No | Name for new object |

---

### purge_unused

Remove all unused data blocks (orphan data).

**Parameters**: None

---

### save_blend

Save the current scene as a .blend file.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filepath` | string | Yes | Output file path |
| `compress` | boolean | No | Compress file (default: true) |

---

### export_scene

Export scene to external format.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filepath` | string | Yes | Output file path |
| `format` | string | No | GLTF, GLB, FBX, OBJ, STL |
| `selected_only` | boolean | No | Export selected only (default: false) |
| `apply_modifiers` | boolean | No | Apply modifiers (default: true) |

**Example Usage**:
```
"Export my scene as a GLB file"
"Save the selected objects as FBX"
```

---

## Procedural Generation

Geometry nodes and procedural content tools.

### scatter_on_surface

Scatter instances on a surface using geometry nodes.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `surface_object` | string | Yes | Name of surface mesh |
| `instance_object` | string | Yes | Object to scatter |
| `density` | float | No | Instances per sq unit (default: 10.0) |
| `seed` | integer | No | Random seed (default: 0) |
| `scale_min/max` | float | No | Scale variation (default: 0.8-1.2) |
| `align_to_normal` | boolean | No | Align to surface (default: true) |

**Example Usage**:
```
"Scatter trees on the terrain"
"Add grass instances across the ground plane"
```

---

### create_procedural_terrain

Generate procedural terrain with noise.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | No | Terrain name (default: "Terrain") |
| `size` | float | No | Size in units (default: 10.0) |
| `resolution` | integer | No | Subdivision (default: 100) |
| `height_scale` | float | No | Height variation (default: 2.0) |
| `noise_scale` | float | No | Noise pattern scale (default: 1.0) |
| `seed` | integer | No | Random seed (default: 0) |

**Example Usage**:
```
"Create a mountainous terrain"
"Generate a procedural landscape"
```

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
