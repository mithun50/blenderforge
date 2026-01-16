# BlenderForge Server
# Copyright (c) 2025 BlenderForge Team
#   - Mithun Gowda B <mithungowda.b7411@gmail.com> (mithun50)
#   - Nevil D'Souza <nevilansondsouza@gmail.com> (nevil06)
#   - Lekhan H R (lekhanpro)
#   - Manvanth Gowda M <appuka1431@gmail.com> (appukannadiga)
#   - NXG Team (Organization) <nxgextra@gmail.com> (NextGenXplorer)
# Licensed under the MIT License

import base64
import re
import json
import logging
import os
import socket
import tempfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mcp.server.fastmcp import Context, FastMCP, Image

# Import telemetry
from .telemetry import record_startup
from .telemetry_decorator import telemetry_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("BlenderForgeServer")

# Default configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876

# Security configuration
CODE_EXECUTION_ENABLED = os.getenv("BLENDERFORGE_ALLOW_CODE_EXECUTION", "true").lower() == "true"

# Dangerous patterns that should be blocked in code execution
DANGEROUS_CODE_PATTERNS = [
    r"\bos\.system\b",
    r"\bsubprocess\b",
    r"\b__import__\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bopen\s*\([^)]*['\"][wa]",  # Writing to files
    r"\bshutil\.rmtree\b",
    r"\bos\.remove\b",
    r"\bos\.unlink\b",
    r"\bos\.rmdir\b",
    r"\bsocket\b",
    r"\brequests\b",
    r"\burllib\b",
    r"\bhttp\b",
]

# Allowed safe imports for code execution
ALLOWED_IMPORTS = {
    "bpy", "bmesh", "mathutils", "math", "random", "json", "re",
    "collections", "itertools", "functools", "typing",
}


def validate_code_security(code: str) -> tuple[bool, str]:
    """
    Validate code for potentially dangerous patterns.

    Returns:
        Tuple of (is_safe, error_message)
    """
    if not CODE_EXECUTION_ENABLED:
        return False, "Code execution is disabled. Set BLENDERFORGE_ALLOW_CODE_EXECUTION=true to enable."

    # Check for dangerous patterns
    for pattern in DANGEROUS_CODE_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Code contains potentially dangerous pattern: {pattern}"

    # Check for suspicious imports
    # We only care about the base module, not what's imported from it
    # "from collections import defaultdict" -> check "collections" (allowed)
    # "import os" -> check "os" (not allowed)

    # Pattern for "from X import Y" - capture the module X
    from_pattern = r"^\s*from\s+(\w+(?:\.\w+)*)\s+import"
    # Pattern for "import X" at start of line - capture the module X
    import_pattern = r"^\s*import\s+(\w+(?:\.\w+)*)"

    for line in code.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Check "from X import" pattern
        from_match = re.match(from_pattern, line)
        if from_match:
            module = from_match.group(1)
            base_module = module.split(".")[0]
            if base_module not in ALLOWED_IMPORTS:
                return False, f"Import from '{module}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_IMPORTS))}"
            continue

        # Check "import X" pattern
        import_match = re.match(import_pattern, line)
        if import_match:
            module = import_match.group(1)
            base_module = module.split(".")[0]
            if base_module not in ALLOWED_IMPORTS:
                return False, f"Import of '{module}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_IMPORTS))}"

    return True, ""


@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict
    auth_token: str = None  # Authentication token
    max_retries: int = 3  # Maximum connection retry attempts
    retry_delay: float = 1.0  # Delay between retries in seconds

    def connect(self, retries: int = None) -> bool:
        """Connect to the Blender addon socket server with retry logic"""
        if self.sock:
            return True

        max_attempts = retries if retries is not None else self.max_retries

        for attempt in range(max_attempts):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(10.0)  # Connection timeout
                self.sock.connect((self.host, self.port))

                # Try to get auth token from environment
                self.auth_token = os.getenv("BLENDERFORGE_AUTH_TOKEN")

                logger.info(f"Connected to Blender at {self.host}:{self.port}")
                return True
            except TimeoutError:
                logger.warning(f"Connection attempt {attempt + 1}/{max_attempts} timed out")
                self.sock = None
            except ConnectionRefusedError:
                logger.warning(
                    f"Connection attempt {attempt + 1}/{max_attempts} refused - is Blender addon running?"
                )
                self.sock = None
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1}/{max_attempts} failed: {str(e)}")
                self.sock = None

            if attempt < max_attempts - 1:
                import time

                time.sleep(self.retry_delay)

        logger.error(f"Failed to connect to Blender after {max_attempts} attempts")
        return False

    def disconnect(self):
        """Disconnect from the Blender addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Blender: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(180.0)  # Match the addon's timeout

        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception("Connection closed before receiving any data")
                        break

                    chunks.append(chunk)

                    # Check if we've received a complete JSON object
                    try:
                        data = b"".join(chunks)
                        json.loads(data.decode("utf-8"))
                        # If we get here, it parsed successfully
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except TimeoutError:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except TimeoutError:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise

        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b"".join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode("utf-8"))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("Timeout: No data received")

    def send_command(self, command_type: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Send a command to Blender and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")

        command = {"type": command_type, "params": params or {}}

        # Include auth token if available
        if self.auth_token:
            command["auth_token"] = self.auth_token

        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")

            # Send the command
            self.sock.sendall(json.dumps(command).encode("utf-8"))
            logger.info("Command sent, waiting for response...")

            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(180.0)  # Match the addon's timeout

            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")

            response = json.loads(response_data.decode("utf-8"))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")

            if response.get("status") == "error":
                logger.error(f"Blender error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Blender"))

            return response.get("result", {})
        except TimeoutError:
            logger.error("Socket timeout while waiting for response from Blender")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Blender response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Blender lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Blender: {str(e)}")
            # Try to log what was received
            if "response_data" in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Blender: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Blender: {str(e)}")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            self.sock = None
            raise Exception(f"Communication error with Blender: {str(e)}")


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    # We don't need to create a connection here since we're using the global connection
    # for resources and tools

    try:
        # Just log that we're starting up
        logger.info("BlenderForge server starting up")

        # Record startup event for telemetry
        try:
            record_startup()
        except Exception as e:
            logger.debug(f"Failed to record startup telemetry: {e}")

        # Try to connect to Blender on startup to verify it's available
        try:
            # This will initialize the global connection if needed
            blender = get_blender_connection()
            logger.info("Successfully connected to Blender on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Blender on startup: {str(e)}")
            logger.warning(
                "Make sure the Blender addon is running before using Blender resources or tools"
            )

        # Return an empty context - we're using the global connection
        yield {}
    finally:
        # Clean up the global connection on shutdown
        global _blender_connection
        if _blender_connection:
            logger.info("Disconnecting from Blender on shutdown")
            _blender_connection.disconnect()
            _blender_connection = None
        logger.info("BlenderForge server shut down")


# MCP Server Instructions for AI Clients
MCP_INSTRUCTIONS = """
# BlenderForge MCP - AI Instructions

You are connected to BlenderForge, an MCP server for controlling Blender through natural language.

## Quick Start
1. Always call `get_scene_info` first to understand the current scene state
2. Use meaningful object names (e.g., "Chair_Main" not "Cube.001")
3. Organize complex scenes with `create_collection` and `move_to_collection`
4. Save work frequently with `save_blend`

## Tool Categories (84 tools available)

### Scene & Objects
- `get_scene_info` - Get scene overview (ALWAYS START HERE)
- `get_object_info` - Get specific object details
- `create_object` - Create primitives (CUBE, SPHERE, CYLINDER, CONE, TORUS, PLANE, etc.)
- `set_object_transform` - Set location, rotation, scale
- `nlp_create_object` - Create objects from natural language description

### Modifiers (Non-Destructive Editing)
- `boolean_operation` - Union, Difference, Intersect between objects
- `add_modifier` - Add any Blender modifier
- `create_array` - Array with count and offset
- `add_bevel` - Bevel edges with width and segments
- `mirror_object` - Mirror across X, Y, or Z axis
- `subdivide_smooth` - Subdivision surface smoothing

### Mesh Editing
- `extrude_faces` - Extrude selected faces
- `inset_faces` - Inset faces with thickness
- `loop_cut` - Add loop cuts to mesh
- `merge_vertices` - Merge vertices by distance
- `join_objects` - Combine multiple objects into one
- `separate_by_loose` - Separate disconnected parts

### Materials & Textures
- `set_material` - Apply or create materials with color
- `ai_generate_material` - AI-powered PBR material from description

### Animation
- `insert_keyframe` - Add keyframe for location/rotation/scale
- `set_animation_range` - Set start and end frames
- `create_turntable` - 360° rotation animation for product shots
- `add_shape_key` - Add morph targets
- `animate_path` - Animate object along a curve
- `bake_animation` - Bake simulation to keyframes

### Physics Simulation
- `add_rigid_body` - Add physics (ACTIVE for dynamic, PASSIVE for static)
- `add_cloth_simulation` - Cloth physics with presets (COTTON, SILK, LEATHER, etc.)
- `add_collision` - Make object a collision surface
- `create_force_field` - Add forces (WIND, VORTEX, TURBULENCE)
- `add_particle_system` - Particle emitter
- `bake_physics` - Cache physics simulation

### Camera & Rendering
- `create_camera` - Add camera to scene
- `configure_camera` - Set focal length, DOF, aperture
- `camera_look_at` - Point camera at target
- `set_render_settings` - Engine (CYCLES/EEVEE), samples, resolution
- `render_image` - Render current frame to file
- `render_animation` - Render frame sequence
- `setup_studio_render` - One-click professional studio lighting

### Curves & Text
- `create_bezier_curve` - Create curve from control points
- `create_text_object` - 3D text with font and extrusion
- `curve_to_mesh` - Convert curve to mesh
- `create_pipe` - Create pipe/tube along curve

### Scene Organization
- `create_collection` - Create object groups
- `move_to_collection` - Organize objects
- `save_blend` - Save .blend file
- `export_scene` - Export to FBX, glTF, OBJ formats
- `purge_unused` - Clean up unused data

### Asset Libraries
- `get_polyhaven_status` - Check PolyHaven availability
- `search_polyhaven_assets` - Search free HDRIs, textures, models
- `download_polyhaven_asset` - Download and apply assets
- `search_sketchfab_models` - Search Sketchfab marketplace
- `download_sketchfab_model` - Import 3D models

### AI-Powered Features
- `ai_generate_material` - Generate PBR materials from text description
- `nlp_create_object` - Create objects using natural language
- `ai_analyze_scene` - Get professional scene critique with scores
- `auto_rig_character` - Automatic character rigging
- `auto_lighting` - Apply studio/cinematic/dramatic lighting presets

### Procedural Generation
- `scatter_on_surface` - Distribute objects on mesh surface
- `create_procedural_terrain` - Generate terrain with noise

## Recommended Workflows

### Product Visualization
1. `get_scene_info` - Check scene
2. `create_object` or import - Add product
3. `set_material` / `ai_generate_material` - Materials
4. `setup_studio_render` - Professional lighting
5. `create_turntable` - 360° animation
6. `render_animation` - Export

### Hard Surface Modeling
1. `create_object` - Base shape
2. `boolean_operation` - Cut/combine shapes
3. `add_bevel` - Refine edges
4. `set_material` - Apply materials

