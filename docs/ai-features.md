# AI-Powered Features

BlenderForge includes powerful AI-assisted tools that enhance your 3D workflow through intelligent automation and natural language processing.

---

## Overview

| Feature | Description |
|---------|-------------|
| **AI Material Generator** | Create PBR materials from text descriptions or reference images |
| **Natural Language Modeling** | Create and modify 3D objects using plain English |
| **AI Scene Analyzer** | Get professional critique and improvement suggestions |
| **Smart Auto-Rig** | Automatically rig characters with proper bone hierarchies |

---

## AI Material Generator

Generate physically-based rendering (PBR) materials using natural language descriptions or reference images.

### generate_material_from_text

Create a PBR material from a text description.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | Natural language description of the material |
| `material_name` | string | No | Name for the material (default: "AI_Material") |

**Supported Keywords**:

| Category | Keywords |
|----------|----------|
| **Surface** | rusty, glossy, matte, rough, smooth, polished, weathered, worn |
| **Material** | metal, metallic, wood, wooden, stone, rock, fabric, cloth, glass, plastic, organic, skin |
| **Effects** | transparent, translucent, emissive, glowing, reflective, shiny |

**Example Usage**:
```
"Create a rusty metal material for my robot"
"Generate a polished wooden floor texture"
"Make a glowing blue crystal material"
```

**Returns**:
```json
{
  "material_name": "RustyMetal",
  "properties_applied": ["metallic", "roughness", "base_color"],
  "base_color": [0.45, 0.25, 0.15, 1.0],
  "metallic": 0.9,
  "roughness": 0.8
}
```

---

### generate_material_from_image

Create a PBR material by analyzing a reference image's colors and textures.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_path` | string | Yes | Path to the reference image |
| `material_name` | string | No | Name for the material (default: "AI_Material") |

**How It Works**:
1. Analyzes the image to extract dominant colors
2. Estimates surface properties from color distribution
3. Creates a Principled BSDF material with appropriate settings
4. Optionally uses the image as a texture

**Example Usage**:
```
"Create a material based on this marble photo"
"Generate material from my fabric sample image"
```

---

### list_material_presets

Get available AI material presets for quick application.

**Parameters**: None

**Available Presets**:

| Preset | Description |
|--------|-------------|
| `metal` | Metallic surface with moderate roughness |
| `wood` | Warm brown organic material |
| `stone` | Gray rough mineral surface |
| `fabric` | Soft matte cloth material |
| `glass` | Transparent with high transmission |
| `plastic` | Smooth synthetic material |
| `organic` | Skin-like subsurface material |

**Returns**:
```json
{
  "presets": ["metal", "wood", "stone", "fabric", "glass", "plastic", "organic"],
  "count": 7
}
```

---

## Natural Language Modeling

Create and modify 3D objects using plain English descriptions.

### create_from_description

Create 3D objects from natural language descriptions.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | string | Yes | Natural language description of what to create |

**Supported Primitives**:
- `cube`, `box` - Rectangular shapes
- `sphere`, `ball` - Round shapes
- `cylinder`, `tube`, `pipe` - Cylindrical shapes
- `plane`, `floor`, `ground` - Flat surfaces
- `cone` - Conical shapes
- `torus`, `donut`, `ring` - Ring shapes
- `circle` - Circle meshes

**Supported Colors**:
Red, blue, green, yellow, orange, purple, pink, cyan, magenta, white, black, gray/grey, brown, gold, silver, bronze, copper, navy, maroon, olive, teal, coral, salmon, turquoise, indigo, violet, crimson, emerald, amber, ivory, beige, tan, khaki, lavender, mint

**Size Parsing**:
- "2 meters tall" - Height specification
- "50 centimeters wide" - Width in cm
- "3 units" - Generic Blender units

**Complex Objects**:

| Object | Description |
|--------|-------------|
| `table` | Four-legged table with top surface |
| `chair` | Chair with seat, back, and four legs |
| `stairs` | 5-step staircase |

**Example Usage**:
```
"Create a red cube 2 meters tall"
"Add a blue sphere at position 5, 0, 0"
"Make a wooden table"
"Create a simple chair"
"Add 3 green cylinders in a row"
```

**Returns**:
```json
{
  "created_objects": ["Cube"],
  "count": 1,
  "properties": {
    "color": [1.0, 0.0, 0.0, 1.0],
    "scale": [1.0, 1.0, 2.0]
  }
}
```

---

### modify_from_description

