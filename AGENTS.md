# BlenderForge - AI Agent Instructions

This file provides instructions for AI agents using BlenderForge MCP tools.

## Overview

BlenderForge is an MCP (Model Context Protocol) server that enables AI assistants to control Blender through natural language. When connected, you have access to 84 tools for 3D modeling, animation, physics, and rendering.

## Connection Status

Before using tools, ensure:
1. BlenderForge MCP server is running (`blenderforge` command)
2. Blender addon is installed and enabled
3. Addon shows "Connected" in the BlenderForge panel

## Tool Usage Guidelines

### Always Start Here
```
get_scene_info
```
This returns the current scene state including all objects, their types, and properties.

### Creating Objects

**Primitives:**
```
create_object(type="CUBE", name="MyBox", location=[0, 0, 0], scale=[1, 1, 1])
create_object(type="SPHERE", name="Ball", location=[2, 0, 0])
create_object(type="CYLINDER", name="Pillar")
```

**Text:**
```
create_text_object(text="Hello", size=1.0, extrude=0.1)
```

**Curves:**
```
create_bezier_curve(points=[[0,0,0], [1,1,0], [2,0,0]], name="MyCurve")
```

### Modifiers (Non-Destructive)

**Boolean Operations:**
```
boolean_operation(target_object="Cube", tool_object="Sphere", operation="DIFFERENCE")
```

**Arrays:**
```
create_array(object_name="Cube", count=5, offset=[2, 0, 0])
```

**Bevels:**
```
add_bevel(object_name="Cube", width=0.1, segments=3)
```

### Materials

**Basic Material:**
```
set_material(object_name="Cube", material_name="Red", color=[1, 0, 0])
```

**AI-Generated PBR:**
```
ai_generate_material(description="worn rusty metal", object_name="Cube")
```

### Animation

**Keyframes:**
```
set_animation_range(start=1, end=120)
insert_keyframe(object_name="Cube", property="location", frame=1, value=[0, 0, 0])
insert_keyframe(object_name="Cube", property="location", frame=60, value=[5, 0, 0])
```

**Turntable:**
```
create_turntable(object_name="Product", frames=120)
```

### Physics

**Rigid Body:**
```
add_rigid_body(object_name="Cube", body_type="ACTIVE", mass=1.0)
add_collision(object_name="Floor")
bake_physics(start=1, end=250)
```

**Cloth:**
```
add_cloth_simulation(object_name="Plane", preset="SILK")
```

### Rendering

**Quick Studio Setup:**
```
setup_studio_render(preset="PRODUCT")
```

**Custom Settings:**
```
set_render_settings(engine="CYCLES", samples=128, resolution=[1920, 1080])
configure_camera(camera_name="Camera", focal_length=50)
render_image(filepath="/tmp/render.png")
```

### Assets

**PolyHaven (Free):**
```
search_polyhaven_assets(asset_type="hdris", query="studio")
download_polyhaven_asset(asset_id="studio_small_03", asset_type="hdris")
```

**Sketchfab:**
```
search_sketchfab_models(query="chair", downloadable=True)
download_sketchfab_model(model_uid="abc123")
```

### Scene Organization

**Collections:**
```
create_collection(name="Furniture", color="COLOR_04")
move_to_collection(object_names=["Chair", "Table"], collection_name="Furniture")
```

**Export:**
```
export_scene(filepath="/tmp/scene.glb", format="GLTF")
save_blend(filepath="/tmp/project.blend")
```

## Recommended Workflows

### Product Visualization
1. `create_object` - Create or import product
2. `set_material` / `ai_generate_material` - Apply materials
3. `setup_studio_render` - Professional lighting
4. `create_turntable` - 360° animation
5. `render_animation` - Export video

### Architectural Visualization
1. Create geometry with `create_object` and `boolean_operation`
2. `search_polyhaven_assets` - Find textures and HDRIs
3. `download_polyhaven_asset` - Apply to scene
4. `configure_camera` - Set up views
5. `render_image` - High quality stills

### Physics Simulation
1. Create objects
2. `add_rigid_body` - Dynamic objects
3. `add_collision` - Static surfaces
4. `create_force_field` - Add forces if needed
5. `bake_physics` - Cache simulation
6. `render_animation` - Export result

### Character Setup
1. Import/create character mesh
2. `auto_rig_character` - Automatic rigging
3. `add_shape_key` - Facial expressions
4. `animate_shape_key` - Animate morphs
5. `bake_animation` - Finalize

## Error Handling

### Common Issues

**"Object not found"**
- Use `get_scene_info` to check exact object names
- Names are case-sensitive

**"Connection failed"**
- Verify Blender addon is running
- Check addon shows "Connected"
- Restart MCP server if needed

**"Operation failed"**
- Some operations require specific object types
- Boolean needs mesh objects
- Cloth needs mesh with enough geometry

## Performance Tips

1. Use lower subdivision/samples during development
2. Bake physics before final render
3. Use EEVEE for previews, CYCLES for final
4. Organize large scenes with collections

## Support

- Documentation: https://mithun50.github.io/blenderforge/
- Issues: https://github.com/mithun50/blenderforge/issues
- Team: @mithun50, @nevil06, @lekhanpro, @appukannadiga, @NextGenXplorer
