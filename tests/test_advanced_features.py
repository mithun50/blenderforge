"""Tests for Advanced Features - Modifiers, Animation, Physics, Rendering, etc."""

import json
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# MODIFIER SYSTEM TESTS
# =============================================================================


class TestModifierSystem:
    """Tests for modifier system tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_add_modifier_success(self, mock_get_conn):
        """Test adding a modifier to an object."""
        from blenderforge.server import add_modifier

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "modifier_name": "Bevel",
            "modifier_type": "BEVEL",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_modifier(ctx, "Cube", "BEVEL")

        data = json.loads(result)
        assert data["success"] is True
        assert data["modifier_type"] == "BEVEL"

    @patch("blenderforge.server.get_blender_connection")
    def test_add_modifier_with_settings(self, mock_get_conn):
        """Test adding modifier with custom settings."""
        from blenderforge.server import add_modifier

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "modifier_name": "Bevel",
            "modifier_type": "BEVEL",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        settings = '{"width": 0.2, "segments": 5}'
        result = add_modifier(ctx, "Cube", "BEVEL", settings)

        data = json.loads(result)
        assert data["success"] is True
        mock_conn.send_command.assert_called_once()

    @patch("blenderforge.server.get_blender_connection")
    def test_boolean_operation_difference(self, mock_get_conn):
        """Test boolean difference operation."""
        from blenderforge.server import boolean_operation

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "operation": "DIFFERENCE",
            "target": "Cube",
            "tool": "Sphere",
            "result_vertices": 156,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = boolean_operation(ctx, "Cube", "Sphere", "DIFFERENCE")

        data = json.loads(result)
        assert data["success"] is True
        assert data["operation"] == "DIFFERENCE"
        assert data["result_vertices"] == 156

    @patch("blenderforge.server.get_blender_connection")
    def test_create_array(self, mock_get_conn):
        """Test creating an array modifier."""
        from blenderforge.server import create_array

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "count": 5,
            "modifier_name": "Array",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_array(ctx, "Cube", count=5, offset_x=2.0)

        data = json.loads(result)
        assert data["success"] is True
        assert data["count"] == 5

    @patch("blenderforge.server.get_blender_connection")
    def test_add_bevel(self, mock_get_conn):
        """Test adding bevel modifier."""
        from blenderforge.server import add_bevel

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "modifier_name": "Bevel",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_bevel(ctx, "Cube", width=0.1, segments=3)

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_mirror_object(self, mock_get_conn):
        """Test adding mirror modifier."""
        from blenderforge.server import mirror_object

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "axis": [True, False, False],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = mirror_object(ctx, "Cube", axis_x=True)

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_subdivide_smooth(self, mock_get_conn):
        """Test adding subdivision surface."""
        from blenderforge.server import subdivide_smooth

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "levels": 2,
            "render_levels": 3,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = subdivide_smooth(ctx, "Cube", levels=2, render_levels=3)

        data = json.loads(result)
        assert data["success"] is True
        assert data["levels"] == 2


# =============================================================================
# MESH EDITING TESTS
# =============================================================================


class TestMeshEditing:
    """Tests for mesh editing tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_extrude_faces(self, mock_get_conn):
        """Test extruding faces."""
        from blenderforge.server import extrude_faces

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "faces_extruded": 3,
            "new_vertices": 12,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = extrude_faces(ctx, "Cube", "[0, 1, 2]", 1.0)

        data = json.loads(result)
        assert data["success"] is True
        assert data["faces_extruded"] == 3

    @patch("blenderforge.server.get_blender_connection")
    def test_loop_cut(self, mock_get_conn):
        """Test adding loop cuts."""
        from blenderforge.server import loop_cut

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "cuts_added": 3,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = loop_cut(ctx, "Cube", 0, cuts=3)

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_join_objects(self, mock_get_conn):
        """Test joining multiple objects."""
        from blenderforge.server import join_objects

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "result_object": "Cube",
            "objects_joined": 3,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = join_objects(ctx, '["Cube", "Sphere", "Cylinder"]')

        data = json.loads(result)
        assert data["success"] is True
        assert data["objects_joined"] == 3


# =============================================================================
# ANIMATION SYSTEM TESTS
# =============================================================================