Modify existing objects using natural language.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_name` | string | Yes | Name of the object to modify |
| `modification` | string | Yes | Description of the modification |

**Supported Modifications**:

| Type | Examples |
|------|----------|
| **Color** | "make it red", "change color to blue" |
| **Scale** | "make it bigger", "scale to 2x", "double the size" |
| **Position** | "move up", "move to 5, 0, 3" |
| **Rotation** | "rotate 45 degrees", "flip upside down" |

**Example Usage**:
```
"Make the cube red"
"Scale the sphere to twice its size"
"Move the chair to position 3, 0, 0"
"Rotate the table 90 degrees on Z axis"
```

---

## AI Scene Analyzer

Get professional analysis and improvement suggestions for your scene.

### analyze_scene_composition

Analyze the current scene and provide detailed critique with scores.

**Parameters**: None

**Analysis Categories**:

| Category | What It Checks |
|----------|----------------|
| **Lighting** | Light count, types, energy levels, shadows |
| **Composition** | Object distribution, camera placement, balance |
| **Materials** | Material usage, variety, quality settings |

**Returns**:
```json
{
  "lighting": {
    "score": 75,
    "issues": ["Single light source creates harsh shadows"],
    "suggestions": ["Add fill light to soften shadows", "Consider 3-point lighting setup"]
  },
  "composition": {
    "score": 80,
    "object_count": 5,
    "has_camera": true,
    "issues": ["Objects clustered in one area"],
    "suggestions": ["Distribute objects for better balance"]
  },
  "materials": {
    "score": 60,
    "total_materials": 3,
    "objects_without_materials": 2,
    "issues": ["Some objects lack materials"],
    "suggestions": ["Add materials to all visible objects"]
  },
  "overall_score": 72
}
```

**Scoring System**:
- 90-100: Professional quality
- 70-89: Good with minor improvements needed
- 50-69: Needs work in several areas
- Below 50: Significant improvements required

---

### get_improvement_suggestions

Get specific, actionable improvement recommendations.

**Parameters**: None

**Suggestion Categories**:
- Lighting setup improvements
- Composition adjustments
- Material enhancements
- Performance optimizations
- Camera positioning tips

---

### auto_optimize_lighting

Automatically set up professional lighting based on a style preset.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `style` | string | No | Lighting style (default: "studio") |

**Available Styles**:

| Style | Description |
|-------|-------------|
| `studio` | 3-point lighting (key, fill, back) - ideal for products |
| `outdoor` | Sun lamp with sky-like ambient |
| `dramatic` | High-contrast single key light |
| `soft` | Even, diffused area lighting |
| `product` | Clean white lighting for showcasing |
| `cinematic` | Warm key with cool fill, rim accent |

**Example Usage**:
```
"Set up studio lighting for my product shot"
"Create dramatic lighting for the character"
"Use cinematic lighting for the scene"
```

**Returns**:
```json
{
  "style": "studio",
  "lights_created": ["Key_Light", "Fill_Light", "Back_Light"],
  "description": "3-point studio lighting setup"
}
```

---

## Smart Auto-Rig

Automatically create armatures and rig characters for animation.

### auto_rig_character

Automatically create an armature for a mesh based on its proportions.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mesh_name` | string | Yes | Name of the mesh to rig |
| `rig_type` | string | No | Type of rig (default: "humanoid") |

**Rig Types**:

| Type | Bones Created | Best For |
|------|--------------|----------|
| `humanoid` | Spine, hips, legs (with IK), arms, head | Human characters |
| `quadruped` | Spine, hips, 4 legs, tail, head | Animals |
| `simple` | Root, spine chain, head | Simple objects |

**Humanoid Bone Structure**:
```
Root
└── Spine
    ├── Spine.001
    │   └── Head
    ├── Arm.L → Forearm.L → Hand.L
    ├── Arm.R → Forearm.R → Hand.R
    └── Hips
        ├── Leg.L → Shin.L → Foot.L
        └── Leg.R → Shin.R → Foot.R
```

**Example Usage**:
```
"Rig my character mesh with humanoid bones"
"Create a quadruped rig for the dog model"
"Add a simple rig to the tentacle"
```

**Returns**:
```json
{
  "armature_name": "Character_Armature",
  "bones_created": 15,
  "rig_type": "humanoid",
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

**How It Works**:
1. Parents mesh to armature
2. Applies automatic weights based on bone proximity
3. Creates vertex groups for each bone

---

### add_ik_controls

Add Inverse Kinematics constraints for easier animation.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `armature_name` | string | Yes | Armature to add IK to |
| `limb` | string | No | Specific limb ("arm_l", "arm_r", "leg_l", "leg_r") or "all" |

**IK Setup**:
- Creates IK target bones (e.g., "Hand.L.IK")
- Adds IK constraints with proper chain length
- Sets up pole targets for knee/elbow direction

---

## Best Practices

### Material Generation
- Be specific with descriptions: "worn leather with scratches" vs just "leather"
- Combine keywords for complex materials: "glossy blue metallic"
- Use presets as starting points, then customize

### Natural Language Modeling
- Start simple, add details incrementally
- Use specific measurements when size matters
- Combine with material generation for complete objects

### Scene Analysis
- Run analysis after major changes
- Address highest-impact suggestions first
- Re-analyze to verify improvements

### Auto-Rigging
- Ensure mesh is in T-pose or A-pose for humanoid rigs
- Check mesh proportions match expected rig type
- Adjust weights manually for fine control after auto-rig

---

## Integration Examples

### Complete Workflow: Character Setup
```
1. "Create a humanoid character mesh"
2. "Auto-rig the character with humanoid skeleton"
3. "Add IK controls to all limbs"
4. "Generate a skin-like material for the character"
5. "Set up studio lighting"
6. "Analyze the scene for improvements"
```

### Quick Product Visualization
```
1. "Create a cylinder for my product base"
2. "Generate a glossy white plastic material"
3. "Set up product lighting"
4. "Take a viewport screenshot"
```

### Environment Setup
```
1. "Create a wooden table"
2. "Add 4 simple chairs around the table"
3. "Generate a wooden floor material"
4. "Set up soft ambient lighting"
5. "Analyze composition and adjust"
```
