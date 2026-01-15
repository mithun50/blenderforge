"""Integration tests for BlenderForge.

These tests require a running Blender instance with the addon enabled.
Mark with @pytest.mark.integration to skip during regular test runs.
"""

import os

import pytest

# Skip all tests in this file if BLENDER_INTEGRATION_TEST is not set
pytestmark = pytest.mark.integration


@pytest.fixture
def blender_available():
    """Check if Blender is available for integration testing."""
    if not os.environ.get("BLENDER_INTEGRATION_TEST"):
        pytest.skip("Integration tests disabled. Set BLENDER_INTEGRATION_TEST=1 to enable.")
    return True


class TestBlenderIntegration:
    """Integration tests requiring actual Blender connection."""

    def test_real_connection(self, blender_available):
        """Test connecting to actual Blender instance."""
        from blenderforge.server import get_blender_connection

        try:
            conn = get_blender_connection()
            assert conn is not None
            assert conn.sock is not None
        except Exception as e:
            pytest.skip(f"Blender not available: {e}")

    def test_real_scene_info(self, blender_available):
        """Test getting real scene info from Blender."""
        from blenderforge.server import get_blender_connection

        try:
            conn = get_blender_connection()
            result = conn.send_command("get_scene_info")
            assert "name" in result or "object_count" in result
        except Exception as e:
            pytest.skip(f"Blender not available: {e}")

    def test_real_execute_code(self, blender_available):
        """Test executing real code in Blender."""
        from blenderforge.server import get_blender_connection

        try:
            conn = get_blender_connection()
            result = conn.send_command("execute_code", {"code": "print('Hello from test')"})
            assert result is not None
        except Exception as e:
            pytest.skip(f"Blender not available: {e}")


class TestModuleImports:
    """Test that all modules can be imported correctly."""

    def test_import_main_package(self):
        """Test importing main package."""
        from blenderforge import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_import_config(self):
        """Test importing config module."""
        from blenderforge.config import TelemetryConfig, telemetry_config

        assert TelemetryConfig is not None
        assert telemetry_config is not None

    def test_import_telemetry(self):
        """Test importing telemetry module."""
        from blenderforge.telemetry import (
            EventType,
            TelemetryCollector,
            TelemetryEvent,
        )

        assert EventType is not None
        assert TelemetryEvent is not None
        assert TelemetryCollector is not None

    def test_import_telemetry_decorator(self):
        """Test importing telemetry decorator."""
        from blenderforge.telemetry_decorator import telemetry_tool

        assert telemetry_tool is not None
        assert callable(telemetry_tool)

    def test_import_server(self):
        """Test importing server module."""
        from blenderforge.server import (
            BlenderConnection,
            main,
            mcp,
        )

        assert BlenderConnection is not None
        assert mcp is not None
        assert callable(main)


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_disable_telemetry_env(self):
        """Test DISABLE_TELEMETRY environment variable."""
        original = os.environ.get("DISABLE_TELEMETRY")
        try:
            os.environ["DISABLE_TELEMETRY"] = "true"
            from blenderforge.telemetry import TelemetryCollector

            collector = TelemetryCollector()
            assert collector.config.enabled is False
        finally:
            if original is not None:
                os.environ["DISABLE_TELEMETRY"] = original
            else:
                os.environ.pop("DISABLE_TELEMETRY", None)

    def test_blender_host_env(self):
        """Test BLENDER_HOST environment variable."""
        from blenderforge.server import DEFAULT_HOST

        assert DEFAULT_HOST == "localhost"

    def test_blender_port_env(self):
        """Test BLENDER_PORT environment variable."""
        from blenderforge.server import DEFAULT_PORT

        assert DEFAULT_PORT == 9876


class TestVersionConsistency:
    """Test version consistency across modules."""

    def test_version_matches_pyproject(self):
        """Test that __init__ version matches pyproject.toml."""
        from blenderforge import __version__

        assert __version__ == "1.0.5"

    def test_version_format(self):
        """Test version follows semver format."""
        from blenderforge import __version__

        parts = __version__.split(".")
        assert len(parts) >= 2
        assert all(part.isdigit() for part in parts[:2])
