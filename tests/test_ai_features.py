"""Tests for AI-powered features."""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestGenerateMaterialFromText:
    """Tests for generate_material_from_text tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_generate_material_success(self, mock_get_conn):
        """Test successful material generation from text."""
        from blenderforge.server import generate_material_from_text

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "material_name": "RustyMetal",
            "properties_applied": ["metallic", "roughness", "base_color"],
            "metallic": 0.9,
            "roughness": 0.8,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = generate_material_from_text(ctx, "rusty metal", "RustyMetal")

        data = json.loads(result)
        assert data["material_name"] == "RustyMetal"
        assert "metallic" in data["properties_applied"]
        mock_conn.send_command.assert_called_with(
            "generate_material_text", {"description": "rusty metal", "name": "RustyMetal"}
        )

    @patch("blenderforge.server.get_blender_connection")
    def test_generate_material_error(self, mock_get_conn):
        """Test material generation with error."""
        from blenderforge.server import generate_material_from_text

        mock_get_conn.side_effect = Exception("Connection failed")

        ctx = MagicMock()
        result = generate_material_from_text(ctx, "glossy wood")

        data = json.loads(result)
        assert "error" in data


class TestGenerateMaterialFromImage:
    """Tests for generate_material_from_image tool."""

    @patch("blenderforge.server.open", create=True)
    @patch("blenderforge.server.os.path.exists")
    @patch("blenderforge.server.get_blender_connection")
    def test_generate_material_from_image_success(self, mock_get_conn, mock_exists, mock_open):
        """Test successful material generation from image."""
        from blenderforge.server import generate_material_from_image

        # Mock file exists and can be read
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = b"fake_image_data"

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "material_name": "ImageMaterial",
            "dominant_color": [0.5, 0.3, 0.2, 1.0],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = generate_material_from_image(ctx, "/path/to/image.png", "ImageMaterial")

        data = json.loads(result)
        assert data["material_name"] == "ImageMaterial"

    def test_generate_material_from_image_file_not_found(self):
        """Test material from image when file doesn't exist."""
        from blenderforge.server import generate_material_from_image

        ctx = MagicMock()
        result = generate_material_from_image(ctx, "/nonexistent/path.png")

        data = json.loads(result)
        assert "error" in data

    @patch("blenderforge.server.open", create=True)
    @patch("blenderforge.server.os.path.exists")
    @patch("blenderforge.server.get_blender_connection")
    def test_generate_material_from_image_connection_error(self, mock_get_conn, mock_exists, mock_open):
        """Test material from image with connection error."""
        from blenderforge.server import generate_material_from_image

        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = b"fake_image_data"
        mock_get_conn.side_effect = Exception("Connection failed")

        ctx = MagicMock()
        result = generate_material_from_image(ctx, "/path/to/image.png")

        data = json.loads(result)
        assert "error" in data


class TestListMaterialPresets:
    """Tests for list_material_presets tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_list_presets_success(self, mock_get_conn):
        """Test listing material presets."""
        from blenderforge.server import list_material_presets

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "presets": ["metal", "wood", "stone", "fabric", "glass", "plastic", "organic"],
            "count": 7,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = list_material_presets(ctx)

        data = json.loads(result)
        assert "presets" in data
        assert "metal" in data["presets"]
        assert "wood" in data["presets"]


class TestCreateFromDescription:
    """Tests for create_from_description tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_create_cube(self, mock_get_conn):
        """Test creating a cube from description."""
        from blenderforge.server import create_from_description

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "created_objects": ["Cube"],
            "count": 1,
            "properties": {"color": [1.0, 0.0, 0.0, 1.0]},
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_from_description(ctx, "a red cube")

        data = json.loads(result)
        assert data["count"] == 1
        assert "Cube" in data["created_objects"]

    @patch("blenderforge.server.get_blender_connection")
    def test_create_table(self, mock_get_conn):
        """Test creating a table from description."""
        from blenderforge.server import create_from_description

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "created_objects": ["Table_Top", "Table_Leg.001", "Table_Leg.002", "Table_Leg.003", "Table_Leg.004"],
            "count": 5,
            "type": "table",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = create_from_description(ctx, "a wooden table")

        data = json.loads(result)
        assert data["count"] >= 1

    @patch("blenderforge.server.get_blender_connection")
    def test_create_error(self, mock_get_conn):
        """Test create with error."""
        from blenderforge.server import create_from_description

        mock_get_conn.side_effect = Exception("Failed to create")

        ctx = MagicMock()
        result = create_from_description(ctx, "something invalid")

        data = json.loads(result)
        assert "error" in data