class TestAnimationSystem:
    """Tests for animation tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_insert_keyframe(self, mock_get_conn):
        """Test inserting a keyframe."""
        from blenderforge.server import insert_keyframe

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cube",
            "data_path": "location",
            "frame": 1,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = insert_keyframe(ctx, "Cube", "location", 1)

        data = json.loads(result)
        assert data["success"] is True
        assert data["frame"] == 1

    @patch("blenderforge.server.get_blender_connection")
    def test_set_animation_range(self, mock_get_conn):
        """Test setting animation range."""
        from blenderforge.server import set_animation_range

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "start_frame": 1,
            "end_frame": 250,
            "fps": 24,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = set_animation_range(ctx, start_frame=1, end_frame=250, fps=24)

        data = json.loads(result)
        assert data["success"] is True
        assert data["fps"] == 24

    @patch("blenderforge.server.get_blender_connection")
    def test_create_turntable(self, mock_get_conn):
        """Test creating turntable animation."""
        from blenderforge.server import create_turntable

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Product",
            "frames": 120,
            "axis": "Z",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_turntable(ctx, "Product", frames=120, axis="Z")

        data = json.loads(result)
        assert data["success"] is True
        assert data["frames"] == 120

    @patch("blenderforge.server.get_blender_connection")
    def test_add_shape_key(self, mock_get_conn):
        """Test adding shape key."""
        from blenderforge.server import add_shape_key

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Face",
            "shape_key_name": "Smile",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_shape_key(ctx, "Face", name="Smile")

        data = json.loads(result)
        assert data["success"] is True


# =============================================================================
# PHYSICS SIMULATION TESTS
# =============================================================================


class TestPhysicsSimulation:
    """Tests for physics simulation tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_add_rigid_body_active(self, mock_get_conn):
        """Test adding active rigid body."""
        from blenderforge.server import add_rigid_body

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Ball",
            "body_type": "ACTIVE",
            "mass": 1.0,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_rigid_body(ctx, "Ball", body_type="ACTIVE", mass=1.0)

        data = json.loads(result)
        assert data["success"] is True
        assert data["body_type"] == "ACTIVE"

    @patch("blenderforge.server.get_blender_connection")
    def test_add_rigid_body_passive(self, mock_get_conn):
        """Test adding passive rigid body (collider)."""
        from blenderforge.server import add_rigid_body

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Floor",
            "body_type": "PASSIVE",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_rigid_body(ctx, "Floor", body_type="PASSIVE")

        data = json.loads(result)
        assert data["success"] is True
        assert data["body_type"] == "PASSIVE"

    @patch("blenderforge.server.get_blender_connection")
    def test_add_cloth_simulation(self, mock_get_conn):
        """Test adding cloth simulation."""
        from blenderforge.server import add_cloth_simulation

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Cloth",
            "preset": "COTTON",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_cloth_simulation(ctx, "Cloth", preset="COTTON")

        data = json.loads(result)
        assert data["success"] is True
        assert data["preset"] == "COTTON"

    @patch("blenderforge.server.get_blender_connection")
    def test_create_force_field(self, mock_get_conn):
        """Test creating force field."""
        from blenderforge.server import create_force_field

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "field_type": "WIND",
            "strength": 10.0,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_force_field(ctx, "WIND", strength=10.0)

        data = json.loads(result)
        assert data["success"] is True
        assert data["field_type"] == "WIND"

    @patch("blenderforge.server.get_blender_connection")
    def test_add_particle_system(self, mock_get_conn):
        """Test adding particle system."""
        from blenderforge.server import add_particle_system

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Emitter",
            "count": 1000,
            "lifetime": 50,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_particle_system(ctx, "Emitter", count=1000)

        data = json.loads(result)
        assert data["success"] is True
        assert data["count"] == 1000


# =============================================================================
# CAMERA & RENDERING TESTS
# =============================================================================


class TestCameraRendering:
    """Tests for camera and rendering tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_create_camera(self, mock_get_conn):
        """Test creating a camera."""
        from blenderforge.server import create_camera

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "name": "Camera.001",
            "focal_length": 50.0,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_camera(ctx, name="Camera.001", focal_length=50.0)

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_set_render_settings(self, mock_get_conn):
        """Test setting render settings."""
        from blenderforge.server import set_render_settings

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "engine": "CYCLES",
            "samples": 256,
            "resolution": [1920, 1080],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = set_render_settings(
            ctx, engine="CYCLES", samples=256, resolution_x=1920, resolution_y=1080
        )

        data = json.loads(result)
        assert data["success"] is True
        assert data["engine"] == "CYCLES"
        assert data["samples"] == 256

    @patch("blenderforge.server.get_blender_connection")
    def test_render_image(self, mock_get_conn):
        """Test rendering an image."""
        from blenderforge.server import render_image

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "filepath": "/tmp/render.png",
            "format": "PNG",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = render_image(ctx, "/tmp/render", format="PNG")

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_setup_studio_render(self, mock_get_conn):
        """Test setting up studio render."""
        from blenderforge.server import setup_studio_render

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "style": "PRODUCT",
            "lights_created": ["Key", "Fill", "Rim"],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = setup_studio_render(ctx, target_object="Product", style="PRODUCT")

        data = json.loads(result)
        assert data["success"] is True
        assert data["style"] == "PRODUCT"


# =============================================================================
# CURVES & TEXT TESTS
# =============================================================================


class TestCurvesText:
    """Tests for curves and text tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_create_bezier_curve(self, mock_get_conn):
        """Test creating bezier curve."""
        from blenderforge.server import create_bezier_curve

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "name": "Curve",
            "points": 3,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_bezier_curve(ctx, "[[0,0,0], [1,0,1], [2,0,0]]")

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_create_text_object(self, mock_get_conn):
        """Test creating 3D text."""
        from blenderforge.server import create_text_object

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "name": "Text",
            "text": "Hello World",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_text_object(ctx, "Hello World", extrude=0.1)

        data = json.loads(result)
        assert data["success"] is True
        assert data["text"] == "Hello World"

    @patch("blenderforge.server.get_blender_connection")
    def test_create_pipe(self, mock_get_conn):
        """Test creating pipe along curve."""
        from blenderforge.server import create_pipe

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "curve": "Curve",
            "radius": 0.1,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_pipe(ctx, "Curve", radius=0.1)

        data = json.loads(result)
        assert data["success"] is True


