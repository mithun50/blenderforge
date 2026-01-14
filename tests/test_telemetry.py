"""Tests for telemetry module."""

import os
from unittest.mock import patch


class TestTelemetryDisabling:
    """Tests for telemetry disabling mechanisms."""

    def test_disable_via_env_var(self):
        """Test that telemetry can be disabled via environment variable."""
        with patch.dict(os.environ, {"DISABLE_TELEMETRY": "true"}):
            # Need to reload to pick up env var
            from blenderforge.config import TelemetryConfig
            from blenderforge.telemetry import TelemetryCollector

            config = TelemetryConfig()
            collector = TelemetryCollector.__new__(TelemetryCollector)
            collector.config = config

            assert collector._is_disabled() is True

    def test_disable_via_blenderforge_env_var(self):
        """Test BLENDERFORGE_DISABLE_TELEMETRY env var."""
        with patch.dict(os.environ, {"BLENDERFORGE_DISABLE_TELEMETRY": "1"}):
            from blenderforge.config import TelemetryConfig
            from blenderforge.telemetry import TelemetryCollector

            config = TelemetryConfig()
            collector = TelemetryCollector.__new__(TelemetryCollector)
            collector.config = config

            assert collector._is_disabled() is True

    def test_disable_via_mcp_env_var(self):
        """Test MCP_DISABLE_TELEMETRY env var."""
        with patch.dict(os.environ, {"MCP_DISABLE_TELEMETRY": "yes"}):
            from blenderforge.config import TelemetryConfig
            from blenderforge.telemetry import TelemetryCollector

            config = TelemetryConfig()
            collector = TelemetryCollector.__new__(TelemetryCollector)
            collector.config = config

            assert collector._is_disabled() is True

    def test_enabled_when_no_env_var_but_no_credentials(self):
        """Test that telemetry is disabled when no credentials configured."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove any disable env vars
            for key in [
                "DISABLE_TELEMETRY",
                "BLENDERFORGE_DISABLE_TELEMETRY",
                "MCP_DISABLE_TELEMETRY",
            ]:
                os.environ.pop(key, None)

            from blenderforge.config import TelemetryConfig
            from blenderforge.telemetry import TelemetryCollector

            # Empty credentials
            config = TelemetryConfig(supabase_url="", supabase_anon_key="")
            collector = TelemetryCollector.__new__(TelemetryCollector)
            collector.config = config

            # Should be disabled due to empty credentials
            assert collector._is_disabled() is True


class TestEventTypes:
    """Tests for telemetry event types."""

    def test_event_type_enum(self):
        """Test that EventType enum has expected values."""
        from blenderforge.telemetry import EventType

        assert EventType.STARTUP.value == "startup"
        assert EventType.TOOL_EXECUTION.value == "tool_execution"
        assert EventType.PROMPT_SENT.value == "prompt_sent"
        assert EventType.CONNECTION.value == "connection"
        assert EventType.ERROR.value == "error"


class TestTelemetryEvent:
    """Tests for TelemetryEvent dataclass."""

    def test_event_creation(self):
        """Test creating a telemetry event."""
        import time

        from blenderforge.telemetry import EventType, TelemetryEvent

        event = TelemetryEvent(
            event_type=EventType.TOOL_EXECUTION,
            customer_uuid="test-uuid",
            session_id="test-session",
            timestamp=time.time(),
            version="1.0.0",
            platform="linux",
            tool_name="get_scene_info",
            success=True,
            duration_ms=150.5,
        )

        assert event.event_type == EventType.TOOL_EXECUTION
        assert event.customer_uuid == "test-uuid"
        assert event.tool_name == "get_scene_info"
        assert event.success is True
        assert event.duration_ms == 150.5

    def test_event_optional_fields(self):
        """Test that optional fields have correct defaults."""
        import time

        from blenderforge.telemetry import EventType, TelemetryEvent

        event = TelemetryEvent(
            event_type=EventType.STARTUP,
            customer_uuid="test-uuid",
            session_id="test-session",
            timestamp=time.time(),
            version="1.0.0",
            platform="darwin",
        )

        assert event.tool_name is None
        assert event.prompt_text is None
        assert event.success is True  # Default
        assert event.duration_ms is None
        assert event.error_message is None
        assert event.blender_version is None
        assert event.metadata is None


class TestVersionDetection:
    """Tests for version detection."""

    def test_mcp_version_available(self):
        """Test that MCP_VERSION is defined."""
        from blenderforge.telemetry import MCP_VERSION

        assert MCP_VERSION is not None
        assert isinstance(MCP_VERSION, str)
