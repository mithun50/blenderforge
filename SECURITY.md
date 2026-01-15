# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in BlenderForge, please report it responsibly:

1. **Email**: Send details to mithungowda.b7411@gmail.com
2. **GitHub**: Open a private security advisory at https://github.com/mithun50/blenderforge/security/advisories/new

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within 48 hours and will work with you to understand and address the issue.

## Security Features

### Code Execution Security

BlenderForge includes several security measures for the `execute_blender_code` tool:

#### Blocked Patterns
The following dangerous patterns are automatically blocked:
- `os.system` - System command execution
- `subprocess` - Process spawning
- `__import__` - Dynamic imports
- `eval()` / `exec()` - Dynamic code execution
- File write operations (`open(..., 'w')`)
- File deletion (`shutil.rmtree`, `os.remove`, `os.unlink`, `os.rmdir`)
- Network operations (`socket`, `requests`, `urllib`, `http`)

#### Allowed Imports
Only the following safe imports are permitted:
- `bpy` - Blender Python API
- `bmesh` - Blender mesh editing
- `mathutils` - Math utilities
- `math` - Standard math functions
- `random` - Random number generation
- `json` - JSON parsing
- `re` - Regular expressions
- `collections` - Data structures
- `itertools` - Iteration utilities
- `functools` - Functional programming tools
- `typing` - Type hints

#### Disabling Code Execution
To completely disable code execution:
```bash
export BLENDERFORGE_ALLOW_CODE_EXECUTION=false
```

### Authentication

BlenderForge uses token-based authentication between the MCP server and Blender addon:

1. **Token Generation**: A secure random token is generated using `secrets.token_hex(32)`
2. **Environment Variable**: Token is stored in `BLENDERFORGE_AUTH_TOKEN`
3. **Verification**: All commands include the auth token for verification

### API Key Security

**Important**: Never hardcode API keys in your code.

BlenderForge supports secure API key management:

#### Hyper3D Rodin API Key
```bash
export BLENDERFORGE_RODIN_API_KEY=your_api_key_here
```

#### Sketchfab API Key
Configure via the Blender addon preferences or environment variable.

### Network Security

- Communication occurs over localhost by default (`localhost:9876`)
- Socket connections use timeout protection (180 seconds)
- Connection retry logic with limits (3 attempts)

## Best Practices

### For Users

1. **Keep BlenderForge Updated**: Always use the latest version for security patches
2. **Secure API Keys**: Use environment variables, never share API keys
3. **Review Code**: Before executing code, review what it does
4. **Use Trusted Sources**: Only use BlenderForge with trusted AI assistants

### For Developers

1. **Input Validation**: Always validate user input before processing
2. **Principle of Least Privilege**: Request only necessary permissions
3. **Secure Defaults**: Default to secure configurations
4. **Logging**: Log security-relevant events without exposing sensitive data

## Telemetry & Privacy

BlenderForge includes optional anonymous telemetry:

- **What's Collected**: Tool usage, session ID, platform, version
- **What's NOT Collected**: Personal data, file contents, API keys, code content
- **Disable Telemetry**:
  ```bash
  export DISABLE_TELEMETRY=true
  # or
  export BLENDERFORGE_DISABLE_TELEMETRY=true
  ```

## Changelog

### v1.0.0
- Added code execution security validation
- Added rate limiting for API calls
- Removed hardcoded API keys
- Added environment variable support for API keys
- Added security documentation
