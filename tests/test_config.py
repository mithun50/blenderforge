"""Tests for configuration module."""



class TestTelemetryConfig:
    """Tests for TelemetryConfig dataclass."""

    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        # Import here to avoid issues if module has import errors
        from blenderforge.config import TelemetryConfig

        config = TelemetryConfig()

        assert config.enabled is True
        assert config.collect_prompts is False
        assert config.max_prompt_length == 500
        assert config.supabase_url == ""
        assert config.supabase_anon_key == ""

    def test_custom_values(self):
        """Test that custom values can be set."""
        from blenderforge.config import TelemetryConfig

        config = TelemetryConfig(
            enabled=False,
            collect_prompts=True,
            max_prompt_length=1000,
            supabase_url="https://example.supabase.co",
            supabase_anon_key="test-key-123",
        )

        assert config.enabled is False
        assert config.collect_prompts is True
        assert config.max_prompt_length == 1000
        assert config.supabase_url == "https://example.supabase.co"
        assert config.supabase_anon_key == "test-key-123"

    def test_config_is_dataclass(self):
        """Test that TelemetryConfig is a proper dataclass."""
        from dataclasses import is_dataclass

        from blenderforge.config import TelemetryConfig

        assert is_dataclass(TelemetryConfig)

    def test_global_config_instance(self):
        """Test that global telemetry_config is available."""
        from blenderforge.config import telemetry_config

        assert telemetry_config is not None
        assert hasattr(telemetry_config, "enabled")
        assert hasattr(telemetry_config, "supabase_url")


class TestConfigLoading:
    """Tests for configuration loading behavior."""

    def test_empty_credentials_detected(self):
        """Test that empty Supabase credentials are properly detected."""
        from blenderforge.config import TelemetryConfig

        config = TelemetryConfig()

        # Empty string should be falsy
        assert not config.supabase_url
        assert not config.supabase_anon_key

    def test_config_with_credentials(self):
        """Test config with valid credentials."""
        from blenderforge.config import TelemetryConfig

        config = TelemetryConfig(
            supabase_url="https://test.supabase.co",
            supabase_anon_key="valid-key",
        )

        assert config.supabase_url
        assert config.supabase_anon_key
