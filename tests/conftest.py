"""Pytest configuration and fixtures."""

import os
import sys

import pytest

# Ensure the src directory is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Disable telemetry during tests
os.environ["DISABLE_TELEMETRY"] = "true"


@pytest.fixture(autouse=True)
def disable_telemetry():
    """Disable telemetry for all tests."""
    os.environ["DISABLE_TELEMETRY"] = "true"
    yield
    # Cleanup not strictly necessary but good practice


@pytest.fixture
def mock_socket():
    """Provide a mock socket for testing."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.recv.return_value = b'{"status": "success", "result": {}}'
    return mock


@pytest.fixture
def sample_scene_info():
    """Sample scene info response for testing."""
    return {
        "name": "Scene",
        "object_count": 3,
        "objects": [
            {"name": "Cube", "type": "MESH", "location": [0.0, 0.0, 0.0]},
            {"name": "Camera", "type": "CAMERA", "location": [7.0, -6.0, 5.0]},
            {"name": "Light", "type": "LIGHT", "location": [4.0, 1.0, 6.0]},
        ],
        "materials_count": 1,
    }


@pytest.fixture
def sample_object_info():
    """Sample object info response for testing."""
    return {
        "name": "Cube",
        "type": "MESH",
        "location": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
        "visible": True,
        "materials": ["Material"],
        "mesh": {"vertices": 8, "edges": 12, "polygons": 6},
        "world_bounding_box": [[-1.0, -1.0, -1.0], [1.0, 1.0, 1.0]],
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires Blender)"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
