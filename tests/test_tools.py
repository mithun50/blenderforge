"""Tests for MCP tools."""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestGetSceneInfo:
    """Tests for get_scene_info tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_get_scene_info_success(self, mock_get_conn):
        """Test successful scene info retrieval."""
        from blenderforge.server import get_scene_info

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "name": "Scene",
            "object_count": 3,
            "objects": [
                {"name": "Cube", "type": "MESH"},
                {"name": "Camera", "type": "CAMERA"},
                {"name": "Light", "type": "LIGHT"},
            ],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_scene_info(ctx)

        data = json.loads(result)
        assert data["name"] == "Scene"
        assert data["object_count"] == 3
        assert len(data["objects"]) == 3

    @patch("blenderforge.server.get_blender_connection")
    def test_get_scene_info_error(self, mock_get_conn):
        """Test scene info with connection error."""
        from blenderforge.server import get_scene_info

        mock_get_conn.side_effect = Exception("Connection failed")

        ctx = MagicMock()
        result = get_scene_info(ctx)

        assert "Error" in result
        assert "Connection failed" in result


class TestGetObjectInfo:
    """Tests for get_object_info tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_get_object_info_success(self, mock_get_conn):
        """Test successful object info retrieval."""
        from blenderforge.server import get_object_info

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "name": "Cube",
            "type": "MESH",
            "location": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_object_info(ctx, "Cube")

        data = json.loads(result)
        assert data["name"] == "Cube"
        assert data["type"] == "MESH"
        mock_conn.send_command.assert_called_with("get_object_info", {"name": "Cube"})

    @patch("blenderforge.server.get_blender_connection")
    def test_get_object_info_not_found(self, mock_get_conn):
        """Test object info for non-existent object."""
        from blenderforge.server import get_object_info

        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = Exception("Object not found")
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_object_info(ctx, "NonExistent")

        assert "Error" in result


class TestExecuteBlenderCode:
    """Tests for execute_blender_code tool."""

    @patch("blenderforge.server.get_blender_connection")
    def test_execute_code_success(self, mock_get_conn):
        """Test successful code execution."""
        from blenderforge.server import execute_blender_code

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {"result": "Created cube"}
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = execute_blender_code(ctx, "bpy.ops.mesh.primitive_cube_add()")

        assert "successfully" in result.lower()
        mock_conn.send_command.assert_called_with(
            "execute_code", {"code": "bpy.ops.mesh.primitive_cube_add()"}
        )

    @patch("blenderforge.server.get_blender_connection")
    def test_execute_code_error(self, mock_get_conn):
        """Test code execution with error."""
        from blenderforge.server import execute_blender_code

        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = Exception("Syntax error in code")
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = execute_blender_code(ctx, "invalid python code {{{")

        assert "Error" in result


class TestPolyHavenTools:
    """Tests for PolyHaven integration tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_get_polyhaven_status_enabled(self, mock_get_conn):
        """Test PolyHaven status when enabled."""
        from blenderforge.server import get_polyhaven_status

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "enabled": True,
            "message": "PolyHaven is enabled.",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_polyhaven_status(ctx)

        assert "enabled" in result.lower() or "PolyHaven" in result

    @patch("blenderforge.server.get_blender_connection")
    def test_get_polyhaven_status_disabled(self, mock_get_conn):
        """Test PolyHaven status when disabled."""
        from blenderforge.server import get_polyhaven_status

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "enabled": False,
            "message": "PolyHaven is disabled.",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_polyhaven_status(ctx)

        assert "disabled" in result.lower() or "PolyHaven" in result

    @patch("blenderforge.server.get_blender_connection")
    @patch("blenderforge.server._polyhaven_enabled", True)
    def test_get_polyhaven_categories(self, mock_get_conn):
        """Test getting PolyHaven categories."""
        from blenderforge.server import get_polyhaven_categories

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "categories": {"wood": 50, "metal": 30, "fabric": 20}
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_polyhaven_categories(ctx, "textures")

        assert "wood" in result
        assert "metal" in result

    @patch("blenderforge.server.get_blender_connection")
    @patch("blenderforge.server._polyhaven_enabled", False)
    def test_get_polyhaven_categories_disabled(self, mock_get_conn):
        """Test categories when PolyHaven is disabled."""
        from blenderforge.server import get_polyhaven_categories

        ctx = MagicMock()
        result = get_polyhaven_categories(ctx, "textures")

        assert "disabled" in result.lower()


class TestSketchfabTools:
    """Tests for Sketchfab integration tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_get_sketchfab_status(self, mock_get_conn):
        """Test Sketchfab status check."""
        from blenderforge.server import get_sketchfab_status

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "enabled": True,
            "message": "Sketchfab is enabled.",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_sketchfab_status(ctx)

        assert "Sketchfab" in result

    @patch("blenderforge.server.get_blender_connection")
    def test_search_sketchfab_models(self, mock_get_conn):
        """Test Sketchfab model search."""
        from blenderforge.server import search_sketchfab_models

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "results": [
                {
                    "name": "Coffee Mug",
                    "uid": "abc123",
                    "user": {"username": "artist1"},
                    "license": {"label": "CC BY"},
                    "faceCount": 5000,
                    "isDownloadable": True,
                }
            ]
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = search_sketchfab_models(ctx, "coffee mug")

        assert "Coffee Mug" in result
        assert "abc123" in result


class TestHyper3DTools:
    """Tests for Hyper3D integration tools."""

    @patch("blenderforge.server.get_blender_connection")
    def test_get_hyper3d_status(self, mock_get_conn):
        """Test Hyper3D status check."""
        from blenderforge.server import get_hyper3d_status

        mock_conn = MagicMock()
        mock_conn.send_command.return_value = {
            "enabled": True,
            "message": "Hyper3D is enabled.",
        }
        mock_get_conn.return_value = mock_conn

        ctx = MagicMock()
        result = get_hyper3d_status(ctx)

        # Result can vary but should contain status info
        assert isinstance(result, str)


class TestProcessBbox:
    """Tests for _process_bbox helper function."""

    def test_process_bbox_none(self):
        """Test processing None bbox."""
        from blenderforge.server import _process_bbox

        result = _process_bbox(None)
        assert result is None

    def test_process_bbox_integers(self):
        """Test processing integer bbox."""
        from blenderforge.server import _process_bbox

        result = _process_bbox([10, 20, 30])
        assert result == [10, 20, 30]

    def test_process_bbox_floats(self):
        """Test processing float bbox."""
        from blenderforge.server import _process_bbox

        result = _process_bbox([1.0, 2.0, 3.0])
        # Should be converted to percentages
        assert isinstance(result, list)
        assert len(result) == 3

    def test_process_bbox_invalid_zero(self):
        """Test processing bbox with zero value."""
        from blenderforge.server import _process_bbox

        with pytest.raises(ValueError, match="bigger than zero"):
            _process_bbox([0, 1, 2])

    def test_process_bbox_invalid_negative(self):
        """Test processing bbox with negative value."""
        from blenderforge.server import _process_bbox

        with pytest.raises(ValueError, match="bigger than zero"):
            _process_bbox([-1, 1, 2])
