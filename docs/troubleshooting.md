# Troubleshooting

Comprehensive guide to diagnosing and resolving BlenderForge issues.

---

## Table of Contents

- [Quick Diagnostic Checklist](#quick-diagnostic-checklist)
- [Connection Issues](#connection-issues)
- [AI Client Issues](#ai-client-issues)
- [Installation Issues](#installation-issues)
- [Asset Integration Issues](#asset-integration-issues)
- [AI Features Issues](#ai-features-issues)
- [Performance Issues](#performance-issues)
- [Error Messages Reference](#error-messages-reference)
- [Debug Mode](#debug-mode)
- [Log Files](#log-files)
- [Platform-Specific Issues](#platform-specific-issues)
- [Getting Help](#getting-help)

---

## Quick Diagnostic Checklist

Run through this checklist before diving into specific issues:

### 1. Verify Installation
```bash
# Check BlenderForge is installed
blenderforge --version

# If not found, try:
python -m blenderforge --version
pip show blenderforge
```

### 2. Check Blender Setup
- [ ] Blender is running
- [ ] BlenderForge addon is enabled (`Edit` → `Preferences` → `Add-ons`)
- [ ] BlenderForge panel is visible (Press `N`, find tab)
- [ ] Server status shows "Connected"

### 3. Verify AI Client
- [ ] Config file exists and has valid JSON
- [ ] AI client has been restarted after config change
- [ ] BlenderForge appears in available tools

### 4. Test Connection
Ask your AI: `"What objects are in my Blender scene?"`

---

## Connection Issues

### "Could not connect to Blender"

**Symptoms:**
- AI assistant reports connection failure
- Tools return timeout errors
- "Connection refused" messages

**Solutions:**

#### Solution 1: Verify Blender is Running
```
Make sure Blender is open and the addon is enabled before using BlenderForge tools.
```

#### Solution 2: Check Addon is Enabled
1. Go to `Edit` → `Preferences` → `Add-ons`
2. Search for "BlenderForge"
3. Ensure the checkbox is checked
4. If missing, reinstall the addon

#### Solution 3: Start the Server
1. Press `N` to open the sidebar in Blender
2. Go to **BlenderForge** tab
3. Click **"Connect to MCP server"**
4. Status should show "Connected"

#### Solution 4: Check Port Configuration
- Default port is **9876**
- Verify the same port is set in:
  - Blender's BlenderForge panel
  - Your MCP configuration (if using `BLENDER_PORT` env var)

```bash
# Check if something else is using the port
# macOS/Linux
lsof -i :9876

# Windows
netstat -ano | findstr 9876
```

#### Solution 5: Check Firewall
- BlenderForge only uses localhost connections
- Some firewalls block localhost (`127.0.0.1`)
- Allow connections to `127.0.0.1:9876`

---

### "Connection refused"

**Symptoms:**
- Error message contains "connection refused"
- Tools fail immediately without timeout

**Solutions:**

#### Solution 1: Restart the Connection
1. In Blender's BlenderForge panel, click "Disconnect"
2. Wait 2-3 seconds
3. Click "Connect to MCP server"

#### Solution 2: Kill Stale Processes
```bash
# macOS/Linux - Find and kill process on port 9876
lsof -i :9876
kill <PID>

# Windows
netstat -ano | findstr 9876
taskkill /PID <PID> /F
```

#### Solution 3: Change Port
If port 9876 is persistently problematic:
1. In Blender panel, change port to 9877
2. Update your MCP config:
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "env": { "BLENDER_PORT": "9877" }
    }
  }
}
```
3. Restart AI client

---

### "Timeout waiting for Blender"

**Symptoms:**
- Tools start but never complete
- Error after 30-60 seconds

**Solutions:**

#### Solution 1: Simplify Operations
```
Instead of: "Create a detailed scene with 100 objects"
Try: "Add 10 cubes" then "Add 10 more cubes"
```

#### Solution 2: Check Blender Responsiveness
- Click in Blender's viewport
- If Blender is frozen, wait for it to recover or restart

#### Solution 3: Increase Timeout
```bash
# Set longer timeout (2 minutes = 120000ms)
export BLENDER_TIMEOUT=120000
blenderforge
```

Or in MCP config:
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "env": { "BLENDER_TIMEOUT": "120000" }
    }
  }
}
```

#### Solution 4: Check System Resources
- High RAM usage can slow Blender
- Close unnecessary applications
- Check for runaway processes

---

## AI Client Issues

### "Tools not appearing in AI assistant"

**Symptoms:**
- AI doesn't recognize BlenderForge commands
- No Blender tools in tools list
- AI says "I don't have access to BlenderForge"

**Solutions:**

#### Solution 1: Restart AI Client
MCP servers load at startup. You must:
1. Close the AI client **completely**
2. Wait a few seconds
3. Reopen the AI client

#### Solution 2: Verify Config File Location

| Client | Config Location |
|--------|-----------------|
| **Claude Desktop (macOS)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Desktop (Windows)** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Claude Desktop (Linux)** | `~/.config/Claude/claude_desktop_config.json` |
| **Claude Code** | `~/.claude.json` |
| **VS Code** | `settings.json` → `github.copilot.chat.mcp.servers` |
| **Cursor** | Settings → MCP tab |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **Zed** | `~/.config/zed/settings.json` |
| **Continue.dev** | `~/.continue/config.yaml` |

#### Solution 3: Validate JSON Syntax
```json
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge"
    }
  }
}
```

Common JSON errors:
- Missing commas between properties
- Trailing commas (not allowed in JSON)
- Unquoted strings
- Wrong bracket types

Use a JSON validator: https://jsonlint.com/

#### Solution 4: Check Command Path
```bash
# Verify blenderforge is in PATH
which blenderforge  # macOS/Linux
where blenderforge  # Windows

# If not found, use full path in config:
{
  "mcpServers": {
    "blenderforge": {
      "command": "/usr/local/bin/blenderforge"
    }
  }
}

# Or use Python module:
{
  "mcpServers": {
    "blenderforge": {
      "command": "python",
      "args": ["-m", "blenderforge"]
    }
  }
}
```

#### Solution 5: Check AI Client Logs
Most clients have developer logs showing MCP errors:

- **Claude Desktop:** `~/Library/Logs/Claude/` (macOS)
- **VS Code:** Help → Toggle Developer Tools → Console
- **Cursor:** Help → Toggle Developer Tools → Console

---

### "Tool calls fail silently"

**Symptoms:**
- AI says it will use a tool but nothing happens
- No visible error message
- Blender doesn't respond

**Solutions:**

#### Solution 1: Check Blender Console
- **Windows:** `Window` → `Toggle System Console`
- **macOS/Linux:** Launch Blender from terminal:
  ```bash
  /Applications/Blender.app/Contents/MacOS/Blender  # macOS
  blender  # Linux
  ```

#### Solution 2: Enable Debug Logging
```bash
export BLENDERFORGE_DEBUG=true
blenderforge
```

#### Solution 3: Test Direct Connection
Ask AI to run a simple test:
```
"Get the Blender version"
"What is the name of the current scene?"
```

---

### "MCP server failed to start"

**Symptoms:**
- AI client shows server startup error
- BlenderForge never connects

**Solutions:**

#### Solution 1: Check Python Environment
```bash
# Verify Python version
python --version  # Should be 3.10+

# Check if blenderforge is importable
python -c "import blenderforge; print('OK')"
```

#### Solution 2: Reinstall BlenderForge
```bash
pip uninstall blenderforge
pip install blenderforge
```

#### Solution 3: Check Dependencies
```bash
pip install "mcp[cli]>=1.3.0"
```

---

## Installation Issues

### "pip: command not found"

**Solutions:**

```bash
# Try pip3
pip3 install blenderforge

# Or use Python module
python -m pip install blenderforge
python3 -m pip install blenderforge
```

### "Permission denied during installation"

**Solutions:**

```bash
# Install for user only
pip install --user blenderforge

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
pip install blenderforge
```

### "blenderforge: command not found" after installation

**Cause:** pip installed to a directory not in PATH

**Solutions:**

```bash
# Find installation location
pip show blenderforge

# Add to PATH (example for user install)
# macOS/Linux - add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"

# Or run as module:
python -m blenderforge
```

### Python version incompatibility

**Symptoms:**
- `SyntaxError` during import
- `ModuleNotFoundError`

**Solution:**
```bash
# Check Python version
python --version

# BlenderForge requires Python 3.10+
# Install newer Python if needed
```

---

## Asset Integration Issues

### "PolyHaven not working"

**Symptoms:**
- Can't search or download PolyHaven assets
- "PolyHaven not enabled" errors

**Solutions:**

1. **Enable PolyHaven Integration:**
   - Open BlenderForge panel in Blender
   - Check **Use PolyHaven** checkbox

2. **Check Internet Connection:**
   - PolyHaven requires network access
   - Test: Visit [polyhaven.com](https://polyhaven.com) in browser

3. **Check API Availability:**
   - PolyHaven API: `https://api.polyhaven.com`
   - If API is down, wait and try later

4. **Update BlenderForge:**
   ```bash
   pip install --upgrade blenderforge
   ```

---

### "Sketchfab not working"

**Symptoms:**
- Authentication failures
- "Invalid API key" errors

**Solutions:**

1. **Verify API Key:**
   - Log into [sketchfab.com](https://sketchfab.com)
   - Go to Settings → API
   - Copy the API token
   - Re-enter in BlenderForge panel

2. **Check API Key Format:**
   - Should be a long alphanumeric string
   - No spaces or special characters

3. **Check Model Permissions:**
   - Not all models are downloadable
   - Use `downloadable: true` filter
   - Check license requirements

---

### "Hyper3D/Hunyuan3D generation fails"

**Symptoms:**
- Generation starts but never completes
- Authentication errors
- Credit exhausted messages

**Solutions:**

1. **Verify Credentials:**
   - Double-check API key/secret
   - Ensure account is active

2. **Check Credit Balance:**
   - Hyper3D uses credits
   - Free trial may have limits
   - Check account dashboard

3. **Check Generation Status:**
   - AI generation takes 15-60+ seconds
   - Use status polling commands
   - Don't cancel too early

4. **Check Rate Limits:**
   - Some services have request limits
   - Wait between generation requests

---

## AI Features Issues

### "AI Material Generator not working"

**Symptoms:**
- Material generation fails
- No material created in Blender

**Solutions:**

1. **Check Object Selection:**
   - Material generator may require an object to be selected
   - Or specify target object name

2. **Check Blender Console:**
   - Look for Python errors during material creation
   - Common: missing node connections

3. **Verify Scene Setup:**
   - Ensure you're in a 3D scene (not compositor, etc.)
   - Check Blender is in Object mode

---

### "Natural Language Modeling fails"

**Symptoms:**
- Object not created as expected
- Wrong position/size/color

**Solutions:**

1. **Use Clearer Descriptions:**
   ```
   Better: "Create a red cube at position (2, 0, 0) with size 1 meter"
   Worse: "Make something red over there"
   ```

2. **Check Units:**
   - Blender uses meters by default
   - Specify units explicitly when needed

3. **One Operation at a Time:**
   ```
   Instead of: "Create a red cube, blue sphere, and green cylinder"
   Try: Three separate commands
   ```

---

### "Scene Analyzer returns empty results"

**Symptoms:**
- No analysis returned
- Generic or unhelpful feedback

**Solutions:**

1. **Ensure Scene Has Objects:**
   - Analyzer needs content to analyze
   - Add some objects first

2. **Check Scene Complexity:**
   - Very simple scenes may not trigger detailed analysis
   - More complex scenes get better feedback

---

### "Auto-Rig not finding mesh"

**Symptoms:**
- "Mesh not found" error
- Armature not created

**Solutions:**

1. **Verify Mesh Name:**
   - Use exact mesh object name
   - Check Object name vs Data name in Blender

2. **Check Mesh Type:**
   - Must be a mesh object (not curve, text, etc.)
   - Humanoid rig needs humanoid-like mesh

3. **Mesh Requirements:**
   - Mesh should be at origin or specify location
   - Should have appropriate topology for rigging

---

## Performance Issues

### "Blender becomes slow/unresponsive"

**Symptoms:**
- Blender UI freezes
- High memory usage
- Operations take too long

**Solutions:**

1. **Reduce Operation Complexity:**
   - Download smaller textures (2K instead of 8K)
   - Import simpler models
   - Process fewer objects at once

2. **Manage Memory:**
   - Close unnecessary panels
   - Purge orphan data: `File` → `Clean Up` → `Purge All`
   - Restart Blender periodically

3. **Optimize Scene:**
   - Use simpler materials for preview
   - Lower subdivision levels
   - Hide complex objects when not needed

---

### "MCP server uses high CPU"

**Symptoms:**
- High CPU from blenderforge process
- System slowdown

**Solutions:**

1. **Avoid Polling Loops:**
   - Don't continuously check AI generation status
   - Wait between status checks

2. **Restart MCP Server:**
   - Restart your AI client
   - This restarts the MCP server process

3. **Check for Stuck Operations:**
   - Kill and restart if an operation is hanging

---

### "Large scenes cause timeouts"

**Solutions:**

1. **Increase Timeout:**
   ```bash
   export BLENDER_TIMEOUT=300000  # 5 minutes
   ```

2. **Work in Sections:**
   - Process parts of the scene separately
   - Use collections to organize

3. **Simplify Queries:**
   - Get info about specific objects, not entire scene
   - Use filters to reduce data

---

## Error Messages Reference

### Python/Module Errors

#### "ModuleNotFoundError: No module named 'mcp'"
```bash
pip install "mcp[cli]>=1.3.0"
```

#### "ImportError: cannot import name 'FastMCP'"
```bash
pip install --upgrade "mcp[cli]>=1.3.0"
```

#### "ModuleNotFoundError: No module named 'blenderforge'"
```bash
pip install blenderforge
# Or if installed in virtual environment, activate it first
```

### Connection Errors

#### "JSONDecodeError" in logs
**Cause:** Malformed messages between server and Blender

**Solution:**
1. Restart both Blender and AI client
2. Check Blender console for errors
3. Update to latest BlenderForge version

#### "Permission denied" when starting server
**Cause:** Port in use or permission issue

**Solution:**
```bash
export BLENDER_PORT=9877
blenderforge
```

#### "Address already in use"
```bash
# Find and kill process using the port
lsof -i :9876 | grep LISTEN
kill <PID>
```

### Blender Errors

#### "Context is incorrect"
**Cause:** Operation called in wrong Blender context

**Solution:** Ensure proper mode (Object/Edit) and selection

#### "Operator poll failed"
**Cause:** Blender operator prerequisites not met

**Solution:** Check object selection, mode, and scene state

---

## Debug Mode

### Enable Debug Logging

```bash
# Environment variable
export BLENDERFORGE_DEBUG=true
blenderforge

# Or in MCP config
{
  "mcpServers": {
    "blenderforge": {
      "command": "blenderforge",
      "env": { "BLENDERFORGE_DEBUG": "true" }
    }
  }
}
```

### Capture Debug Output

```bash
# Save logs to file
blenderforge 2>&1 | tee blenderforge_debug.log

# Or redirect stderr
blenderforge 2>blenderforge_error.log
```

### View Real-time Logs

```bash
# Follow log output
tail -f blenderforge_debug.log
```

---

## Log Files

### Log File Locations

| Component | Location |
|-----------|----------|
| **BlenderForge (with debug)** | stderr output |
| **Blender Console** | System console window |
| **Claude Desktop (macOS)** | `~/Library/Logs/Claude/` |
| **VS Code** | Developer Tools → Console |

### Blender Console Access

**Windows:**
```
Window → Toggle System Console
```

**macOS:**
```bash
/Applications/Blender.app/Contents/MacOS/Blender
```

**Linux:**
```bash
blender
```

### Collecting Logs for Bug Reports

```bash
# 1. Enable debug mode
export BLENDERFORGE_DEBUG=true

# 2. Capture output
blenderforge 2>&1 | tee debug.log

# 3. Reproduce the issue

# 4. Include debug.log in bug report
```

---

## Platform-Specific Issues

### macOS

#### "Operation not permitted"
- Check System Preferences → Security & Privacy
- Allow terminal/Python access

#### "blenderforge: command not found" with Homebrew Python
```bash
# Add Homebrew bin to PATH
export PATH="/opt/homebrew/bin:$PATH"
# Or
export PATH="/usr/local/bin:$PATH"
```

#### Blender from App Store Issues
- App Store version may have sandboxing restrictions
- Download from blender.org instead

---

### Windows

#### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or add manually:
  ```
  C:\Users\<username>\AppData\Local\Programs\Python\Python311\
  C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts\
  ```

#### "Access denied" errors
- Run Command Prompt as Administrator
- Check antivirus isn't blocking

#### Path Issues
```cmd
:: Use forward slashes or escape backslashes
"C:/Users/name/path"
"C:\\Users\\name\\path"
```

---

### Linux

#### Snap/Flatpak Blender Restrictions
- Snap and Flatpak have sandboxed file access
- May not be able to access all directories
- Consider official tarball from blender.org

#### Permission Issues
```bash
# Check addon directory permissions
ls -la ~/.config/blender/4.0/scripts/addons/

# Fix if needed
chmod 755 ~/.config/blender/4.0/scripts/addons/
```

#### "externally-managed-environment" Error
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install blenderforge

# Or use pipx
pipx install blenderforge
```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Search existing issues:** [GitHub Issues](https://github.com/mithun50/blenderforge/issues)
3. **Enable debug logging** and collect logs
4. **Try to reproduce** with minimal setup

### Creating a Bug Report

Include the following information:

```markdown
**Environment:**
- OS: [e.g., Windows 11, macOS 14.0, Ubuntu 22.04]
- Python version: [output of `python --version`]
- Blender version: [e.g., 4.0.2]
- BlenderForge version: [output of `blenderforge --version`]
- AI client: [e.g., Claude Desktop, VS Code + Copilot]

**Description:**
[What you were trying to do]

**Expected behavior:**
[What you expected to happen]

**Actual behavior:**
[What actually happened]

**Steps to reproduce:**
1. [First step]
2. [Second step]
3. ...

**Error messages:**
[Copy any error messages]

**Debug logs:**
[Attach or paste debug log output]
```

### Contact Channels

- **GitHub Issues:** [Report bugs](https://github.com/mithun50/blenderforge/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/mithun50/blenderforge/discussions)

### Useful Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Blender Stack Exchange](https://blender.stackexchange.com/)
