# Blender Python API Reference

Quick reference guide for Blender's Python API (`bpy`) commonly used with BlenderForge.

---

## Table of Contents

- [Overview](#overview)
- [Core Modules](#core-modules)
- [Scene and Objects](#scene-and-objects)
- [Mesh Operations](#mesh-operations)
- [Materials and Textures](#materials-and-textures)
- [Modifiers](#modifiers)
- [Animation](#animation)
- [Rendering](#rendering)
- [Common Patterns](#common-patterns)
- [BlenderForge Integration](#blenderforge-integration)
- [Resources](#resources)

---

## Overview

Blender's Python API (`bpy`) provides programmatic access to almost all of Blender's functionality. BlenderForge uses this API to execute commands sent from AI assistants.

### Importing bpy

```python
import bpy
```

### Key Concepts

| Concept | Description | Access |
|---------|-------------|--------|
| **Context** | Current state (selection, mode, etc.) | `bpy.context` |
| **Data** | All Blender data blocks | `bpy.data` |
| **Operators** | Actions/commands | `bpy.ops` |
| **Types** | Blender type definitions | `bpy.types` |
| **Props** | Custom properties | `bpy.props` |

---

## Core Modules

### bpy.context - Current State

```python
# Active objects and selections
bpy.context.scene           # Current scene
bpy.context.object          # Active object
bpy.context.selected_objects  # List of selected objects
bpy.context.view_layer      # Active view layer
bpy.context.mode            # Current mode ('OBJECT', 'EDIT', etc.)

# Examples
scene_name = bpy.context.scene.name
active_obj = bpy.context.object
selected = bpy.context.selected_objects
```

### bpy.data - Data Blocks

```python
# Access all data of a type
bpy.data.objects        # All objects
bpy.data.meshes         # All meshes
bpy.data.materials      # All materials
bpy.data.textures       # All textures
bpy.data.images         # All images
bpy.data.scenes         # All scenes
bpy.data.collections    # All collections
bpy.data.armatures      # All armatures
bpy.data.cameras        # All cameras
bpy.data.lights         # All lights

# Access by name
cube = bpy.data.objects['Cube']
mat = bpy.data.materials['Material']
```

### bpy.ops - Operators

```python
# Mesh primitives
bpy.ops.mesh.primitive_cube_add()
bpy.ops.mesh.primitive_uv_sphere_add()
bpy.ops.mesh.primitive_cylinder_add()
bpy.ops.mesh.primitive_plane_add()

# Object operations
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.object.duplicate()

# Transform
bpy.ops.transform.translate()
bpy.ops.transform.rotate()
bpy.ops.transform.resize()
```

---

## Scene and Objects

### Creating Objects

```python
# Add primitives at specific locations
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(2, 0, 0))
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(4, 0, 0))
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -1))
bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(6, 0, 0))
bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.25)

# Monkey (Suzanne)
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 2))

# Empty
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))

# Camera
bpy.ops.object.camera_add(location=(0, -5, 2))

# Light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 5))
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
```

### Accessing Objects

```python
# Get object by name
obj = bpy.data.objects.get('Cube')

# Check if object exists
if 'Cube' in bpy.data.objects:
    cube = bpy.data.objects['Cube']

# Get active object
active = bpy.context.object

# Get selected objects
selected = bpy.context.selected_objects
for obj in selected:
    print(obj.name)
```

### Object Properties

```python
obj = bpy.data.objects['Cube']

# Transform
obj.location = (1, 2, 3)
obj.rotation_euler = (0, 0, 0.785)  # Radians (45 degrees)
obj.scale = (2, 2, 2)

# Read transform
pos = obj.location
rot = obj.rotation_euler
scl = obj.scale

# Dimensions (bounding box)
dims = obj.dimensions

# Type
obj_type = obj.type  # 'MESH', 'CAMERA', 'LIGHT', etc.

# Visibility
obj.hide_viewport = False
obj.hide_render = False
```

### Object Selection

```python
import bpy

# Deselect all
bpy.ops.object.select_all(action='DESELECT')

# Select by name
obj = bpy.data.objects['Cube']
obj.select_set(True)

# Make active
bpy.context.view_layer.objects.active = obj

# Select all
bpy.ops.object.select_all(action='SELECT')

# Select by type
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
```

### Deleting Objects

```python
# Delete selected objects
bpy.ops.object.delete()

# Delete specific object
obj = bpy.data.objects.get('Cube')
if obj:
    bpy.data.objects.remove(obj)

# Delete all mesh objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj)
```

---

## Mesh Operations

### Creating Mesh from Scratch

```python
import bpy
import bmesh

# Create mesh data
mesh = bpy.data.meshes.new('CustomMesh')

# Create vertices and faces
vertices = [
    (-1, -1, 0),
    (1, -1, 0),
    (1, 1, 0),
    (-1, 1, 0),
]
edges = []
faces = [(0, 1, 2, 3)]

# Apply to mesh
mesh.from_pydata(vertices, edges, faces)
mesh.update()

# Create object from mesh
obj = bpy.data.objects.new('CustomObject', mesh)

# Link to scene
bpy.context.collection.objects.link(obj)
```

### BMesh Operations

```python
import bpy
import bmesh

# Get active object's mesh
obj = bpy.context.object
bm = bmesh.new()
bm.from_mesh(obj.data)

# Create a vertex
v = bm.verts.new((0, 0, 1))

# Update indices
bm.verts.ensure_lookup_table()

# Apply to mesh
bm.to_mesh(obj.data)
bm.free()
```

### Edit Mode Operations

```python
import bpy

# Enter edit mode
bpy.ops.object.mode_set(mode='EDIT')

# Select all vertices
bpy.ops.mesh.select_all(action='SELECT')

# Extrude
bpy.ops.mesh.extrude_region_move(
    TRANSFORM_OT_translate={"value": (0, 0, 1)}
)

# Subdivide
bpy.ops.mesh.subdivide(number_cuts=2)

# Return to object mode
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## Materials and Textures

### Creating Materials

```python
import bpy

# Create new material
mat = bpy.data.materials.new(name="MyMaterial")
mat.use_nodes = True

# Access node tree
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Get Principled BSDF node
bsdf = nodes.get('Principled BSDF')

# Set base color (RGBA)
bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)  # Red

# Set other properties
bsdf.inputs['Metallic'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Alpha'].default_value = 1.0
```

### Assigning Materials

```python
import bpy

# Get object and material
obj = bpy.data.objects['Cube']
mat = bpy.data.materials['MyMaterial']

# Assign to object
if obj.data.materials:
    obj.data.materials[0] = mat  # Replace first slot
else:
    obj.data.materials.append(mat)  # Add new slot
```

### Creating PBR Material with Nodes

```python
import bpy

def create_pbr_material(name, color, metallic=0.0, roughness=0.5):
    """Create a PBR material with the given properties."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    nodes.clear()

    # Add output node
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # Add Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    # Connect
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

# Usage
mat = create_pbr_material("Gold", (1, 0.8, 0), metallic=1.0, roughness=0.2)
```

### Loading Images as Textures

```python
import bpy

# Load image
img = bpy.data.images.load('/path/to/texture.png')

# Create material with image texture
mat = bpy.data.materials.new(name="TexturedMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Add image texture node
tex_node = nodes.new('ShaderNodeTexImage')
tex_node.image = img
tex_node.location = (-300, 0)

# Connect to Principled BSDF
bsdf = nodes.get('Principled BSDF')
links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
```

---

## Modifiers

### Adding Modifiers

```python
import bpy

obj = bpy.context.object

# Subdivision Surface
subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Mirror
mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
mirror.use_axis[0] = True  # X axis

# Array
array = obj.modifiers.new(name="Array", type='ARRAY')
array.count = 5
array.relative_offset_displace = (1.5, 0, 0)

# Boolean
boolean = obj.modifiers.new(name="Boolean", type='BOOLEAN')
boolean.operation = 'DIFFERENCE'
boolean.object = bpy.data.objects['Cutter']

# Bevel
bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.02
bevel.segments = 3
```

### Applying Modifiers

```python
import bpy

obj = bpy.context.object

# Apply all modifiers
for mod in obj.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)

# Apply specific modifier
bpy.ops.object.modifier_apply(modifier="Subsurf")
```

---

## Animation

### Setting Keyframes

```python
import bpy

obj = bpy.data.objects['Cube']

# Set location at frame 1
bpy.context.scene.frame_set(1)
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location", frame=1)

# Set location at frame 50
bpy.context.scene.frame_set(50)
obj.location = (5, 0, 0)
obj.keyframe_insert(data_path="location", frame=50)

# Other properties
obj.keyframe_insert(data_path="rotation_euler", frame=1)
obj.keyframe_insert(data_path="scale", frame=1)
```

### Creating Simple Animation

```python
import bpy
import math

obj = bpy.data.objects['Cube']

# Clear existing animation
obj.animation_data_clear()

# Create bouncing animation
for frame in range(1, 101):
    bpy.context.scene.frame_set(frame)

    # Calculate bounce
    t = frame / 100
    height = abs(math.sin(t * math.pi * 4)) * 2

    obj.location.z = height
    obj.keyframe_insert(data_path="location", index=2, frame=frame)
```

### Armature Animation

```python
import bpy

armature = bpy.data.objects['Armature']
bpy.context.view_layer.objects.active = armature
bpy.ops.object.mode_set(mode='POSE')

bone = armature.pose.bones['Bone']

# Set keyframes
bpy.context.scene.frame_set(1)
bone.rotation_quaternion = (1, 0, 0, 0)
bone.keyframe_insert(data_path="rotation_quaternion", frame=1)

bpy.context.scene.frame_set(30)
bone.rotation_quaternion = (0.707, 0.707, 0, 0)
bone.keyframe_insert(data_path="rotation_quaternion", frame=30)

bpy.ops.object.mode_set(mode='OBJECT')
```

---

## Rendering

### Render Settings

```python
import bpy

scene = bpy.context.scene

# Resolution
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Output format
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/path/to/output.png'

# Render engine
scene.render.engine = 'CYCLES'  # or 'BLENDER_EEVEE'

# Samples (Cycles)
scene.cycles.samples = 128
scene.cycles.preview_samples = 32

# Samples (EEVEE)
scene.eevee.taa_render_samples = 64
```

### Executing Render

```python
import bpy

# Render current frame
bpy.ops.render.render(write_still=True)

# Render animation
bpy.ops.render.render(animation=True)

# Render to viewport (for screenshots)
bpy.ops.render.opengl(write_still=True)
```

### HDRI Environment Setup

```python
import bpy

# Get world
world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear nodes
nodes.clear()

# Add Environment Texture
env_tex = nodes.new('ShaderNodeTexEnvironment')
env_tex.image = bpy.data.images.load('/path/to/hdri.hdr')

# Add Background node
background = nodes.new('ShaderNodeBackground')
background.inputs['Strength'].default_value = 1.0

# Add Output
output = nodes.new('ShaderNodeOutputWorld')

# Connect
links.new(env_tex.outputs['Color'], background.inputs['Color'])
links.new(background.outputs['Background'], output.inputs['Surface'])
```

---

## Common Patterns

### Safe Object Access

```python
def get_object_safe(name):
    """Get object by name, returning None if not found."""
    return bpy.data.objects.get(name)

# Usage
obj = get_object_safe('MaybeExists')
if obj:
    print(f"Found: {obj.name}")
```

### Context Override (Legacy)

```python
# For operators that require specific context
# Note: Blender 4.0+ prefers context.temp_override()

# Blender 4.0+
with bpy.context.temp_override(active_object=obj):
    bpy.ops.object.mode_set(mode='EDIT')

# Legacy method (pre-4.0)
override = {'active_object': obj, 'object': obj}
bpy.ops.object.mode_set(override, mode='EDIT')
```

### Clean Scene

```python
def clean_scene():
    """Remove all objects from scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Also clean orphan data
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)
```

### Get Scene Info

```python
def get_scene_info():
    """Get comprehensive scene information."""
    scene = bpy.context.scene
    objects = bpy.data.objects

    info = {
        'scene_name': scene.name,
        'frame_current': scene.frame_current,
        'frame_start': scene.frame_start,
        'frame_end': scene.frame_end,
        'render_engine': scene.render.engine,
        'objects': []
    }

    for obj in objects:
        obj_info = {
            'name': obj.name,
            'type': obj.type,
            'location': list(obj.location),
            'rotation': list(obj.rotation_euler),
            'scale': list(obj.scale),
        }
        info['objects'].append(obj_info)

    return info
```

---

## BlenderForge Integration

### Using with BlenderForge

When using BlenderForge, Python code is executed in Blender's context through the `execute_blender_code` tool.

**Example via AI:**
```
"Execute this code in Blender:
import bpy
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 2))
cube = bpy.context.active_object
cube.name = 'MyCube'"
```

### Common BlenderForge Patterns

**Create and Position Objects:**
```python
import bpy

# Clear selection
bpy.ops.object.select_all(action='DESELECT')

# Create object
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), size=2)
obj = bpy.context.active_object
obj.name = "AI_Cube"
```

**Apply Material:**
```python
import bpy

# Get or create material
mat_name = "AI_Material"
mat = bpy.data.materials.get(mat_name)
if not mat:
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True

# Set color
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)

# Apply to active object
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```

**Scene Query:**
```python
import bpy
import json

# Get scene info
info = {
    'objects': [
        {'name': obj.name, 'type': obj.type}
        for obj in bpy.data.objects
    ]
}

# Output as JSON (for BlenderForge to parse)
print(json.dumps(info))
```

---

## Resources

### Official Documentation

- **Blender Python API:** [docs.blender.org/api/current](https://docs.blender.org/api/current/)
- **Blender Manual - Python:** [docs.blender.org/manual/en/latest/advanced/scripting](https://docs.blender.org/manual/en/latest/advanced/scripting/)

### Quick Reference

- **bpy.types:** [docs.blender.org/api/current/bpy.types.html](https://docs.blender.org/api/current/bpy.types.html)
- **bpy.ops:** [docs.blender.org/api/current/bpy.ops.html](https://docs.blender.org/api/current/bpy.ops.html)
- **bpy.data:** [docs.blender.org/api/current/bpy.data.html](https://docs.blender.org/api/current/bpy.data.html)

### Community Resources

- **Blender Stack Exchange:** [blender.stackexchange.com](https://blender.stackexchange.com/)
- **Blender Artists Forum:** [blenderartists.org](https://www.blenderartists.org/)
- **Blender Developers:** [developer.blender.org](https://developer.blender.org/)

### Learning Resources

- **Blender Scripting Playlist:** YouTube tutorials on Blender Python
- **Scripting for Artists:** Blender official video series
