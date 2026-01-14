# Development Guide

Guide for contributing to BlenderForge development.

---

## Development Setup

### Prerequisites

- Python 3.10+
- Blender 3.0+ (for testing)
- Git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/blenderforge.git
cd blenderforge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy src/
```

---

## Project Structure

```
blenderforge/
├── src/blenderforge/       # Main package
│   ├── __init__.py         # Package init, version
│   ├── server.py           # MCP server implementation
│   ├── config.py           # Configuration management
│   ├── telemetry.py        # Telemetry client
│   └── telemetry_decorator.py  # Telemetry decorator
├── addon.py                # Blender addon (standalone)
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest configuration
│   ├── test_config.py      # Config tests
│   ├── test_server.py      # Server tests
│   └── test_telemetry.py   # Telemetry tests
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD pipelines
├── pyproject.toml          # Project configuration
└── README.md               # Main readme
```

---

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=src/blenderforge --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Specific Tests

```bash
# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::test_default_config

# Run tests matching pattern
pytest -k "telemetry"
```

### Test Markers

```bash
# Skip integration tests (require Blender)
pytest -m "not integration"

# Skip slow tests
pytest -m "not slow"
```

---

## Code Quality

### Formatting

```bash
# Format code
ruff format .

# Check formatting without changing
ruff format --check .
```

### Linting

```bash
# Run linter
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Type Checking

```bash
mypy src/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Adding New Tools

### 1. Define the Tool in server.py

```python
@mcp.tool()
async def my_new_tool(
    required_param: str,
    optional_param: int = 10
) -> dict:
    """
    Short description of what the tool does.

    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter

    Returns:
        dict with result data
    """
    result = await send_to_blender({
        "command": "my_new_command",
        "required_param": required_param,
        "optional_param": optional_param
    })
    return result
```

### 2. Add Handler in addon.py

```python
class BlenderForgeOperator:
    def handle_command(self, command):
        # ... existing handlers ...

        elif command["command"] == "my_new_command":
            return self.handle_my_new_command(command)

    def handle_my_new_command(self, params):
        """Handle my_new_command."""
        required = params["required_param"]
        optional = params.get("optional_param", 10)

        # Execute Blender operations
        # ...

        return {
            "success": True,
            "result": "..."
        }
```

### 3. Add Tests

```python
# tests/test_server.py

def test_my_new_tool():
    """Test my_new_tool function."""
    # Test implementation
    pass
```

### 4. Document the Tool

Add to `docs/tools-reference.md`:

```markdown
### my_new_tool

Description of what the tool does.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `required_param` | string | Yes | Description |
| `optional_param` | integer | No | Description (default: 10) |

**Returns**:
...
```

---

## Adding External API Integrations

### 1. Create API Module (if complex)

For simple APIs, add directly to server.py. For complex APIs, create a new module:

```python
# src/blenderforge/myapi.py

import httpx

class MyAPIClient:
    BASE_URL = "https://api.example.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()

    async def search(self, query: str) -> list:
        response = await self.client.get(
            f"{self.BASE_URL}/search",
            params={"q": query},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
```

### 2. Add Configuration

In `addon.py`, add to the preferences class:

```python
class BlenderForgePreferences(bpy.types.AddonPreferences):
    # ... existing preferences ...

    use_myapi: bpy.props.BoolProperty(
        name="Use MyAPI",
        default=False
    )

    myapi_key: bpy.props.StringProperty(
        name="MyAPI Key",
        subtype='PASSWORD'
    )
```

### 3. Add Tools

```python
@mcp.tool()
async def search_myapi(query: str) -> dict:
    """Search MyAPI for resources."""
    if not is_myapi_enabled():
        return {"error": "MyAPI is not enabled"}

    client = MyAPIClient(get_myapi_key())
    results = await client.search(query)
    return {"results": results}
```

### 4. Document

Add to `docs/asset-integrations.md`.

---

## Testing with Blender

### Integration Tests

Integration tests require Blender to be running:

```python
# tests/test_integration.py

import pytest

@pytest.mark.integration
def test_get_scene_info_integration():
    """Test actual connection to Blender."""
    # This test requires Blender to be running
    # with the addon enabled
    pass
```

### Manual Testing

1. Start Blender with addon
2. Connect BlenderForge server
3. Run the MCP server manually:
   ```bash
   python -m blenderforge.server
   ```
4. Test with MCP client or manually send JSON-RPC

---

## Release Process

### Version Bump

1. Update version in `pyproject.toml`
2. Update version in `src/blenderforge/__init__.py`
3. Commit: `git commit -m "Bump version to X.Y.Z"`

### Create Release

1. Create and push tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

2. GitHub Actions will:
   - Run full test suite
   - Build distribution
   - Publish to PyPI
   - Create GitHub release

---

## Code Style Guidelines

### Python Style

- Follow PEP 8 (enforced by ruff)
- Use type hints for function parameters and returns
- Write docstrings for public functions
- Keep functions focused and small

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int = 10) -> dict:
    """
    Short description of function.

    Longer description if needed. Can span
    multiple lines.

    Args:
        param1: Description of param1
        param2: Description of param2, defaults to 10

    Returns:
        Dictionary containing result data

    Raises:
        ValueError: If param1 is empty
    """
```

### Naming Conventions

- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Error Handling

```python
# Return errors in consistent format
async def my_tool():
    try:
        result = await do_something()
        return {"success": True, "data": result}
    except SomeError as e:
        return {"success": False, "error": str(e)}
```

---

## Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** following code style guidelines
4. **Add tests** for new functionality
5. **Run checks**:
   ```bash
   ruff format .
   ruff check .
   mypy src/
   pytest
   ```
6. **Commit** with clear message
7. **Push** to your fork
8. **Create PR** with description of changes

### PR Requirements

- All tests pass
- Code is formatted and linted
- New features have tests
- Documentation is updated
- Commit messages are clear

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/blenderforge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/blenderforge/discussions)
- **MCP Spec**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Blender API**: [docs.blender.org/api](https://docs.blender.org/api/current/)