# =============================================================================
# CONSTRAINTS & RELATIONSHIPS TESTS
# =============================================================================


class TestConstraintsRelationships:
    """Tests for constraints and relationships tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_add_constraint(self, mock_get_conn):
        """Test adding a constraint."""
        from blenderforge.server import add_constraint

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "object": "Object",
            "constraint_type": "COPY_LOCATION",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_constraint(ctx, "Object", "COPY_LOCATION", target_object="Target")

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_create_empty(self, mock_get_conn):
        """Test creating an empty."""
        from blenderforge.server import create_empty

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "name": "Control",
            "empty_type": "PLAIN_AXES",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_empty(ctx, name="Control")

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_parent_objects(self, mock_get_conn):
        """Test parenting objects."""
        from blenderforge.server import parent_objects

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "parent": "Parent",
            "children_parented": 3,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = parent_objects(ctx, '["Child1", "Child2", "Child3"]', "Parent")

        data = json.loads(result)
        assert data["success"] is True
        assert data["children_parented"] == 3


# =============================================================================
# SCENE ORGANIZATION TESTS
# =============================================================================


class TestSceneOrganization:
    """Tests for scene organization tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_create_collection(self, mock_get_conn):
        """Test creating a collection."""
        from blenderforge.server import create_collection

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "name": "MyCollection",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_collection(ctx, "MyCollection")

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_move_to_collection(self, mock_get_conn):
        """Test moving objects to collection."""
        from blenderforge.server import move_to_collection

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "objects_moved": 2,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = move_to_collection(ctx, '["Cube", "Sphere"]', "MyCollection")

        data = json.loads(result)
        assert data["success"] is True
        assert data["objects_moved"] == 2

    @patch("blenderforge.server.get_blender_connection")
    def test_export_scene(self, mock_get_conn):
        """Test exporting scene."""
        from blenderforge.server import export_scene

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "filepath": "/tmp/scene.glb",
            "format": "GLB",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = export_scene(ctx, "/tmp/scene.glb", format="GLB")

        data = json.loads(result)
        assert data["success"] is True
        assert data["format"] == "GLB"

    @patch("blenderforge.server.get_blender_connection")
    def test_save_blend(self, mock_get_conn):
        """Test saving blend file."""
        from blenderforge.server import save_blend

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "filepath": "/tmp/scene.blend",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = save_blend(ctx, "/tmp/scene.blend")

        data = json.loads(result)
        assert data["success"] is True


# =============================================================================
# PROCEDURAL GENERATION TESTS
# =============================================================================


class TestProceduralGeneration:
    """Tests for procedural generation tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_scatter_on_surface(self, mock_get_conn):
        """Test scattering instances on surface."""
        from blenderforge.server import scatter_on_surface

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "surface": "Terrain",
            "instance": "Tree",
            "instances_created": 100,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = scatter_on_surface(ctx, "Terrain", "Tree", density=10.0)

        data = json.loads(result)
        assert data["success"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_create_procedural_terrain(self, mock_get_conn):
        """Test creating procedural terrain."""
        from blenderforge.server import create_procedural_terrain

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "success": True,
            "name": "Terrain",
            "size": 10.0,
            "resolution": 100,
            "vertices": 10201,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_procedural_terrain(
            ctx, name="Terrain", size=10.0, resolution=100
        )

        data = json.loads(result)
        assert data["success"] is True
        assert data["name"] == "Terrain"


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for error handling across tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_modifier_object_not_found(self, mock_get_conn):
        """Test error when object not found for modifier."""
        from blenderforge.server import add_modifier

        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = Exception("Object 'NonExistent' not found")
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_modifier(ctx, "NonExistent", "BEVEL")

        assert "error" in result.lower()
        assert "NonExistent" in result

    @patch("blenderforge.server.get_blender_connection")
    def test_render_connection_error(self, mock_get_conn):
        """Test error when connection fails during render."""
        from blenderforge.server import render_image

        mock_get_conn.side_effect = Exception("Connection refused")

        ctx = MagicMock()
        result = render_image(ctx, "/tmp/test")

        assert "error" in result.lower()

    @patch("blenderforge.server.get_blender_connection")
    def test_invalid_json_parameter(self, mock_get_conn):
        """Test error with invalid JSON parameter."""
        from blenderforge.server import extrude_faces

        ctx = MagicMock()
        result = extrude_faces(ctx, "Cube", "invalid json", 1.0)

        assert "error" in result.lower()
