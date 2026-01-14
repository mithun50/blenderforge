"""
Configuration for BlenderForge telemetry.

This file contains the telemetry configuration settings.
To disable telemetry, set DISABLE_TELEMETRY=true in your environment.

To use custom Supabase credentials, create config.local.py in this directory with:
    from .config import TelemetryConfig
    telemetry_config = TelemetryConfig(
        supabase_url="https://your-project.supabase.co",
        supabase_anon_key="your-anon-key",
    )
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TelemetryConfig:
    """Configuration for telemetry collection"""

    # Whether telemetry is enabled
    enabled: bool = True

    # Whether to collect prompt text (disabled by default for privacy)
    collect_prompts: bool = False

    # Maximum length of prompts to store if collection is enabled
    max_prompt_length: int = 500

    # Supabase configuration for telemetry storage
    # Override these in config.local.py for production use
    supabase_url: str = ""
    supabase_anon_key: str = ""


def _load_config() -> TelemetryConfig:
    """Load configuration, preferring local overrides if available"""
    # Try to load from config.local.py if it exists
    config_dir = Path(__file__).parent
    local_config = config_dir / "config.local.py"

    if local_config.exists():
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("config_local", local_config)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "telemetry_config"):
                    return module.telemetry_config
        except Exception:
            pass

    # Return default config (telemetry effectively disabled without Supabase credentials)
    return TelemetryConfig()


# Global telemetry configuration instance
telemetry_config = _load_config()
