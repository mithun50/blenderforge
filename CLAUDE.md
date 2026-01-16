# BlenderForge AI Instructions

You are working with **BlenderForge**, an MCP-based tool for controlling Blender through natural language.

## Available Tools (84 MCP Tools)

### Core Tools
- `get_scene_info` - Get current scene overview
- `get_object_info` - Get details about specific object
- `execute_blender_code` - Run Python code in Blender
- `take_screenshot` - Capture viewport image

### Object Creation
- `create_object` - Create primitives (cube, sphere, cylinder, etc.)
- `create_text_object` - Create 3D text
- `create_bezier_curve` - Create curves from points
- `create_empty` - Create empty objects for control

### Transformations
- `set_object_transform` - Set location/rotation/scale
- `parent_objects` - Create parent-child relationships

### Modifiers (Non-Destructive Editing)
- `add_modifier` - Add any modifier type
- `boolean_operation` - Union/Difference/Intersect objects
- `create_array` - Array modifier with offset
- `add_bevel` - Bevel edges
- `mirror_object` - Mirror across axis
- `subdivide_smooth` - Subdivision surface

### Mesh Editing
- `extrude_faces` - Extrude geometry
- `inset_faces` - Inset faces
- `loop_cut` - Add loop cuts
- `merge_vertices` - Merge by distance
- `join_objects` - Combine multiple objects
- `separate_by_loose` - Separate loose parts

### Materials & Textures
- `set_material` - Apply/create materials
- `ai_generate_material` - AI-powered PBR material creation

### Animation
- `insert_keyframe` - Add keyframes
- `set_animation_range` - Set frame range
- `create_turntable` - 360° rotation animation
- `add_shape_key` - Morphing targets
- `animate_path` - Object follows curve
- `bake_animation` - Bake to keyframes

### Physics
- `add_rigid_body` - Rigid body dynamics
- `add_cloth_simulation` - Cloth physics
- `add_collision` - Collision object
- `create_force_field` - Wind/vortex/turbulence
- `add_particle_system` - Particle emitters
- `bake_physics` - Bake simulation

### Camera & Rendering
- `create_camera` - Add camera
- `configure_camera` - Focal length, DOF, etc.
- `camera_look_at` - Point at target
- `set_render_settings` - Engine, samples, resolution
- `render_image` - Render to file
- `render_animation` - Render sequence
- `setup_studio_render` - One-click studio setup

### Scene Organization
- `create_collection` - Organize objects
- `move_to_collection` - Move objects
- `save_blend` - Save .blend file
- `export_scene` - Export FBX/glTF/OBJ

### Asset Libraries
- `get_polyhaven_status` - Check PolyHaven availability
- `search_polyhaven_assets` - Search HDRIs/textures/models
- `download_polyhaven_asset` - Download and apply assets
- `search_sketchfab_models` - Search Sketchfab
- `download_sketchfab_model` - Import 3D models

### AI Features
- `ai_generate_material` - Generate PBR materials from description
- `nlp_create_object` - Create objects from natural language
- `ai_analyze_scene` - Professional scene critique
- `auto_rig_character` - Automatic rigging
- `auto_lighting` - Studio/cinematic lighting presets

### Procedural Generation
- `scatter_on_surface` - Distribute instances on surfaces
- `create_procedural_terrain` - Generate terrain with noise

## Best Practices

### 1. Always Check Scene First
```
Before making changes, use get_scene_info to understand the current state.
```

### 2. Use Descriptive Names
```
When creating objects, use meaningful names like "Table_Main" not "Cube.001"
```

### 3. Organize with Collections
```
Group related objects: create_collection("Furniture") then move_to_collection
```

### 4. Non-Destructive Workflow
```
Prefer modifiers over direct mesh editing when possible.
Use boolean_operation instead of manual cutting.
```

### 5. Save Frequently
```
Use save_blend after significant changes.
```

### 6. Render Pipeline
```
1. setup_studio_render for quick professional lighting
2. configure_camera for composition
3. set_render_settings for quality
4. render_image or render_animation
```

## Common Workflows

### Create a Simple Scene
1. `get_scene_info` - Check current state
2. `create_object` - Add objects
3. `set_material` - Apply materials
4. `setup_studio_render` - Add lighting
5. `render_image` - Capture result

### Hard Surface Modeling
1. Create base shape with `create_object`
2. Add details with `boolean_operation`
3. Refine edges with `add_bevel`
4. Apply materials with `set_material`

### Animation
1. Create objects
2. `set_animation_range` - Define timeline
3. `insert_keyframe` at different frames
4. Or use `create_turntable` for product shots

### Physics Simulation
1. Create objects
2. `add_rigid_body` to dynamic objects
3. `add_collision` to static surfaces
4. `bake_physics` to cache simulation

## Error Handling

If a tool fails:
1. Check object names are correct with `get_scene_info`
2. Verify Blender addon is connected
3. Check tool parameters match expected types

## Team

- Mithun Gowda B (@mithun50)
- Nevil D'Souza (@nevil06)
- Lekhan H R (@lekhanpro)
- Manvanth Gowda M (@appukannadiga)
- NXG Team Organization (@NextGenXplorer)
