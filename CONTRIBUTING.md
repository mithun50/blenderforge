# Contributing to BlenderForge

Thank you for your interest in contributing to BlenderForge! This document provides guidelines and information for contributors.

## Code of Conduct

Please be respectful and constructive in all interactions. We're building something together.

## Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/blenderforge.git
   cd blenderforge
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/blenderforge --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run tests matching pattern
pytest -k "test_telemetry"
```

### Code Style

We use the following tools for code quality:

- **Ruff** - Linting and formatting
- **MyPy** - Type checking

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type checking
mypy src/
```

## Project Structure

```
blenderforge/
├── addon.py                 # Blender addon - runs inside Blender
├── src/blenderforge/        # MCP server package
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── server.py            # MCP server & tools
│   ├── telemetry.py         # Analytics
│   └── telemetry_decorator.py
├── tests/                   # Test suite
└── .github/workflows/       # CI/CD
```

## Making Changes

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

Example: `feature/add-texture-painting-support`

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting (no code change)
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance

Examples:
```
feat(server): add texture painting tool
fix(addon): handle connection timeout gracefully
docs: update installation instructions
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run quality checks**
   ```bash
   ruff format .
   ruff check .
   pytest
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Describe what changes you made
   - Reference any related issues
   - Ensure CI passes

## Adding New Tools

To add a new MCP tool:

1. **Add the handler in `addon.py`**
   ```python
   def your_new_handler(self, param1, param2):
       """Handle the operation in Blender"""
       # Implementation
       return {"success": True, "result": data}
   ```

2. **Register the handler**
   ```python
   handlers = {
       # ... existing handlers
       "your_new_command": self.your_new_handler,
   }
   ```

3. **Add the MCP tool in `server.py`**
   ```python
   @telemetry_tool("your_new_tool")
   @mcp.tool()
   def your_new_tool(ctx: Context, param1: str, param2: int = 10) -> str:
       """
       Description of what this tool does.

       Parameters:
       - param1: Description of param1
       - param2: Description of param2 (default: 10)
       """
       try:
           blender = get_blender_connection()
           result = blender.send_command("your_new_command", {
               "param1": param1,
               "param2": param2
           })
           return json.dumps(result, indent=2)
       except Exception as e:
           return f"Error: {str(e)}"
   ```

4. **Add tests**
   ```python
   # tests/test_server.py
   def test_your_new_tool():
       # Test implementation
       pass
   ```

## Testing Guidelines

### Unit Tests

Test individual functions in isolation:

```python
def test_config_defaults():
    config = TelemetryConfig()
    assert config.enabled is True
    assert config.max_prompt_length == 500
```

### Integration Tests

Test component interactions (mark with `@pytest.mark.integration`):

```python
@pytest.mark.integration
def test_blender_connection():
    # Requires running Blender instance
    pass
```

### Test Fixtures

Use fixtures for common setup:

```python
@pytest.fixture
def mock_blender_connection():
    with patch('blenderforge.server.get_blender_connection') as mock:
        yield mock
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 10) -> dict:
    """Short description of function.

    Longer description if needed, explaining what the function
    does in more detail.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 10.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
    """
```

### README Updates

When adding features, update:
- Feature list in README.md
- Tool table if adding new tools
- Configuration section if adding options

## Release Process

Releases are automated via GitHub Actions when a tag is pushed:

```bash
# Create release tag
git tag v1.0.1
git push origin v1.0.1
```

The CI will:
1. Run all tests
2. Build the package
3. Publish to PyPI
4. Create GitHub release

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community (link TBD)

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- README acknowledgments (for significant contributions)

Thank you for contributing to BlenderForge!
