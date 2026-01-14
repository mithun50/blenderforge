# Troubleshooting

Common issues and their solutions.

---

## Connection Issues

### "Could not connect to Blender"

**Symptoms**:
- AI assistant reports connection failure
- Tools return timeout errors

**Solutions**:

1. **Check if Blender is running**
   ```
   Make sure Blender is open before using BlenderForge tools.
   ```

2. **Check if addon is enabled**
   - Go to `Edit` → `Preferences` → `Add-ons`
   - Search for "BlenderForge"
   - Ensure the checkbox is checked

3. **Check if server is started**
   - Press `N` to open sidebar
   - Go to **BlenderForge** tab
   - Click **"Connect to MCP server"**
   - Status should show "Connected"

4. **Check for port conflicts**
   - Default port is 9876
   - If another application uses this port, change it in the BlenderForge panel
   - Also set `BLENDER_PORT` environment variable to match

5. **Check firewall settings**
   - BlenderForge only uses localhost
   - Some firewalls block localhost connections
   - Allow connections to `127.0.0.1:9876`

---

### "Connection refused"

**Symptoms**:
- Error message mentions "connection refused"
- Tools fail immediately

**Solutions**:

1. **Restart the connection in Blender**
   - Click "Disconnect" in BlenderForge panel
   - Wait 2 seconds
   - Click "Connect to MCP server"

2. **Check the port setting**
   - BlenderForge panel shows the port number
   - Ensure it matches what the MCP server expects
   - Default: 9876

3. **Kill any stale processes**
   ```bash
   # On macOS/Linux
   lsof -i :9876
   kill <PID>

   # On Windows
   netstat -ano | findstr 9876
   taskkill /PID <PID> /F
   ```

---

### "Timeout waiting for Blender"

**Symptoms**:
- Tools start but never complete
- Error after 30-60 seconds

**Solutions**:

1. **Break complex operations into smaller steps**
   ```
   Instead of: "Create a detailed scene with 100 objects"
   Try: "Add 10 cubes" then "Add 10 spheres" etc.
   ```

2. **Check if Blender is responsive**
   - Try clicking in the Blender viewport
   - If Blender is frozen, wait or restart it

3. **Increase timeout (environment variable)**
   ```bash
   export BLENDER_TIMEOUT=120000  # 2 minutes
   ```

---

## AI Client Issues

### "Tools not appearing in AI assistant"

**Symptoms**:
- AI doesn't recognize BlenderForge commands
- No Blender tools in tools list

**Solutions**:

1. **Restart your AI assistant**
   - Close completely and reopen
   - MCP servers are loaded at startup

2. **Check configuration file location**

   | Client | Config Location |
   |--------|-----------------|
   | Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
   | Claude Desktop (Linux) | `~/.config/Claude/claude_desktop_config.json` |
   | VS Code | Settings → `github.copilot.chat.mcp.servers` |
   | Cursor | Settings → MCP |

3. **Validate JSON syntax**
   ```json
   {
     "mcpServers": {
       "blenderforge": {
         "command": "blenderforge"
       }
     }
   }
   ```
   Use a JSON validator to check for syntax errors.

4. **Check if blenderforge command is in PATH**
   ```bash
   which blenderforge  # macOS/Linux
   where blenderforge  # Windows
   ```
   If not found, reinstall or add to PATH.

5. **Check AI client logs**
   - Most clients have developer logs
   - Look for MCP-related errors

---

### "Tool calls fail silently"

**Symptoms**:
- AI says it will use a tool but nothing happens
- No error message shown

**Solutions**:

1. **Check Blender console for errors**
   - `Window` → `Toggle System Console` (Windows)
   - Launch Blender from terminal (macOS/Linux)

2. **Enable verbose logging**
   ```bash
   export BLENDERFORGE_DEBUG=true
   blenderforge
   ```

---

## Asset Integration Issues

### "PolyHaven not working"

**Symptoms**:
- Can't search or download PolyHaven assets
- "PolyHaven not enabled" errors

**Solutions**:

1. **Enable PolyHaven integration**
   - Open BlenderForge panel in Blender
   - Check **Use PolyHaven**

2. **Check internet connection**
   - PolyHaven requires network access
   - Try visiting [polyhaven.com](https://polyhaven.com) in browser

3. **Check for API changes**
   - PolyHaven API may have changed
   - Update BlenderForge to latest version

---

### "Sketchfab not working"

**Symptoms**:
- Authentication failures
- Can't search or download models

**Solutions**:

1. **Verify API key**
   - Log into Sketchfab
   - Go to Settings → API
   - Copy the API token
   - Re-enter in BlenderForge panel

2. **Check API key permissions**
   - Ensure your account has download permissions
   - Some models require specific license agreements

3. **Check model availability**
   - Not all models are downloadable
   - Use `downloadable: true` filter in searches

---

### "Hyper3D/Hunyuan3D not working"

**Symptoms**:
- Generation fails
- Authentication errors

**Solutions**:

1. **Verify API credentials**
   - Double-check API key/secret
   - Ensure account is in good standing

2. **Check credit balance**
   - Hyper3D uses credits
   - Free trial may have expired

3. **Check generation status**
   - Use `poll_*_job_status` to check progress
   - Generation can take 15-60+ seconds

---

## Performance Issues

### "Blender becomes slow/unresponsive"

**Symptoms**:
- Blender UI freezes during operations
- High memory usage

**Solutions**:

1. **Reduce operation complexity**
   - Download smaller textures (2K instead of 8K)
   - Import simpler models
   - Process fewer objects at once

2. **Close unnecessary panels**
   - Minimize BlenderForge panel when not in use
   - Close other heavy panels

3. **Restart Blender periodically**
   - Memory can accumulate over long sessions
   - Save and restart every few hours

---

### "MCP server uses high CPU"

**Symptoms**:
- High CPU usage from blenderforge process
- System becomes slow

**Solutions**:

1. **Check for polling loops**
   - If using AI generation, don't poll continuously
   - Wait between status checks

2. **Restart MCP server**
   - Restart your AI client
   - This restarts the MCP server process

---

## Error Messages

### "ModuleNotFoundError: No module named 'mcp'"

**Solution**:
```bash
pip install "mcp[cli]>=1.3.0"
```

### "ImportError: cannot import name 'FastMCP'"

**Solution**:
```bash
pip install --upgrade "mcp[cli]>=1.3.0"
```

### "JSONDecodeError" in logs

**Cause**: Malformed messages between server and Blender

**Solution**:
1. Restart both Blender and AI client
2. Check for Blender console errors
3. Update to latest BlenderForge version

### "Permission denied" when starting server

**Cause**: Port already in use or permission issue

**Solution**:
```bash
# Change to a different port
export BLENDER_PORT=9877
blenderforge
```

---

## Getting Help

If none of these solutions work:

1. **Check existing issues**: [GitHub Issues](https://github.com/yourusername/blenderforge/issues)

2. **Create a new issue** with:
   - OS and version
   - Python version
   - Blender version
   - AI client being used
   - Error messages (from Blender console and AI client)
   - Steps to reproduce

3. **Enable debug logging** and include logs:
   ```bash
   export BLENDERFORGE_DEBUG=true
   blenderforge 2>&1 | tee blenderforge.log
   ```
