"""Tests for server module."""


import pytest


class TestBlenderConnection:
    """Tests for BlenderConnection class."""

    def test_connection_init(self):
        """Test BlenderConnection initialization."""
        from blenderforge.server import BlenderConnection

        conn = BlenderConnection(host="localhost", port=9876)

        assert conn.host == "localhost"
        assert conn.port == 9876
        assert conn.sock is None
        assert conn.auth_token is None
        assert conn.max_retries == 3
        assert conn.retry_delay == 1.0

    def test_connection_custom_params(self):
        """Test BlenderConnection with custom parameters."""
        from blenderforge.server import BlenderConnection

        conn = BlenderConnection(
            host="192.168.1.100",
            port=8888,
            max_retries=5,
            retry_delay=2.0,
        )

        assert conn.host == "192.168.1.100"
        assert conn.port == 8888
        assert conn.max_retries == 5
        assert conn.retry_delay == 2.0

    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected doesn't raise."""
        from blenderforge.server import BlenderConnection

        conn = BlenderConnection(host="localhost", port=9876)
        conn.disconnect()  # Should not raise

        assert conn.sock is None


class TestServerConstants:
    """Tests for server constants."""

    def test_default_host(self):
        """Test default host constant."""
        from blenderforge.server import DEFAULT_HOST

        assert DEFAULT_HOST == "localhost"

    def test_default_port(self):
        """Test default port constant."""
        from blenderforge.server import DEFAULT_PORT

        assert DEFAULT_PORT == 9876


class TestGetBlenderConnection:
    """Tests for get_blender_connection function."""

    def test_connection_failure_raises(self):
        """Test that connection failure raises appropriate exception."""
        import blenderforge.server as server_module
        from blenderforge.server import get_blender_connection

        # Reset global connection
        server_module._blender_connection = None

        with pytest.raises(Exception) as exc_info:
            get_blender_connection()

        assert "Could not connect to Blender" in str(exc_info.value)


class TestMCPServerSetup:
    """Tests for MCP server setup."""

    def test_mcp_instance_exists(self):
        """Test that MCP server instance is created."""
        from blenderforge.server import mcp

        assert mcp is not None
        assert mcp.name == "BlenderForge"

    def test_tools_registered(self):
        """Test that tools are registered with MCP server."""

        # FastMCP stores tools internally
        # We can check by verifying the decorated functions exist
        from blenderforge import server

        assert hasattr(server, "get_scene_info")
        assert hasattr(server, "get_object_info")
        assert hasattr(server, "execute_blender_code")
        assert hasattr(server, "get_viewport_screenshot")


class TestBboxProcessing:
    """Tests for bounding box processing."""

    def test_process_bbox_none(self):
        """Test _process_bbox with None input."""
        from blenderforge.server import _process_bbox

        result = _process_bbox(None)
        assert result is None

    def test_process_bbox_integers(self):
        """Test _process_bbox with integer input."""
        from blenderforge.server import _process_bbox

        result = _process_bbox([10, 20, 30])
        assert result == [10, 20, 30]

    def test_process_bbox_floats(self):
        """Test _process_bbox with float input."""
        from blenderforge.server import _process_bbox

        result = _process_bbox([1.0, 2.0, 3.0])
        # Should normalize to percentages
        assert isinstance(result, list)
        assert len(result) == 3

    def test_process_bbox_invalid_raises(self):
        """Test _process_bbox with invalid input raises."""
        from blenderforge.server import _process_bbox

        with pytest.raises(ValueError):
            _process_bbox([0.0, 0.0, 0.0])  # Zero values invalid

        with pytest.raises(ValueError):
            _process_bbox([-1.0, 2.0, 3.0])  # Negative values invalid


class TestMainFunction:
    """Tests for main entry point."""

    def test_main_function_exists(self):
        """Test that main function exists."""
        from blenderforge.server import main

        assert callable(main)
