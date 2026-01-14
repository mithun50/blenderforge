# Asset Integrations

BlenderForge integrates with several asset services to provide textures, HDRIs, 3D models, and AI-generated content.

---

## Overview

| Service | Type | API Key Required | Cost |
|---------|------|------------------|------|
| PolyHaven | Textures, HDRIs, Models | No | Free |
| Sketchfab | 3D Models | Yes | Freemium |
| Hyper3D Rodin | AI-Generated Models | Yes | Free trial |
| Hunyuan3D | AI-Generated Models | Yes | Pay-per-use |

---

## PolyHaven

[PolyHaven](https://polyhaven.com/) provides **free, high-quality** assets for 3D projects.

### What's Available

| Asset Type | Count | Description |
|------------|-------|-------------|
| **HDRIs** | 600+ | High dynamic range environment maps |
| **Textures** | 1500+ | PBR texture sets (diffuse, roughness, normal) |
| **Models** | 100+ | 3D models with textures |

### Setup

1. Open Blender with BlenderForge addon enabled
2. Press `N` to open the sidebar
3. Go to **BlenderForge** tab
4. Check **Use PolyHaven**

No API key is required.

### Usage Examples

```
"Search for wood textures on PolyHaven"
"Download the 'studio_small_09' HDRI"
"Get a brick texture and apply it to the wall"
"List outdoor HDRI environments"
```

### Asset Categories

**HDRIs**:
- `outdoor` - Outdoor environments
- `indoor` - Indoor environments
- `studio` - Studio lighting setups
- `nature` - Natural landscapes
- `urban` - City environments

**Textures**:
- `wood` - Wood surfaces
- `brick` - Brick walls
- `concrete` - Concrete surfaces
- `fabric` - Fabric and cloth
- `metal` - Metallic surfaces
- `ground` - Ground and terrain

**Models**:
- `furniture` - Tables, chairs, etc.
- `props` - Decorative objects
- `nature` - Plants, rocks

---

## Sketchfab

[Sketchfab](https://sketchfab.com/) is a marketplace for 3D models with millions of assets.

### What's Available

- **Millions** of 3D models
- Free and paid content
- Many downloadable under Creative Commons
- Animated models
- High-quality scanned objects

### Setup

1. **Get an API key**:
   - Create a Sketchfab account at [sketchfab.com](https://sketchfab.com/)
   - Go to Settings → API
   - Copy your API token

2. **Configure in Blender**:
   - Open BlenderForge panel (`N` key)
   - Check **Use Sketchfab**
   - Enter your API key

### Usage Examples

```
"Search Sketchfab for coffee mug"
"Find downloadable character models"
"Get a preview of model uid abc123"
"Download and import the selected model"
```

### Tips

- Use `downloadable: true` to filter for models you can import
- Check license before using in commercial projects
- Preview models before downloading to save time

---

## Hyper3D Rodin

[Hyper3D](https://hyper3d.ai/) provides AI-powered 3D model generation from text or images.

### What It Does

- **Text-to-3D**: Describe what you want, get a 3D model
- **Image-to-3D**: Upload reference images, get a 3D model
- High-quality mesh output
- Supports various styles (realistic, stylized, game-ready)

### Setup

1. **Get API credentials**:
   - Sign up at [hyper3d.ai](https://hyper3d.ai/)
   - Free trial credits available
   - Copy your API key

2. **Configure in Blender**:
   - Open BlenderForge panel
   - Check **Use Hyper3D Rodin**
   - Enter your API key

### Usage Examples

```
"Generate a 3D model of a medieval sword"
"Create a stylized coffee cup from this description"
"Generate a model from these reference images"
"Check the status of my generation job"
"Import the completed model"
```

### Quality Settings

| Quality | Time | Credits | Best For |
|---------|------|---------|----------|
| `draft` | ~15s | 1 | Quick previews |
| `standard` | ~30s | 2 | General use |
| `high` | ~60s | 5 | Final assets |

### Workflow

1. **Submit generation request** → Get job ID
2. **Poll job status** → Wait for completion
3. **Import model** → Add to Blender scene

---

## Hunyuan3D

[Hunyuan3D](https://cloud.tencent.com/) is Tencent's AI 3D generation service.

### What It Does

- Text-to-3D generation
- Image-to-3D generation
- High-quality mesh output
- Fast generation times

### Setup

1. **Get Tencent Cloud credentials**:
   - Create account at [cloud.tencent.com](https://cloud.tencent.com/)
   - Enable Hunyuan3D API
   - Get your Secret ID and Secret Key

2. **Configure in Blender**:
   - Open BlenderForge panel
   - Check **Use Hunyuan3D**
   - Enter your Tencent Secret ID
   - Enter your Tencent Secret Key

### Usage Examples

```
"Generate a 3D model using Hunyuan: a cute cartoon cat"
"Create a model from this image using Hunyuan3D"
"Check Hunyuan generation status"
```

### Notes

- Requires valid Tencent Cloud account with billing
- Pricing varies by usage
- Results may differ from Hyper3D Rodin

---

## Comparison

### Which Service to Use?

| Use Case | Recommended Service |
|----------|---------------------|
| Free textures and HDRIs | PolyHaven |
| Specific real-world objects | Sketchfab |
| Custom objects from description | Hyper3D Rodin |
| Alternative AI generation | Hunyuan3D |

### Quality Comparison

| Aspect | PolyHaven | Sketchfab | Hyper3D | Hunyuan3D |
|--------|-----------|-----------|---------|-----------|
| Texture Quality | Excellent | Varies | N/A | N/A |
| Model Quality | Good | Excellent | Good | Good |
| Customization | None | None | Full | Full |
| Speed | Instant | Instant | 15-60s | 15-60s |
| Cost | Free | Freemium | Credits | Pay-per-use |

---

## Best Practices

### Textures and Materials

1. Start with PolyHaven for common materials (wood, brick, metal)
2. Download at appropriate resolution (2K for most uses, 4K for close-ups)
3. Use the `set_texture` tool to apply properly with UV mapping

### 3D Models

1. Search Sketchfab first for existing models
2. Use AI generation for custom/unique objects
3. Check polygon count before importing large models

### AI Generation

1. Be specific in your prompts
2. Start with `draft` quality to test
3. Use reference images for better results
4. Multiple iterations may be needed

### Performance

- Don't download 8K textures unless necessary
- Limit AI generation to what you need
- Cache frequently used assets locally