### Physics Animation
1. Create objects
2. `add_rigid_body` (ACTIVE) - Moving objects
3. `add_collision` - Ground/walls
4. `bake_physics` - Cache simulation
5. `render_animation` - Export

## Best Practices
- Prefer modifiers over direct mesh editing (non-destructive)
- Use collections to organize large scenes
- Set up cameras before final rendering
- Bake physics before rendering animations
- Use EEVEE for fast previews, CYCLES for final quality

## Error Handling
- If "Object not found": Use `get_scene_info` to check exact names
- If connection fails: Ensure Blender addon shows "Connected"
- Names are case-sensitive

## Team
BlenderForge by @mithun50, @nevil06, @lekhanpro, @appukannadiga, @NextGenXplorer
Documentation: https://mithun50.github.io/blenderforge/
"""

# Create the MCP server with lifespan support and instructions
mcp = FastMCP("BlenderForge", lifespan=server_lifespan, instructions=MCP_INSTRUCTIONS)

# Resource endpoints

# Global connection for resources (since resources can't access context)
_blender_connection = None
_polyhaven_enabled = False  # Add this global variable


def get_blender_connection():
    """Get or create a persistent Blender connection"""
    global _blender_connection, _polyhaven_enabled  # Add _polyhaven_enabled to globals

    # If we have an existing connection, check if it's still valid
    if _blender_connection is not None:
        try:
            # First check if PolyHaven is enabled by sending a ping command
            result = _blender_connection.send_command("get_polyhaven_status")
            # Store the PolyHaven status globally
            _polyhaven_enabled = result.get("enabled", False)
            return _blender_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _blender_connection.disconnect()
            except:
                pass
            _blender_connection = None

    # Create a new connection if needed
    if _blender_connection is None:
        host = os.getenv("BLENDER_HOST", DEFAULT_HOST)
        port = int(os.getenv("BLENDER_PORT", DEFAULT_PORT))
        _blender_connection = BlenderConnection(host=host, port=port)
        if not _blender_connection.connect():
            logger.error("Failed to connect to Blender")
            _blender_connection = None
            raise Exception("Could not connect to Blender. Make sure the Blender addon is running.")
        logger.info("Created new persistent connection to Blender")

    return _blender_connection


@telemetry_tool("get_scene_info")
@mcp.tool()
def get_scene_info(ctx: Context) -> str:
    """Get detailed information about the current Blender scene"""
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_scene_info")

        # Just return the JSON representation of what Blender sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scene info from Blender: {str(e)}")
        return f"Error getting scene info: {str(e)}"


@telemetry_tool("get_object_info")
@mcp.tool()
def get_object_info(ctx: Context, object_name: str) -> str:
    """
    Get detailed information about a specific object in the Blender scene.

    Parameters:
    - object_name: The name of the object to get information about
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_object_info", {"name": object_name})

        # Just return the JSON representation of what Blender sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting object info from Blender: {str(e)}")
        return f"Error getting object info: {str(e)}"


@telemetry_tool("get_viewport_screenshot")
@mcp.tool()
def get_viewport_screenshot(ctx: Context, max_size: int = 800) -> Image:
    """
    Capture a screenshot of the current Blender 3D viewport.

    Parameters:
    - max_size: Maximum size in pixels for the largest dimension (default: 800)

    Returns the screenshot as an Image.
    """
    try:
        blender = get_blender_connection()

        # Create temp file path
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"blender_screenshot_{os.getpid()}.png")

        result = blender.send_command(
            "get_viewport_screenshot",
            {"max_size": max_size, "filepath": temp_path, "format": "png"},
        )

        if "error" in result:
            raise Exception(result["error"])

        if not os.path.exists(temp_path):
            raise Exception("Screenshot file was not created")

        # Read the file
        with open(temp_path, "rb") as f:
            image_bytes = f.read()

        # Delete the temp file
        os.remove(temp_path)

        return Image(data=image_bytes, format="png")

    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        raise Exception(f"Screenshot failed: {str(e)}")


@telemetry_tool("execute_blender_code")
@mcp.tool()
def execute_blender_code(ctx: Context, code: str) -> str:
    """
    Execute Python code in Blender with security validation.

    Parameters:
    - code: The Python code to execute (must use only allowed imports: bpy, bmesh, mathutils, math, random, json, re, collections, itertools, functools, typing)

    Security:
    - Code is validated against dangerous patterns (os.system, subprocess, eval, exec, etc.)
    - Only Blender-safe imports are allowed
    - Can be disabled via BLENDERFORGE_ALLOW_CODE_EXECUTION=false environment variable
    """
    # Security validation
    is_safe, error_msg = validate_code_security(code)
    if not is_safe:
        logger.warning(f"Code security validation failed: {error_msg}")
        return f"Security validation failed: {error_msg}"

    try:
        # Get the global connection
        blender = get_blender_connection()
        result = blender.send_command("execute_code", {"code": code})
        return f"Code executed successfully: {result.get('result', '')}"
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return f"Error executing code: {str(e)}"


@telemetry_tool("get_polyhaven_categories")
@mcp.tool()
def get_polyhaven_categories(ctx: Context, asset_type: str = "hdris") -> str:
    """
    Get a list of categories for a specific asset type on Polyhaven.

    Parameters:
    - asset_type: The type of asset to get categories for (hdris, textures, models, all)
    """
    try:
        blender = get_blender_connection()
        if not _polyhaven_enabled:
            return "PolyHaven integration is disabled. Select it in the sidebar in BlenderForge, then run it again."
        result = blender.send_command("get_polyhaven_categories", {"asset_type": asset_type})

        if "error" in result:
            return f"Error: {result['error']}"

        # Format the categories in a more readable way
        categories = result["categories"]
        formatted_output = f"Categories for {asset_type}:\n\n"

        # Sort categories by count (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

        for category, count in sorted_categories:
            formatted_output += f"- {category}: {count} assets\n"

        return formatted_output
    except Exception as e:
        logger.error(f"Error getting Polyhaven categories: {str(e)}")
        return f"Error getting Polyhaven categories: {str(e)}"


@telemetry_tool("search_polyhaven_assets")
@mcp.tool()
def search_polyhaven_assets(ctx: Context, asset_type: str = "all", categories: str = None) -> str:
    """
    Search for assets on Polyhaven with optional filtering.

    Parameters:
    - asset_type: Type of assets to search for (hdris, textures, models, all)
    - categories: Optional comma-separated list of categories to filter by

    Returns a list of matching assets with basic information.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "search_polyhaven_assets", {"asset_type": asset_type, "categories": categories}
        )

        if "error" in result:
            return f"Error: {result['error']}"

        # Format the assets in a more readable way
        assets = result["assets"]
        total_count = result["total_count"]
        returned_count = result["returned_count"]

        formatted_output = f"Found {total_count} assets"
        if categories:
            formatted_output += f" in categories: {categories}"
        formatted_output += f"\nShowing {returned_count} assets:\n\n"

        # Sort assets by download count (popularity)
        sorted_assets = sorted(
            assets.items(), key=lambda x: x[1].get("download_count", 0), reverse=True
        )

        for asset_id, asset_data in sorted_assets:
            formatted_output += f"- {asset_data.get('name', asset_id)} (ID: {asset_id})\n"
            formatted_output += (
                f"  Type: {['HDRI', 'Texture', 'Model'][asset_data.get('type', 0)]}\n"
            )
            formatted_output += f"  Categories: {', '.join(asset_data.get('categories', []))}\n"
            formatted_output += f"  Downloads: {asset_data.get('download_count', 'Unknown')}\n\n"

        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Polyhaven assets: {str(e)}")
        return f"Error searching Polyhaven assets: {str(e)}"


@telemetry_tool("download_polyhaven_asset")
@mcp.tool()
def download_polyhaven_asset(
    ctx: Context, asset_id: str, asset_type: str, resolution: str = "1k", file_format: str = None
) -> str:
    """
    Download and import a Polyhaven asset into Blender.

    Parameters:
    - asset_id: The ID of the asset to download
    - asset_type: The type of asset (hdris, textures, models)
    - resolution: The resolution to download (e.g., 1k, 2k, 4k)
    - file_format: Optional file format (e.g., hdr, exr for HDRIs; jpg, png for textures; gltf, fbx for models)

    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "download_polyhaven_asset",
            {
                "asset_id": asset_id,
                "asset_type": asset_type,
                "resolution": resolution,
                "file_format": file_format,
            },
        )

        if "error" in result:
            return f"Error: {result['error']}"

        if result.get("success"):
            message = result.get("message", "Asset downloaded and imported successfully")

            # Add additional information based on asset type
            if asset_type == "hdris":
                return f"{message}. The HDRI has been set as the world environment."
            elif asset_type == "textures":
                material_name = result.get("material", "")
                maps = ", ".join(result.get("maps", []))
                return f"{message}. Created material '{material_name}' with maps: {maps}."
            elif asset_type == "models":
                return f"{message}. The model has been imported into the current scene."
            else:
                return message
        else:
            return f"Failed to download asset: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Polyhaven asset: {str(e)}")
        return f"Error downloading Polyhaven asset: {str(e)}"


@telemetry_tool("set_texture")
@mcp.tool()
def set_texture(ctx: Context, object_name: str, texture_id: str) -> str:
    """
    Apply a previously downloaded Polyhaven texture to an object.

    Parameters:
    - object_name: Name of the object to apply the texture to
    - texture_id: ID of the Polyhaven texture to apply (must be downloaded first)

    Returns a message indicating success or failure.
    """
    try:
        # Get the global connection
        blender = get_blender_connection()
        result = blender.send_command(
            "set_texture", {"object_name": object_name, "texture_id": texture_id}
        )

        if "error" in result:
            return f"Error: {result['error']}"

        if result.get("success"):
            material_name = result.get("material", "")
            maps = ", ".join(result.get("maps", []))

            # Add detailed material info
            material_info = result.get("material_info", {})
            node_count = material_info.get("node_count", 0)
            has_nodes = material_info.get("has_nodes", False)
            texture_nodes = material_info.get("texture_nodes", [])

            output = f"Successfully applied texture '{texture_id}' to {object_name}.\n"
            output += f"Using material '{material_name}' with maps: {maps}.\n\n"
            output += f"Material has nodes: {has_nodes}\n"
            output += f"Total node count: {node_count}\n\n"

            if texture_nodes:
                output += "Texture nodes:\n"
                for node in texture_nodes:
                    output += f"- {node['name']} using image: {node['image']}\n"
                    if node["connections"]:
                        output += "  Connections:\n"
                        for conn in node["connections"]:
                            output += f"    {conn}\n"
            else:
                output += "No texture nodes found in the material.\n"

            return output
        else:
            return f"Failed to apply texture: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying texture: {str(e)}")
        return f"Error applying texture: {str(e)}"