class TestModifyFromDescription:
    """Tests for modify_from_description tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_modify_color(self, mock_get_conn):
        """Test modifying object color."""
        from blenderforge.server import modify_from_description

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "object_name": "Cube",
            "modifications": ["color"],
            "new_color": [0.0, 0.0, 1.0, 1.0],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = modify_from_description(ctx, "Cube", "make it blue")

        data = json.loads(result)
        assert data["object_name"] == "Cube"

    @patch("blenderforge.server.get_blender_connection")
    def test_modify_object_not_found(self, mock_get_conn):
        """Test modifying non-existent object."""
        from blenderforge.server import modify_from_description

        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = Exception("Object not found")
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = modify_from_description(ctx, "NonExistent", "make it red")

        data = json.loads(result)
        assert "error" in data


class TestAnalyzeSceneComposition:
    """Tests for analyze_scene_composition tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_analyze_scene_success(self, mock_get_conn):
        """Test successful scene analysis."""
        from blenderforge.server import analyze_scene_composition

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "lighting": {"score": 75, "issues": [], "suggestions": []},
            "composition": {"score": 80, "issues": [], "suggestions": []},
            "materials": {"score": 60, "issues": [], "suggestions": []},
            "overall_score": 72,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = analyze_scene_composition(ctx)

        data = json.loads(result)
        assert "lighting" in data
        assert "composition" in data
        assert "materials" in data
        assert "overall_score" in data

    @patch("blenderforge.server.get_blender_connection")
    def test_analyze_scene_error(self, mock_get_conn):
        """Test scene analysis with error."""
        from blenderforge.server import analyze_scene_composition

        mock_get_conn.side_effect = Exception("Analysis failed")

        ctx = MagicMock()
        result = analyze_scene_composition(ctx)

        data = json.loads(result)
        assert "error" in data


class TestAutoOptimizeLighting:
    """Tests for auto_optimize_lighting tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_studio_lighting(self, mock_get_conn):
        """Test studio lighting setup."""
        from blenderforge.server import auto_optimize_lighting

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "style": "studio",
            "lights_created": ["Key_Light", "Fill_Light", "Back_Light"],
            "description": "3-point studio lighting",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = auto_optimize_lighting(ctx, "studio")

        data = json.loads(result)
        assert data["style"] == "studio"
        assert len(data["lights_created"]) == 3

    @patch("blenderforge.server.get_blender_connection")
    def test_cinematic_lighting(self, mock_get_conn):
        """Test cinematic lighting setup."""
        from blenderforge.server import auto_optimize_lighting

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "style": "cinematic",
            "lights_created": ["Cinematic_Key", "Cinematic_Fill", "Cinematic_Rim"],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = auto_optimize_lighting(ctx, "cinematic")

        data = json.loads(result)
        assert data["style"] == "cinematic"


class TestAutoRigCharacter:
    """Tests for auto_rig_character tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_humanoid_rig(self, mock_get_conn):
        """Test humanoid rig creation."""
        from blenderforge.server import auto_rig_character

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "armature_name": "Character_Armature",
            "bones_created": 15,
            "rig_type": "humanoid",
            "mesh_parented": True,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = auto_rig_character(ctx, "MyCharacter", "humanoid")

        data = json.loads(result)
        assert data["rig_type"] == "humanoid"
        assert data["bones_created"] > 0
        assert data["mesh_parented"] is True

    @patch("blenderforge.server.get_blender_connection")
    def test_quadruped_rig(self, mock_get_conn):
        """Test quadruped rig creation."""
        from blenderforge.server import auto_rig_character

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "armature_name": "Dog_Armature",
            "bones_created": 20,
            "rig_type": "quadruped",
            "mesh_parented": True,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = auto_rig_character(ctx, "Dog", "quadruped")

        data = json.loads(result)
        assert data["rig_type"] == "quadruped"

    @patch("blenderforge.server.get_blender_connection")
    def test_rig_invalid_mesh(self, mock_get_conn):
        """Test rigging with invalid mesh."""
        from blenderforge.server import auto_rig_character

        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = Exception("Object is not a mesh")
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = auto_rig_character(ctx, "Camera", "humanoid")

        data = json.loads(result)
        assert "error" in data


class TestAutoWeightPaint:
    """Tests for auto_weight_paint tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_weight_paint_success(self, mock_get_conn):
        """Test successful weight painting."""
        from blenderforge.server import auto_weight_paint

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "mesh_name": "Character",
            "armature_name": "Armature",
            "vertex_groups_created": 15,
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = auto_weight_paint(ctx, "Character", "Armature")

        data = json.loads(result)
        assert data["mesh_name"] == "Character"
        assert data["vertex_groups_created"] > 0


class TestAddIKControls:
    """Tests for add_ik_controls tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_add_ik_all_limbs(self, mock_get_conn):
        """Test adding IK to all limbs."""
        from blenderforge.server import add_ik_controls

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "armature_name": "Armature",
            "ik_targets_created": ["Hand.L.IK", "Hand.R.IK", "Foot.L.IK", "Foot.R.IK"],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_ik_controls(ctx, "Armature", "all")

        data = json.loads(result)
        assert len(data["ik_targets_created"]) == 4

    @patch("blenderforge.server.get_blender_connection")
    def test_add_ik_single_limb(self, mock_get_conn):
        """Test adding IK to single limb."""
        from blenderforge.server import add_ik_controls

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "armature_name": "Armature",
            "ik_targets_created": ["Hand.L.IK"],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = add_ik_controls(ctx, "Armature", "arm_l")

        data = json.loads(result)
        assert "Hand.L.IK" in data["ik_targets_created"]


class TestGetImprovementSuggestions:
    """Tests for get_improvement_suggestions tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_get_suggestions_success(self, mock_get_conn):
        """Test getting improvement suggestions."""
        from blenderforge.server import get_improvement_suggestions

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "suggestions": [
                {"category": "lighting", "suggestion": "Add fill light"},
                {"category": "materials", "suggestion": "Add materials to objects"},
            ],
            "priority_actions": ["Add more lights"],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_improvement_suggestions(ctx)

        data = json.loads(result)
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
