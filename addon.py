# BlenderForge - AI-powered Blender Integration
# Copyright (c) 2025 BlenderForge Team
#   - Mithun Gowda B <mithungowda.b7411@gmail.com> (mithun50)
#   - Nevil D'Souza <nevilansondsouza@gmail.com> (nevil06)
#   - Lekhan H R (lekhanpro)
#   - Manvanth Gowda M <appuka1431@gmail.com> (appukannadiga)
#   - NXG Team (Organization) <nxgextra@gmail.com> (NextGenXplorer)
# Licensed under the MIT License

import base64
import hashlib
import hmac
import io
import json
import os
import os.path as osp
import re
import secrets
import shutil
import socket
import tempfile
import threading
import time
import traceback
import zipfile
from contextlib import redirect_stdout, suppress
from datetime import datetime

import bpy
import mathutils
import requests
from bpy.props import BoolProperty, IntProperty

bl_info = {
    "name": "BlenderForge",
    "author": "Mithun Gowda B",
    "version": (1, 0, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > BlenderForge",
    "description": "AI-powered Blender integration for 3D modeling",
    "category": "Interface",
    "doc_url": "https://github.com/mithun50/blenderforge",
    "tracker_url": "https://github.com/mithun50/blenderforge/issues",
}

# API keys should be set via environment variables for security
# Set BLENDERFORGE_RODIN_API_KEY environment variable to use Rodin API
# Or configure via addon preferences
def get_rodin_api_key():
    """Get Rodin API key from environment or return None."""
    return os.environ.get("BLENDERFORGE_RODIN_API_KEY")

# Add User-Agent as required by Poly Haven API
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blenderforge"})


class BlenderForgeServer:
    def __init__(self, host="localhost", port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None
        # Generate auth token for secure communication
        self.auth_token = secrets.token_hex(32)
        self._temp_files = set()  # Track temp files for cleanup

    def start(self):
        if self.running:
            print("Server is already running")
            return

        self.running = True

        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)

            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"BlenderForge server started on {self.host}:{self.port}")
            print(f"Auth token: {self.auth_token}")
            # Store token in environment for MCP server to read
            os.environ["BLENDERFORGE_AUTH_TOKEN"] = self.auth_token
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()

    def stop(self):
        self.running = False

        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"Error closing socket: {e}")
            self.socket = None

        # Wait for thread to finish
        if self.server_thread:
            try:
                if self.server_thread.is_alive():
                    self.server_thread.join(timeout=1.0)
            except Exception as e:
                print(f"Error joining thread: {e}")
            self.server_thread = None

        # Cleanup temp files
        self._cleanup_temp_files()

        # Clear auth token from environment
        if "BLENDERFORGE_AUTH_TOKEN" in os.environ:
            del os.environ["BLENDERFORGE_AUTH_TOKEN"]

        print("BlenderForge server stopped")

    def _cleanup_temp_files(self):
        """Clean up all tracked temporary files"""
        for temp_path in list(self._temp_files):
            try:
                if os.path.isfile(temp_path):
                    os.unlink(temp_path)
                elif os.path.isdir(temp_path):
                    shutil.rmtree(temp_path)
                self._temp_files.discard(temp_path)
            except Exception as e:
                print(f"Failed to cleanup temp file {temp_path}: {e}")

    def _track_temp_file(self, path):
        """Track a temporary file for cleanup"""
        self._temp_files.add(path)

    @staticmethod
    def _make_error_response(message: str, details: str = None) -> dict:
        """Create a consistent error response format"""
        response = {"error": message}
        if details:
            response["details"] = details
        return response

    @staticmethod
    def _make_success_response(result: dict = None, message: str = None) -> dict:
        """Create a consistent success response format"""
        response = {"success": True}
        if message:
            response["message"] = message
        if result:
            response.update(result)
        return response

    def _server_loop(self):
        """Main server loop in a separate thread"""
        print("Server thread started")
        self.socket.settimeout(1.0)  # Timeout to allow for stopping

        while self.running:
            try:
                # Accept new connection
                try:
                    client, address = self.socket.accept()
                    print(f"Connected to client: {address}")

                    # Handle client in a separate thread
                    client_thread = threading.Thread(target=self._handle_client, args=(client,))
                    client_thread.daemon = True
                    client_thread.start()
                except TimeoutError:
                    # Just check running condition
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {str(e)}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in server loop: {str(e)}")
                if not self.running:
                    break
                time.sleep(0.5)

        print("Server thread stopped")

    def _handle_client(self, client):
        """Handle connected client"""
        print("Client handler started")
        client.settimeout(None)  # No timeout
        buffer = b""

        try:
            while self.running:
                # Receive data
                try:
                    data = client.recv(8192)
                    if not data:
                        print("Client disconnected")
                        break

                    buffer += data
                    try:
                        # Try to parse command
                        command = json.loads(buffer.decode("utf-8"))
                        buffer = b""

                        # Execute command in Blender's main thread
                        def execute_wrapper():
                            try:
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                try:
                                    client.sendall(response_json.encode("utf-8"))
                                except:
                                    print("Failed to send response - client disconnected")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                traceback.print_exc()
                                try:
                                    error_response = {"status": "error", "message": str(e)}
                                    client.sendall(json.dumps(error_response).encode("utf-8"))
                                except:
                                    pass
                            return None

                        # Schedule execution in main thread
                        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    except json.JSONDecodeError:
                        # Incomplete data, wait for more
                        pass
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Error in client handler: {str(e)}")
        finally:
            try:
                client.close()
            except:
                pass
            print("Client handler stopped")

    def execute_command(self, command):
        """Execute a command in the main Blender thread"""
        try:
            return self._execute_command_internal(command)

        except Exception as e:
            print(f"Error executing command: {str(e)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _execute_command_internal(self, command):
        """Internal command execution with proper context"""
        cmd_type = command.get("type")
        params = command.get("params", {})

        # Verify auth token if provided (backwards compatible)
        provided_token = command.get("auth_token")
        if provided_token and provided_token != self.auth_token:
            return {"status": "error", "message": "Invalid authentication token"}

        # Add a handler for checking PolyHaven status
        if cmd_type == "get_polyhaven_status":
            return {"status": "success", "result": self.get_polyhaven_status()}

        # Base handlers that are always available
        handlers = {
            "get_scene_info": self.get_scene_info,
            "get_object_info": self.get_object_info,
            "get_viewport_screenshot": self.get_viewport_screenshot,
            "execute_code": self.execute_code,
            "get_telemetry_consent": self.get_telemetry_consent,
            "get_polyhaven_status": self.get_polyhaven_status,
            "get_hyper3d_status": self.get_hyper3d_status,
            "get_sketchfab_status": self.get_sketchfab_status,
            "get_hunyuan3d_status": self.get_hunyuan3d_status,
        }

        # Add Polyhaven handlers only if enabled
        if bpy.context.scene.blenderforge_use_polyhaven:
            polyhaven_handlers = {
                "get_polyhaven_categories": self.get_polyhaven_categories,
                "search_polyhaven_assets": self.search_polyhaven_assets,
                "download_polyhaven_asset": self.download_polyhaven_asset,
                "set_texture": self.set_texture,
            }
            handlers.update(polyhaven_handlers)

        # Add Hyper3d handlers only if enabled
        if bpy.context.scene.blenderforge_use_hyper3d:
            hyper3d_handlers = {
                "create_rodin_job": self.create_rodin_job,
                "poll_rodin_job_status": self.poll_rodin_job_status,
                "import_generated_asset": self.import_generated_asset,
            }
            handlers.update(hyper3d_handlers)

        # Add Sketchfab handlers only if enabled
        if bpy.context.scene.blenderforge_use_sketchfab:
            sketchfab_handlers = {
                "search_sketchfab_models": self.search_sketchfab_models,
                "get_sketchfab_model_preview": self.get_sketchfab_model_preview,
                "download_sketchfab_model": self.download_sketchfab_model,
            }
            handlers.update(sketchfab_handlers)

        # Add Hunyuan3d handlers only if enabled
        if bpy.context.scene.blenderforge_use_hunyuan3d:
            hunyuan_handlers = {
                "create_hunyuan_job": self.create_hunyuan_job,
                "poll_hunyuan_job_status": self.poll_hunyuan_job_status,
                "import_generated_asset_hunyuan": self.import_generated_asset_hunyuan,
            }
            handlers.update(hunyuan_handlers)

        # AI-powered feature handlers (always available)
        ai_handlers = {
            # Material Generator
            "generate_material_text": self.generate_material_text,
            "generate_material_image": self.generate_material_image,
            "list_material_presets": self.list_material_presets,
            # Natural Language Modeling
            "nlp_create": self.nlp_create,
            "nlp_modify": self.nlp_modify,
            # Scene Analyzer
            "analyze_scene_composition": self.analyze_scene_composition,
            "get_improvement_suggestions": self.get_improvement_suggestions,
            "auto_optimize_lighting": self.auto_optimize_lighting,
            # Auto-Rig
            "auto_rig": self.auto_rig,
            "auto_weight_paint": self.auto_weight_paint,
            "add_ik_controls": self.add_ik_controls,
        }
        handlers.update(ai_handlers)

        # Advanced Features handlers
        advanced_handlers = {
            # Modifier System
            "add_modifier": self.add_modifier,
            "configure_modifier": self.configure_modifier,
            "apply_modifier": self.apply_modifier,
            "boolean_operation": self.boolean_operation,
            "create_array": self.create_array,
            "add_bevel": self.add_bevel,
            "mirror_object": self.mirror_object,
            "subdivide_smooth": self.subdivide_smooth,
            # Mesh Editing Operations
            "extrude_faces": self.extrude_faces,
            "inset_faces": self.inset_faces,
            "loop_cut": self.loop_cut,
            "merge_vertices": self.merge_vertices,
            "separate_by_loose": self.separate_by_loose,
            "join_objects": self.join_objects,
            # Animation System
            "insert_keyframe": self.insert_keyframe,
            "set_animation_range": self.set_animation_range,
            "create_turntable": self.create_turntable,
            "add_shape_key": self.add_shape_key,
            "animate_shape_key": self.animate_shape_key,
            "animate_path": self.animate_path,
            "bake_animation": self.bake_animation,
            # Physics Simulation
            "add_rigid_body": self.add_rigid_body,
            "add_cloth_simulation": self.add_cloth_simulation,
            "add_collision": self.add_collision,
            "create_force_field": self.create_force_field,
            "bake_physics": self.bake_physics,
            "add_particle_system": self.add_particle_system,
            # Camera & Rendering System
            "create_camera": self.create_camera,
            "set_active_camera": self.set_active_camera,
            "configure_camera": self.configure_camera,
            "camera_look_at": self.camera_look_at,
            "set_render_settings": self.set_render_settings,
            "render_image": self.render_image,
            "render_animation": self.render_animation,
            "setup_studio_render": self.setup_studio_render,
            # Curves & Text System
            "create_bezier_curve": self.create_bezier_curve,
            "create_text_object": self.create_text_object,
            "curve_to_mesh": self.curve_to_mesh,
            "create_pipe": self.create_pipe,
            # Constraints & Relationships
            "add_constraint": self.add_constraint,
            "create_empty": self.create_empty,
            "parent_objects": self.parent_objects,
            # Scene Organization
            "create_collection": self.create_collection,
            "move_to_collection": self.move_to_collection,
            "set_collection_visibility": self.set_collection_visibility,
            "duplicate_linked": self.duplicate_linked,
            "purge_unused": self.purge_unused,
            "save_blend": self.save_blend,
            "export_scene": self.export_scene,
            # Geometry Nodes / Procedural Generation
            "scatter_on_surface": self.scatter_on_surface,
            "create_procedural_terrain": self.create_procedural_terrain,
        }
        handlers.update(advanced_handlers)

        handler = handlers.get(cmd_type)
        if handler:
            try:
                print(f"Executing handler for {cmd_type}")
                result = handler(**params)
                print("Handler execution complete")
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"Error in handler: {str(e)}")
                traceback.print_exc()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

    def get_scene_info(self):
        """Get information about the current Blender scene"""
        try:
            print("Getting scene info...")
            # Simplify the scene info to reduce data size
            scene_info = {
                "name": bpy.context.scene.name,
                "object_count": len(bpy.context.scene.objects),
                "objects": [],
                "materials_count": len(bpy.data.materials),
            }

            # Collect minimal object information (limit to first 10 objects)
            for i, obj in enumerate(bpy.context.scene.objects):
                if i >= 10:  # Reduced from 20 to 10
                    break

                obj_info = {
                    "name": obj.name,
                    "type": obj.type,
                    # Only include basic location data
                    "location": [
                        round(float(obj.location.x), 2),
                        round(float(obj.location.y), 2),
                        round(float(obj.location.z), 2),
                    ],
                }
                scene_info["objects"].append(obj_info)

            print(f"Scene info collected: {len(scene_info['objects'])} objects")
            return scene_info
        except Exception as e:
            print(f"Error in get_scene_info: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}

    @staticmethod
    def _get_aabb(obj):
        """Returns the world-space axis-aligned bounding box (AABB) of an object."""
        if obj.type != "MESH":
            raise TypeError("Object must be a mesh")

        # Get the bounding box corners in local space
        local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]

        # Convert to world coordinates
        world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]

        # Compute axis-aligned min/max coordinates
        min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
        max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))

        return [[*min_corner], [*max_corner]]

    def get_object_info(self, name):
        """Get detailed information about a specific object"""
        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object not found: {name}")

        # Basic object info
        obj_info = {
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            "visible": obj.visible_get(),
            "materials": [],
        }

        if obj.type == "MESH":
            bounding_box = self._get_aabb(obj)
            obj_info["world_bounding_box"] = bounding_box

        # Add material slots
        for slot in obj.material_slots:
            if slot.material:
                obj_info["materials"].append(slot.material.name)

        # Add mesh data if applicable
        if obj.type == "MESH" and obj.data:
            mesh = obj.data
            obj_info["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
            }

        return obj_info

    def get_viewport_screenshot(self, max_size=800, filepath=None, format="png"):
        """
        Capture a screenshot of the current 3D viewport and save it to the specified path.

        Parameters:
        - max_size: Maximum size in pixels for the largest dimension of the image
        - filepath: Path where to save the screenshot file
        - format: Image format (png, jpg, etc.)

        Returns success/error status
        """
        try:
            if not filepath:
                return {"error": "No filepath provided"}

            # Find the active 3D viewport
            area = None
            for a in bpy.context.screen.areas:
                if a.type == "VIEW_3D":
                    area = a
                    break

            if not area:
                return {"error": "No 3D viewport found"}

            # Take screenshot with proper context override
            with bpy.context.temp_override(area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)

            # Load and resize if needed
            img = bpy.data.images.load(filepath)
            width, height = img.size

            if max(width, height) > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img.scale(new_width, new_height)

                # Set format and save
                img.file_format = format.upper()
                img.save()
                width, height = new_width, new_height

            # Cleanup Blender image data
            bpy.data.images.remove(img)

            return {"success": True, "width": width, "height": height, "filepath": filepath}

        except Exception as e:
            return {"error": str(e)}

    def execute_code(self, code):
        """Execute arbitrary Blender Python code"""
        # This is powerful but potentially dangerous - use with caution
        try:
            # Create a local namespace for execution
            namespace = {"bpy": bpy}

            # Capture stdout during execution, and return it as result
            capture_buffer = io.StringIO()
            with redirect_stdout(capture_buffer):
                exec(code, namespace)

            captured_output = capture_buffer.getvalue()
            return {"executed": True, "result": captured_output}
        except Exception as e:
            raise Exception(f"Code execution error: {str(e)}")

    def get_polyhaven_categories(self, asset_type):
        """Get categories for a specific asset type from Polyhaven"""
        try:
            if asset_type not in ["hdris", "textures", "models", "all"]:
                return {
                    "error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"
                }

            response = requests.get(
                f"https://api.polyhaven.com/categories/{asset_type}", headers=REQ_HEADERS
            )
            if response.status_code == 200:
                return {"categories": response.json()}
            else:
                return {"error": f"API request failed with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def search_polyhaven_assets(self, asset_type=None, categories=None):
        """Search for assets from Polyhaven with optional filtering"""
        try:
            url = "https://api.polyhaven.com/assets"
            params = {}

            if asset_type and asset_type != "all":
                if asset_type not in ["hdris", "textures", "models"]:
                    return {
                        "error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"
                    }
                params["type"] = asset_type

            if categories:
                params["categories"] = categories

            response = requests.get(url, params=params, headers=REQ_HEADERS)
            if response.status_code == 200:
                # Limit the response size to avoid overwhelming Blender
                assets = response.json()
                # Return only the first 20 assets to keep response size manageable
                limited_assets = {}
                for i, (key, value) in enumerate(assets.items()):
                    if i >= 20:  # Limit to 20 assets
                        break
                    limited_assets[key] = value

                return {
                    "assets": limited_assets,
                    "total_count": len(assets),
                    "returned_count": len(limited_assets),
                }
            else:
                return {"error": f"API request failed with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def download_polyhaven_asset(self, asset_id, asset_type, resolution="1k", file_format=None):
        try:
            # First get the files information
            files_response = requests.get(
                f"https://api.polyhaven.com/files/{asset_id}", headers=REQ_HEADERS
            )
            if files_response.status_code != 200:
                return {"error": f"Failed to get asset files: {files_response.status_code}"}

            files_data = files_response.json()

            # Handle different asset types
            if asset_type == "hdris":
                # For HDRIs, download the .hdr or .exr file
                if not file_format:
                    file_format = "hdr"  # Default format for HDRIs

                if (
                    "hdri" in files_data
                    and resolution in files_data["hdri"]
                    and file_format in files_data["hdri"][resolution]
                ):
                    file_info = files_data["hdri"][resolution][file_format]
                    file_url = file_info["url"]

                    # For HDRIs, we need to save to a temporary file first
                    # since Blender can't properly load HDR data directly from memory
                    with tempfile.NamedTemporaryFile(
                        suffix=f".{file_format}", delete=False
                    ) as tmp_file:
                        # Download the file
                        response = requests.get(file_url, headers=REQ_HEADERS)
                        if response.status_code != 200:
                            return {"error": f"Failed to download HDRI: {response.status_code}"}

                        tmp_file.write(response.content)
                        tmp_path = tmp_file.name

                    try:
                        # Create a new world if none exists
                        if not bpy.data.worlds:
                            bpy.data.worlds.new("World")

                        world = bpy.data.worlds[0]
                        world.use_nodes = True
                        node_tree = world.node_tree

                        # Clear existing nodes
                        for node in node_tree.nodes:
                            node_tree.nodes.remove(node)

                        # Create nodes
                        tex_coord = node_tree.nodes.new(type="ShaderNodeTexCoord")
                        tex_coord.location = (-800, 0)

                        mapping = node_tree.nodes.new(type="ShaderNodeMapping")
                        mapping.location = (-600, 0)

                        # Load the image from the temporary file
                        env_tex = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
                        env_tex.location = (-400, 0)
                        env_tex.image = bpy.data.images.load(tmp_path)

                        # Use a color space that exists in all Blender versions
                        if file_format.lower() == "exr":
                            # Try to use Linear color space for EXR files
                            try:
                                env_tex.image.colorspace_settings.name = "Linear"
                            except:
                                # Fallback to Non-Color if Linear isn't available
                                env_tex.image.colorspace_settings.name = "Non-Color"
                        else:  # hdr
                            # For HDR files, try these options in order
                            for color_space in ["Linear", "Linear Rec.709", "Non-Color"]:
                                try:
                                    env_tex.image.colorspace_settings.name = color_space
                                    break  # Stop if we successfully set a color space
                                except:
                                    continue

                        background = node_tree.nodes.new(type="ShaderNodeBackground")
                        background.location = (-200, 0)

                        output = node_tree.nodes.new(type="ShaderNodeOutputWorld")
                        output.location = (0, 0)

                        # Connect nodes
                        node_tree.links.new(
                            tex_coord.outputs["Generated"], mapping.inputs["Vector"]
                        )
                        node_tree.links.new(mapping.outputs["Vector"], env_tex.inputs["Vector"])
                        node_tree.links.new(env_tex.outputs["Color"], background.inputs["Color"])
                        node_tree.links.new(
                            background.outputs["Background"], output.inputs["Surface"]
                        )

                        # Set as active world
                        bpy.context.scene.world = world

                        # Clean up temporary file
                        try:
                            tempfile._cleanup()  # This will clean up all temporary files
                        except:
                            pass

                        return {
                            "success": True,
                            "message": f"HDRI {asset_id} imported successfully",
                            "image_name": env_tex.image.name,
                        }
                    except Exception as e:
                        return {"error": f"Failed to set up HDRI in Blender: {str(e)}"}
                else:
                    return {"error": "Requested resolution or format not available for this HDRI"}

            elif asset_type == "textures":
                if not file_format:
                    file_format = "jpg"  # Default format for textures

                downloaded_maps = {}

                try:
                    for map_type in files_data:
                        if map_type not in ["blend", "gltf"]:  # Skip non-texture files
                            if (
                                resolution in files_data[map_type]
                                and file_format in files_data[map_type][resolution]
                            ):
                                file_info = files_data[map_type][resolution][file_format]
                                file_url = file_info["url"]

                                # Use NamedTemporaryFile like we do for HDRIs
                                with tempfile.NamedTemporaryFile(
                                    suffix=f".{file_format}", delete=False
                                ) as tmp_file:
                                    # Download the file
                                    response = requests.get(file_url, headers=REQ_HEADERS)
                                    if response.status_code == 200:
                                        tmp_file.write(response.content)
                                        tmp_path = tmp_file.name

                                        # Load image from temporary file
                                        image = bpy.data.images.load(tmp_path)
                                        image.name = f"{asset_id}_{map_type}.{file_format}"

                                        # Pack the image into .blend file
                                        image.pack()

                                        # Set color space based on map type
                                        if map_type in ["color", "diffuse", "albedo"]:
                                            try:
                                                image.colorspace_settings.name = "sRGB"
                                            except:
                                                pass
                                        else:
                                            try:
                                                image.colorspace_settings.name = "Non-Color"
                                            except:
                                                pass

                                        downloaded_maps[map_type] = image

                                        # Clean up temporary file
                                        try:
                                            os.unlink(tmp_path)
                                        except:
                                            pass

                    if not downloaded_maps:
                        return {
                            "error": "No texture maps found for the requested resolution and format"
                        }

                    # Create a new material with the downloaded textures
                    mat = bpy.data.materials.new(name=asset_id)
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links

                    # Clear default nodes
                    for node in nodes:
                        nodes.remove(node)

                    # Create output node
                    output = nodes.new(type="ShaderNodeOutputMaterial")
                    output.location = (300, 0)

                    # Create principled BSDF node
                    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
                    principled.location = (0, 0)
                    links.new(principled.outputs[0], output.inputs[0])

                    # Add texture nodes based on available maps
                    tex_coord = nodes.new(type="ShaderNodeTexCoord")
                    tex_coord.location = (-800, 0)

                    mapping = nodes.new(type="ShaderNodeMapping")
                    mapping.location = (-600, 0)
                    mapping.vector_type = "TEXTURE"  # Changed from default 'POINT' to 'TEXTURE'
                    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])

                    # Position offset for texture nodes
                    x_pos = -400
                    y_pos = 300

                    # Connect different texture maps
                    for map_type, image in downloaded_maps.items():
                        tex_node = nodes.new(type="ShaderNodeTexImage")
                        tex_node.location = (x_pos, y_pos)
                        tex_node.image = image

                        # Set color space based on map type
                        if map_type.lower() in ["color", "diffuse", "albedo"]:
                            try:
                                tex_node.image.colorspace_settings.name = "sRGB"
                            except:
                                pass  # Use default if sRGB not available
                        else:
                            try:
                                tex_node.image.colorspace_settings.name = "Non-Color"
                            except:
                                pass  # Use default if Non-Color not available

                        links.new(mapping.outputs["Vector"], tex_node.inputs["Vector"])

                        # Connect to appropriate input on Principled BSDF
                        if map_type.lower() in ["color", "diffuse", "albedo"]:
                            links.new(tex_node.outputs["Color"], principled.inputs["Base Color"])
                        elif map_type.lower() in ["roughness", "rough"]:
                            links.new(tex_node.outputs["Color"], principled.inputs["Roughness"])
                        elif map_type.lower() in ["metallic", "metalness", "metal"]:
                            links.new(tex_node.outputs["Color"], principled.inputs["Metallic"])
                        elif map_type.lower() in ["normal", "nor"]:
                            # Add normal map node
                            normal_map = nodes.new(type="ShaderNodeNormalMap")
                            normal_map.location = (x_pos + 200, y_pos)
                            links.new(tex_node.outputs["Color"], normal_map.inputs["Color"])
                            links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
                        elif map_type in ["displacement", "disp", "height"]:
                            # Add displacement node
                            disp_node = nodes.new(type="ShaderNodeDisplacement")
                            disp_node.location = (x_pos + 200, y_pos - 200)
                            links.new(tex_node.outputs["Color"], disp_node.inputs["Height"])
                            links.new(
                                disp_node.outputs["Displacement"], output.inputs["Displacement"]
                            )

                        y_pos -= 250

                    return {
                        "success": True,
                        "message": f"Texture {asset_id} imported as material",
                        "material": mat.name,
                        "maps": list(downloaded_maps.keys()),
                    }

                except Exception as e:
                    return {"error": f"Failed to process textures: {str(e)}"}

            elif asset_type == "models":
                # For models, prefer glTF format if available
                if not file_format:
                    file_format = "gltf"  # Default format for models

                if file_format in files_data and resolution in files_data[file_format]:
                    file_info = files_data[file_format][resolution][file_format]
                    file_url = file_info["url"]

                    # Create a temporary directory to store the model and its dependencies
                    temp_dir = tempfile.mkdtemp()
                    main_file_path = ""

                    try:
                        # Download the main model file
                        main_file_name = file_url.split("/")[-1]
                        main_file_path = os.path.join(temp_dir, main_file_name)

                        response = requests.get(file_url, headers=REQ_HEADERS)
                        if response.status_code != 200:
                            return {"error": f"Failed to download model: {response.status_code}"}

                        with open(main_file_path, "wb") as f:
                            f.write(response.content)

                        # Check for included files and download them
                        if "include" in file_info and file_info["include"]:
                            for include_path, include_info in file_info["include"].items():
                                # Get the URL for the included file - this is the fix
                                include_url = include_info["url"]

                                # Create the directory structure for the included file
                                include_file_path = os.path.join(temp_dir, include_path)
                                os.makedirs(os.path.dirname(include_file_path), exist_ok=True)

                                # Download the included file
                                include_response = requests.get(include_url, headers=REQ_HEADERS)
                                if include_response.status_code == 200:
                                    with open(include_file_path, "wb") as f:
                                        f.write(include_response.content)
                                else:
                                    print(f"Failed to download included file: {include_path}")

                        # Import the model into Blender
                        if file_format == "gltf" or file_format == "glb":
                            bpy.ops.import_scene.gltf(filepath=main_file_path)
                        elif file_format == "fbx":
                            bpy.ops.import_scene.fbx(filepath=main_file_path)
                        elif file_format == "obj":
                            bpy.ops.import_scene.obj(filepath=main_file_path)
                        elif file_format == "blend":
                            # For blend files, we need to append or link
                            with bpy.data.libraries.load(main_file_path, link=False) as (
                                data_from,
                                data_to,
                            ):
                                data_to.objects = data_from.objects

                            # Link the objects to the scene
                            for obj in data_to.objects:
                                if obj is not None:
                                    bpy.context.collection.objects.link(obj)
                        else:
                            return {"error": f"Unsupported model format: {file_format}"}

                        # Get the names of imported objects
                        imported_objects = [obj.name for obj in bpy.context.selected_objects]

                        return {
                            "success": True,
                            "message": f"Model {asset_id} imported successfully",
                            "imported_objects": imported_objects,
                        }
                    except Exception as e:
                        return {"error": f"Failed to import model: {str(e)}"}
                    finally:
                        # Clean up temporary directory
                        with suppress(Exception):
                            shutil.rmtree(temp_dir)
                else:
                    return {"error": "Requested format or resolution not available for this model"}

            else:
                return {"error": f"Unsupported asset type: {asset_type}"}

        except Exception as e:
            return {"error": f"Failed to download asset: {str(e)}"}

    def set_texture(self, object_name, texture_id):
        """Apply a previously downloaded Polyhaven texture to an object by creating a new material"""
        try:
            # Get the object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object not found: {object_name}"}

            # Make sure object can accept materials
            if not hasattr(obj, "data") or not hasattr(obj.data, "materials"):
                return {"error": f"Object {object_name} cannot accept materials"}

            # Find all images related to this texture and ensure they're properly loaded
            texture_images = {}
            for img in bpy.data.images:
                if img.name.startswith(texture_id + "_"):
                    # Extract the map type from the image name
                    map_type = img.name.split("_")[-1].split(".")[0]

                    # Force a reload of the image
                    img.reload()

                    # Ensure proper color space
                    if map_type.lower() in ["color", "diffuse", "albedo"]:
                        try:
                            img.colorspace_settings.name = "sRGB"
                        except:
                            pass
                    else:
                        try:
                            img.colorspace_settings.name = "Non-Color"
                        except:
                            pass

                    # Ensure the image is packed
                    if not img.packed_file:
                        img.pack()

                    texture_images[map_type] = img
                    print(f"Loaded texture map: {map_type} - {img.name}")

                    # Debug info
                    print(f"Image size: {img.size[0]}x{img.size[1]}")
                    print(f"Color space: {img.colorspace_settings.name}")
                    print(f"File format: {img.file_format}")
                    print(f"Is packed: {bool(img.packed_file)}")

            if not texture_images:
                return {
                    "error": f"No texture images found for: {texture_id}. Please download the texture first."
                }

            # Create a new material
            new_mat_name = f"{texture_id}_material_{object_name}"

            # Remove any existing material with this name to avoid conflicts
            existing_mat = bpy.data.materials.get(new_mat_name)
            if existing_mat:
                bpy.data.materials.remove(existing_mat)

            new_mat = bpy.data.materials.new(name=new_mat_name)
            new_mat.use_nodes = True

            # Set up the material nodes
            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links

            # Clear default nodes
            nodes.clear()

            # Create output node
            output = nodes.new(type="ShaderNodeOutputMaterial")
            output.location = (600, 0)

            # Create principled BSDF node
            principled = nodes.new(type="ShaderNodeBsdfPrincipled")
            principled.location = (300, 0)
            links.new(principled.outputs[0], output.inputs[0])

            # Add texture nodes based on available maps
            tex_coord = nodes.new(type="ShaderNodeTexCoord")
            tex_coord.location = (-800, 0)

            mapping = nodes.new(type="ShaderNodeMapping")
            mapping.location = (-600, 0)
            mapping.vector_type = "TEXTURE"  # Changed from default 'POINT' to 'TEXTURE'
            links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])

            # Position offset for texture nodes
            x_pos = -400
            y_pos = 300

            # Connect different texture maps
            for map_type, image in texture_images.items():
                tex_node = nodes.new(type="ShaderNodeTexImage")
                tex_node.location = (x_pos, y_pos)
                tex_node.image = image

                # Set color space based on map type
                if map_type.lower() in ["color", "diffuse", "albedo"]:
                    try:
                        tex_node.image.colorspace_settings.name = "sRGB"
                    except:
                        pass  # Use default if sRGB not available
                else:
                    try:
                        tex_node.image.colorspace_settings.name = "Non-Color"
                    except:
                        pass  # Use default if Non-Color not available

                links.new(mapping.outputs["Vector"], tex_node.inputs["Vector"])

                # Connect to appropriate input on Principled BSDF
                if map_type.lower() in ["color", "diffuse", "albedo"]:
                    links.new(tex_node.outputs["Color"], principled.inputs["Base Color"])
                elif map_type.lower() in ["roughness", "rough"]:
                    links.new(tex_node.outputs["Color"], principled.inputs["Roughness"])
                elif map_type.lower() in ["metallic", "metalness", "metal"]:
                    links.new(tex_node.outputs["Color"], principled.inputs["Metallic"])
                elif map_type.lower() in ["normal", "nor", "dx", "gl"]:
                    # Add normal map node
                    normal_map = nodes.new(type="ShaderNodeNormalMap")
                    normal_map.location = (x_pos + 200, y_pos)
                    links.new(tex_node.outputs["Color"], normal_map.inputs["Color"])
                    links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
                elif map_type.lower() in ["displacement", "disp", "height"]:
                    # Add displacement node
                    disp_node = nodes.new(type="ShaderNodeDisplacement")
                    disp_node.location = (x_pos + 200, y_pos - 200)
                    disp_node.inputs["Scale"].default_value = 0.1  # Reduce displacement strength
                    links.new(tex_node.outputs["Color"], disp_node.inputs["Height"])
                    links.new(disp_node.outputs["Displacement"], output.inputs["Displacement"])

                y_pos -= 250

            # Second pass: Connect nodes with proper handling for special cases
            texture_nodes = {}

            # First find all texture nodes and store them by map type
            for node in nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    for map_type, image in texture_images.items():
                        if node.image == image:
                            texture_nodes[map_type] = node
                            break

            # Now connect everything using the nodes instead of images
            # Handle base color (diffuse)
            for map_name in ["color", "diffuse", "albedo"]:
                if map_name in texture_nodes:
                    links.new(
                        texture_nodes[map_name].outputs["Color"], principled.inputs["Base Color"]
                    )
                    print(f"Connected {map_name} to Base Color")
                    break

            # Handle roughness
            for map_name in ["roughness", "rough"]:
                if map_name in texture_nodes:
                    links.new(
                        texture_nodes[map_name].outputs["Color"], principled.inputs["Roughness"]
                    )
                    print(f"Connected {map_name} to Roughness")
                    break

            # Handle metallic
            for map_name in ["metallic", "metalness", "metal"]:
                if map_name in texture_nodes:
                    links.new(
                        texture_nodes[map_name].outputs["Color"], principled.inputs["Metallic"]
                    )
                    print(f"Connected {map_name} to Metallic")
                    break

            # Handle normal maps
            for map_name in ["gl", "dx", "nor"]:
                if map_name in texture_nodes:
                    normal_map_node = nodes.new(type="ShaderNodeNormalMap")
                    normal_map_node.location = (100, 100)
                    links.new(
                        texture_nodes[map_name].outputs["Color"], normal_map_node.inputs["Color"]
                    )
                    links.new(normal_map_node.outputs["Normal"], principled.inputs["Normal"])
                    print(f"Connected {map_name} to Normal")
                    break

            # Handle displacement
            for map_name in ["displacement", "disp", "height"]:
                if map_name in texture_nodes:
                    disp_node = nodes.new(type="ShaderNodeDisplacement")
                    disp_node.location = (300, -200)
                    disp_node.inputs["Scale"].default_value = 0.1  # Reduce displacement strength
                    links.new(texture_nodes[map_name].outputs["Color"], disp_node.inputs["Height"])
                    links.new(disp_node.outputs["Displacement"], output.inputs["Displacement"])
                    print(f"Connected {map_name} to Displacement")
                    break

            # Handle ARM texture (Ambient Occlusion, Roughness, Metallic)
            if "arm" in texture_nodes:
                separate_rgb = nodes.new(type="ShaderNodeSeparateRGB")
                separate_rgb.location = (-200, -100)
                links.new(texture_nodes["arm"].outputs["Color"], separate_rgb.inputs["Image"])

                # Connect Roughness (G) if no dedicated roughness map
                if not any(map_name in texture_nodes for map_name in ["roughness", "rough"]):
                    links.new(separate_rgb.outputs["G"], principled.inputs["Roughness"])
                    print("Connected ARM.G to Roughness")

                # Connect Metallic (B) if no dedicated metallic map
                if not any(
                    map_name in texture_nodes for map_name in ["metallic", "metalness", "metal"]
                ):
                    links.new(separate_rgb.outputs["B"], principled.inputs["Metallic"])
                    print("Connected ARM.B to Metallic")

                # For AO (R channel), multiply with base color if we have one
                base_color_node = None
                for map_name in ["color", "diffuse", "albedo"]:
                    if map_name in texture_nodes:
                        base_color_node = texture_nodes[map_name]
                        break

                if base_color_node:
                    mix_node = nodes.new(type="ShaderNodeMixRGB")
                    mix_node.location = (100, 200)
                    mix_node.blend_type = "MULTIPLY"
                    mix_node.inputs["Fac"].default_value = 0.8  # 80% influence

                    # Disconnect direct connection to base color
                    for link in base_color_node.outputs["Color"].links:
                        if link.to_socket == principled.inputs["Base Color"]:
                            links.remove(link)

                    # Connect through the mix node
                    links.new(base_color_node.outputs["Color"], mix_node.inputs[1])
                    links.new(separate_rgb.outputs["R"], mix_node.inputs[2])
                    links.new(mix_node.outputs["Color"], principled.inputs["Base Color"])
                    print("Connected ARM.R to AO mix with Base Color")

            # Handle AO (Ambient Occlusion) if separate
            if "ao" in texture_nodes:
                base_color_node = None
                for map_name in ["color", "diffuse", "albedo"]:
                    if map_name in texture_nodes:
                        base_color_node = texture_nodes[map_name]
                        break

                if base_color_node:
                    mix_node = nodes.new(type="ShaderNodeMixRGB")
                    mix_node.location = (100, 200)
                    mix_node.blend_type = "MULTIPLY"
                    mix_node.inputs["Fac"].default_value = 0.8  # 80% influence

                    # Disconnect direct connection to base color
                    for link in base_color_node.outputs["Color"].links:
                        if link.to_socket == principled.inputs["Base Color"]:
                            links.remove(link)

                    # Connect through the mix node
                    links.new(base_color_node.outputs["Color"], mix_node.inputs[1])
                    links.new(texture_nodes["ao"].outputs["Color"], mix_node.inputs[2])
                    links.new(mix_node.outputs["Color"], principled.inputs["Base Color"])
                    print("Connected AO to mix with Base Color")

            # CRITICAL: Make sure to clear all existing materials from the object
            while len(obj.data.materials) > 0:
                obj.data.materials.pop(index=0)

            # Assign the new material to the object
            obj.data.materials.append(new_mat)

            # CRITICAL: Make the object active and select it
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            # CRITICAL: Force Blender to update the material
            bpy.context.view_layer.update()

            # Get the list of texture maps
            texture_maps = list(texture_images.keys())

            # Get info about texture nodes for debugging
            material_info = {
                "name": new_mat.name,
                "has_nodes": new_mat.use_nodes,
                "node_count": len(new_mat.node_tree.nodes),
                "texture_nodes": [],
            }

            for node in new_mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    connections = []
                    for output in node.outputs:
                        for link in output.links:
                            connections.append(
                                f"{output.name} → {link.to_node.name}.{link.to_socket.name}"
                            )

                    material_info["texture_nodes"].append(
                        {
                            "name": node.name,
                            "image": node.image.name,
                            "colorspace": node.image.colorspace_settings.name,
                            "connections": connections,
                        }
                    )

            return {
                "success": True,
                "message": f"Created new material and applied texture {texture_id} to {object_name}",
                "material": new_mat.name,
                "maps": texture_maps,
                "material_info": material_info,
            }

        except Exception as e:
            print(f"Error in set_texture: {str(e)}")
            traceback.print_exc()
            return {"error": f"Failed to apply texture: {str(e)}"}

    def get_telemetry_consent(self):
        """Get the current telemetry consent status"""
        try:
            # Get addon preferences - use the module name
            addon_prefs = bpy.context.preferences.addons.get(__name__)
            if addon_prefs:
                consent = addon_prefs.preferences.telemetry_consent
            else:
                # Fallback to default if preferences not available
                consent = True
        except (AttributeError, KeyError):
            # Fallback to default if preferences not available
            consent = True
        return {"consent": consent}

    def get_polyhaven_status(self):
        """Get the current status of PolyHaven integration"""
        enabled = bpy.context.scene.blenderforge_use_polyhaven
        if enabled:
            return {
                "enabled": True,
                "message": "PolyHaven integration is enabled and ready to use.",
            }
        else:
            return {
                "enabled": False,
                "message": """PolyHaven integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                            2. Check the 'Use assets from Poly Haven' checkbox
                            3. Restart the connection to Claude""",
            }

    # region Hyper3D
    def get_hyper3d_status(self):
        """Get the current status of Hyper3D Rodin integration"""
        enabled = bpy.context.scene.blenderforge_use_hyper3d
        if enabled:
            if not bpy.context.scene.blenderforge_hyper3d_api_key:
                return {
                    "enabled": False,
                    "message": """Hyper3D Rodin integration is currently enabled, but API key is not given. To enable it:
                                1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                                2. Keep the 'Use Hyper3D Rodin 3D model generation' checkbox checked
                                3. Choose the right plaform and fill in the API Key
                                4. Restart the connection to Claude""",
                }
            mode = bpy.context.scene.blenderforge_hyper3d_mode
            api_key = bpy.context.scene.blenderforge_hyper3d_api_key
            key_type = "configured" if api_key else "not_set"
            message = (
                f"Hyper3D Rodin integration is enabled and ready to use. Mode: {mode}. "
                + f"Key type: {key_type}"
            )
            return {"enabled": True, "message": message}
        else:
            return {
                "enabled": False,
                "message": """Hyper3D Rodin integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                            2. Check the 'Use Hyper3D Rodin 3D model generation' checkbox
                            3. Restart the connection to Claude""",
            }

    def create_rodin_job(self, *args, **kwargs):
        match bpy.context.scene.blenderforge_hyper3d_mode:
            case "MAIN_SITE":
                return self.create_rodin_job_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.create_rodin_job_fal_ai(*args, **kwargs)
            case _:
                return "Error: Unknown Hyper3D Rodin mode!"

    def create_rodin_job_main_site(
        self, text_prompt: str = None, images: list[tuple[str, str]] = None, bbox_condition=None
    ):
        try:
            if images is None:
                images = []
            """Call Rodin API, get the job uuid and subscription key"""
            files = [
                *[
                    ("images", (f"{i:04d}{img_suffix}", img))
                    for i, (img_suffix, img) in enumerate(images)
                ],
                ("tier", (None, "Sketch")),
                ("mesh_mode", (None, "Raw")),
            ]
            if text_prompt:
                files.append(("prompt", (None, text_prompt)))
            if bbox_condition:
                files.append(("bbox_condition", (None, json.dumps(bbox_condition))))
            response = requests.post(
                "https://hyperhuman.deemos.com/api/v2/rodin",
                headers={
                    "Authorization": f"Bearer {bpy.context.scene.blenderforge_hyper3d_api_key}",
                },
                files=files,
            )
            data = response.json()
            return data
        except Exception as e:
            return {"error": str(e)}

    def create_rodin_job_fal_ai(
        self, text_prompt: str = None, images: list[tuple[str, str]] = None, bbox_condition=None
    ):
        try:
            req_data = {
                "tier": "Sketch",
            }
            if images:
                req_data["input_image_urls"] = images
            if text_prompt:
                req_data["prompt"] = text_prompt
            if bbox_condition:
                req_data["bbox_condition"] = bbox_condition
            response = requests.post(
                "https://queue.fal.run/fal-ai/hyper3d/rodin",
                headers={
                    "Authorization": f"Key {bpy.context.scene.blenderforge_hyper3d_api_key}",
                    "Content-Type": "application/json",
                },
                json=req_data,
            )
            data = response.json()
            return data
        except Exception as e:
            return {"error": str(e)}

    def poll_rodin_job_status(self, *args, **kwargs):
        match bpy.context.scene.blenderforge_hyper3d_mode:
            case "MAIN_SITE":
                return self.poll_rodin_job_status_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.poll_rodin_job_status_fal_ai(*args, **kwargs)
            case _:
                return "Error: Unknown Hyper3D Rodin mode!"

    def poll_rodin_job_status_main_site(self, subscription_key: str):
        """Call the job status API to get the job status"""
        response = requests.post(
            "https://hyperhuman.deemos.com/api/v2/status",
            headers={
                "Authorization": f"Bearer {bpy.context.scene.blenderforge_hyper3d_api_key}",
            },
            json={
                "subscription_key": subscription_key,
            },
        )
        data = response.json()
        return {"status_list": [i["status"] for i in data["jobs"]]}

    def poll_rodin_job_status_fal_ai(self, request_id: str):
        """Call the job status API to get the job status"""
        response = requests.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}/status",
            headers={
                "Authorization": f"KEY {bpy.context.scene.blenderforge_hyper3d_api_key}",
            },
        )
        data = response.json()
        return data

    @staticmethod
    def _clean_imported_glb(filepath, mesh_name=None):
        # Get the set of existing objects before import
        existing_objects = set(bpy.data.objects)

        # Import the GLB file
        bpy.ops.import_scene.gltf(filepath=filepath)

        # Ensure the context is updated
        bpy.context.view_layer.update()

        # Get all imported objects
        imported_objects = list(set(bpy.data.objects) - existing_objects)
        # imported_objects = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]

        if not imported_objects:
            print("Error: No objects were imported.")
            return

        # Identify the mesh object
        mesh_obj = None

        if len(imported_objects) == 1 and imported_objects[0].type == "MESH":
            mesh_obj = imported_objects[0]
            print("Single mesh imported, no cleanup needed.")
        else:
            if len(imported_objects) == 2:
                empty_objs = [i for i in imported_objects if i.type == "EMPTY"]
                if len(empty_objs) != 1:
                    print(
                        "Error: Expected an empty node with one mesh child or a single mesh object."
                    )
                    return
                parent_obj = empty_objs.pop()
                if len(parent_obj.children) == 1:
                    potential_mesh = parent_obj.children[0]
                    if potential_mesh.type == "MESH":
                        print("GLB structure confirmed: Empty node with one mesh child.")

                        # Unparent the mesh from the empty node
                        potential_mesh.parent = None

                        # Remove the empty node
                        bpy.data.objects.remove(parent_obj)
                        print("Removed empty node, keeping only the mesh.")

                        mesh_obj = potential_mesh
                    else:
                        print("Error: Child is not a mesh object.")
                        return
                else:
                    print(
                        "Error: Expected an empty node with one mesh child or a single mesh object."
                    )
                    return
            else:
                print("Error: Expected an empty node with one mesh child or a single mesh object.")
                return

        # Rename the mesh if needed
        try:
            if mesh_obj and mesh_obj.name is not None and mesh_name:
                mesh_obj.name = mesh_name
                if mesh_obj.data.name is not None:
                    mesh_obj.data.name = mesh_name
                print(f"Mesh renamed to: {mesh_name}")
        except Exception:
            print("Having issue with renaming, give up renaming.")

        return mesh_obj

    def import_generated_asset(self, *args, **kwargs):
        match bpy.context.scene.blenderforge_hyper3d_mode:
            case "MAIN_SITE":
                return self.import_generated_asset_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.import_generated_asset_fal_ai(*args, **kwargs)
            case _:
                return "Error: Unknown Hyper3D Rodin mode!"

    def import_generated_asset_main_site(self, task_uuid: str, name: str):
        """Fetch the generated asset, import into blender"""
        response = requests.post(
            "https://hyperhuman.deemos.com/api/v2/download",
            headers={
                "Authorization": f"Bearer {bpy.context.scene.blenderforge_hyper3d_api_key}",
            },
            json={"task_uuid": task_uuid},
        )
        data_ = response.json()
        temp_file = None
        for i in data_["list"]:
            if i["name"].endswith(".glb"):
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    prefix=task_uuid,
                    suffix=".glb",
                )

                try:
                    # Download the content
                    response = requests.get(i["url"], stream=True)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Write the content to the temporary file
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)

                    # Close the file
                    temp_file.close()

                except Exception as e:
                    # Clean up the file if there's an error
                    temp_file.close()
                    os.unlink(temp_file.name)
                    return {"succeed": False, "error": str(e)}

                break
        else:
            return {
                "succeed": False,
                "error": "Generation failed. Please first make sure that all jobs of the task are done and then try again later.",
            }

        try:
            obj = self._clean_imported_glb(filepath=temp_file.name, mesh_name=name)
            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {"succeed": True, **result}
        except Exception as e:
            return {"succeed": False, "error": str(e)}

    def import_generated_asset_fal_ai(self, request_id: str, name: str):
        """Fetch the generated asset, import into blender"""
        response = requests.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}",
            headers={
                "Authorization": f"Key {bpy.context.scene.blenderforge_hyper3d_api_key}",
            },
        )
        data_ = response.json()
        temp_file = None

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix=request_id,
            suffix=".glb",
        )

        try:
            # Download the content
            response = requests.get(data_["model_mesh"]["url"], stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Write the content to the temporary file
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)

            # Close the file
            temp_file.close()

        except Exception as e:
            # Clean up the file if there's an error
            temp_file.close()
            os.unlink(temp_file.name)
            return {"succeed": False, "error": str(e)}

        try:
            obj = self._clean_imported_glb(filepath=temp_file.name, mesh_name=name)
            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {"succeed": True, **result}
        except Exception as e:
            return {"succeed": False, "error": str(e)}

    # endregion

    # region Sketchfab API
    def get_sketchfab_status(self):
        """Get the current status of Sketchfab integration"""
        enabled = bpy.context.scene.blenderforge_use_sketchfab
        api_key = bpy.context.scene.blenderforge_sketchfab_api_key

        # Test the API key if present
        if api_key:
            try:
                headers = {"Authorization": f"Token {api_key}"}

                response = requests.get(
                    "https://api.sketchfab.com/v3/me",
                    headers=headers,
                    timeout=30,  # Add timeout of 30 seconds
                )

                if response.status_code == 200:
                    user_data = response.json()
                    username = user_data.get("username", "Unknown user")
                    return {
                        "enabled": True,
                        "message": f"Sketchfab integration is enabled and ready to use. Logged in as: {username}",
                    }
                else:
                    return {
                        "enabled": False,
                        "message": f"Sketchfab API key seems invalid. Status code: {response.status_code}",
                    }
            except requests.exceptions.Timeout:
                return {
                    "enabled": False,
                    "message": "Timeout connecting to Sketchfab API. Check your internet connection.",
                }
            except Exception as e:
                return {"enabled": False, "message": f"Error testing Sketchfab API key: {str(e)}"}

        if enabled and api_key:
            return {
                "enabled": True,
                "message": "Sketchfab integration is enabled and ready to use.",
            }
        elif enabled and not api_key:
            return {
                "enabled": False,
                "message": """Sketchfab integration is currently enabled, but API key is not given. To enable it:
                            1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                            2. Keep the 'Use Sketchfab' checkbox checked
                            3. Enter your Sketchfab API Key
                            4. Restart the connection to Claude""",
            }
        else:
            return {
                "enabled": False,
                "message": """Sketchfab integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                            2. Check the 'Use assets from Sketchfab' checkbox
                            3. Enter your Sketchfab API Key
                            4. Restart the connection to Claude""",
            }

    def search_sketchfab_models(self, query, categories=None, count=20, downloadable=True):
        """Search for models on Sketchfab based on query and optional filters"""
        try:
            api_key = bpy.context.scene.blenderforge_sketchfab_api_key
            if not api_key:
                return {"error": "Sketchfab API key is not configured"}

            # Build search parameters with exact fields from Sketchfab API docs
            params = {
                "type": "models",
                "q": query,
                "count": count,
                "downloadable": downloadable,
                "archives_flavours": False,
            }

            if categories:
                params["categories"] = categories

            # Make API request to Sketchfab search endpoint
            # The proper format according to Sketchfab API docs for API key auth
            headers = {"Authorization": f"Token {api_key}"}

            # Use the search endpoint as specified in the API documentation
            response = requests.get(
                "https://api.sketchfab.com/v3/search",
                headers=headers,
                params=params,
                timeout=30,  # Add timeout of 30 seconds
            )

            if response.status_code == 401:
                return {"error": "Authentication failed (401). Check your API key."}

            if response.status_code != 200:
                return {"error": f"API request failed with status code {response.status_code}"}

            response_data = response.json()

            # Safety check on the response structure
            if response_data is None:
                return {"error": "Received empty response from Sketchfab API"}

            # Handle 'results' potentially missing from response
            results = response_data.get("results", [])
            if not isinstance(results, list):
                return {"error": f"Unexpected response format from Sketchfab API: {response_data}"}

            return response_data

        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Check your internet connection."}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response from Sketchfab API: {str(e)}"}
        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def get_sketchfab_model_preview(self, uid):
        """Get thumbnail preview image of a Sketchfab model by its UID"""
        try:
            import base64

            api_key = bpy.context.scene.blenderforge_sketchfab_api_key
            if not api_key:
                return {"error": "Sketchfab API key is not configured"}

            headers = {"Authorization": f"Token {api_key}"}

            # Get model info which includes thumbnails
            response = requests.get(
                f"https://api.sketchfab.com/v3/models/{uid}", headers=headers, timeout=30
            )

            if response.status_code == 401:
                return {"error": "Authentication failed (401). Check your API key."}

            if response.status_code == 404:
                return {"error": f"Model not found: {uid}"}

            if response.status_code != 200:
                return {"error": f"Failed to get model info: {response.status_code}"}

            data = response.json()
            thumbnails = data.get("thumbnails", {}).get("images", [])

            if not thumbnails:
                return {"error": "No thumbnail available for this model"}

            # Find a suitable thumbnail (prefer medium size ~640px)
            selected_thumbnail = None
            for thumb in thumbnails:
                width = thumb.get("width", 0)
                if 400 <= width <= 800:
                    selected_thumbnail = thumb
                    break

            # Fallback to the first available thumbnail
            if not selected_thumbnail:
                selected_thumbnail = thumbnails[0]

            thumbnail_url = selected_thumbnail.get("url")
            if not thumbnail_url:
                return {"error": "Thumbnail URL not found"}

            # Download the thumbnail image
            img_response = requests.get(thumbnail_url, timeout=30)
            if img_response.status_code != 200:
                return {"error": f"Failed to download thumbnail: {img_response.status_code}"}

            # Encode image as base64
            image_data = base64.b64encode(img_response.content).decode("ascii")

            # Determine format from content type or URL
            content_type = img_response.headers.get("Content-Type", "")
            if "png" in content_type or thumbnail_url.endswith(".png"):
                img_format = "png"
            else:
                img_format = "jpeg"

            # Get additional model info for context
            model_name = data.get("name", "Unknown")
            author = data.get("user", {}).get("username", "Unknown")

            return {
                "success": True,
                "image_data": image_data,
                "format": img_format,
                "model_name": model_name,
                "author": author,
                "uid": uid,
                "thumbnail_width": selected_thumbnail.get("width"),
                "thumbnail_height": selected_thumbnail.get("height"),
            }

        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Check your internet connection."}
        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"error": f"Failed to get model preview: {str(e)}"}

    def download_sketchfab_model(self, uid, normalize_size=False, target_size=1.0):
        """Download a model from Sketchfab by its UID

        Parameters:
        - uid: The unique identifier of the Sketchfab model
        - normalize_size: If True, scale the model so its largest dimension equals target_size
        - target_size: The target size in Blender units (meters) for the largest dimension
        """
        try:
            api_key = bpy.context.scene.blenderforge_sketchfab_api_key
            if not api_key:
                return {"error": "Sketchfab API key is not configured"}

            # Use proper authorization header for API key auth
            headers = {"Authorization": f"Token {api_key}"}

            # Request download URL using the exact endpoint from the documentation
            download_endpoint = f"https://api.sketchfab.com/v3/models/{uid}/download"

            response = requests.get(
                download_endpoint,
                headers=headers,
                timeout=30,  # Add timeout of 30 seconds
            )

            if response.status_code == 401:
                return {"error": "Authentication failed (401). Check your API key."}

            if response.status_code != 200:
                return {"error": f"Download request failed with status code {response.status_code}"}

            data = response.json()

            # Safety check for None data
            if data is None:
                return {"error": "Received empty response from Sketchfab API for download request"}

            # Extract download URL with safety checks
            gltf_data = data.get("gltf")
            if not gltf_data:
                return {
                    "error": "No gltf download URL available for this model. Response: " + str(data)
                }

            download_url = gltf_data.get("url")
            if not download_url:
                return {
                    "error": "No download URL available for this model. Make sure the model is downloadable and you have access."
                }

            # Download the model (already has timeout)
            model_response = requests.get(download_url, timeout=60)  # 60 second timeout

            if model_response.status_code != 200:
                return {
                    "error": f"Model download failed with status code {model_response.status_code}"
                }

            # Save to temporary file
            temp_dir = tempfile.mkdtemp()
            zip_file_path = os.path.join(temp_dir, f"{uid}.zip")

            with open(zip_file_path, "wb") as f:
                f.write(model_response.content)

            # Extract the zip file with enhanced security
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                # More secure zip slip prevention
                for file_info in zip_ref.infolist():
                    # Get the path of the file
                    file_path = file_info.filename

                    # Convert directory separators to the current OS style
                    # This handles both / and \ in zip entries
                    target_path = os.path.join(temp_dir, os.path.normpath(file_path))

                    # Get absolute paths for comparison
                    abs_temp_dir = os.path.abspath(temp_dir)
                    abs_target_path = os.path.abspath(target_path)

                    # Ensure the normalized path doesn't escape the target directory
                    if not abs_target_path.startswith(abs_temp_dir):
                        with suppress(Exception):
                            shutil.rmtree(temp_dir)
                        return {
                            "error": "Security issue: Zip contains files with path traversal attempt"
                        }

                    # Additional explicit check for directory traversal
                    if ".." in file_path:
                        with suppress(Exception):
                            shutil.rmtree(temp_dir)
                        return {
                            "error": "Security issue: Zip contains files with directory traversal sequence"
                        }

                # If all files passed security checks, extract them
                zip_ref.extractall(temp_dir)

            # Find the main glTF file
            gltf_files = [
                f for f in os.listdir(temp_dir) if f.endswith(".gltf") or f.endswith(".glb")
            ]

            if not gltf_files:
                with suppress(Exception):
                    shutil.rmtree(temp_dir)
                return {"error": "No glTF file found in the downloaded model"}

            main_file = os.path.join(temp_dir, gltf_files[0])

            # Import the model
            bpy.ops.import_scene.gltf(filepath=main_file)

            # Get the imported objects
            imported_objects = list(bpy.context.selected_objects)
            imported_object_names = [obj.name for obj in imported_objects]

            # Clean up temporary files
            with suppress(Exception):
                shutil.rmtree(temp_dir)

            # Find root objects (objects without parents in the imported set)
            root_objects = [obj for obj in imported_objects if obj.parent is None]

            # Helper function to recursively get all mesh children
            def get_all_mesh_children(obj):
                """Recursively collect all mesh objects in the hierarchy"""
                meshes = []
                if obj.type == "MESH":
                    meshes.append(obj)
                for child in obj.children:
                    meshes.extend(get_all_mesh_children(child))
                return meshes

            # Collect ALL meshes from the entire hierarchy (starting from roots)
            all_meshes = []
            for obj in root_objects:
                all_meshes.extend(get_all_mesh_children(obj))

            if all_meshes:
                # Calculate combined world bounding box for all meshes
                all_min = mathutils.Vector((float("inf"), float("inf"), float("inf")))
                all_max = mathutils.Vector((float("-inf"), float("-inf"), float("-inf")))

                for mesh_obj in all_meshes:
                    # Get world-space bounding box corners
                    for corner in mesh_obj.bound_box:
                        world_corner = mesh_obj.matrix_world @ mathutils.Vector(corner)
                        all_min.x = min(all_min.x, world_corner.x)
                        all_min.y = min(all_min.y, world_corner.y)
                        all_min.z = min(all_min.z, world_corner.z)
                        all_max.x = max(all_max.x, world_corner.x)
                        all_max.y = max(all_max.y, world_corner.y)
                        all_max.z = max(all_max.z, world_corner.z)

                # Calculate dimensions
                dimensions = [all_max.x - all_min.x, all_max.y - all_min.y, all_max.z - all_min.z]
                max_dimension = max(dimensions)

                # Apply normalization if requested
                scale_applied = 1.0
                if normalize_size and max_dimension > 0:
                    scale_factor = target_size / max_dimension
                    scale_applied = scale_factor

                    # ✅ Only apply scale to ROOT objects (not children!)
                    # Child objects inherit parent's scale through matrix_world
                    for root in root_objects:
                        root.scale = (
                            root.scale.x * scale_factor,
                            root.scale.y * scale_factor,
                            root.scale.z * scale_factor,
                        )

                    # Update the scene to recalculate matrix_world for all objects
                    bpy.context.view_layer.update()

                    # Recalculate bounding box after scaling
                    all_min = mathutils.Vector((float("inf"), float("inf"), float("inf")))
                    all_max = mathutils.Vector((float("-inf"), float("-inf"), float("-inf")))

                    for mesh_obj in all_meshes:
                        for corner in mesh_obj.bound_box:
                            world_corner = mesh_obj.matrix_world @ mathutils.Vector(corner)
                            all_min.x = min(all_min.x, world_corner.x)
                            all_min.y = min(all_min.y, world_corner.y)
                            all_min.z = min(all_min.z, world_corner.z)
                            all_max.x = max(all_max.x, world_corner.x)
                            all_max.y = max(all_max.y, world_corner.y)
                            all_max.z = max(all_max.z, world_corner.z)

                    dimensions = [
                        all_max.x - all_min.x,
                        all_max.y - all_min.y,
                        all_max.z - all_min.z,
                    ]

                world_bounding_box = [
                    [all_min.x, all_min.y, all_min.z],
                    [all_max.x, all_max.y, all_max.z],
                ]
            else:
                world_bounding_box = None
                dimensions = None
                scale_applied = 1.0

            result = {
                "success": True,
                "message": "Model imported successfully",
                "imported_objects": imported_object_names,
            }

            if world_bounding_box:
                result["world_bounding_box"] = world_bounding_box
            if dimensions:
                result["dimensions"] = [round(d, 4) for d in dimensions]
            if normalize_size:
                result["scale_applied"] = round(scale_applied, 6)
                result["normalized"] = True

            return result

        except requests.exceptions.Timeout:
            return {
                "error": "Request timed out. Check your internet connection and try again with a simpler model."
            }
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response from Sketchfab API: {str(e)}"}
        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"error": f"Failed to download model: {str(e)}"}

    # endregion

    # region Hunyuan3D
    def get_hunyuan3d_status(self):
        """Get the current status of Hunyuan3D integration"""
        enabled = bpy.context.scene.blenderforge_use_hunyuan3d
        hunyuan3d_mode = bpy.context.scene.blenderforge_hunyuan3d_mode
        if enabled:
            match hunyuan3d_mode:
                case "OFFICIAL_API":
                    if (
                        not bpy.context.scene.blenderforge_hunyuan3d_secret_id
                        or not bpy.context.scene.blenderforge_hunyuan3d_secret_key
                    ):
                        return {
                            "enabled": False,
                            "mode": hunyuan3d_mode,
                            "message": """Hunyuan3D integration is currently enabled, but SecretId or SecretKey is not given. To enable it:
                                1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                                2. Keep the 'Use Tencent Hunyuan 3D model generation' checkbox checked
                                3. Choose the right platform and fill in the SecretId and SecretKey
                                4. Restart the connection to Claude""",
                        }
                case "LOCAL_API":
                    if not bpy.context.scene.blenderforge_hunyuan3d_api_url:
                        return {
                            "enabled": False,
                            "mode": hunyuan3d_mode,
                            "message": """Hunyuan3D integration is currently enabled, but API URL  is not given. To enable it:
                                1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                                2. Keep the 'Use Tencent Hunyuan 3D model generation' checkbox checked
                                3. Choose the right platform and fill in the API URL
                                4. Restart the connection to Claude""",
                        }
                case _:
                    return {
                        "enabled": False,
                        "message": "Hunyuan3D integration is enabled and mode is not supported.",
                    }
            return {
                "enabled": True,
                "mode": hunyuan3d_mode,
                "message": "Hunyuan3D integration is enabled and ready to use.",
            }
        return {
            "enabled": False,
            "message": """Hunyuan3D integration is currently disabled. To enable it:
                        1. In the 3D Viewport, find the BlenderForge panel in the sidebar (press N if hidden)
                        2. Check the 'Use Tencent Hunyuan 3D model generation' checkbox
                        3. Restart the connection to Claude""",
        }

    @staticmethod
    def get_tencent_cloud_sign_headers(
        method: str,
        path: str,
        headParams: dict,
        data: dict,
        service: str,
        region: str,
        secret_id: str,
        secret_key: str,
        host: str = None,
    ):
        """Generate the signature header required for Tencent Cloud API requests headers"""
        # Generate timestamp
        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        # If host is not provided, it is generated based on service and region.
        if not host:
            host = f"{service}.tencentcloudapi.com"

        endpoint = f"https://{host}"

        # Constructing the request body
        payload_str = json.dumps(data)

        # ************* Step 1: Concatenate the canonical request string *************
        canonical_uri = path
        canonical_querystring = ""
        ct = "application/json; charset=utf-8"
        canonical_headers = (
            f"content-type:{ct}\nhost:{host}\nx-tc-action:{headParams.get('Action', '').lower()}\n"
        )
        signed_headers = "content-type;host;x-tc-action"
        hashed_request_payload = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        canonical_request = (
            method
            + "\n"
            + canonical_uri
            + "\n"
            + canonical_querystring
            + "\n"
            + canonical_headers
            + "\n"
            + signed_headers
            + "\n"
            + hashed_request_payload
        )

        # ************* Step 2: Construct the reception signature string *************
        credential_scope = f"{date}/{service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = (
            "TC3-HMAC-SHA256"
            + "\n"
            + str(timestamp)
            + "\n"
            + credential_scope
            + "\n"
            + hashed_canonical_request
        )

        # ************* Step 3: Calculate the signature *************
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
        secret_service = sign(secret_date, service)
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(
            secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # ************* Step 4: Connect Authorization *************
        authorization = (
            "TC3-HMAC-SHA256"
            + " "
            + "Credential="
            + secret_id
            + "/"
            + credential_scope
            + ", "
            + "SignedHeaders="
            + signed_headers
            + ", "
            + "Signature="
            + signature
        )

        # Constructing request headers
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json; charset=utf-8",
            "Host": host,
            "X-TC-Action": headParams.get("Action", ""),
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": headParams.get("Version", ""),
            "X-TC-Region": region,
        }

        return headers, endpoint

    def create_hunyuan_job(self, *args, **kwargs):
        match bpy.context.scene.blenderforge_hunyuan3d_mode:
            case "OFFICIAL_API":
                return self.create_hunyuan_job_main_site(*args, **kwargs)
            case "LOCAL_API":
                return self.create_hunyuan_job_local_site(*args, **kwargs)
            case _:
                return "Error: Unknown Hunyuan3D mode!"

    def create_hunyuan_job_main_site(self, text_prompt: str = None, image: str = None):
        try:
            secret_id = bpy.context.scene.blenderforge_hunyuan3d_secret_id
            secret_key = bpy.context.scene.blenderforge_hunyuan3d_secret_key

            if not secret_id or not secret_key:
                return {"error": "SecretId or SecretKey is not given"}

            # Parameter verification
            if not text_prompt and not image:
                return {"error": "Prompt or Image is required"}
            if text_prompt and image:
                return {"error": "Prompt and Image cannot be provided simultaneously"}
            # Fixed parameter configuration
            service = "hunyuan"
            action = "SubmitHunyuanTo3DJob"
            version = "2023-09-01"
            region = "ap-guangzhou"

            headParams = {
                "Action": action,
                "Version": version,
                "Region": region,
            }

            # Constructing request parameters
            data = {
                "Num": 1  # The current API limit is only 1
            }

            # Handling text prompts
            if text_prompt:
                if len(text_prompt) > 200:
                    return {"error": "Prompt exceeds 200 characters limit"}
                data["Prompt"] = text_prompt

            # Handling image
            if image:
                if re.match(r"^https?://", image, re.IGNORECASE) is not None:
                    data["ImageUrl"] = image
                else:
                    try:
                        # Convert to Base64 format
                        with open(image, "rb") as f:
                            image_base64 = base64.b64encode(f.read()).decode("ascii")
                        data["ImageBase64"] = image_base64
                    except Exception as e:
                        return {"error": f"Image encoding failed: {str(e)}"}

            # Get signed headers
            headers, endpoint = self.get_tencent_cloud_sign_headers(
                "POST", "/", headParams, data, service, region, secret_id, secret_key
            )

            response = requests.post(endpoint, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                return response.json()
            return {"error": f"API request failed with status {response.status_code}: {response}"}
        except Exception as e:
            return {"error": str(e)}

    def create_hunyuan_job_local_site(self, text_prompt: str = None, image: str = None):
        try:
            base_url = bpy.context.scene.blenderforge_hunyuan3d_api_url.rstrip("/")
            octree_resolution = bpy.context.scene.blenderforge_hunyuan3d_octree_resolution
            num_inference_steps = bpy.context.scene.blenderforge_hunyuan3d_num_inference_steps
            guidance_scale = bpy.context.scene.blenderforge_hunyuan3d_guidance_scale
            texture = bpy.context.scene.blenderforge_hunyuan3d_texture

            if not base_url:
                return {"error": "API URL is not given"}
            # Parameter verification
            if not text_prompt and not image:
                return {"error": "Prompt or Image is required"}

            # Constructing request parameters
            data = {
                "octree_resolution": octree_resolution,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "texture": texture,
            }

            # Handling text prompts
            if text_prompt:
                data["text"] = text_prompt

            # Handling image
            if image:
                if re.match(r"^https?://", image, re.IGNORECASE) is not None:
                    try:
                        resImg = requests.get(image)
                        resImg.raise_for_status()
                        image_base64 = base64.b64encode(resImg.content).decode("ascii")
                        data["image"] = image_base64
                    except Exception as e:
                        return {"error": f"Failed to download or encode image: {str(e)}"}
                else:
                    try:
                        # Convert to Base64 format
                        with open(image, "rb") as f:
                            image_base64 = base64.b64encode(f.read()).decode("ascii")
                        data["image"] = image_base64
                    except Exception as e:
                        return {"error": f"Image encoding failed: {str(e)}"}

            response = requests.post(
                f"{base_url}/generate",
                json=data,
            )

            if response.status_code != 200:
                return {"error": f"Generation failed: {response.text}"}

            # Decode base64 and save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as temp_file:
                temp_file.write(response.content)
                temp_file_name = temp_file.name

            # Import the GLB file in the main thread
            def import_handler():
                bpy.ops.import_scene.gltf(filepath=temp_file_name)
                os.unlink(temp_file.name)
                return None

            bpy.app.timers.register(import_handler)

            return {"status": "DONE", "message": "Generation and Import glb succeeded"}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": str(e)}

    def poll_hunyuan_job_status(self, *args, **kwargs):
        return self.poll_hunyuan_job_status_ai(*args, **kwargs)

    def poll_hunyuan_job_status_ai(self, job_id: str):
        """Call the job status API to get the job status"""
        print(job_id)
        try:
            secret_id = bpy.context.scene.blenderforge_hunyuan3d_secret_id
            secret_key = bpy.context.scene.blenderforge_hunyuan3d_secret_key

            if not secret_id or not secret_key:
                return {"error": "SecretId or SecretKey is not given"}
            if not job_id:
                return {"error": "JobId is required"}

            service = "hunyuan"
            action = "QueryHunyuanTo3DJob"
            version = "2023-09-01"
            region = "ap-guangzhou"

            headParams = {
                "Action": action,
                "Version": version,
                "Region": region,
            }

            clean_job_id = job_id.removeprefix("job_")
            data = {"JobId": clean_job_id}

            headers, endpoint = self.get_tencent_cloud_sign_headers(
                "POST", "/", headParams, data, service, region, secret_id, secret_key
            )

            response = requests.post(endpoint, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                return response.json()
            return {"error": f"API request failed with status {response.status_code}: {response}"}
        except Exception as e:
            return {"error": str(e)}

    def import_generated_asset_hunyuan(self, *args, **kwargs):
        return self.import_generated_asset_hunyuan_ai(*args, **kwargs)

    def import_generated_asset_hunyuan_ai(self, name: str, zip_file_url: str):
        if not zip_file_url:
            return {"error": "Zip file not found"}

        # Validate URL
        if not re.match(r"^https?://", zip_file_url, re.IGNORECASE):
            return {"error": "Invalid URL format. Must start with http:// or https://"}

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="tencent_obj_")
        zip_file_path = osp.join(temp_dir, "model.zip")
        obj_file_path = osp.join(temp_dir, "model.obj")
        mtl_file_path = osp.join(temp_dir, "model.mtl")

        try:
            # Download ZIP file
            zip_response = requests.get(zip_file_url, stream=True)
            zip_response.raise_for_status()
            with open(zip_file_path, "wb") as f:
                for chunk in zip_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Unzip the ZIP
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the .obj file (there may be multiple, assuming the main file is model.obj)
            for file in os.listdir(temp_dir):
                if file.endswith(".obj"):
                    obj_file_path = osp.join(temp_dir, file)

            if not osp.exists(obj_file_path):
                return {"succeed": False, "error": "OBJ file not found after extraction"}

            # Import obj file
            if bpy.app.version >= (4, 0, 0):
                bpy.ops.wm.obj_import(filepath=obj_file_path)
            else:
                bpy.ops.import_scene.obj(filepath=obj_file_path)

            imported_objs = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
            if not imported_objs:
                return {"succeed": False, "error": "No mesh objects imported"}

            obj = imported_objs[0]
            if name:
                obj.name = name

            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {"succeed": True, **result}
        except Exception as e:
            return {"succeed": False, "error": str(e)}
        finally:
            #  Clean up temporary zip and obj, save texture and mtl
            try:
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)
                if os.path.exists(obj_file_path):
                    os.remove(obj_file_path)
            except Exception as e:
                print(f"Failed to clean up temporary directory {temp_dir}: {e}")

    # endregion

    # ==========================================================================
    # AI-POWERED FEATURES
    # ==========================================================================

    # region Material Generator

    # Material keyword mappings for AI material generation
    MATERIAL_KEYWORDS = {
        # Surface types
        "metal": {"metallic": 0.9, "roughness": 0.4},
        "metallic": {"metallic": 0.95, "roughness": 0.3},
        "plastic": {"metallic": 0.0, "roughness": 0.4, "specular": 0.5},
        "glass": {"metallic": 0.0, "roughness": 0.0, "transmission": 1.0, "ior": 1.45},
        "wood": {"metallic": 0.0, "roughness": 0.6},
        "stone": {"metallic": 0.0, "roughness": 0.8},
        "concrete": {"metallic": 0.0, "roughness": 0.9},
        "fabric": {"metallic": 0.0, "roughness": 0.9, "sheen": 0.5},
        "leather": {"metallic": 0.0, "roughness": 0.5, "sheen": 0.3},
        "rubber": {"metallic": 0.0, "roughness": 0.8, "specular": 0.2},
        "ceramic": {"metallic": 0.0, "roughness": 0.2, "specular": 0.8},
        "porcelain": {"metallic": 0.0, "roughness": 0.1, "specular": 0.9},
        # Surface qualities
        "shiny": {"roughness": 0.1},
        "glossy": {"roughness": 0.15},
        "polished": {"roughness": 0.05},
        "matte": {"roughness": 0.9},
        "rough": {"roughness": 0.85},
        "smooth": {"roughness": 0.2},
        "brushed": {"roughness": 0.4, "anisotropic": 0.5},
        "satin": {"roughness": 0.3},
        "frosted": {"roughness": 0.6, "transmission": 0.8},
        # Conditions
        "rusty": {"roughness": 0.9, "metallic": 0.7},
        "weathered": {"roughness": 0.8},
        "worn": {"roughness": 0.7},
        "new": {"roughness": 0.3},
        "aged": {"roughness": 0.75},
        "scratched": {"roughness": 0.6},
        "dirty": {"roughness": 0.85},
        "clean": {"roughness": 0.3},
        # Special
        "emissive": {"emission_strength": 5.0},
        "glowing": {"emission_strength": 10.0},
        "transparent": {"transmission": 0.9},
        "translucent": {"transmission": 0.5, "roughness": 0.3},
    }

    COLOR_KEYWORDS = {
        "red": (1.0, 0.0, 0.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
        "yellow": (1.0, 1.0, 0.0, 1.0),
        "orange": (1.0, 0.5, 0.0, 1.0),
        "purple": (0.5, 0.0, 0.5, 1.0),
        "pink": (1.0, 0.75, 0.8, 1.0),
        "cyan": (0.0, 1.0, 1.0, 1.0),
        "magenta": (1.0, 0.0, 1.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0, 1.0),
        "gray": (0.5, 0.5, 0.5, 1.0),
        "grey": (0.5, 0.5, 0.5, 1.0),
        "brown": (0.4, 0.2, 0.0, 1.0),
        "beige": (0.96, 0.96, 0.86, 1.0),
        "tan": (0.82, 0.71, 0.55, 1.0),
        "gold": (1.0, 0.84, 0.0, 1.0),
        "silver": (0.75, 0.75, 0.75, 1.0),
        "bronze": (0.8, 0.5, 0.2, 1.0),
        "copper": (0.72, 0.45, 0.2, 1.0),
        "brass": (0.71, 0.65, 0.26, 1.0),
        "chrome": (0.55, 0.55, 0.55, 1.0),
        "steel": (0.45, 0.45, 0.5, 1.0),
        "iron": (0.3, 0.3, 0.35, 1.0),
        "ivory": (1.0, 1.0, 0.94, 1.0),
        "cream": (1.0, 0.99, 0.82, 1.0),
        "navy": (0.0, 0.0, 0.5, 1.0),
        "teal": (0.0, 0.5, 0.5, 1.0),
        "olive": (0.5, 0.5, 0.0, 1.0),
        "maroon": (0.5, 0.0, 0.0, 1.0),
    }

    MATERIAL_PRESETS = {
        "metal": [
            {"name": "Polished Steel", "desc": "Clean, reflective steel surface"},
            {"name": "Brushed Aluminum", "desc": "Anisotropic brushed metal"},
            {"name": "Rusty Iron", "desc": "Weathered, oxidized iron"},
            {"name": "Gold", "desc": "Shiny gold metal"},
            {"name": "Copper", "desc": "Warm copper with patina"},
        ],
        "wood": [
            {"name": "Oak", "desc": "Light oak wood grain"},
            {"name": "Walnut", "desc": "Dark walnut wood"},
            {"name": "Pine", "desc": "Light pine with knots"},
            {"name": "Mahogany", "desc": "Rich reddish-brown wood"},
        ],
        "stone": [
            {"name": "Marble", "desc": "Polished white marble"},
            {"name": "Granite", "desc": "Speckled granite surface"},
            {"name": "Slate", "desc": "Dark layered slate"},
            {"name": "Sandstone", "desc": "Rough sandstone"},
        ],
        "fabric": [
            {"name": "Cotton", "desc": "Soft cotton fabric"},
            {"name": "Silk", "desc": "Shiny silk material"},
            {"name": "Velvet", "desc": "Soft velvet with sheen"},
            {"name": "Denim", "desc": "Blue denim fabric"},
        ],
        "glass": [
            {"name": "Clear Glass", "desc": "Transparent glass"},
            {"name": "Frosted Glass", "desc": "Translucent frosted"},
            {"name": "Tinted Glass", "desc": "Colored glass"},
        ],
        "plastic": [
            {"name": "Glossy Plastic", "desc": "Shiny plastic surface"},
            {"name": "Matte Plastic", "desc": "Non-reflective plastic"},
            {"name": "Rubber", "desc": "Soft rubber material"},
        ],
        "organic": [
            {"name": "Skin", "desc": "Human skin with SSS"},
            {"name": "Leaves", "desc": "Green leaf material"},
            {"name": "Bark", "desc": "Tree bark texture"},
        ],
    }

    def generate_material_text(self, description, name="AI_Material"):
        """Generate a PBR material from text description"""
        try:
            description_lower = description.lower()

            # Create new material
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            # Get principled BSDF node
            principled = nodes.get("Principled BSDF")
            if not principled:
                principled = nodes.new("ShaderNodeBsdfPrincipled")

            # Default values
            base_color = (0.8, 0.8, 0.8, 1.0)
            metallic = 0.0
            roughness = 0.5
            specular = 0.5
            transmission = 0.0
            emission_strength = 0.0
            ior = 1.45

            # Parse color from description
            for color_name, color_value in self.COLOR_KEYWORDS.items():
                if color_name in description_lower:
                    base_color = color_value
                    break

            # Parse material properties from keywords
            for keyword, properties in self.MATERIAL_KEYWORDS.items():
                if keyword in description_lower:
                    metallic = properties.get("metallic", metallic)
                    roughness = properties.get("roughness", roughness)
                    specular = properties.get("specular", specular)
                    transmission = properties.get("transmission", transmission)
                    emission_strength = properties.get("emission_strength", emission_strength)
                    ior = properties.get("ior", ior)

            # Apply properties to principled BSDF
            principled.inputs["Base Color"].default_value = base_color
            principled.inputs["Metallic"].default_value = metallic
            principled.inputs["Roughness"].default_value = roughness
            if "IOR" in principled.inputs:
                principled.inputs["IOR"].default_value = ior
            if "Transmission" in principled.inputs:
                principled.inputs["Transmission"].default_value = transmission
            if transmission > 0:
                mat.blend_method = 'HASHED'
            if emission_strength > 0:
                principled.inputs["Emission Strength"].default_value = emission_strength
                principled.inputs["Emission Color"].default_value = base_color

            return {
                "material_name": mat.name,
                "base_color": list(base_color),
                "metallic": metallic,
                "roughness": roughness,
                "transmission": transmission,
                "keywords_detected": [k for k in self.MATERIAL_KEYWORDS.keys() if k in description_lower],
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_material_image(self, image_data, name="AI_Material", image_path=None):
        """Generate material from image analysis"""
        try:
            # Decode image and save temporarily
            temp_path = image_path or tempfile.mktemp(suffix=".png")
            if not image_path:
                img_bytes = base64.b64decode(image_data)
                with open(temp_path, "wb") as f:
                    f.write(img_bytes)

            # Load image in Blender
            img = bpy.data.images.load(temp_path)

            # Analyze dominant color (simple average)
            pixels = list(img.pixels)
            r = sum(pixels[0::4]) / (len(pixels) // 4)
            g = sum(pixels[1::4]) / (len(pixels) // 4)
            b = sum(pixels[2::4]) / (len(pixels) // 4)

            # Estimate roughness from color variance
            variance = sum((pixels[i] - r) ** 2 for i in range(0, len(pixels), 4)) / (len(pixels) // 4)
            estimated_roughness = min(0.9, max(0.1, variance * 10))

            # Create material
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            principled = nodes.get("Principled BSDF")
            output = nodes.get("Material Output")

            # Add image texture
            tex_node = nodes.new("ShaderNodeTexImage")
            tex_node.image = img
            tex_node.location = (-300, 300)

            # Connect texture to base color
            links.new(tex_node.outputs["Color"], principled.inputs["Base Color"])
            principled.inputs["Roughness"].default_value = estimated_roughness

            return {
                "material_name": mat.name,
                "dominant_color": [r, g, b],
                "estimated_roughness": estimated_roughness,
                "image_loaded": img.name,
            }
        except Exception as e:
            return {"error": str(e)}

    def list_material_presets(self, category="all"):
        """List available material presets"""
        try:
            if category == "all":
                result = {}
                for cat, presets in self.MATERIAL_PRESETS.items():
                    result[cat] = presets
                return {"presets": result}
            elif category in self.MATERIAL_PRESETS:
                return {"presets": {category: self.MATERIAL_PRESETS[category]}}
            else:
                return {"error": f"Unknown category: {category}", "available": list(self.MATERIAL_PRESETS.keys())}
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Natural Language Modeling

    PRIMITIVES = {
        "cube": lambda: bpy.ops.mesh.primitive_cube_add(),
        "sphere": lambda: bpy.ops.mesh.primitive_uv_sphere_add(),
        "cylinder": lambda: bpy.ops.mesh.primitive_cylinder_add(),
        "cone": lambda: bpy.ops.mesh.primitive_cone_add(),
        "plane": lambda: bpy.ops.mesh.primitive_plane_add(),
        "torus": lambda: bpy.ops.mesh.primitive_torus_add(),
        "monkey": lambda: bpy.ops.mesh.primitive_monkey_add(),
        "circle": lambda: bpy.ops.mesh.primitive_circle_add(),
        "grid": lambda: bpy.ops.mesh.primitive_grid_add(),
        "icosphere": lambda: bpy.ops.mesh.primitive_ico_sphere_add(),
    }

    def nlp_create(self, description):
        """Create objects from natural language description"""
        try:
            desc_lower = description.lower()
            created_objects = []

            # Parse primitive type
            primitive_type = None
            for prim_name in self.PRIMITIVES.keys():
                if prim_name in desc_lower:
                    primitive_type = prim_name
                    break

            # Check for complex objects
            if "table" in desc_lower:
                obj = self._generate_table(desc_lower)
                created_objects.append(obj.name)
            elif "chair" in desc_lower:
                obj = self._generate_chair(desc_lower)
                created_objects.append(obj.name)
            elif "stairs" in desc_lower or "staircase" in desc_lower:
                obj = self._generate_stairs(desc_lower)
                created_objects.append(obj.name)
            elif primitive_type:
                # Parse quantity
                quantity = 1
                import re
                qty_match = re.search(r"(\d+)\s+" + primitive_type, desc_lower)
                if qty_match:
                    quantity = int(qty_match.group(1))

                for i in range(quantity):
                    self.PRIMITIVES[primitive_type]()
                    obj = bpy.context.active_object

                    # Apply color if specified
                    for color_name, color_value in self.COLOR_KEYWORDS.items():
                        if color_name in desc_lower:
                            mat = bpy.data.materials.new(name=f"{color_name.capitalize()}_Material")
                            mat.use_nodes = True
                            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color_value
                            obj.data.materials.append(mat)
                            break

                    # Parse size
                    size_match = re.search(r"(\d+\.?\d*)\s*(meter|metre|m|cm|unit)", desc_lower)
                    if size_match:
                        size = float(size_match.group(1))
                        unit = size_match.group(2)
                        if unit in ["cm"]:
                            size /= 100
                        obj.scale = (size, size, size)

                    # Parse position
                    pos_match = re.search(r"at\s*[(\[]?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)", desc_lower)
                    if pos_match:
                        obj.location = (float(pos_match.group(1)), float(pos_match.group(2)), float(pos_match.group(3)))
                    elif quantity > 1:
                        # Arrange in a row
                        obj.location.x = i * 2.5

                    created_objects.append(obj.name)
            else:
                return {"error": "Could not understand what to create. Try: 'a red cube' or 'a table'"}

            return {
                "created_objects": created_objects,
                "count": len(created_objects),
                "description_parsed": desc_lower,
            }
        except Exception as e:
            return {"error": str(e)}

    def nlp_modify(self, object_name, modification):
        """Modify an object using natural language"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod_lower = modification.lower()
            changes = []
            import re

            # Scale modifications
            if "twice" in mod_lower or "double" in mod_lower:
                obj.scale = tuple(s * 2 for s in obj.scale)
                changes.append("doubled size")
            elif "half" in mod_lower:
                obj.scale = tuple(s * 0.5 for s in obj.scale)
                changes.append("halved size")

            scale_match = re.search(r"scale\s*(\d+\.?\d*)", mod_lower)
            if scale_match:
                factor = float(scale_match.group(1))
                obj.scale = tuple(s * factor for s in obj.scale)
                changes.append(f"scaled by {factor}")

            # Rotation modifications
            rot_match = re.search(r"rotate\s*(-?\d+\.?\d*)\s*(?:degrees?)?\s*(?:on\s*)?(x|y|z)?", mod_lower)
            if rot_match:
                import math
                angle = math.radians(float(rot_match.group(1)))
                axis = rot_match.group(2) or "z"
                if axis == "x":
                    obj.rotation_euler.x += angle
                elif axis == "y":
                    obj.rotation_euler.y += angle
                else:
                    obj.rotation_euler.z += angle
                changes.append(f"rotated {rot_match.group(1)} degrees on {axis}")

            # Position modifications
            move_match = re.search(r"move\s*(-?\d+\.?\d*)\s*(meter|m|unit)?\s*(up|down|left|right|forward|backward)?", mod_lower)
            if move_match:
                distance = float(move_match.group(1))
                direction = move_match.group(3) or "up"
                if direction == "up":
                    obj.location.z += distance
                elif direction == "down":
                    obj.location.z -= distance
                elif direction in ["left"]:
                    obj.location.x -= distance
                elif direction in ["right"]:
                    obj.location.x += distance
                elif direction == "forward":
                    obj.location.y += distance
                elif direction == "backward":
                    obj.location.y -= distance
                changes.append(f"moved {distance} {direction}")

            # Color modifications
            for color_name, color_value in self.COLOR_KEYWORDS.items():
                if color_name in mod_lower:
                    if obj.data.materials:
                        mat = obj.data.materials[0]
                    else:
                        mat = bpy.data.materials.new(name=f"{color_name.capitalize()}_Material")
                        mat.use_nodes = True
                        obj.data.materials.append(mat)
                    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color_value
                    changes.append(f"changed color to {color_name}")
                    break

            # Material properties
            if "shiny" in mod_lower or "glossy" in mod_lower:
                if obj.data.materials:
                    mat = obj.data.materials[0]
                    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.1
                    changes.append("made shiny")

            if "matte" in mod_lower or "rough" in mod_lower:
                if obj.data.materials:
                    mat = obj.data.materials[0]
                    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
                    changes.append("made matte")

            if "metallic" in mod_lower:
                if obj.data.materials:
                    mat = obj.data.materials[0]
                    mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.9
                    changes.append("made metallic")

            if not changes:
                return {"error": "Could not understand modification. Try: 'rotate 45 degrees', 'make it red', 'move 2 up'"}

            return {
                "object": object_name,
                "changes": changes,
                "new_location": list(obj.location),
                "new_rotation": list(obj.rotation_euler),
                "new_scale": list(obj.scale),
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_table(self, description):
        """Generate a simple table"""
        # Create table top
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
        top = bpy.context.active_object
        top.scale = (1.5, 0.8, 0.05)
        top.name = "Table_Top"

        # Create legs
        leg_positions = [(-0.6, -0.3, 0.35), (0.6, -0.3, 0.35), (-0.6, 0.3, 0.35), (0.6, 0.3, 0.35)]
        legs = []
        for i, pos in enumerate(leg_positions):
            bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
            leg = bpy.context.active_object
            leg.scale = (0.05, 0.05, 0.35)
            leg.name = f"Table_Leg_{i+1}"
            legs.append(leg)

        # Join all parts
        bpy.ops.object.select_all(action='DESELECT')
        top.select_set(True)
        for leg in legs:
            leg.select_set(True)
        bpy.context.view_layer.objects.active = top
        bpy.ops.object.join()
        top.name = "Table"

        # Apply color if specified
        for color_name, color_value in self.COLOR_KEYWORDS.items():
            if color_name in description:
                mat = bpy.data.materials.new(name=f"Table_{color_name}")
                mat.use_nodes = True
                mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color_value
                top.data.materials.append(mat)
                break

        return top

    def _generate_chair(self, description):
        """Generate a simple chair"""
        # Seat
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45))
        seat = bpy.context.active_object
        seat.scale = (0.5, 0.5, 0.05)
        seat.name = "Chair_Seat"

        # Back
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.22, 0.75))
        back = bpy.context.active_object
        back.scale = (0.5, 0.03, 0.3)
        back.name = "Chair_Back"

        # Legs
        leg_positions = [(-0.2, -0.2, 0.2), (0.2, -0.2, 0.2), (-0.2, 0.2, 0.2), (0.2, 0.2, 0.2)]
        legs = []
        for i, pos in enumerate(leg_positions):
            bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
            leg = bpy.context.active_object
            leg.scale = (0.03, 0.03, 0.2)
            leg.name = f"Chair_Leg_{i+1}"
            legs.append(leg)

        # Join
        bpy.ops.object.select_all(action='DESELECT')
        seat.select_set(True)
        back.select_set(True)
        for leg in legs:
            leg.select_set(True)
        bpy.context.view_layer.objects.active = seat
        bpy.ops.object.join()
        seat.name = "Chair"

        return seat

    def _generate_stairs(self, description):
        """Generate simple stairs"""
        import re
        steps = 5
        step_match = re.search(r"(\d+)\s*step", description)
        if step_match:
            steps = int(step_match.group(1))

        all_steps = []
        for i in range(steps):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, i * 0.3, i * 0.2))
            step = bpy.context.active_object
            step.scale = (1, 0.3, 0.1)
            step.name = f"Step_{i+1}"
            all_steps.append(step)

        # Join
        bpy.ops.object.select_all(action='DESELECT')
        for step in all_steps:
            step.select_set(True)
        bpy.context.view_layer.objects.active = all_steps[0]
        bpy.ops.object.join()
        all_steps[0].name = "Stairs"

        return all_steps[0]

    # endregion

    # region Scene Analyzer

    def analyze_scene_composition(self):
        """Analyze scene and provide feedback"""
        try:
            scene = bpy.context.scene
            analysis = {
                "lighting": self._analyze_lighting(),
                "composition": self._analyze_composition(),
                "materials": self._analyze_materials(),
                "overall_score": 0,
                "recommendations": [],
            }

            # Calculate overall score
            scores = [
                analysis["lighting"].get("score", 50),
                analysis["composition"].get("score", 50),
                analysis["materials"].get("score", 50),
            ]
            analysis["overall_score"] = sum(scores) // len(scores)

            # Compile recommendations
            analysis["recommendations"] = (
                analysis["lighting"].get("suggestions", []) +
                analysis["composition"].get("suggestions", []) +
                analysis["materials"].get("suggestions", [])
            )

            return analysis
        except Exception as e:
            return {"error": str(e)}

    def _analyze_lighting(self):
        """Analyze scene lighting"""
        lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
        score = 50
        suggestions = []

        if len(lights) == 0:
            score = 20
            suggestions.append("No lights in scene - add at least one light source")
        elif len(lights) == 1:
            score = 50
            suggestions.append("Single light creates harsh shadows - consider 3-point lighting setup")
        elif len(lights) >= 3:
            score = 80
            suggestions.append("Good lighting setup with multiple lights")

        # Check for environment lighting
        world = bpy.context.scene.world
        if world and world.use_nodes:
            for node in world.node_tree.nodes:
                if node.type == 'TEX_ENVIRONMENT':
                    score += 15
                    break

        # Check light types
        light_types = [l.data.type for l in lights]
        if 'SUN' in light_types:
            score += 5
        if 'AREA' in light_types:
            score += 5

        return {
            "score": min(100, score),
            "light_count": len(lights),
            "light_types": light_types,
            "has_environment": world.use_nodes if world else False,
            "suggestions": suggestions,
        }

    def _analyze_composition(self):
        """Analyze scene composition"""
        camera = bpy.context.scene.camera
        objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        score = 50
        suggestions = []

        if not camera:
            score = 30
            suggestions.append("No camera in scene - add a camera for rendering")
        else:
            score = 60

        if len(objects) == 0:
            score = 20
            suggestions.append("No mesh objects in scene")
        elif len(objects) == 1:
            suggestions.append("Single object - consider adding environment or context")
        elif len(objects) > 20:
            suggestions.append("Many objects - ensure scene isn't cluttered")

        # Check object distribution
        if objects:
            positions = [obj.location for obj in objects]
            avg_x = sum(p.x for p in positions) / len(positions)
            avg_y = sum(p.y for p in positions) / len(positions)

            # Check balance
            if abs(avg_x) < 1 and abs(avg_y) < 1:
                score += 10
                suggestions.append("Objects are well-centered")
            else:
                suggestions.append("Scene may be unbalanced - consider centering subjects")

        return {
            "score": min(100, score),
            "has_camera": camera is not None,
            "object_count": len(objects),
            "suggestions": suggestions,
        }

    def _analyze_materials(self):
        """Analyze scene materials"""
        objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        score = 50
        suggestions = []

        objects_without_materials = []
        for obj in objects:
            if not obj.data.materials:
                objects_without_materials.append(obj.name)

        if objects_without_materials:
            score -= len(objects_without_materials) * 5
            if len(objects_without_materials) <= 3:
                suggestions.append(f"Objects without materials: {', '.join(objects_without_materials)}")
            else:
                suggestions.append(f"{len(objects_without_materials)} objects have no materials")
        else:
            score = 70
            suggestions.append("All objects have materials assigned")

        # Check material variety
        materials = set()
        for obj in objects:
            for mat in obj.data.materials:
                if mat:
                    materials.add(mat.name)

        if len(materials) > 5:
            score += 10
            suggestions.append("Good material variety in scene")

        return {
            "score": min(100, max(0, score)),
            "material_count": len(materials),
            "objects_without_materials": len(objects_without_materials),
            "suggestions": suggestions,
        }

    def get_improvement_suggestions(self, focus_area="all"):
        """Get specific improvement suggestions"""
        try:
            suggestions = {"high_priority": [], "medium_priority": [], "low_priority": []}

            if focus_area in ["all", "lighting"]:
                lighting = self._analyze_lighting()
                if lighting["score"] < 50:
                    suggestions["high_priority"].extend(lighting["suggestions"])
                else:
                    suggestions["medium_priority"].extend(lighting["suggestions"])

            if focus_area in ["all", "composition"]:
                composition = self._analyze_composition()
                if composition["score"] < 50:
                    suggestions["high_priority"].extend(composition["suggestions"])
                else:
                    suggestions["low_priority"].extend(composition["suggestions"])

            if focus_area in ["all", "materials"]:
                materials = self._analyze_materials()
                if materials["score"] < 50:
                    suggestions["medium_priority"].extend(materials["suggestions"])
                else:
                    suggestions["low_priority"].extend(materials["suggestions"])

            return suggestions
        except Exception as e:
            return {"error": str(e)}

    def auto_optimize_lighting(self, style="studio"):
        """Automatically set up lighting based on style"""
        try:
            changes = []

            # Remove existing lights if requested
            for obj in list(bpy.context.scene.objects):
                if obj.type == 'LIGHT':
                    bpy.data.objects.remove(obj, do_unlink=True)
                    changes.append(f"Removed existing light: {obj.name}")

            if style == "studio":
                # Three-point lighting
                # Key light
                bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
                key = bpy.context.active_object
                key.name = "Key_Light"
                key.data.energy = 1000
                key.rotation_euler = (1.0, 0.0, 0.8)
                changes.append("Added key light")

                # Fill light
                bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
                fill = bpy.context.active_object
                fill.name = "Fill_Light"
                fill.data.energy = 300
                fill.rotation_euler = (1.2, 0.0, -0.8)
                changes.append("Added fill light")

                # Rim light
                bpy.ops.object.light_add(type='AREA', location=(0, 4, 4))
                rim = bpy.context.active_object
                rim.name = "Rim_Light"
                rim.data.energy = 500
                rim.rotation_euler = (0.5, 3.14, 0.0)
                changes.append("Added rim light")

            elif style == "outdoor":
                # Sun light
                bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
                sun = bpy.context.active_object
                sun.name = "Sun"
                sun.data.energy = 5
                sun.rotation_euler = (0.8, 0.2, 0.5)
                changes.append("Added sun light")

            elif style == "dramatic":
                # Single strong light with shadows
                bpy.ops.object.light_add(type='SPOT', location=(5, -5, 6))
                spot = bpy.context.active_object
                spot.name = "Dramatic_Spot"
                spot.data.energy = 2000
                spot.data.spot_size = 0.8
                spot.rotation_euler = (1.0, 0.0, 0.8)
                changes.append("Added dramatic spot light")

            elif style == "soft":
                # Large area lights for soft shadows
                bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
                soft = bpy.context.active_object
                soft.name = "Soft_Light"
                soft.data.energy = 800
                soft.data.size = 10
                changes.append("Added large soft area light")

            elif style == "product":
                # Clean product photography lighting
                for i, pos in enumerate([(3, -3, 3), (-3, -3, 3), (0, 3, 2)]):
                    bpy.ops.object.light_add(type='AREA', location=pos)
                    light = bpy.context.active_object
                    light.name = f"Product_Light_{i+1}"
                    light.data.energy = 500
                    light.data.size = 2
                changes.append("Added product photography lighting")

            elif style == "cinematic":
                # Warm key, cool fill
                bpy.ops.object.light_add(type='AREA', location=(4, -3, 4))
                key = bpy.context.active_object
                key.name = "Cinematic_Key"
                key.data.energy = 800
                key.data.color = (1.0, 0.9, 0.8)
                changes.append("Added warm key light")

                bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
                fill = bpy.context.active_object
                fill.name = "Cinematic_Fill"
                fill.data.energy = 200
                fill.data.color = (0.8, 0.9, 1.0)
                changes.append("Added cool fill light")

            return {
                "style_applied": style,
                "changes": changes,
                "lights_created": len([o for o in bpy.context.scene.objects if o.type == 'LIGHT']),
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Auto-Rig

    def auto_rig(self, mesh_name, rig_type="humanoid"):
        """Automatically rig a character mesh"""
        try:
            mesh_obj = bpy.data.objects.get(mesh_name)
            if not mesh_obj:
                return {"error": f"Mesh '{mesh_name}' not found"}
            if mesh_obj.type != 'MESH':
                return {"error": f"Object '{mesh_name}' is not a mesh"}

            # Get mesh bounds
            bounds = self._get_aabb(mesh_obj)
            min_bound = bounds[0]
            max_bound = bounds[1]
            height = max_bound[2] - min_bound[2]
            width = max_bound[0] - min_bound[0]
            center_x = (min_bound[0] + max_bound[0]) / 2
            center_y = (min_bound[1] + max_bound[1]) / 2

            # Create armature
            bpy.ops.object.armature_add(enter_editmode=True, location=(center_x, center_y, min_bound[2]))
            armature = bpy.context.active_object
            armature.name = f"{mesh_name}_Rig"

            arm_data = armature.data
            arm_data.name = f"{mesh_name}_Armature"

            bones_created = []

            if rig_type == "humanoid":
                bones_created = self._create_humanoid_bones(arm_data, height, min_bound[2])
            elif rig_type == "quadruped":
                bones_created = self._create_quadruped_bones(arm_data, height, width, min_bound[2])
            elif rig_type == "simple":
                bones_created = self._create_simple_bones(arm_data, height, min_bound[2])
            else:
                bones_created = self._create_simple_bones(arm_data, height, min_bound[2])

            # Exit edit mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Parent mesh to armature with automatic weights
            bpy.ops.object.select_all(action='DESELECT')
            mesh_obj.select_set(True)
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

            return {
                "armature_name": armature.name,
                "bones_created": bones_created,
                "rig_type": rig_type,
                "mesh_parented": mesh_name,
            }
        except Exception as e:
            return {"error": str(e)}

    def _create_humanoid_bones(self, arm_data, height, base_z):
        """Create humanoid bone structure"""
        bones = []

        # Remove default bone
        if arm_data.edit_bones:
            for bone in list(arm_data.edit_bones):
                arm_data.edit_bones.remove(bone)

        # Spine
        spine_base = arm_data.edit_bones.new("Spine")
        spine_base.head = (0, 0, base_z + height * 0.4)
        spine_base.tail = (0, 0, base_z + height * 0.55)
        bones.append("Spine")

        spine_mid = arm_data.edit_bones.new("Spine.001")
        spine_mid.head = spine_base.tail
        spine_mid.tail = (0, 0, base_z + height * 0.7)
        spine_mid.parent = spine_base
        bones.append("Spine.001")

        # Neck and Head
        neck = arm_data.edit_bones.new("Neck")
        neck.head = spine_mid.tail
        neck.tail = (0, 0, base_z + height * 0.8)
        neck.parent = spine_mid
        bones.append("Neck")

        head = arm_data.edit_bones.new("Head")
        head.head = neck.tail
        head.tail = (0, 0, base_z + height * 1.0)
        head.parent = neck
        bones.append("Head")

        # Hips
        hips = arm_data.edit_bones.new("Hips")
        hips.head = (0, 0, base_z + height * 0.4)
        hips.tail = (0, 0, base_z + height * 0.35)
        bones.append("Hips")

        # Legs
        for side, x_offset in [("L", 0.1 * height), ("R", -0.1 * height)]:
            thigh = arm_data.edit_bones.new(f"Thigh.{side}")
            thigh.head = (x_offset, 0, base_z + height * 0.4)
            thigh.tail = (x_offset, 0, base_z + height * 0.2)
            thigh.parent = hips
            bones.append(f"Thigh.{side}")

            shin = arm_data.edit_bones.new(f"Shin.{side}")
            shin.head = thigh.tail
            shin.tail = (x_offset, 0, base_z + height * 0.05)
            shin.parent = thigh
            bones.append(f"Shin.{side}")

            foot = arm_data.edit_bones.new(f"Foot.{side}")
            foot.head = shin.tail
            foot.tail = (x_offset, -0.1 * height, base_z)
            foot.parent = shin
            bones.append(f"Foot.{side}")

        # Arms
        for side, x_offset in [("L", 0.15 * height), ("R", -0.15 * height)]:
            shoulder = arm_data.edit_bones.new(f"Shoulder.{side}")
            shoulder.head = (0, 0, base_z + height * 0.7)
            shoulder.tail = (x_offset, 0, base_z + height * 0.7)
            shoulder.parent = spine_mid
            bones.append(f"Shoulder.{side}")

            upper_arm = arm_data.edit_bones.new(f"UpperArm.{side}")
            upper_arm.head = shoulder.tail
            upper_arm.tail = (x_offset * 2, 0, base_z + height * 0.55)
            upper_arm.parent = shoulder
            bones.append(f"UpperArm.{side}")

            forearm = arm_data.edit_bones.new(f"Forearm.{side}")
            forearm.head = upper_arm.tail
            forearm.tail = (x_offset * 2.5, 0, base_z + height * 0.4)
            forearm.parent = upper_arm
            bones.append(f"Forearm.{side}")

            hand = arm_data.edit_bones.new(f"Hand.{side}")
            hand.head = forearm.tail
            hand.tail = (x_offset * 2.7, 0, base_z + height * 0.35)
            hand.parent = forearm
            bones.append(f"Hand.{side}")

        return bones

    def _create_quadruped_bones(self, arm_data, height, width, base_z):
        """Create quadruped bone structure"""
        bones = []

        for bone in list(arm_data.edit_bones):
            arm_data.edit_bones.remove(bone)

        # Spine
        spine = arm_data.edit_bones.new("Spine")
        spine.head = (0, -width * 0.3, base_z + height * 0.5)
        spine.tail = (0, width * 0.3, base_z + height * 0.5)
        bones.append("Spine")

        # Head
        head = arm_data.edit_bones.new("Head")
        head.head = spine.tail
        head.tail = (0, width * 0.5, base_z + height * 0.6)
        head.parent = spine
        bones.append("Head")

        # Tail
        tail = arm_data.edit_bones.new("Tail")
        tail.head = spine.head
        tail.tail = (0, -width * 0.5, base_z + height * 0.4)
        tail.parent = spine
        bones.append("Tail")

        # Legs
        leg_positions = [
            ("Front.L", (width * 0.2, width * 0.2)),
            ("Front.R", (-width * 0.2, width * 0.2)),
            ("Back.L", (width * 0.2, -width * 0.2)),
            ("Back.R", (-width * 0.2, -width * 0.2)),
        ]

        for name, (x, y) in leg_positions:
            upper = arm_data.edit_bones.new(f"UpperLeg.{name}")
            upper.head = (x, y, base_z + height * 0.5)
            upper.tail = (x, y, base_z + height * 0.25)
            upper.parent = spine
            bones.append(f"UpperLeg.{name}")

            lower = arm_data.edit_bones.new(f"LowerLeg.{name}")
            lower.head = upper.tail
            lower.tail = (x, y, base_z)
            lower.parent = upper
            bones.append(f"LowerLeg.{name}")

        return bones

    def _create_simple_bones(self, arm_data, height, base_z):
        """Create simple bone chain"""
        bones = []

        for bone in list(arm_data.edit_bones):
            arm_data.edit_bones.remove(bone)

        segments = 5
        for i in range(segments):
            bone = arm_data.edit_bones.new(f"Bone.{i:03d}")
            bone.head = (0, 0, base_z + (height / segments) * i)
            bone.tail = (0, 0, base_z + (height / segments) * (i + 1))
            if i > 0:
                bone.parent = arm_data.edit_bones[f"Bone.{i-1:03d}"]
            bones.append(f"Bone.{i:03d}")

        return bones

    def auto_weight_paint(self, mesh_name, armature_name):
        """Automatically paint weights"""
        try:
            mesh_obj = bpy.data.objects.get(mesh_name)
            armature_obj = bpy.data.objects.get(armature_name)

            if not mesh_obj:
                return {"error": f"Mesh '{mesh_name}' not found"}
            if not armature_obj:
                return {"error": f"Armature '{armature_name}' not found"}

            # Clear existing weights
            mesh_obj.vertex_groups.clear()

            # Parent with automatic weights
            bpy.ops.object.select_all(action='DESELECT')
            mesh_obj.select_set(True)
            armature_obj.select_set(True)
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

            return {
                "mesh": mesh_name,
                "armature": armature_name,
                "vertex_groups_created": len(mesh_obj.vertex_groups),
            }
        except Exception as e:
            return {"error": str(e)}

    def add_ik_controls(self, armature_name, limb_type="all"):
        """Add IK controls to armature"""
        try:
            armature_obj = bpy.data.objects.get(armature_name)
            if not armature_obj:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature_obj.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}

            ik_targets = []
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.mode_set(mode='POSE')

            arm_data = armature_obj.data

            # Find end bones and add IK
            for bone in armature_obj.pose.bones:
                should_add_ik = False

                if limb_type == "all":
                    should_add_ik = any(x in bone.name.lower() for x in ["hand", "foot", "paw"])
                elif limb_type == "arms":
                    should_add_ik = "hand" in bone.name.lower()
                elif limb_type == "legs":
                    should_add_ik = any(x in bone.name.lower() for x in ["foot", "paw"])

                if should_add_ik:
                    # Add IK constraint
                    ik = bone.constraints.new('IK')
                    ik.chain_count = 2

                    # Create IK target
                    bpy.ops.object.mode_set(mode='EDIT')
                    target_bone = arm_data.edit_bones.new(f"IK_Target_{bone.name}")
                    target_bone.head = arm_data.edit_bones[bone.name].tail
                    target_bone.tail = (
                        target_bone.head[0],
                        target_bone.head[1] - 0.1,
                        target_bone.head[2]
                    )
                    bpy.ops.object.mode_set(mode='POSE')

                    ik.target = armature_obj
                    ik.subtarget = target_bone.name
                    ik_targets.append(target_bone.name)

            bpy.ops.object.mode_set(mode='OBJECT')

            return {
                "armature": armature_name,
                "ik_targets_created": ik_targets,
                "limb_type": limb_type,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # =============================================================================
    # ADVANCED FEATURES - PHASE 1
    # =============================================================================

    # region Modifier System

    def add_modifier(self, object_name, modifier_type, settings=None):
        """Add a modifier to an object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            # Validate modifier type
            valid_types = [
                'BOOLEAN', 'BEVEL', 'ARRAY', 'MIRROR', 'SUBSURF', 'SOLIDIFY',
                'DECIMATE', 'REMESH', 'SMOOTH', 'TRIANGULATE', 'WIREFRAME',
                'SKIN', 'SCREW', 'DISPLACE', 'SHRINKWRAP', 'SIMPLE_DEFORM',
                'LATTICE', 'CURVE', 'ARMATURE', 'CAST', 'WAVE'
            ]
            modifier_type = modifier_type.upper()
            if modifier_type not in valid_types:
                return {"error": f"Invalid modifier type. Valid types: {', '.join(valid_types)}"}

            # Add modifier
            mod = obj.modifiers.new(name=modifier_type.title(), type=modifier_type)

            # Apply settings if provided
            if settings:
                for key, value in settings.items():
                    if hasattr(mod, key):
                        setattr(mod, key, value)

            return {
                "success": True,
                "object": object_name,
                "modifier_name": mod.name,
                "modifier_type": modifier_type,
            }
        except Exception as e:
            return {"error": str(e)}

    def configure_modifier(self, object_name, modifier_name, settings):
        """Configure modifier parameters by name"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod = obj.modifiers.get(modifier_name)
            if not mod:
                return {"error": f"Modifier '{modifier_name}' not found on '{object_name}'"}

            applied_settings = {}
            for key, value in settings.items():
                if hasattr(mod, key):
                    setattr(mod, key, value)
                    applied_settings[key] = value

            return {
                "success": True,
                "object": object_name,
                "modifier": modifier_name,
                "settings_applied": applied_settings,
            }
        except Exception as e:
            return {"error": str(e)}

    def apply_modifier(self, object_name, modifier_name, remove_only=False):
        """Apply or remove a modifier"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod = obj.modifiers.get(modifier_name)
            if not mod:
                return {"error": f"Modifier '{modifier_name}' not found on '{object_name}'"}

            bpy.context.view_layer.objects.active = obj

            if remove_only:
                obj.modifiers.remove(mod)
                return {"success": True, "action": "removed", "modifier": modifier_name}
            else:
                bpy.ops.object.modifier_apply(modifier=modifier_name)
                return {"success": True, "action": "applied", "modifier": modifier_name}
        except Exception as e:
            return {"error": str(e)}

    def boolean_operation(self, target, tool, operation="DIFFERENCE", apply=True):
        """Perform boolean operation between two objects"""
        try:
            target_obj = bpy.data.objects.get(target)
            tool_obj = bpy.data.objects.get(tool)

            if not target_obj:
                return {"error": f"Target object '{target}' not found"}
            if not tool_obj:
                return {"error": f"Tool object '{tool}' not found"}

            operation = operation.upper()
            if operation not in ['UNION', 'DIFFERENCE', 'INTERSECT']:
                return {"error": "Operation must be UNION, DIFFERENCE, or INTERSECT"}

            # Add boolean modifier
            mod = target_obj.modifiers.new(name="Boolean", type='BOOLEAN')
            mod.operation = operation
            mod.object = tool_obj

            result_verts = 0
            if apply:
                bpy.context.view_layer.objects.active = target_obj
                bpy.ops.object.modifier_apply(modifier=mod.name)
                tool_obj.hide_set(True)
                result_verts = len(target_obj.data.vertices)

            return {
                "success": True,
                "operation": operation,
                "target": target,
                "tool": tool,
                "applied": apply,
                "result_vertices": result_verts if apply else "modifier_pending",
            }
        except Exception as e:
            return {"error": str(e)}

    def create_array(self, object_name, count=3, offset=(1, 0, 0), use_relative=True):
        """Create array modifier with count and offset"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod = obj.modifiers.new(name="Array", type='ARRAY')
            mod.count = count
            mod.use_relative_offset = use_relative
            mod.use_constant_offset = not use_relative

            if use_relative:
                mod.relative_offset_displace = offset
            else:
                mod.constant_offset_displace = offset

            return {
                "success": True,
                "object": object_name,
                "modifier": mod.name,
                "count": count,
                "offset": list(offset),
                "use_relative": use_relative,
            }
        except Exception as e:
            return {"error": str(e)}

    def add_bevel(self, object_name, width=0.1, segments=3, profile=0.5, limit_method="NONE"):
        """Add bevel modifier with settings"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod = obj.modifiers.new(name="Bevel", type='BEVEL')
            mod.width = width
            mod.segments = segments
            mod.profile = profile
            mod.limit_method = limit_method

            return {
                "success": True,
                "object": object_name,
                "modifier": mod.name,
                "width": width,
                "segments": segments,
                "profile": profile,
            }
        except Exception as e:
            return {"error": str(e)}

    def mirror_object(self, object_name, axis='X', use_bisect=False, merge_threshold=0.001):
        """Mirror object across axis"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod = obj.modifiers.new(name="Mirror", type='MIRROR')
            mod.use_axis[0] = 'X' in axis.upper()
            mod.use_axis[1] = 'Y' in axis.upper()
            mod.use_axis[2] = 'Z' in axis.upper()
            mod.use_bisect_axis[0] = use_bisect and 'X' in axis.upper()
            mod.use_bisect_axis[1] = use_bisect and 'Y' in axis.upper()
            mod.use_bisect_axis[2] = use_bisect and 'Z' in axis.upper()
            mod.merge_threshold = merge_threshold

            return {
                "success": True,
                "object": object_name,
                "modifier": mod.name,
                "axis": axis,
                "use_bisect": use_bisect,
            }
        except Exception as e:
            return {"error": str(e)}

    def subdivide_smooth(self, object_name, levels=2, render_levels=None):
        """Add subdivision surface modifier"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            mod.levels = levels
            mod.render_levels = render_levels if render_levels is not None else levels

            return {
                "success": True,
                "object": object_name,
                "modifier": mod.name,
                "viewport_levels": levels,
                "render_levels": mod.render_levels,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Mesh Editing Operations

    def extrude_faces(self, object_name, distance=1.0, face_indices=None):
        """Extrude faces by distance"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')

            import bmesh
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()

            # Select faces
            if face_indices:
                for i in face_indices:
                    if i < len(bm.faces):
                        bm.faces[i].select = True
            else:
                # Select all faces
                for f in bm.faces:
                    f.select = True

            bmesh.update_edit_mesh(obj.data)

            # Extrude
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value": (0, 0, distance)}
            )

            bpy.ops.object.mode_set(mode='OBJECT')

            return {
                "success": True,
                "object": object_name,
                "distance": distance,
                "faces_extruded": len(face_indices) if face_indices else "all",
            }
        except Exception as e:
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"error": str(e)}

    def inset_faces(self, object_name, thickness=0.1, depth=0.0, face_indices=None):
        """Inset selected faces"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')

            import bmesh
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()

            if face_indices:
                for i in face_indices:
                    if i < len(bm.faces):
                        bm.faces[i].select = True
            else:
                for f in bm.faces:
                    f.select = True

            bmesh.update_edit_mesh(obj.data)
            bpy.ops.mesh.inset(thickness=thickness, depth=depth)
            bpy.ops.object.mode_set(mode='OBJECT')

            return {
                "success": True,
                "object": object_name,
                "thickness": thickness,
                "depth": depth,
            }
        except Exception as e:
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"error": str(e)}

    def loop_cut(self, object_name, cuts=1, edge_index=0, smoothness=0):
        """Add loop cuts to mesh"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')

            bpy.ops.mesh.loopcut_slide(
                MESH_OT_loopcut={
                    "number_cuts": cuts,
                    "smoothness": smoothness,
                    "falloff": 'INVERSE_SQUARE',
                    "edge_index": edge_index
                }
            )

            bpy.ops.object.mode_set(mode='OBJECT')

            return {
                "success": True,
                "object": object_name,
                "cuts": cuts,
                "smoothness": smoothness,
            }
        except Exception as e:
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"error": str(e)}

    def merge_vertices(self, object_name, threshold=0.0001):
        """Merge vertices by distance"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            verts_before = len(obj.data.vertices)

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=threshold)
            bpy.ops.object.mode_set(mode='OBJECT')

            verts_after = len(obj.data.vertices)

            return {
                "success": True,
                "object": object_name,
                "vertices_before": verts_before,
                "vertices_after": verts_after,
                "vertices_removed": verts_before - verts_after,
            }
        except Exception as e:
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"error": str(e)}

    def separate_by_loose(self, object_name):
        """Separate loose parts into individual objects"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')

            new_objects = [o.name for o in bpy.context.selected_objects]

            return {
                "success": True,
                "original": object_name,
                "resulting_objects": new_objects,
                "object_count": len(new_objects),
            }
        except Exception as e:
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"error": str(e)}

    def join_objects(self, object_names, result_name=None):
        """Join multiple objects into one"""
        try:
            if len(object_names) < 2:
                return {"error": "Need at least 2 objects to join"}

            objects = [bpy.data.objects.get(name) for name in object_names]
            if None in objects:
                missing = [n for n, o in zip(object_names, objects) if o is None]
                return {"error": f"Objects not found: {missing}"}

            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects:
                obj.select_set(True)

            bpy.context.view_layer.objects.active = objects[0]
            bpy.ops.object.join()

            result = bpy.context.active_object
            if result_name:
                result.name = result_name

            return {
                "success": True,
                "joined_objects": object_names,
                "result_name": result.name,
                "vertex_count": len(result.data.vertices),
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Animation System

    def insert_keyframe(self, object_name, data_path, frame, value=None):
        """Insert keyframe for property at frame"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            # Map common property names
            property_map = {
                'location': 'location',
                'rotation': 'rotation_euler',
                'scale': 'scale',
                'location_x': 'location',
                'location_y': 'location',
                'location_z': 'location',
            }

            actual_path = property_map.get(data_path, data_path)

            # Set value if provided
            if value is not None:
                if actual_path == 'location' and isinstance(value, (list, tuple)):
                    obj.location = value
                elif actual_path == 'rotation_euler' and isinstance(value, (list, tuple)):
                    obj.rotation_euler = value
                elif actual_path == 'scale' and isinstance(value, (list, tuple)):
                    obj.scale = value

            # Insert keyframe
            obj.keyframe_insert(data_path=actual_path, frame=frame)

            return {
                "success": True,
                "object": object_name,
                "data_path": actual_path,
                "frame": frame,
                "value": value,
            }
        except Exception as e:
            return {"error": str(e)}

    def set_animation_range(self, start_frame, end_frame):
        """Set animation start and end frames"""
        try:
            bpy.context.scene.frame_start = start_frame
            bpy.context.scene.frame_end = end_frame

            return {
                "success": True,
                "start_frame": start_frame,
                "end_frame": end_frame,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_turntable(self, object_name, frames=120, axis='Z'):
        """Create 360 degree turntable animation"""
        try:
            import math
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            axis_index = {'X': 0, 'Y': 1, 'Z': 2}.get(axis.upper(), 2)

            # Set start keyframe
            bpy.context.scene.frame_set(1)
            rotation = list(obj.rotation_euler)
            rotation[axis_index] = 0
            obj.rotation_euler = rotation
            obj.keyframe_insert(data_path="rotation_euler", frame=1)

            # Set end keyframe
            bpy.context.scene.frame_set(frames)
            rotation[axis_index] = math.radians(360)
            obj.rotation_euler = rotation
            obj.keyframe_insert(data_path="rotation_euler", frame=frames)

            # Set linear interpolation
            if obj.animation_data and obj.animation_data.action:
                for fc in obj.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'LINEAR'

            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = frames

            return {
                "success": True,
                "object": object_name,
                "frames": frames,
                "axis": axis,
                "rotation_degrees": 360,
            }
        except Exception as e:
            return {"error": str(e)}

    def add_shape_key(self, object_name, shape_name="Key"):
        """Add shape key to mesh"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            bpy.context.view_layer.objects.active = obj

            # Add basis shape key if none exists
            if not obj.data.shape_keys:
                bpy.ops.object.shape_key_add(from_mix=False)

            # Add new shape key
            bpy.ops.object.shape_key_add(from_mix=False)
            new_key = obj.data.shape_keys.key_blocks[-1]
            new_key.name = shape_name

            return {
                "success": True,
                "object": object_name,
                "shape_key": new_key.name,
                "total_shape_keys": len(obj.data.shape_keys.key_blocks),
            }
        except Exception as e:
            return {"error": str(e)}

    def animate_shape_key(self, object_name, shape_key_name, keyframes):
        """Animate shape key value over frames. keyframes: list of (frame, value) tuples"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            if not obj.data.shape_keys:
                return {"error": "Object has no shape keys"}

            shape_key = obj.data.shape_keys.key_blocks.get(shape_key_name)
            if not shape_key:
                return {"error": f"Shape key '{shape_key_name}' not found"}

            for frame, value in keyframes:
                shape_key.value = value
                shape_key.keyframe_insert(data_path="value", frame=frame)

            return {
                "success": True,
                "object": object_name,
                "shape_key": shape_key_name,
                "keyframes_set": len(keyframes),
            }
        except Exception as e:
            return {"error": str(e)}

    def animate_path(self, object_name, curve_name, frames=100, follow=True):
        """Animate object along curve path"""
        try:
            obj = bpy.data.objects.get(object_name)
            curve = bpy.data.objects.get(curve_name)

            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            if not curve or curve.type != 'CURVE':
                return {"error": f"Curve '{curve_name}' not found"}

            # Add follow path constraint
            constraint = obj.constraints.new('FOLLOW_PATH')
            constraint.target = curve
            constraint.use_curve_follow = follow
            constraint.use_fixed_location = True
            constraint.offset_factor = 0

            # Animate offset
            constraint.offset_factor = 0
            constraint.keyframe_insert(data_path="offset_factor", frame=1)
            constraint.offset_factor = 1
            constraint.keyframe_insert(data_path="offset_factor", frame=frames)

            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = frames

            return {
                "success": True,
                "object": object_name,
                "curve": curve_name,
                "frames": frames,
                "follow_curve": follow,
            }
        except Exception as e:
            return {"error": str(e)}

    def bake_animation(self, object_name, start_frame=None, end_frame=None):
        """Bake animation (constraints/physics) to keyframes"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            start = start_frame or bpy.context.scene.frame_start
            end = end_frame or bpy.context.scene.frame_end

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.nla.bake(
                frame_start=start,
                frame_end=end,
                only_selected=True,
                visual_keying=True,
                clear_constraints=False,
                bake_types={'OBJECT'}
            )

            return {
                "success": True,
                "object": object_name,
                "start_frame": start,
                "end_frame": end,
                "frames_baked": end - start + 1,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Physics Simulation

    def add_rigid_body(self, object_name, body_type="ACTIVE", mass=1.0, friction=0.5, bounciness=0.5):
        """Add rigid body physics to object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.rigidbody.object_add()

            rb = obj.rigid_body
            rb.type = body_type.upper()
            rb.mass = mass
            rb.friction = friction
            rb.restitution = bounciness

            return {
                "success": True,
                "object": object_name,
                "body_type": body_type,
                "mass": mass,
                "friction": friction,
                "bounciness": bounciness,
            }
        except Exception as e:
            return {"error": str(e)}

    def add_cloth_simulation(self, object_name, preset="COTTON", collision_quality=5):
        """Add cloth physics simulation"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj or obj.type != 'MESH':
                return {"error": f"Mesh object '{object_name}' not found"}

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Add cloth modifier
            mod = obj.modifiers.new(name="Cloth", type='CLOTH')

            # Preset configurations
            presets = {
                "COTTON": {"mass": 0.3, "stiffness": 15, "damping": 5},
                "SILK": {"mass": 0.1, "stiffness": 5, "damping": 1},
                "LEATHER": {"mass": 0.4, "stiffness": 80, "damping": 25},
                "RUBBER": {"mass": 0.3, "stiffness": 25, "damping": 25},
            }

            preset_config = presets.get(preset.upper(), presets["COTTON"])
            cloth = mod.settings
            cloth.mass = preset_config["mass"]
            cloth.tension_stiffness = preset_config["stiffness"]
            cloth.compression_stiffness = preset_config["stiffness"]
            cloth.tension_damping = preset_config["damping"]
            cloth.compression_damping = preset_config["damping"]

            mod.collision_settings.collision_quality = collision_quality

            return {
                "success": True,
                "object": object_name,
                "preset": preset,
                "mass": cloth.mass,
                "stiffness": cloth.tension_stiffness,
            }
        except Exception as e:
            return {"error": str(e)}

    def add_collision(self, object_name):
        """Add collision modifier for physics interactions"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            mod = obj.modifiers.new(name="Collision", type='COLLISION')

            return {
                "success": True,
                "object": object_name,
                "modifier": mod.name,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_force_field(self, field_type="WIND", strength=1.0, location=(0, 0, 0)):
        """Create force field (wind, vortex, turbulence, etc.)"""
        try:
            valid_types = ['WIND', 'VORTEX', 'TURBULENCE', 'FORCE', 'HARMONIC', 'CHARGE', 'MAGNET']
            field_type = field_type.upper()
            if field_type not in valid_types:
                return {"error": f"Invalid field type. Valid types: {', '.join(valid_types)}"}

            bpy.ops.object.effector_add(type=field_type, location=location)
            field_obj = bpy.context.active_object
            field_obj.field.strength = strength

            return {
                "success": True,
                "field_type": field_type,
                "object_name": field_obj.name,
                "strength": strength,
                "location": list(location),
            }
        except Exception as e:
            return {"error": str(e)}

    def bake_physics(self, start_frame=1, end_frame=250):
        """Bake physics simulation"""
        try:
            bpy.context.scene.frame_start = start_frame
            bpy.context.scene.frame_end = end_frame

            # Bake rigid body
            if bpy.context.scene.rigidbody_world:
                bpy.context.scene.rigidbody_world.point_cache.frame_start = start_frame
                bpy.context.scene.rigidbody_world.point_cache.frame_end = end_frame
                bpy.ops.ptcache.bake_all(bake=True)

            return {
                "success": True,
                "start_frame": start_frame,
                "end_frame": end_frame,
            }
        except Exception as e:
            return {"error": str(e)}

    def add_particle_system(self, object_name, count=1000, lifetime=50, emit_from="FACE"):
        """Add particle emitter system"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            # Add particle system modifier
            mod = obj.modifiers.new(name="ParticleSystem", type='PARTICLE_SYSTEM')
            ps = obj.particle_systems[mod.name]
            settings = ps.settings

            settings.count = count
            settings.lifetime = lifetime
            settings.emit_from = emit_from

            return {
                "success": True,
                "object": object_name,
                "particle_system": ps.name,
                "count": count,
                "lifetime": lifetime,
                "emit_from": emit_from,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Camera & Rendering System

    def create_camera(self, name="Camera", location=(0, -10, 5), focal_length=50):
        """Create camera with settings"""
        try:
            bpy.ops.object.camera_add(location=location)
            camera = bpy.context.active_object
            camera.name = name
            camera.data.lens = focal_length

            # Point at origin by default
            direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector(location)
            camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

            return {
                "success": True,
                "camera_name": camera.name,
                "location": list(location),
                "focal_length": focal_length,
            }
        except Exception as e:
            return {"error": str(e)}

    def set_active_camera(self, camera_name):
        """Set active camera for scene"""
        try:
            camera = bpy.data.objects.get(camera_name)
            if not camera or camera.type != 'CAMERA':
                return {"error": f"Camera '{camera_name}' not found"}

            bpy.context.scene.camera = camera

            return {
                "success": True,
                "active_camera": camera_name,
            }
        except Exception as e:
            return {"error": str(e)}

    def configure_camera(self, camera_name, focal_length=None, dof_object=None, aperture=None, sensor_width=None):
        """Configure camera settings with optional DOF"""
        try:
            camera = bpy.data.objects.get(camera_name)
            if not camera or camera.type != 'CAMERA':
                return {"error": f"Camera '{camera_name}' not found"}

            cam_data = camera.data
            settings_changed = []

            if focal_length is not None:
                cam_data.lens = focal_length
                settings_changed.append(f"focal_length={focal_length}")

            if sensor_width is not None:
                cam_data.sensor_width = sensor_width
                settings_changed.append(f"sensor_width={sensor_width}")

            if dof_object is not None:
                dof_obj = bpy.data.objects.get(dof_object)
                if dof_obj:
                    cam_data.dof.use_dof = True
                    cam_data.dof.focus_object = dof_obj
                    settings_changed.append(f"dof_object={dof_object}")

            if aperture is not None:
                cam_data.dof.use_dof = True
                cam_data.dof.aperture_fstop = aperture
                settings_changed.append(f"aperture={aperture}")

            return {
                "success": True,
                "camera": camera_name,
                "settings_changed": settings_changed,
            }
        except Exception as e:
            return {"error": str(e)}

    def camera_look_at(self, camera_name, target):
        """Point camera at target object or location"""
        try:
            camera = bpy.data.objects.get(camera_name)
            if not camera or camera.type != 'CAMERA':
                return {"error": f"Camera '{camera_name}' not found"}

            if isinstance(target, str):
                target_obj = bpy.data.objects.get(target)
                if not target_obj:
                    return {"error": f"Target object '{target}' not found"}
                target_loc = target_obj.location
            else:
                target_loc = mathutils.Vector(target)

            direction = target_loc - camera.location
            camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

            return {
                "success": True,
                "camera": camera_name,
                "looking_at": list(target_loc),
            }
        except Exception as e:
            return {"error": str(e)}

    def set_render_settings(self, engine="CYCLES", samples=128, resolution=(1920, 1080), denoise=True):
        """Configure render settings"""
        try:
            scene = bpy.context.scene

            # Set render engine
            engine = engine.upper()
            if engine in ['CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH']:
                scene.render.engine = engine

            # Resolution
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]
            scene.render.resolution_percentage = 100

            # Samples
            if engine == 'CYCLES':
                scene.cycles.samples = samples
                scene.cycles.use_denoising = denoise
            elif 'EEVEE' in engine:
                scene.eevee.taa_render_samples = samples

            return {
                "success": True,
                "engine": engine,
                "samples": samples,
                "resolution": list(resolution),
                "denoise": denoise,
            }
        except Exception as e:
            return {"error": str(e)}

    def render_image(self, filepath, file_format="PNG"):
        """Render current frame to file"""
        try:
            scene = bpy.context.scene

            # Set output path
            scene.render.filepath = filepath
            scene.render.image_settings.file_format = file_format.upper()

            # Render
            bpy.ops.render.render(write_still=True)

            return {
                "success": True,
                "filepath": filepath,
                "format": file_format,
                "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            }
        except Exception as e:
            return {"error": str(e)}

    def render_animation(self, filepath, file_format="FFMPEG", start_frame=None, end_frame=None):
        """Render animation to file"""
        try:
            scene = bpy.context.scene

            if start_frame is not None:
                scene.frame_start = start_frame
            if end_frame is not None:
                scene.frame_end = end_frame

            scene.render.filepath = filepath

            if file_format.upper() == "FFMPEG":
                scene.render.image_settings.file_format = 'FFMPEG'
                scene.render.ffmpeg.format = 'MPEG4'
                scene.render.ffmpeg.codec = 'H264'
            else:
                scene.render.image_settings.file_format = file_format.upper()

            bpy.ops.render.render(animation=True)

            return {
                "success": True,
                "filepath": filepath,
                "format": file_format,
                "frame_range": [scene.frame_start, scene.frame_end],
            }
        except Exception as e:
            return {"error": str(e)}

    def setup_studio_render(self, background_color=(0.1, 0.1, 0.1)):
        """One-click studio render setup with lighting and background"""
        try:
            scene = bpy.context.scene
            changes = []

            # Set world background
            if not bpy.data.worlds:
                bpy.data.worlds.new("World")
            world = bpy.data.worlds[0]
            world.use_nodes = True
            bg_node = world.node_tree.nodes.get("Background")
            if bg_node:
                bg_node.inputs[0].default_value = (*background_color, 1.0)
            scene.world = world
            changes.append("Set background color")

            # Add key light
            bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
            key = bpy.context.active_object
            key.name = "Studio_Key"
            key.data.energy = 1000
            key.data.size = 3
            key.rotation_euler = (1.0, 0.0, 0.8)
            changes.append("Added key light")

            # Add fill light
            bpy.ops.object.light_add(type='AREA', location=(-4, -2, 4))
            fill = bpy.context.active_object
            fill.name = "Studio_Fill"
            fill.data.energy = 500
            fill.data.size = 2
            fill.rotation_euler = (1.0, 0.0, -0.8)
            changes.append("Added fill light")

            # Add rim light
            bpy.ops.object.light_add(type='AREA', location=(0, 4, 3))
            rim = bpy.context.active_object
            rim.name = "Studio_Rim"
            rim.data.energy = 800
            rim.data.size = 2
            rim.rotation_euler = (0.5, 3.14, 0.0)
            changes.append("Added rim light")

            # Add camera
            bpy.ops.object.camera_add(location=(7, -7, 5))
            camera = bpy.context.active_object
            camera.name = "Studio_Camera"
            camera.data.lens = 85
            direction = mathutils.Vector((0, 0, 0)) - camera.location
            camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
            scene.camera = camera
            changes.append("Added and set camera")

            # Render settings
            scene.render.engine = 'CYCLES'
            scene.cycles.samples = 128
            scene.cycles.use_denoising = True
            changes.append("Set render settings")

            return {
                "success": True,
                "changes": changes,
                "camera": camera.name,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Curves & Text System

    def create_bezier_curve(self, points, name="Curve", resolution=12, closed=False):
        """Create bezier curve from points list"""
        try:
            # Create curve data
            curve_data = bpy.data.curves.new(name, 'CURVE')
            curve_data.dimensions = '3D'
            curve_data.resolution_u = resolution

            # Create spline
            spline = curve_data.splines.new('BEZIER')
            spline.bezier_points.add(len(points) - 1)
            spline.use_cyclic_u = closed

            for i, point in enumerate(points):
                bp = spline.bezier_points[i]
                bp.co = point
                bp.handle_left_type = 'AUTO'
                bp.handle_right_type = 'AUTO'

            # Create object
            curve_obj = bpy.data.objects.new(name, curve_data)
            bpy.context.collection.objects.link(curve_obj)

            return {
                "success": True,
                "curve_name": curve_obj.name,
                "points": len(points),
                "closed": closed,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_text_object(self, text, name="Text", size=1, extrude=0, bevel_depth=0, font=None):
        """Create 3D text object"""
        try:
            # Create text curve data
            text_data = bpy.data.curves.new(name, 'FONT')
            text_data.body = text
            text_data.size = size
            text_data.extrude = extrude
            text_data.bevel_depth = bevel_depth

            if font and font in bpy.data.fonts:
                text_data.font = bpy.data.fonts[font]

            # Create object
            text_obj = bpy.data.objects.new(name, text_data)
            bpy.context.collection.objects.link(text_obj)
            bpy.context.view_layer.objects.active = text_obj

            return {
                "success": True,
                "text_name": text_obj.name,
                "text_content": text,
                "size": size,
                "extrude": extrude,
            }
        except Exception as e:
            return {"error": str(e)}

    def curve_to_mesh(self, curve_name, apply_modifiers=True):
        """Convert curve to mesh"""
        try:
            curve = bpy.data.objects.get(curve_name)
            if not curve or curve.type != 'CURVE':
                return {"error": f"Curve '{curve_name}' not found"}

            bpy.ops.object.select_all(action='DESELECT')
            curve.select_set(True)
            bpy.context.view_layer.objects.active = curve

            bpy.ops.object.convert(target='MESH')

            return {
                "success": True,
                "object_name": curve.name,
                "vertex_count": len(curve.data.vertices) if curve.type == 'MESH' else 0,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_pipe(self, curve_name, radius=0.1, resolution=8):
        """Create pipe along curve"""
        try:
            curve = bpy.data.objects.get(curve_name)
            if not curve or curve.type != 'CURVE':
                return {"error": f"Curve '{curve_name}' not found"}

            curve_data = curve.data
            curve_data.bevel_depth = radius
            curve_data.bevel_resolution = resolution
            curve_data.fill_mode = 'FULL'

            return {
                "success": True,
                "curve": curve_name,
                "radius": radius,
                "resolution": resolution,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Constraints & Relationships

    def add_constraint(self, object_name, constraint_type, target=None, settings=None):
        """Add constraint to object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            valid_constraints = [
                'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS',
                'TRACK_TO', 'DAMPED_TRACK', 'LOCKED_TRACK',
                'LIMIT_LOCATION', 'LIMIT_ROTATION', 'LIMIT_SCALE',
                'CHILD_OF', 'FLOOR', 'FOLLOW_PATH', 'PIVOT', 'SHRINKWRAP'
            ]

            constraint_type = constraint_type.upper()
            if constraint_type not in valid_constraints:
                return {"error": f"Invalid constraint type. Valid: {', '.join(valid_constraints)}"}

            constraint = obj.constraints.new(constraint_type)

            if target:
                target_obj = bpy.data.objects.get(target)
                if target_obj and hasattr(constraint, 'target'):
                    constraint.target = target_obj

            if settings:
                for key, value in settings.items():
                    if hasattr(constraint, key):
                        setattr(constraint, key, value)

            return {
                "success": True,
                "object": object_name,
                "constraint": constraint.name,
                "constraint_type": constraint_type,
                "target": target,
            }
        except Exception as e:
            return {"error": str(e)}

    def create_empty(self, name="Empty", empty_type="PLAIN_AXES", location=(0, 0, 0), size=1):
        """Create empty object for control"""
        try:
            bpy.ops.object.empty_add(type=empty_type, location=location)
            empty = bpy.context.active_object
            empty.name = name
            empty.empty_display_size = size

            return {
                "success": True,
                "empty_name": empty.name,
                "type": empty_type,
                "location": list(location),
            }
        except Exception as e:
            return {"error": str(e)}

    def parent_objects(self, child_name, parent_name, keep_transform=True):
        """Parent one object to another"""
        try:
            child = bpy.data.objects.get(child_name)
            parent = bpy.data.objects.get(parent_name)

            if not child:
                return {"error": f"Child object '{child_name}' not found"}
            if not parent:
                return {"error": f"Parent object '{parent_name}' not found"}

            if keep_transform:
                child.parent = parent
                child.matrix_parent_inverse = parent.matrix_world.inverted()
            else:
                child.parent = parent

            return {
                "success": True,
                "child": child_name,
                "parent": parent_name,
                "keep_transform": keep_transform,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Scene Organization

    def create_collection(self, name, parent=None, color_tag='NONE'):
        """Create new collection"""
        try:
            new_collection = bpy.data.collections.new(name)

            if parent:
                parent_coll = bpy.data.collections.get(parent)
                if parent_coll:
                    parent_coll.children.link(new_collection)
                else:
                    bpy.context.scene.collection.children.link(new_collection)
            else:
                bpy.context.scene.collection.children.link(new_collection)

            new_collection.color_tag = color_tag

            return {
                "success": True,
                "collection_name": new_collection.name,
                "parent": parent,
                "color_tag": color_tag,
            }
        except Exception as e:
            return {"error": str(e)}

    def move_to_collection(self, object_names, collection_name):
        """Move objects to collection"""
        try:
            target_coll = bpy.data.collections.get(collection_name)
            if not target_coll:
                return {"error": f"Collection '{collection_name}' not found"}

            moved = []
            for obj_name in object_names:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    # Remove from all collections
                    for coll in obj.users_collection:
                        coll.objects.unlink(obj)
                    # Add to target collection
                    target_coll.objects.link(obj)
                    moved.append(obj_name)

            return {
                "success": True,
                "collection": collection_name,
                "objects_moved": moved,
            }
        except Exception as e:
            return {"error": str(e)}

    def set_collection_visibility(self, collection_name, visible=True, render_visible=True):
        """Set collection visibility"""
        try:
            collection = bpy.data.collections.get(collection_name)
            if not collection:
                return {"error": f"Collection '{collection_name}' not found"}

            # Set viewport visibility
            layer_coll = bpy.context.view_layer.layer_collection.children.get(collection_name)
            if layer_coll:
                layer_coll.exclude = not visible

            # Set render visibility
            collection.hide_render = not render_visible

            return {
                "success": True,
                "collection": collection_name,
                "visible": visible,
                "render_visible": render_visible,
            }
        except Exception as e:
            return {"error": str(e)}

    def duplicate_linked(self, object_name, new_name=None):
        """Create linked duplicate of object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.object.duplicate(linked=True)
            new_obj = bpy.context.active_object

            if new_name:
                new_obj.name = new_name

            return {
                "success": True,
                "original": object_name,
                "duplicate": new_obj.name,
                "linked": True,
            }
        except Exception as e:
            return {"error": str(e)}

    def purge_unused(self):
        """Purge unused data blocks"""
        try:
            # Count before
            before = {
                "materials": len(bpy.data.materials),
                "textures": len(bpy.data.textures),
                "images": len(bpy.data.images),
                "meshes": len(bpy.data.meshes),
            }

            bpy.ops.outliner.orphans_purge(do_recursive=True)

            # Count after
            after = {
                "materials": len(bpy.data.materials),
                "textures": len(bpy.data.textures),
                "images": len(bpy.data.images),
                "meshes": len(bpy.data.meshes),
            }

            return {
                "success": True,
                "before": before,
                "after": after,
                "removed": {k: before[k] - after[k] for k in before},
            }
        except Exception as e:
            return {"error": str(e)}

    def save_blend(self, filepath):
        """Save .blend file"""
        try:
            bpy.ops.wm.save_as_mainfile(filepath=filepath)
            return {
                "success": True,
                "filepath": filepath,
            }
        except Exception as e:
            return {"error": str(e)}

    def export_scene(self, filepath, export_format="GLTF", selected_only=False, apply_modifiers=True):
        """Export scene to format (FBX, glTF, OBJ)"""
        try:
            export_format = export_format.upper()

            if export_format in ['GLTF', 'GLB']:
                bpy.ops.export_scene.gltf(
                    filepath=filepath,
                    use_selection=selected_only,
                    export_apply=apply_modifiers,
                    export_format='GLB' if export_format == 'GLB' else 'GLTF_SEPARATE'
                )
            elif export_format == 'FBX':
                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=selected_only,
                    apply_scale_options='FBX_SCALE_ALL',
                    use_mesh_modifiers=apply_modifiers
                )
            elif export_format == 'OBJ':
                bpy.ops.wm.obj_export(
                    filepath=filepath,
                    export_selected_objects=selected_only,
                    apply_modifiers=apply_modifiers
                )
            else:
                return {"error": f"Unsupported format: {export_format}. Use GLTF, GLB, FBX, or OBJ"}

            return {
                "success": True,
                "filepath": filepath,
                "format": export_format,
                "selected_only": selected_only,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion

    # region Geometry Nodes / Procedural

    def scatter_on_surface(self, surface_object, instance_object, density=10, seed=0, scale_min=0.8, scale_max=1.2, align_to_normal=True):
        """Scatter instances on mesh surface using geometry nodes"""
        try:
            surface = bpy.data.objects.get(surface_object)
            instance = bpy.data.objects.get(instance_object)

            if not surface or surface.type != 'MESH':
                return {"error": f"Surface mesh '{surface_object}' not found"}
            if not instance:
                return {"error": f"Instance object '{instance_object}' not found"}

            # Add geometry nodes modifier
            mod = surface.modifiers.new(name="ScatterInstances", type='NODES')

            # Create geometry nodes tree
            node_tree = bpy.data.node_groups.new("ScatterNodes", 'GeometryNodeTree')
            mod.node_group = node_tree

            nodes = node_tree.nodes
            links = node_tree.links

            # Create input/output
            group_input = nodes.new('NodeGroupInput')
            group_output = nodes.new('NodeGroupOutput')
            group_input.location = (-800, 0)
            group_output.location = (400, 0)

            # Add geometry socket to group
            node_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
            node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

            # Distribute points
            distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
            distribute.location = (-400, 0)
            distribute.distribute_method = 'POISSON'
            distribute.inputs['Density'].default_value = density
            distribute.inputs['Seed'].default_value = seed

            # Instance on points
            instance_node = nodes.new('GeometryNodeInstanceOnPoints')
            instance_node.location = (0, 0)

            # Object info for instance
            obj_info = nodes.new('GeometryNodeObjectInfo')
            obj_info.location = (-200, -200)
            obj_info.inputs['Object'].default_value = instance

            # Random scale
            random_val = nodes.new('FunctionNodeRandomValue')
            random_val.location = (-200, -400)
            random_val.data_type = 'FLOAT_VECTOR'
            random_val.inputs[0].default_value = (scale_min, scale_min, scale_min)
            random_val.inputs[1].default_value = (scale_max, scale_max, scale_max)

            # Join geometry
            join = nodes.new('GeometryNodeJoinGeometry')
            join.location = (200, 0)

            # Link nodes
            links.new(group_input.outputs[0], distribute.inputs['Mesh'])
            links.new(distribute.outputs['Points'], instance_node.inputs['Points'])
            links.new(obj_info.outputs['Geometry'], instance_node.inputs['Instance'])
            links.new(random_val.outputs[1], instance_node.inputs['Scale'])

            if align_to_normal:
                links.new(distribute.outputs['Rotation'], instance_node.inputs['Rotation'])

            links.new(group_input.outputs[0], join.inputs['Geometry'])
            links.new(instance_node.outputs['Instances'], join.inputs['Geometry'])
            links.new(join.outputs[0], group_output.inputs[0])

            return {
                "success": True,
                "surface": surface_object,
                "instance": instance_object,
                "density": density,
                "seed": seed,
                "scale_range": [scale_min, scale_max],
            }
        except Exception as e:
            return {"error": str(e)}

    def create_procedural_terrain(self, name="Terrain", size=10, resolution=50, height_scale=2, noise_scale=1):
        """Generate procedural terrain mesh"""
        try:
            # Create grid
            bpy.ops.mesh.primitive_grid_add(
                x_subdivisions=resolution,
                y_subdivisions=resolution,
                size=size
            )
            terrain = bpy.context.active_object
            terrain.name = name

            # Add displace modifier with texture
            tex = bpy.data.textures.new(f"{name}_Noise", type='CLOUDS')
            tex.noise_scale = noise_scale

            mod = terrain.modifiers.new(name="Displace", type='DISPLACE')
            mod.texture = tex
            mod.strength = height_scale
            mod.mid_level = 0.5

            return {
                "success": True,
                "terrain_name": terrain.name,
                "size": size,
                "resolution": resolution,
                "height_scale": height_scale,
            }
        except Exception as e:
            return {"error": str(e)}

    # endregion


# Blender Addon Preferences
class BLENDERFORGE_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    telemetry_consent: BoolProperty(
        name="Allow Anonymized Prompt Collection",
        description="Allow collection of anonymized prompts to help improve Blender MCP",
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        # Telemetry section
        layout.label(text="Telemetry & Privacy:", icon="PREFERENCES")

        box = layout.box()
        row = box.row()
        row.prop(self, "telemetry_consent", text="Allow Anonymized Prompt Collection")

        # Info text
        box.separator()
        box.label(text="All data is anonymized and helps improve Blender MCP.", icon="INFO")
        box.label(text="You can opt out anytime by unchecking the box above.", icon="INFO")

        # Terms and Conditions link
        box.separator()
        row = box.row()
        row.operator("blendermcp.open_terms", text="View Terms and Conditions", icon="TEXT")


# Blender UI Panel
class BLENDERFORGE_PT_Panel(bpy.types.Panel):
    bl_label = "Blender MCP"
    bl_idname = "BLENDERFORGE_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderForge"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "blenderforge_port")
        layout.prop(scene, "blenderforge_use_polyhaven", text="Use assets from Poly Haven")

        layout.prop(scene, "blenderforge_use_hyper3d", text="Use Hyper3D Rodin 3D model generation")
        if scene.blenderforge_use_hyper3d:
            layout.prop(scene, "blenderforge_hyper3d_mode", text="Rodin Mode")
            layout.prop(scene, "blenderforge_hyper3d_api_key", text="API Key")
            layout.operator(
                "blendermcp.set_hyper3d_free_trial_api_key", text="Set Free Trial API Key"
            )

        layout.prop(scene, "blenderforge_use_sketchfab", text="Use assets from Sketchfab")
        if scene.blenderforge_use_sketchfab:
            layout.prop(scene, "blenderforge_sketchfab_api_key", text="API Key")

        layout.prop(
            scene, "blenderforge_use_hunyuan3d", text="Use Tencent Hunyuan 3D model generation"
        )
        if scene.blenderforge_use_hunyuan3d:
            layout.prop(scene, "blenderforge_hunyuan3d_mode", text="Hunyuan3D Mode")
            if scene.blenderforge_hunyuan3d_mode == "OFFICIAL_API":
                layout.prop(scene, "blenderforge_hunyuan3d_secret_id", text="SecretId")
                layout.prop(scene, "blenderforge_hunyuan3d_secret_key", text="SecretKey")
            if scene.blenderforge_hunyuan3d_mode == "LOCAL_API":
                layout.prop(scene, "blenderforge_hunyuan3d_api_url", text="API URL")
                layout.prop(
                    scene, "blenderforge_hunyuan3d_octree_resolution", text="Octree Resolution"
                )
                layout.prop(
                    scene,
                    "blenderforge_hunyuan3d_num_inference_steps",
                    text="Number of Inference Steps",
                )
                layout.prop(scene, "blenderforge_hunyuan3d_guidance_scale", text="Guidance Scale")
                layout.prop(scene, "blenderforge_hunyuan3d_texture", text="Generate Texture")

        if not scene.blenderforge_server_running:
            layout.operator("blendermcp.start_server", text="Connect to MCP server")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from MCP server")
            layout.label(text=f"Running on port {scene.blenderforge_port}")


# Operator to guide user to get Hyper3D API Key
class BLENDERFORGE_OT_SetFreeTrialHyper3DAPIKey(bpy.types.Operator):
    bl_idname = "blendermcp.set_hyper3d_free_trial_api_key"
    bl_label = "Get API Key"
    bl_description = "Opens Hyper3D website to get your API key"

    def execute(self, context):
        import webbrowser
        # Check for environment variable first
        env_key = get_rodin_api_key()
        if env_key:
            context.scene.blenderforge_hyper3d_api_key = env_key
            context.scene.blenderforge_hyper3d_mode = "MAIN_SITE"
            self.report({"INFO"}, "API Key loaded from environment!")
            return {"FINISHED"}
        # Otherwise, guide user to get their own key
        webbrowser.open("https://hyper3d.ai/")
        self.report({"INFO"}, "Please sign up at hyper3d.ai to get your free API key")
        return {"FINISHED"}


# Operator to start the server
class BLENDERFORGE_OT_StartServer(bpy.types.Operator):
    bl_idname = "blendermcp.start_server"
    bl_label = "Connect to Claude"
    bl_description = "Start the BlenderForge server to connect with Claude"

    def execute(self, context):
        scene = context.scene

        # Create a new server instance
        if not hasattr(bpy.types, "blenderforge_server") or not bpy.types.blenderforge_server:
            bpy.types.blenderforge_server = BlenderForgeServer(port=scene.blenderforge_port)

        # Start the server
        bpy.types.blenderforge_server.start()
        scene.blenderforge_server_running = True

        return {"FINISHED"}


# Operator to stop the server
class BLENDERFORGE_OT_StopServer(bpy.types.Operator):
    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop the connection to Claude"
    bl_description = "Stop the connection to Claude"

    def execute(self, context):
        scene = context.scene

        # Stop the server if it exists
        if hasattr(bpy.types, "blenderforge_server") and bpy.types.blenderforge_server:
            bpy.types.blenderforge_server.stop()
            del bpy.types.blenderforge_server

        scene.blenderforge_server_running = False

        return {"FINISHED"}


# Operator to open Terms and Conditions
class BLENDERFORGE_OT_OpenTerms(bpy.types.Operator):
    bl_idname = "blendermcp.open_terms"
    bl_label = "View Terms and Conditions"
    bl_description = "Open the Terms and Conditions document"

    def execute(self, context):
        # Open the Terms and Conditions on GitHub
        terms_url = "https://github.com/ahujasid/blender-mcp/blob/main/TERMS_AND_CONDITIONS.md"
        try:
            import webbrowser

            webbrowser.open(terms_url)
            self.report({"INFO"}, "Terms and Conditions opened in browser")
        except Exception as e:
            self.report({"ERROR"}, f"Could not open Terms and Conditions: {str(e)}")

        return {"FINISHED"}


# Registration functions
def register():
    bpy.types.Scene.blenderforge_port = IntProperty(
        name="Port",
        description="Port for the BlenderForge server",
        default=9876,
        min=1024,
        max=65535,
    )

    bpy.types.Scene.blenderforge_server_running = bpy.props.BoolProperty(
        name="Server Running", default=False
    )

    bpy.types.Scene.blenderforge_use_polyhaven = bpy.props.BoolProperty(
        name="Use Poly Haven", description="Enable Poly Haven asset integration", default=False
    )

    bpy.types.Scene.blenderforge_use_hyper3d = bpy.props.BoolProperty(
        name="Use Hyper3D Rodin",
        description="Enable Hyper3D Rodin generatino integration",
        default=False,
    )

    bpy.types.Scene.blenderforge_hyper3d_mode = bpy.props.EnumProperty(
        name="Rodin Mode",
        description="Choose the platform used to call Rodin APIs",
        items=[
            ("MAIN_SITE", "hyper3d.ai", "hyper3d.ai"),
            ("FAL_AI", "fal.ai", "fal.ai"),
        ],
        default="MAIN_SITE",
    )

    bpy.types.Scene.blenderforge_hyper3d_api_key = bpy.props.StringProperty(
        name="Hyper3D API Key",
        subtype="PASSWORD",
        description="API Key provided by Hyper3D",
        default="",
    )

    bpy.types.Scene.blenderforge_use_hunyuan3d = bpy.props.BoolProperty(
        name="Use Hunyuan 3D", description="Enable Hunyuan asset integration", default=False
    )

    bpy.types.Scene.blenderforge_hunyuan3d_mode = bpy.props.EnumProperty(
        name="Hunyuan3D Mode",
        description="Choose a local or official APIs",
        items=[
            ("LOCAL_API", "local api", "local api"),
            ("OFFICIAL_API", "official api", "official api"),
        ],
        default="LOCAL_API",
    )

    bpy.types.Scene.blenderforge_hunyuan3d_secret_id = bpy.props.StringProperty(
        name="Hunyuan 3D SecretId", description="SecretId provided by Hunyuan 3D", default=""
    )

    bpy.types.Scene.blenderforge_hunyuan3d_secret_key = bpy.props.StringProperty(
        name="Hunyuan 3D SecretKey",
        subtype="PASSWORD",
        description="SecretKey provided by Hunyuan 3D",
        default="",
    )

    bpy.types.Scene.blenderforge_hunyuan3d_api_url = bpy.props.StringProperty(
        name="API URL",
        description="URL of the Hunyuan 3D API service",
        default="http://localhost:8081",
    )

    bpy.types.Scene.blenderforge_hunyuan3d_octree_resolution = bpy.props.IntProperty(
        name="Octree Resolution",
        description="Octree resolution for the 3D generation",
        default=256,
        min=128,
        max=512,
    )

    bpy.types.Scene.blenderforge_hunyuan3d_num_inference_steps = bpy.props.IntProperty(
        name="Number of Inference Steps",
        description="Number of inference steps for the 3D generation",
        default=20,
        min=20,
        max=50,
    )

    bpy.types.Scene.blenderforge_hunyuan3d_guidance_scale = bpy.props.FloatProperty(
        name="Guidance Scale",
        description="Guidance scale for the 3D generation",
        default=5.5,
        min=1.0,
        max=10.0,
    )

    bpy.types.Scene.blenderforge_hunyuan3d_texture = bpy.props.BoolProperty(
        name="Generate Texture",
        description="Whether to generate texture for the 3D model",
        default=False,
    )

    bpy.types.Scene.blenderforge_use_sketchfab = bpy.props.BoolProperty(
        name="Use Sketchfab", description="Enable Sketchfab asset integration", default=False
    )

    bpy.types.Scene.blenderforge_sketchfab_api_key = bpy.props.StringProperty(
        name="Sketchfab API Key",
        subtype="PASSWORD",
        description="API Key provided by Sketchfab",
        default="",
    )

    # Register preferences class
    bpy.utils.register_class(BLENDERFORGE_AddonPreferences)

    bpy.utils.register_class(BLENDERFORGE_PT_Panel)
    bpy.utils.register_class(BLENDERFORGE_OT_SetFreeTrialHyper3DAPIKey)
    bpy.utils.register_class(BLENDERFORGE_OT_StartServer)
    bpy.utils.register_class(BLENDERFORGE_OT_StopServer)
    bpy.utils.register_class(BLENDERFORGE_OT_OpenTerms)

    print("BlenderForge addon registered")


def unregister():
    # Stop the server if it's running
    if hasattr(bpy.types, "blenderforge_server") and bpy.types.blenderforge_server:
        bpy.types.blenderforge_server.stop()
        del bpy.types.blenderforge_server

    bpy.utils.unregister_class(BLENDERFORGE_PT_Panel)
    bpy.utils.unregister_class(BLENDERFORGE_OT_SetFreeTrialHyper3DAPIKey)
    bpy.utils.unregister_class(BLENDERFORGE_OT_StartServer)
    bpy.utils.unregister_class(BLENDERFORGE_OT_StopServer)
    bpy.utils.unregister_class(BLENDERFORGE_OT_OpenTerms)
    bpy.utils.unregister_class(BLENDERFORGE_AddonPreferences)

    del bpy.types.Scene.blenderforge_port
    del bpy.types.Scene.blenderforge_server_running
    del bpy.types.Scene.blenderforge_use_polyhaven
    del bpy.types.Scene.blenderforge_use_hyper3d
    del bpy.types.Scene.blenderforge_hyper3d_mode
    del bpy.types.Scene.blenderforge_hyper3d_api_key
    del bpy.types.Scene.blenderforge_use_sketchfab
    del bpy.types.Scene.blenderforge_sketchfab_api_key
    del bpy.types.Scene.blenderforge_use_hunyuan3d
    del bpy.types.Scene.blenderforge_hunyuan3d_mode
    del bpy.types.Scene.blenderforge_hunyuan3d_secret_id
    del bpy.types.Scene.blenderforge_hunyuan3d_secret_key
    del bpy.types.Scene.blenderforge_hunyuan3d_api_url
    del bpy.types.Scene.blenderforge_hunyuan3d_octree_resolution
    del bpy.types.Scene.blenderforge_hunyuan3d_num_inference_steps
    del bpy.types.Scene.blenderforge_hunyuan3d_guidance_scale
    del bpy.types.Scene.blenderforge_hunyuan3d_texture

    print("BlenderForge addon unregistered")


if __name__ == "__main__":
    register()