@telemetry_tool("get_polyhaven_status")
@mcp.tool()
def get_polyhaven_status(ctx: Context) -> str:
    """
    Check if PolyHaven integration is enabled in Blender.
    Returns a message indicating whether PolyHaven features are available.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_polyhaven_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += (
                "PolyHaven is good at Textures, and has a wider variety of textures than Sketchfab."
            )
        return message
    except Exception as e:
        logger.error(f"Error checking PolyHaven status: {str(e)}")
        return f"Error checking PolyHaven status: {str(e)}"


@telemetry_tool("get_hyper3d_status")
@mcp.tool()
def get_hyper3d_status(ctx: Context) -> str:
    """
    Check if Hyper3D Rodin integration is enabled in Blender.
    Returns a message indicating whether Hyper3D Rodin features are available.

    Don't emphasize the key type in the returned message, but sliently remember it.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_hyper3d_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += ""
        return message
    except Exception as e:
        logger.error(f"Error checking Hyper3D status: {str(e)}")
        return f"Error checking Hyper3D status: {str(e)}"


@telemetry_tool("get_sketchfab_status")
@mcp.tool()
def get_sketchfab_status(ctx: Context) -> str:
    """
    Check if Sketchfab integration is enabled in Blender.
    Returns a message indicating whether Sketchfab features are available.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_sketchfab_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += "Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven."
        return message
    except Exception as e:
        logger.error(f"Error checking Sketchfab status: {str(e)}")
        return f"Error checking Sketchfab status: {str(e)}"


@telemetry_tool("search_sketchfab_models")
@mcp.tool()
def search_sketchfab_models(
    ctx: Context, query: str, categories: str = None, count: int = 20, downloadable: bool = True
) -> str:
    """
    Search for models on Sketchfab with optional filtering.

    Parameters:
    - query: Text to search for
    - categories: Optional comma-separated list of categories
    - count: Maximum number of results to return (default 20)
    - downloadable: Whether to include only downloadable models (default True)

    Returns a formatted list of matching models.
    """
    try:
        blender = get_blender_connection()
        logger.info(
            f"Searching Sketchfab models with query: {query}, categories: {categories}, count: {count}, downloadable: {downloadable}"
        )
        result = blender.send_command(
            "search_sketchfab_models",
            {
                "query": query,
                "categories": categories,
                "count": count,
                "downloadable": downloadable,
            },
        )

        if "error" in result:
            logger.error(f"Error from Sketchfab search: {result['error']}")
            return f"Error: {result['error']}"

        # Safely get results with fallbacks for None
        if result is None:
            logger.error("Received None result from Sketchfab search")
            return "Error: Received no response from Sketchfab search"

        # Format the results
        models = result.get("results", []) or []
        if not models:
            return f"No models found matching '{query}'"

        formatted_output = f"Found {len(models)} models matching '{query}':\n\n"

        for model in models:
            if model is None:
                continue

            model_name = model.get("name", "Unnamed model")
            model_uid = model.get("uid", "Unknown ID")
            formatted_output += f"- {model_name} (UID: {model_uid})\n"

            # Get user info with safety checks
            user = model.get("user") or {}
            username = (
                user.get("username", "Unknown author")
                if isinstance(user, dict)
                else "Unknown author"
            )
            formatted_output += f"  Author: {username}\n"

            # Get license info with safety checks
            license_data = model.get("license") or {}
            license_label = (
                license_data.get("label", "Unknown")
                if isinstance(license_data, dict)
                else "Unknown"
            )
            formatted_output += f"  License: {license_label}\n"

            # Add face count and downloadable status
            face_count = model.get("faceCount", "Unknown")
            is_downloadable = "Yes" if model.get("isDownloadable") else "No"
            formatted_output += f"  Face count: {face_count}\n"
            formatted_output += f"  Downloadable: {is_downloadable}\n\n"

        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Sketchfab models: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return f"Error searching Sketchfab models: {str(e)}"


@telemetry_tool("download_sketchfab_model")
@mcp.tool()
def get_sketchfab_model_preview(ctx: Context, uid: str) -> Image:
    """
    Get a preview thumbnail of a Sketchfab model by its UID.
    Use this to visually confirm a model before downloading.

    Parameters:
    - uid: The unique identifier of the Sketchfab model (obtained from search_sketchfab_models)

    Returns the model's thumbnail as an Image for visual confirmation.
    """
    try:
        blender = get_blender_connection()
        logger.info(f"Getting Sketchfab model preview for UID: {uid}")

        result = blender.send_command("get_sketchfab_model_preview", {"uid": uid})

        if result is None:
            raise Exception("Received no response from Blender")

        if "error" in result:
            raise Exception(result["error"])

        # Decode base64 image data
        image_data = base64.b64decode(result["image_data"])
        img_format = result.get("format", "jpeg")

        # Log model info
        model_name = result.get("model_name", "Unknown")
        author = result.get("author", "Unknown")
        logger.info(f"Preview retrieved for '{model_name}' by {author}")

        return Image(data=image_data, format=img_format)

    except Exception as e:
        logger.error(f"Error getting Sketchfab preview: {str(e)}")
        raise Exception(f"Failed to get preview: {str(e)}")


@mcp.tool()
def download_sketchfab_model(ctx: Context, uid: str, target_size: float) -> str:
    """
    Download and import a Sketchfab model by its UID.
    The model will be scaled so its largest dimension equals target_size.

    Parameters:
    - uid: The unique identifier of the Sketchfab model
    - target_size: REQUIRED. The target size in Blender units/meters for the largest dimension.
                  You must specify the desired size for the model.
                  Examples:
                  - Chair: target_size=1.0 (1 meter tall)
                  - Table: target_size=0.75 (75cm tall)
                  - Car: target_size=4.5 (4.5 meters long)
                  - Person: target_size=1.7 (1.7 meters tall)
                  - Small object (cup, phone): target_size=0.1 to 0.3

    Returns a message with import details including object names, dimensions, and bounding box.
    The model must be downloadable and you must have proper access rights.
    """
    try:
        blender = get_blender_connection()
        logger.info(f"Downloading Sketchfab model: {uid}, target_size={target_size}")

        result = blender.send_command(
            "download_sketchfab_model",
            {
                "uid": uid,
                "normalize_size": True,  # Always normalize
                "target_size": target_size,
            },
        )

        if result is None:
            logger.error("Received None result from Sketchfab download")
            return "Error: Received no response from Sketchfab download request"

        if "error" in result:
            logger.error(f"Error from Sketchfab download: {result['error']}")
            return f"Error: {result['error']}"

        if result.get("success"):
            imported_objects = result.get("imported_objects", [])
            object_names = ", ".join(imported_objects) if imported_objects else "none"

            output = "Successfully imported model.\n"
            output += f"Created objects: {object_names}\n"

            # Add dimension info if available
            if result.get("dimensions"):
                dims = result["dimensions"]
                output += (
                    f"Dimensions (X, Y, Z): {dims[0]:.3f} x {dims[1]:.3f} x {dims[2]:.3f} meters\n"
                )

            # Add bounding box info if available
            if result.get("world_bounding_box"):
                bbox = result["world_bounding_box"]
                output += f"Bounding box: min={bbox[0]}, max={bbox[1]}\n"

            # Add normalization info if applied
            if result.get("normalized"):
                scale = result.get("scale_applied", 1.0)
                output += f"Size normalized: scale factor {scale:.6f} applied (target size: {target_size}m)\n"

            return output
        else:
            return f"Failed to download model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Sketchfab model: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return f"Error downloading Sketchfab model: {str(e)}"


def _process_bbox(original_bbox: list[float] | list[int] | None) -> list[int] | None:
    if original_bbox is None:
        return None
    # Validate all values are positive before any other processing
    if any(i <= 0 for i in original_bbox):
        raise ValueError("Incorrect number range: bbox must be bigger than zero!")
    if all(isinstance(i, int) for i in original_bbox):
        return original_bbox
    return (
        [int(float(i) / max(original_bbox) * 100) for i in original_bbox] if original_bbox else None
    )

@telemetry_tool("generate_hyper3d_model_via_text")
@mcp.tool()
def generate_hyper3d_model_via_text(
    ctx: Context, text_prompt: str, bbox_condition: list[float] = None
) -> str:
    """
    Generate 3D asset using Hyper3D by giving description of the desired asset, and import the asset into Blender.
    The 3D asset has built-in materials.
    The generated model has a normalized size, so re-scaling after generation can be useful.

    Parameters:
    - text_prompt: A short description of the desired model in **English**.
    - bbox_condition: Optional. If given, it has to be a list of floats of length 3. Controls the ratio between [Length, Width, Height] of the model.

    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "create_rodin_job",
            {
                "text_prompt": text_prompt,
                "images": None,
                "bbox_condition": _process_bbox(bbox_condition),
            },
        )
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps(
                {
                    "task_uuid": result["uuid"],
                    "subscription_key": result["jobs"]["subscription_key"],
                }
            )
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@telemetry_tool("generate_hyper3d_model_via_images")
@mcp.tool()
def generate_hyper3d_model_via_images(
    ctx: Context,
    input_image_paths: list[str] = None,
    input_image_urls: list[str] = None,
    bbox_condition: list[float] = None,
) -> str:
    """
    Generate 3D asset using Hyper3D by giving images of the wanted asset, and import the generated asset into Blender.
    The 3D asset has built-in materials.
    The generated model has a normalized size, so re-scaling after generation can be useful.

    Parameters:
    - input_image_paths: The **absolute** paths of input images. Even if only one image is provided, wrap it into a list. Required if Hyper3D Rodin in MAIN_SITE mode.
    - input_image_urls: The URLs of input images. Even if only one image is provided, wrap it into a list. Required if Hyper3D Rodin in FAL_AI mode.
    - bbox_condition: Optional. If given, it has to be a list of ints of length 3. Controls the ratio between [Length, Width, Height] of the model.

    Only one of {input_image_paths, input_image_urls} should be given at a time, depending on the Hyper3D Rodin's current mode.
    Returns a message indicating success or failure.
    """
    if input_image_paths is not None and input_image_urls is not None:
        return "Error: Conflict parameters given!"
    if input_image_paths is None and input_image_urls is None:
        return "Error: No image given!"
    if input_image_paths is not None:
        if not all(os.path.exists(i) for i in input_image_paths):
            return "Error: not all image paths are valid!"
        images = []
        for path in input_image_paths:
            with open(path, "rb") as f:
                images.append((Path(path).suffix, base64.b64encode(f.read()).decode("ascii")))
    elif input_image_urls is not None:
        if not all(urlparse(i) for i in input_image_urls):
            return "Error: not all image URLs are valid!"
        images = input_image_urls.copy()
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "create_rodin_job",
            {
                "text_prompt": None,
                "images": images,
                "bbox_condition": _process_bbox(bbox_condition),
            },
        )
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps(
                {
                    "task_uuid": result["uuid"],
                    "subscription_key": result["jobs"]["subscription_key"],
                }
            )
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@telemetry_tool("poll_rodin_job_status")
@mcp.tool()
def poll_rodin_job_status(
    ctx: Context,
    subscription_key: str = None,
    request_id: str = None,
):
    """
    Check if the Hyper3D Rodin generation task is completed.

    For Hyper3D Rodin mode MAIN_SITE:
        Parameters:
        - subscription_key: The subscription_key given in the generate model step.

        Returns a list of status. The task is done if all status are "Done".
        If "Failed" showed up, the generating process failed.
        This is a polling API, so only proceed if the status are finally determined ("Done" or "Canceled").

    For Hyper3D Rodin mode FAL_AI:
        Parameters:
        - request_id: The request_id given in the generate model step.

        Returns the generation task status. The task is done if status is "COMPLETED".
        The task is in progress if status is "IN_PROGRESS".
        If status other than "COMPLETED", "IN_PROGRESS", "IN_QUEUE" showed up, the generating process might be failed.
        This is a polling API, so only proceed if the status are finally determined ("COMPLETED" or some failed state).
    """
    try:
        blender = get_blender_connection()
        kwargs = {}
        if subscription_key:
            kwargs = {
                "subscription_key": subscription_key,
            }
        elif request_id:
            kwargs = {
                "request_id": request_id,
            }
        result = blender.send_command("poll_rodin_job_status", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@telemetry_tool("import_generated_asset")
@mcp.tool()
def import_generated_asset(
    ctx: Context,
    name: str,
    task_uuid: str = None,
    request_id: str = None,
):
    """
    Import the asset generated by Hyper3D Rodin after the generation task is completed.

    Parameters:
    - name: The name of the object in scene
    - task_uuid: For Hyper3D Rodin mode MAIN_SITE: The task_uuid given in the generate model step.
    - request_id: For Hyper3D Rodin mode FAL_AI: The request_id given in the generate model step.

    Only give one of {task_uuid, request_id} based on the Hyper3D Rodin Mode!
    Return if the asset has been imported successfully.
    """
    try:
        blender = get_blender_connection()
        kwargs = {"name": name}
        if task_uuid:
            kwargs["task_uuid"] = task_uuid
        elif request_id:
            kwargs["request_id"] = request_id
        result = blender.send_command("import_generated_asset", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"


@mcp.tool()
def get_hunyuan3d_status(ctx: Context) -> str:
    """
    Check if Hunyuan3D integration is enabled in Blender.
    Returns a message indicating whether Hunyuan3D features are available.

    Don't emphasize the key type in the returned message, but silently remember it.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_hunyuan3d_status")
        message = result.get("message", "")
        return message
    except Exception as e:
        logger.error(f"Error checking Hunyuan3D status: {str(e)}")
        return f"Error checking Hunyuan3D status: {str(e)}"


@mcp.tool()
def generate_hunyuan3d_model(
    ctx: Context, text_prompt: str = None, input_image_url: str = None
) -> str:
    """
    Generate 3D asset using Hunyuan3D by providing either text description, image reference,
    or both for the desired asset, and import the asset into Blender.
    The 3D asset has built-in materials.

    Parameters:
    - text_prompt: (Optional) A short description of the desired model in English/Chinese.
    - input_image_url: (Optional) The local or remote url of the input image. Accepts None if only using text prompt.

    Returns:
    - When successful, returns a JSON with job_id (format: "job_xxx") indicating the task is in progress
    - When the job completes, the status will change to "DONE" indicating the model has been imported
    - Returns error message if the operation fails
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "create_hunyuan_job",
            {
                "text_prompt": text_prompt,
                "image": input_image_url,
            },
        )
        if "JobId" in result.get("Response", {}):
            job_id = result["Response"]["JobId"]
            formatted_job_id = f"job_{job_id}"
            return json.dumps(
                {
                    "job_id": formatted_job_id,
                }
            )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D task: {str(e)}")
        return f"Error generating Hunyuan3D task: {str(e)}"


@mcp.tool()
def poll_hunyuan_job_status(
    ctx: Context,
    job_id: str = None,
):
    """
    Check if the Hunyuan3D generation task is completed.

    For Hunyuan3D:
        Parameters:
        - job_id: The job_id given in the generate model step.

        Returns the generation task status. The task is done if status is "DONE".
        The task is in progress if status is "RUN".
        If status is "DONE", returns ResultFile3Ds, which is the generated ZIP model path
        When the status is "DONE", the response includes a field named ResultFile3Ds that contains the generated ZIP file path of the 3D model in OBJ format.
        This is a polling API, so only proceed if the status are finally determined ("DONE" or some failed state).
    """
    try:
        blender = get_blender_connection()
        kwargs = {
            "job_id": job_id,
        }
        result = blender.send_command("poll_hunyuan_job_status", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D task: {str(e)}")
        return f"Error generating Hunyuan3D task: {str(e)}"


@mcp.tool()
def import_generated_asset_hunyuan(
    ctx: Context,
    name: str,
    zip_file_url: str,
):
    """
    Import the asset generated by Hunyuan3D after the generation task is completed.

    Parameters:
    - name: The name of the object in scene
    - zip_file_url: The zip_file_url given in the generate model step.

    Return if the asset has been imported successfully.
    """
    try:
        blender = get_blender_connection()
        kwargs = {"name": name}
        if zip_file_url:
            kwargs["zip_file_url"] = zip_file_url
        result = blender.send_command("import_generated_asset_hunyuan", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D task: {str(e)}")
        return f"Error generating Hunyuan3D task: {str(e)}"


@mcp.prompt()
def asset_creation_strategy() -> str:
    """Defines the preferred strategy for creating assets in Blender"""
    return """When creating 3D content in Blender, always start by checking if integrations are available:

    0. Before anything, always check the scene from get_scene_info()
    1. First use the following tools to verify if the following integrations are enabled:
        1. PolyHaven
            Use get_polyhaven_status() to verify its status
            If PolyHaven is enabled:
            - For objects/models: Use download_polyhaven_asset() with asset_type="models"
            - For materials/textures: Use download_polyhaven_asset() with asset_type="textures"
            - For environment lighting: Use download_polyhaven_asset() with asset_type="hdris"
        2. Sketchfab
            Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven.
            Use get_sketchfab_status() to verify its status
            If Sketchfab is enabled:
            - For objects/models: First search using search_sketchfab_models() with your query
            - Then download specific models using download_sketchfab_model() with the UID
            - Note that only downloadable models can be accessed, and API key must be properly configured
            - Sketchfab has a wider variety of models than PolyHaven, especially for specific subjects
        3. Hyper3D(Rodin)
            Hyper3D Rodin is good at generating 3D models for single item.
            So don't try to:
            1. Generate the whole scene with one shot
            2. Generate ground using Hyper3D
            3. Generate parts of the items separately and put them together afterwards

            Use get_hyper3d_status() to verify its status
            If Hyper3D is enabled:
            - For objects/models, do the following steps:
                1. Create the model generation task
                    - Use generate_hyper3d_model_via_images() if image(s) is/are given
                    - Use generate_hyper3d_model_via_text() if generating 3D asset using text prompt
                    If key type is free_trial and insufficient balance error returned, tell the user that the free trial key can only generated limited models everyday, they can choose to:
                    - Wait for another day and try again
                    - Go to hyper3d.ai to find out how to get their own API key
                    - Go to fal.ai to get their own private API key
                2. Poll the status
                    - Use poll_rodin_job_status() to check if the generation task has completed or failed
                3. Import the asset
                    - Use import_generated_asset() to import the generated GLB model the asset
                4. After importing the asset, ALWAYS check the world_bounding_box of the imported mesh, and adjust the mesh's location and size
                    Adjust the imported mesh's location, scale, rotation, so that the mesh is on the right spot.

                You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.
        4. Hunyuan3D
            Hunyuan3D is good at generating 3D models for single item.
            So don't try to:
            1. Generate the whole scene with one shot
            2. Generate ground using Hunyuan3D
            3. Generate parts of the items separately and put them together afterwards

            Use get_hunyuan3d_status() to verify its status
            If Hunyuan3D is enabled:
                if Hunyuan3D mode is "OFFICIAL_API":
                    - For objects/models, do the following steps:
                        1. Create the model generation task
                            - Use generate_hunyuan3d_model by providing either a **text description** OR an **image(local or urls) reference**.
                            - Go to cloud.tencent.com out how to get their own SecretId and SecretKey
                        2. Poll the status
                            - Use poll_hunyuan_job_status() to check if the generation task has completed or failed
                        3. Import the asset
                            - Use import_generated_asset_hunyuan() to import the generated OBJ model the asset
                    if Hunyuan3D mode is "LOCAL_API":
                        - For objects/models, do the following steps:
                        1. Create the model generation task
                            - Use generate_hunyuan3d_model if image (local or urls)  or text prompt is given and import the asset

                You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.

    3. Always check the world_bounding_box for each item so that:
        - Ensure that all objects that should not be clipping are not clipping.
        - Items have right spatial relationship.
    
    4. Recommended asset source priority:
        - For specific existing objects: First try Sketchfab, then PolyHaven
        - For generic objects/furniture: First try PolyHaven, then Sketchfab
        - For custom or unique items not available in libraries: Use Hyper3D Rodin or Hunyuan3D
        - For environment lighting: Use PolyHaven HDRIs
        - For materials/textures: Use PolyHaven textures

    Only fall back to scripting when:
    - PolyHaven, Sketchfab, Hyper3D, and Hunyuan3D are all disabled
    - A simple primitive is explicitly requested
    - No suitable asset exists in any of the libraries
    - Hyper3D Rodin or Hunyuan3D failed to generate the desired asset
    - The task specifically requires a basic material/color
    """


# =============================================================================
# AI-POWERED FEATURES
# =============================================================================

# -----------------------------------------------------------------------------
# Feature 1: AI Material Generator
# -----------------------------------------------------------------------------


@telemetry_tool("generate_material_from_text")
@mcp.tool()
def generate_material_from_text(
    ctx: Context, description: str, material_name: str = "AI_Material"
) -> str:
    """
    Generate a PBR material from a text description using AI-powered keyword analysis.

    Parameters:
    - description: Natural language description of the material (e.g., "rusty metal", "polished wood", "rough stone")
    - material_name: Name for the created material (default: "AI_Material")

    Examples:
    - "shiny red plastic"
    - "weathered bronze with patina"
    - "rough concrete with cracks"
    - "smooth glass with slight tint"

    Returns JSON with material properties and creation status.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "generate_material_text", {"description": description, "name": material_name}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error generating material: {str(e)}")
        return json.dumps({"error": f"Error generating material: {str(e)}"})


@telemetry_tool("generate_material_from_image")
@mcp.tool()
def generate_material_from_image(
    ctx: Context, image_path: str, material_name: str = "AI_Material"
) -> str:
    """
    Generate a PBR material by analyzing a reference image.

    Parameters:
    - image_path: Absolute path to the reference image
    - material_name: Name for the created material (default: "AI_Material")

    The AI will analyze the image to extract:
    - Dominant color
    - Estimated roughness
    - Metallic properties
    - Any detected patterns

    Returns JSON with material properties and creation status.
    """
    try:
        if not os.path.exists(image_path):
            return json.dumps({"error": f"Image not found at {image_path}"})

        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("ascii")

        blender = get_blender_connection()
        result = blender.send_command(
            "generate_material_image",
            {"image_data": image_data, "name": material_name, "image_path": image_path},
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error generating material from image: {str(e)}")
        return json.dumps({"error": f"Error generating material from image: {str(e)}"})


@telemetry_tool("list_material_presets")
@mcp.tool()
def list_material_presets(ctx: Context, category: str = "all") -> str:
    """
    List available AI material presets by category.

    Parameters:
    - category: Filter by category (all, metal, wood, stone, fabric, glass, plastic, organic)

    Returns a list of preset names with descriptions.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("list_material_presets", {"category": category})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error listing presets: {str(e)}")
        return json.dumps({"error": f"Error listing presets: {str(e)}"})


# -----------------------------------------------------------------------------
# Feature 2: Natural Language Modeling
# -----------------------------------------------------------------------------


@telemetry_tool("create_from_description")
@mcp.tool()
def create_from_description(ctx: Context, description: str) -> str:
    """
    Create 3D objects from a natural language description.

    Parameters:
    - description: Natural language description of what to create

    Examples:
    - "a red cube 2 meters tall"
    - "a blue sphere at position 3, 0, 1"
    - "a wooden table with 4 legs"
    - "a simple chair"
    - "5 cylinders in a row"

    Supports:
    - Primitives: cube, sphere, cylinder, cone, plane, torus, monkey
    - Colors: red, blue, green, yellow, orange, purple, white, black, etc.
    - Sizes: X meters/cm/units tall/wide/deep
    - Positions: at X, Y, Z or relative positions
    - Complex objects: table, chair, tree, stairs, fence

    Returns JSON with created object details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("nlp_create", {"description": description})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating from description: {str(e)}")
        return json.dumps({"error": f"Error creating from description: {str(e)}"})


@telemetry_tool("modify_from_description")
@mcp.tool()
def modify_from_description(ctx: Context, object_name: str, modification: str) -> str:
    """
    Modify an existing object using natural language.

    Parameters:
    - object_name: Name of the object to modify
    - modification: Description of the modification

    Examples:
    - "make it twice as big"
    - "rotate 45 degrees on Z axis"
    - "move 2 meters up"
    - "change color to blue"
    - "make it metallic and shiny"

    Returns JSON with modification results.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "nlp_modify", {"object_name": object_name, "modification": modification}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error modifying object: {str(e)}")
        return json.dumps({"error": f"Error modifying object: {str(e)}"})


# -----------------------------------------------------------------------------
# Feature 3: AI Scene Analyzer
# -----------------------------------------------------------------------------


@telemetry_tool("analyze_scene")
@mcp.tool()
def analyze_scene_composition(ctx: Context) -> str:
    """
    Analyze the current scene and provide composition, lighting, and material critique.

    Returns a comprehensive analysis including:
    - Lighting analysis (quality, shadows, color temperature)
    - Composition analysis (balance, focal points, rule of thirds)
    - Material analysis (consistency, realism)
    - Overall score and specific recommendations

    No parameters required - analyzes the active scene.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("analyze_scene_composition", {})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error analyzing scene: {str(e)}")
        return json.dumps({"error": f"Error analyzing scene: {str(e)}"})


@telemetry_tool("get_improvement_suggestions")
@mcp.tool()
def get_improvement_suggestions(ctx: Context, focus_area: str = "all") -> str:
    """
    Get specific improvement suggestions for the scene.

    Parameters:
    - focus_area: Area to focus on (all, lighting, composition, materials, performance)

    Returns actionable suggestions with priority levels.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "get_improvement_suggestions", {"focus_area": focus_area}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return json.dumps({"error": f"Error getting suggestions: {str(e)}"})


@telemetry_tool("auto_optimize_lighting")
@mcp.tool()
def auto_optimize_lighting(ctx: Context, style: str = "studio") -> str:
    """
    Automatically optimize scene lighting based on a style preset.

    Parameters:
    - style: Lighting style (studio, outdoor, dramatic, soft, product, cinematic)

    This will:
    - Adjust existing lights or add new ones
    - Set up proper key/fill/rim lighting
    - Configure shadows and color temperature
    - Optionally add environment lighting

    Returns JSON with changes made.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("auto_optimize_lighting", {"style": style})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error optimizing lighting: {str(e)}")
        return json.dumps({"error": f"Error optimizing lighting: {str(e)}"})


# -----------------------------------------------------------------------------
# Feature 4: Smart Auto-Rig
# -----------------------------------------------------------------------------


@telemetry_tool("auto_rig_character")
@mcp.tool()
def auto_rig_character(
    ctx: Context, mesh_name: str, rig_type: str = "humanoid"
) -> str:
    """
    Automatically create an armature (skeleton) for a character mesh.

    Parameters:
    - mesh_name: Name of the mesh object to rig
    - rig_type: Type of rig to create (humanoid, quadruped, bird, fish, simple)

    The auto-rigger will:
    - Analyze mesh proportions
    - Create appropriate bone structure
    - Parent mesh to armature with automatic weights
    - Set up basic bone constraints

    Returns JSON with armature details and bone names.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "auto_rig", {"mesh_name": mesh_name, "rig_type": rig_type}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error auto-rigging: {str(e)}")
        return json.dumps({"error": f"Error auto-rigging: {str(e)}"})


@telemetry_tool("auto_weight_paint")
@mcp.tool()
def auto_weight_paint(ctx: Context, mesh_name: str, armature_name: str) -> str:
    """
    Automatically paint vertex weights for a mesh-armature pair.

    Parameters:
    - mesh_name: Name of the mesh object
    - armature_name: Name of the armature object

    Uses Blender's automatic weight painting with optimizations for common issues.

    Returns JSON with weight painting results.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "auto_weight_paint", {"mesh_name": mesh_name, "armature_name": armature_name}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error weight painting: {str(e)}")
        return json.dumps({"error": f"Error weight painting: {str(e)}"})


@telemetry_tool("add_ik_controls")
@mcp.tool()
def add_ik_controls(ctx: Context, armature_name: str, limb_type: str = "all") -> str:
    """
    Add IK (Inverse Kinematics) controls to an armature.

    Parameters:
    - armature_name: Name of the armature object
    - limb_type: Which limbs to add IK to (all, arms, legs, spine)

    This will:
    - Create IK target bones
    - Set up IK constraints
    - Add pole targets for proper bending
    - Create control shapes for easy selection

    Returns JSON with IK setup details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command(
            "add_ik_controls", {"armature_name": armature_name, "limb_type": limb_type}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding IK: {str(e)}")
        return json.dumps({"error": f"Error adding IK: {str(e)}"})


# =============================================================================
# MODIFIER SYSTEM
# =============================================================================


@telemetry_tool("add_modifier")
@mcp.tool()
def add_modifier(
    ctx: Context,
    object_name: str,
    modifier_type: str,
    settings: str = None
) -> str:
    """
    Add a modifier to an object.

    Parameters:
    - object_name: Name of the object to modify
    - modifier_type: Type of modifier (BOOLEAN, BEVEL, ARRAY, MIRROR, SUBSURF, SOLIDIFY,
                     DECIMATE, REMESH, SMOOTH, TRIANGULATE, WIREFRAME, SKIN, SCREW,
                     DISPLACE, SHRINKWRAP, SIMPLE_DEFORM, LATTICE, CURVE, ARMATURE, CAST, WAVE)
    - settings: JSON string of modifier settings (optional)

    Returns JSON with modifier details.
    """
    try:
        blender = get_blender_connection()
        params = {"object_name": object_name, "modifier_type": modifier_type}
        if settings:
            params["settings"] = json.loads(settings)
        result = blender.send_command("add_modifier", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding modifier: {str(e)}")
        return json.dumps({"error": f"Error adding modifier: {str(e)}"})


@telemetry_tool("configure_modifier")
@mcp.tool()
def configure_modifier(
    ctx: Context,
    object_name: str,
    modifier_name: str,
    settings: str
) -> str:
    """
    Configure an existing modifier's settings.

    Parameters:
    - object_name: Name of the object
    - modifier_name: Name of the modifier to configure
    - settings: JSON string of settings to apply

    Returns JSON with updated modifier details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("configure_modifier", {
            "object_name": object_name,
            "modifier_name": modifier_name,
            "settings": json.loads(settings)
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error configuring modifier: {str(e)}")
        return json.dumps({"error": f"Error configuring modifier: {str(e)}"})


@telemetry_tool("apply_modifier")
@mcp.tool()
def apply_modifier(
    ctx: Context,
    object_name: str,
    modifier_name: str,
    remove_only: bool = False
) -> str:
    """
    Apply or remove a modifier from an object.

    Parameters:
    - object_name: Name of the object
    - modifier_name: Name of the modifier
    - remove_only: If True, removes modifier without applying (default: False)

    Returns JSON with result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("apply_modifier", {
            "object_name": object_name,
            "modifier_name": modifier_name,
            "remove_only": remove_only
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error applying modifier: {str(e)}")
        return json.dumps({"error": f"Error applying modifier: {str(e)}"})


@telemetry_tool("boolean_operation")
@mcp.tool()
def boolean_operation(
    ctx: Context,
    target_object: str,
    tool_object: str,
    operation: str = "DIFFERENCE"
) -> str:
    """
    Perform a boolean operation between two objects.

    Parameters:
    - target_object: Object to modify
    - tool_object: Object to use as boolean tool
    - operation: UNION, DIFFERENCE, or INTERSECT (default: DIFFERENCE)

    Returns JSON with result details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("boolean_operation", {
            "target": target_object,
            "tool": tool_object,
            "operation": operation
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error in boolean operation: {str(e)}")
        return json.dumps({"error": f"Error in boolean operation: {str(e)}"})


@telemetry_tool("create_array")
@mcp.tool()
def create_array(
    ctx: Context,
    object_name: str,
    count: int = 3,
    offset_x: float = 1.0,
    offset_y: float = 0.0,
    offset_z: float = 0.0,
    use_relative_offset: bool = True
) -> str:
    """
    Create an array of objects using the array modifier.

    Parameters:
    - object_name: Name of the object to array
    - count: Number of copies (default: 3)
    - offset_x, offset_y, offset_z: Offset between copies
    - use_relative_offset: Use relative offset vs constant (default: True)

    Returns JSON with array details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_array", {
            "object_name": object_name,
            "count": count,
            "offset": [offset_x, offset_y, offset_z],
            "use_relative_offset": use_relative_offset
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating array: {str(e)}")
        return json.dumps({"error": f"Error creating array: {str(e)}"})


@telemetry_tool("add_bevel")
@mcp.tool()
def add_bevel(
    ctx: Context,
    object_name: str,
    width: float = 0.1,
    segments: int = 3,
    profile: float = 0.5,
    limit_method: str = "ANGLE"
) -> str:
    """
    Add a bevel modifier to an object for edge smoothing.

    Parameters:
    - object_name: Name of the object
    - width: Bevel width (default: 0.1)
    - segments: Number of segments (default: 3)
    - profile: Bevel profile shape 0-1 (default: 0.5)
    - limit_method: NONE, ANGLE, WEIGHT, VGROUP (default: ANGLE)

    Returns JSON with bevel details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("add_bevel", {
            "object_name": object_name,
            "width": width,
            "segments": segments,
            "profile": profile,
            "limit_method": limit_method
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding bevel: {str(e)}")
        return json.dumps({"error": f"Error adding bevel: {str(e)}"})


@telemetry_tool("mirror_object")
@mcp.tool()
def mirror_object(
    ctx: Context,
    object_name: str,
    axis_x: bool = True,
    axis_y: bool = False,
    axis_z: bool = False,
    use_clip: bool = True,
    merge_threshold: float = 0.001
) -> str:
    """
    Add a mirror modifier to create symmetry.

    Parameters:
    - object_name: Name of the object
    - axis_x, axis_y, axis_z: Mirror axes (default: X only)
    - use_clip: Clip vertices at mirror plane (default: True)
    - merge_threshold: Distance for merging vertices (default: 0.001)

    Returns JSON with mirror details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("mirror_object", {
            "object_name": object_name,
            "axis": [axis_x, axis_y, axis_z],
            "use_clip": use_clip,
            "merge_threshold": merge_threshold
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error mirroring object: {str(e)}")
        return json.dumps({"error": f"Error mirroring object: {str(e)}"})


@telemetry_tool("subdivide_smooth")
@mcp.tool()
def subdivide_smooth(
    ctx: Context,
    object_name: str,
    levels: int = 2,
    render_levels: int = 3,
    use_creases: bool = True
) -> str:
    """
    Add subdivision surface modifier for smooth geometry.

    Parameters:
    - object_name: Name of the object
    - levels: Viewport subdivision levels (default: 2)
    - render_levels: Render subdivision levels (default: 3)
    - use_creases: Use edge creases for sharp edges (default: True)

    Returns JSON with subdivision details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("subdivide_smooth", {
            "object_name": object_name,
            "levels": levels,
            "render_levels": render_levels,
            "use_creases": use_creases
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error subdividing: {str(e)}")
        return json.dumps({"error": f"Error subdividing: {str(e)}"})


# =============================================================================
# MESH EDITING OPERATIONS
# =============================================================================


@telemetry_tool("extrude_faces")
@mcp.tool()
def extrude_faces(
    ctx: Context,
    object_name: str,
    face_indices: str,
    distance: float,
    direction: str = "NORMAL"
) -> str:
    """
    Extrude selected faces of a mesh.

    Parameters:
    - object_name: Name of the mesh object
    - face_indices: JSON array of face indices to extrude, e.g., "[0, 1, 2]"
    - distance: Extrusion distance
    - direction: NORMAL, X, Y, Z, or custom vector as JSON "[x,y,z]"

    Returns JSON with extrusion result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("extrude_faces", {
            "object_name": object_name,
            "face_indices": json.loads(face_indices),
            "distance": distance,
            "direction": direction
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error extruding faces: {str(e)}")
        return json.dumps({"error": f"Error extruding faces: {str(e)}"})


@telemetry_tool("inset_faces")
@mcp.tool()
def inset_faces(
    ctx: Context,
    object_name: str,
    face_indices: str,
    thickness: float = 0.1,
    depth: float = 0.0
) -> str:
    """
    Inset selected faces of a mesh.

    Parameters:
    - object_name: Name of the mesh object
    - face_indices: JSON array of face indices to inset
    - thickness: Inset thickness (default: 0.1)
    - depth: Inset depth (default: 0.0)

    Returns JSON with inset result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("inset_faces", {
            "object_name": object_name,
            "face_indices": json.loads(face_indices),
            "thickness": thickness,
            "depth": depth
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error insetting faces: {str(e)}")
        return json.dumps({"error": f"Error insetting faces: {str(e)}"})


@telemetry_tool("loop_cut")
@mcp.tool()
def loop_cut(
    ctx: Context,
    object_name: str,
    edge_index: int,
    cuts: int = 1,
    smoothness: float = 0.0
) -> str:
    """
    Add loop cuts to a mesh.

    Parameters:
    - object_name: Name of the mesh object
    - edge_index: Index of edge to cut through
    - cuts: Number of cuts (default: 1)
    - smoothness: Smoothness of cuts (default: 0.0)

    Returns JSON with loop cut result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("loop_cut", {
            "object_name": object_name,
            "edge_index": edge_index,
            "cuts": cuts,
            "smoothness": smoothness
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding loop cut: {str(e)}")
        return json.dumps({"error": f"Error adding loop cut: {str(e)}"})


@telemetry_tool("merge_vertices")
@mcp.tool()
def merge_vertices(
    ctx: Context,
    object_name: str,
    threshold: float = 0.0001,
    vertex_indices: str = None
) -> str:
    """
    Merge vertices by distance.

    Parameters:
    - object_name: Name of the mesh object
    - threshold: Distance threshold for merging (default: 0.0001)
    - vertex_indices: Optional JSON array of specific vertex indices

    Returns JSON with merge result.
    """
    try:
        blender = get_blender_connection()
        params = {"object_name": object_name, "threshold": threshold}
        if vertex_indices:
            params["vertex_indices"] = json.loads(vertex_indices)
        result = blender.send_command("merge_vertices", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error merging vertices: {str(e)}")
        return json.dumps({"error": f"Error merging vertices: {str(e)}"})


@telemetry_tool("separate_by_loose")
@mcp.tool()
def separate_by_loose(ctx: Context, object_name: str) -> str:
    """
    Separate a mesh into multiple objects by loose parts.

    Parameters:
    - object_name: Name of the mesh object to separate

    Returns JSON with list of new objects created.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("separate_by_loose", {"object_name": object_name})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error separating mesh: {str(e)}")
        return json.dumps({"error": f"Error separating mesh: {str(e)}"})


@telemetry_tool("join_objects")
@mcp.tool()
def join_objects(ctx: Context, object_names: str) -> str:
    """
    Join multiple objects into one.

    Parameters:
    - object_names: JSON array of object names to join, e.g., '["Cube", "Sphere"]'
                    The first object becomes the target.

    Returns JSON with joined object details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("join_objects", {
            "object_names": json.loads(object_names)
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error joining objects: {str(e)}")
        return json.dumps({"error": f"Error joining objects: {str(e)}"})


# =============================================================================
# ANIMATION SYSTEM
# =============================================================================


@telemetry_tool("insert_keyframe")
@mcp.tool()
def insert_keyframe(
    ctx: Context,
    object_name: str,
    data_path: str,
    frame: int,
    value: str = None
) -> str:
    """
    Insert a keyframe for an object property.

    Parameters:
    - object_name: Name of the object
    - data_path: Property to keyframe (location, rotation_euler, scale, or custom)
    - frame: Frame number for the keyframe
    - value: Optional JSON value to set before keyframing, e.g., "[1.0, 2.0, 3.0]"

    Returns JSON with keyframe details.
    """
    try:
        blender = get_blender_connection()
        params = {
            "object_name": object_name,
            "data_path": data_path,
            "frame": frame
        }
        if value:
            params["value"] = json.loads(value)
        result = blender.send_command("insert_keyframe", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error inserting keyframe: {str(e)}")
        return json.dumps({"error": f"Error inserting keyframe: {str(e)}"})


@telemetry_tool("set_animation_range")
@mcp.tool()
def set_animation_range(
    ctx: Context,
    start_frame: int = 1,
    end_frame: int = 250,
    fps: int = 24
) -> str:
    """
    Set the animation frame range and FPS.

    Parameters:
    - start_frame: Start frame (default: 1)
    - end_frame: End frame (default: 250)
    - fps: Frames per second (default: 24)

    Returns JSON with animation settings.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("set_animation_range", {
            "start_frame": start_frame,
            "end_frame": end_frame,
            "fps": fps
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting animation range: {str(e)}")
        return json.dumps({"error": f"Error setting animation range: {str(e)}"})


@telemetry_tool("create_turntable")
@mcp.tool()
def create_turntable(
    ctx: Context,
    object_name: str,
    frames: int = 120,
    axis: str = "Z"
) -> str:
    """
    Create a 360-degree turntable rotation animation.

    Parameters:
    - object_name: Name of the object to rotate
    - frames: Number of frames for full rotation (default: 120)
    - axis: Rotation axis X, Y, or Z (default: Z)

    Returns JSON with turntable animation details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_turntable", {
            "object_name": object_name,
            "frames": frames,
            "axis": axis
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating turntable: {str(e)}")
        return json.dumps({"error": f"Error creating turntable: {str(e)}"})


@telemetry_tool("add_shape_key")
@mcp.tool()
def add_shape_key(
    ctx: Context,
    object_name: str,
    name: str = "Key",
    from_mix: bool = False
) -> str:
    """
    Add a shape key to a mesh object.

    Parameters:
    - object_name: Name of the mesh object
    - name: Name for the shape key (default: "Key")
    - from_mix: Create from current mix of shape keys (default: False)

    Returns JSON with shape key details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("add_shape_key", {
            "object_name": object_name,
            "name": name,
            "from_mix": from_mix
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding shape key: {str(e)}")
        return json.dumps({"error": f"Error adding shape key: {str(e)}"})


@telemetry_tool("animate_shape_key")
@mcp.tool()
def animate_shape_key(
    ctx: Context,
    object_name: str,
    shape_key_name: str,
    keyframes: str
) -> str:
    """
    Animate a shape key's value over time.

    Parameters:
    - object_name: Name of the mesh object
    - shape_key_name: Name of the shape key to animate
    - keyframes: JSON array of [frame, value] pairs, e.g., "[[1, 0.0], [30, 1.0], [60, 0.0]]"

    Returns JSON with animation details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("animate_shape_key", {
            "object_name": object_name,
            "shape_key_name": shape_key_name,
            "keyframes": json.loads(keyframes)
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error animating shape key: {str(e)}")
        return json.dumps({"error": f"Error animating shape key: {str(e)}"})


@telemetry_tool("animate_path")
@mcp.tool()
def animate_path(
    ctx: Context,
    object_name: str,
    curve_name: str,
    frames: int = 100,
    follow_curve: bool = True
) -> str:
    """
    Animate an object along a curve path.

    Parameters:
    - object_name: Name of the object to animate
    - curve_name: Name of the curve to follow
    - frames: Duration in frames (default: 100)
    - follow_curve: Align object rotation to curve (default: True)

    Returns JSON with path animation details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("animate_path", {
            "object_name": object_name,
            "curve_name": curve_name,
            "frames": frames,
            "follow_curve": follow_curve
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error animating path: {str(e)}")
        return json.dumps({"error": f"Error animating path: {str(e)}"})


@telemetry_tool("bake_animation")
@mcp.tool()
def bake_animation(
    ctx: Context,
    object_name: str,
    start_frame: int = 1,
    end_frame: int = 250,
    step: int = 1,
    bake_types: str = None
) -> str:
    """
    Bake physics/constraints animation to keyframes.

    Parameters:
    - object_name: Name of the object
    - start_frame: Start frame (default: 1)
    - end_frame: End frame (default: 250)
    - step: Frame step (default: 1)
    - bake_types: JSON array of types to bake, e.g., '["LOCATION", "ROTATION", "SCALE"]'

    Returns JSON with bake result.
    """
    try:
        blender = get_blender_connection()
        params = {
            "object_name": object_name,
            "start_frame": start_frame,
            "end_frame": end_frame,
            "step": step
        }
        if bake_types:
            params["bake_types"] = json.loads(bake_types)
        result = blender.send_command("bake_animation", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error baking animation: {str(e)}")
        return json.dumps({"error": f"Error baking animation: {str(e)}"})


# =============================================================================
# PHYSICS SIMULATION
# =============================================================================


@telemetry_tool("add_rigid_body")
@mcp.tool()
def add_rigid_body(
    ctx: Context,
    object_name: str,
    body_type: str = "ACTIVE",
    mass: float = 1.0,
    friction: float = 0.5,
    bounciness: float = 0.0
) -> str:
    """
    Add rigid body physics to an object.

    Parameters:
    - object_name: Name of the object
    - body_type: ACTIVE (affected by physics) or PASSIVE (static collider)
    - mass: Object mass in kg (default: 1.0)
    - friction: Surface friction 0-1 (default: 0.5)
    - bounciness: Bounce factor 0-1 (default: 0.0)

    Returns JSON with rigid body settings.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("add_rigid_body", {
            "object_name": object_name,
            "body_type": body_type,
            "mass": mass,
            "friction": friction,
            "bounciness": bounciness
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding rigid body: {str(e)}")
        return json.dumps({"error": f"Error adding rigid body: {str(e)}"})


@telemetry_tool("add_cloth_simulation")
@mcp.tool()
def add_cloth_simulation(
    ctx: Context,
    object_name: str,
    preset: str = "COTTON",
    collision_objects: str = None
) -> str:
    """
    Add cloth simulation to a mesh.

    Parameters:
    - object_name: Name of the mesh object
    - preset: Material preset (COTTON, DENIM, LEATHER, RUBBER, SILK)
    - collision_objects: Optional JSON array of collision object names

    Returns JSON with cloth simulation settings.
    """
    try:
        blender = get_blender_connection()
        params = {"object_name": object_name, "preset": preset}
        if collision_objects:
            params["collision_objects"] = json.loads(collision_objects)
        result = blender.send_command("add_cloth_simulation", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding cloth: {str(e)}")
        return json.dumps({"error": f"Error adding cloth: {str(e)}"})


@telemetry_tool("add_collision")
@mcp.tool()
def add_collision(
    ctx: Context,
    object_name: str,
    damping: float = 0.1,
    thickness: float = 0.02
) -> str:
    """
    Add collision physics to an object for cloth/soft body interaction.

    Parameters:
    - object_name: Name of the object
    - damping: Collision damping (default: 0.1)
    - thickness: Collision thickness (default: 0.02)

    Returns JSON with collision settings.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("add_collision", {
            "object_name": object_name,
            "damping": damping,
            "thickness": thickness
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding collision: {str(e)}")
        return json.dumps({"error": f"Error adding collision: {str(e)}"})


@telemetry_tool("create_force_field")
@mcp.tool()
def create_force_field(
    ctx: Context,
    field_type: str,
    strength: float = 10.0,
    location_x: float = 0.0,
    location_y: float = 0.0,
    location_z: float = 0.0
) -> str:
    """
    Create a force field for physics simulations.

    Parameters:
    - field_type: WIND, VORTEX, TURBULENCE, FORCE, MAGNET, HARMONIC, CHARGE
    - strength: Field strength (default: 10.0)
    - location_x, location_y, location_z: Field position

    Returns JSON with force field details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_force_field", {
            "field_type": field_type,
            "strength": strength,
            "location": [location_x, location_y, location_z]
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating force field: {str(e)}")
        return json.dumps({"error": f"Error creating force field: {str(e)}"})


@telemetry_tool("bake_physics")
@mcp.tool()
def bake_physics(
    ctx: Context,
    start_frame: int = 1,
    end_frame: int = 250
) -> str:
    """
    Bake all physics simulations in the scene.

    Parameters:
    - start_frame: Start frame for baking (default: 1)
    - end_frame: End frame for baking (default: 250)

    Returns JSON with bake result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("bake_physics", {
            "start_frame": start_frame,
            "end_frame": end_frame
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error baking physics: {str(e)}")
        return json.dumps({"error": f"Error baking physics: {str(e)}"})


@telemetry_tool("add_particle_system")
@mcp.tool()
def add_particle_system(
    ctx: Context,
    object_name: str,
    count: int = 1000,
    lifetime: int = 50,
    emit_from: str = "FACE",
    render_type: str = "HALO"
) -> str:
    """
    Add a particle emitter system to an object.

    Parameters:
    - object_name: Name of the emitter object
    - count: Number of particles (default: 1000)
    - lifetime: Particle lifetime in frames (default: 50)
    - emit_from: FACE, VERT, VOLUME (default: FACE)
    - render_type: NONE, HALO, PATH, OBJECT, COLLECTION (default: HALO)

    Returns JSON with particle system settings.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("add_particle_system", {
            "object_name": object_name,
            "count": count,
            "lifetime": lifetime,
            "emit_from": emit_from,
            "render_type": render_type
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding particle system: {str(e)}")
        return json.dumps({"error": f"Error adding particle system: {str(e)}"})


# =============================================================================
# CAMERA & RENDERING SYSTEM
# =============================================================================


@telemetry_tool("create_camera")
@mcp.tool()
def create_camera(
    ctx: Context,
    name: str = "Camera",
    location_x: float = 0.0,
    location_y: float = -10.0,
    location_z: float = 5.0,
    focal_length: float = 50.0
) -> str:
    """
    Create a new camera in the scene.

    Parameters:
    - name: Camera name (default: "Camera")
    - location_x, location_y, location_z: Camera position
    - focal_length: Lens focal length in mm (default: 50.0)

    Returns JSON with camera details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_camera", {
            "name": name,
            "location": [location_x, location_y, location_z],
            "focal_length": focal_length
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating camera: {str(e)}")
        return json.dumps({"error": f"Error creating camera: {str(e)}"})


@telemetry_tool("set_active_camera")
@mcp.tool()
def set_active_camera(ctx: Context, camera_name: str) -> str:
    """
    Set the active camera for rendering.

    Parameters:
    - camera_name: Name of the camera to make active

    Returns JSON with result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("set_active_camera", {"camera_name": camera_name})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting active camera: {str(e)}")
        return json.dumps({"error": f"Error setting active camera: {str(e)}"})


@telemetry_tool("configure_camera")
@mcp.tool()
def configure_camera(
    ctx: Context,
    camera_name: str,
    focal_length: float = None,
    dof_focus_object: str = None,
    aperture: float = None,
    sensor_width: float = None
) -> str:
    """
    Configure camera settings including depth of field.

    Parameters:
    - camera_name: Name of the camera
    - focal_length: Lens focal length in mm
    - dof_focus_object: Object name for DOF focus
    - aperture: F-stop value for DOF
    - sensor_width: Camera sensor width in mm

    Returns JSON with camera settings.
    """
    try:
        blender = get_blender_connection()
        params = {"camera_name": camera_name}
        if focal_length is not None:
            params["focal_length"] = focal_length
        if dof_focus_object is not None:
            params["dof_focus_object"] = dof_focus_object
        if aperture is not None:
            params["aperture"] = aperture
        if sensor_width is not None:
            params["sensor_width"] = sensor_width
        result = blender.send_command("configure_camera", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error configuring camera: {str(e)}")
        return json.dumps({"error": f"Error configuring camera: {str(e)}"})


@telemetry_tool("camera_look_at")
@mcp.tool()
def camera_look_at(
    ctx: Context,
    camera_name: str,
    target_object: str = None,
    target_point: str = None
) -> str:
    """
    Point a camera at an object or location.

    Parameters:
    - camera_name: Name of the camera
    - target_object: Name of object to look at
    - target_point: JSON array point to look at, e.g., "[0, 0, 0]"

    Returns JSON with camera orientation.
    """
    try:
        blender = get_blender_connection()
        params = {"camera_name": camera_name}
        if target_object:
            params["target_object"] = target_object
        if target_point:
            params["target_point"] = json.loads(target_point)
        result = blender.send_command("camera_look_at", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error pointing camera: {str(e)}")
        return json.dumps({"error": f"Error pointing camera: {str(e)}"})


@telemetry_tool("set_render_settings")
@mcp.tool()
def set_render_settings(
    ctx: Context,
    engine: str = "CYCLES",
    samples: int = 128,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    denoise: bool = True,
    use_gpu: bool = True
) -> str:
    """
    Configure render engine and settings.

    Parameters:
    - engine: CYCLES, BLENDER_EEVEE, or BLENDER_WORKBENCH (default: CYCLES)
    - samples: Render samples (default: 128)
    - resolution_x, resolution_y: Output resolution (default: 1920x1080)
    - denoise: Enable denoising (default: True)
    - use_gpu: Use GPU for rendering if available (default: True)

    Returns JSON with render settings.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("set_render_settings", {
            "engine": engine,
            "samples": samples,
            "resolution": [resolution_x, resolution_y],
            "denoise": denoise,
            "use_gpu": use_gpu
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting render settings: {str(e)}")
        return json.dumps({"error": f"Error setting render settings: {str(e)}"})


@telemetry_tool("render_image")
@mcp.tool()
def render_image(
    ctx: Context,
    filepath: str,
    format: str = "PNG"
) -> str:
    """
    Render the current frame to an image file.

    Parameters:
    - filepath: Output file path (without extension)
    - format: Image format PNG, JPEG, EXR, TIFF (default: PNG)

    Returns JSON with render result and file path.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("render_image", {
            "filepath": filepath,
            "format": format
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error rendering image: {str(e)}")
        return json.dumps({"error": f"Error rendering image: {str(e)}"})


@telemetry_tool("render_animation")
@mcp.tool()
def render_animation(
    ctx: Context,
    output_path: str,
    format: str = "PNG",
    start_frame: int = None,
    end_frame: int = None
) -> str:
    """
    Render animation sequence.

    Parameters:
    - output_path: Output directory and filename base
    - format: Frame format PNG, JPEG, EXR, or FFMPEG for video (default: PNG)
    - start_frame: Start frame (uses scene default if not specified)
    - end_frame: End frame (uses scene default if not specified)

    Returns JSON with render result.
    """
    try:
        blender = get_blender_connection()
        params = {"output_path": output_path, "format": format}
        if start_frame is not None:
            params["start_frame"] = start_frame
        if end_frame is not None:
            params["end_frame"] = end_frame
        result = blender.send_command("render_animation", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error rendering animation: {str(e)}")
        return json.dumps({"error": f"Error rendering animation: {str(e)}"})


@telemetry_tool("setup_studio_render")
@mcp.tool()
def setup_studio_render(
    ctx: Context,
    target_object: str = None,
    style: str = "PRODUCT",
    background_color: str = None
) -> str:
    """
    Set up a professional studio render environment.

    Parameters:
    - target_object: Object to focus on (optional)
    - style: PRODUCT, PORTRAIT, DRAMATIC, SOFT (default: PRODUCT)
    - background_color: JSON RGB array, e.g., "[1.0, 1.0, 1.0]" for white

    Returns JSON with studio setup details.
    """
    try:
        blender = get_blender_connection()
        params = {"style": style}
        if target_object:
            params["target_object"] = target_object
        if background_color:
            params["background_color"] = json.loads(background_color)
        result = blender.send_command("setup_studio_render", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting up studio: {str(e)}")
        return json.dumps({"error": f"Error setting up studio: {str(e)}"})


# =============================================================================
# CURVES & TEXT SYSTEM
# =============================================================================


@telemetry_tool("create_bezier_curve")
@mcp.tool()
def create_bezier_curve(
    ctx: Context,
    points: str,
    name: str = "Curve",
    resolution: int = 12,
    closed: bool = False
) -> str:
    """
    Create a bezier curve from control points.

    Parameters:
    - points: JSON array of point coordinates, e.g., "[[0,0,0], [1,0,1], [2,0,0]]"
    - name: Curve object name (default: "Curve")
    - resolution: Curve resolution (default: 12)
    - closed: Close the curve into a loop (default: False)

    Returns JSON with curve details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_bezier_curve", {
            "points": json.loads(points),
            "name": name,
            "resolution": resolution,
            "closed": closed
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating curve: {str(e)}")
        return json.dumps({"error": f"Error creating curve: {str(e)}"})


@telemetry_tool("create_text_object")
@mcp.tool()
def create_text_object(
    ctx: Context,
    text: str,
    name: str = "Text",
    size: float = 1.0,
    extrude: float = 0.0,
    bevel_depth: float = 0.0,
    font: str = None
) -> str:
    """
    Create a 3D text object.

    Parameters:
    - text: The text content
    - name: Object name (default: "Text")
    - size: Text size (default: 1.0)
    - extrude: Extrusion depth (default: 0.0)
    - bevel_depth: Bevel depth for rounded edges (default: 0.0)
    - font: Font file path or Blender font name

    Returns JSON with text object details.
    """
    try:
        blender = get_blender_connection()
        params = {
            "text": text,
            "name": name,
            "size": size,
            "extrude": extrude,
            "bevel_depth": bevel_depth
        }
        if font:
            params["font"] = font
        result = blender.send_command("create_text_object", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating text: {str(e)}")
        return json.dumps({"error": f"Error creating text: {str(e)}"})


@telemetry_tool("curve_to_mesh")
@mcp.tool()
def curve_to_mesh(ctx: Context, curve_name: str) -> str:
    """
    Convert a curve object to a mesh.

    Parameters:
    - curve_name: Name of the curve object to convert

    Returns JSON with resulting mesh details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("curve_to_mesh", {"curve_name": curve_name})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error converting curve to mesh: {str(e)}")
        return json.dumps({"error": f"Error converting curve to mesh: {str(e)}"})


@telemetry_tool("create_pipe")
@mcp.tool()
def create_pipe(
    ctx: Context,
    curve_name: str,
    radius: float = 0.1,
    resolution: int = 8,
    fill_caps: bool = True
) -> str:
    """
    Create a pipe/tube mesh along a curve.

    Parameters:
    - curve_name: Name of the curve to follow
    - radius: Pipe radius (default: 0.1)
    - resolution: Circular resolution (default: 8)
    - fill_caps: Cap the ends (default: True)

    Returns JSON with pipe mesh details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_pipe", {
            "curve_name": curve_name,
            "radius": radius,
            "resolution": resolution,
            "fill_caps": fill_caps
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating pipe: {str(e)}")
        return json.dumps({"error": f"Error creating pipe: {str(e)}"})


# =============================================================================
# CONSTRAINTS & RELATIONSHIPS
# =============================================================================


@telemetry_tool("add_constraint")
@mcp.tool()
def add_constraint(
    ctx: Context,
    object_name: str,
    constraint_type: str,
    target_object: str = None,
    settings: str = None
) -> str:
    """
    Add a constraint to an object.

    Parameters:
    - object_name: Name of the object to constrain
    - constraint_type: COPY_LOCATION, COPY_ROTATION, COPY_SCALE, TRACK_TO,
                       LIMIT_LOCATION, LIMIT_ROTATION, CHILD_OF, FLOOR, etc.
    - target_object: Target object for the constraint
    - settings: JSON string of additional constraint settings

    Returns JSON with constraint details.
    """
    try:
        blender = get_blender_connection()
        params = {
            "object_name": object_name,
            "constraint_type": constraint_type
        }
        if target_object:
            params["target_object"] = target_object
        if settings:
            params["settings"] = json.loads(settings)
        result = blender.send_command("add_constraint", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding constraint: {str(e)}")
        return json.dumps({"error": f"Error adding constraint: {str(e)}"})


@telemetry_tool("create_empty")
@mcp.tool()
def create_empty(
    ctx: Context,
    name: str = "Empty",
    empty_type: str = "PLAIN_AXES",
    location_x: float = 0.0,
    location_y: float = 0.0,
    location_z: float = 0.0,
    size: float = 1.0
) -> str:
    """
    Create an empty object for use as control or parent.

    Parameters:
    - name: Empty name (default: "Empty")
    - empty_type: PLAIN_AXES, ARROWS, SINGLE_ARROW, CIRCLE, CUBE, SPHERE
    - location_x, location_y, location_z: Position
    - size: Display size (default: 1.0)

    Returns JSON with empty object details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_empty", {
            "name": name,
            "empty_type": empty_type,
            "location": [location_x, location_y, location_z],
            "size": size
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating empty: {str(e)}")
        return json.dumps({"error": f"Error creating empty: {str(e)}"})


@telemetry_tool("parent_objects")
@mcp.tool()
def parent_objects(
    ctx: Context,
    child_names: str,
    parent_name: str,
    keep_transform: bool = True
) -> str:
    """
    Set parent-child relationships between objects.

    Parameters:
    - child_names: JSON array of child object names
    - parent_name: Name of the parent object
    - keep_transform: Maintain child world transforms (default: True)

    Returns JSON with parenting result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("parent_objects", {
            "child_names": json.loads(child_names),
            "parent_name": parent_name,
            "keep_transform": keep_transform
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error parenting objects: {str(e)}")
        return json.dumps({"error": f"Error parenting objects: {str(e)}"})


# =============================================================================
# SCENE ORGANIZATION
# =============================================================================


@telemetry_tool("create_collection")
@mcp.tool()
def create_collection(
    ctx: Context,
    name: str,
    parent_collection: str = None,
    color_tag: str = "NONE"
) -> str:
    """
    Create a new collection for organizing objects.

    Parameters:
    - name: Collection name
    - parent_collection: Parent collection name (default: Scene Collection)
    - color_tag: Color tag NONE, COLOR_01 through COLOR_08

    Returns JSON with collection details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_collection", {
            "name": name,
            "parent_collection": parent_collection,
            "color_tag": color_tag
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        return json.dumps({"error": f"Error creating collection: {str(e)}"})


@telemetry_tool("move_to_collection")
@mcp.tool()
def move_to_collection(
    ctx: Context,
    object_names: str,
    collection_name: str
) -> str:
    """
    Move objects to a collection.

    Parameters:
    - object_names: JSON array of object names to move
    - collection_name: Target collection name

    Returns JSON with result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("move_to_collection", {
            "object_names": json.loads(object_names),
            "collection_name": collection_name
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error moving to collection: {str(e)}")
        return json.dumps({"error": f"Error moving to collection: {str(e)}"})


@telemetry_tool("set_collection_visibility")
@mcp.tool()
def set_collection_visibility(
    ctx: Context,
    collection_name: str,
    visible: bool = True,
    render_visible: bool = True
) -> str:
    """
    Set collection visibility in viewport and render.

    Parameters:
    - collection_name: Name of the collection
    - visible: Viewport visibility (default: True)
    - render_visible: Render visibility (default: True)

    Returns JSON with visibility settings.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("set_collection_visibility", {
            "collection_name": collection_name,
            "visible": visible,
            "render_visible": render_visible
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting visibility: {str(e)}")
        return json.dumps({"error": f"Error setting visibility: {str(e)}"})


@telemetry_tool("duplicate_linked")
@mcp.tool()
def duplicate_linked(
    ctx: Context,
    object_name: str,
    new_name: str = None
) -> str:
    """
    Create a linked duplicate that shares mesh data.

    Parameters:
    - object_name: Name of the object to duplicate
    - new_name: Name for the new object (auto-generated if not specified)

    Returns JSON with new object details.
    """
    try:
        blender = get_blender_connection()
        params = {"object_name": object_name}
        if new_name:
            params["new_name"] = new_name
        result = blender.send_command("duplicate_linked", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error duplicating linked: {str(e)}")
        return json.dumps({"error": f"Error duplicating linked: {str(e)}"})


@telemetry_tool("purge_unused")
@mcp.tool()
def purge_unused(ctx: Context) -> str:
    """
    Remove all unused data blocks (orphan data).

    Returns JSON with purge statistics.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("purge_unused", {})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error purging: {str(e)}")
        return json.dumps({"error": f"Error purging: {str(e)}"})


@telemetry_tool("save_blend")
@mcp.tool()
def save_blend(
    ctx: Context,
    filepath: str,
    compress: bool = True
) -> str:
    """
    Save the current scene as a .blend file.

    Parameters:
    - filepath: Output file path (should end in .blend)
    - compress: Compress the file (default: True)

    Returns JSON with save result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("save_blend", {
            "filepath": filepath,
            "compress": compress
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error saving blend: {str(e)}")
        return json.dumps({"error": f"Error saving blend: {str(e)}"})


@telemetry_tool("export_scene")
@mcp.tool()
def export_scene(
    ctx: Context,
    filepath: str,
    format: str = "GLTF",
    selected_only: bool = False,
    apply_modifiers: bool = True
) -> str:
    """
    Export scene to external format.

    Parameters:
    - filepath: Output file path
    - format: GLTF, GLB, FBX, OBJ, STL (default: GLTF)
    - selected_only: Export only selected objects (default: False)
    - apply_modifiers: Apply modifiers before export (default: True)

    Returns JSON with export result.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("export_scene", {
            "filepath": filepath,
            "format": format,
            "selected_only": selected_only,
            "apply_modifiers": apply_modifiers
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error exporting: {str(e)}")
        return json.dumps({"error": f"Error exporting: {str(e)}"})


# =============================================================================
# GEOMETRY NODES / PROCEDURAL GENERATION
# =============================================================================


@telemetry_tool("scatter_on_surface")
@mcp.tool()
def scatter_on_surface(
    ctx: Context,
    surface_object: str,
    instance_object: str,
    density: float = 10.0,
    seed: int = 0,
    scale_min: float = 0.8,
    scale_max: float = 1.2,
    align_to_normal: bool = True
) -> str:
    """
    Scatter instances of an object on a surface using geometry nodes.

    Parameters:
    - surface_object: Name of the surface mesh
    - instance_object: Name of the object to scatter
    - density: Instances per square unit (default: 10.0)
    - seed: Random seed (default: 0)
    - scale_min, scale_max: Scale variation range (default: 0.8-1.2)
    - align_to_normal: Align instances to surface normal (default: True)

    Returns JSON with scatter details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("scatter_on_surface", {
            "surface_object": surface_object,
            "instance_object": instance_object,
            "density": density,
            "seed": seed,
            "scale_min": scale_min,
            "scale_max": scale_max,
            "align_to_normal": align_to_normal
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error scattering: {str(e)}")
        return json.dumps({"error": f"Error scattering: {str(e)}"})


@telemetry_tool("create_procedural_terrain")
@mcp.tool()
def create_procedural_terrain(
    ctx: Context,
    name: str = "Terrain",
    size: float = 10.0,
    resolution: int = 100,
    height_scale: float = 2.0,
    noise_scale: float = 1.0,
    seed: int = 0
) -> str:
    """
    Generate procedural terrain mesh with noise displacement.

    Parameters:
    - name: Terrain object name (default: "Terrain")
    - size: Terrain size in units (default: 10.0)
    - resolution: Mesh subdivision resolution (default: 100)
    - height_scale: Maximum height variation (default: 2.0)
    - noise_scale: Noise pattern scale (default: 1.0)
    - seed: Random seed (default: 0)

    Returns JSON with terrain details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_procedural_terrain", {
            "name": name,
            "size": size,
            "resolution": resolution,
            "height_scale": height_scale,
            "noise_scale": noise_scale,
            "seed": seed
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error creating terrain: {str(e)}")
        return json.dumps({"error": f"Error creating terrain: {str(e)}"})


# Main execution


def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
